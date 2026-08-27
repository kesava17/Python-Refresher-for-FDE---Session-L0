# Assignment 02 · Harden transactions-insight: authorize the object, bind the fields, mask the data, prove the secrets are out

> Offline practice for the Secure chapter. You made `transactions-insight` dependable in the last
> assignment, giving it an exactly-once write and an all-or-nothing append. Now add the security layer
> money code cannot ship without: let only the owner read a transaction, refuse a crafted body, keep a
> full account number out of every log, and prove no secret is baked into the source or the image. This
> is the financial-transactions track of the chapter's build, run through the same shared-responsibility
> loop: the architect sets the posture, the engineer proves it holds.

This is a do-it-yourself assignment. The Secure chapter is about one job with two owners: the architect
owns what secure means here and how the system is arranged to allow it, and the engineer owns the code
that is secure or is not. Your dependable transactions service already validates every request at the
edge, records a money write exactly once, and never loses an accepted write. But a payment record is the
most sensitive data in this course, so an open edge on it now owes four hard guarantees: one caller must
never read another caller's transaction, a crafted body must never set a server-only field, a full
account number must never reach a log, and no secret may live in the source tree or the container image.
You will build the small, testable pieces that deliver those guarantees, each one an instance of a
principle from the chapter: least privilege, fail secure, complete mediation, and secure by default.

Start from your dependable `transactions-insight` project, green, with its `TransactionIn` contract, the
`/v1/score` scoring route, the exactly-once `TransactionStore`, the paginated `POST`/`GET
/v1/transactions` pair, the signed webhook, and the `observe` middleware carrying the trace id all in
place.

## The goal

Run each security concern for this domain through the chapter's shared-responsibility loop: name the
threat, place the control, and prove it with a test that turns red if the control is removed. Concretely:

1. Add **object-level authorization** on `GET /v1/transactions/{transaction_id}`. The owner is the
   caller, read from the `X-User-Id` header and set by the server at write time. A non-owner (and a
   made-up id) gets the same `404`, never the data and never a `403`, so an id cannot be enumerated.
   This is the fix for Broken Object Level Authorization (BOLA), the number one API risk.
2. Add **mass-assignment protection**. The `TransactionIn` contract lists only the fields a caller may
   set and ignores every extra field, so a body that sends `owner` or `status` cannot bind them. The
   server sets the owner and the status itself.
3. Add **sensitive-field masking**. A `mask_account` helper shows only the last four characters of an
   account id (for example `****6789`) so a full account number never reaches a log or a log tool.
4. Add **structured security events**. A `log_security_event` function emits one JSON line for an
   authorization denial or a validation rejection, carrying the trace id and the masked account and no
   token, signature, password, or full account number.
5. Add a **secret scan**. A `scripts/secret_scan.py` that scans the `src/` tree for a hard-coded secret
   and exits `0` when it finds none, so it can gate a commit or a pipeline. It must catch a planted
   secret and pass the real source.
6. Add a **hardened container**. A multi-stage `Dockerfile` that runs the app as a non-root user and
   documents the read-only root and dropped-capability run flags, so a flaw in the app cannot easily
   become control of the host.

By the end you have a secure service: a read that authorizes the specific object, a write that binds only
the fields the caller may set, logs that carry masked accounts and structured security events, a scan
that keeps secrets out of source, and an image that runs unprivileged. The deliverable proof is small and
sharp: caller B asks for caller A's transaction and is told it does not exist; a crafted body that names
another owner is ignored; a denied read logs `****6789`, never the full number; the secret scan finds a
planted key and passes the real source.

## The starting point

You already have the dependable transactions service: the frozen `Transaction` model (money in paise),
the `LedgerService`, the exactly-once `TransactionStore` with its `atomic_append`, the `Capacity`,
`Metrics`, and structured `log_event` from `dependability.py`, and the Day 5 edge in `api.py` (the
`TransactionIn` contract, `/v1/score` leaning on the native CRC32, the paginated transactions pair, the
signed webhook, and the `observe` middleware). Reuse all of it. This assignment adds a security layer
beside the edge; it does not change the dependable layer or the scoring formula.

