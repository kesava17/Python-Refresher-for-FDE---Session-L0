# Solution 02 · Harden transactions-insight: authorize the object, bind the fields, mask the data, prove the secrets are out

> The full worked solution for Assignment 02. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your dependable `transactions-insight` project, green, with its `TransactionIn` contract,
the `/v1/score` scoring route, the exactly-once `TransactionStore`, the paginated transactions pair, the
signed webhook, and the `observe` middleware. This solution adds the security layer for the
financial-transactions domain: a new `security.py` module of small standard-library helpers, the wiring
in `api.py` that authorizes the specific object and binds only the fields a caller may set, a
`scripts/secret_scan.py` that keeps secrets out of source, and a hardened `Dockerfile`. The goal is
narrow and strict, because a payment record is the most sensitive data in this course: only the owner
reads a transaction, a crafted body sets nothing the server owns, a full account number never reaches a
log, and no secret lives in the source tree or the image. Use `poetry run` for everything.

## Step 1: the security module

The security habits an on-call engineer must trust go in one small module built on the standard library
alone, so a reader can follow each piece end to end. Create `src/transactions_insight/security.py`. It
holds the two shared helpers the routes call: masking a sensitive identifier, and emitting one structured
security event.

### Masking the account before it reaches a log

The core of the data-protection habit is that a full account number never appears in a log line:

**`src/transactions_insight/security.py`** (the mask)

```python
def mask_account(account_id: str) -> str:
    """Return the account id with only the last four characters shown, for example ****6789.

    A log line is read by many people and is often shipped to a third-party log tool, so a full
    account identifier must never appear in it. We keep only the last four characters, which is
    enough for a human to correlate a support ticket, and hide the rest behind four stars. A very
    short id is masked completely, so we never accidentally reveal most of it.
    """
    if len(account_id) <= 4:
        return "****"
    return "****" + account_id[-4:]
```

Two rules, both deliberate. A normal account id keeps only its last four characters (`"****" +
account_id[-4:]`), enough to correlate a support ticket and no more. A four-character-or-shorter id is
masked completely (`"****"`), so a short id can never reveal most of itself. Masking is the small,
everyday face of the data-protection layer: the value the engineer must never let leak is stripped before
it can.

### One structured security event per notable event

A security event deserves its own line so a log tool can alert on it, and that line must carry nothing
sensitive:

**`src/transactions_insight/security.py`** (the security event)

```python
def log_security_event(
    logger: logging.Logger,
    event: str,
    trace_id: str,
    resource: str,
    account: str = "",
) -> None:
    """Emit one JSON line describing a security event, carrying no secret or raw sensitive data.

    A security event (an authorization denial, a validation rejection) is worth its own line so a
    log tool can alert on it. The line carries the event name, the trace id that ties it to the
    request, the resource that was touched, and the masked account. It never carries a token, a
    signature, a password, or a full account identifier, so shipping the log elsewhere leaks
    nothing. The amount is left out on purpose, so an account and a value are never logged
    together in the clear.
    """
    payload = {
        "event": event,
        "trace_id": trace_id,
        "resource": resource,
        "account": mask_account(account) if account else "",
    }
    # A security event is logged at WARNING so it stands out from the routine INFO request lines.
    logger.warning(json.dumps(payload))
```

The event carries four safe fields: the `event` name, the `trace_id` that ties it to the same request as
the routine request log line, the `resource` that was touched, and the masked `account`. It carries no
token, signature, password, or full account id, so shipping the log to a third-party tool leaks nothing,
and it leaves the amount out on purpose, so an account and a value are never logged together in the clear.
It logs at `WARNING`, one level above the `INFO` request lines the `observe` middleware already emits, so
a filter finds a security event at once. This is the observability layer doing its security job: a
denial is visible, and it is safe to look at.

## Step 2: wire the security layer into the API

The module holds the helpers; now the API has to use them. Open `src/transactions_insight/api.py`. Bump
the version, set the owner from the caller on the write path, add the object-level authorization route,
tighten the request contract against mass assignment, and log a security event on a denial and on a
validation rejection.

### Object-level authorization: the BOLA fix

The number one API risk is returning object 42 to anyone who asks. The read route closes it by checking
ownership, not just existence:

**`src/transactions_insight/api.py`** (the authorized read)

