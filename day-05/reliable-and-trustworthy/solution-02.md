# Solution 02 · Make transactions-insight dependable: no data loss and an exactly-once effect

> The full worked solution for Assignment 02. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your interoperable `transactions-insight` project, green, with its `TransactionIn`
contract, the `/v1/score` scoring route, the paginated transactions pair, the signed webhook, and the
trace-id middleware. This solution adds the dependability layer for the financial-transactions domain: a
new `dependability.py` module of small standard-library pieces, and the wiring that routes the money
write through them. The reliability goal is narrow and strict, because a payment record is
audit-critical: never lose an accepted write, and never apply the same write twice. Use `poetry run` for
everything.

## Step 1: the dependability module

The transactions service needs two hard guarantees at its edge (exactly-once under retry and all-or-
nothing under a crash) and the operational surface an on-call engineer needs to trust it (readiness,
structured logs, and SLI metrics). Put all of it in one module built on the standard library alone, so a
reader can follow each piece end to end. Create `src/transactions_insight/dependability.py`.

### All-or-nothing writes

The core of no-data-loss is a write that can be interrupted without leaving a half or a duplicate:

**`src/transactions_insight/dependability.py`** (the atomic append)

```python
def atomic_append(
    rows: list[dict[str, str]],
    record: dict[str, str],
    on_prepared: Callable[[], None] | None = None,
) -> None:
    """Append one record so an interruption leaves the store with all of it or none of it.

    The write has two phases. The prepare phase builds a complete, private copy of the record
    and touches nothing that a reader can see. The commit phase is a single list.append, which
    is one atomic step in CPython, so a reader ever sees either no record or the whole record,
    never a half-written one and never two.

    The on_prepared hook sits between the two phases. A test passes a function that raises there
    to simulate a crash in the middle of the write. Because the commit has not run yet, the
    exception propagates and the store is left exactly as it was.
    """
    staged = dict(record)  # prepare: a complete copy, not yet visible in the store
    if on_prepared is not None:
        on_prepared()  # a test raises here to simulate an interruption before the commit
    rows.append(staged)  # commit: one atomic step, so the record is whole or absent
```

Two phases, one atomic commit. The prepare phase (`staged = dict(record)`) builds a full private copy
that no reader can see. The commit phase is a single `rows.append(staged)`, which is one atomic step in
CPython, so a reader ever sees no record or the whole record. The `on_prepared` hook sits between the
phases; a test raises there to simulate a crash before the commit, and because the append has not run,
the store is left exactly as it was. This is the crash-in-the-middle safety the durability metric
demands.

### The exactly-once store

Wrap the atomic append in an idempotency-keyed store, so a retry cannot double-record a payment:

**`src/transactions_insight/dependability.py`** (the store)

```python
class TransactionStore:
    """An in-memory transaction store with exactly-once writes keyed by an idempotency key.

    Submitting the same idempotency key twice (a retry, including one caused by a response that
    was lost on the way back to the client) records exactly one transaction and returns the
    first stored result. That is the core promise of the transactions domain: a retry must never
    double-record a payment.
    """

    def __init__(self) -> None:
        self._rows: list[dict[str, str]] = []
        self._by_key: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()

    def add(
        self,
        record: dict[str, str],
        key: str | None = None,
        on_prepared: Callable[[], None] | None = None,
    ) -> tuple[dict[str, str], bool]:
        """Store one record, or return the earlier one for a repeated key."""
        with self._lock:
            if key is not None and key in self._by_key:
                # Idempotent replay: this key already recorded a transaction, so return the first
                # result and write nothing. This is what turns a retry into an exactly-once effect.
                return self._by_key[key], False
            atomic_append(self._rows, record, on_prepared)
            stored = self._rows[-1]
            if key is not None:
                self._by_key[key] = stored
            return stored, True
```

`add` returns a pair `(stored, created)`. On the first write for a key, `created` is `True`; on every
replay it is `False`, so a caller can keep its response identical across a retry. The idempotency check,
the append, and the key registration all happen under one `threading.Lock`, so a concurrent retry
cannot slip a second row in between the lookup and the write. The store also carries an `all()` that
returns a copy of the rows (so a caller cannot mutate the store by accident) and a `__len__`. Retry and
idempotency are the two halves of one pattern, and this store holds both.

