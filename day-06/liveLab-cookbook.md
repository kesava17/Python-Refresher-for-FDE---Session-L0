# Secure liveLab: run it, then understand it

This is the `reviews-insight` liveLab for the Secure topic. The idea of the day is that security is
not one feature you bolt on at the end; it is a set of layers, each one closing a specific way a real
service gets abused, and each one owned by a clear party. The service already worked and already held
up under load. This topic makes it *safe to expose*: a caller can read only their own data, cannot
smuggle in fields the server is meant to control, and never leaves personal data or a secret sitting
in a log or in source. Run the project first so you see the layers holding, then read the second half
to understand what each change added and why it matters.

The topic frames every security concern through two ideas: **shared responsibility** (some controls
are the app's job, some are the platform's, and the line between them is explicit) and **defense in
depth** (no single check is trusted to be the only thing standing between an attacker and the data).
Keep both in mind; the code you run below is those ideas made concrete.

Code lives at
`shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/secure/liveLab`.
Open a terminal there.

---

## Part 1: Run the project

### Set it up (once)

This is a standard Poetry project. Install its dependencies once:

```bash
poetry install
```

### Run the checks

Prove the whole thing is green before touching it:

```bash
poetry run pytest -q          # 33 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
```

Seven of those tests are the security tests in `tests/test_security.py`, one per hardening layer this
topic adds: object-level authorization (owner can read, another caller cannot), the authorization
denial emits a security event, mass assignment cannot set server fields, a reviewer email is masked in
logs and the raw address never appears, a schema rejection emits a security event, the secret scanner
finds nothing in the real source, and the secret scanner does catch a planted secret. They join the
earlier API, dependability, model, native, service, and summary tests for 33 in total.

### Run the batch summary

The command-line surface still does the batch job from the earlier days:

```bash
poetry run reviews summary
```

Expect (the first line names the environment and app; the counts are what matter):

```text
[dev] reviews-insight
reviews : 5
products: 3
rejected: 2
```

### Run the API

Start the HTTP server (add `--port N` to change the port):

```bash
poetry run reviews serve
```

It listens on `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for the interactive,
auto-generated contract. The routes are:

```text
GET  /health                 liveness: is the process up at all?
GET  /ready                  readiness: is there free capacity right now? (503 when full)
GET  /metrics                the SLIs as plain text (request rate, error rate, duration)
POST /v1/reviews             create; sets the owner from an X-User-Id header (201)
GET  /v1/reviews             paginated list (items + total + limit + offset), owner never shown
GET  /v1/reviews/{id}        read one review, only if the caller owns it (else 404)
GET  /v1/insight             summary
POST /v1/webhooks/rating     signed webhook, 401 on a bad signature
                             (every response also carries an x-trace-id header)
```

The new route this topic adds is `GET /v1/reviews/{id}`. It is where object-level authorization is
enforced: the caller identity arrives in an `X-User-Id` header (a stand-in for a verified token), and
the review is returned only if that caller owns it.

### See object-level authorization for yourself

Create a review as one user, then try to read it back as that user and as a different one:

```bash
# create as user-a
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" -H "X-User-Id: user-a" \
  -d '{"product_id":"P1","rating":5}'

# find the id from the listing
curl -s http://127.0.0.1:8000/v1/reviews
```

Take the `review_id` from that listing and read it back two ways:

```bash
# the owner: 200 with the review
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<review_id> -H "X-User-Id: user-a"

# a different caller: 404, not 403
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<review_id> -H "X-User-Id: user-b"
```

Expect `200` for `user-a` and `404` for `user-b`. The denial is a 404, not a 403, on purpose: a
caller who does not own the review cannot even confirm that the id exists, so the id space cannot be
walked to discover what belongs to other people.

### See mass-assignment protection for yourself

Submit a review that tries to smuggle in server-controlled fields:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" -H "X-User-Id: real-owner" \
  -d '{"product_id":"P1","rating":5,"owner_id":"attacker","is_flagged":true,"enriched":true}'
```

The submit returns 201, but the smuggled `owner_id` and `is_flagged` are ignored. Read the new review
back: `real-owner` gets 200 and `attacker` gets 404, which proves the owner was taken from the verified
caller and not from the body.

```bash
curl -s http://127.0.0.1:8000/v1/reviews    # get the new review_id
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<review_id> -H "X-User-Id: real-owner"   # 200
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/v1/reviews/<review_id> -H "X-User-Id: attacker"     # 404
```

### See PII masking in the security log

Submit a review that carries a reviewer email, and watch the server's stdout:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" -H "X-User-Id: user-a" \
  -d '{"product_id":"P1","rating":5,"reviewer_email":"alice@example.com"}'
