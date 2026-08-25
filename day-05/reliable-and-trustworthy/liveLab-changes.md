# Dependable liveLab: file-level changes

What changed in the `reviews-insight` liveLab going from the Interoperable topic to
the Dependable (reliable and trustworthy) topic, file by file, with the reason for each
change. The Interoperable topic made the service talk to the world safely. The Dependable
topic keeps it up while it does so: a slow dependency cannot take it down, a client retry
has exactly one effect, an orchestrator can tell whether the instance still has room, and
an operator can read the service's request rate, error rate, and latency.

Project path: `shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/reliable-and-trustworthy/liveLab`

## At a glance

| File | Status | What changed | Why |
| --- | --- | --- | --- |
| `src/reviews_insight/enrichment.py` | New | An async `enrich_or_degrade` that calls an external enrichment service with a 1.0s timeout and degrades to `enriched: False` on timeout or error. | A dependable service does not let a slow dependency fail its own work. This is the availability lesson in one function. |
| `src/reviews_insight/observability.py` | New | Structured JSON logging carrying the trace id, a `Metrics` SLI class (requests, errors, duration), and a `Capacity` gauge of in-flight work. | You cannot operate what you cannot see. This makes the service measurable, all on the standard library. |
| `scripts/soak.py` | New | Drives the core summarize loop 2000 times under `tracemalloc` and prints memory at intervals, showing it stays flat. | MTBF: a leak only shows up under sustained load, so a soak test proves the loop retains no growing state. |
| `tests/test_dependability.py` | New | Seven tests: graceful degradation, the async enrich function on timeout and on success, idempotent submit, distinct keys, readiness, and the metrics endpoint. | Every operational habit the topic adds is proved by a test that a change cannot silently break. |
| `src/reviews_insight/api.py` | Modified | Trace-id middleware grew into an `observe` middleware (capacity, timing, metrics, structured log); `POST /v1/reviews` is now async, enriches-or-degrades, honors `Idempotency-Key`, and stores an `enriched` flag; new `GET /ready` and `GET /metrics`; `ReviewAccepted` gained `enriched`. | The API is where availability, idempotency, readiness, and observability all land. It is the centerpiece of the topic. |
| `src/reviews_insight/config.py` | Modified | Added `enrichment_url`, default `http://enrichment.invalid/enrich`. | The submit path needs a configurable enrichment target, and a fail-fast default so an unconfigured service degrades instead of hanging. |
| `pyproject.toml` | Modified | Version `0.5.0` to `0.6.0`; new description naming the dependable goals. | Keep the package version and its description in step with the topic. |

## New files, in detail

### `src/reviews_insight/enrichment.py` (availability under a slow dependency)

An async `enrich_or_degrade(review, client, url, timeout=1.0)`. On success it returns the
review with an `insight` from the service and `enriched: True`. On an `httpx.TimeoutException`
or any `httpx.HTTPError` (a connection failure or a non-2xx response) it returns the same
review with `insight: None` and `enriched: False`, so the caller still gets a usable result.
The 1.0s timeout is the budget: past it the service stops waiting so one slow dependency
cannot pile up requests and exhaust the process. The client is passed in (dependency
injection), which lets a test supply a failing client. Rationale: this is graceful
degradation, the core availability idea. A submit stays available whether or not the
enrichment dependency is healthy.

### `src/reviews_insight/observability.py` (measurable and operable)

Three plain-standard-library pieces, none of which change what a valid request returns:

1. **Structured logging.** `get_logger()` returns a logger that writes one JSON object per
   line to stdout, configured once (repeated calls do not add handlers). `log_request(...)`
   writes one line per request carrying the same trace id the middleware echoes in the
   response header, so a log line and a client-visible request can be matched up. Rationale:
   machine-parseable logs plus a correlation id make a failure findable across services.
2. **SLI metrics.** `Metrics` keeps in-memory counters (`requests`, `errors`,
   `duration_ms_total`), counts a 5xx as a service error, and renders the three golden
   signals (rate, errors, duration) as plain text. Rationale: request rate, error rate, and
   latency are the signals an operator watches, exposed without a heavy metrics library.
3. **Capacity gauge.** `Capacity(limit)` tracks in-flight requests with a plain integer
   (safe because the event loop runs handlers cooperatively on one thread): `acquire` on
   start, `release` on finish, `has_free()` for readiness. Rationale: readiness must reflect
   real capacity, not a fixed guess.

### `scripts/soak.py` (MTBF: no leak under sustained load)

