# Secure Setup and Run Cheatsheet

Everything you need to get the Secure code running, on one page. This topic is about building
software that resists attack: object-level authorization, injection, unsafe input, secrets in code,
vulnerable dependencies, cryptography for data at rest and in transit, safe security logging, and
process isolation. This page is a setup-and-run guide, not a recap of those ideas. It covers how to
run all four Secure samples: the **concept demos**, the **live-lab** (`reviews-insight`), and the two
**assignments**. As always in this course, run everything through `poetry run`.

There is no new software to install for this topic. Everything runs on the Day 1 toolchain (Poetry and
Python 3.11 or newer, plus WSL on Windows) and the Poetry packages each project already declares
(`fastapi`, `httpx`, `pytest`, `cryptography`). `poetry install` pulls those in per project.

---

## 0. Prerequisites (Day 1 toolchain, nothing new)

Confirm the Day 1 toolchain is in place. If any of these is missing, go back to the Day 1 setup
cheatsheet first.

```bash
python3 -V          # Python 3.11 or newer
poetry --version    # Poetry 2.x
git version
```

- On Windows, do all of this **inside WSL** (the Ubuntu terminal), as set up on Day 1.
- **Docker is not needed to run the samples.** Each project ships a `Dockerfile` you can read, and the
  three services build a container that runs as a **non-root** user, but you do not have to build or
  run any image for this topic.
- **Additional software: none.** The packages the code uses (`fastapi`, `httpx`, `pytest`, and
  `cryptography` for the encryption work) are declared in each project, and `poetry install` pulls
  them in. There is nothing to install by hand.
- **A benign deprecation warning is expected.** When you run the API tests or drive the HTTP API, you
  may see a single Starlette/httpx `DeprecationWarning`. It is harmless and does not affect the
  result; ignore it.

---

## 1. The concept demos: run the attacks and the fixes

Small, self-contained scripts you run while reading the lesson, at each **Try it** note. They live in
the Secure workspace's `demos/` folder, which is its own tiny Poetry project. Each script is heavily
commented, so open the file as you run it.

**Set up once**, from inside the `demos/` folder:

```bash
cd demos
poetry install
```

**Then run any demo** with `poetry run python <name>.py`. There are **twelve** demos. Three of them are
pytest files, so run those with `poetry run pytest <name>.py -v` instead of a bare `python`. Here they
are in lesson order, with what to expect (from `demos/README.md`):

```bash
poetry run pytest demo_bola.py -v              # 4 passed; user B is denied review R-1 on the fixed handler, reads it on the broken one
poetry run python demo_sql_injection.py        # unsafe query returns 3 rows for the ' OR '1'='1 payload, safe returns 0, safe with a real id returns 2
poetry run python demo_mass_assignment.py      # whole-body bind sets is_approved True and a forged owner; the allowlist bind stays False and keeps the real caller
poetry run pytest demo_pickle_trap.py -v       # 3 passed; the pickle payload writes the sentinel, the JSON path leaves none and validates the shape
poetry run python demo_ssrf.py                 # metadata, localhost, and the private-range host are BLOCKED; the allowlisted image host is ALLOWED
poetry run python demo_secret_scan.py          # 3 findings: a stripe_live_key, a password_assignment, and a bearer_token, each redacted
poetry run python demo_dep_scan.py             # 1 finding: requests 2.19.1 [ADV-2018-0001], fix upgrade to 2.20.0 or later
poetry run python demo_password_hash.py        # the two scrypt hashes differ, correct-password verifies are True, the wrong one is False, unsalted SHA-256 is one fixed value
poetry run python demo_field_encryption.py     # the plaintext is absent from the ciphertext, the round trip matches, a tampered ciphertext is rejected
poetry run pytest demo_hmac_webhook.py -v      # 3 passed; genuine signature accepted, forged signature and tampered body rejected
poetry run python demo_security_logging.py     # one JSON line with trace_id 9f2a-fixed-trace, actor p***@example.com, and the raw email absent
poetry run python demo_sandbox.py              # exec prints the secret value, the contained subprocess prints None because the secret was stripped from its environment
```

To run every plain-script demo in one go:

```bash
for f in demo_*.py; do echo "== $f =="; poetry run python "$f"; done
```

(That loop runs the nine plain scripts. Run the three pytest demos, `demo_bola.py`,
`demo_pickle_trap.py`, and `demo_hmac_webhook.py`, with `poetry run pytest <name>.py -v`.)

The exact numbers do not matter; the pattern is the point. `demos/README.md` has the same list in a
table.

---

## 2. The live-lab: `reviews-insight`

This is the running application you harden in the live lab (`reviews-insight` version 0.7.0). `cd` into
it, install, then run the CLI summary.

```bash
cd reviews-insight     # or wherever the Secure liveLab project is
poetry install
poetry run reviews summary
```

The summary prints a small count block. The two rejected rows are the sample's malformed rows,
rejected honestly rather than being silently coerced into bad data:

```
reviews : 5
products: 3
rejected: 2
```

**Run the quality gate:**

```bash
poetry run pytest -q          # 33 passed
poetry run ruff check .
poetry run mypy src
```