```

The server writes one structured security line that looks like this (the email is masked, and the raw
address never appears anywhere):

```json
{"kind": "security", "event": "review_received", "trace_id": "...", "resource_id": "...", "caller": "r***", "masked_email": "a***@example.com"}
```

Note `kind: "security"`, so a log tool can filter these events out of the request stream, and
`masked_email: "a***@example.com"`, so the account is identifiable enough to investigate without the
raw personal data being recorded.

### Run the secret scan

A hard-coded secret in source is one of the easiest ways a service gets compromised. The CI scanner
walks `src/` and fails the build if it finds one:

```bash
poetry run python scripts/secret_scan.py
```

Expect a clean report and exit 0:

```text
secret scan: no findings under .../src
```

The scanner looks for the shapes secrets actually take (cloud access keys, private-key blocks, a
secret-looking value assigned straight to a secret-named variable), never for English words, and it
reports only the location of a hit, never the value. The tests prove both halves: it finds nothing in
the real source, and it does catch a planted `aws_secret_access_key = "..."`.

### Note the hardened container

`Dockerfile` builds an image that runs as a non-root user. It creates an unprivileged account with
`useradd --create-home --system --uid 10001 appuser` and switches to it with `USER appuser` before the
service starts, so a bug or an exploit in the process cannot write outside its allowed paths or bind a
privileged port. The comments spell out the run-time controls that belong to the orchestrator rather
than the image: a read-only root filesystem, all Linux capabilities dropped, and no privilege
escalation. That split is the shared-responsibility idea in one file.

---

## Part 2: What changed, and why it matters

You have now seen the service refuse a read from a caller who does not own the record, ignore fields a
request tried to smuggle in, mask an email before it reaches a log, and prove its source carries no
secret. Here is what was added to make that happen, grouped by the concept it teaches. Before this
topic the API was already dependable: a versioned, validated HTTP surface with a trace id,
pagination, idempotency, graceful degradation, readiness, and SLI metrics. This topic makes it
*secure*, and it does so by adding one layer at a time, each layer owned by a clear party, so no
single check is the only thing protecting the data.

### The centerpiece: `src/reviews_insight/api.py` (the service hardened)

The API is still built by `create_app()`, and it now carries the security layers on top of everything
it already did, without changing that behavior. The version moved to `0.7.0` (matching
`pyproject.toml`). Four layers live here.

**1. Object-level authorization (fixing BOLA).** The new `GET /v1/reviews/{review_id}` route finds the
review, then returns it only if the caller owns it:

```python
for row in store:
    if row.review_id == review_id:
        if row.owner_id != caller_id:
            log_security_event(logger, event="authz_denied", ...)
            raise HTTPException(status_code=404, detail="not found")
        return ReviewOut(review_id=row.review_id, product_id=row.product_id, rating=row.rating)
raise HTTPException(status_code=404, detail="not found")
```

The caller identity comes from `caller_id_from_header(x_user_id)`, never from the URL or the body. A
present-but-forbidden review and an absent one both return the same 404, so the two cases are
indistinguishable to the caller.

Why it matters: broken object-level authorization (BOLA) is the most common serious API flaw. It
happens when an endpoint checks that you are logged in but not that the specific object is yours, so
changing one id in the URL hands you someone else's data. Checking ownership on every read closes that,
and answering 404 rather than 403 means the id space cannot be enumerated to learn what exists. The
test `test_bola_owner_can_read_other_cannot` pins the 200-versus-404 behavior.

**2. Mass-assignment protection (server-set fields).** The request contract `ReviewIn` lists only the
fields a caller may set, and the stored record `StoredReview` holds the fields only the server may set:

```python
class ReviewIn(BaseModel):
    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    reviewer_email: str | None = None

# in submit(), the server assigns the protected fields itself:
store.append(StoredReview(
    review_id=review_id,
    owner_id=caller_id,        # from the verified caller, never the body
    product_id=review.product_id,
    rating=review.rating,
    is_flagged=False,          # server-controlled; a body field of the same name is ignored
    enriched=bool(enriched["enriched"]),
))
```

Pydantic ignores any field in the body that `ReviewIn` does not declare, so `owner_id`, `is_flagged`,
and `enriched` sent in the request never reach the store. The server sets each of them from a trusted
source.

Why it matters: mass assignment is what lets a request set a field it should not, like naming a
different owner, clearing a moderation flag, or marking itself enriched. The fix is to make the write
model list only caller-settable fields and have the server assign everything else. The test
`test_mass_assignment_cannot_set_server_fields` sends the smuggled fields and proves the real owner,
not the attacker, ends up owning the record.

**3. PII masking before logs (`mask_email`).** When a submit carries a reviewer email, only its masked
form is ever recorded:

```python
pii = {"masked_email": mask_email(review.reviewer_email)} if review.reviewer_email else None
log_security_event(logger, event="review_received", trace_id=trace_id,
                   resource_id=review_id, caller=mask_identifier(caller_id), extra=pii)
