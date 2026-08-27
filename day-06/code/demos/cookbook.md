# Secure demos: a run cookbook

Twelve tiny, self-contained demos, one idea each, for the Secure topic (building software that
resists attack). They follow the same flow as the lesson:

- **Control access:** check that the caller owns the object before you return it.
- **Distrust every input:** parameterize queries, allowlist the fields you bind, refuse pickle, and
  check the resolved host before you fetch it.
- **Guard secrets and the supply chain:** scan the diff for hard-coded secrets and pinned versions
  for known-vulnerable dependencies.
- **Use real cryptography:** salted password hashing and authenticated field encryption.
- **Verify integrity, then watch runtime:** an HMAC-signed webhook, a masked security log, and a
  contained subprocess.

Run them in the order below to follow that flow. A few values differ on your machine (a scrypt hash
with a random salt, a Fernet ciphertext); those are flagged where they appear. The pattern each demo
shows is the point.

## Setup (once)

This folder is its own small Poetry project. Set it up once, then run any demo through Poetry:

```bash
poetry install
```

Nine demos are plain scripts you run with `poetry run python <name>.py`. Three are pytest files
(`demo_bola.py`, `demo_pickle_trap.py`, and `demo_hmac_webhook.py`); run those with `poetry run
pytest <name>.py -v`. The demos use only the standard library plus `cryptography` (the
field-encryption demo) and `pytest` (the three test files), so run everything through Poetry, not a
bare `python`. (`fastapi` and `httpx` are declared to match the course baseline but are not imported
by these scripts, so no demo prints a startup or dependency warning.)

## Run everything at once

```bash
for f in demo_sql_injection demo_mass_assignment demo_ssrf demo_secret_scan demo_dep_scan \
         demo_password_hash demo_field_encryption demo_security_logging demo_sandbox; do
  echo "==== $f ===="; poetry run python "$f.py"; echo
done
poetry run pytest demo_bola.py demo_pickle_trap.py demo_hmac_webhook.py -v
```

On Windows PowerShell:

```powershell
'demo_sql_injection','demo_mass_assignment','demo_ssrf','demo_secret_scan','demo_dep_scan','demo_password_hash','demo_field_encryption','demo_security_logging','demo_sandbox' | ForEach-Object { Write-Host "==== $_ ===="; poetry run python "$_.py" }
poetry run pytest demo_bola.py demo_pickle_trap.py demo_hmac_webhook.py -v
```

---

## Access and authorization

### 1. `demo_bola.py`

**Demonstrates:** an object-level ownership check, which stops broken object-level authorization
(BOLA). Before returning a review, the handler confirms the caller owns it; the fixed handler returns
404 (not 403) so a missing object and a forbidden one look the same and reveal nothing.

```bash
poetry run pytest demo_bola.py -v
```

**Expect:** four tests pass. On the fixed handler user B is denied review R-1 and cannot tell absent
from forbidden; the last test pins the bug, showing the broken handler leaks another user's review.

```text
demo_bola.py::test_fixed_blocks_other_users_with_404 PASSED              [ 25%]
demo_bola.py::test_fixed_allows_the_owner PASSED                         [ 50%]
demo_bola.py::test_fixed_missing_and_forbidden_are_indistinguishable PASSED [ 75%]
demo_bola.py::test_broken_leaks_other_users_data PASSED                  [100%]

============================== 4 passed in 0.02s ==============================
```

---

## Injection and untrusted input

### 2. `demo_sql_injection.py`

**Demonstrates:** a parameterized query, which stops SQL injection. Building SQL by string
concatenation lets the input `' OR '1'='1` become SQL code and return the whole table; passing the
input as a bound parameter treats it as data, so it matches nothing.

```bash
poetry run python demo_sql_injection.py
```

**Expect:** the unsafe query returns all 3 rows for the injection payload; the safe query returns 0
for the same payload and 2 for a real id.

```text
unsafe query with payload -> returned 3 rows: ['R-1', 'R-2', 'R-3']
  the whole table leaked, because the input became SQL code
safe query with payload   -> returned 0 rows: []
  no product literally has that id, so the parameterized query matches none
safe query with real id   -> returned 2 rows: ['R-1', 'R-2']
```

