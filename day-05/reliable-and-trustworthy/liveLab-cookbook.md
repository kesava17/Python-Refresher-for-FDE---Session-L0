# Dependable liveLab: run it, then understand it

This is the `reviews-insight` liveLab for the Reliable and Trustworthy topic. The idea of the day is
that a service is judged not by whether it works once, but by whether it keeps working: it stays up
when a dependency it calls is slow or down, it does not lose or duplicate accepted data, and it keeps
emitting the signals that prove all of this while it runs. Run the project first so you see it holding
up, then read the second half to understand what each change added and why it matters.

The topic frames every reliability concern as one loop: **define** the target, **defend** it by
demonstration, and **operate** it with continuous monitoring. Keep that loop in mind; the code you run
below is that loop made concrete.

Code lives at
`shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/reliable-and-trustworthy/liveLab`.
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
poetry run pytest -q          # 26 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
```

Seven of those tests are the dependability tests in `tests/test_dependability.py`, one per
operational habit this topic adds: graceful degradation, the async enrich-or-degrade function on both
timeout and success, idempotent submit, distinct keys stored separately, readiness, and the metrics
endpoint.

### Run the batch summary

The command-line surface still does the batch job from the earlier days:

```bash
poetry run reviews summary
```

Expect (the first line names the environment and app; the counts are what matter):

```text
[dev] reviews-insight
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
GET  /health                 liveness: is the process up at all?
GET  /ready                  readiness: is there free capacity right now? (503 when full)
GET  /metrics                the SLIs as plain text (request rate, error rate, duration)
POST /v1/reviews             create, with an optional Idempotency-Key header (201)
GET  /v1/reviews             paginated list (items + total + limit + offset)
GET  /v1/insight             summary
POST /v1/webhooks/rating     signed webhook, 401 on a bad signature
                             (every response also carries an x-trace-id header)
```

### See graceful degradation for yourself

Submit a review from another terminal:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" \
  -d '{"product_id":"P1","rating":5}'
```

Expect:

```json
{"status":"accepted","enriched":false}
```

Note `enriched: false`. The service tries to call an enrichment dependency for every review, but the
default target is `http://enrichment.invalid/enrich`. The `.invalid` top-level domain is reserved and
never resolves (RFC 2606), so with no real enrichment server configured the call fails fast and the
submit path degrades gracefully instead of hanging. The review is still accepted and stored; it is
simply marked as not enriched. Point `ENRICHMENT_URL` at a real service and the same submit comes back
with `enriched: true`.

### Retry the same submit safely

Send the same request twice with the same idempotency key:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" -H "Idempotency-Key: demo-1" \
  -d '{"product_id":"P1","rating":5}'
curl -s -X POST http://127.0.0.1:8000/v1/reviews \
  -H "content-type: application/json" -H "Idempotency-Key: demo-1" \
  -d '{"product_id":"P1","rating":5}'
curl -s http://127.0.0.1:8000/v1/insight
```

Both submits return the same result, and `insight` counts the review once, not twice. A retry has
exactly one effect.

### Read the signals

The metrics endpoint reports the golden signals as plain text:

```bash
curl -s http://127.0.0.1:8000/metrics
```

Expect something like:

```text
requests_total 4
errors_total 0
request_duration_ms_sum 12.34
request_duration_ms_avg 3.09
```

Every request also logs one structured JSON line to the server's stdout, carrying the same
`x-trace-id` the response header echoes, so a log line and a client-visible request can be matched up.

### Run the soak

A dependable service must survive a long run, not just one request. The soak script drives the core
summarize loop for 2000 iterations and prints the traced memory at intervals:

```bash
poetry run python scripts/soak.py
```

Expect the memory number to stay flat from the first report to the last:

```text
after run     1: current memory   ...  MB
after run   500: current memory   ...  MB
after run  1000: current memory   ...  MB
after run  1500: current memory   ...  MB
after run  2000: current memory   ...  MB
current memory stays flat across runs: no state is retained, so no leak.
```

Flat memory across 2000 runs means the loop keeps nothing between iterations, which is what lets the
process run for weeks without slowly rotting.

---

## Part 2: What changed, and why it matters

You have now seen the service accept a review while its enrichment dependency is unreachable, swallow
a duplicate retry, report its own signals, and hold memory flat over a long run. Here is what was
added to make that happen, grouped by the concept it teaches. Before this topic, the API was already
interoperable: a versioned, validated HTTP surface with a trace id, pagination, and a signed webhook.
This topic makes it *dependable*, and it does so by running each concern through the topic's loop:
define the target, defend it with a test, and operate it with a live signal.

### The centerpiece: `src/reviews_insight/api.py` (the service made dependable)

The API is still built by `create_app()`, and it now carries the operational habits that keep a
service up under real conditions. The version moved to `0.6.0` (matching `pyproject.toml`).

**1. Enrichment with a timeout and graceful degradation (availability).** Every submit calls an
external enrichment service, but the call is bounded and the failure is handled. The logic lives in
`src/reviews_insight/enrichment.py`:

```python
ENRICH_TIMEOUT_SECONDS = 1.0

