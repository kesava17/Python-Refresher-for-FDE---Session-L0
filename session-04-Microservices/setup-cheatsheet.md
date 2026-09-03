# Microservices Setup and Run Cheatsheet

Everything you need to get the Microservices Architecture code running, on one page. This topic
redesigns the `reviews-insight` service into a small system: two vertical slices behind a gateway, each
owning its store, talking over a versioned contract and an event, with guarded calls and a shared
correlation id. This page is a setup-and-run guide, not a recap of those ideas. It covers how to run
all four samples: the **concept demos**, the **liveLab** (`reviews-insight`), and the two **assignments**
(`telemetry-insight` and `transactions-insight`). As always in this course, run everything through
`poetry run`.

---

## 0. Prerequisites

Confirm the Day 1 toolchain is in place. If any of these is missing, go back to the Day 1 setup
cheatsheet first.

```bash
python3 -V          # Python 3.11 or newer
poetry --version    # Poetry 2.x
git version
```

- On Windows, do all of this **inside WSL** (the Ubuntu terminal), as set up on Day 1.
- **Docker is needed for the Compose run only.** This topic ships a `docker-compose.yml` that runs the
  three services as real, separate processes on their own ports. You need Docker (Docker Desktop with
  the WSL backend, or Docker Engine inside WSL) for that one step. Everything else (tests, the smoke
  script, the demos) runs without Docker. Check it with:

  ```bash
  docker --version
  docker compose version
  ```

- **Extra dependencies this topic adds.** The liveLab and both assignments serve HTTP and call between
  services, so they declare `fastapi` and `uvicorn` (serving), `httpx` (the calls between services),
  and `tenacity` (retry with backoff), on top of the `pytest`, `ruff`, and `mypy` dev tools. There is
  nothing to install by hand: `poetry install` in each project pulls them in. The concept demos are
  standard-library only.
- **A benign deprecation warning is expected.** When you run the tests or drive the HTTP API, you may
  see a single Starlette or httpx `DeprecationWarning`. It is harmless and does not affect the result;
  ignore it.

---

## 1. The concept demos: see one idea at a time

Six tiny, runnable scripts, one microservice idea each, standard library only. They are the "see it" to
the liveLab's "build it". They live in the workspace's `demos/` folder, which is its own small Poetry
project. Each script is heavily commented, so open the file as you run it.

**Set up once**, from inside the `demos/` folder:

```bash
cd demos
poetry install
poetry run python demo_two_services.py
```

**Then run any demo** with `poetry run python <name>.py`. Here they are in lesson order, with what to
watch for (from `demos/README.md`):

```bash
poetry run python demo_two_services.py        # an orders service calling an inventory service over a local port
poetry run python demo_sync_vs_async.py       # a blocking call taking 0.20s, and a handoff returning at once
poetry run python demo_timeout_retry.py       # two failures retried to success, and a slow call cut off at 0.3s
poetry run python demo_circuit_breaker.py     # the circuit opening on the third failure, half-opening after cooldown
poetry run python demo_idempotent_consumer.py # a redelivered event skipped, so the total does not double-count
poetry run python demo_data_per_service.py    # the query side building its own view without opening the ingest store
```

To run all six in one go:

```bash
for f in demo_*.py; do echo "== $f =="; poetry run python "$f"; done
```

The exact numbers do not matter; the pattern is the point. `demos/README.md` and `demos/cookbook.md`
have the same list with a guided walkthrough.

---

## 2. The liveLab: `reviews-insight`

This is the running system you build in the live lab (`reviews-insight-microservices` version 1.0.0):
`reviews-ingest` and `reviews-query` behind a `gateway`. `cd` into it and install.

```bash
cd liveLab     # or wherever the Microservices liveLab project is
poetry install
```

**Run the quality gate.** The tests wire the services together in-process over a shared temporary
broker, so nothing needs to be listening:

```bash
poetry run pytest              # 16 passed
poetry run ruff check src tests
poetry run mypy src
```

All **16 tests pass** (contract, each slice, gateway degradation, resilience, and observability). The
lint and type checks report no problems.

**Run the end-to-end smoke** in one process. It submits reviews through reviews-ingest, lets
reviews-query consume the events, reads the aggregate back, replays an event to show the idempotent
consumer, and asks for an unknown product:

```bash
poetry run python scripts/smoke.py
```