### 3. `demo_mass_assignment.py`

**Demonstrates:** an allowlist bind, which stops mass assignment. Binding the whole request body lets
a crafted field flip `is_approved` and forge an owner; binding only the allowlisted fields ignores the
smuggled ones.

```bash
poetry run python demo_mass_assignment.py
```

**Expect:** the whole-body bind approves itself and sets a false owner; the allowlist bind stays
unapproved and keeps the real caller.

```text
whole-body bind -> is_approved=True, owner_id='user-A'
  the crafted body approved itself and set a false owner
allowlist bind  -> is_approved=False, owner_id='user-B'
  smuggled fields ignored: stays unapproved and owned by the real caller
```

### 4. `demo_pickle_trap.py`

**Demonstrates:** JSON plus a schema check, which stops deserialization code execution. `pickle.loads`
runs code carried in the payload as it loads; parsing JSON and validating the shape only ever produces
data.

```bash
poetry run pytest demo_pickle_trap.py -v
```

**Expect:** three tests pass. The pickle payload writes a sentinel as it loads (code ran); the JSON
path leaves no sentinel and validates the shape, and a bad shape is rejected.

```text
demo_pickle_trap.py::test_pickle_payload_executes_on_load PASSED         [ 33%]
demo_pickle_trap.py::test_json_path_does_not_execute_and_validates_shape PASSED [ 66%]
demo_pickle_trap.py::test_json_schema_rejects_bad_shape PASSED           [100%]

============================== 3 passed in 0.02s ==============================
```

### 5. `demo_ssrf.py`

**Demonstrates:** resolving and checking the host, which stops server-side request forgery (SSRF). An
allowlist plus a check on the resolved address blocks internal targets, including a hostname that
resolves to a loopback address, while an allowlisted image host passes.

```bash
poetry run python demo_ssrf.py
```

**Expect:** the metadata host, localhost, the private-range host, and the host that resolves to
127.0.0.1 are all BLOCKED; the allowlisted image host is ALLOWED.

```text
BLOCKED  http://metadata.internal/latest/meta-data/
         host not on allowlist: 'metadata.internal'
BLOCKED  http://localhost/admin
         host not on allowlist: 'localhost'
BLOCKED  http://db.internal:5432/
         host not on allowlist: 'db.internal'
BLOCKED  https://cdn.example.com.attacker/latest/meta-data/
         resolved to an internal address: 127.0.0.1
ALLOWED  https://images.example.com/avatar/P-77.png
         (simulated 200 OK from 93.184.216.34)
```

---

## Secrets and the supply chain

### 6. `demo_secret_scan.py`

**Demonstrates:** regex secret scanning, the check a pre-commit hook runs to stop a hard-coded secret
from ever being committed. Each finding is reported with a line number and the value redacted.

```bash
poetry run python demo_secret_scan.py
```

**Expect:** three findings, a `stripe_live_key`, a `password_assignment`, and a `bearer_token`, each
redacted to a short head and tail.

```text
found 3 likely secret(s):
  line  7: stripe_live_key      sk_liv...QR
  line  9: password_assignment  passwo...d"
  line 13: bearer_token         Bearer...ZZ

a pre-commit hook would stop the commit until these are removed
```

### 7. `demo_dep_scan.py`

**Demonstrates:** matching pinned versions against an advisory database, the check a CI dependency
scan runs to stop shipping a known-vulnerable dependency.

```bash
poetry run python demo_dep_scan.py
```

**Expect:** one finding, `requests 2.19.1` under advisory ADV-2018-0001, with the fix to upgrade to
2.20.0 or later.

```text
found 1 vulnerable dependency(ies):
  requests 2.19.1  [ADV-2018-0001]
    Credentials leaked to the destination on cross-host redirect.
    fix: upgrade to 2.20.0 or later

a CI dependency scan would fail the build on this finding
```

---

## Cryptography

### 8. `demo_password_hash.py`

