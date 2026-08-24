# Assignment 01 · Make telemetry-insight interoperable

> Offline practice for Day 5. In class you gave a service two ways to talk to the world beyond
> Python: a versioned, validated HTTP API at its edge, and a native routine that reaches across
> the language boundary into compiled C. Now do the Day 5 layer on your `telemetry-insight`
> service: add an ingestion and query API and a native routine, mirroring the `reviews-insight`
> liveLab.

This is a do-it-yourself assignment. The point is to feel what "interoperable" buys you: once the
service speaks HTTP behind a validated contract, any other system can hand it data over the network,
and the boundary rejects bad input before your code ever runs. Once a hot routine can drop into C,
you have a way to move a tight loop out of the interpreter when it matters. The counting logic from
Day 3 does not change. What changes is how many other things can now talk to it.

Start from your `telemetry-insight` project, green, with the Day 3 maintainable layers in place.

## The goal

One thing, done honestly: put a versioned, validated HTTP surface in front of the service you
already have, and add a small native routine beside it. The API accepts readings, rejects bad ones
at the edge, and answers a query with the same three-number summary the CLI prints. The `telemetry
summary` command still prints exactly what it did before.

The behaviour of the summary is unchanged. The target output is still:

```text
readings: 5
devices : 3
rejected: 2
```

## What you have to build

1. **The web dependencies.** Add `fastapi`, `httpx`, and `uvicorn` to the project. FastAPI is the
   API framework, `httpx` is what the test client rides on, and `uvicorn` is the server that runs
   the app for the `serve` command.
2. **A native routine (`native.py`).** Reach across the language boundary two ways: a `ctypes` call
   into the C standard library's `strlen`, and a hot loop done twice, once in pure Python and once
   by the standard library's C implementation. This is the two-language boundary, in miniature.
3. **A validated, versioned API (`api.py`).** A `create_app()` factory that builds a FastAPI app
   with a `ReadingIn` pydantic model, a `/health` liveness route, a `POST /v1/readings` that
   ingests one reading, and a `GET /v1/insight` that returns the summary. The `/v1` prefix versions
   the contract; the pydantic model validates at the edge. On top of that basic surface, add the
   four pieces a real API needs:
   - **A response model on create.** Declare `response_model=ReadingAccepted` on `POST /v1/readings`
     so the response is validated on the way out too, and return `ReadingAccepted(status="accepted")`.
   - **A paginated list route.** `GET /v1/readings?limit=20&offset=0` returns one page of readings,
     not the whole store. Model the page with `ReadingOut(device_id, value)` and
     `ReadingPage(items, total, limit, offset)`, so the caller gets the total and can page through.
   - **A signed webhook.** `POST /v1/webhooks/reading` accepts a reading from a system you do not
     control. Verify an HMAC-SHA256 `x-signature` over the raw request body against a shared secret
     before storing anything, and refuse a bad signature with a 401.
   - **A trace-id middleware.** An HTTP middleware that reuses an incoming `x-trace-id` header or
     generates a new one, and echoes it on the response, so one request can be followed across
     services.
4. **A `serve` command in the CLI.** Add `serve` alongside `summary`, so the same CLI that prints
   the summary can also start the HTTP API. Keep the CLI thin: `serve` just launches the server.
5. **Contract tests.** Prove the API keeps its contract with a `TestClient`, one test per behaviour,
   eight in `tests/test_api.py`: health works, a valid reading POST returns 201, an out-of-range
   value returns 422, the insight route returns the counts, the OpenAPI document lists the versioned
   route, the list route pages, a valid webhook signature is accepted, a forged one is refused with
   401, and the trace id is generated and echoed. Add native tests that the compiled path agrees with
   the pure-Python one. This is the deliverable proof.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the web dependencies

Add `fastapi`, `httpx`, and `uvicorn` to your `pyproject.toml` and install them. Bump the project
version to `0.5.0` while you are there, so the package version tracks the day.

Hint: `poetry add fastapi httpx uvicorn` does the edit and the install in one step. FastAPI pulls
pydantic in as its own dependency, so you do not add it yourself. `httpx` is what the FastAPI
`TestClient` uses under the hood, which is why it belongs in the runtime dependencies and not only
in the test group.

