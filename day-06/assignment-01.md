# Assignment 01 · Make telemetry-insight secure by design and execution

> Offline practice for the Secure topic. In class you hardened `reviews-insight` layer by layer,
> reading each control as a pair: the architect's blueprint that sets the posture, and the engineer's
> realization that makes the code either secure or not. Now run that same pass on your
> `telemetry-insight` service, with the emphasis the telemetry domain calls for: the readings belong
> to devices, and a device owner's contact is sensitive. The pressure is not a clever answer, it is
> making sure only the owner of a reading can read it, that a crafted body cannot claim ownership, and
> that nothing sensitive ever lands in a log.

This is a do-it-yourself assignment. The point is to feel what "secure" buys you once the data is
real: a caller who does not own a reading gets the same 404 as a caller asking for an id that never
existed, a body that tries to set `owner_id` is ignored, a raw contact email never reaches a log
line, and a hard-coded secret cannot slip into the source. The counting logic from earlier days does
not change. What changes is that the service now proves who may see what, keeps data as data, and
emits the structured signals that let you watch for abuse.

Start from your `telemetry-insight` project, green, with the dependability layer already in place
(idempotency, load shedding, the sink, readiness, and the SLI metrics). The security layer sits on
top of all of it, and everything earlier keeps working unchanged.

## The goal

One thing, done honestly: put a security layer in front of the service you already have, following
the shared-responsibility rule from the chapter. Only the owner of a reading may fetch it by id. The
ingest boundary binds only the fields a caller may set, and the server sets the owner itself. A
sensitive contact field is masked before it is ever logged. Secrets stay out of the source, checked
by a scanner that fails the build. The runtime is a hardened non-root container. And every
authorization denial and validation rejection is a structured security event. The `telemetry
summary` command still prints exactly what it did before.

The behaviour of the summary is unchanged. The target output is still:

```text
readings: 5
devices : 3
rejected: 2
```

Run the whole assignment through the chapter's lens. For each control, hold both halves in view:

- **Blueprint (architect).** State the posture in the telemetry domain's terms: a reading is an owned
  object, so authority is checked at the object level; the ingest contract is the mass-assignment
  boundary; a device-owner contact is regulated data and never leaves the service in the clear; the
  container is non-root and least privilege.
- **Realization (engineer).** Make the code hold the posture, and prove it fails secure: a non-owner
  read returns 404 with no enumeration, an owner field in the body is dropped, a raw email is absent
  from every log, the secret scan exits 0 and still catches a planted secret.

## What you have to build

Bump the project version to `0.7.0` first, so the package version tracks the topic. Then build the
security layer on top of the dependability API you already have.

1. **Security helpers (`security.py`).** Standard-library-only masking and a structured security-event
   logger. A `mask_email` that keeps the first character of the local part and the whole domain, a
   `mask_caller` that keeps only the first character of an identity, and a `log_security_event` that
   emits one structured line carrying the trace id, the resource, a masked caller, and a status, with
   no secrets and no raw personal data.
2. **The security layer on the API (`api.py`).** Object-level authorization on a single-reading route,
   mass-assignment protection at the ingest contract, a server-set `owner_id`, sensitive-field masking
   on an optional contact, and structured security events for an authorization denial and a validation
   rejection. The webhook secret comes from the environment, not the source.
3. **Security tests (`tests/test_security.py`).** One test per behaviour: the owner reads their record
   and a non-owner is denied, a body-supplied owner and status are ignored, a raw contact is masked in
   the logs, the secret scan is clean over `src/`, and the scanner catches a planted secret.
4. **A secret scanner (`scripts/secret_scan.py`).** A dependency-light scan over `src/` for the common
   shapes of a hard-coded secret that exits 0 when the tree is clean and non-zero when it finds one.
5. **A hardened container (`Dockerfile`).** A slim, pinned base, a non-root user, and documented
   run-time hardening (read-only root filesystem, dropped capabilities, no new privileges).

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the security helpers

Write `src/telemetry_insight/security.py` on the standard library alone (`re` plus the package's
`log_event`). The teaching point is that a log is a real attack surface: anything sensitive that
lands in a log line can leak, so you mask before you write, never after. Give it three pieces:

- `mask_email(value)` that returns a form safe to log. Keep the first character of the local part and
  the whole domain, and replace the rest of the local part with asterisks, so `alice@example.com`
  becomes `a****@example.com`. A value that does not look like an email is masked whole, so an
  unexpected raw value never leaks.
- `mask_caller(caller)` that keeps only the first character of an identity, so you can record who was
  denied without recording the full identity.
- `log_security_event(event, trace_id, resource, caller, status)` that masks the caller and emits one
  structured line through `log_event`, carrying the event name (for example `authz_denied` or
  `validation_rejected`), the trace id, the affected resource, the masked caller, and a status.

Hint: the mask keeps just enough to be useful in an investigation and no more. Keeping the first
character and the domain lets an operator recognize a pattern without ever seeing a whole address.

### Level 2: object-level authorization and the owner model

Extend the stored record and add the owner-scoped read. Each stored reading now carries a
server-generated `reading_id` and a server-set `owner_id` alongside the `device_id` and `value`.
Read the caller identity from an `X-User-Id` header (in production this is a validated token; here a
plain header stands in so the authorization check is the point). Default a missing identity to a
fixed `anonymous` value that can never match a real owner.

Add `GET /v1/readings/{reading_id}`. Find the record; if the caller does not own it, log an
`authz_denied` security event and raise a 404, the same 404 an outsider sees for an id that does not
exist. A missing id raises the same 404. The two cases are indistinguishable, so ownership is never
revealed and ids cannot be enumerated.

Hint: this is the fix for Broken Object Level Authorization, the number one API risk. "Logged in" is
not "allowed." Returning 404 rather than 403 is the fail-secure choice: a 403 would confirm the id
exists, which is itself a leak.

### Level 3: mass-assignment protection and the server-set owner

Make the ingest contract the mass-assignment boundary. Declare on `ReadingIn` exactly the fields a
caller may set: `device_id`, `value` (the range constraint `-50` to `150`, carried forward so
readings can be negative and out of a small range), the optional idempotency `key`, and an optional
`contact_email`. Pydantic drops any other key in the body, so a request that also carries `owner_id`
or a `status` flag has those extra keys dropped at the bind. In the handler, take the owner from the
caller identity and set it on the record yourself; never read it from the body.

Hint: mass assignment is the bug where a caller sets a field they should not, by adding it to the
JSON. The defence is to bind only the allowed fields and let the server set the rest. Even if the
body carries `owner_id: "attacker"`, it is gone by the time your code runs.

### Level 4: sensitive-field masking

Handle the optional `contact_email` as regulated data. If a caller sent one, log only its masked
form through `log_event`, never the raw address. Store the record with whatever the caller sent, but
keep the sensitive field out of the owner-scoped read response so it is not handed back out through
that route. Also add a validation-error handler that logs a `validation_rejected` security event with
a masked caller and returns a plain 422 that does not echo the offending input back to the caller.

Hint: the rule is mask before the value can reach any log or prompt. Do it at the point where you
build the log line, so there is no window where the raw value could be written.

### Level 5: secret hygiene

Write `scripts/secret_scan.py` on the standard library (`re`, `pathlib`). Scan the Python files under
`src/` for the common shapes of a hard-coded secret: a secret-like name (`password`, `secret`,
`api_key`, `auth_token`, `private_key`, and similar) assigned directly to a string literal, an AWS
access key id shape, and a PEM private-key header. Exempt comments and any line that reads from the
environment, because reading a secret from the environment is exactly the pattern you want. Exit 0
when the tree is clean and non-zero, printing each finding, when it is not.

Keep the webhook secret out of the source: read it from `WEBHOOK_SECRET` in the environment, with a
dev-only fallback so local tests still run. The scanner exempts the env-reading line, so the source
stays clean.

Hint: secrets belong in the environment, never in the source, where they would be committed to
history and shared with everyone who can read the repository. A scan that runs in a pre-commit hook
or CI gate fails the build before a secret lands.

### Level 6: the hardened runtime

Write a `Dockerfile` that runs as a non-root user. Start from a slim, pinned base
(`python:3.12-slim`), export a plain requirements list from Poetry at build time and install with pip
so the runtime image does not carry Poetry, copy the source after the dependency layer, create an
unprivileged user, hand it ownership of the app directory, and switch to it before the `CMD`.
Document the run-time hardening the operator applies but the image cannot bake in: a read-only root
filesystem, a small writable tmpfs, dropped Linux capabilities, and no new privileges.

