# Assignment 01 · Make telemetry-insight dependable under load

> Offline practice for the Dependable topic. In class you shaped `reviews-insight` scenario by
> scenario, running each reliability concern through the same loop: define the target, defend it by
> demonstration, and operate it with continuous monitoring. Now do that loop on your
> `telemetry-insight` service, with the emphasis the telemetry domain calls for: durability under
> load and throughput. High-volume numeric time-series is a never-ending stream, so the pressure is
> not a clever answer, it is holding up while readings pour in and a downstream system misbehaves.

This is a do-it-yourself assignment. The point is to feel what "dependable" buys you once the load
is real: a redelivered reading does not double-count, a burst past capacity is shed fast instead of
dragging every request down, a slow sink never fails ingest, and the process runs for a long stream
without leaking. The counting logic from earlier days does not change. What changes is that the
service now keeps its promise while things around it go wrong, and it emits the signals that prove
it.

Start from your `telemetry-insight` project, green, with the interoperable layer in place (the
versioned validated API, the native routine, and the contract tests).

## The goal

One thing, done honestly: put a durability-under-load dependability layer in front of the service
you already have. Ingest must survive a redelivered reading, a burst past capacity, and a slow or
dead downstream sink, and it must keep meeting its target while it does. The service exposes the
readiness and metrics signals that let you watch the target in production. The `telemetry summary`
command still prints exactly what it did before.

The behaviour of the summary is unchanged. The target output is still:

```text
readings: 5
devices : 3
rejected: 2
```

Run the whole assignment through the topic's loop. For each behaviour, hold all three moves in view:

- **Define.** State the target the behaviour meets, in the telemetry domain's terms: a duplicate has
  exactly one effect, a burst past the concurrency ceiling is shed with a fast 429, a sink slower
  than one second is buffered rather than allowed to fail ingest, memory stays flat over a long
  stream.
- **Defend.** Prove it with a test, a fault-injection run, or a soak, not a claim.
- **Operate.** Expose the signal that keeps proving it while the service runs: the readiness route,
  the structured log line carrying the trace id, and the SLI metrics.

## What you have to build

Bump the project version to `0.6.0` first, so the package version tracks the topic. Then build the
dependability layer as a set of small modules beside the API.

1. **A downstream sink with a timeout and graceful degradation (`sink.py`).** An async
   `forward_or_buffer(reading, client)` that forwards one reading to a configurable sink URL with a
   short timeout, and on any failure buffers it locally instead of raising. This is the throughput
   guard: a slow sink must slow nothing upstream.
2. **Structured logging and SLI metrics (`observability.py`).** A `log_event` that emits one JSON
   line per event carrying the trace id, and a small `Metrics` collector for the service level
   indicators. Both on the standard library, so nothing heavy is pulled in.
3. **The dependability layer on the API (`api.py`).** On top of the interoperable surface, add
   bounded-concurrency load shedding, idempotency on ingest, optional sink wiring, a readiness route,
   a metrics route, and per-request logging and metrics in the middleware.
4. **Dependability tests (`tests/test_dependability.py`).** One test per behaviour: idempotency
   stores once, load shedding returns 429 when full, the sink degrades on an injected timeout,
   `/ready` answers 200 with free capacity and 503 with none, and `/metrics` exposes the counts.
5. **A soak proof (`scripts/soak.py`).** Drive ingest for a long high-volume run and print memory at
   intervals, so a leak in the request path would show as a steady climb.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the downstream sink with a timeout and graceful degradation

Write `src/telemetry_insight/sink.py`. Read a `SINK_URL` from the environment (with a local default
for the assignment, noting that real code takes it from configuration). Fix a short timeout,
`1.0` second, generous for a same-datacenter hop and short enough to protect throughput. Write an
async `forward_or_buffer(reading, client)` that posts the reading to the sink within the timeout and
calls `raise_for_status()`. On success return the reading with `forwarded` set to `True`; on an
`httpx.TimeoutException` (the sink was too slow) or any other `httpx.HTTPError` (connection refused,
a 5xx, and so on) return `{**reading, "forwarded": False}` instead of raising.

Hint: the whole point of the timeout is that a slow sink cannot hold up ingest. Catch the timeout
and the general `httpx.HTTPError` together, because both mean the same thing to the caller: the
downstream is not usable right now, so buffer locally and let ingest keep meeting its target. The
caller treats a buffered reading (`forwarded: False`) as accepted, which is graceful degradation:
partly done beats not done.