### Readiness, metrics, and structured logs

The operational surface is the "operate" step of the loop: signals an engineer can watch. First
readiness, distinct from liveness:

```python
class Capacity:
    """Tracks in-flight requests against a limit, so readiness can report saturation."""

    def __init__(self, limit: int = 64) -> None:
        self.limit = limit
        self._in_flight = 0
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            self._in_flight += 1

    def release(self) -> None:
        with self._lock:
            self._in_flight -= 1

    def is_ready(self) -> bool:
        with self._lock:
            return self._in_flight <= self.limit
```

Liveness (health) answers "is the process up". Readiness answers "can it take more work right now". When
in-flight work reaches the limit, readiness reports not-ready (a 503) so a load balancer stops sending
new requests until the service drains, instead of piling on and losing work.

Then the SLI metrics, the three first-look signals (how much traffic, how many failures, how slow),
hand-rolled so there is no heavy metrics dependency:

```python
class Metrics:
    """A tiny SLI collector: a request count, an error count, and a duration summary."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.requests = 0
        self.errors = 0  # counts responses with a 5xx status (a server-side failure)
        self.total_duration_ms = 0.0
        self.max_duration_ms = 0.0

    def record(self, duration_ms: float, status: int) -> None:
        with self._lock:
            self.requests += 1
            if status >= 500:
                self.errors += 1
            self.total_duration_ms += duration_ms
            self.max_duration_ms = max(self.max_duration_ms, duration_ms)

    def render(self) -> str:
        """Render the metrics as plain text, one metric per line (a Prometheus-like shape)."""
        with self._lock:
            avg = self.total_duration_ms / self.requests if self.requests else 0.0
            lines = [
                "# SLI metrics for transactions-insight (plain text, no external dependency)",
                f"requests_total {self.requests}",
                f"errors_total {self.errors}",
                f"request_duration_ms_avg {avg:.3f}",
                f"request_duration_ms_max {self.max_duration_ms:.3f}",
            ]
        return "\n".join(lines) + "\n"
```

And the structured logging, one JSON line per event carrying the trace id:

```python
def get_logger() -> logging.Logger:
    """Return the shared logger, configured once to emit each event as a raw line."""
    logger = logging.getLogger("transactions_insight")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))  # the message is already JSON
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    trace_id: str,
    duration_ms: float,
    status: int,
) -> None:
    """Emit one JSON line for one event, carrying the trace id that ties a request together."""
    line = json.dumps(
        {
            "event": event,
            "trace_id": trace_id,
            "duration_ms": round(duration_ms, 3),
            "status": status,
        }
    )
    logger.log(level, line)
```

One structured line per event (not free-form text) is what lets a log tool filter by trace id, sum by
event, or alert on status, without parsing prose. This is the same `trace_id` the interoperable layer
introduced, now doing its real job: tying a request's logs together as it crosses services.

### The ledger invariant

Last, state the financial invariant on its own so a property test can exercise it:

```python
@dataclass(frozen=True)
class LedgerEntry:
    """One posting against an account, in paise: a positive amount credits, a negative debits."""

    account_id: str
    amount_paise: int


def running_balance_ok(entries: Sequence[LedgerEntry]) -> bool:
    """The ledger invariant: applied in order, no account's running balance ever goes below zero."""
    balances: dict[str, int] = {}
    for entry in entries:
        new_balance = balances.get(entry.account_id, 0) + entry.amount_paise
        if new_balance < 0:
            return False  # this posting would overdraw the account, so the invariant is broken
        balances[entry.account_id] = new_balance
    return True
```

A financial ledger must hold this at every step, not only at the end, so a debit can never take an
account overdrawn. The live store never violates it because the API accepts only positive amounts
(`amount` greater than 0), but stating the rule on its own is what lets a property test generate many
sequences and check every step.

## Step 2: wire the dependability layer into the API

The module holds the guarantees; now the API has to use them. Open
`src/transactions_insight/api.py`. Build one set of dependability objects per app instance, replace the
plain trace-id middleware with one `observe` middleware that does all the cross-cutting work, add the
`/ready` and `/metrics` routes, and route the money write through the store:

**`src/transactions_insight/api.py`** (the changed parts)

