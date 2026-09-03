# Microservices liveLab: what this layer adds

What changed in the `reviews-insight` liveLab going into the Microservices Architecture topic. Earlier
topics built one dependable service: a single deployable with one database, a validated HTTP surface,
and function calls between its internal parts. This topic keeps the same behaviour a customer sees and
redesigns the shape underneath it: the one deployable becomes two services and a gateway, the one
database becomes a store per service, and an internal function call becomes an HTTP call plus an event.
Nothing about what a review is or how it is rolled up changes; what changes is that the write side and
the read side are now independent services that can be deployed, scaled, and owned on their own, and
the calls between them are made to survive a slow or missing neighbour.

Project path: `shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/microservices-architecture/liveLab`

## The shape change, in one picture

| Before (one dependable service) | After (a small system) |
| --- | --- |
| One deployable | Two services (`reviews-ingest`, `reviews-query`) behind a `gateway` |
| One database | A store per service (`ingest.db` for writes, `query.db` for reads) |
| A function call between internal parts | An HTTP call (gateway to service) plus one event (ingest to query) |
| Shapes shared by being in one module | A `contracts` package both sides depend on, validated by pydantic at the boundary |
| A call just returns or raises | Every remote call has a timeout, a retry, and a circuit breaker |
| One process, one log | A correlation id stamped per request and threaded across services |

## The new pieces

The liveLab is now a five-package `src/` tree. Each package is one clear responsibility, and in
production each service package would be its own repository and image; here they share one project for
readability.

| Package | Role | What lives in it |
| --- | --- | --- |
| `contracts` | The one Answer both sides agree on | `ReviewIn`, `ReviewCreated`, `Aggregate`, and the `ReviewReceived` event, all pydantic models so a wrong shape is rejected at the boundary before any logic runs. |
| `common` | The shared machinery every service uses | `config` (settings from the environment with offline defaults), `observability` (correlation id middleware, structured logging, `/health`), `broker` (the file-backed event broker), `client` (the resilient HTTP client). |
| `reviews_ingest` | The write slice | `POST /v1/reviews`: validate, store in its own `ingest.db`, and publish a `review-received` event. Owns the write store; nothing else opens it. |
| `reviews_query` | The read slice | `GET /v1/aggregates/{product_id}`: serve the per-product rollup, kept fresh by consuming `review-received` events into its own `query.db`. Never opens the ingest database. |
| `gateway` | The front door | `POST /reviews` forwards to reviews-ingest; `GET /bff/dashboard/{product_id}` is a small backend-for-frontend that makes one guarded call to reviews-query and degrades cleanly. |

### `contracts` (the shared agreement)

Four pydantic models are the single definition both sides depend on. `ReviewIn` (product_id, rating 1
to 5, text) is validated at the ingest boundary. `ReviewCreated` (id) is the write response. `Aggregate`
(product_id, count, average_rating) is the read model. `ReviewReceived` (id, product_id, rating) is the
event reviews-ingest publishes and reviews-query consumes. Because this is one shared package, a change
to a shape is a change both services see, and the contract test pins the fields so a change on one side
cannot silently break the other. Rationale: the boundary between services is a promise, so it is
written down as a typed contract rather than left implicit.

### `common/config.py` (settings from the environment)

Settings are read from environment variables with offline defaults anchored to the project root: the
two store paths, the broker path, the two service URLs, and the HTTP timeout. No secret is hard-coded.
docker compose sets the service URLs to the container names and the store and broker paths to mounted
volumes; on a laptop the defaults let the whole system run with nothing configured. Rationale: the same
image runs in every environment, and only the environment changes.

### `common/observability.py` (one request across many services)

A middleware stamps every request with a correlation id, taken from the incoming `X-Correlation-ID`
header or generated when absent, puts it on every structured log line, and echoes it back on the
response. `install` also adds the `/health` route the gateway and the platform poll. Rationale: once a
request spans several services, the only way to follow it is a shared id threaded through every hop and
every log line.

### `common/broker.py` (the asynchronous seam)