All **33 tests pass** (API contract, dependability, and the security tests). The lint and type checks
report no problems.

**Run the repo secret scan.** This walks the source for hard-coded secrets, the same check a
pre-commit hook or CI step would run:

```bash
poetry run python scripts/secret_scan.py
# exit code 0 (a clean tree finds nothing)
```

A clean tree exits `0`. If it ever finds a hard-coded secret it prints the file, line, and a redacted
match, and exits non-zero.

**Serve the HTTP API.** Start it and leave it running in its own terminal:

```bash
poetry run reviews serve
```

It serves on `http://127.0.0.1:8000`. The routes include `GET /health` (liveness), `GET /ready`
(readiness), `GET /metrics` (the SLIs as plain text), `GET /v1/reviews/{id}` (object-level
authorization, which requires an `X-User-Id` header and only returns a review the caller owns),
`POST /v1/reviews` (submit), and the other paginated `GET`/`POST` review routes. You can also open
`http://127.0.0.1:8000/docs` to try the endpoints interactively.

**Try the object-level check** from a second terminal. A caller can read only a review they own; asking
for another user's review returns a `404`, not a `403`, so the endpoint does not confirm the object
exists:

```bash
curl -s http://127.0.0.1:8000/v1/reviews/R-1 -H 'X-User-Id: user-a'
```

**Note on the container.** The shipped `Dockerfile` builds an image that runs as a **non-root** user,
so a compromised process does not start with root inside the container. You do not need to build it to
finish the lab.

---

## 3. Assignment 01: `telemetry-insight`

A device readings feed you secure the same way (`telemetry-insight` version 0.7.0). Its own Poetry
project. `cd` into it, install, then run.

```bash
cd assignment01     # or wherever the Secure assignment 01 project is
poetry install
poetry run pytest -q          # 30 passed
poetry run telemetry summary
```

All **30 tests pass**. The summary prints the same shape of count block, with two malformed rows
rejected:

```
readings: 5
devices : 3
rejected: 2
```

Serve it the same way as the live-lab (`poetry run telemetry serve`, on `http://127.0.0.1:8000`). Its
`GET /v1/readings/{id}` applies the same **object-level authorization** as the live-lab: the caller
gets back only a reading they own. Run the repo secret scan the same way, and it exits `0` on a clean
tree:

```bash
poetry run python scripts/secret_scan.py
# exit code 0
```

---

## 4. Assignment 02: `transactions-insight`

An account transactions feed you secure end to end (`transactions-insight` version 0.7.0). Its own
Poetry project, run the same way.

```bash
cd assignment02     # or wherever the Secure assignment 02 project is
poetry install
poetry run pytest -q          # 34 passed
poetry run transactions summary
```

All **34 tests pass**. The summary prints the count block, with two malformed rows rejected rather than
coerced:

```
transactions: 5
accounts    : 3
rejected    : 2
```

Serve it the same way (`poetry run transactions serve`, on `http://127.0.0.1:8000`). Its
`GET /v1/transactions/{id}` applies **object-level authorization**, so a caller reads only a
transaction they own. Run the repo secret scan the same way, and it exits `0` on a clean tree:

```bash
poetry run python scripts/secret_scan.py
# exit code 0
```

---

## 5. The commands you use everywhere (recap)

- `poetry install` sets up a project's own environment and pulls in `fastapi`, `httpx`, `pytest`, and
  `cryptography`.
- `poetry run <cmd>` runs inside that environment. Never use a bare `python` for project code.
- `poetry run pytest -q`, `poetry run ruff check .`, `poetry run mypy src` are the quality gate.
- `poetry run reviews summary` runs the live-lab; `poetry run reviews serve` starts the HTTP API.
- `poetry run python scripts/secret_scan.py` scans the tree for hard-coded secrets and exits `0` when
  it is clean.

---

## 6. Readiness check

- [ ] `python3 -V` shows 3.11 or newer and `poetry --version` shows Poetry 2.x (from Day 1).
- [ ] In `demos/`, `poetry install` succeeds and all **12** demos run: nine via
  `poetry run python <name>.py` and three via `poetry run pytest <name>.py -v` (`demo_bola.py`,
  `demo_pickle_trap.py`, `demo_hmac_webhook.py`).
- [ ] The `reviews-insight` project runs `poetry run reviews summary` and shows `reviews : 5`,
  `products: 3`, `rejected: 2`.
- [ ] `poetry run pytest -q` passes all **33** tests in `reviews-insight`, and `ruff check .` plus
  `mypy src` report no problems.
- [ ] `poetry run reviews serve` starts the API on `http://127.0.0.1:8000`;
  `GET /v1/reviews/{id}` with an `X-User-Id` header returns only a review that caller owns.
- [ ] `poetry run python scripts/secret_scan.py` exits `0` in each of the three service projects.
- [ ] `assignment01` (`telemetry-insight`) passes **30** tests and its summary shows `readings: 5`,
  `devices : 3`, `rejected: 2`.
- [ ] `assignment02` (`transactions-insight`) passes **34** tests and its summary shows
  `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- [ ] You saw the single Starlette/httpx deprecation warning and know it is harmless.

If every line checks out, you can run every Secure sample and follow every **Try it** in the lesson.
