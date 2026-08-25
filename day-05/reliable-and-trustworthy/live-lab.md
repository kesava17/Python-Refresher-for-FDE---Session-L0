# Dependable Live Lab: Make reviews-insight Reliable and Trustworthy

## What we're building

You already have the interoperable `reviews-insight` service: a versioned, validated HTTP surface with a
trace-id middleware, `/health`, `POST` and `GET /v1/reviews`, `GET /v1/insight`, and a signed webhook. It
speaks a clean contract to the outside world, but it makes no promise about staying up. Nothing stops a
slow enrichment dependency from hanging a request, a client retry from storing the same review twice, a
long run from leaking memory, or a bad deploy from taking the fleet down with no way back.

In this lab you make the service **dependable**: it holds up on real input, you can prove it holds up, and
you keep proving it while it runs. You add a thin operational layer on top of the interoperable version and
walk it through four concrete scenarios, each run through the same loop the chapter builds toward:

1. **Define** the target: state the number and the rule up front.
2. **Defend** it by demonstration: a test, a fault-injection run, or a soak that shows the target is met.
3. **Operate** it with continuous monitoring: the signals (`/ready`, `/metrics`, structured logs) that keep
   the target honest in production.

The four scenarios are:

- **Scenario A**, a slow or dead enrichment dependency (availability, graceful degradation).
- **Scenario B**, the same review submitted twice (durability, exactly-once).
- **Scenario C**, the service running for weeks (MTBF, no leak).
- **Scenario D**, a bad change deployed (MTTR, change failure rate).

Work in order. Copy, paste, run. After each step there is one line on what happened and why it matters.
Start from your interoperable `reviews-insight` project folder, with everything green.

Ground rules, same as before: everything Python runs through `poetry run`; run commands from inside the
project folder.

---

## Step 0: Set up and confirm the gate is green

Install the dependencies, then run the three checks. This is the baseline every scenario builds on: if the
suite is green, ruff is clean, and mypy is strict-clean before you start, then any red later is something
you did, not something you inherited.

```bash
poetry install
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

You should see:

```text
26 passed
All checks passed!
Success: no issues found in 6 source files
```

**What happened.** The service is at version `0.6.0` and carries **26 passing tests**: the interoperable
contract tests plus the new dependability tests in `tests/test_dependability.py` (graceful degradation,
idempotency, readiness, and the SLI metrics endpoint). ruff and mypy strict both pass. That is the "green
before you start" line the whole lab depends on.

Confirm the batch path still prints the same counts it always has:

```bash
poetry run reviews summary
```

```text
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
rejected: 2
```

The `summarize` method still carries the `@timed("summary")` decorator, so the timing line prints first,
then the environment header and the three counts (`reviews: 5 / products: 3 / rejected: 2`). Nothing about
the batch path changed; the dependable layer sits on the HTTP surface.

---

## Step 1: Meet the dependable layer

Before the scenarios, look at the three files that make the service operable. Read them, do not retype
them; they are already built and tested.

`src/reviews_insight/enrichment.py` is the availability layer. It calls an external enrichment service to
add an insight to each review, but it bounds the call and degrades instead of failing:

```python
async def enrich_or_degrade(
    review: dict[str, str],
    client: httpx.AsyncClient,
    url: str,
    timeout: float = ENRICH_TIMEOUT_SECONDS,
) -> dict[str, object]:
    try:
        response = await client.post(url, json=review, timeout=timeout)
        response.raise_for_status()
        body = response.json()
        insight = body.get("insight") if isinstance(body, dict) else None
        return {**review, "insight": insight, "enriched": True}
    except (httpx.TimeoutException, httpx.HTTPError):
        return {**review, "insight": None, "enriched": False}