async def enrich_or_degrade(review, client, url, timeout=ENRICH_TIMEOUT_SECONDS):
    try:
        response = await client.post(url, json=review, timeout=timeout)
        response.raise_for_status()
        body = response.json()
        insight = body.get("insight") if isinstance(body, dict) else None
        return {**review, "insight": insight, "enriched": True}
    except (httpx.TimeoutException, httpx.HTTPError):
        return {**review, "insight": None, "enriched": False}
```

The one-second timeout caps the worst case, and the `except` turns a slow or broken dependency into a
degraded result rather than a failed request. In `api.py`, the submit route awaits this and stores the
review either way, recording the `enriched` flag so a downstream reader knows whether a record carries
an insight.

Why it matters: availability is lost most often not when a dependency crashes, but when it gets slow
and the code waits forever. A bounded call plus a fallback means one sick dependency cannot take the
whole submit path down with it. That is the **define, defend, operate** loop for availability: the
target is "serve the review even when enrichment is down," the test `test_fault_injection_degrades_but_still_accepts`
injects a client that always times out and asserts a 201 with `enriched: false`, and the enrichment
error rate is something you would put on a dashboard in production.

**2. Idempotency on submit (durability, exactly-once effect).** The submit route accepts an optional
`Idempotency-Key` header and keeps a small ledger of results it has already produced:

```python
if idempotency_key is not None and idempotency_key in idempotent_results:
    return idempotent_results[idempotency_key]
# ... enrich and store the review ...
result = ReviewAccepted(status="accepted", enriched=bool(enriched["enriched"]))
if idempotency_key is not None:
    idempotent_results[idempotency_key] = result
return result
```

Why it matters: networks lose responses, so clients retry. A retry without idempotency applies the
effect twice, which on a payment path is a double charge. Storing the result against the key means a
second submit with the same key returns the first result and stores nothing new, so a retry has
exactly one effect. The test `test_idempotent_submit_stores_once` submits the same key twice and
asserts one stored review; `test_distinct_keys_store_separately` proves a genuinely new key is not
swallowed.

**3. A readiness endpoint separate from liveness (availability, honest capacity).** There are now two
health routes, and they answer different questions:

```python
@app.get("/health")
def health():
    return {"status": "ok"}          # liveness: is the process up at all?

@app.get("/ready")
def ready(response):                 # readiness: should it get traffic right now?
    if capacity.has_free():
        return {"status": "ready"}
    response.status_code = 503
    return {"status": "at capacity"}
```

The `Capacity` gauge in `observability.py` counts in-flight requests; the observe middleware calls
`capacity.acquire()` when a request starts and `capacity.release()` in a `finally` block, so capacity
is returned even if the handler raises. Readiness returns 503 once in-flight work reaches the limit.

Why it matters: a load balancer needs to route work away from a saturated or stuck instance, not pile
more on. A liveness check that only proves the process is alive will call a hung service healthy.
Readiness tells the truth about capacity, so an orchestrator can stop sending traffic to an instance
that has no room. The test `test_ready_returns_200_normally` pins the healthy case.

**4. Structured logging with a trace id, and SLI metrics (observability, operate).** A single
middleware named `observe` handles the cross-cutting work for every request: reuse or mint a trace id,
count the request as in-flight, time it, record its SLIs, and write one structured log line.

```python
metrics.observe(status=response.status_code, duration_ms=duration_ms)
log_request(logger, event=request.url.path, trace_id=trace_id,
            duration_ms=duration_ms, status=response.status_code)
