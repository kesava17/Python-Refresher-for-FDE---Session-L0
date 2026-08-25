# Assignment 02 · Make transactions-insight dependable: no data loss and an exactly-once effect

> Offline practice for the Dependable chapter. You made `transactions-insight` interoperable in the
> last assignment, giving it a validated, versioned HTTP surface. Now add the dependability layer money
> code cannot ship without: never lose an accepted write, and never apply the same write twice. This is
> the financial-transactions track of the chapter's closing pair, run through the same define, defend,
> operate loop.

This is a do-it-yourself assignment. The Dependable chapter is about two qualities that are one job:
**reliable** (the promise, in numbers) and **trustworthy** (how you set the number, prove you meet it,
and watch it in production). Your interoperable transactions service already validates every request at
the edge and publishes an OpenAPI contract. But an open edge on a money service now owes two hard
guarantees at that boundary: a retry must not double-record a payment, and a crash in the middle of a
write must not leave a half-written or duplicated record. You will build the small, testable pieces
that deliver those guarantees, plus the operational surface (readiness, structured logs, SLI metrics)
that lets an on-call engineer trust the service while it runs.

Start from your interoperable `transactions-insight` project, green, with its `TransactionIn` contract,
the `/v1/score` scoring route, the paginated `POST`/`GET /v1/transactions` pair, the signed webhook,
and the trace-id middleware all in place.

## The goal

Run each reliability concern for this domain through the chapter's loop: **define** the target,
**defend** it by demonstration, and **operate** it with monitoring. Concretely:

1. Add an **exactly-once write path**. A `POST /v1/transactions` that honors an idempotency key, so
   submitting the same key twice (a retry, including one caused by a response lost on the way back to
   the client) records exactly one transaction and returns the first stored result. The key may arrive
   in an `Idempotency-Key` header or in the request body; the header wins if both are sent.
2. Add **all-or-nothing writes**. A two-phase `atomic_append` so an interruption during a write leaves
   the store with the whole record or none of it, never a half and never a duplicate. Prove it with a
   crash-in-the-middle test.
3. Add a **readiness endpoint** distinct from liveness. `GET /ready` reports `503` when the service is
   saturated, so a load balancer stops routing new work; `GET /health` stays a plain always-200
   liveness check.
4. Add **structured, leveled logging** carrying the trace id. One JSON line per event with `event`,
   `trace_id`, `duration_ms`, and `status`, so a log tool can filter by trace id and alert on status
   without parsing prose.
5. Add **SLI metrics**. A `GET /metrics` route that renders a request count, an error count, and a
   duration summary as plain text, the three signals you look at first when a service misbehaves.
6. Add a **ledger-invariant property test**. State the rule that no account's running balance ever goes
   below zero, then generate many sequences and check it holds at every step, plus one overdraft case
   that proves the invariant actually fires.

By the end you have a dependable service: a money write that is exactly-once under retry and all-or-
nothing under a crash, a readiness gauge and metrics an operator can watch, structured logs tied
together by the trace id, and a property test that pins the ledger invariant over hundreds of generated
cases. The deliverable proof is small and sharp: send the same idempotency key twice, and the account
is recorded once; interrupt a write, and the store holds the whole record or none of it.

## The starting point

You already have the interoperable transactions service: a validated `Transaction` model (frozen, money
in paise), the `LedgerService`, the `timed` decorator, the CLI composition root, and the Day 5 edge in
`api.py` (the `TransactionIn` contract, `/v1/score` leaning on the native CRC32, the paginated
transactions pair, the signed webhook, and the trace-id middleware). Reuse all of it. This assignment
adds a dependability layer beside the edge; it does not change the maintainable layer or the scoring
formula.