```

`ENRICH_TIMEOUT_SECONDS` is `1.0`. On a timeout or any HTTP or transport error the review comes back with
`"insight": None` and `"enriched": False`, so a slow or broken dependency degrades the result rather than
failing the whole request. The client is passed in, so a test can inject a failing one.

`src/reviews_insight/observability.py` is the operate layer, all standard library:

- `get_logger()` returns a logger that writes one JSON object per line to stdout.
- `log_request(...)` writes one structured line per request carrying the `trace_id`, `duration_ms`, and
  `status`.
- `Metrics` holds three counters (requests, errors, total duration) and renders them as plain text.
- `Capacity` is a gauge of in-flight requests, so readiness can reflect real capacity.

`src/reviews_insight/api.py` wires it together. `create_app` now accepts an injected `enrichment_client`
and `enrichment_url`, builds a `Metrics`, a `Capacity(limit=100)`, and a logger, and replaces the old
trace-id middleware with a single `observe` middleware:

```python
@app.middleware("http")
async def observe(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
    capacity.acquire()
    start = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        capacity.release()  # released even if the handler raised, so capacity does not leak
    duration_ms = (time.perf_counter() - start) * 1000.0
    metrics.observe(status=response.status_code, duration_ms=duration_ms)
    log_request(logger, event=request.url.path, trace_id=trace_id,
                duration_ms=duration_ms, status=response.status_code)
    response.headers["x-trace-id"] = trace_id
    return response
```

One middleware now handles the cross-cutting concerns: reuse or start a trace id, count the request as
in-flight for readiness, time it, record its SLIs, log one structured line, and echo the trace id back.
`capacity.release()` sits in a `finally`, so a raising handler still frees the slot.

`config.py` sets the enrichment target's default to `http://enrichment.invalid/enrich`. The `.invalid`
TLD is reserved and never resolves, so with no enrichment server configured the call fails fast and the
submit path degrades. That is what makes Scenario A visible on a laptop with nothing else running.

**What happened.** The service gained an availability layer (timeout plus graceful degradation), an
idempotency ledger on submit, a real readiness endpoint, and an observability layer (structured logs, SLI
metrics, a capacity gauge). Each scenario below drives one of these.

---

## Scenario A: the enrichment dependency is slow or down

**Availability, graceful degradation.**

### Define

The core path must stay available even when enrichment is slow or dead. The rule: if the enrichment call
does not answer within its one-second timeout, or fails, serve the review anyway and mark it
`enriched: false`. A submit is never failed by a bad dependency.

### Defend by demonstration

The default enrichment URL, `http://enrichment.invalid/enrich`, never resolves, so a local submit exercises
the degraded path directly. Start the server:

```bash
poetry run reviews serve
```

```text
serving reviews-insight on http://127.0.0.1:8000 (press Ctrl+C to stop)
```

In another terminal, submit a review:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "P1", "rating": 5}'
```

```json
{"status":"accepted","enriched":false}
```

The submit returned `201` with `enriched: false`: the enrichment host did not resolve, the call failed
inside its budget, and the service degraded instead of hanging or erroring. The review was still stored.
Confirm it counts:

```bash
curl -s http://127.0.0.1:8000/v1/insight
```

```json
{"reviews":1,"products":1,"rejected":0}
```

The proof that this is deliberate, not luck, is the fault-injection test. `tests/test_dependability.py`
injects a client whose `post` always raises `httpx.TimeoutException`:

```python
def test_fault_injection_degrades_but_still_accepts() -> None:
    client = TestClient(create_app(enrichment_client=_TimeoutClient()))
    resp = client.post("/v1/reviews", json={"product_id": "P1", "rating": 5})
    assert resp.status_code == 201
    assert resp.json() == {"status": "accepted", "enriched": False}
    assert client.get("/v1/insight").json()["reviews"] == 1
```

Run just the degradation tests:

```bash
poetry run pytest -q -k "degrade or fault"
```

```text
3 passed
```

`test_fault_injection_degrades_but_still_accepts` proves the HTTP path degrades and still stores the review;
`test_enrich_or_degrade_on_timeout_returns_degraded` and `test_enrich_or_degrade_on_success_returns_enriched`
pin the enrichment function itself on both branches, driven with `asyncio.run` so no `pytest-asyncio` is
needed.

### Operate with continuous monitoring

The `observe` middleware records every request's status and duration into `Metrics`, and `GET /metrics`
renders them as plain text. With the server still running:

```bash
curl -s http://127.0.0.1:8000/metrics
```

```text
requests_total 3
errors_total 0
request_duration_ms_sum 12.34
request_duration_ms_avg 4.11
```

`requests_total` is the request-rate SLI, `errors_total` counts `5xx` responses, and the duration lines are
the latency SLI. In production these feed a dashboard and an error-budget burn-rate alert, so a real
enrichment slowdown pages someone in about a minute instead of going unseen. Note that a degraded submit is
a `201`, not a `5xx`, so it does not burn the error budget: degradation is the service working as designed.

---

## Scenario B: the same review is submitted twice

**Durability, exactly-once.**

### Define

Submitting a review with the same `Idempotency-Key` twice must have exactly one effect: one stored review,
the same result returned both times. RPO for accepted reviews is zero.

### Defend by demonstration

`POST /v1/reviews` reads an `Idempotency-Key` header. The first time a key is seen the review is stored and
the result is remembered; a repeat of that key returns the stored result without storing again. With the
server running, submit the same key twice:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -H "Idempotency-Key: retry-key-1" \
  -d '{"product_id": "P9", "rating": 4}'

curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -H "Idempotency-Key: retry-key-1" \
  -d '{"product_id": "P9", "rating": 4}'
```