```

`mask_email` in `security.py` turns `alice@example.com` into `a***@example.com`: the first character
and the domain are kept as a hint, the rest is hidden. `mask_identifier` reduces a caller id to a
similar non-identifying hint. The raw email is never stored and never logged.

Why it matters: logs get shipped, searched, and kept for a long time, so a raw email or phone number
in a log line is a data leak waiting to happen. Masking at the point of logging keeps enough to
investigate an incident without turning the log store into a copy of the personal data. The test
`test_pii_email_is_masked_in_logs_and_raw_never_appears` asserts the masked form is present and the raw
address appears in no line.

**4. Structured security events (`log_security_event`).** Two kinds of security-relevant moment are now
recorded as their own events: an authorization denial (`authz_denied`) and a rejected request
(`validation_rejected`, emitted from the `RequestValidationError` handler). Each one is a JSON line
tagged `kind: "security"` with a stable event name, and it carries only values that are already safe to
record:

```python
def log_security_event(logger, *, event, trace_id, resource_id=None, caller=None,
                       reason=None, extra=None):
    payload = {"kind": "security", "event": event, "trace_id": trace_id}
    ...
```

The function deliberately does not accept an email or a token, only the masked or non-sensitive forms,
so a secret or raw PII cannot be logged through it by accident.

Why it matters: a security tool (a SIEM) can only alert on what it can find and parse. A denial buried
in prose is invisible; a tagged `authz_denied` event with a resource id and a masked caller is
something an alert can count and a responder can trace. The validation handler also records the
rejection without echoing the raw input back, because that input could itself contain personal data.
The tests `test_bola_denial_emits_security_event` and `test_validation_rejection_emits_security_event`
pin both events.

### Secret hygiene: `src/reviews_insight/config.py` and `scripts/secret_scan.py`

The webhook signing secret is read through the config object, which reads it from the environment:

```python
webhook_secret=os.environ.get("WEBHOOK_SECRET", "shared-webhook-secret"),
```

In `api.py`, `create_app()` takes the secret from `config.webhook_secret`, not from a literal in the
handler. The inline fallback is a non-secret development placeholder that matches the test fixture, so
nothing sensitive lives in source. `scripts/secret_scan.py` is the CI guard that keeps it that way: it
scans `src/` for real secret shapes, prints only the location of any hit, and exits non-zero so a CI
step can block the merge. Its assignment pattern requires a quoted literal sitting right after the
`=`, so it fires on a hard-coded credential but not on a value read through `os.environ.get(...)`.

Why it matters: secrets belong in the environment or a secret manager, never committed to source,
because a committed secret lives in the history forever and leaks the moment the repo does. Reading
secrets through config keeps them out of the code, and a scanner in CI is the automated check that a
new one does not slip in. The tests prove the scanner both passes the clean source and catches a
planted secret, so it is a real guard and not a rubber stamp.

### The hardened container: `Dockerfile`

The image runs as an unprivileged user. It installs the app, then creates and switches to
`appuser` (uid 10001) before the `CMD` starts the server, so the process never runs as root. The
comments document the run-time controls (read-only root filesystem, `--cap-drop=ALL`, no privilege
escalation) that the orchestrator applies rather than the image.

Why it matters: this is the shared-responsibility line drawn in one file. The image is responsible for
not running as root and for a small base with fewer packages to exploit; the deployment platform is
responsible for locking the running container down further. Keeping the run-time controls in the
manifest lets one image be deployed under one consistent, auditable policy, and running as non-root
means a bug in the process is contained instead of owning the box.

### The proof, pinned: `tests/test_security.py`

Seven tests, one per layer, so a later change cannot quietly break a promise: the BOLA read behavior
and its security event, mass assignment, PII masking, the validation-rejection event, and the secret
scanner in both directions (clean source, planted secret). These seven join the API, dependability,
model, native, service, and summary tests for 33 in total.

Why it matters: every security layer the service added is defended by a test. A control that is not
tested is a control that quietly rots, and a security control that rots is worse than none because it
gives false confidence. The tests turn "we added authorization" into "authorization holds, and we can
prove it on every commit."

### The wiring: `pyproject.toml`

The project moved to version `0.7.0`, and its description now spells out the hardening: object-level
authorization, mass-assignment protection, PII masking, security logging, secret scan, and a hardened
container. No dependency was added for the security layer; the checks use FastAPI, Pydantic, and the
standard library the service already carried. The batch `summary` path did not change; the earlier
logic is the stable base the secure API sits on.

---

## What to take away

Security is a set of layers, not a single feature, and it is made concrete by drawing two lines
clearly: who owns each control (shared responsibility), and how many independent controls stand
between an attacker and the data (defense in depth). In this liveLab you can point to each layer.
Authorization: ownership checked on every read, answered as 404 so ids cannot be enumerated, defended
by a test and recorded as a security event. Mass assignment: a write model that lists only
caller-settable fields, with the server assigning owner and flags itself. Privacy: an email masked
before it ever reaches a log. Observability for security: `authz_denied` and `validation_rejected`
events a SIEM can alert on, carrying no secret and no raw PII. Secret hygiene: the signing secret read
from the environment and a CI scanner that fails the build on a hard-coded one. Platform hardening: a
non-root container, with the run-time controls left to the orchestrator. Run the project, break one
layer (drop the ownership check, declare `owner_id` on `ReviewIn`, log the raw email, plant a secret in
source), and watch a test turn red. That is each layer doing its job, and it is exactly what makes a
service safe to expose.
