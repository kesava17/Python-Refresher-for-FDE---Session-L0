# Interoperable liveLab: run it, then understand it

This is the `reviews-insight` liveLab for the Interoperable topic. The idea of the day is that
almost no service stands alone: its value comes from how cleanly it connects to other systems, at two boundaries: the
network edge (a real HTTP API) and the code edge (calling a fast native routine in the same
process). Run the project first so you see it working, then read the second half to understand what
each change added and why it matters.

Code lives at
`shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/interoperable/liveLab`.
Open a terminal there.

---

## Part 1: Run the project

### Set it up (once)

This is a standard Poetry project. Install its dependencies once:

```bash
poetry install
```

### Run the checks

Prove the whole thing is green before touching it:

```bash
poetry run pytest -q          # 19 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
```

Eight of those tests are the API contract tests in `tests/test_api.py`, one per behaviour of the
edge.

### Run the batch summary

The command-line surface still does the batch job from the earlier days:

```bash
poetry run reviews summary
```

Expect:

```text
reviews : 5
products: 3
rejected: 2
```

### Run the API

Start the HTTP server (add `--port N` to change the port):

```bash
poetry run reviews serve
```

It listens on `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for the interactive,
auto-generated contract. The routes are:

```text
GET  /health                 liveness
POST /v1/reviews             create, validated in and out (201)
GET  /v1/reviews             paginated list (items + total + limit + offset)
GET  /v1/insight             summary
POST /v1/webhooks/rating     signed webhook, 401 on a bad signature
                             (every response also carries an x-trace-id header)
```

Exercise it from another terminal:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/v1/reviews -H "content-type: application/json" -d '{"product_id":"P1","rating":5}'
curl -s -X POST http://127.0.0.1:8000/v1/reviews -H "content-type: application/json" -d '{"product_id":"P1","rating":11}'   # 422, rejected at the edge
curl -s "http://127.0.0.1:8000/v1/reviews?limit=2&offset=0"    # one page plus the total
curl -si http://127.0.0.1:8000/health | grep -i x-trace-id     # trace id echoed on every response
```

Prefer clicking through requests? The folder `tests/http/` has ready-made request files
(`reviews.http`, `webhook.http`, `trace-id.http`) for the VS Code REST Client or a JetBrains IDE.
The webhook file carries a real signature pinned to its exact body.

---

## Part 2: What changed, and why it matters

You have now seen the service accept and reject requests, page a list, verify a webhook, and stamp a
trace id. Here is what was added to make that happen, grouped by the concept it teaches. Before this
topic, the API had only three plain routes (a health check, a create route that checked its input,
and a summary). Interoperability turned that into a production-shaped API and added a fast native
path underneath.

### The centerpiece: `src/reviews_insight/api.py` (the network boundary)

A FastAPI app built by `create_app()`. It adds four habits a real API needs. Each one is a small
change with an outsized effect on how safely other systems can depend on you.

**1. A response model, so the contract is checked on both sides.** The create route is declared with
`response_model=ReviewAccepted` and returns that model.

```python
@app.post("/v1/reviews", status_code=201, response_model=ReviewAccepted)
def submit(review: ReviewIn) -> ReviewAccepted:
    ...
    return ReviewAccepted(status="accepted")
```

Why it matters: input was already validated; now the reply is validated too. A caller can trust the
shape of what comes back, not just what it sends.

**2. Pagination, so a list never dumps everything.** `GET /v1/reviews` returns a `ReviewPage` with
the items plus the total, limit, and offset.

```python
@app.get("/v1/reviews", response_model=ReviewPage)
def list_reviews(limit: int = 20, offset: int = 0) -> ReviewPage:
    page = store[offset : offset + limit]
    return ReviewPage(items=..., total=len(store), limit=limit, offset=offset)
```

Why it matters: a real collection can be huge. Returning one page plus the total lets the caller walk
the rest, and keeps a single response small.

**3. A signed webhook, so an inbound call is trusted only when proven.** `POST /v1/webhooks/rating`
verifies an HMAC signature over the raw body before it acts.

```python
expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
if not hmac.compare_digest(signature, expected):
    raise HTTPException(status_code=401, detail="invalid signature")
```

Why it matters: a webhook comes from a system you do not control. Arriving is not the same as being
genuine. Only a sender who knows the shared secret can produce the right signature, so a forgery is
refused with a 401 before any payload is used.

**4. A trace id, so one request is findable across services.** A middleware reuses an incoming
`x-trace-id` or mints a new one, and echoes it on every response.

```python
@app.middleware("http")
async def add_trace_id(request, call_next):
    trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response
```

Why it matters: when A calls B calls C and something breaks, one correlation id ties all their log
lines together, so you can follow a single request through the whole system.

Still there from before, and still part of the story: input validation at the edge (a rating of 11 is
refused with 422 before the handler runs), the versioned `/v1` path, and the generated OpenAPI
document at `/openapi.json` that other teams build against.

### The other boundary: `src/reviews_insight/native.py` (the code boundary)

New file. Python calling compiled C in the same process, no network in between. It loads the C
library, declares the argument and return types, marshals a Python string to bytes, and calls
`strlen`. It also exposes a checksum in two forms, a pure-Python loop and `zlib.crc32` (C), so the
benchmark and tests can compare them.

Why it matters: this is the other kind of interoperability, the two-language pattern that most of the
fast Python world (NumPy and the data stack) is built on. When a loop is too slow in Python, you push
it into native code that runs at machine speed.

### The proof: the tests

- `tests/test_api.py` grew to **eight tests**: health, a valid create, bad input rejected at the
  edge, the OpenAPI contract exists, pagination returns one page plus the total, a valid webhook
  signature is accepted, a forged one is refused, and the trace id is generated and echoed.
- `tests/test_native.py` (new) checks the pure-Python and C checksums agree.
- `scripts/benchmark_native.py` (new) times one against the other, so the native win is measured, not
  claimed.

Why it matters: every capability the API added is pinned by a test, so a later change cannot quietly
break the contract.

### The wiring: `cli.py`, `pyproject.toml`, `__init__.py`

- `cli.py` gained a `serve` command (and `--port`) that starts the API. It imports `uvicorn` lazily,
  so the `summary` path stays light. The batch job behaves exactly as before.
- `pyproject.toml` moved to version `0.5.0` and added `fastapi`, `uvicorn`, and `httpx` (the API
  framework, the server that runs it, and the client the tests use). `__init__.py` tracks the same
  version.

Why it matters: one thin entry point now runs either the batch summary or the web server, with all
the real logic still living in the service and the API.

### The quiet files: `service.py`, `models.py`, `sources.py`, `decorators.py`

These changed only in their comments, not their behaviour. The reliability and structure they carry
were built on earlier days and are settled now, so their "new this day" notes step back to short
provenance labels. Nothing to relearn here; they are the stable base the API sits on.

---

## What to take away

Interoperability is a set of boundary decisions. At the network edge: validate both directions,
version the contract, page large lists, verify inbound calls, and stamp every request with an id you
can follow. At the code edge: cross into fast native code in a few large, safe steps. Run the project,
change one rule, and watch a test turn red: that is the contract doing its job. The same ideas scale
straight to production systems, which is exactly why they are worth appreciating here on a small one.