Starts `tracemalloc`, runs `summarize_rows` over a fixed 10,000-row batch for 2000
iterations, and prints the traced memory every 500 runs. The number stays flat because
each run builds, counts, and discards, retaining nothing between runs. Rationale: a
dependable service must survive a long run, not just one request. A memory leak surfaces
only under sustained load, so the soak test drives the loop hard and shows memory does not
grow.

### `tests/test_dependability.py` (seven tests)

Uses the FastAPI `TestClient` for the HTTP surface and `asyncio.run` with small fake clients
for the async function, so no `pytest-asyncio` is needed. The tests: a submit still returns
201 with `enriched: False` when the injected enrichment client always times out (fault
injection proving degradation); the async `enrich_or_degrade` returns the degraded shape on
timeout and the enriched shape on success; two submits with the same `Idempotency-Key` store
only one review and return the same result; two different keys store separately; `GET /ready`
returns 200 with free capacity while `GET /health` stays a separate check; and `GET /metrics`
exposes the SLI counters as text. Rationale: each new operational behavior gets a test that
locks the contract in place.

## Modified files, in detail

### `src/reviews_insight/api.py`

The topic's changes concentrate here.

1. **`observe` middleware.** The old `add_trace_id` middleware became `observe`. It still
   reuses or mints a trace id and echoes it, and now also acquires a capacity slot, times the
   request with `time.perf_counter`, records the SLIs on `Metrics`, and writes one structured
   log line. The capacity slot is released in a `finally`, so it does not leak even if a
   handler raises. Rationale: one place for the cross-cutting operational concerns, applied to
   every request.
2. **`POST /v1/reviews` made dependable.** The handler is now `async`. It reads an optional
   `Idempotency-Key` header: if the key was seen before, it returns the earlier result and
   stores nothing new, so a retry has exactly one effect. Otherwise it calls `_enrich` (which
   bounds the enrichment call with the timeout and degrades on failure), stores the review with
   an `enriched` flag alongside it, and records the result under the idempotency key. Rationale:
   idempotency makes a client retry safe, and enrich-or-degrade keeps the submit available.
3. **`GET /ready` and `GET /metrics`.** Readiness returns `{"status": "ready"}` with free
   capacity and 503 `{"status": "at capacity"}` when the in-flight limit (`_CAPACITY_LIMIT`,
   100) is reached, so an orchestrator can route work away from a saturated instance. Metrics
   returns the plain-text SLI exposition. Rationale: readiness is distinct from liveness, and
   the SLIs need a scrapeable surface.
4. **`ReviewAccepted` gained `enriched`.** The response model now reports whether the
   enrichment dependency answered in time or the request was accepted in degraded form.
   Rationale: the caller should know honestly whether the record carries an insight.
5. **Injection and version.** `create_app` accepts an optional `enrichment_client` and
   `enrichment_url` (tests inject a failing client or a fake URL; otherwise the URL comes from
   config and a fresh `httpx` client is opened per submit), and the app version moved to
   `0.6.0`.

Carried forward unchanged from the Interoperable topic: `GET /health`, `GET /v1/reviews`
pagination, `GET /v1/insight`, the signed `POST /v1/webhooks/rating`, and the generated
OpenAPI document.

### `src/reviews_insight/config.py`

Added an `enrichment_url` field to `Config`, read from `ENRICHMENT_URL` with a default of
`http://enrichment.invalid/enrich`. The `.invalid` TLD is reserved and never resolves
(RFC 2606), so with no enrichment server configured the call fails fast and the submit path
degrades gracefully instead of hanging. Rationale: durability of the submit path, the
default is deliberately unreachable so an unconfigured service still behaves well.

### `pyproject.toml`

Version `0.5.0` to `0.6.0`, and the description now names the dependable goals (timeouts,
graceful degradation, idempotency, readiness, structured logging, SLI metrics). Rationale:
keep the package metadata in step with the topic. No new third-party dependency was needed,
`httpx` was already present from the Interoperable topic.

### A note on `__init__.py`

`src/reviews_insight/__init__.py` was not changed and still reads `__version__ = "0.5.0"`.
Only `pyproject.toml` carries the `0.6.0` bump in this topic.

## How it is verified

- `poetry run pytest -q` reports **26 passed** (up from 19), the seven new ones in
  `tests/test_dependability.py`.
- `poetry run ruff check .` is clean.
- `poetry run mypy src` is clean under strict typing.
- `poetry run reviews summary` prints `reviews: 5 / products: 3 / rejected: 2`.