Keep your `transactions-insight` sample CSV (`account_id,ts,amount,currency`) with its five good INR
rows across three accounts plus the two bad rows. The batch summary target stays exactly the same:
`transactions: 5`, `accounts    : 3`, `rejected    : 2`. Money is in rupees on the wire and stored as
paise, as before. The `POST /v1/score` behavior is unchanged: the score is
`crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.

## What you have to build

1. **A dependability module.** A `dependability.py` (standard library only, so a reader can follow each
   piece end to end) holding:
   - `atomic_append(rows, record, on_prepared)`: a two-phase append. The prepare phase builds a
     complete private copy and touches nothing a reader can see; the commit phase is a single
     `list.append`, one atomic step in CPython. The `on_prepared` hook sits between the phases so a
     test can raise there to simulate a crash before the commit.
   - `TransactionStore`: an idempotency-keyed, lock-guarded store. `add(record, key, on_prepared)`
     returns a pair `(stored, created)`. `created` is `True` on the first write for a key and `False`
     on every replay; a repeated key returns the first stored result and writes nothing. The lookup,
     the append, and the key registration all happen under one lock.
   - `Capacity`: a readiness gauge that tracks in-flight requests against a limit, so readiness can
     report saturation.
   - `Metrics`: a tiny SLI collector (a request count, an error count, and a duration summary) rendered
     as plain text, with no external metrics dependency.
   - `get_logger()` and `log_event(...)`: a shared logger and a function that emits one JSON line per
     event carrying `event`, `trace_id`, `duration_ms`, and `status`.
   - `LedgerEntry` and `running_balance_ok(entries)`: the ledger invariant stated on its own, so a
     property test can generate many sequences and check it.
2. **The wiring into `api.py`.** An `observe` middleware that replaces the plain trace-id middleware:
   it carries the trace id, tracks in-flight load through `Capacity`, times the call, and records one
   metric and one structured log line per request (logging a `request.error` at status 500 if the
   handler raises, and always freeing the capacity slot). Add `GET /ready` (503 when saturated) and
   `GET /metrics`. Route both `POST /v1/transactions` and the webhook write through the
   `TransactionStore`, and have `POST /v1/transactions` read the key from the `Idempotency-Key` header
   or the body. Keep `/health` a plain liveness check and leave `/v1/score` unchanged.
3. **The dependability tests (the deliverable).** A `tests/test_dependability.py` of nine tests, listed
   in the staged guidance below. Your interoperable tests (`test_api.py`, `test_native.py`) and the
   carried maintainable-layer tests all keep passing unchanged.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the exactly-once store

Create `dependability.py` and write `atomic_append` and `TransactionStore` first. `atomic_append`
stages a copy (`staged = dict(record)`), calls the `on_prepared` hook if one was passed, then commits
with a single `rows.append(staged)`. `TransactionStore.add` takes the lock, returns
`(self._by_key[key], False)` when the key is already present, otherwise appends through `atomic_append`,
registers the key, and returns `(stored, True)`.

Hint: the two-phase shape is the whole point. Because the commit is one atomic `list.append` and the
crash hook fires before it, a reader ever sees either no record or the whole record. The idempotency
check and the append share one lock, so a concurrent retry cannot slip a second row in between. Retry
and idempotency are two halves of one pattern; you are building both.

### Level 2: readiness, metrics, and structured logs

Add `Capacity` (an `acquire`/`release`/`is_ready` gauge over an in-flight count against a limit),
`Metrics` (a `record(duration_ms, status)` that counts requests, counts a 5xx as an error, and tracks
total and max duration, plus a `render()` that prints `requests_total`, `errors_total`,
`request_duration_ms_avg`, and `request_duration_ms_max`), and the logging pair `get_logger()` and
`log_event(logger, level, event, trace_id, duration_ms, status)` that emits one JSON line.

Hint: readiness is not liveness. `/health` proves the process is up; `/ready` proves it can take more
work right now. A stuck-but-alive process must fail readiness so the platform stops routing to it. The
metrics are the three first-look signals: how much traffic, how many failures, how slow.

### Level 3: the ledger invariant

Add the frozen `LedgerEntry(account_id, amount_paise)` dataclass and `running_balance_ok(entries)`,
which applies the entries in order and returns `False` the moment any account's running balance would
go below zero, `True` otherwise.

Hint: a financial ledger must hold this at every step, not only at the end, so a debit can never take an
account overdrawn. The API enforces the matching real-world rule by accepting only positive amounts
(`amount` greater than 0), which is why the live store can never violate it; stating the invariant on
its own is what lets a property test generate many sequences and check it.

### Level 4: wire the dependability layer into the API

In `create_app()`, build a `TransactionStore`, a `Capacity`, a `Metrics`, and the shared logger, each
owned per app instance so tests stay independent. Replace the plain trace-id middleware with an
`observe` middleware that acquires capacity, times the call in a `try`/`except`/`finally`, records a
metric and a structured log line (a `request.error` at 500 on an exception, a `request` at the real
status otherwise), releases capacity in `finally`, and echoes the trace id. Add `GET /ready` (a `503`
with `{"status": "saturated"}` when `capacity.is_ready()` is false) and `GET /metrics`
(`metrics.render()` as plain text). Change `POST /v1/transactions` to read the key from an
`Idempotency-Key` header or `txn.idempotency_key` (header wins) and store through `store.add`, and route
the webhook write through `store.add` too, using a webhook `id` as the key when present.

Hint: bump the app version to `0.6.0`, matching `pyproject.toml`. `/v1/score` does not change, and
`/health` stays a plain always-200 liveness check separate from `/ready`.

### Level 5: the dependability tests (the deliverable)

In `tests/test_dependability.py`, build a fresh app per test with `TestClient(create_app())`. Write nine
tests, grouped by the failure each one defends against:

- **Exactly-once idempotency (three tests).**
  - `test_same_key_twice_records_one_and_returns_the_same_result`: POST the same body twice with the
    same `Idempotency-Key` header (a lost-response retry). Assert both return `201`, the two JSON bodies
    are identical, and `GET /v1/transactions` reports `total == 1`.
  - `test_a_key_in_the_body_is_honoured_too`: send the key in the body as `idempotency_key`, POST twice,
    and assert `total == 1`.
  - `test_no_key_records_each_call`: with no key, POST twice and assert `total == 2` (no key, no
    idempotency promise).
- **Crash in the middle (one test).** `test_crash_in_the_middle_stores_none_then_a_retry_stores_exactly_one`:
  call `store.add(record, key="k1", on_prepared=crash)` where `crash` raises, assert the store length is
  `0` (whole or none, never a partial row), then a clean retry stores exactly one with `created is True`.
- **Readiness (one test).** `test_ready_returns_200_normally`: `GET /ready` returns `200` and
  `{"status": "ready"}` under normal load.
- **Health (one test).** `test_health_stays_plain_liveness`: `GET /health` still answers
  `{"status": "ok"}`.
- **Metrics (one test).** `test_metrics_report_request_and_error_counts`: after a request, `GET /metrics`
  text contains `requests_total`, `errors_total`, and `request_duration_ms_avg`.
- **Ledger invariant (two tests).**
  - `test_ledger_invariant_holds_over_many_generated_sequences`: with a seeded `random.Random(1234)`,
    generate 500 sequences that by construction never overdraw (each step credits a random amount or
    debits at most the current balance) and assert `running_balance_ok(...)` is `True` for each.
  - `test_ledger_invariant_catches_an_overdraft`: a credit of 500 paise followed by a debit of 900 paise
    breaks the invariant, so `running_balance_ok(...)` is `False`.

Hint: the exactly-once test is the deliverable's heart. A retry that arrives because the first response
was lost must not charge the account twice, and the store proves it: one row, same result. The
crash-in-the-middle test is the other half of no-data-loss: an interrupted write leaves nothing behind,
so a later retry stores exactly one, never two. hypothesis is not a base dependency, so the property
test seeds its own random source (repeatable, no new heavy dependency).

### Level 6: green gate and commit

Run ruff and mypy strict, make the new dependability tests and the carried interoperable and
maintainable tests all pass, confirm the batch summary output is unchanged, then commit the
dependability layer on top of your interoperable project.

## Done when

- [ ] `atomic_append(rows, record, on_prepared)` is two-phase: an interruption at the `on_prepared` hook
  leaves the store whole or empty, never a half and never a duplicate.
- [ ] `TransactionStore.add(...)` returns `(stored, created)`, records exactly one transaction for a
  repeated idempotency key, and returns the first stored result on every replay, all under one lock.
- [ ] `POST /v1/transactions` honors an `Idempotency-Key` header or a body `idempotency_key` (header
  wins), and the webhook write routes through the same store.
- [ ] `GET /ready` reports `503` when saturated and `200` with `{"status": "ready"}` normally, while
  `GET /health` stays a plain always-200 liveness check.
- [ ] The `observe` middleware carries the trace id, tracks in-flight load, times the call, and records
  one metric and one structured log line per request (a `request.error` at 500 on an exception).
- [ ] `log_event(...)` emits one JSON line per event with `event`, `trace_id`, `duration_ms`, and
  `status`.
- [ ] `GET /metrics` renders `requests_total`, `errors_total`, `request_duration_ms_avg`, and
  `request_duration_ms_max` as plain text.
- [ ] `running_balance_ok(entries)` holds the ledger invariant at every step, proven over 500 generated
  sequences and refuted by an overdraft case.
- [ ] `POST /v1/score` is unchanged: the score is
  `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.
- [ ] `tests/test_dependability.py` holds nine tests: three idempotency (header, body, no-key control),
  crash-in-the-middle, readiness, health, metrics, and the two ledger-invariant tests.
- [ ] `transactions summary` still prints `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- [ ] `pytest` reports 29 passed, and `ruff check` and `mypy src` are both clean, and the layer is
  committed.

When every box is ticked, you have built the dependability layer: the same interoperable service, now
carrying the two guarantees a money edge cannot ship without. Submit the same idempotency key twice and
the account is recorded once; interrupt a write and the store holds the whole record or none of it;
watch `/ready` and `/metrics` and follow one request across the logs by its trace id. That is no data
loss and an exactly-once effect, defined, defended by demonstration, and made operable. The worked
solution is in `solution-02.md` if you want to compare, but try first.
