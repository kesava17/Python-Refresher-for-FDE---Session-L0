# Secure Live Lab: Harden reviews-insight Layer by Layer

## What we're building

You already have the dependable `reviews-insight` service: a versioned, validated HTTP surface with an
`observe` middleware, `/health` and `/ready`, `/metrics`, `POST` and `GET /v1/reviews`, `GET /v1/insight`,
a signed webhook, enrichment with graceful degradation, and an idempotency ledger. It holds up under load,
but it makes no promise about who may read what, what a caller is allowed to set, whether a secret has
leaked into the source, or whether the container runs with more power than it needs.

In this lab you make the service **secure**: you add a hardening layer on top of the dependable version and
walk it through the concrete controls the chapter names. Each control is presented the same way:

1. **Define** the rule: state the security property in one line.
2. **Do** it: run a real command that exercises the control.
3. **Prove** it: show the test, the log line, or the exit code that makes the property auditable.

The controls, one per layer of the chapter, are:

- **Identity and access:** object-level authorization, so a caller reads only reviews they own (the BOLA fix).
- **The API surface:** mass-assignment protection, so the body cannot set server-controlled fields.
- **Data protection:** PII masking, so a reviewer's email is only ever logged in masked form.
- **Threat modeling and observability:** structured security events, one per denial, rejection, and submit.
- **Supply chain:** a secret scan that fails the build on a hard-coded secret.
- **Infrastructure:** a hardened container that runs as a non-root user with run-time lockdown documented.

Work in order. Copy, paste, run. After each step there is one line on what happened and why it matters.
Start from your dependable `reviews-insight` project folder, with everything green.

Ground rules, same as before: everything Python runs through `poetry run`; run commands from inside the
project folder.

---

## Step 0: Set up and confirm the gate is green

Install the dependencies, then run the three checks. This is the baseline every control builds on: if the
suite is green, ruff is clean, and mypy is strict-clean before you start, then any red later is something
you did, not something you inherited.

```bash
poetry install
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

You should see:

```text
33 passed
All checks passed!
Success: no issues found
```

**What happened.** The service is at version `0.7.0` and carries **33 passing tests**: everything carried
forward from the dependable topic plus the **7 new tests in `tests/test_security.py`** (object-level
authorization and its security event, mass-assignment protection, PII masking, validation rejection as a
security event, and the two secret-scan tests). ruff and mypy strict both pass. That is the "green before
you start" line the whole lab depends on.

Confirm the batch path still prints the same counts it always has:

```bash
poetry run reviews summary
```

```text
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
rejected: 2
```

The `summarize` method still carries the `@timed("summary")` decorator, so the timing line prints first,
then the environment header and the three counts (`reviews: 5 / products: 3 / rejected: 2`). Nothing about
the batch path changed; the security layer sits on the HTTP surface.

---

## Step 1: Meet the security layer

Before the controls, look at the pieces that were added. Read them, do not retype them; they are already
built and tested.

`src/reviews_insight/security.py` holds the small reusable helpers. `caller_id_from_header` resolves the
verified caller (from an `X-User-Id` header here, from a validated token in production, defaulting to
`"anonymous"` when absent). `mask_email` turns `alice@example.com` into `a***@example.com`, and
`mask_identifier` reduces a caller id to a non-identifying hint like `u***`.

`src/reviews_insight/observability.py` gains `log_security_event`: it writes one structured line tagged
`kind="security"` with a stable `event` name, a `trace_id`, and only values that are already safe to
record (a masked email, a masked caller, a resource id). It deliberately does not accept a raw email or a
token, so a secret or a raw address cannot land in the security stream by mistake.

`src/reviews_insight/api.py` is the app, now at version `0.7.0`. The request contract `ReviewIn` lists only
`product_id`, `rating`, and an optional `reviewer_email`; `StoredReview` adds the server-controlled
`owner_id`, `is_flagged`, and `enriched`. The submit handler reads `X-User-Id`, sets the owner from it, and
never from the body. `GET /v1/reviews/{review_id}` is the new by-id read that enforces ownership. The
webhook signing secret comes from `config.webhook_secret`, which reads `WEBHOOK_SECRET` from the
environment, not from a literal in the file.

**What happened.** The service gained an identity-aware submit and by-id read, a request model that binds
only caller-settable fields, masked logging of personal data, structured security events, a secret read
from configuration, plus a CI secret scanner and a hardened Dockerfile. Each control below drives one of
these.

---

## Control 1: object-level authorization (identity and access)

**Broken object-level authorization, BOLA, is the top API risk. Knowing an id is not permission to read it.**

### Define

`GET /v1/reviews/{review_id}` returns the review only when the caller owns it. The rule: if
`owner_id == caller`, return `200` with the review; otherwise return `404`, never `403`, so a caller cannot
even confirm that the id exists. That fail-secure `404` is what stops object enumeration. Every denial
records a security event.

### Do

Start the server:

```bash
poetry run reviews serve
```

```text
serving reviews-insight on http://127.0.0.1:8000 (press Ctrl+C to stop)
```

In another terminal, submit a review as `user-a`, then read the listing to learn its id (the listing
exposes `review_id` but never the owner):

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -H "X-User-Id: user-a" \
  -d '{"product_id": "P1", "rating": 5}'

curl -s http://127.0.0.1:8000/v1/reviews
```

