# Solution 01 · Make telemetry-insight dependable under load

> The full worked solution for Assignment 01. Try the assignment yourself first. This is here to
> check your work, or to unstick you when you're truly stuck.

You start from your `telemetry-insight` project, green, with the interoperable layer in place. This
solution adds the dependability layer, tuned for the telemetry domain where the pressure is durability
under load and throughput: a downstream sink with a timeout and graceful degradation, structured
logging with an SLI collector, and an API that sheds load, dedupes redeliveries, and reports its
readiness and metrics. Each piece runs the topic's loop: a target defined in the domain's terms, a
demonstration that defends it, and a signal that operates it in production. Use `poetry run` for
everything.

The result you are after: the summary behaviour is unchanged, `telemetry summary` still prints five
valid readings, three devices, and two rejected rows, but the service now survives a redelivered
reading, a burst past capacity, and a slow or dead sink, and it runs a long high-volume stream with
flat memory.

## Step 1: the downstream sink with a timeout and graceful degradation

Throughput is lost when ingest waits on a slow dependency. The fix is a short timeout on the outbound
call and a fallback that buffers locally instead of failing the request. **Define:** a sink slower
than one second, or down, must not fail ingest. **Defend:** a fault-injection test (Step 5) drives a
timing-out sink and asserts the reading is buffered, not raised.

**`src/telemetry_insight/sink.py`**

```python
"""A downstream sink with a timeout and graceful degradation (the dependability layer).

Ingest must not fail just because a downstream system is slow or down. `forward_or_buffer`
tries to forward one reading to a configured sink URL with a short timeout. If the sink
times out or returns an error, we degrade gracefully: buffer the reading locally (here we
mark it as not forwarded and return it) instead of failing the request. A slow sink then
slows nothing upstream, and the caller still gets its reading accepted.
"""

from __future__ import annotations

import os

import httpx

# Where to forward readings. In real code this comes from configuration, not a default here.
SINK_URL = os.environ.get("SINK_URL", "http://localhost:9999/sink")

# A short timeout so a slow sink cannot hold up ingest. One second is generous for a
# same-datacenter hop and short enough to protect throughput.
_TIMEOUT_SECONDS = 1.0


async def forward_or_buffer(
    reading: dict[str, object], client: httpx.AsyncClient
) -> dict[str, object]:
    """Forward the reading within the timeout, or buffer it locally on any failure."""
    try:
        response = await client.post(SINK_URL, json=reading, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
    except (httpx.TimeoutException, httpx.HTTPError):
        # Graceful degradation: keep the reading locally instead of failing the request.
        return {**reading, "forwarded": False}
    return {**reading, "forwarded": True}
```

The timeout is the throughput guard: one second caps the worst case so a slow sink cannot hold up
ingest. The `except` catches the timeout and the general `httpx.HTTPError` together, because both mean
the same thing to the caller: the downstream is not usable right now. On either, the reading comes
back with `forwarded` set to `False`, which the caller treats as accepted. That is graceful
degradation: a buffered reading beats a failed request.

## Step 2: structured logging and SLI metrics

You cannot operate a target you cannot see. This module is the Operate half of the loop: one
structured log line per request carrying the trace id, and a small collector for the service level
indicators. Both on the standard library, so nothing heavy is pulled in.

**`src/telemetry_insight/observability.py`**

```python
"""Structured logging and simple SLI metrics (the dependability layer)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

# One named logger for the whole package. Handlers are attached once in configure_logging.
_logger = logging.getLogger("telemetry_insight")


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a single stream handler once, so each event becomes one line on stderr."""
    if _logger.handlers:
        return
    handler = logging.StreamHandler()
    # We format each record ourselves as JSON, so the handler passes the message through as-is.
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(level)
    _logger.propagate = False


def log_event(
    event: str, trace_id: str, duration_ms: float, status: int, **extra: object
) -> None:
    """Emit one structured JSON line. The trace id ties the line to a single request."""
    record: dict[str, object] = {
        "event": event,
        "trace_id": trace_id,
        "duration_ms": round(duration_ms, 3),
        "status": status,
    }
    record.update(extra)
    # Leveled: a server error (5xx) logs at ERROR, everything else at INFO.
    level = logging.ERROR if status >= 500 else logging.INFO
    _logger.log(level, json.dumps(record))


@dataclass
class Metrics:
    """A tiny in-memory SLI collector: two counts plus a running duration total."""

    requests: int = 0
    errors: int = 0
    duration_ms_sum: float = 0.0

    def record(self, duration_ms: float, status: int) -> None:
        # Called once per request. A 5xx counts as an error; shed (429) and 4xx do not.
        self.requests += 1
        if status >= 500:
            self.errors += 1
        self.duration_ms_sum += duration_ms

    def render(self) -> str:
        """Render the metrics as plain text in a Prometheus-like shape (easy to scrape)."""
        avg = self.duration_ms_sum / self.requests if self.requests else 0.0
        lines = [
            f"telemetry_requests_total {self.requests}",
            f"telemetry_errors_total {self.errors}",
            f"telemetry_request_duration_ms_sum {self.duration_ms_sum:.3f}",
            f"telemetry_request_duration_ms_avg {avg:.3f}",
        ]
        return "\n".join(lines) + "\n"
```

