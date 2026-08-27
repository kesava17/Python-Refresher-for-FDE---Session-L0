# Secure liveLab: file-level changes

What changed in the `reviews-insight` liveLab going from the Dependable topic to the
Secure topic, file by file, with the reason for each change. The Dependable topic kept the
service up under real conditions (timeouts, graceful degradation, idempotency, readiness,
structured logging, SLI metrics). The Secure topic hardens that same service without
changing any of its behavior: a caller can read only the reviews they own, the caller can
set only the fields they are allowed to set, a reviewer's email never lands in a log line,
an authorization denial or a rejected request is recorded as a security event, and the
webhook signing secret comes from configuration instead of a literal in the code.

Project path: `shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/secure/liveLab`

## At a glance

| File | Status | What changed | Why |
| --- | --- | --- | --- |
| `src/reviews_insight/security.py` | New | `caller_id_from_header` reads a pre-verified `X-User-Id`, plus `mask_email` and `mask_identifier` for safe logging. | The small reusable pieces the API needs to enforce security: who the caller is, and how to name a person or an id in a log without exposing it. |
| `scripts/secret_scan.py` | New | A CI scanner that walks `src/` for cloud keys, private-key blocks, and hard-coded secret assignments, and exits non-zero on a find. | Secret hygiene: a build step that blocks a merge when a credential is committed to source, reporting the location but never the value. |
| `Dockerfile` | New | A hardened image: slim base, a non-root `appuser` at uid 10001, and comments naming the run-time controls the orchestrator applies. | Runtime hardening: a container that runs as a non-root user with a small attack surface contains a bug or an exploit. |
| `tests/test_security.py` | New | Seven tests: object-level authorization, the denial security event, mass-assignment protection, PII masking, validation-rejection event, and the secret scanner on clean and planted input. | Each security behavior the topic adds is locked in by a test that a change cannot silently break. |
| `src/reviews_insight/api.py` | Modified | Version `0.7.0`; a `StoredReview` with server-set `owner_id`/`is_flagged`/`enriched`; new `GET /v1/reviews/{review_id}` with object-level authorization; submit takes the owner from the caller and ignores smuggled fields; a validation-error handler; the webhook uses a config-sourced secret. | The API is where object-level authorization, mass-assignment protection, PII masking, and security logging all land. It is the centerpiece of the topic. |
| `src/reviews_insight/observability.py` | Modified | Added `log_security_event`, which writes one `kind="security"` JSON line tagged with a stable event name. | Security events need a findable, alertable shape in the log stream, carrying only already-safe values (a masked email, a masked id, a resource id). |
| `src/reviews_insight/config.py` | Modified | Added a `webhook_secret` field, read from `WEBHOOK_SECRET` with a non-secret development fallback. | Secret hygiene: the webhook signing secret is read through the config object from the environment, so it is not a literal in the app code. |
| `pyproject.toml` | Modified | Version `0.6.0` to `0.7.0`; new description naming the secure goals. | Keep the package version and its description in step with the topic. |
| `.env.example` | Modified | Added `WEBHOOK_SECRET` with a note that a real value belongs in each environment. | Document the new secret input so an operator knows to set it, and knows the fallback is a placeholder only. |

## New files, in detail

### `src/reviews_insight/security.py` (caller identity and PII masking)

Three plain-standard-library helpers, no cryptography, because the teaching point is the
shape of the checks:

1. **`caller_id_from_header(x_user_id)`.** Resolves the verified caller identity. In
   production this identity comes from a validated OAuth or JWT bearer token that an auth
   layer checks before the request reaches the handler; that verification is out of scope
   for the lesson, so the helper reads a pre-verified id from the `X-User-Id` header and the
   topic focuses on the authorization check itself. A missing identity becomes `"anonymous"`
   so the carried-forward tests keep working (a real service would answer 401 instead).
   Rationale: object-level authorization needs a trustworthy answer to "who is asking", kept
   in one place.
2. **`mask_email(email)`.** Turns `alice@example.com` into `a***@example.com`: it keeps the
   first character of the local part as a hint, hides the rest, and preserves the domain for
   routing questions; a value that is not an email is fully masked. Rationale: PII masking,
   so a log line can say which account was involved without recording the raw address.