A tiny file-backed broker so the asynchronous path runs with no external service. `publish` appends an
event to a JSONL file and returns at once; `drain` reads the events for a topic and hands each to a
handler exactly once, tracking processed ids in a sidecar `.seen` file. That gives the two teaching
properties that matter: at-least-once delivery, and an idempotent consumer that skips a duplicate by
its id. Rationale: the `publish` and `drain` seam is the shape a real broker (Redis or a queue) would
have, so production swaps the implementation without touching the services.

### `common/client.py` (calls that survive a bad neighbour)

The `resilient_get` helper wraps every cross-service call in a timeout, a retry with backoff for
transient errors (via `tenacity`), and a `CircuitBreaker` that opens after a threshold of failures and
half-opens after a cooldown to try again. Rationale: in a distributed system a dependency will be slow
or down at some point, and a caller that hangs or crashes with it turns one failure into many; guarding
every call is how a service survives its neighbour.

### `reviews_ingest` (the write slice)

`create_app` builds a FastAPI service with its own `IngestStore` (a private sqlite database) and a
broker. `POST /v1/reviews` validates the body against `ReviewIn`, saves it, publishes a
`review-received` event, and returns the new id. It is the only service that opens the ingest database.
Rationale: the write side is a service in its own right, owning its data and announcing what happened
as an event rather than reaching into anyone else's store.

### `reviews_query` (the read slice)

`create_app` builds a FastAPI service with its own `QueryStore` and the same broker. `GET
/v1/aggregates/{product_id}` drains any new events into the read model first, then serves the rollup, or
answers 404 for an unknown product; `POST /internal/drain` consumes pending events on demand. The read
model is built only from consumed events, so reviews-query never opens the ingest database. Rationale:
the read side owns its own shape of the data, optimised for reads and updated asynchronously, which is
what lets the two slices scale and change independently.

### `gateway` (the front door)

`create_app` builds the gateway pointed at the two service URLs, with its own circuit breaker. `POST
/reviews` forwards synchronously to reviews-ingest and raises a clear 502 if it is unavailable. `GET
/bff/dashboard/{product_id}` is a backend-for-frontend: it makes one guarded call to reviews-query and,
when that service is down, returns a note with a null summary instead of hanging or failing hard. Both
paths forward the correlation id. Rationale: a client should talk to one front door, and that front
door should shape the answer it needs and degrade cleanly when a part behind it is missing.

### The wiring: `pyproject.toml`, `Dockerfile`, `docker-compose.yml`

The project is version `1.0.0` and declares the five packages plus the new dependencies this topic
needs: `fastapi` and `uvicorn` to serve each service, `httpx` for the calls between them, and
`tenacity` for the retry. The `Dockerfile` builds one slim image; `docker-compose.yml` runs that one
image three times with a different `uvicorn` command and different environment, each service on its own
port (gateway 8000, reviews-ingest 8001, reviews-query 8002) with its own database volume and a shared
broker volume. Rationale: one image, many services, is the deployment shape of the design in the small,
and Compose gives that parity on a laptop.

## The proof

- `poetry run pytest` reports **16 passed**: `test_contract.py` (3) pins the event and aggregate
  shapes and one ingest-to-query end-to-end path; `test_ingest.py` (4) and `test_query.py` (3) cover
  each slice; `test_gateway.py` (2) proves the dashboard degrades to a note and a write fails fast with
  a 502 when a downstream is down; `test_resilience.py` (2) opens and recovers the circuit breaker; and
  `test_observability.py` (2) shows the correlation id honoured and echoed.
- `poetry run ruff check src tests` is clean.
- `poetry run mypy src` is clean under strict typing.
- `poetry run python scripts/smoke.py` runs the whole path in one process: three reviews in, the read
  model built to count 3 and average 4.0 by consuming events, a replayed event that does not
  double-count, and an honest 404 for an unknown product.
- `docker compose up --build` brings all three services up healthy, each on its own port with its own
  store, and the gateway degrades cleanly when a service is stopped.

## What to take away

This topic does not add a feature; it changes a shape. The same dependable service is redrawn as two
independent slices behind a gateway, each owning its data, communicating over a written contract and one
event, with every call between them guarded and every request traceable by a shared id. That buys
independence (deploy, scale, and own each slice on its own) at the cost of more moving parts and the
new work of making a distributed call survive. The 16 tests, the clean lint and types, the one-process
smoke, and the healthy Compose stack are the evidence that the redesign holds its behaviour while
gaining that independence.