`configure_logging` is guarded by the handler check, so a fresh app per test does not stack duplicate
handlers. `log_event` writes one JSON line carrying the trace id, and it is leveled: a 5xx logs at
ERROR, everything else at INFO. `Metrics` counts a shed request (429) and other 4xx as not-an-error,
because the client, not the service, caused them; only a 5xx burns the error budget. That distinction
is the difference between an SLI that reflects the service's health and one that blames the service
for its callers.

## Step 3: the dependability layer on the API

The service becomes dependable under load here. On top of the interoperable surface (the versioned
routes, the pydantic edge, the signed webhook, the trace id) sit four dependability behaviours:
load shedding through a bounded-concurrency gate, idempotency on ingest, optional sink forwarding
with graceful degradation, and a readiness route that reflects real capacity. The middleware wires in
per-request logging and metrics.

**`src/telemetry_insight/api.py`**

```python
"""The API at the edge: a versioned, validated HTTP surface with a dependability layer.

This topic adds the dependability layer, tuned for the telemetry domain where the pressure is
durability under load and throughput:

- Idempotency on ingest, so a redelivered reading is recognized and not stored twice.
- Load shedding through bounded concurrency, so excess work gets a fast 429 and the accepted
  work keeps meeting its target instead of everything degrading together.
- A downstream sink with a timeout and graceful degradation, so a slow sink never fails ingest.
- A readiness route that reflects real free capacity (503 when there is none), separate from
  plain liveness at `/health`.
- Structured, leveled logging with the trace id, and simple SLI metrics at `/metrics`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from collections.abc import Awaitable, Callable

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from telemetry_insight.observability import Metrics, configure_logging, log_event
from telemetry_insight.service import summarize_rows
from telemetry_insight.sink import forward_or_buffer

_WEBHOOK_SECRET = b"shared-webhook-secret"

# Default ceiling on concurrent ingest work. Beyond this we shed with a 429 rather than let
# every request slow down at once. Small enough to keep latency bounded on modest hardware.
_DEFAULT_MAX_CONCURRENT = 64


class Capacity:
    """A bounded-concurrency gate: at most `limit` units of work in flight at once."""

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._in_flight = 0

    def try_acquire(self) -> bool:
        # Non-blocking: take a slot if one is free, otherwise report that we are full.
        if self._in_flight >= self._limit:
            return False
        self._in_flight += 1
        return True

    def release(self) -> None:
        # Always paired with a successful try_acquire, in a finally block.
        if self._in_flight > 0:
            self._in_flight -= 1

    @property
    def free(self) -> int:
        return self._limit - self._in_flight
```

`Capacity` is where load shedding lives. `try_acquire` is non-blocking: it takes a slot when one is
free and returns `False` when the gate is full, and the ingest handler then sheds with a fast 429.
`free` is what the readiness route reads to report whether the service can take new work at all. The
`ReadingIn` model carries the range constraint from the interoperable base, plus an optional key for
dedup:

```python
class ReadingIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    device_id: str = Field(min_length=1)
    value: float = Field(ge=-50, le=150)  # a value outside -50 to 150 is rejected with a 422
    # Optional per-reading idempotency key. A redelivery carrying the same key is deduped.
    key: str | None = Field(default=None, min_length=1)
```

The value range is `-50` to `150`, so readings can be negative and out of a small range, exactly what
a real sensor produces. The factory builds the gate, the metrics, the store, and the seen-keys ledger,
and exposes the moving parts on `app.state`:

```python
def create_app(
    max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
    sink_client: httpx.AsyncClient | None = None,
) -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    configure_logging()
    app = FastAPI(title="telemetry-insight", version="0.6.0")
    store: list[dict[str, str]] = []
    # Idempotency ledger: keys we have already stored, so a redelivery is a no-op.
    seen_keys: set[str] = set()
    capacity = Capacity(max_concurrent)
    metrics = Metrics()

    # Expose the moving parts on app.state so tests and operators can inspect real capacity.
    app.state.capacity = capacity
    app.state.metrics = metrics

    @app.middleware("http")
    async def observe(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        request.state.trace_id = trace_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        response.headers["x-trace-id"] = trace_id
        # One SLI sample and one structured log line per request, both carrying the trace id.
        metrics.record(duration_ms, response.status_code)
        log_event(
            "request", trace_id, duration_ms, response.status_code, path=request.url.path
        )
        return response
```

Keeping the store, the ledger, the gate, and the metrics inside `create_app()` makes each app instance
independent, which is what lets every test start clean. The middleware reuses or generates the trace
id, stashes it on `request.state` so handlers can log with the same id, times the request, and records
one SLI sample and one structured line per request. The readiness, metrics, and ingest routes are the
heart of the layer:

```python
    @app.get("/health")
    def health() -> dict[str, str]:
        # Plain liveness: the process is up and serving. It says nothing about capacity.
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> Response:
        # Readiness reflects real capacity: with no free slot we cannot take new work, so we
        # answer 503 and load balancers route elsewhere until a slot frees up.
        if capacity.free <= 0:
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ready"}, status_code=200)

    @app.get("/metrics")
    def metrics_route() -> Response:
        # Hand-rolled SLI metrics as plain text: request count, error count, duration summary.
        return PlainTextResponse(metrics.render())

    @app.post("/v1/readings", status_code=201, response_model=ReadingAccepted)
    async def ingest(reading: ReadingIn, request: Request) -> ReadingAccepted:
        # Load shedding first: if the gate is full, shed with a fast 429 so accepted work
        # keeps its target instead of everyone slowing down together.
        if not capacity.try_acquire():
            raise HTTPException(status_code=429, detail="load shed: no free capacity")
        try:
            # Idempotency: a key can arrive on the reading or in an Idempotency-Key header.
            # If we have seen it, this is a redelivery, so we recognize it and store nothing.
            key = reading.key or request.headers.get("idempotency-key")
            if key is not None and key in seen_keys:
                return ReadingAccepted(status="duplicate")

            # Optional downstream forwarding. A slow or failing sink degrades to a buffered
            # reading (forwarded False) and never fails ingest.
            if sink_client is not None:
                outcome = await forward_or_buffer(
                    {"device_id": reading.device_id, "value": reading.value}, sink_client
                )
                log_event(
                    "forward",
                    request.state.trace_id,
                    0.0,
                    200,
                    forwarded=outcome["forwarded"],
                )

            store.append({"device_id": reading.device_id, "value": str(reading.value)})
            if key is not None:
                seen_keys.add(key)
            return ReadingAccepted(status="accepted")
        finally:
            # Always release the slot, whether we stored, deduped, or raised.
            capacity.release()
```

The order inside `ingest` is the whole design. Load shedding comes first: a full gate raises a fast
429 before any work, so accepted work keeps its target instead of everyone slowing down together. Then,
inside a `try` whose `finally` always releases the slot, idempotency short-circuits a redelivery
(returning `duplicate` and storing nothing), the optional sink forwards or buffers without ever
failing ingest, and only then does the reading land in the store and the key join the ledger. The key
can arrive on the reading's `key` field or in an `Idempotency-Key` header, so both a queue that stamps
the body and a client that sets a header are covered. `/ready` reads real free capacity and answers
503 when there is none, which is what lets a load balancer route away from a saturated instance;
`/health` stays plain liveness. The paginated list, insight, and signed webhook routes are carried
forward from the interoperable base and the factory ends with the module-level `app = create_app()`.

## Step 4: run it

```bash
poetry run telemetry summary
```

```text
readings: 5
devices : 3
rejected: 2
```

The same five valid readings, three devices, and two rejected rows as before. The dependability layer
did not change what the summary does; it changed how the service holds up while it does. To see the
readiness and metrics signals, start the API and read them:

```bash
poetry run telemetry serve
# then GET http://127.0.0.1:8000/ready and http://127.0.0.1:8000/metrics
```

## Step 5: the dependability tests