### Level 2: structured logging and SLI metrics

Write `src/telemetry_insight/observability.py`, on the standard library alone (`logging`, `json`,
`dataclasses`). Give it three pieces:

- `configure_logging(level=logging.INFO)` that attaches a single stream handler once, guarded so a
  fresh app per test does not stack duplicate handlers. Format each record as the message itself,
  because you build the JSON yourself.
- `log_event(event, trace_id, duration_ms, status, **extra)` that emits one JSON line carrying
  `event`, `trace_id`, `duration_ms` (rounded), and `status`, plus any extra fields. Make it leveled:
  a server error (status 500 or above) logs at ERROR, everything else at INFO.
- A `Metrics` dataclass with `requests`, `errors`, and `duration_ms_sum`, a `record(duration_ms,
  status)` that counts one request and treats a 5xx as an error, and a `render()` that prints the
  counts and a duration summary as plain text.

Hint: one structured line per request, always carrying the trace id, is what lets you follow a
single request across services and machines when something goes wrong at load. The metrics are your
service level indicators: request count, error count, and a duration summary are enough to watch the
success-rate and latency targets without a metrics library. Count a shed request (429) and other 4xx
as not-an-error, because the client, not the service, caused them; only a 5xx burns the error budget.

### Level 3: the dependability layer on the API

Extend `create_app()` in `src/telemetry_insight/api.py`. Change its signature to
`create_app(max_concurrent=64, sink_client=None)`, set the FastAPI `version` to `0.6.0`, and add the
following, all inside the factory so each app instance stays independent.

**A bounded-concurrency gate for load shedding.** Write a small `Capacity` class holding a `limit`
and an `in_flight` count, with a non-blocking `try_acquire()` that takes a slot when one is free and
returns `False` when the gate is full, a `release()` paired with it in a `finally` block, and a
`free` property. Load shedding lives here: when the gate is full the caller sheds with a fast 429
instead of piling on more work.

**Idempotency on ingest.** Keep a `seen_keys` set beside the store. Let the ingest handler read a key
from the reading's optional `key` field or from an `Idempotency-Key` header. Extend `ReadingIn` with
an optional `key: str | None` (`min_length=1`). If the key has been seen, this is a redelivery:
return `ReadingAccepted(status="duplicate")` and store nothing. Only add the key to `seen_keys` after
you store the reading.

**The ingest handler, in order.** Make `POST /v1/readings` async. First try to acquire capacity, and
raise `HTTPException(status_code=429)` when it fails. Inside a `try` whose `finally` always releases
the slot: check idempotency and short-circuit a duplicate; if a `sink_client` was given, call
`forward_or_buffer` and log a `forward` event; then append to the store, record the key, and return
`ReadingAccepted(status="accepted")`.

**A readiness route.** Add `GET /ready` that reflects real free capacity: 200 with `{"status":
"ready"}` when a slot is free, 503 with `{"status": "unavailable"}` when the gate is full. Keep
`GET /health` as plain liveness, saying nothing about capacity.

**A metrics route.** Add `GET /metrics` returning the `Metrics.render()` output as plain text.

**Per-request observability in the middleware.** Reuse or generate the trace id, stash it on
`request.state` so handlers can log with the same id, time the request, echo `x-trace-id` on the
response, and call `metrics.record` and `log_event` once per request. Expose `capacity` and `metrics`
on `app.state` so tests and operators can inspect real capacity.

Hint: acquire the slot before any work and release it in a `finally`, whether you stored, deduped, or
raised, so the gate never leaks a slot. Readings can be negative and out of a small range: the value
constraint is the range `-50` to `150`, so hold that on `ReadingIn` exactly as the interoperable base
did. Keep the sink off by default (`sink_client=None`) so tests touch no network; wiring a real
client in is how you turn forwarding on.

### Level 4: prove it with dependability tests

Write `tests/test_dependability.py` with a `TestClient`, six tests, one per behaviour. Build a fresh
app per test so the in-memory store does not leak between them. Assert that:

- an ingest with the same `Idempotency-Key` twice stores the reading once: the first returns 201 and
  `accepted`, the second returns `duplicate`, and `/v1/insight` reports one reading.
- with `max_concurrent=2` and both slots filled by hand through `app.state.capacity`, a further
  ingest is shed with a 429, and after releasing the slots ingest returns 201 again.
