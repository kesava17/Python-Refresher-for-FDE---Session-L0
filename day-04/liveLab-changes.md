# Day 5 liveLab: file-level changes

What changed in the `reviews-insight` liveLab going from Day 4 (Reliable) to Day 5
(Interoperable), file by file, with the reason for each change. Day 5's job is to make
the service talk to the world safely, at two boundaries: the network edge (a real HTTP
API) and the code edge (calling a native C routine in the same process).

Project path: `shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/interoperable/liveLab`

## At a glance

| File | Status | What changed | Why |
| --- | --- | --- | --- |
| `src/reviews_insight/api.py` | New | The whole HTTP API: validated request and response, a versioned path, pagination, a signed webhook, and a trace-id middleware. | This is the network boundary. It is the centerpiece of the day. |
| `src/reviews_insight/native.py` | New | A two-language boundary: Python calls C (`ctypes` for `strlen`, `zlib.crc32` for a fast checksum). | This is the code boundary, the second half of interoperability. |
| `tests/test_api.py` | New | Eight contract tests for the API. | Prove the contract at the edge, not just by hand. |
| `tests/test_native.py` | New | Tests for the native path (pure Python and C agree). | Prove the fast path returns the same answer. |
| `scripts/benchmark_native.py` | New | Times the pure-Python checksum against the C one. | Show the native win is real and measured. |
| `tests/http/*.http` + `README.md` | New | Hand-run request files for the API. | Explore the running service by clicking through requests. |
| `src/reviews_insight/cli.py` | Modified | Added a `serve` command (and `--port`) that starts the API; `summary` is unchanged. | One thin entry point now runs either the batch summary or the web server. |
| `pyproject.toml` | Modified | Bumped to `0.5.0`; added `fastapi`, `uvicorn`, `httpx`; new description. | The API and its test client need these dependencies. |
| `src/reviews_insight/__init__.py` | Modified | Version `0.4.0` to `0.5.0`. | Keep the package version in step with the day. |
| `service.py`, `models.py`, `sources.py`, `decorators.py`, `test_service.py` | Modified (text only) | Day-label comments trimmed; no behavior change. | Day 4's reliability features are no longer new on Day 5, so their "new this day" notes become short provenance labels. |

## New files, in detail

### `src/reviews_insight/api.py` (the network boundary)

A FastAPI application built by `create_app()`. It adds four standard habits a real API
needs, on top of the input validation and versioning the service already had.

1. **Response model.** `POST /v1/reviews` is declared with `response_model=ReviewAccepted`
   and returns a `ReviewAccepted`. Rationale: the API now checks what it sends back, not
   only what it receives, so the contract is complete on both sides.
2. **Pagination.** `GET /v1/reviews?limit=&offset=` returns a `ReviewPage(items, total,
   limit, offset)`. Rationale: a list route must never return the whole collection. It
   returns one page plus the total, so a caller can page through the rest.
3. **Signed webhook.** `POST /v1/webhooks/rating` reads the raw body, computes an
   HMAC-SHA256 over it with a shared secret, and compares it to the `x-signature` header
   using `hmac.compare_digest`. A mismatch is refused with 401 before the payload is used.
   Rationale: a request from a system we do not control cannot be trusted just because it
   arrived. We verify a signature first.
4. **Trace id.** An `@app.middleware("http")` reuses an incoming `x-trace-id` header or
   mints a new one, and echoes it on every response. Rationale: one correlation id ties a
   single request's logs together as it crosses services, so a failure is findable.

Carried forward and still part of the interoperability story: input validation at the
edge (a rating of 11 is refused with 422 before the handler runs), the versioned `/v1`
path, the generated OpenAPI document at `/openapi.json`, and the `/v1/insight` summary
that reuses the shared Day 3 logic.

The routes after Day 5:

```
GET  /health                 liveness
POST /v1/reviews             create, validated in and out (201)
GET  /v1/reviews             paginated list (items + total + limit + offset)
GET  /v1/insight             summary
POST /v1/webhooks/rating     signed webhook, 401 on a bad signature
                             (every response also carries an x-trace-id header)
```

### `src/reviews_insight/native.py` (the code boundary)

Python calling into compiled C in the same process, no network involved. It loads the C
library, declares the argument and return types, marshals a Python string to bytes, and
calls `strlen`. It also exposes a checksum in two forms, a pure-Python loop and
`zlib.crc32` (C), which the benchmark and tests use. Rationale: this is the other kind of
interoperability, the two-language pattern that most of the fast Python world is built on.

### `tests/test_api.py`

Eight tests (up from the four an earlier draft had): health, a valid create, bad input
rejected at the edge, the OpenAPI contract exists, pagination returns one page plus the
total, a valid webhook signature is accepted, a forged one is refused, and the trace id
is generated and echoed. Rationale: every capability the API added is proved by a test
that a change cannot silently break.

### `tests/http/` (hand-run requests)

`reviews.http`, `webhook.http`, `trace-id.http`, and a `README.md`. Rationale: a quick way
to exercise the running API by clicking through requests in VS Code (REST Client) or a
JetBrains IDE. The webhook file carries a real HMAC signature pinned to its exact body.
These complement the automated tests in `tests/test_api.py`; they do not replace them.

## Modified files, in detail

### `src/reviews_insight/cli.py`

Added a `serve` command and a `--port` option. `serve` imports `uvicorn` lazily (only the
serve path needs the web server, so the summary path stays light) and runs
`reviews_insight.api:app`. `summary` behaves exactly as before. Rationale: keep the CLI a
thin surface that can start either the batch job or the API, with all the real logic still
in the service and the API.

### `pyproject.toml` and `__init__.py`

Version moved from `0.4.0` to `0.5.0`, the description now names the Day 5 goal, and
`fastapi`, `uvicorn`, and `httpx` were added as dependencies (the API framework, the
server that runs it, and the client the tests use). Rationale: the new API surface needs
these, and the version tracks the day.

### The relabeled files

`service.py`, `models.py`, `sources.py`, `decorators.py`, and `test_service.py` changed
only in their comments and docstrings: Day 4's "new this day" notes became short labels
like "(from Day 4)". No logic changed. Rationale: those reliability features are settled
by Day 5, so the narrative labels step back rather than keep claiming to be new.

## How it is verified

- `poetry run pytest -q` reports **19 passed** (eight of them in `tests/test_api.py`).
- `poetry run ruff check .` and `poetry run mypy src` are both clean.
- `poetry run reviews summary` prints `reviews: 5 / products: 3 / rejected: 2`.
- `poetry run reviews serve` starts the API on `http://127.0.0.1:8000` (`/docs` for the
  interactive contract).