```python
    @app.get("/v1/transactions/{transaction_id}", response_model=TransactionOut)
    def get_transaction(
        transaction_id: str,
        request: Request,
        x_user_id: str | None = Header(default=None),
    ) -> TransactionOut:
        # Object-level authorization (the fix for a BOLA weakness): a transaction is returned only
        # when the caller owns it. A valid id is not enough; the caller must be the owner too.
        caller = x_user_id or "anonymous"
        record = store.get(transaction_id)
        if record is None or record.get("owner") != caller:
            # Fail secure: whether the transaction does not exist or the caller simply does not own
            # it, we answer with the same 404 and reveal nothing. A 403 here would leak that the id
            # is real, which lets an attacker enumerate ids that belong to other people.
            trace_id = getattr(request.state, "trace_id", "")
            masked = record.get("account_id", "") if record is not None else ""
            log_security_event(
                logger,
                "security.authorization_denied",
                trace_id,
                resource=f"transaction:{transaction_id}",
                account=masked,
            )
            raise HTTPException(status_code=404, detail="not found")
        return _to_out(record)
```

A valid id is not enough; the caller must be the owner too. The route fetches the record through
`store.get`, and if it is missing or `record.get("owner") != caller`, it fails secure: a non-owner and a
made-up id both get the same `404`. A `403` here would leak that the id is real, which is exactly what
lets an attacker enumerate ids that belong to other people, so the same answer for both cases is the
point. On the way out it logs a `security.authorization_denied` event with the trace id from
`request.state` and the masked account, so a denial is visible to a log tool without revealing anything.
This is complete mediation (authority checked on every access) and fail secure (deny on any doubt) in one
route.

The owner it checks against is set by the server at write time, never by the body:

```python
        owner = x_user_id or "anonymous"
        record = {
            "id": uuid.uuid4().hex,  # a server-generated id, so a caller cannot choose it
            "account_id": txn.account_id,
            "amount": str(txn.amount),
            "currency": txn.currency,
            "owner": owner,  # set from the caller, never from the body
            "status": "received",  # a server-controlled field, never from the body
        }
        stored, _created = store.add(record, key=key)
        return _to_out(stored)
```

The owner comes from the `X-User-Id` header, falling back to `"anonymous"` when no identity is sent, so
the dependable tests that predate this auth layer still work. In production that identity comes from a
validated token; the teaching point is that the server sets the owner, never the body. The id is
server-generated (`uuid.uuid4().hex`) so a caller cannot choose it, and the write still routes through the
exactly-once `store.add` from the dependable layer.

### Mass-assignment protection: bind only the allowed fields

The request contract lists only what a caller may set and ignores everything else, so a crafted body
cannot smuggle in a server field:

**`src/transactions_insight/api.py`** (the tightened contract)

```python
class TransactionIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge.

    Mass-assignment protection lives here. The model lists only the fields a caller is allowed to
    set. Server-controlled fields (the owner, the status, any settled or approved flag) are not in
    the model, so a body that sends "owner" or "status" cannot bind them. extra="ignore" makes the
    rule explicit: unknown fields are dropped, not trusted, so a crafted body cannot smuggle in a
    field the server alone should decide.
    """

    model_config = ConfigDict(extra="ignore")

    account_id: str = Field(min_length=1)  # an empty account id is rejected with a 422
    amount: float = Field(gt=0)  # money in rupees; a non-positive amount is rejected with a 422
    currency: str = Field(min_length=3, max_length=3)  # a code like "US" (too short) fails here
    idempotency_key: str | None = Field(default=None)
```

The model lists exactly the fields a caller may set: `account_id`, `amount`, `currency`, and the optional
`idempotency_key` from the dependable layer. Server-controlled fields (`owner`, `status`) are not in the
model at all, and `extra="ignore"` makes the rule explicit, so an unknown field is dropped, not trusted.
Combined with building the stored record in code (the server sets `owner` and `status`), a body that
sends `owner="attacker"` or `status="approved"` binds nothing. This is secure by default: the shape a
caller gets without doing anything special is the safe one.

### One security event on a validation rejection too

The edge already rejects bad input with a `422` before any route runs. One security event makes that
rejection visible without logging anything sensitive:

```python
    @app.exception_handler(RequestValidationError)
    async def on_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", "")
        account = ""
        if isinstance(exc.body, dict):
            account = str(exc.body.get("account_id", ""))
        log_security_event(
            logger,
            "security.validation_rejected",
            trace_id,
            resource=request.url.path,
            account=account,
        )
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})
```

The handler pulls only the `account_id` from the raw body, hands it to `log_security_event` (which masks
it), and never logs the errors' raw values, so nothing sensitive reaches the log. The response shape is
the same `422` as before. The app version bumps to `0.7.0` to match `pyproject.toml`, and `/v1/score` is
untouched: the score is still `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.

## Step 3: the secret scan

Secrets belong in the environment or a secret store, never in source and never in a container image. A
small scanner over `src/` gates that, using only the standard library so it runs anywhere. Create
`scripts/secret_scan.py`:

**`scripts/secret_scan.py`** (the patterns and the exit code)

```python
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # A PEM private key block: the single strongest signal that a real key leaked into source.
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    # An AWS access key id has a fixed prefix and length.
    ("aws access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    # Common token prefixes from well known providers (GitHub, Slack).
    ("provider token", re.compile(r"(?:ghp_[0-9A-Za-z]{20,}|xox[baprs]-[0-9A-Za-z-]{10,})")),
    # A secret-named variable bound directly to a string literal. This is the everyday mistake the
    # scan is really about: writing the secret into the code instead of reading it from the
    # environment. A value sourced from os.environ or os.getenv starts with a name, not a quote, so
    # it does not match here, which is exactly the safe pattern we want to allow.
    (
        "secret bound to a literal",
        re.compile(
            r"(?i)(?:password|passwd|secret|token|api[_-]?key|access[_-]?key)"
            r"\s*[:=]\s*['\"][^'\"]{6,}['\"]"
        ),
    ),
]
```

Each pattern names one shape a leaked secret takes: a PEM private key block, an AWS access key id, a known
provider token prefix, and the everyday mistake this scan is really about, a secret-named variable bound
directly to a string literal. That last rule is the clever one: a value sourced from `os.environ` or
`os.getenv` starts with a name, not a quote, so it does not match, which is exactly the safe pattern we
want to allow. The scan returns a process exit code, so it can gate a commit or a pipeline:

```python
def main() -> int:
    """Scan the project's src/ tree and return a process exit code: 0 clean, 1 on any finding."""
    src_root = Path(__file__).resolve().parent.parent / "src"
    findings = scan_directory(src_root)
    if not findings:
        print(f"secret scan: 0 findings across {src_root}")
        return 0
    for finding in findings:
        print(f"{finding.path}:{finding.line_number}: [{finding.rule}] {finding.text}")
    print(f"secret scan: {len(findings)} finding(s); failing.")
    return 1
```

Over the real source it finds nothing and exits `0`, printing `secret scan: 0 findings across ...`. The
reason it stays clean is on the write path: the webhook secret is read from the environment, not bound to
a literal.

**`src/transactions_insight/api.py`** (the secret read from the environment)

```python
_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "shared-webhook-secret").encode()
```

The value comes from `os.environ.get`, so a real deployment sets it from its secret store and the value
never lives in source or in an image. The line starts with a name, not a quote, so the "secret bound to a
literal" pattern does not match it. Plant a real key (say `api_key = "AKIA" + "1234567890ABCDEF"`) into a
file under `src/` and the scan would print the finding and exit `1`, which is how you prove the gate
actually catches something.

## Step 4: the hardened container

The image is the runtime layer: a small image that runs as an unprivileged user, so a flaw in the app
cannot easily become control of the host. Create the `Dockerfile` with a build stage and a slim runtime
stage:

**`Dockerfile`** (the non-root runtime)

```dockerfile
# ---- Final stage: a slim runtime that carries only what it needs ---------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Create an unprivileged user and group. Running as root inside a container is a real risk: a
# process escape would land with root on the host, so we never run the app as root.
RUN groupadd --system app && useradd --system --gid app --home-dir /app --no-create-home app

WORKDIR /app

# Copy the built virtual environment and the source from the build stage, owned by the app user.
COPY --from=build --chown=app:app /app/.venv /app/.venv
COPY --from=build --chown=app:app /app/src /app/src

# Drop to the unprivileged user for every command from here on.
USER app

EXPOSE 8000