```json
{"status":"accepted","enriched":false}
{"status":"accepted","enriched":false}
```

Both calls return the same result, but only one review was stored. Check the count moved by one, not two
(the number here reflects whatever you submitted earlier in the session):

```bash
curl -s http://127.0.0.1:8000/v1/insight
```

The test that pins this down is `test_idempotent_submit_stores_once`:

```python
def test_idempotent_submit_stores_once() -> None:
    client = TestClient(create_app(enrichment_client=_OkClient()))
    headers = {"Idempotency-Key": "retry-key-1"}
    first = client.post("/v1/reviews", json={"product_id": "P1", "rating": 5}, headers=headers)
    second = client.post("/v1/reviews", json={"product_id": "P1", "rating": 5}, headers=headers)
    assert first.status_code == 201
    assert second.json() == first.json()
    assert client.get("/v1/insight").json()["reviews"] == 1
```

Its partner, `test_distinct_keys_store_separately`, submits two different keys and asserts both are stored,
so the idempotency check cannot swallow genuinely new submissions. Run both:

```bash
poetry run pytest -q -k "idempotent or distinct_keys"
```

```text
2 passed
```

### Operate with continuous monitoring

The signal here is the duplicate-key rate. In production the idempotency ledger's hit count is exported as a
metric: a rising duplicate rate is an early sign that a client or the network is retrying more than
expected, visible on the dashboard before it becomes a support ticket. Every submit still flows through the
`observe` middleware, so its duration and status land in `/metrics` and its structured log line carries the
`trace_id`, which is how you tie a suspected duplicate back to the exact request that caused it.

---

## Scenario C: the service runs for weeks

**MTBF, no leak.**

### Define

Memory and latency stay flat over a long run. No cache or structure grows without bound, so the process
does not slowly rot and fall over. This is what turns a service that survives a demo into one that survives
weeks.

### Defend by demonstration

`scripts/soak.py` drives the core `summarize_rows` loop for 2000 iterations over a fixed 10,000-row batch,
sampling traced memory with `tracemalloc` at intervals. If nothing is retained between runs the number
stays flat.

```bash
poetry run python scripts/soak.py
```

```text
after run     1: current memory   1.53 MB
after run   500: current memory   1.53 MB
after run  1000: current memory   1.53 MB
after run  1500: current memory   1.53 MB
after run  2000: current memory   1.53 MB
current memory stays flat across runs: no state is retained, so no leak.
```

The current traced memory does not climb across the 2000 runs. Each iteration builds its counts and
discards them, retaining no growing state, so the summarize loop does not leak. That flat line is the
evidence behind the MTBF claim: the difference between a service that runs for months and one that dies in
days is exactly this.

### Operate with continuous monitoring

In production the same idea becomes a live signal: export process memory and the duration SLI (already
recorded by the `observe` middleware into `Metrics`) and alert on a slow upward trend. A leak that would
exhaust the process in a week shows as drift days ahead, so it is caught during business hours rather than
at 3 a.m. The soak run is the pre-ship proof; the memory-trend alert is the same proof kept running.

---

## Scenario D: a bad change is deployed

**MTTR, change failure rate.**

### Define

Deploys go out gated on the readiness endpoint, with an automatic rollback. Target MTTR for a bad deploy is
under a minute, with no human in the loop. Most outages come from change, so the deploy path itself is a
reliability concern.

### Defend by demonstration

There is no real cloud deploy in this lab, so the demonstration is the mechanism a rollout gate reads:
`/health` versus `/ready`. `/health` is plain liveness (is the process up at all), while `/ready` reflects
real capacity, backed by the `Capacity(limit=100)` gauge that the `observe` middleware increments per
in-flight request. A rollout gate routes traffic only to instances that pass readiness, so a new revision
that cannot serve is never given traffic and the previous version stays live.

With the server running, look at both:

```bash
curl -s -i http://127.0.0.1:8000/health | head -n 1
curl -s -i http://127.0.0.1:8000/ready  | head -n 1
```

```text
HTTP/1.1 200 OK
HTTP/1.1 200 OK
```