**Demonstrates:** salted scrypt hashing, which stops precomputed (rainbow-table) and cheap
brute-force attacks on stored passwords. A random salt makes the same password store as two different
hashes that both still verify; an unsalted SHA-256 gives one fixed value for everyone.

```bash
poetry run python demo_password_hash.py
```

**Expect:** the two scrypt hashes differ but both verify the correct password, the wrong password is
False, and the unsalted SHA-256 is one fixed hex value. The two `hash #.. starts` values carry a
random salt and vary on every run; the SHA-256 line is fixed for this password.

```text
salted scrypt (same password, two stored hashes):
  hash #1 starts 4bb20bb1c363...
  hash #2 starts 4f908c901caa...
  the two stored hashes differ: True
  verify correct password vs #1: True
  verify correct password vs #2: True
  verify wrong password vs #1:   False

unsafe fast unsalted SHA-256 (same password, same output every time):
  c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a
  identical for every user with this password, and cheap to brute-force
```

### 9. `demo_field_encryption.py`

**Demonstrates:** Fernet field encryption, which keeps a stored PII field unreadable at rest and
detects tampering. Encryption turns the field into opaque ciphertext, decryption round-trips it back,
and a modified ciphertext is rejected rather than silently decrypted.

```bash
poetry run python demo_field_encryption.py
```

**Expect:** the plaintext email is absent from the ciphertext, the round trip matches, and a tampered
ciphertext is rejected. The `stored ciphertext` value is a fresh Fernet token and varies on every
run.

```text
original field:   reviewer.priya@example.com
stored ciphertext (unreadable): gAAAAABqj4N6iDWkTTTDtqYV...
  plaintext present in ciphertext? False
decrypted field:  reviewer.priya@example.com
  round trip matches original: True
  tampered ciphertext is rejected, not silently accepted
```

---

## Integrity

### 10. `demo_hmac_webhook.py`

**Demonstrates:** an HMAC-SHA256 signature over the body, which stops a forged or tampered webhook. A
shared secret signs the payload, so the receiver accepts a genuine call and rejects both a wrong
signature and a body changed after signing.

```bash
poetry run pytest demo_hmac_webhook.py -v
```

**Expect:** three tests pass. The genuine signature is accepted; a forged signature and a tampered
body are both rejected.

```text
demo_hmac_webhook.py::test_genuine_signature_is_accepted PASSED          [ 33%]
demo_hmac_webhook.py::test_forged_signature_is_rejected PASSED           [ 66%]
demo_hmac_webhook.py::test_tampered_body_is_rejected PASSED              [100%]

============================== 3 passed in 0.01s ==============================
```

---

## Detection and runtime

### 11. `demo_security_logging.py`

**Demonstrates:** a structured security event with PII masked, so you can detect and audit an
access-denied without writing a raw email to the log. One JSON line carries a trace id, the resource,
and the actor's email masked.

```bash
poetry run python demo_security_logging.py
```

**Expect:** one JSON line with trace id `9f2a-fixed-trace` and the actor masked to `p***@example.com`;
the raw email never appears.

```text
{"level": "security", "event": "review.access_denied", "trace_id": "9f2a-fixed-trace", "resource": "review:R-1", "actor": "p***@example.com"}

raw email present in the log line? False
masked form shown instead:         p***@example.com
```

### 12. `demo_sandbox.py`

**Demonstrates:** running untrusted code in a contained subprocess with a cleaned environment, which
stops the snippet from reading process secrets. In-process `exec` shares this process and sees the
secret; the subprocess is handed a stripped environment and reads `None`.

```bash
poetry run python demo_sandbox.py
```

**Expect:** the in-process `exec` prints the secret value, while the contained subprocess prints
`None` because the secret was stripped from its environment.

```text
in-process exec (shares this process):
snippet sees secret: s3cr3t-demo-value
  the secret leaked, because exec has no boundary

contained subprocess (cleaned env + timeout):
snippet sees secret: None
  the child never received the secret, so it reads None
```

---

Each demo also has a matching "Try it" pointer in the lesson at the topic it illustrates, and the
same ideas are then built for real in the liveLab (`reviews-insight`).