```python
from transactions_insight.dependability import (
    Capacity,
    Metrics,
    TransactionStore,
    get_logger,
    log_event,
)
from transactions_insight.native import crc32_native


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="transactions-insight", version="0.6.0")
    # The dependability layer: an exactly-once store, a capacity gauge for readiness, a metrics
    # collector, and the shared structured logger. Each app instance owns its own set, so the
    # tests stay independent.
    store = TransactionStore()
    capacity = Capacity()
    metrics = Metrics()
    logger = get_logger()

    @app.middleware("http")
    async def observe(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # One middleware does the cross-cutting work for every request: it carries the trace id,
        # tracks in-flight load for readiness, times the call, and records one metric and one
        # structured log line.
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        capacity.acquire()
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # A crash is never allowed to be invisible: record it as an error and log it before
            # re-raising. The finally block still frees the capacity slot.
            duration_ms = (time.perf_counter() - start) * 1000
            metrics.record(duration_ms, 500)
            log_event(logger, logging.ERROR, "request.error", trace_id, duration_ms, 500)
            raise
        finally:
            capacity.release()
        duration_ms = (time.perf_counter() - start) * 1000
        metrics.record(duration_ms, response.status_code)
        log_event(logger, logging.INFO, "request", trace_id, duration_ms, response.status_code)
        response.headers["x-trace-id"] = trace_id
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        # Liveness: is the process up. This stays a plain, always-200 check, separate from
        # readiness below, so a load balancer can tell "up" apart from "ready for more work".
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> Response:
        # Readiness: can the service take more work right now. When in-flight load reaches the
        # capacity limit, we report 503 so callers back off instead of piling on and losing work.
        if capacity.is_ready():
            return PlainTextResponse('{"status": "ready"}', media_type="application/json")
        return PlainTextResponse(
            '{"status": "saturated"}', status_code=503, media_type="application/json"
        )

    @app.get("/metrics")
    def metrics_endpoint() -> Response:
        return PlainTextResponse(metrics.render())
```

One `observe` middleware carries the whole "operate" surface for every route: it reuses an incoming
`x-trace-id` or starts a new `uuid.uuid4().hex`, acquires a capacity slot, times the call, and on the
way out records a metric and a structured log line and echoes the trace id. The `try`/`except`/`finally`
is the careful part: an exception is recorded as a 500 error and logged as a `request.error` before it
re-raises, and the `finally` frees the capacity slot no matter what, so a crash can never leak a slot or
go unseen. `/health` stays a plain always-200 liveness check, while `/ready` reports `503` when the
capacity gauge is saturated, so the two answer different questions.

The write path is where exactly-once lands:

```python
    @app.post("/v1/transactions", status_code=201, response_model=TransactionOut)
    def submit(
        txn: TransactionIn,
        idempotency_key: str | None = Header(default=None),
    ) -> TransactionOut:
        # The idempotency key can arrive in the Idempotency-Key header or in the body; the header
        # wins if both are sent. With a key, a retry (including one after a lost response) records
        # exactly one transaction and returns the same result, so an account is never charged
        # twice. Without a key, each call records a new transaction as before.
        key = idempotency_key or txn.idempotency_key
        record = {
            "account_id": txn.account_id,
            "amount": str(txn.amount),
            "currency": txn.currency,
        }
        stored, _created = store.add(record, key=key)
        return TransactionOut(
            account_id=stored["account_id"],
            amount=float(stored["amount"]),
            currency=stored["currency"],
        )
```