### Level 2: the native boundary

Write `native.py`. Load the C standard library with `ctypes` (it lives in a different place per
platform), declare `strlen`'s argument and return types, and wrap it in `native_strlen(text)` that
encodes the string to bytes and returns the length. Then write two CRC32 routines over `bytes`: a
pure-Python `crc32_python` that runs the loop in the interpreter, and a `crc32_native` that calls
`zlib.crc32`, which is the same algorithm written in C.

Hint: the crossing is only safe once you declare the types. Set `strlen.argtypes` to
`[ctypes.c_char_p]` and `strlen.restype` to `ctypes.c_size_t`, so ctypes marshals the bytes in and
the integer out correctly. Marshaling is the reason `native_strlen` has to `text.encode("utf-8")`
first: a Python `str` cannot cross into C until it is bytes. For the two CRC32 routines, the whole
point is that they agree on every input, so the pure-Python one is worth writing exactly, bit for
bit, against the standard polynomial.

### Level 3: the validated, versioned API

Write `api.py`. Define a `ReadingIn` pydantic `BaseModel` with a `device_id` string constrained to
`min_length=1` and a `value` float constrained to the range `-50` to `150`. Write a `create_app()`
factory that builds a `FastAPI` app, keeps a small in-memory store, and registers three routes:
`GET /health`, `POST /v1/readings` (status code 201), and `GET /v1/insight`. The ingest route
appends the validated reading to the store; the insight route runs the store through your Day 3
`summarize_rows`.

Hint: put the store inside `create_app()` as a local list, so every app instance is independent and
each test starts clean. Type the ingest handler's parameter as `ReadingIn` and FastAPI does the
validation for you: by the time your handler runs, the reading is already valid, and anything out
of range was rejected with a 422 before your code was reached. Reuse `summarize_rows` from the
service so the API and the CLI count the same way. Expose a module-level `app = create_app()` too,
so a server can load it by import path.

Now add the four pieces a real API needs, all inside the same `create_app()` factory.

**Response model on create.** Add a `ReadingAccepted` model with a single `status: str` field, pass
`response_model=ReadingAccepted` to the `POST /v1/readings` decorator, and return
`ReadingAccepted(status="accepted")`. The request model validates input on the way in; the response
model validates and documents the output on the way out.

**A paginated list route.** Add a second `GET /v1/readings` route that takes `limit` (default 20) and
`offset` (default 0) query parameters and returns one page, never the whole store. Model it with a
`ReadingOut` (`device_id`, `value`) for a single row and a `ReadingPage` (`items`, `total`, `limit`,
`offset`) for the page, and slice the store with `store[offset : offset + limit]`. Report `total` as
the full store length so the caller knows how many pages remain.

**A signed webhook.** Add an async `POST /v1/webhooks/reading` route. A webhook comes from a system
you do not control, so do not trust it just because it arrived. Read the raw body with
`await request.body()`, compute an HMAC-SHA256 over that raw body with a shared secret, and compare it
to the `x-signature` header using `hmac.compare_digest`. On a mismatch, raise `HTTPException(status_code=401)`
before touching the payload; only on a match parse the JSON and append it to the store.

**A trace-id middleware.** Register an `@app.middleware("http")` handler that reads an incoming
`x-trace-id` header (or generates one with `uuid.uuid4().hex` when none is sent), calls the next
handler, and sets `x-trace-id` on the response before returning it. In real code you would log that id
too, so every line for one request shares a key as it crosses services.

Hint: sign the webhook over the *raw* bytes, not the parsed JSON, because re-serializing can change
the bytes and break the signature. Use `hmac.compare_digest` rather than `==` so the comparison does
not leak timing information. Keep the shared secret in a module-level constant for the assignment, but
note in a comment that real code reads it from configuration and never hard-codes it.

### Level 4: the serve command

Add a `serve` command to the CLI, next to `summary`. Give the parser a `--port` option with a
sensible default, and when the command is `serve`, start `uvicorn` on the app. Leave the `summary`
path exactly as it was.