Both return `200` here because the instance is healthy and has free capacity. The point is that they answer
different questions. `/ready` returns `503` when in-flight work reaches the capacity limit, so an
orchestrator stops routing to a saturated or wedged instance instead of piling on. The readiness logic is:

```python
@app.get("/ready")
def ready(response: Response) -> dict[str, str]:
    if capacity.has_free():
        return {"status": "ready"}
    response.status_code = 503
    return {"status": "at capacity"}
```

`test_ready_returns_200_normally` confirms `/ready` reports `200` with capacity free and that `/health`
stays a separate check. Conceptually, a progressive rollout (canary or blue-green) points its post-deploy
health check at `/ready`; a revision that fails it is rolled back automatically, keeping MTTR to seconds
with no human paging in.

### Operate with continuous monitoring

The operate signals for a deploy are a post-deploy synthetic smoke test hitting `/health`, `/ready`, and a
sample submit, plus the SLI counters at `/metrics` watched for a jump in `errors_total` right after a
rollout:

```bash
curl -s http://127.0.0.1:8000/metrics
```

```text
requests_total 8
errors_total 0
request_duration_ms_sum 41.90
request_duration_ms_avg 5.24
```

A rising `errors_total` immediately after a deploy is the burn signal that triggers rollback. Every real
incident then becomes a new regression test, closing the loop back to Defend so the same failure cannot
return unseen. Notice that observability and deployment are not extra topics here; they are the Operate step
of the loop.

---

## Serve it: the full route list

`reviews serve` starts the versioned API through uvicorn on a real port, so another process can reach every
route this lab added:

```bash
poetry run reviews serve
```

```text
serving reviews-insight on http://127.0.0.1:8000 (press Ctrl+C to stop)
```

Live routes:

- `GET /health`, liveness.
- `GET /ready`, readiness (`503` when at capacity, `200` otherwise).
- `GET /metrics`, the SLI counters as plain text.
- `POST /v1/reviews`, submit (enriches or degrades, honors `Idempotency-Key`).
- `GET /v1/reviews`, one paginated page plus the total.
- `GET /v1/insight`, the running summary.
- `POST /v1/webhooks/rating`, the signed webhook.
- `/openapi.json` and `/docs`, the generated contract and interactive docs.

Every response carries an `x-trace-id` header, whether you sent one in or the server generated it, and every
request writes one structured JSON log line carrying that same trace id. Read the counters any time:

```bash
curl -s http://127.0.0.1:8000/metrics
```

```text
requests_total 12
errors_total 0
request_duration_ms_sum 63.71
request_duration_ms_avg 5.31
```

Press Ctrl+C to stop the server.

---

## You should see

Run through this recap. If each line matches, the dependable lab is done.

- `poetry run pytest -q` reports **26 passed**: the interoperable contract tests plus the dependability
  tests in `tests/test_dependability.py`.
- `poetry run ruff check .` and `poetry run mypy src` are both clean, and the project is at version
  `0.6.0`.
- `poetry run reviews summary` still prints the timing line and the counts, `reviews: 5 / products: 3 /
  rejected: 2`, with no crash.
- **Scenario A:** a submit against the default (non-resolving) enrichment URL returns `201` with
  `enriched: false`, the review is still stored and counted, and the fault-injection test proves it is
  deliberate.
- **Scenario B:** two submits with the same `Idempotency-Key` store exactly one review and return the same
  result, while two different keys store two.
- **Scenario C:** `poetry run python scripts/soak.py` runs the core loop 2000 times and prints flat memory,
  so the loop retains no growing state.
- **Scenario D:** `/health` and `/ready` answer different questions; readiness is backed by a real capacity
  gauge and gates a rollout, which is what keeps MTTR to seconds.
- `poetry run reviews serve` exposes `/health`, `/ready`, `/metrics`, the `/v1` routes, the signed webhook,
  and `/openapi.json`, every response carrying an `x-trace-id`, and `GET /metrics` renders the SLI counters
  as plain text.

That is the dependable layer: the same small service now carries a defined target, a demonstration that
defends it, and a monitor that operates it, for each of the four scenarios. Availability holds against a
dead dependency because the call is bounded and degrades; a retried submit has exactly one effect because
the key is remembered; the long run stays flat because nothing is retained; and a bad change is caught at
the readiness gate before it reaches everyone. Reliability is the promise in numbers, trustworthiness is the
define, defend, operate loop around each number, and this lab is that loop applied to a running service.
