# Solution 01 · Make telemetry-insight secure by design and execution

> The full worked solution for Assignment 01. Try the assignment yourself first. This is here to
> check your work, or to unstick you when you're truly stuck.

You start from your `telemetry-insight` project, green, with the dependability layer already in place.
This solution adds the security layer, tuned for the telemetry domain where the readings are owned by
devices and a device owner's contact is sensitive: object-level authorization on a single-reading
route, mass-assignment protection at the ingest contract, sensitive-field masking, a secret scanner,
and a hardened non-root container. Each control runs the chapter's pair: an architect's blueprint
that sets the posture, and an engineer's realization that makes the code hold it and fail secure. Use
`poetry run` for everything.

The result you are after: the summary behaviour is unchanged, `telemetry summary` still prints five
valid readings, three devices, and two rejected rows, but the service now proves who may read a
reading, drops a body that tries to claim ownership, keeps a raw contact out of every log, and refuses
to let a hard-coded secret into the source.

## Step 1: the security helpers

A log is a real attack surface: anything sensitive that lands in a log line can leak, so we mask
before we write, never after. **Blueprint:** a device-owner contact and a caller identity are
sensitive, so neither is ever recorded in the clear. **Realization:** small standard-library masking
helpers, plus a structured security-event logger that carries the trace id and the resource but no
secrets and no raw personal data.

**`src/telemetry_insight/security.py`**

```python
"""Security helpers for the hardened layer.

This module holds the small, dependency-light pieces the security layer needs, all
built on the standard library:

- A masking helper for sensitive contact fields, so a raw email never reaches a log.
- A caller-identity masking helper, so we can record who was denied without leaking the
  full identity.
- A structured security-event logger that carries the trace id and the affected resource
  but no secrets and no raw personal data.

The teaching point is that logs are a real attack surface. Anything sensitive that lands
in a log line can leak, so we mask before we write, never after.
"""

from __future__ import annotations

import re

from telemetry_insight.observability import log_event

# A simple email shape. We only need to split the local part from the domain so we can mask
# the local part. This is not full email validation, just enough to mask safely.
_EMAIL_RE = re.compile(r"^([^@]+)@(.+)$")


def _mask_token(value: str) -> str:
    """Keep the first character and replace the rest with asterisks."""
    if not value:
        return "****"
    return value[0] + "*" * max(len(value) - 1, 1)


def mask_email(value: str) -> str:
    """Return a masked form of an email that is safe to log."""
    match = _EMAIL_RE.match(value)
    if match is None:
        # Not an email shape: mask the whole value rather than risk leaking it.
        return "****"
    local, domain = match.group(1), match.group(2)
    return f"{_mask_token(local)}@{domain}"


def mask_caller(caller: str) -> str:
    """Mask a caller identity for logging, keeping only the first character."""
    return _mask_token(caller)


def log_security_event(
    event: str, trace_id: str, resource: str, caller: str, status: int
) -> None:
    """Emit one structured security event: no secrets, no raw personal data."""
    log_event(
        event,
        trace_id,
        0.0,
        status,
        resource=resource,
        caller=mask_caller(caller),
    )
```

`mask_email` keeps the first character of the local part and the whole domain, so
`alice@example.com` becomes `a****@example.com`: enough for an operator to recognize a pattern, never
enough to read the address. A value that is not email-shaped is masked whole, so an unexpected raw
value never leaks. `log_security_event` masks the caller before the line is built and reuses the
package's own `log_event`, so a security event is one structured JSON line like every other, carrying
the event name, the trace id, the resource, the masked caller, and a status.

## Step 2: the security layer on the API

The service becomes secure by execution here. On top of the dependability surface (idempotency, load
shedding, the sink, readiness, the SLI metrics) sit four security behaviours: object-level
authorization on a single-reading route, mass-assignment protection at the ingest contract, a
server-set owner, and sensitive-field masking, with structured security events for a denial and a
validation rejection.

**`src/telemetry_insight/api.py`** (the security additions; the dependability code is carried forward)