```json
{"status":"accepted","enriched":false}
{"items":[{"review_id":"<id>","product_id":"P1","rating":5}],"total":1,"limit":20,"offset":0}
```

Take the `review_id` from that listing and read it twice, once as the owner and once as a different caller:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<id> -H "X-User-Id: user-a"

curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<id> -H "X-User-Id: user-b"
```

```text
200
404
```

The owner gets `200` and the review; the other caller gets `404`, the same answer they would get for an id
that does not exist. Ownership is checked on every read, so holding the id buys nothing.

### Prove

`test_bola_owner_can_read_other_cannot` in `tests/test_security.py` pins both branches:

```python
def test_bola_owner_can_read_other_cannot() -> None:
    client = _client()
    _submit(client, "P1", 5, user="user-a")
    review_id = _first_review_id(client)

    owner = client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "user-a"})
    assert owner.status_code == 200
    assert owner.json()["review_id"] == review_id

    other = client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "user-b"})
    assert other.status_code == 404
```

Run just the authorization tests:

```bash
poetry run pytest -q -k "bola"
```

```text
2 passed
```

The partner test, `test_bola_denial_emits_security_event`, checks that a denial writes an `authz_denied`
event carrying the resource id and the masked caller, with the raw caller id absent. Control 4 looks at
that event directly.

---

## Control 2: mass-assignment protection (the API surface)

**A caller may set only the fields it is allowed to set; the server owns the rest.**

### Define

`POST /v1/reviews` binds only `product_id`, `rating`, and the optional `reviewer_email` from the body. The
server-controlled fields, `owner_id`, `is_flagged`, and `enriched`, are set by the handler, never from the
JSON. A body that also sends `owner_id` or `is_flagged` cannot reach the stored record with them.

### Do

With the server running, submit a review whose body tries to smuggle a different owner and clear the flags,
sent by the real caller `real-owner`:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -H "X-User-Id: real-owner" \
  -d '{"product_id": "P1", "rating": 5, "owner_id": "attacker", "is_flagged": true, "enriched": true}'
```

```json
{"status":"accepted","enriched":false}
```

The response says `enriched: false`, not the `true` the body asked for: the enrichment flag is
server-decided (it degraded, because the default enrichment host does not resolve), and the smuggled value
was ignored. The owner was taken from `X-User-Id`, not from `owner_id` in the body. Read the new review's id
from the listing and confirm who can see it:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<id> -H "X-User-Id: real-owner"

curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<id> -H "X-User-Id: attacker"
```

```text
200
404
```

`real-owner` reads it; the smuggled `attacker` owner cannot. The owner in the store came from the verified
caller, so the body field never took effect.

### Prove

`test_mass_assignment_cannot_set_server_fields` submits exactly that crafted body and asserts the same
outcome:

```python
def test_mass_assignment_cannot_set_server_fields() -> None:
    client = _client()
    resp = client.post(
        "/v1/reviews",
        json={"product_id": "P1", "rating": 5,
              "owner_id": "attacker", "is_flagged": True, "enriched": True},
        headers={"X-User-Id": "real-owner"},
    )
    assert resp.status_code == 201
    review_id = _first_review_id(client)
    assert client.get(f"/v1/reviews/{review_id}",
                      headers={"X-User-Id": "real-owner"}).status_code == 200
    assert client.get(f"/v1/reviews/{review_id}",
                      headers={"X-User-Id": "attacker"}).status_code == 404
```

```bash
poetry run pytest -q -k "mass_assignment"
```

```text
1 passed
```

The protection is structural: `ReviewIn` simply does not list the server fields, so Pydantic drops any
extra key in the body before the handler ever runs.

---

## Control 3: PII masking (data protection)

**A reviewer's email is only ever recorded in masked form; the raw address is never logged or stored.**

### Define

`reviewer_email` is optional. When present, the submit path logs it only through `mask_email`, which keeps
the first character and the domain (`a***@example.com`) and hides the rest. The raw address appears in no
log line, and it is not written into the stored review at all.

### Do

The masked form lands in the security log, which prints as JSON on the server's stdout. Submit a review
carrying an email and watch the server terminal:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -H "X-User-Id: user-a" \
  -d '{"product_id": "P1", "rating": 5, "reviewer_email": "alice@example.com"}'
```

On the terminal running `reviews serve` you see a `review_received` security event whose masked email is
present and whose raw address is not:

```json
{"kind":"security","event":"review_received","trace_id":"...","resource_id":"...","caller":"u***","masked_email":"a***@example.com"}
```

The line says `a***@example.com`; the string `alice@example.com` appears nowhere in it. The caller is masked
to `u***` as well.

### Prove

`test_pii_email_is_masked_in_logs_and_raw_never_appears` captures the logs and asserts both halves:

```python
def test_pii_email_is_masked_in_logs_and_raw_never_appears(captured_logs: list[str]) -> None:
    client = _client()
    raw_email = "alice@example.com"
    resp = client.post(
        "/v1/reviews",
        json={"product_id": "P1", "rating": 5, "reviewer_email": raw_email},
        headers={"X-User-Id": "user-a"},
    )
    assert resp.status_code == 201
    masked = mask_email(raw_email)
    assert masked == "a***@example.com"
    events = [line for line in captured_logs if "review_received" in line]
    assert any(masked in line for line in events)
    assert all(raw_email not in line for line in captured_logs)  # raw email never appears
```

```bash
poetry run pytest -q -k "pii"
```

```text
1 passed
```

The last assertion is the strong one: it scans every captured line and requires the raw address to be
absent from all of them, not just the one event.

---

## Control 4: structured security events (threat modeling and observability)

**Every denial, rejection, and accepted submit emits a structured security event a SIEM can alert on.**

### Define

`log_security_event` writes one JSON line tagged `kind="security"` with a stable event name and the request
`trace_id`. Three events flow through it: `authz_denied` on a failed ownership check, `validation_rejected`
when the edge refuses malformed input, and `review_received` on a stored submit. Each carries only masked or
non-sensitive fields, so no secret and no raw personal data enters the security stream.

### Do

Trigger the denial event: read a review you do not own, then watch the server terminal.

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<id-owned-by-user-a> -H "X-User-Id: user-b"
```

```text
404
```

The server logs the denial:

```json
{"kind":"security","event":"authz_denied","trace_id":"...","resource_id":"<id>","caller":"u***","reason":"caller is not the owner"}
```

Now trigger the rejection event with an out-of-range rating (the model requires 1 to 5):

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "P1", "rating": 99}'
```