Hint: a non-root user means a process breakout does not start as root; combined with a read-only root
filesystem and no capabilities, a compromised process has very little it can do. That is defence in
depth: independent controls, so a failure in one is caught by the next.

### Level 7: prove it with security tests

Write `tests/test_security.py` with a `TestClient` and five tests, one per behaviour. Build a fresh
app per test so the in-memory store does not leak between them. Assert that:

- caller A ingests a reading with `X-User-Id: userA`, then A reads it back at 200 with
  `owner_id == "userA"`, and caller B gets a 404 (not a 403), so the id is not confirmed to exist.
- a body that also carries `owner_id: "attacker"` and `status: "admin"` is ingested with the owner
  set from the header instead, and neither the attacker owner nor the status flag is on the record.
- a reading ingested with a `contact_email` masks the raw address in every log line: capture the
  package logger, assert the raw email is absent, and assert the masked form is present and equal to
  `a****@example.com`.
- running `scripts/secret_scan.py` over the real `src/` exits 0.
- the scanner's `find_secrets` catches exactly one finding in a temporary file holding a planted
  hard-coded secret.

Hint: the package logger does not propagate to the root logger, so pytest's `caplog` does not see its
records. Attach a small capturing handler directly to the `telemetry_insight` logger to inspect the
lines. Run the clean scan as a subprocess and the planted-secret check by importing `find_secrets`
against a `tmp_path`.

### Level 8: green gate

Run pytest, ruff, and mypy strict, then run the secret scan. Expect 30 tests to pass: the five new
security tests in `tests/test_security.py`, plus the dependability tests and everything carried
forward from earlier days. ruff clean, mypy strict clean, secret scan exit 0.

```bash
poetry run pytest -q               # 30 passed
poetry run ruff check .            # All checks passed!
poetry run mypy src                # Success: no issues found
poetry run python scripts/secret_scan.py   # secret scan: no hard-coded secrets found
```

## Done when

- [ ] The project version is `0.7.0`, and the FastAPI app reports `version="0.7.0"`.
- [ ] `security.py` has a `mask_email` that turns `alice@example.com` into `a****@example.com`, a
  `mask_caller`, and a `log_security_event` that emits one structured line with the trace id, the
  resource, and a masked caller, and no secrets or raw personal data.
- [ ] `GET /v1/readings/{reading_id}` returns the reading only to its owner and returns 404 to any
  other caller and for a missing id, so ownership is never revealed and ids cannot be enumerated. A
  non-owner read logs an `authz_denied` security event.
- [ ] Ingest binds only caller-settable fields; `owner_id` is taken from the `X-User-Id` header and
  set on the server, and a body-supplied `owner_id` or `status` is dropped.
- [ ] An optional `contact_email` is masked before it reaches any log line and is never returned
  through the owner-scoped read; a validation rejection logs a `validation_rejected` event and returns
  a plain 422.
- [ ] `scripts/secret_scan.py` scans `src/`, exits 0 when the tree is clean, and catches a planted
  secret; the webhook secret is read from `WEBHOOK_SECRET`, not hard-coded.
- [ ] The `Dockerfile` uses a slim pinned base, runs as a non-root user, and documents read-only root
  filesystem, dropped capabilities, and no new privileges.
- [ ] `tests/test_security.py` proves object-level authorization (owner 200, non-owner 404),
  mass-assignment protection, contact masking in logs, a clean secret scan, and a caught planted
  secret, five tests in all.
- [ ] Readings may be negative and within the range `-50` to `150`.
- [ ] `pytest` (30 passed), `ruff check`, and `mypy src` are all green, the secret scan exits 0, and
  `telemetry summary` still prints `readings: 5`, `devices : 3`, `rejected: 2`.

When every box is ticked, you have run the chapter's lens over the telemetry domain: for each control
a blueprint that sets the posture in the domain's terms and a realization that makes the code hold it
and fail secure. The behaviour your CLI prints did not change; the service now proves who may see
what, keeps data as data, keeps secrets and sensitive fields out of the clear, and emits the security
events that let you watch. The worked solution is in `solution-01.md` if you want to compare, but try
first.