response.headers["x-trace-id"] = trace_id
```

`observability.py` keeps this dependency-free. `get_logger` writes one JSON object per line to stdout;
`log_request` carries the trace id, so a log line matches the id the client saw in the response
header. `Metrics` holds three counters, request count, error count (a 5xx), and duration total, and
renders them at `GET /metrics` as `requests_total`, `errors_total`, `request_duration_ms_sum`, and
`request_duration_ms_avg`. These are the golden signals: rate, errors, and duration.

Why it matters: this is the **operate** step. A defined-and-defended target only stays met if you can
watch it in production. Structured logs let a machine query them, the trace id ties one request across
every service it touches, and the SLIs are the numbers a dashboard and a burn-rate alert read. The
test `test_metrics_exposes_counters` asserts the counters are exposed.

### The proof under long running: `scripts/soak.py` (MTBF, no leak)

The soak script drives `summarize_rows` over a fixed batch of 10,000 rows for `ITERATIONS = 2000`,
printing traced memory at run 1 and every 500 runs, then stopping. Nothing is kept between runs, so
the printed memory stays flat.

Why it matters: a memory leak shows up only under sustained load, never in a single request. A flat
soak profile is the evidence that defends the MTBF target: the loop retains no growing state, so the
process can run for a long time without exhausting memory and falling over.

### The configuration behind graceful degradation: `src/reviews_insight/config.py`

`Config.from_env()` reads `ENRICHMENT_URL` from the environment and defaults it to
`http://enrichment.invalid/enrich`. The reserved `.invalid` domain never resolves, so out of the box
the enrichment call fails fast and the submit path degrades. This is a deliberate teaching default: it
lets you see graceful degradation on a fresh checkout with no enrichment server to run. In production
you set `ENRICHMENT_URL` to a real service.

### The proof, pinned: `tests/test_dependability.py`

Seven tests, one per habit, so a later change cannot quietly break the promise:

- `test_fault_injection_degrades_but_still_accepts` injects a timing-out client and asserts a 201 with
  `enriched: false`, and that the review is still counted.
- `test_enrich_or_degrade_on_timeout_returns_degraded` and `test_enrich_or_degrade_on_success_returns_enriched`
  test the async function directly with `asyncio.run` and small fake clients, so no `pytest-asyncio`
  is needed.
- `test_idempotent_submit_stores_once` and `test_distinct_keys_store_separately` prove the exactly-once
  effect and that distinct keys are not swallowed.
- `test_ready_returns_200_normally` pins readiness, and `test_metrics_exposes_counters` pins the SLI
  endpoint.

These seven join the 8 API tests, plus the native, service, summary, and model tests, for 26 in total.

Why it matters: every dependability habit the service added is defended by a test. That is the
**defend** step of the loop, and it is what turns "it ran in the demo" into "it holds up, and we can
prove it."

### The wiring: `pyproject.toml`

The project moved to version `0.6.0` and its dependencies now include `httpx` (the async client used
to call enrichment) alongside `fastapi` and `uvicorn`. The description spells out the new habits:
timeouts, graceful degradation, idempotency, readiness, structured logging, and SLI metrics. Nothing
in the batch `summary` path changed; the earlier logic is the stable base the dependable API sits on.

---

## What to take away

Dependability is a promise kept while the service runs, and it is made concrete by wrapping one loop
around every reliability concern: define the target, defend it with a demonstration, and operate it
with a live signal. In this liveLab you can point to each turn of that loop. Availability: a one-second
timeout and a fallback, defended by a fault-injection test, operated by an error-rate metric.
Durability: an idempotency key, defended by a retry test, operated by a duplicate-hit count you could
graph. Honest capacity: a readiness endpoint separate from liveness. Observability: structured logs
carrying a trace id and the golden-signal SLIs at `/metrics`. MTBF: a soak run held flat over 2000
iterations. Run the project, break one rule (drop the timeout, remove the idempotency check, let the
cache grow), and watch a test turn red or the soak climb. That is the contract doing its job, and it
is exactly what makes a real service dependable.