`TransactionIn` gains one optional field, `idempotency_key: str | None`, so a caller can send a
per-transaction key in the body instead of the header. The handler reads `idempotency_key or
txn.idempotency_key` (the header wins), then stores through `store.add`. With a key, a retry records
exactly one transaction and returns the first stored result; without one, each call records a new row,
just as before. The webhook write routes through the same store too, using a webhook `id` as the key
when present, so a redelivered event is recorded only once and every inbound write is all-or-nothing.
The `/v1/score` route is untouched: the score is still
`crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.

## Step 3: the dependability tests (the deliverable proof)

This is the proof. One file exercises every guarantee: exactly-once under a lost-response retry, all-or-
nothing under a crash, readiness apart from liveness, the metrics surface, and the ledger invariant over
hundreds of generated cases. Create `tests/test_dependability.py`:

**`tests/test_dependability.py`** (the exactly-once and crash tests)

```python
def test_same_key_twice_records_one_and_returns_the_same_result() -> None:
    # Simulate a lost response: the client sends a transaction, the reply is lost, so the client
    # retries with the same idempotency key. The service must record exactly one transaction and
    # return the same result both times, never charging the account twice.
    client = _client()
    body = {"account_id": "A1", "amount": 250.0, "currency": "INR"}
    headers = {"Idempotency-Key": "retry-key-1"}

    first = client.post("/v1/transactions", json=body, headers=headers)
    second = client.post("/v1/transactions", json=body, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()  # the retry returns the same result
    assert client.get("/v1/transactions").json()["total"] == 1  # exactly one is stored


def test_crash_in_the_middle_stores_none_then_a_retry_stores_exactly_one() -> None:
    # Simulate an interruption during the write: the on_prepared hook raises after the record is
    # prepared but before it is committed. The store must be left with none of it, never a
    # partial row. A later successful write then stores exactly one, never two.
    store = TransactionStore()
    record = {"account_id": "A9", "amount": "500.0", "currency": "INR"}

    def crash() -> None:
        raise _SimulatedCrash("interrupted before commit")

    with pytest.raises(_SimulatedCrash):
        store.add(record, key="k1", on_prepared=crash)

    assert len(store) == 0  # whole or none: the interrupted write left nothing behind

    stored, created = store.add(record, key="k1")  # the retry now succeeds
    assert created is True
    assert len(store) == 1  # exactly one, never a duplicate from the failed attempt
    assert stored["account_id"] == "A9"
```

`test_same_key_twice_records_one_and_returns_the_same_result` is the deliverable's heart. It posts the
same body twice with the same `Idempotency-Key`, exactly the shape of a client whose first response was
lost and who retried. Both calls return `201`, the two JSON bodies are identical, and the list reports
`total == 1`: one row, same result, the account charged once.
`test_crash_in_the_middle_stores_none_then_a_retry_stores_exactly_one` is the other half of no-data-
loss. It raises inside `on_prepared`, before the commit, and asserts `len(store) == 0`, so an
interrupted write leaves nothing behind, and a clean retry then stores exactly one with `created is
True`, never a duplicate from the failed attempt.

Two more tests pin the idempotency contract from both ends, and a control proves it is off without a
key:

```python
def test_a_key_in_the_body_is_honoured_too() -> None:
    # The idempotency key may travel in the body (a per-transaction key) instead of the header.
    client = _client()
    body = {"account_id": "A2", "amount": 99.0, "currency": "INR", "idempotency_key": "body-key"}

    client.post("/v1/transactions", json=body)
    client.post("/v1/transactions", json=body)

    assert client.get("/v1/transactions").json()["total"] == 1


def test_no_key_records_each_call() -> None:
    # Without a key there is no idempotency promise, so two calls record two transactions.
    client = _client()
    body = {"account_id": "A3", "amount": 10.0, "currency": "INR"}
    client.post("/v1/transactions", json=body)
    client.post("/v1/transactions", json=body)
    assert client.get("/v1/transactions").json()["total"] == 2
```

`test_a_key_in_the_body_is_honoured_too` proves a body key works the same as a header key, and
`test_no_key_records_each_call` is the control: with no key there is no promise, so two calls record two
rows. Together they show the exactly-once effect is exactly scoped to a supplied key.

The operational surface gets three tests, and the ledger invariant gets two:

```python
def test_ready_returns_200_normally() -> None:
    # Under normal load the service is ready to take work.
    resp = _client().get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_health_stays_plain_liveness() -> None:
    # Liveness is separate from readiness and always answers a plain ok.
    assert _client().get("/health").json() == {"status": "ok"}


def test_metrics_report_request_and_error_counts() -> None:
    client = _client()
    client.get("/health")
    text = client.get("/metrics").text
    assert "requests_total" in text
    assert "errors_total" in text
    assert "request_duration_ms_avg" in text


def test_ledger_invariant_holds_over_many_generated_sequences() -> None:
    # A parametric property check: over many generated valid sequences, the running balance never
    # goes below zero. hypothesis is not a direct dev dependency in the base, so we generate the
    # cases ourselves with a seeded random source (repeatable, and no new heavy dependency).
    rng = random.Random(1234)
    for _ in range(500):
        entries = _random_safe_sequence(rng, length=rng.randint(0, 40))
        assert running_balance_ok(entries) is True


def test_ledger_invariant_catches_an_overdraft() -> None:
    # The invariant must actually fire: a debit larger than the balance breaks it.
    entries = [
        LedgerEntry("A0", 500),  # credit 5 rupees
        LedgerEntry("A0", -900),  # debit 9 rupees, which would overdraw the account
    ]
    assert running_balance_ok(entries) is False
```

`test_ready_returns_200_normally` and `test_health_stays_plain_liveness` prove readiness and liveness
are two different answers, and `test_metrics_report_request_and_error_counts` confirms the SLI surface
renders the counts an operator watches. The two ledger tests are a small property check: a helper
`_random_safe_sequence` builds sequences that by construction never overdraw (each step credits a random
amount or debits at most the current balance), and `test_ledger_invariant_holds_over_many_generated_sequences`
runs `running_balance_ok` over 500 of them from a seeded `random.Random(1234)`, so the run is repeatable
and needs no hypothesis dependency. `test_ledger_invariant_catches_an_overdraft` makes sure the
invariant actually fires: a debit of 900 paise against a 500-paise balance returns `False`. That is nine
tests in `test_dependability.py`, each naming the failure it defends against.

## Step 4: the carried tests

Keep your interoperable tests (`tests/test_api.py`, `tests/test_native.py`) and the maintainable-layer
tests exactly as they were. They pass unchanged, because this assignment added a dependability layer
beside the edge; it did not alter the scoring formula, the request contract, or the model. That they
keep passing with no edit is itself a small proof of the layering: the new guarantees grew next to the
existing edge without disturbing it.

## Step 5: green gate and commit

```bash
poetry run pytest -q          # 29 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "dependable: exactly-once idempotency, atomic writes, readiness, metrics, structured logs"
```

The 29 come together as the nine new dependability tests in `test_dependability.py` on top of the
carried interoperable and maintainable tests, all still green. ruff and mypy strict are both clean.

Confirm the batch summary is unchanged while you are here:

```bash
poetry run transactions summary
```

```text
[timed] summary: 0.3 ms
[dev] transactions-insight
transactions: 5
accounts    : 3
rejected    : 2
```

## Done when

- `atomic_append(rows, record, on_prepared)` is two-phase: an interruption at the `on_prepared` hook
  leaves the store whole or empty, never a half and never a duplicate.
- `TransactionStore.add(...)` returns `(stored, created)`, records exactly one transaction for a
  repeated idempotency key, and returns the first stored result on every replay, all under one lock.
- `POST /v1/transactions` honors an `Idempotency-Key` header or a body `idempotency_key` (header wins),
  and the webhook write routes through the same store.
- `GET /ready` reports `503` when saturated and `200` normally, while `GET /health` stays a plain
  always-200 liveness check.
- The `observe` middleware carries the trace id, tracks in-flight load, times the call, and records one
  metric and one structured log line per request, logging a `request.error` at 500 on an exception.
- `GET /metrics` renders `requests_total`, `errors_total`, `request_duration_ms_avg`, and
  `request_duration_ms_max` as plain text.
- `running_balance_ok(entries)` holds the ledger invariant at every step, proven over 500 generated
  sequences and refuted by an overdraft case.
- `POST /v1/score` is unchanged: the score is
  `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.
- `transactions summary` still prints `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- `pytest` reports 29 passed (nine in `test_dependability.py`), and `ruff` and `mypy` are both clean,
  and the layer is committed.

You have built the dependability layer: the same interoperable service, now carrying the two guarantees
a money edge cannot ship without. The write path is exactly-once under retry, so a lost response and a
resend record one transaction, not two; the append is all-or-nothing under a crash, so an interrupted
write leaves the store whole or empty; and readiness, metrics, and structured logs give an operator the
signals to watch it while it runs. The deliverable proof is small and sharp: submit the same idempotency
key twice and the account is charged once, interrupt a write and the store holds the whole record or
none of it. That is no data loss and an exactly-once effect, defined, defended by demonstration, and
made operable, which is exactly what money code owes at an open edge.
