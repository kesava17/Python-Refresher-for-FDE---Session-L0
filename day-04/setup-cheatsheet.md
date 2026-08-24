# Day 5 Setup and Run Cheatsheet

Everything you need to get the Day 5 code running, on one page. Day 5 is about being **interoperable**:
your code talks to other code across a boundary, whether that boundary is an HTTP request, a native
library, or a JSON document. To do that, Day 5 adds three Python packages via Poetry: `fastapi`,
`uvicorn`, and `httpx`. `poetry install` pulls them in; there is still no separate software to
install. Everything else uses the toolchain you set up on Day 1 (Poetry, Python 3.11 or newer, and on
Windows, WSL) plus the standard library (`ctypes`, `zlib`, `json`, `dataclasses`).

This page covers how to run the three Day 5 samples: the **concept demos**, the **live-lab**
(`reviews-insight`), and the two **assignments**. As always in this course, run everything through
`poetry run`.

---

## 0. Prerequisites (Day 1 toolchain plus three Poetry packages)

Confirm the Day 1 toolchain is in place. If any of these is missing, go back to the Day 1 setup
cheatsheet first.

```bash
python3 -V          # Python 3.11 or newer
poetry --version    # Poetry 2.x
git version
```

- On Windows, do all of this **inside WSL** (the Ubuntu terminal), as set up on Day 1.
- **Docker is not needed for Day 5.** The Postgres stub from Day 1 is only used on a later day, so
  you do not have to start it now.
- **Additional software for Day 5: none.** Day 5 adds three Python packages via Poetry: `fastapi`,
  `uvicorn`, and `httpx`. `poetry install` pulls them in; there is still no separate software to
  install.

---

## 1. The concept demos: run and execute them

Small, one-idea scripts you run while reading the lesson, at each **Try it** note. They live in the
Day 5 workspace's `demos/` folder, which is its own tiny Poetry project. Each script is heavily
commented, so open the file as you run it.

**Set up once**, from inside the `demos/` folder:

```bash
cd demos
poetry install
```

**Then run any demo** with `poetry run python <name>.py`. The demos that reach a web boundary need
the packages `poetry install` just pulled in, so run these through `poetry run`. Here are all twelve,
in lesson order, with what to expect:

```bash
poetry run python demo_edge_validation.py      # a pydantic model rejects rating 11 with a ValidationError
poetry run python demo_rest_contract.py        # a FastAPI app via TestClient: health ok, valid POST 201, rating 11 -> 422, openapi has /v1/reviews
poetry run python demo_response_model.py       # a response model validates the reply on the way out, not just the request
poetry run python demo_pagination.py           # a list endpoint returns one page plus the total, never the whole collection
poetry run python demo_n_plus_one.py           # one query per item is slow; one batched query returns the same data fast
poetry run python demo_webhook_signature.py    # an HMAC signature is verified before the webhook body is trusted; a forged one is refused
poetry run python demo_trace_id.py             # a trace id is reused or generated and echoed on the response, tying a request's logs together
poetry run python demo_ctypes_call.py          # C strlen called across the ctypes boundary
poetry run python demo_native_speed.py         # pure-Python CRC32 vs native zlib, native far faster
poetry run python demo_coarse_vs_fine.py       # one coarse crossing beats one call per item
poetry run python demo_error_translation.py    # a boundary error re-raised as a clear domain error
poetry run python demo_json_interop.py         # a dataclass round-trips through JSON
```

To run them all in one go:

```bash
for f in demo_*.py; do echo "== $f =="; poetry run python "$f"; done
```

Times and sizes vary with your machine; the pattern is the point, not the exact number.
`demos/README.md` has the same list in a table.

---

## 2. The live-lab: `reviews-insight`

This is the running application you make interoperable on Day 5 (a versioned HTTP API with validation
at the edge, a native fast path for a hot loop, and clean JSON contracts across every boundary). If
you built it during the live lab you are already inside the `reviews-insight` folder; if you are using
the provided project, `cd` into it first.

```bash
cd reviews-insight     # or wherever the Day 5 liveLab project is
poetry install
poetry run reviews summary
```

The summary prints a small count block. The first line comes from the `@timed` decorator, a
cross-cutting concern kept out of the service logic, so the exact millisecond figure varies with
your machine:

```
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
rejected: 2
```

The two rejected rows are the sample's malformed rows, rejected honestly rather than being silently
coerced into bad data.

**Serve the versioned HTTP API.** Start the API and leave it running in its own terminal:

```bash
poetry run reviews serve
```

It serves on `http://127.0.0.1:8000`. The routes are `GET /health`, `POST /v1/reviews`, the paginated
`GET /v1/reviews?limit=20&offset=0`, `GET /v1/insight`, the signed `POST /v1/webhooks/rating`, and the
machine-readable contract at `GET /openapi.json`. Every response also carries an `x-trace-id` header
(the one you sent, or one the server generated). You can also open `http://127.0.0.1:8000/docs` in a
browser to try the endpoints interactively.

**Run the native benchmark.** This shows why the native fast path is worth crossing the boundary:

```bash
poetry run python scripts/benchmark_native.py
```

The pure-Python CRC32 takes roughly 100 ms; the native `zlib` CRC takes roughly 0.05 ms, about a
thousand times faster. The exact numbers vary by machine, but the native step wins by a wide margin
every time.