3. **`mask_identifier(value)`.** Reduces a caller id to a non-identifying hint (`user-b`
   becomes `u***`) for a security log line. Rationale: the same masking idea applied to the
   caller id, so an authorization denial can be logged without the raw identity in it.

### `scripts/secret_scan.py` (secret hygiene in CI)

A small scanner that walks the source tree for the shapes secrets usually take and fails the
build when it finds one. Three patterns fire on real secret shapes, not English words: an
AWS access key id (`AKIA` followed by 16 chars), a PEM private-key block, and a secret-named
variable (`password`, `secret`, `api_key`, `token`, and similar) assigned directly to a
quoted literal of some length, which is the classic hard-coded-credential mistake. The
assignment pattern does not fire on a value read through `os.environ.get(...)`, because there
the quote does not sit right after the `=`. `scan_source` returns one `Finding` per matching
line (path, line, pattern, never the value); `main` prints each location and the rule it
matched, then exits `1` so a CI step can block the merge, or prints a clean line and exits
`0`. Rationale: secrets belong in the environment or a secret manager, never committed, and a
CI gate is how that rule gets enforced. The report itself is safe because it records where a
match is, not what it is.

### `Dockerfile` (runtime hardening)

A hardened container image for the service. It starts from `python:3.11-slim` so the attack
surface stays small (fewer packages means fewer known vulnerabilities), sets predictable
Python container behavior, installs the app with `--no-cache-dir`, then creates an
unprivileged system user (`appuser`, uid 10001) and switches to it with `USER appuser`. A
process that is not root cannot write outside its allowed paths or bind a privileged port, so
a bug or an exploit is contained; nothing in the image binds a port below 1024, on purpose. A
block of comments names the run-time controls that belong in the deployment manifest rather
than in the image: a read-only root filesystem, all Linux capabilities dropped, and no
privilege escalation, so one image can be deployed under one consistent, auditable policy.
Rationale: runtime hardening reduces what an attacker can do if they reach the process, and
keeping the run-time policy in the orchestrator keeps the image reusable.

### `tests/test_security.py` (seven tests)

Uses the FastAPI `TestClient` for the HTTP surface, attaches a throwaway logging handler to
capture the structured security events (the service logger does not propagate, so `caplog`
cannot see it), and loads the CI scanner from its script path. The tests: caller A can read
its own review (200) while caller B gets 404, not 403 (object-level authorization, and a 404
so B cannot even confirm the id exists); a denial emits an `authz_denied` event carrying the
resource id and the masked caller with no raw identity; a body that smuggles `owner_id`,
`is_flagged`, and `enriched` cannot set them, so the real owner reads the record and the
smuggled owner cannot (mass assignment); a submit with a `reviewer_email` logs only the
masked form and the raw address never appears in any line (PII masking); a bad rating is
refused with 422 and recorded as `validation_rejected`; the scanner reports zero findings on
the real source; and the scanner catches a planted hard-coded secret. Rationale: each new
security behavior gets a test that locks the contract in place.

## Modified files, in detail

### `src/reviews_insight/api.py`

The topic's changes concentrate here, and none of them alter the dependable behavior carried
forward.

1. **`StoredReview` and server-controlled fields.** The store moved from a loose
   `list[dict[str, str]]` to a `list[StoredReview]`. `StoredReview` carries `review_id`,
   `owner_id`, `product_id`, `rating`, `is_flagged`, and `enriched`, and the last three are
   set by the server, never by the request body. That separation is what makes both the
   authorization check and the mass-assignment protection real: a caller cannot name a
   different owner or clear a flag by sending extra JSON. Rationale: the security-relevant
   fields live in a shape the caller does not control.
2. **Mass-assignment protection on submit.** `ReviewIn` now documents that it lists only the
   fields a caller may set (`product_id`, `rating`, and an optional `reviewer_email`); Pydantic
   ignores any other field in the body, so `owner_id`, `is_flagged`, or `enriched` in the JSON
   never reach the stored record. The submit handler reads the caller id from `X-User-Id`,
   assigns `owner_id` from it, mints a `review_id`, and stores the review with server-set
   flags. Rationale: the server controls identity and state, not the client.