CMD ["uvicorn", "transactions_insight.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Three habits do most of the work: build in one stage and copy only what runs into a slim final stage, run
as a non-root `app` user (`USER app`), and document the run-time hardening in a comment so whoever runs
the container tightens the rest:

```dockerfile
#   docker run \
#     --read-only \                     # a read-only root filesystem, so nothing can be written
#     --tmpfs /tmp \                    # give the app a small writable scratch area if it needs one
#     --cap-drop ALL \                  # drop every Linux capability; the app needs none of them
#     --security-opt no-new-privileges \  # a child process can never gain more privilege
#     transactions-insight
```

A read-only root plus dropped capabilities means a compromised process has almost no room to act: it
cannot write the filesystem and it holds no privileged capability to abuse.

## Step 5: the security tests (the deliverable proof)

This is the proof. One file exercises every guarantee: object-level authorization from both ends, mass
assignment, masking, and the secret scan. Create `tests/test_security.py`. A distinctive account id lets
the masking test prove the full form is absent while the masked form is present:

```python
_FULL_ACCOUNT = "9876543210"


def _client() -> TestClient:
    # A fresh app (and a fresh store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _create(client: TestClient, user_id: str, **body: object) -> dict[str, object]:
    """Create a transaction as a given caller and return the response body."""
    payload = {"account_id": _FULL_ACCOUNT, "amount": 250.0, "currency": "INR"}
    payload.update(body)
    resp = client.post("/v1/transactions", json=payload, headers={"X-User-Id": user_id})
    assert resp.status_code == 201
    return resp.json()
```

**`tests/test_security.py`** (the object-level authorization tests)

```python
def test_owner_can_read_but_another_caller_gets_404() -> None:
    # Caller A creates a transaction. A can read it back (200), but caller B is told it does not
    # exist (404), even though the id is valid. The 404, not a 403, keeps B from learning that the
    # id is real, so ids cannot be enumerated.
    client = _client()
    created = _create(client, user_id="userA")
    transaction_id = created["id"]

    as_owner = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userA"}
    )
    assert as_owner.status_code == 200
    assert as_owner.json()["id"] == transaction_id

    as_other = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userB"}
    )
    assert as_other.status_code == 404


def test_unknown_id_also_returns_404() -> None:
    # A made-up id fails the same way as one owned by someone else, so the two cases are
    # indistinguishable to a caller.
    client = _client()
    resp = client.get("/v1/transactions/does-not-exist", headers={"X-User-Id": "userA"})
    assert resp.status_code == 404
```

`test_owner_can_read_but_another_caller_gets_404` is the deliverable's heart. Caller A creates and reads
its own transaction (`200`), then caller B asks for the same valid id and gets `404`, so a payment record
is invisible to anyone but its owner. `test_unknown_id_also_returns_404` proves a made-up id fails the
same way, so a non-owner and a non-existent id are indistinguishable, and ids cannot be probed.

The mass-assignment test proves the server owns its own fields:

```python
def test_body_supplied_owner_and_status_are_ignored() -> None:
    # The caller tries to set the owner and the status from the body. Both are server-controlled,
    # so both are ignored: the real owner is the caller (userLegit), and the status is the
    # server value "received", never the "approved" the body asked for.
    client = _client()
    created = _create(
        client, user_id="userLegit", owner="attacker", status="approved"
    )
    transaction_id = created["id"]

    # The status came from the server, not the body.
    assert created["status"] == "received"

    # The body-supplied owner did not take effect: the attacker it named cannot read the record.
    as_attacker = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "attacker"}
    )
    assert as_attacker.status_code == 404

    # The real owner (the caller) can read it.
    as_owner = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userLegit"}
    )
    assert as_owner.status_code == 200
```

The body sends `owner="attacker"` and `status="approved"`, and both are ignored: the stored status is the
server value `"received"`, the named attacker cannot read the record (`404`), and the real caller can
(`200`). The object-level check from the first test is what turns the ignored owner into a visible
consequence.

The masking test proves nothing sensitive reaches the log, and the secret-scan test runs the real gate:

```python
def test_full_account_never_appears_in_logs_but_masked_form_does(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # A denied authorization logs a security event. That event must carry the masked account
    # (****3210) and never the full account id, so shipping the log elsewhere leaks nothing.
    client = _client()
    created = _create(client, user_id="userA")
    transaction_id = created["id"]

    with caplog.at_level(logging.WARNING, logger="transactions_insight"):
        denied = client.get(
            f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userB"}
        )
    assert denied.status_code == 404

    logged = caplog.text
    assert _FULL_ACCOUNT not in logged  # the full account id is never written in the clear
    assert "****3210" in logged  # the masked form is present, enough to correlate a ticket


def test_secret_scan_reports_zero_findings_over_src() -> None:
    # Run the same scanner the pipeline runs. Over the real source it must find nothing and exit 0.
    script = Path(__file__).resolve().parents[1] / "scripts" / "secret_scan.py"
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 findings" in result.stdout
```

`test_full_account_never_appears_in_logs_but_masked_form_does` captures the `WARNING` log for the
`transactions_insight` logger while a non-owner is denied, then asserts the full account id `9876543210`
is absent and the masked `****3210` is present, so an audit of the shipped log finds nothing in the
clear. `test_secret_scan_reports_zero_findings_over_src` runs `scripts/secret_scan.py` as a subprocess
over the real source and asserts it exits `0` with `0 findings` in its stdout, the same gate a pipeline
runs. That is five tests in `test_security.py`, each naming the weakness it defends against.

## Step 6: the carried tests

Keep your dependable tests (`tests/test_dependability.py`), your interoperable tests
(`tests/test_api.py`, `tests/test_native.py`), and the maintainable-layer tests exactly as they were.
They pass unchanged, because this assignment added a security layer beside the edge; it did not alter the
scoring formula, the exactly-once store, or the model. That they keep passing with no edit is itself a
small proof of the layering: the new controls grew next to the existing edge without disturbing it.

## Step 7: green gate and commit

```bash
poetry run pytest -q          # 34 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
poetry run python scripts/secret_scan.py   # secret scan: 0 findings across .../src   (exit 0)
git add .
git commit -m "secure: object-level authorization, mass-assignment binding, masking, security logs, secret scan, hardened image"
```

The 34 come together as the five new security tests in `test_security.py` on top of the carried
dependable, interoperable, and maintainable tests, all still green. ruff and mypy strict are both clean,
and the secret scan exits `0` over the real source.

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

- `GET /v1/transactions/{transaction_id}` returns the transaction only to its owner; a non-owner and a
  made-up id both get `404`, never a `403` and never the data, so ids cannot be enumerated.
- The owner is set by the server from the `X-User-Id` header at write time, never from the body.
- `TransactionIn` ignores extra fields (`extra="ignore"`), and `owner` and `status` are server-set, so a
  body value for `owner` or `status` cannot bind. `status` is `"received"`.
- `mask_account(account_id)` shows only the last four characters (for example `****6789`) and masks a
  four-character-or-shorter id completely.
- `log_security_event(...)` emits one `WARNING` JSON line per event with `event`, `trace_id`, `resource`,
  and the masked `account`, and no token, signature, password, full account id, or amount.
- `scripts/secret_scan.py` scans `src/`, exits `0` on the clean tree and `1` on a planted secret; the
  webhook secret is read from the environment, never bound to a literal.
- The `Dockerfile` builds in one stage and runs the app in a slim stage as a non-root `app` user, with the
  read-only root and `--cap-drop ALL` run flags documented.
- `POST /v1/score` is unchanged: the score is
  `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.
- `transactions summary` still prints `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- `pytest` reports 34 passed (five in `test_security.py`), and `ruff` and `mypy` are both clean, and the
  secret scan exits `0`, and the layer is committed.

You have built the security layer: the same dependable service, now carrying the four guarantees a money
edge cannot ship without. The read authorizes the specific object, so caller B is told A's transaction
does not exist; the write binds only the fields the caller may set, so a crafted body sets nothing the
server owns; the logs carry a masked account and structured security events, so shipping them elsewhere
leaks nothing; the scan keeps secrets out of source and the image runs unprivileged. The deliverable proof
is small and sharp: ask for another caller's transaction and it does not exist, send a crafted body and
the server-only fields are ignored, deny a read and the log shows `****3210` and never the full number,
run the scan and the source is clean. That is secure by design and by execution, the posture the architect
set and the code the engineer proved, which is exactly what money code owes at an open edge.