```json
{"detail":[{"loc":["body","rating"],"msg":"Input should be less than or equal to 5","type":"less_than_equal"}]}
```

The response is `422`, and the server logs a `validation_rejected` event that names the path but never
echoes the rejected body:

```json
{"kind":"security","event":"validation_rejected","trace_id":"...","resource_id":"/v1/reviews","reason":"request failed schema validation"}
```

### Prove

The denial event is pinned by `test_bola_denial_emits_security_event`, which asserts the masked caller is
present and the raw id absent:

```python
    denials = [line for line in captured_logs if "authz_denied" in line]
    assert denials, "expected an authz_denied security event"
    assert review_id in denials[-1]
    assert mask_identifier("user-b") in denials[-1]
    assert "user-b" not in denials[-1]  # the raw caller id is never logged
```

The rejection event is pinned by `test_validation_rejection_emits_security_event`. Run both:

```bash
poetry run pytest -q -k "security_event"
```

```text
2 passed
```

In production these `kind="security"` lines are routed to a SIEM, and a rising `authz_denied` rate on one
resource is an early sign of an enumeration attempt, visible before it becomes an incident.

---

## Control 5: secret hygiene (supply chain)

**No secret is hard-coded in source; a CI scanner fails the build if one appears.**

### Define

Secrets belong in the environment, never in the repository. The webhook signing secret is read from
`WEBHOOK_SECRET` through the config object. `scripts/secret_scan.py` walks `src/` for the shapes secrets
take (cloud access keys, private-key blocks, a secret-looking literal assigned to a secret-named variable)
and exits `0` when the source is clean, non-zero otherwise, so a CI step can block the merge.

### Do

Run the scanner over the real source:

```bash
poetry run python scripts/secret_scan.py
```

```text
secret scan: no findings under .../src
```

```bash
echo $?
```

```text
0
```

Exit code `0`: nothing in `src/` looks like a hard-coded secret. Note the scanner is not fooled by the
config default, because `os.environ.get("WEBHOOK_SECRET", ...)` reads the value at run time; the quote does
not sit right after the `=`, so the assignment pattern does not fire.

### Prove

The scanner is only convincing if it catches a real secret, so one test feeds it a planted one and another
confirms the real tree is clean:

```python
def test_secret_scan_finds_nothing_in_real_source() -> None:
    scanner = _load_secret_scan()
    findings = scanner.scan_source()
    assert findings == []


def test_secret_scan_detects_a_planted_secret() -> None:
    scanner = _load_secret_scan()
    planted = 'aws_secret_access_key = "AbcdEfgh1234567890Xyz"'
    assert scanner.scan_text(planted)
```

```bash
poetry run pytest -q -k "secret_scan"
```

```text
2 passed
```

`scan_source()` returns an empty list on the shipped source; `scan_text(...)` returns a non-empty list of
matched pattern names for the planted line. The same `scan_source()` call is what a CI job runs to gate a
merge.

---

## Control 6: the hardened container (infrastructure)

**The image runs as a non-root user, and the run-time lockdown is documented for the orchestrator.**

### Define

The container drops root: it creates an unprivileged service account (`uid 10001`) and runs as it, so a bug
or an exploit cannot write outside allowed paths or bind a privileged port. The run-time controls that
belong in the deployment manifest, a read-only root filesystem and dropped Linux capabilities, are called
out so one image deploys under one auditable policy.

### Do

Read `Dockerfile`. The non-root user is created and selected:

```dockerfile
RUN useradd --create-home --system --uid 10001 appuser
USER appuser

EXPOSE 8000
```

The run-time hardening is documented as the flags the orchestrator applies, not baked into the image:

```dockerfile
# Run-time hardening is applied by the orchestrator, not baked in here. In a Kubernetes
# securityContext (or the equivalent docker run flags) the deployment should set:
#   - a read-only root filesystem (docker run --read-only),
#   - all Linux capabilities dropped (docker run --cap-drop=ALL),
#   - no privilege escalation (allowPrivilegeEscalation: false).
```

The base is `python:3.11-slim` to keep the attack surface small, and the final command runs the app under
uvicorn as the non-root user:

```dockerfile
CMD ["uvicorn", "reviews_insight.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Prove

The image proves itself by construction: there is no `USER root` after the switch, nothing binds a port
below 1024, and the run-time flags are the auditable policy a reviewer checks against the deployment
manifest. Together with the `--read-only` and `--cap-drop=ALL` flags at run time, a process that is
compromised keeps the least privilege it can be given.

---

## Serve it: the full route list

`reviews serve` starts the versioned API through uvicorn on a real port, so another process can reach every
route, including the by-id read this topic added:

```bash
poetry run reviews serve
```

```text
serving reviews-insight on http://127.0.0.1:8000 (press Ctrl+C to stop)
```

Live routes:

- `GET /health`, liveness.
- `GET /ready`, readiness (`503` when at capacity, `200` otherwise).
- `GET /metrics`, the SLI counters as plain text.
- `POST /v1/reviews`, submit (owner from `X-User-Id`, binds only caller-settable fields, honors
  `Idempotency-Key`, enriches or degrades).
- `GET /v1/reviews`, one paginated page plus the total (never exposes the owner).
- `GET /v1/reviews/{review_id}`, the by-id read, gated by object-level authorization (`404` when the caller
  is not the owner).
- `GET /v1/insight`, the running summary.
- `POST /v1/webhooks/rating`, the signed webhook (secret from `WEBHOOK_SECRET`).
- `/openapi.json` and `/docs`, the generated contract and interactive docs.

Every response still carries an `x-trace-id` header, and every security-relevant action writes one
structured `kind="security"` log line carrying that same trace id, so a denial can be tied back to the exact
request that caused it. Press Ctrl+C to stop the server.

---

## You should see

Run through this recap. If each line matches, the secure lab is done.

- `poetry run pytest -q` reports **33 passed**: everything from the dependable topic plus the **7 tests in
  `tests/test_security.py`**.
- `poetry run ruff check .` and `poetry run mypy src` are both clean, and the project is at version `0.7.0`.
- `poetry run reviews summary` still prints the timing line and the counts, `reviews: 5 / products: 3 /
  rejected: 2`, with no crash.
- **Control 1 (BOLA):** `GET /v1/reviews/{id}` returns `200` to the owner and `404` to any other caller, and
  the denial emits an `authz_denied` security event.
- **Control 2 (mass assignment):** a body carrying `owner_id`, `is_flagged`, or `enriched` is ignored; the
  owner is taken from `X-User-Id`, and the smuggled owner cannot read the review.
- **Control 3 (PII):** a submit with `reviewer_email` logs only `a***@example.com`; the raw address appears
  in no log line.
- **Control 4 (security events):** `authz_denied`, `validation_rejected`, and `review_received` are emitted
  as `kind="security"` JSON lines, each with a trace id and no raw personal data.
- **Control 5 (secrets):** `poetry run python scripts/secret_scan.py` exits `0` on the real source, and the
  tests prove it catches a planted secret.
- **Control 6 (container):** the `Dockerfile` runs as non-root `appuser` (`uid 10001`), and the read-only
  root filesystem and dropped capabilities are documented for run time.

That is the secure layer: the same small service now checks the object, not just the login; binds only the
fields the caller may set; masks personal data before it reaches a log; emits security events a SIEM can
watch; keeps secrets out of source and proves it in CI; and ships in a container that runs with the least
privilege it needs. Security is defense in depth, and this lab is that depth applied, layer by layer, to a
running service, each layer with a rule defined, a command that does it, and a test or a log line that
proves it.