The deliverable proof, six tests, one per behaviour. A `TestClient` drives the API the way a real
caller would, and each test builds a fresh app so the in-memory store never leaks between them.

**`tests/test_dependability.py`**

```python
"""Dependability-layer tests, tuned for the telemetry domain (durability under load).

These prove the four dependability behaviors added on top of the interoperable base:
idempotency on ingest, load shedding through bounded concurrency, graceful sink degradation
under fault injection, and a readiness route that reflects real capacity.
"""

from __future__ import annotations

import asyncio

import httpx
from fastapi.testclient import TestClient

from telemetry_insight.api import create_app
from telemetry_insight.sink import forward_or_buffer


def _client(**kwargs: object) -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app(**kwargs))  # type: ignore[arg-type]


def test_idempotent_ingest_stores_once() -> None:
    client = _client()
    reading = {"device_id": "D1", "value": 20.5}
    headers = {"Idempotency-Key": "dedupe-1"}
    # The same reading redelivered with the same key must be stored only once.
    first = client.post("/v1/readings", json=reading, headers=headers)
    second = client.post("/v1/readings", json=reading, headers=headers)
    assert first.status_code == 201
    assert first.json()["status"] == "accepted"
    assert second.json()["status"] == "duplicate"  # the redelivery is recognized
    assert client.get("/v1/insight").json()["readings"] == 1  # not stored twice


def test_load_shedding_returns_429_when_full() -> None:
    app = create_app(max_concurrent=2)
    client = TestClient(app)
    capacity = app.state.capacity
    # Simulate two units of accepted work already in flight by filling both slots.
    assert capacity.try_acquire() is True
    assert capacity.try_acquire() is True
    # With no free capacity, excess ingest is shed fast with a 429.
    shed = client.post("/v1/readings", json={"device_id": "D1", "value": 20.0})
    assert shed.status_code == 429
    # Free the slots (the accepted work finished) and ingest succeeds again.
    capacity.release()
    capacity.release()
    ok = client.post("/v1/readings", json={"device_id": "D1", "value": 20.0})
    assert ok.status_code == 201


def test_sink_degrades_gracefully_on_timeout() -> None:
    # Fault injection: a mock sink client whose post always times out.
    class _TimingOutClient:
        async def post(self, *args: object, **kwargs: object) -> httpx.Response:
            raise httpx.TimeoutException("sink too slow")

    reading: dict[str, object] = {"device_id": "D1", "value": 20.0}
    # Test the async function directly with asyncio.run plus the mock, no pytest-asyncio needed.
    outcome = asyncio.run(forward_or_buffer(reading, _TimingOutClient()))  # type: ignore[arg-type]
    # Ingest degrades gracefully: the reading is buffered, marked not forwarded, never raised.
    assert outcome["forwarded"] is False
    assert outcome["device_id"] == "D1"


def test_ready_returns_200_with_free_capacity() -> None:
    client = _client()
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_ready_returns_503_when_no_capacity() -> None:
    app = create_app(max_concurrent=1)
    client = TestClient(app)
    # Fill the only slot: readiness must now report no free capacity with a 503.
    app.state.capacity.try_acquire()
    resp = client.get("/ready")
    assert resp.status_code == 503
    assert resp.json()["status"] == "unavailable"


def test_metrics_expose_request_and_error_counts() -> None:
    client = _client()
    client.get("/health")
    body = client.get("/metrics").text
    # Hand-rolled plain-text SLI metrics: counts and a duration summary are present.
    assert "telemetry_requests_total" in body
    assert "telemetry_errors_total" in body
    assert "telemetry_request_duration_ms_sum" in body
```

Read the six as the loop applied one behaviour at a time. The idempotency test posts the same key
twice and checks the second is recognized as a `duplicate` and the store holds one row, the durability
promise for a redelivered reading. The load-shedding test fills the gate by hand through
`app.state.capacity` and asserts the next ingest is a fast 429, then that ingest recovers once slots
free, the throughput promise under a burst. The sink test injects a timing-out client and asserts the
reading is buffered rather than raised, the graceful-degradation promise against a slow downstream.
The two readiness tests show `/ready` answering 200 with a free slot and 503 with none, the signal a
load balancer routes on. The metrics test shows the SLI counts are exposed for scraping. Driving the
capacity gate directly and testing `forward_or_buffer` with `asyncio.run` are what make the shed and
degrade paths reachable deterministically, with no real concurrency and no `pytest-asyncio`.