The module docstring names the layer, and the identity and owner constants make the posture explicit.
The webhook secret is read from the environment, never hard-coded:

```python
# The webhook secret comes from the environment, never hard-coded in the source. The literal
# here is only a dev fallback so the local tests run without extra setup.
_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "shared-webhook-secret").encode("utf-8")

# The header that carries the caller identity. In production this is a validated token; the
# teaching point here is the authorization check, so we read a plain header for the identity.
_CALLER_HEADER = "x-user-id"

# The owner recorded when a request carries no caller identity, so an anonymous ingest still
# stores a valid record and can never accidentally match a real owner.
_ANONYMOUS_OWNER = "anonymous"

# The owner recorded for a signed webhook, which is a server-to-server call with no end user.
_SYSTEM_OWNER = "system"


def _caller_id(request: Request) -> str:
    return request.headers.get(_CALLER_HEADER) or _ANONYMOUS_OWNER


def _make_record(
    device_id: str, value: object, owner_id: str, contact_email: str = ""
) -> dict[str, str]:
    # Build one stored record with a server-generated id and a server-set owner. Callers never
    # supply the id or the owner, which is what closes the mass-assignment hole.
    return {
        "reading_id": uuid.uuid4().hex,
        "device_id": device_id,
        "value": str(value),
        "owner_id": owner_id,
        "contact_email": contact_email,
    }
```

Reading the caller from `X-User-Id` stands in for a validated token, and defaulting a missing
identity to `anonymous`, a value no real owner can hold, keeps an anonymous ingest safe. `_make_record`
sets the `reading_id` and `owner_id` on the server, so a caller can never supply either. The
`ReadingIn` contract is the mass-assignment boundary:

```python
class ReadingIn(BaseModel):
    """The request contract, and the mass-assignment boundary.

    This model declares exactly the fields a caller is allowed to set. Pydantic ignores any
    other key in the JSON body by default, so a body that also carries `owner_id` or a `status`
    flag has those extra keys dropped here.
    """

    device_id: str = Field(min_length=1)
    value: float = Field(ge=-50, le=150)  # a value outside -50 to 150 is rejected with a 422
    key: str | None = Field(default=None, min_length=1)
    # Optional device-owner contact. A caller may set it, but it is sensitive, so it is never
    # logged raw, only in a masked form (see the ingest handler).
    contact_email: str | None = Field(default=None, min_length=1)
```

The value range stays `-50` to `150`, so readings can be negative and out of a small range, exactly
what a real sensor produces. The model declares only the four fields a caller may set; pydantic drops
any other key, so a body carrying `owner_id` or `status` loses those at the bind. The factory reports
`version="0.7.0"` and wires the middleware and a validation handler:

```python
def create_app(
    max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
    sink_client: httpx.AsyncClient | None = None,
) -> FastAPI:
    configure_logging()
    app = FastAPI(title="telemetry-insight", version="0.7.0")
    store: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    capacity = Capacity(max_concurrent)
    metrics = Metrics()
    app.state.capacity = capacity
    app.state.metrics = metrics

    # ... the observe() middleware (trace id, SLI sample, one log line per request) is
    # carried forward from the dependability layer unchanged ...

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: Exception) -> JSONResponse:
        # A rejected body is a security-relevant event: someone sent input the contract does
        # not allow. We record a structured security event (masked caller, no raw body) and
        # return a plain 422 that does not echo the offending input back to the caller.
        trace_id = getattr(request.state, "trace_id", "")
        log_security_event(
            "validation_rejected", trace_id, request.url.path, _caller_id(request), 422
        )
        return JSONResponse({"detail": "validation error"}, status_code=422)
```

The validation handler turns a rejected body into a `validation_rejected` security event with a
masked caller, and returns a plain 422 that does not echo the offending input. The ingest handler
sets the owner from the caller and masks the contact:

```python
    @app.post("/v1/readings", status_code=201, response_model=ReadingAccepted)
    async def ingest(reading: ReadingIn, request: Request) -> ReadingAccepted:
        if not capacity.try_acquire():
            raise HTTPException(status_code=429, detail="load shed: no free capacity")
        try:
            # The owner is taken from the caller identity, never from the request body. Even if
            # the body tried to carry an owner_id, ReadingIn does not bind it, so it is gone.
            owner_id = _caller_id(request)

            key = reading.key or request.headers.get("idempotency-key")
            if key is not None and key in seen_keys:
                return ReadingAccepted(status="duplicate")

            # ... optional sink forwarding, carried forward ...

            # Never log the raw contact email. If one was sent, log only its masked form.
            if reading.contact_email is not None:
                log_event(
                    "reading_ingested",
                    request.state.trace_id,
                    0.0,
                    201,
                    device_id=reading.device_id,
                    contact=mask_email(reading.contact_email),
                )

            record = _make_record(
                reading.device_id,
                reading.value,
                owner_id,
                reading.contact_email or "",
            )
            store.append(record)
            if key is not None:
                seen_keys.add(key)
            return ReadingAccepted(status="accepted", id=record["reading_id"])
        finally:
            capacity.release()
```

The owner is set from `_caller_id`, never from the body, which is what closes the mass-assignment
hole. The optional contact is logged only through `mask_email`, so the raw address never reaches a
line. The owner-scoped read is the object-level authorization check:

```python
    @app.get("/v1/readings/{reading_id}", response_model=ReadingDetail)
    def get_reading(reading_id: str, request: Request) -> ReadingDetail:
        # Object-level authorization (the BOLA fix). Having a valid id is not enough: the
        # caller must own the record. A caller who is not the owner gets the same 404 as a
        # missing id, so ownership is not revealed and ids cannot be enumerated (fail secure).
        caller = _caller_id(request)
        for row in store:
            if row["reading_id"] != reading_id:
                continue
            if row["owner_id"] != caller:
                log_security_event(
                    "authz_denied",
                    request.state.trace_id,
                    f"reading:{reading_id}",
                    caller,
                    404,
                )
                raise HTTPException(status_code=404, detail="not found")
            return ReadingDetail(
                id=row["reading_id"],
                device_id=row["device_id"],
                value=float(row["value"]),
                owner_id=row["owner_id"],
            )
        # No record with that id at all: the same 404 an outsider sees for a record they do
        # not own, so the two cases are indistinguishable.
        raise HTTPException(status_code=404, detail="not found")
```

This is the fix for Broken Object Level Authorization, the number one API risk. Having a valid id is
not enough: the caller must own the record. A non-owner and a missing id both raise the same 404, so
ownership is never revealed and ids cannot be enumerated, the fail-secure choice. The denial is
recorded as an `authz_denied` security event with a masked caller. The `ReadingDetail` response
carries `owner_id` but never `contact_email`, so the sensitive field is not handed back out through
this route. The list, insight, and signed webhook routes are carried forward; the webhook still
verifies its HMAC over the raw body and owns its records as `system`.

## Step 3: keep secrets out of the source

Secrets belong in the environment, never in the source, where they would be committed to history and
shared with everyone who can read the repository. **Blueprint:** no credential literal in the tree.
**Realization:** a dependency-light scanner that runs in a pre-commit hook or CI gate and fails the
build before a secret lands.

**`scripts/secret_scan.py`**

```python
# A secret-like variable name assigned directly to a string literal, for example
# `password = "hunter2"` or `API_KEY = 's3cr3t'`.
_ASSIGNED_SECRET = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|apikey|access[_-]?key"
    r"|auth[_-]?token|private[_-]?key)\b\s*[:=]\s*['\"][^'\"]{3,}['\"]"
)

# An AWS access key id has a fixed, recognizable shape.
_AWS_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# The header line of a PEM-encoded private key.
_PRIVATE_KEY_HEADER = re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")

_PATTERNS = (_ASSIGNED_SECRET, _AWS_ACCESS_KEY, _PRIVATE_KEY_HEADER)


def _is_exempt(line: str) -> bool:
    # A comment is documentation, not a live secret. A line that reads from the environment
    # is the pattern we want, so skip it too even if it names a secret.
    stripped = line.strip()
    if stripped.startswith("#"):
        return True
    return "os.environ" in line or "getenv" in line


def find_secrets(root: Path) -> list[str]:
    """Return one human-readable finding per suspected hard-coded secret under `root`."""
    findings: list[str] = []
    for path in sorted(root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if _is_exempt(line):
                continue
            if any(pattern.search(line) for pattern in _PATTERNS):
                findings.append(f"{path}:{line_no}: possible hard-coded secret")
    return findings
```

