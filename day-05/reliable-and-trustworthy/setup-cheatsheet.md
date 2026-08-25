# Dependable Setup and Run Cheatsheet

Everything you need to get the Dependable code running, on one page. This topic is about being
**reliable and trustworthy**: the service holds up under real load, you can prove it holds up, and it
fails in safe ways when a dependency is slow or a process is killed mid-write. The topics covered are
SLOs and error budgets, graceful degradation on timeout, safe retries with idempotency, load
shedding, bounded memory, crash recovery, structured logging, and gated rollouts.

There is no new software to install for this topic. Everything runs on the toolchain you set up on
Day 1 (Poetry and Python 3.11 or newer, plus WSL on Windows) and the same Poetry packages the
interoperable topic already added (`fastapi`, `uvicorn`, `httpx`). `poetry install` pulls those in per
project. This page covers how to run all four Dependable samples: the **concept demos**, the
**live-lab** (`reviews-insight`), and the two **assignments**. As always in this course, run
everything through `poetry run`.

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
- **Docker is not needed for this topic.** The Postgres stub from Day 1 is only used on a later day,
  so you do not have to start it now.
- **Additional software: none.** The three Poetry packages the API uses (`fastapi`, `uvicorn`,
  `httpx`) are declared in each project, and `poetry install` pulls them in. There is no separate
  software to install.
- **A benign deprecation warning is expected.** When you run the API tests or the soak scripts, you
  may see a single Starlette/httpx `DeprecationWarning`. It is harmless and does not affect the
  result; ignore it.

---

## 1. The concept demos: run and execute them

Small, one-idea scripts you run while reading the lesson, at each **Try it** note. They live in the
Dependable workspace's `demos/` folder, which is its own tiny Poetry project. Each script is heavily
commented, so open the file as you run it.

**Set up once**, from inside the `demos/` folder:

```bash
cd demos
poetry install
```

**Then run any demo** with `poetry run python <name>.py`. There are ten demos. Two of them are pytest
files, so run those with `poetry run pytest <name>.py -v` instead of a bare `python`. Here they are in
lesson order, with what to expect:

```bash
poetry run python demo_slo_burn.py                        # 40 failures spend 4x a budget of 10 -> "budget burned too fast: ALERT"
poetry run pytest demo_degrade_on_timeout.py -v           # on timeout the result is enriched=False and insight=None
poetry run python demo_latency_percentiles.py             # p50 ~41 ms, p99 ~930 ms, mean ~76 ms (the tail hides from the mean)
poetry run python demo_retry_idempotency.py               # no key applies twice; with a key it applies exactly once
poetry run python demo_load_shedding.py                   # 10 offered, 4 accepted, 6 shed with a fast 429
poetry run python demo_soak_flat.py                       # the unbounded dict climbs; the lru_cache holds flat at 128
poetry run python demo_restart_resumes.py                 # crash then resume, no lost and no duplicated records
poetry run pytest demo_crash_in_the_middle.py -v          # store holds 0 after an interrupted write, 1 after a clean write
poetry run python demo_structured_logging.py              # JSON log lines with trace ids, filterable by id
poetry run python demo_rollback_gate.py                   # "rollout v2 -> readiness FAIL -> auto rollback to v1"
```

To run every plain-script demo in one go:

```bash
for f in demo_*.py; do echo "== $f =="; poetry run python "$f"; done
```

(That loop runs the eight plain scripts. Run the two pytest demos, `demo_degrade_on_timeout.py` and
`demo_crash_in_the_middle.py`, with `poetry run pytest <name>.py -v`.)

Times and sizes vary with your machine; the pattern is the point, not the exact number.
`demos/README.md` has the same list in a table.

---

## 2. The live-lab: `reviews-insight`

This is the running application you make dependable in the live lab (`reviews-insight` version 0.6.0).
It keeps the versioned HTTP API from the interoperable topic and adds the operational habits that keep
a service up: a timeout with graceful degradation, idempotent submit, a readiness endpoint, structured
logging, and SLI metrics. If you built it during the live lab you are already inside the
`reviews-insight` folder; if you are using the provided project, `cd` into it first.

```bash
cd reviews-insight     # or wherever the Dependable liveLab project is
poetry install
poetry run reviews summary
```

The summary prints a small count block. The first line comes from the `@timed` decorator, so the exact
millisecond figure varies with your machine:

```
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
rejected: 2
```

The two rejected rows are the sample's malformed rows, rejected honestly rather than being silently
coerced into bad data.

**Run the quality gate** the same way as Day 1:

```bash
poetry run pytest -q          # 26 passed
poetry run ruff check .
poetry run mypy src
```

All **26 tests pass** (including the API contract tests and the dependability tests). The lint and type
checks report no problems.

**Serve the HTTP API.** Start the API and leave it running in its own terminal:

```bash
poetry run reviews serve
```

It serves on `http://127.0.0.1:8000`. The routes are `GET /health` (liveness), `GET /ready`
(readiness, which reflects in-flight capacity), `GET /metrics` (the SLIs as plain text),
`POST /v1/reviews` (submit, which accepts an `Idempotency-Key` header), the paginated `GET /v1/reviews`,
and `GET /v1/insight`. Every response also carries an `x-trace-id` header (the one you sent, or one the
server generated). You can also open `http://127.0.0.1:8000/docs` in a browser to try the endpoints
interactively.