## Step 6: the soak, memory flat over a long stream

The MTBF proof for a domain whose input never ends. **Define:** memory stays flat over a long
high-volume run. **Defend:** drive ingest for 8000 iterations and print memory every 2000, with a
fixed idempotency key so dedup pins the store at one row and any memory that moves is per-request
overhead, not stored data.

**`scripts/soak.py`**

```python
"""Soak test: prove memory stays flat under a long, high-volume ingest stream."""

from __future__ import annotations

import tracemalloc

from fastapi.testclient import TestClient

from telemetry_insight.api import create_app

ITERATIONS = 8_000
REPORT_EVERY = 2_000


def main() -> None:
    client = TestClient(create_app())
    reading = {"device_id": "D1", "value": 20.5, "key": "soak-fixed-key"}

    tracemalloc.start()
    for i in range(1, ITERATIONS + 1):
        # Same key every time: dedup keeps the store at one row, so growth would be a leak.
        client.post("/v1/readings", json=reading)
        if i % REPORT_EVERY == 0:
            current, peak = tracemalloc.get_traced_memory()
            print(
                f"iter {i:>7}  current {current / 1_000_000:6.2f} MB  "
                f"peak {peak / 1_000_000:6.2f} MB"
            )
    tracemalloc.stop()

    # A final confirmation that dedup held the store flat across the whole run.
    total = client.get("/v1/insight").json()["readings"]
    print(f"stored readings after {ITERATIONS} posts: {total} (flat under dedup)")
```

```bash
poetry run python scripts/soak.py
```

```text
iter    2000  current   0.05 MB  peak   0.13 MB
iter    4000  current   0.05 MB  peak   0.13 MB
iter    6000  current   0.05 MB  peak   0.13 MB
iter    8000  current   0.05 MB  peak   0.13 MB
stored readings after 8000 posts: 1 (flat under dedup)
```

Memory holds flat across all 8000 iterations, and the store stays at one row because every post
carries the same key and dedup drops the redeliveries. Fixing the key is what separates the request
path from intentional growth: with the store pinned by dedup, a rising memory line could only be the
request handling itself. Flat memory here is the difference between a service that runs for months on
a telemetry stream and one that slowly rots and falls over.

## Step 7: green gate

```bash
poetry run pytest -q          # 25 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
```

The six dependability tests join the interoperable tests and everything carried forward from earlier
days, for 25 in all. ruff is clean and mypy strict is clean.

## Done when

- The project version is `0.6.0`, and the FastAPI app reports `version="0.6.0"`.
- `sink.py` has an async `forward_or_buffer(reading, client)` that forwards to a configurable
  `SINK_URL` with a 1.0 second timeout and, on `httpx.TimeoutException` or `httpx.HTTPError`, returns
  the reading with `forwarded` set to `False` instead of raising.
- `observability.py` has a `log_event` that emits one JSON line with `event`, `trace_id`,
  `duration_ms`, and `status`, leveled so a 5xx logs at ERROR, and a `Metrics` collector with a
  request count, an error count, and a duration summary.
- `api.py` has a `Capacity` gate and sheds ingest with a fast 429 when full, dedupes a reading whose
  key (from the `key` field or an `Idempotency-Key` header) has been seen, forwards through the sink
  only when a `sink_client` is given, and exposes `/ready` (200 or 503), `/health`, and `/metrics`.
- `create_app` takes `max_concurrent` and `sink_client`; readings may be negative and within the
  range `-50` to `150`; the middleware logs one structured line per request and records one SLI sample.
- `tests/test_dependability.py` proves idempotency stores once, load shedding returns 429 when full,
  the sink degrades on an injected timeout, `/ready` answers 200 and 503, and `/metrics` exposes the
  counts, six tests in all.
- `scripts/soak.py` runs 8000 ingest iterations with a fixed idempotency key, prints memory every 2000
  iterations, holds memory flat, and leaves the store at one row.
- `pytest` (25 passed), `ruff`, and `mypy` are all green, and `telemetry summary` still prints
  `readings: 5`, `devices : 3`, `rejected: 2`.

You have run the topic's loop on the telemetry domain: for each behaviour a target defined in the
domain's terms, a demonstration that defends it under load, and a signal that operates it in
production. The behaviour your CLI prints did not change; the service now holds its promise while
readings pour in and a downstream system misbehaves, and it can prove it.