The scanner flags a secret-like name assigned to a string literal, an AWS access key id shape, and a
PEM private-key header. It exempts comments and any line that reads from the environment, because
reading a secret from the environment is exactly the pattern you want. `main()` prints every finding
and returns 1 when the tree is dirty, or prints `secret scan: no hard-coded secrets found` and returns
0 when it is clean. The webhook secret in `api.py` is read through `os.environ.get`, so that line is
exempt and the source stays clean.

## Step 4: harden the runtime

**Blueprint:** the container is least privilege, non-root, with a locked-down runtime. **Realization:**
a slim pinned base, a non-root user, and documented run-time hardening.

**`Dockerfile`**

```dockerfile
# A slim base keeps the attack surface small. Pin a specific version for repeatable builds.
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Export a plain requirements list from Poetry at build time and install with pip, so the
# runtime image does not need Poetry itself.
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==2.4.1 \
    && poetry export --without-hashes --output requirements.txt \
    && pip install --no-cache-dir --requirement requirements.txt \
    && pip uninstall --yes poetry

COPY src ./src

# Create an unprivileged user and hand it ownership of the app directory, then switch to it.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "telemetry_insight.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

The image runs as `appuser`, never as root, so a process breakout does not start with root. The
comment block at the end documents the run-time hardening the operator applies but the image cannot
bake in: `--read-only` for a read-only root filesystem, `--tmpfs /tmp` for a small writable scratch
area, `--cap-drop ALL` to drop every Linux capability, and `--security-opt no-new-privileges`. That is
defence in depth: independent controls, so a failure in one is caught by the next.

## Step 5: the security tests

The deliverable proof, five tests, one per behaviour. A `TestClient` drives the API the way a real
caller would, and each test builds a fresh app so the in-memory store never leaks between them.

**`tests/test_security.py`**

```python
def test_bola_owner_gets_200_other_caller_gets_404() -> None:
    client = _client()
    created = client.post(
        "/v1/readings",
        json={"device_id": "D1", "value": 20.5},
        headers={"X-User-Id": "userA"},
    )
    assert created.status_code == 201
    reading_id = created.json()["id"]

    owner_view = client.get(f"/v1/readings/{reading_id}", headers={"X-User-Id": "userA"})
    assert owner_view.status_code == 200
    assert owner_view.json()["owner_id"] == "userA"

    # Caller B, who does not own it, gets a 404, not a 403, so the id is not confirmed to exist.
    other_view = client.get(f"/v1/readings/{reading_id}", headers={"X-User-Id": "userB"})
    assert other_view.status_code == 404


def test_mass_assignment_ignores_body_owner_and_status() -> None:
    client = _client()
    created = client.post(
        "/v1/readings",
        json={"device_id": "D1", "value": 20.5, "owner_id": "attacker", "status": "admin"},
        headers={"X-User-Id": "userA"},
    )
    reading_id = created.json()["id"]
    view = client.get(f"/v1/readings/{reading_id}", headers={"X-User-Id": "userA"})
    assert view.json()["owner_id"] == "userA"   # the caller, not "attacker"
    assert "status" not in view.json()          # the server-controlled flag never landed


def test_pii_contact_is_masked_in_logs() -> None:
    logger = logging.getLogger("telemetry_insight")
    capture = _CaptureHandler()
    logger.addHandler(capture)
    try:
        client = _client()
        raw_email = "alice@example.com"
        resp = client.post(
            "/v1/readings",
            json={"device_id": "D1", "value": 20.5, "contact_email": raw_email},
            headers={"X-User-Id": "userA"},
        )
        assert resp.status_code == 201
    finally:
        logger.removeHandler(capture)

    joined = "\n".join(capture.messages)
    assert raw_email not in joined                      # the raw contact never reaches a log
    assert mask_email(raw_email) in joined              # the masked form is present instead
    assert mask_email(raw_email) == "a****@example.com"