Keep your `transactions-insight` sample CSV (`account_id,ts,amount,currency`) with its five good INR rows
across three accounts plus the two bad rows. The batch summary target stays exactly the same:
`transactions: 5`, `accounts    : 3`, `rejected    : 2`. Money is in rupees on the wire and stored as
paise, as before. The `POST /v1/score` behavior is unchanged: the score is
`crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.

## What you have to build

1. **A security module.** A `security.py` (standard library only, so a reader can follow each piece end
   to end) holding:
   - `mask_account(account_id)`: return the account id with only the last four characters shown, for
     example `****6789`. A very short id (four characters or fewer) is masked completely, so a full
     number is never revealed by accident.
   - `log_security_event(logger, event, trace_id, resource, account)`: emit one JSON line for a security
     event, carrying the event name, the trace id, the resource, and the masked account, and nothing
     sensitive. It logs at `WARNING` so a security event stands out from the routine `INFO` request
     lines, and it leaves the amount out on purpose, so an account and a value are never logged together
     in the clear.
2. **The wiring into `api.py`.** Set the owner from the `X-User-Id` header on the write path, and add
   `GET /v1/transactions/{transaction_id}` with an object-level authorization check that returns `404`
   for a non-owner. Tighten `TransactionIn` so extra fields are ignored, and set `owner` and `status`
   from the server, never the body. Log a security event on an authorization denial and on a validation
   rejection. Bump the app version to `0.7.0`, matching `pyproject.toml`. `/v1/score` does not change.
3. **The secret scan and the hardened image.** A `scripts/secret_scan.py` over `src/`, and a multi-stage
   `Dockerfile` that runs as a non-root user.
4. **The security tests (the deliverable).** A `tests/test_security.py` of five tests, listed in the
   staged guidance below. Your dependable tests (`test_dependability.py`, `test_api.py`, `test_native.py`)
   and the carried maintainable-layer tests all keep passing unchanged.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: mask the sensitive identifier

Create `src/transactions_insight/security.py` and write `mask_account` first. Show only the last four
characters behind four stars (`"****" + account_id[-4:]`), and mask a four-character-or-shorter id
completely (return `"****"`), so a short id can never reveal most of itself.

Hint: masking is the "data protection" habit made small. A log line is read by many people and is often
shipped to a third-party log tool, so a full account number must never appear in it. The last four
characters are enough for a human to correlate a support ticket; the rest is hidden.

### Level 2: one structured security event

Add `log_security_event(logger, event, trace_id, resource, account="")`. Build a payload of `event`,
`trace_id`, `resource`, and the masked account (`mask_account(account) if account else ""`), and log it
as one JSON line at `WARNING`. Never put a token, a signature, a password, a full account id, or the
amount in it.

Hint: a security event (an authorization denial, a validation rejection) is worth its own line so a log
tool can alert on it. `WARNING` is deliberate: it lifts a security event above the routine `INFO` request
lines the `observe` middleware already emits, so a filter finds it at once.

### Level 3: object-level authorization (the BOLA fix)

In `api.py`, set the owner on the write path from the `X-User-Id` header (falling back to `"anonymous"`
when no identity is sent, so the dependable tests that predate this auth layer still work), and store it
as a server-set field on the record. Then add `GET /v1/transactions/{transaction_id}`: fetch the record
through `store.get`, and if it is missing or `record.get("owner") != caller`, log a security event and
raise a `404`.

Hint: a valid id is not enough; the caller must be the owner too. Answer a non-owner and a made-up id with
the same `404`, never a `403`. A `403` here would leak that the id is real, which lets an attacker
enumerate ids that belong to other people. This is fail secure and complete mediation in one route:
authority is checked on every access, and on any doubt the answer is deny.

### Level 4: mass-assignment protection

Tighten `TransactionIn` so it lists only the fields a caller may set (`account_id`, `amount`, `currency`,
and the optional `idempotency_key`) and sets `model_config = ConfigDict(extra="ignore")`, so an unknown
field is dropped, not trusted. Build the stored record in the handler from the validated caller fields
plus the server-set `owner` and `status`, so a body value for `owner` or `status` can never bind. Keep
`status` a server-controlled field set to `"received"`.

Hint: mass assignment is a data-integrity threat: a crafted body tries to set a field the server alone
should decide. Binding only the allowed fields, and building the server fields in code, closes it. Secure
by default: the shape a caller gets without doing anything special is the safe one.

### Level 5: the secret scan and the hardened container

Add `scripts/secret_scan.py` (standard library only: `re`, `pathlib`, `sys`) that scans the `src/` tree
for the shapes a leaked secret takes (a PEM private key block, an AWS access key id, a known provider
token prefix, and a secret-named variable bound directly to a string literal) and returns a process exit
code: `0` when clean, `1` on any finding. A value sourced from `os.environ` or `os.getenv` starts with a
name, not a quote, so the safe pattern does not match. Keep the webhook secret read from the environment
(`os.environ.get("WEBHOOK_SECRET", ...)`), never bound to a literal, so the scan stays clean.

Then write a multi-stage `Dockerfile`: a build stage that installs into a virtual environment, and a slim
runtime stage that creates an unprivileged `app` user and group, copies only the built environment and
the source, and drops to that user with `USER app`. Document the run-time hardening in a comment: the
read-only root filesystem, a `tmpfs` scratch area, `--cap-drop ALL`, and `--security-opt
no-new-privileges`.

Hint: this is the supply-chain and runtime layer. A secret scan in the pipeline keeps a leaked key from
ever merging, and a non-root, read-only, capability-dropped container means a compromised process has
almost no room to act. Both are cheap to add and hard to add back later.

### Level 6: the security tests (the deliverable)

In `tests/test_security.py`, build a fresh app per test with `TestClient(create_app())` and use a
distinctive account id (for example `9876543210`, so the masking test can look for its masked form
`****3210`). Write five tests, grouped by the weakness each one defends against:

- **Object-level authorization (two tests).**
  - `test_owner_can_read_but_another_caller_gets_404`: caller A creates a transaction with an `X-User-Id`
    header, reads it back as `userA` (`200`), then caller B reads the same id and gets `404`, even though
    the id is valid.
  - `test_unknown_id_also_returns_404`: a made-up id fails the same way, so the two cases are
    indistinguishable to a caller.
- **Mass-assignment protection (one test).** `test_body_supplied_owner_and_status_are_ignored`: a body
  that sends `owner="attacker"` and `status="approved"` is created as `userLegit`; assert the stored
  status is the server value `"received"`, the named attacker cannot read the record (`404`), and the
  real caller can (`200`).
- **Sensitive-data masking (one test).** `test_full_account_never_appears_in_logs_but_masked_form_does`:
  capture the log at `WARNING` for the `transactions_insight` logger, trigger a denied read, then assert
  the full account id is absent from the log text and the masked form `****3210` is present.
- **Secret hygiene (one test).** `test_secret_scan_reports_zero_findings_over_src`: run
  `scripts/secret_scan.py` as a subprocess over the real source; assert it exits `0` and its stdout
  contains `0 findings`.

Hint: each test names the weakness it defends against, so a removed control turns the suite red. The
authorization test is the deliverable's heart: caller B is told the transaction does not exist, so an id
cannot be probed. The masking test proves the other habit an audit checks: shipping the log elsewhere
leaks nothing, because the full account number was never written in the clear.

### Level 7: green gate and commit

Run ruff and mypy strict, make the five new security tests and the carried dependable, interoperable, and
maintainable tests all pass, run the secret scan and confirm it exits `0`, confirm the batch summary
output is unchanged, then commit the security layer on top of your dependable project.

## Done when

- [ ] `GET /v1/transactions/{transaction_id}` returns the transaction only to its owner; a non-owner and
  a made-up id both get `404`, never a `403` and never the data, so ids cannot be enumerated.
- [ ] The owner is set by the server from the `X-User-Id` header at write time, never from the body.
- [ ] `TransactionIn` ignores extra fields (`extra="ignore"`), and `owner` and `status` are server-set,
  so a body value for `owner` or `status` cannot bind. `status` is `"received"`.
- [ ] `mask_account(account_id)` shows only the last four characters (for example `****6789`) and masks a
  four-character-or-shorter id completely.
- [ ] `log_security_event(...)` emits one `WARNING` JSON line per event with `event`, `trace_id`,
  `resource`, and the masked `account`, and no token, signature, password, full account id, or amount.
- [ ] `scripts/secret_scan.py` scans `src/`, exits `0` on the clean tree, and would exit `1` on a planted
  secret; the webhook secret is read from the environment, never bound to a literal.
- [ ] The `Dockerfile` builds in one stage and runs the app in a slim stage as a non-root `app` user,
  with the read-only root and `--cap-drop ALL` run flags documented.
- [ ] `POST /v1/score` is unchanged: the score is
  `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`.
- [ ] `tests/test_security.py` holds five tests: two object-level authorization (non-owner and unknown
  id), mass assignment, masking, and the secret scan.
- [ ] `transactions summary` still prints `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- [ ] `pytest` reports 34 passed (five in `test_security.py`), and `ruff check` and `mypy src` are both
  clean, and the secret scan exits `0`, and the layer is committed.

When every box is ticked, you have built the security layer: the same dependable service, now carrying
the four guarantees a money edge cannot ship without. Ask for another caller's transaction and it does
not exist; send a crafted body and the server-only fields are ignored; deny a read and the log shows a
masked account, never the full number; run the scan and the source is clean. That is secure by design and
by execution, the posture the architect set and the code the engineer proved. The worked solution is in
`solution-02.md` if you want to compare, but try first.