- the sink degrades on an injected timeout: call `forward_or_buffer` directly with a mock client
  whose `post` always raises `httpx.TimeoutException`, and assert the outcome is buffered
  (`forwarded` is `False`) and never raised.
- `/ready` returns 200 and `ready` with free capacity.
- `/ready` returns 503 and `unavailable` when the only slot is filled (build with `max_concurrent=1`
  and acquire it).
- `/metrics` exposes the request count, the error count, and the duration summary.

Hint: test the async `forward_or_buffer` directly with `asyncio.run` and a small mock client, so you
need no `pytest-asyncio`. Drive the capacity gate through `app.state.capacity` to simulate work
already in flight, which is how you reach the shed path deterministically without real concurrency.
These six join everything carried forward from earlier days.

### Level 5: prove memory stays flat with a soak

Write `scripts/soak.py`. Drive ingest for a long high-volume run (8000 iterations) and print
`tracemalloc` memory every 2000 iterations. Send the same fixed idempotency key on every post, so
dedup holds the store at one row and any memory that moves is per-request overhead, not stored data.
At the end, confirm through `/v1/insight` that the store is still one row.

Hint: this is the MTBF proof for the telemetry domain, where the input is a never-ending stream. If
memory climbs steadily you have a leak in the request path; if it stays flat the service can run for
a long time without degrading. Fixing the idempotency key is the trick that separates the request
path from intentional growth: with the store pinned at one row by dedup, a rising memory line can
only be the request handling itself.

### Level 6: green gate

Run pytest, ruff, and mypy strict, then run the soak. Expect 25 tests to pass (six in
`tests/test_dependability.py`, plus the interoperable tests and everything carried forward from
earlier days). ruff clean, mypy strict clean.

```bash
poetry run pytest -q            # 25 passed
poetry run ruff check .         # All checks passed!
poetry run mypy src             # Success: no issues found
poetry run python scripts/soak.py
```

## Done when

- [ ] The project version is `0.6.0`, and the FastAPI app reports `version="0.6.0"`.
- [ ] `sink.py` has an async `forward_or_buffer(reading, client)` that forwards to a configurable
  `SINK_URL` with a 1.0 second timeout and, on `httpx.TimeoutException` or `httpx.HTTPError`, returns
  the reading with `forwarded` set to `False` instead of raising.
- [ ] `observability.py` has a `log_event` that emits one JSON line with `event`, `trace_id`,
  `duration_ms`, and `status`, leveled so a 5xx logs at ERROR, and a `Metrics` collector with a
  request count, an error count, and a duration summary.
- [ ] `api.py` has a `Capacity` gate, and `POST /v1/readings` sheds with a fast 429 when it is full.
- [ ] Ingest is idempotent: a key from the reading's `key` field or an `Idempotency-Key` header that
  has been seen returns status `duplicate` and stores nothing.
- [ ] `create_app` takes `max_concurrent` and `sink_client`; the sink is off by default, and when a
  client is given a slow or dead sink degrades to a buffered reading rather than failing ingest.
- [ ] `GET /ready` returns 200 with free capacity and 503 when the gate is full; `GET /health` stays
  plain liveness; `GET /metrics` returns the SLI counts as plain text.
- [ ] The middleware logs one structured line per request carrying the trace id and records one SLI
  sample, and readings may be negative and within the range `-50` to `150`.
- [ ] `tests/test_dependability.py` proves idempotency stores once, load shedding returns 429 when
  full, the sink degrades on an injected timeout, `/ready` answers 200 and 503, and `/metrics`
  exposes the counts, six tests in all.
- [ ] `scripts/soak.py` runs 8000 ingest iterations with a fixed idempotency key, prints memory every
  2000 iterations, holds memory flat, and leaves the store at one row through dedup.
- [ ] `pytest` (25 passed), `ruff check`, and `mypy src` are all green, and
  `telemetry summary` still prints `readings: 5`, `devices : 3`, `rejected: 2`.

When every box is ticked, you have run the topic's loop on the telemetry domain: for each behaviour a
target defined in the domain's terms, a demonstration that defends it under load, and a signal that
operates it in production. The behaviour your CLI prints did not change; the service now holds its
promise while readings pour in and a downstream system misbehaves, and it can prove it. The worked
solution is in `solution-01.md` if you want to compare, but try first.