**Submit a review** from a second terminal. The submit path always accepts a valid review, enriched
when the enrichment dependency answers and degraded when it does not:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-1' \
  -d '{"product_id": "P-77", "rating": 5}'
# {"status":"accepted","enriched":false}
```

`enriched` is `false` here on purpose. The default enrichment URL is `http://enrichment.invalid/enrich`,
which does not resolve, so the call times out or fails and the service degrades gracefully instead of
failing the submit. Sending the same `Idempotency-Key` again returns the same result and does not store
a second review.

**Read the metrics.** After a few requests, the SLI counters are exposed as plain text:

```bash
curl -s http://127.0.0.1:8000/metrics
# requests_total 3
# errors_total 0
# request_duration_ms_sum 12.34
# request_duration_ms_avg 4.11
```

**Run the soak test.** This proves memory stays flat over a long run rather than climbing (a leak):

```bash
poetry run python scripts/soak.py
```

It drives the core loop for **2000 iterations** and prints the traced memory at intervals. The number
stays flat across runs, which means the loop retains no growing state and does not leak.

---

## 3. Assignment 01: `telemetry-insight`

A device readings feed you make dependable under load (`telemetry-insight` version 0.6.0). Each
assignment is its own Poetry project. `cd` into it, `poetry install`, then run.

```bash
cd assignment01     # or wherever the Dependable assignment 01 project is
poetry install
poetry run pytest -q          # 25 passed
poetry run telemetry summary
```

All **25 tests pass**. The summary prints the same shape of count block, with two malformed rows
rejected:

```
readings: 5
devices : 3
rejected: 2
```

Serve it the same way as the live-lab (`poetry run telemetry serve`, on `http://127.0.0.1:8000`). On
top of the interoperable routes it adds `GET /ready`, `GET /metrics`, **load shedding** (excess
concurrent work is shed with a fast `429`), and idempotency on ingest via an `Idempotency-Key` header.
The soak script proves flat memory over a longer run:

```bash
poetry run python scripts/soak.py
```

It drives ingest for **8000 iterations** and holds the store flat under dedup, so memory does not climb.

---

## 4. Assignment 02: `transactions-insight`

An account transactions feed you make dependable with no data loss and an exactly-once effect
(`transactions-insight` version 0.6.0). Its own Poetry project, run the same way.

```bash
cd assignment02     # or wherever the Dependable assignment 02 project is
poetry install
poetry run pytest -q          # 29 passed
poetry run transactions summary
```

All **29 tests pass**. The summary prints the count block, with two malformed rows rejected rather than
coerced:

```
transactions: 5
accounts    : 3
rejected    : 2
```

Serve it the same way (`poetry run transactions serve`, on `http://127.0.0.1:8000`). On top of the
interoperable routes it adds `GET /ready`, `GET /metrics`, and **exactly-once idempotency** on
`POST /v1/transactions`: a client that retries the same transaction with the same `Idempotency-Key`
produces exactly one stored transaction, so a retried money write is applied once, never twice.

---

## 5. The commands you use everywhere (recap)

- `poetry install` sets up a project's own environment and pulls in `fastapi`, `uvicorn`, and `httpx`.
- `poetry run <cmd>` runs inside that environment. Never use a bare `python` for project code.
- `poetry run pytest -q`, `poetry run ruff check .`, `poetry run mypy src` are the quality gate.
- `poetry run reviews summary` runs the live-lab; `poetry run reviews serve` starts the HTTP API;
  `poetry run python scripts/soak.py` proves flat memory over a long run.
- `curl http://127.0.0.1:8000/metrics` reads the SLI counters; `curl -X POST .../v1/reviews` submits a
  review with an `Idempotency-Key` header.

---

## 6. Readiness check

- [ ] `python3 -V` shows 3.11 or newer and `poetry --version` shows Poetry 2.x (from Day 1).
- [ ] In `demos/`, `poetry install` succeeds and `poetry run python demo_slo_burn.py` ends with
  "budget burned too fast: ALERT". All ten demos run (two of them via `poetry run pytest ... -v`).
- [ ] The `reviews-insight` project runs `poetry run reviews summary` and shows `reviews : 5`,
  `products: 3`, `rejected: 2`, with a `[timed] summary:` line above it.
- [ ] `poetry run pytest -q` passes all **26** tests in `reviews-insight`.
- [ ] `poetry run reviews serve` starts the API on `http://127.0.0.1:8000`; a `POST /v1/reviews` returns
  `{"status":"accepted","enriched":false}` and `GET /metrics` returns the `requests_total` block.
- [ ] `poetry run python scripts/soak.py` in `reviews-insight` holds memory flat across 2000 iterations.
- [ ] `assignment01` (`telemetry-insight`) passes **25** tests and its summary shows `readings: 5`,
  `devices : 3`, `rejected: 2`.
- [ ] `assignment02` (`transactions-insight`) passes **29** tests and its summary shows
  `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- [ ] You saw the single Starlette/httpx deprecation warning and know it is harmless.

If every line checks out, you can run every Dependable sample and follow every **Try it** in the lesson.
