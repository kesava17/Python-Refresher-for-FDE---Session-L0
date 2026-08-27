# Secure demos: run the attacks and the fixes, do not just read them

Each script is a tiny, self-contained demonstration of one idea from the Secure topic
(building software that resists attack: authorization, injection, unsafe input, secrets,
dependencies, cryptography, logging, and isolation). This folder is its own small Poetry
project, so you run the demos the same way as everything else in this course. Set it up
once, then run any demo:

```bash
poetry install                           # once, from this demos/ folder
poetry run python demo_sql_injection.py
```

Three of the demos are pytest files, so run those with pytest instead of a bare `python`:

```bash
poetry run pytest demo_bola.py -v
poetry run pytest demo_pickle_trap.py -v
poetry run pytest demo_hmac_webhook.py -v
```

The demos use only the standard library, plus `cryptography` (the field-encryption demo)
and `pytest` (the three test files); both are declared here, so run everything through
Poetry. `fastapi` and `httpx` are declared to match the course baseline but are not
imported by these scripts.

| Demo | What it shows | Expected |
| --- | --- | --- |
| `demo_bola.py` | an owner check blocks reading another user's object, with 404 not 403 | pytest: 4 passed; user B is denied review R-1 on the fixed handler and (the bug) reads it on the broken one |
| `demo_sql_injection.py` | string-built SQL leaks the whole table; a parameterized query does not | unsafe query returns 3 rows for the `' OR '1'='1` payload, safe query returns 0, safe query with a real id returns 2 |
| `demo_mass_assignment.py` | binding the whole body lets a crafted field set is_approved; an allowlist blocks it | whole-body bind shows is_approved True and a forged owner, allowlist bind stays False and keeps the real caller |
| `demo_pickle_trap.py` | pickle executes code on load; JSON plus a schema check cannot | pytest: 3 passed; the pickle payload writes the sentinel, the JSON path leaves no sentinel and validates the shape |
| `demo_ssrf.py` | resolving and checking the host blocks internal targets while an allowed host passes | metadata, localhost, and the private-range host are BLOCKED; the allowlisted image host is ALLOWED |
| `demo_secret_scan.py` | regex scanning flags hard-coded secrets with line numbers, like a pre-commit hook | 3 findings: a stripe_live_key, a password_assignment, and a bearer_token, each redacted |
| `demo_dep_scan.py` | pinned versions are matched against an advisory database, like a CI scan | 1 finding: requests 2.19.1 [ADV-2018-0001], fix upgrade to 2.20.0 or later |
| `demo_password_hash.py` | salted scrypt stores the same password as two different hashes and still verifies | the two scrypt hashes differ, all correct-password verifies are True, the wrong password is False, unsalted SHA-256 is one fixed value |
| `demo_field_encryption.py` | Fernet encrypts a field to unreadable ciphertext and decrypts it back | the plaintext is absent from the ciphertext, the round trip matches, a tampered ciphertext is rejected |
| `demo_hmac_webhook.py` | an HMAC-SHA256 signature accepts a genuine webhook and rejects a forged one | pytest: 3 passed; genuine signature accepted, forged signature and tampered body rejected |
| `demo_security_logging.py` | a structured JSON security event with the actor's email masked | one JSON line with trace_id 9f2a-fixed-trace, actor `p***@example.com`, and the raw email absent |
| `demo_sandbox.py` | in-process exec reads a secret; a contained subprocess with a cleaned env does not | exec prints the secret value, the subprocess prints `None` because the secret was stripped from its environment |

The exact numbers do not matter; the pattern is the point. The lesson points you to each of
these with a "Try it" note at the matching topic.