Hint: import `uvicorn` inside the `serve` branch, not at the top of the file, so the summary path
stays light and does not pay for the web server it never uses. Point `uvicorn.run` at the app by its
import string, `"telemetry_insight.api:app"`, which is why `api.py` exposes a module-level `app`.

### Level 5: prove it with contract tests

Write `tests/test_api.py` using FastAPI's `TestClient`, eight tests in all, one per behaviour. Build
a fresh client per test so the in-memory store does not leak between tests. Assert that:

- `/health` returns `{"status": "ok"}`.
- posting a valid reading returns 201 and a following `/v1/insight` returns the right counts.
- a value of `999` is rejected with 422 and an empty `device_id` is rejected with 422.
- the generated `/openapi.json` lists the `/v1/readings` path.
- `GET /v1/readings` pages: post five readings, then request `limit=2&offset=2` and check `total` is
  5, `limit` and `offset` come back as sent, and `items` holds two rows, not five.
- a webhook with a correct `x-signature` returns 201 and the reading lands in the store.
- a webhook with a forged `x-signature` returns 401 and nothing is stored.
- the trace id is generated when none is sent and echoed back unchanged when one is.

Write `tests/test_native.py` asserting that `crc32_python`, `zlib.crc32`, and `crc32_native` all
agree, and that `native_strlen` counts the same bytes as `len` for ASCII text.

Hint: `TestClient(create_app())` gives you a client with its own fresh store, which is exactly why
the factory keeps the store inside. The 422 cases are the heart of the input proof: they show the
boundary rejecting bad input before any of your logic runs; the two webhook tests are the same proof
for a caller you do not control. Sign the webhook body in the test with the same secret and the same
HMAC the app uses, so a correct signature passes and a forged one fails. For the native tests, loop
over a few strings and assert the two CRC32 paths are equal on each, so a single disagreement anywhere
fails the test.

### Level 6: green gate and commit

Run pytest, ruff, and mypy strict, then commit the Day 5 interoperable layer on top of your
telemetry project. Expect 19 tests to pass (eight in `tests/test_api.py`, plus the native tests and
everything carried forward from earlier days). A single `StarletteDeprecationWarning` from the test
client is expected and harmless.

## Done when

- [ ] `fastapi`, `httpx`, and `uvicorn` are dependencies, and the project version is `0.5.0`.
- [ ] `native.py` calls C `strlen` across the `ctypes` boundary and offers a pure-Python and a
  native CRC32 that agree on every input.
- [ ] `api.py` has a `create_app()` factory with a `ReadingIn` model, a `/health` route, a
  `POST /v1/readings` returning 201, and a `GET /v1/insight` returning the counts.
- [ ] `POST /v1/readings` declares `response_model=ReadingAccepted` and returns
  `ReadingAccepted(status="accepted")`.
- [ ] `GET /v1/readings` is paginated with `ReadingOut` and `ReadingPage`, takes `limit` and `offset`,
  and reports the `total`.
- [ ] `POST /v1/webhooks/reading` verifies an HMAC-SHA256 `x-signature` over the raw body and refuses
  a forged signature with a 401.
- [ ] An `http` middleware reuses or generates an `x-trace-id` and echoes it on the response.
- [ ] A value of `999` is rejected with 422 and an empty `device_id` is rejected with 422, both at
  the edge, before the handler runs.
- [ ] The CLI has a `serve` command that starts the API, and `telemetry summary` still prints
  `readings: 5`, `devices : 3`, `rejected: 2`.
- [ ] Contract tests with a `TestClient` (eight in `tests/test_api.py`) prove health, ingest, the 422
  rejection, insight, the OpenAPI contract, pagination, the signed webhook (accepted and forged), and
  the trace id; the native tests prove the two CRC32 paths agree.
- [ ] `pytest` (19 passed), `ruff check`, and `mypy src` are all green, and the layer is committed.

When every box is ticked, you have shown the Day 5 point: a service becomes interoperable when it
speaks a versioned contract other systems can build against and validates input at its edge, and
when it can drop a hot routine into compiled code across a language boundary. The behaviour your CLI
prints did not change; the number of things that can now talk to your service did. The worked
solution is in `solution-01.md` if you want to compare, but try first.