def test_secret_scan_reports_zero_findings_over_src() -> None:
    # The real source must contain no hard-coded secret, so the scanner exits 0.
    script = _PROJECT_ROOT / "scripts" / "secret_scan.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_secret_scan_detects_a_planted_secret(tmp_path: Path) -> None:
    # A negative control: the scanner must actually catch a hard-coded secret when there is one.
    planted = tmp_path / "leak.py"
    planted.write_text('password = "hunter2-not-a-real-secret"\n', encoding="utf-8")
    # ... import find_secrets from the script and run it over tmp_path ...
    findings = module.find_secrets(tmp_path)
    assert len(findings) == 1
```

Read the five as the chapter's lens applied one control at a time. The BOLA test posts as caller A,
reads back at 200 as the owner, and gets a 404 as caller B, the fail-secure denial with no
enumeration. The mass-assignment test sends `owner_id: "attacker"` and `status: "admin"` in the body
and proves neither reached the record, the caller header won. The masking test captures the package
logger and proves the raw email is absent while `a****@example.com` is present. The clean-scan test
runs `secret_scan.py` as a subprocess over the real `src/` and asserts exit 0. The planted-secret
test imports `find_secrets` and proves it catches exactly one finding in a temporary file, the
negative control that shows the scanner is not simply always green. The `_CaptureHandler` is needed
because the package logger does not propagate to the root logger, so pytest's `caplog` would not see
its records.

## Step 6: run it

```bash
poetry run telemetry summary
```

```text
readings: 5
devices : 3
rejected: 2
```

The same five valid readings, three devices, and two rejected rows as before. The security layer did
not change what the summary does; it changed who may read a reading, what a body may set, and what can
reach a log. Run the secret scan on its own to see the clean gate:

```bash
poetry run python scripts/secret_scan.py
```

```text
secret scan: no hard-coded secrets found
```

## Step 7: green gate

```bash
poetry run pytest -q          # 30 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
```

The five security tests join the dependability tests and everything carried forward from earlier
days, for 30 in all. ruff is clean and mypy strict is clean, and the secret scan exits 0.

## Done when

- The project version is `0.7.0`, and the FastAPI app reports `version="0.7.0"`.
- `security.py` has a `mask_email` that turns `alice@example.com` into `a****@example.com`, a
  `mask_caller`, and a `log_security_event` that emits one structured line with the trace id, the
  resource, and a masked caller, and no secrets or raw personal data.
- `api.py` enforces object-level authorization on `GET /v1/readings/{reading_id}` (owner 200,
  non-owner and missing id both 404, with an `authz_denied` event on a denial), binds only
  caller-settable fields and sets `owner_id` on the server, masks an optional `contact_email` before
  any log, and logs a `validation_rejected` event on a rejected body. The webhook secret is read from
  `WEBHOOK_SECRET`.
- `scripts/secret_scan.py` scans `src/`, exits 0 when clean, and catches a planted secret; the
  `Dockerfile` runs as a non-root user on a slim pinned base and documents the run-time hardening.
- `tests/test_security.py` proves object-level authorization, mass-assignment protection, contact
  masking in logs, a clean secret scan, and a caught planted secret, five tests in all.
- Readings may be negative and within the range `-50` to `150`.
- `pytest` (30 passed), `ruff`, and `mypy` are all green, the secret scan exits 0, and
  `telemetry summary` still prints `readings: 5`, `devices : 3`, `rejected: 2`.

You have run the chapter's lens on the telemetry domain: for each control a blueprint that sets the
posture in the domain's terms and a realization that makes the code hold it and fail secure. The
behaviour your CLI prints did not change; the service now proves who may see what, keeps data as data,
keeps secrets and sensitive fields out of the clear, and emits the security events that let you watch.