Run the quality gate the same way as Day 1:

```bash
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

Nineteen tests pass, including 8 API contract tests (in `tests/test_api.py`) and 2 native tests. A
single `StarletteDeprecationWarning` is expected and harmless. The Day 5 proofs to look for:

1. **Validation happens at the edge, both ways.** A request with `rating` 11 is rejected with a `422`
   before any business logic runs, and the create route also validates its reply against the
   `ReviewAccepted` response model. Bad input never reaches the service.
2. **The list endpoint pages.** `GET /v1/reviews` returns one page of items plus the `total`, not the
   whole collection.
3. **The webhook is trusted only when signed.** `POST /v1/webhooks/rating` verifies the HMAC signature
   over the raw body and answers `401` for a forged `x-signature`, before the payload is used.
4. **Every request can be traced.** The trace-id middleware returns an `x-trace-id` header, reusing the
   caller's value or generating one.
5. **The native step is measurably faster.** The native `zlib` CRC path beats the pure-Python loop by
   a wide margin, as the benchmark shows.

---

## 3. The offline assignments

Each is its own Poetry project. `cd` into it, `poetry install`, then run.

**Assignment 01, `telemetry-insight`** (a device readings feed given a versioned ingestion and query
API with edge validation, plus a native routine for a hot loop):

```bash
poetry run telemetry summary
```

It prints the same shape of count block, with two malformed rows rejected:

```
readings: 5
devices : 3
rejected: 2
```

It also exposes versioned ingestion and query endpoints over HTTP and uses a native routine for the
hot loop, the same two Day 5 proofs as the live-lab: validation at the edge, and a native fast path.

**Assignment 02, `transactions-insight`** (an account transactions feed given a versioned scoring
endpoint with edge validation, plus a native checksum):

```bash
poetry run transactions summary
```

Again, two malformed rows are rejected rather than coerced:

```
transactions: 5
accounts    : 3
rejected    : 2
```

It also exposes a versioned `/v1/score` endpoint that validates its input at the edge and uses a
native checksum for its hot loop.

---

## 4. The commands you use everywhere (recap)

- `poetry install` sets up a project's own environment, and on Day 5 it pulls in `fastapi`,
  `uvicorn`, and `httpx`.
- `poetry run <cmd>` runs inside that environment. Never use a bare `python` for project code.
- `poetry run pytest -q`, `poetry run ruff check .`, `poetry run mypy src` are the quality gate.
- `poetry run reviews summary` runs the live-lab; `poetry run reviews serve` starts the versioned HTTP
  API; `poetry run python scripts/benchmark_native.py` shows the native fast path.

---

## 5. Troubleshooting

- **`can't open file '...py:'`** You have a stray character (usually a `:`) on the end of the
  command. Retype it: `poetry run python demo_edge_validation.py`, no trailing colon.
- **`ModuleNotFoundError: No module named 'fastapi'`** (or `uvicorn`, or `httpx`). You have not run
  `poetry install` in that project yet, or you ran the script with a bare `python`. Run
  `poetry install`, then use `poetry run`.
- **`Address already in use` when you run `serve`.** An earlier API is still running on port 8000.
  Stop it (Ctrl+C in its terminal), or free the port, then start `serve` again.
- **A valid-looking POST returns `422`.** That is validation working at the edge: a field is out of
  range or the wrong type (for example `rating` 11). Fix the request body to match the contract shown
  at `/openapi.json`; the rejection is the Day 5 proof, not a setup problem.
- **The summary shows fewer rejected rows than you expect.** The sample deliberately contains two
  malformed rows. If they are not being rejected, the parser is coercing bad data instead of
  failing fast; that is behavior the lesson has you keep, not a setup problem.
- **The native benchmark shows no speedup.** The native path should call into `zlib`, not re-run the
  pure-Python loop. If both numbers are close, the fast path is not actually crossing to the native
  routine.
- **`poetry run` cannot find the command** (`reviews`, `telemetry`, `transactions`). Run
  `poetry install` in that project first; the command is defined under `[tool.poetry.scripts]`.

---

## 6. Readiness check

- [ ] `python3 -V` shows 3.11 or newer and `poetry --version` shows Poetry 2.x (from Day 1).
- [ ] In `demos/`, `poetry install` succeeds and `poetry run python demo_edge_validation.py`
  prints its expected output.
- [ ] The `reviews-insight` project runs `poetry run reviews summary` and shows `reviews : 5`,
  `products: 3`, `rejected: 2`, with a `[timed] summary:` line above it.
- [ ] `poetry run reviews serve` starts the API on `http://127.0.0.1:8000` and `/openapi.json` lists
  `/v1/reviews`.
- [ ] `poetry run python scripts/benchmark_native.py` shows the native `zlib` CRC far faster than the
  pure-Python one.
- [ ] `poetry run pytest -q` passes all nineteen tests, including the 8 API contract tests and 2 native
  tests.
- [ ] You confirmed the only new pieces for Day 5 are three Poetry packages (`fastapi`, `uvicorn`,
  `httpx`), with no separate software to install.

If every line checks out, you can run every Day 5 sample and follow every **Try it** in the lesson.