Expect the aggregate to reach `count 3, average 4.0`, a replayed event that leaves it unchanged, and a
404 for the unknown product.

**Run the whole system with Docker Compose.** This is the only step that needs Docker. One image is
built and run three times with a different command, each service on its own port:

```bash
docker compose up --build
# gateway on http://localhost:8000, reviews-ingest on 8001, reviews-query on 8002
```

From a second terminal, submit a review and read the dashboard through the gateway:

```bash
curl -s -X POST http://localhost:8000/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "p1", "rating": 5, "text": "great"}'

curl -s http://localhost:8000/bff/dashboard/p1
```

The `tests/http/reviews.http` and `tests/http/services.http` files hold these same calls for an
editor's REST client. See `liveLab-cookbook.md` for the guided run-and-explore walkthrough.

---

## 3. Assignment 01: `telemetry-insight`

A device readings feed you redesign the same way (`telemetry-insight-microservices` version 1.0.0):
`telemetry-ingest` and `telemetry-rollup` behind a gateway, its focus the asynchronous split and
idempotency. Its own Poetry project.

```bash
cd assignment01     # or wherever the Microservices assignment 01 project is
poetry install
poetry run pytest              # 18 passed
poetry run ruff check src tests
poetry run mypy src
```

All **18 tests pass**. Run its smoke and Compose stack the same way as the liveLab:

```bash
poetry run python scripts/smoke.py
docker compose up --build
```

---

## 4. Assignment 02: `transactions-insight`

A financial account transactions feed you redesign end to end
(`transactions-insight-microservices` version 1.0.0): `transactions-service` and a `ledger-service`
behind a gateway, its focus a versioned contract plus resilience (timeout, retry, circuit breaker). Its
own Poetry project, run the same way.

```bash
cd assignment02     # or wherever the Microservices assignment 02 project is
poetry install
poetry run pytest              # 20 passed
poetry run ruff check src tests
poetry run mypy src
```

All **20 tests pass**. Run its smoke and Compose stack the same way:

```bash
poetry run python scripts/smoke.py
docker compose up --build
```

---

## 5. Troubleshooting

- **`poetry install` is slow the first time.** It builds a fresh virtual environment per project and
  pulls `fastapi`, `uvicorn`, `httpx`, and `tenacity`. That is expected once per project; later runs
  are fast.
- **`docker compose` says the command is not found.** On older Docker the subcommand was
  `docker-compose` (with a hyphen). Prefer a current Docker with the built-in `docker compose`, run
  inside WSL.
- **A port is already in use (8000, 8001, or 8002).** Something else is listening. Stop it, or stop a
  previous stack with `docker compose down`, then bring it up again.
- **The dashboard returns `"note": "temporarily unavailable"`.** That is the design working, not a
  bug: reviews-query is down or the circuit breaker is open. Start the service (`docker compose start
  reviews-query`) and let the cooldown pass.
- **A submit returns 502.** reviews-ingest is unreachable; a write fails fast on purpose rather than
  hanging. Start the service and retry.
- **You see a single Starlette or httpx deprecation warning.** It is harmless; ignore it.
- **Never use a bare `python`.** Always run project code through `poetry run` so it uses that project's
  environment.

---

## 6. Readiness check

- [ ] `python3 -V` shows 3.11 or newer and `poetry --version` shows Poetry 2.x (from Day 1).
- [ ] `docker --version` and `docker compose version` both work inside WSL.
- [ ] In `demos/`, `poetry install` succeeds and all **6** demos run via `poetry run python <name>.py`.
- [ ] The `liveLab` project passes all **16** tests with `poetry run pytest`, and `ruff check src tests`
  plus `mypy src` report no problems.
- [ ] `poetry run python scripts/smoke.py` in `liveLab` reaches `count 3, average 4.0`, shows the
  replayed event not double-counting, and returns 404 for the unknown product.
- [ ] `docker compose up --build` in `liveLab` brings up the gateway on 8000, reviews-ingest on 8001,
  and reviews-query on 8002, and the dashboard through the gateway returns a summary.
- [ ] `assignment01` (`telemetry-insight`) passes **18** tests.
- [ ] `assignment02` (`transactions-insight`) passes **20** tests.
- [ ] You saw the single Starlette or httpx deprecation warning and know it is harmless.

If every line checks out, you can run every Microservices sample and follow every **Try it** in the
lesson.
