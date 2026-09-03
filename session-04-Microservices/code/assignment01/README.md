# telemetry-insight, as microservices (assignment 01)

A telemetry-insight system split into a microservice design: two vertical slices behind one
gateway, each owning its store, talking over a versioned contract and an event. The focus of
this assignment is the asynchronous split and idempotency: at-least-once delivery means
duplicates happen, so the read side must fold a replayed event without moving the rollup.

```
src/
  contracts/          the shared API and event models (one shape both sides agree on)
  common/             config, observability (correlation id, health), the broker, the resilient client
  telemetry_ingest/   the write slice: POST a reading, store it, publish reading-received
  telemetry_rollup/   the read slice: serve per-device rollups, updated by consuming events
  gateway/            the front door and a small backend-for-frontend
tests/                per-service tests, a contract test, the idempotency proof, resilience, observability
scripts/smoke.py      an end-to-end run you can read
```

## Run the tests (offline, no servers)

```bash
poetry install
poetry run pytest
poetry run ruff check src tests
poetry run mypy src
```

## See it end to end in one process

```bash
poetry run python scripts/smoke.py
```

## Run the whole system with Docker Compose

```bash
docker compose up --build
# gateway on http://localhost:8000, telemetry-ingest on 8001, telemetry-rollup on 8002
```

Then submit a reading through the gateway and read the device view:

```bash
curl -X POST http://localhost:8000/readings \
  -H "content-type: application/json" \
  -d '{"device_id": "d1", "value": 21.5, "ts": "2026-09-01T10:00:00Z"}'

curl http://localhost:8000/bff/device/d1
```

## What the design shows

- **Two vertical slices.** `telemetry-ingest` (write) and `telemetry-rollup` (read), each with
  its own store. telemetry-rollup never opens the ingest database.
- **A contract.** The `contracts` package holds the versioned request, response, and event
  shapes both sides depend on, validated by pydantic at the boundary.
- **Sync and async.** The gateway calls services synchronously; the read model is updated
  asynchronously by consuming the `reading-received` event, idempotently.
- **Idempotency under at-least-once delivery.** A redelivered event carries an id the consumer
  has already processed, so it is skipped and the rollup (count and average) stays put. See
  `tests/test_idempotency.py` for the replay proof.
- **Resilience.** Calls have a timeout, retry with backoff, and a circuit breaker; the gateway
  degrades cleanly when a service is down.
- **Observability.** A correlation id is stamped per request and threaded across services.

The broker here is a small file-backed stand-in so the assignment needs no external service;
in production the `publish` and `drain` seam is swapped for a real broker. Each service is one
package for readability; in production each would be its own repository and image.