3. **Object-level authorization: `GET /v1/reviews/{review_id}`.** A new by-id read finds the
   review and returns it only if the caller owns it. A non-owner (and a missing id) both get
   404, not 403, so present-but-forbidden and absent are indistinguishable and a caller
   cannot enumerate ids. A non-owner read records an `authz_denied` security event with the
   resource id and the masked caller. Rationale: this fixes BOLA (broken object-level
   authorization), the most common serious API flaw, and fails secure by hiding existence.
4. **PII masking on submit.** `ReviewIn` gained an optional `reviewer_email` that is used only
   in masked form: it is never stored and never sent to the enrichment call. On submit, a
   `review_received` security event carries the masked email (via `mask_email`) and the masked
   caller (via `mask_identifier`). Rationale: personal data stays out of the logs and out of
   the downstream dependency.
5. **Security event on validation failure.** A `RequestValidationError` handler records a
   `validation_rejected` security event (with the request path and a reason, but not the raw
   input, which could contain personal data) and returns a trimmed 422 body. The `observe`
   middleware now stashes the trace id on `request.state`, so this handler and the read
   handlers can tag their events with the same id. Rationale: the edge refusing malformed or
   unexpected input is a security-relevant event a tool should be able to alert on.
6. **Config-sourced webhook secret.** The hard-coded `_WEBHOOK_SECRET` literal is gone. The
   webhook signature is now verified with `config.webhook_secret` (read from the environment),
   encoded once at app construction. The webhook still stores its review, now as a
   `StoredReview` owned by `system:webhook`. Rationale: secret hygiene, the signing secret
   lives in configuration, not in the source.
7. **New imports and version.** Added `RequestValidationError`, `JSONResponse`,
   `log_security_event`, and the three `security` helpers; the app version moved to `0.7.0`.

Carried forward unchanged from the Dependable topic: the `observe` middleware (capacity,
timing, SLIs, structured log), `GET /health` and `GET /ready`, `GET /metrics`, submit
idempotency on `Idempotency-Key`, enrichment with graceful degradation, `GET /v1/reviews`
pagination, and `GET /v1/insight`.

### `src/reviews_insight/observability.py`

Added `log_security_event`, which writes one structured JSON line tagged `kind="security"`
with a stable `event` name and a `trace_id`, plus optional `resource_id`, `caller`, `reason`,
and an `extra` map. It accepts only values that are already safe to record (a masked email, a
masked caller id, a resource id): it does not take an email or a token, so a raw secret or
raw personal data cannot pass through it. Rationale: security events belong in the log stream
like request lines, but a reader needs to find them and a SIEM needs to alert on them, so
each one is tagged and shaped for that.

### `src/reviews_insight/config.py`

Added a `webhook_secret` field to `Config`, read from the `WEBHOOK_SECRET` environment
variable with an inline non-secret development fallback (`shared-webhook-secret`) that matches
the test fixture. Reading the secret here, through the config object, keeps secrets out of the
app code. Rationale: secret hygiene, the app code asks config for the secret instead of
holding a literal, and the fallback is a documented placeholder, not a real credential.

### `pyproject.toml`

Version `0.6.0` to `0.7.0`, and the description now names the secure goals (object-level
authorization, mass-assignment protection, PII masking, security logging, secret scan,
hardened container). Rationale: keep the package metadata in step with the topic. No new
third-party dependency was needed.

### `.env.example`

Added `WEBHOOK_SECRET` with a note that a real value belongs in each environment and that the
app falls back to a non-secret development placeholder only when it is unset. Rationale:
document the new secret input so an operator knows to set it.

### A note on `__init__.py`

`src/reviews_insight/__init__.py` was not changed. As in the Dependable topic, only
`pyproject.toml` carries the version bump; the package `__version__` string is not touched
here.

## How it is verified

- `poetry run pytest -q` reports **33 passed** (up from 26), the seven new ones in
  `tests/test_security.py`.
- `poetry run ruff check .` is clean.
- `poetry run mypy src` is clean under strict typing.
- `poetry run python scripts/secret_scan.py` exits `0` (no findings under `src/`).
- `poetry run reviews summary` prints `reviews: 5 / products: 3 / rejected: 2`.
