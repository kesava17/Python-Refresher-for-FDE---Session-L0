# reviews-insight, as microservices (live lab)

The `reviews-insight` monolith, redesigned into a microservice system: two vertical slices
behind one gateway, each owning its store, talking over a versioned contract and an event.

```
src/
  contracts/        the shared API and event models (one Answer both sides agree on)
  common/           config, observability (correlation id, health), the broker, the resilient client
  reviews_ingest/   the write slice: POST a review, store it, publish review-received
  reviews_query/    the read slice: serve aggregates, updated by consuming events
  gateway/          the front door and a small backend-for-frontend
tests/              per-service tests, a contract test, resilience and observability tests
scripts/smoke.py    an end-to-end run you can read
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
# gateway on http://localhost:8000, reviews-ingest on 8001, reviews-query on 8002
```

Then submit a review through the gateway and read the dashboard:

```bash
curl -X POST http://localhost:8000/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "p1", "rating": 5, "text": "great"}'

curl http://localhost:8000/bff/dashboard/p1
```

## What the design shows

- **Two vertical slices.** `reviews-ingest` (write) and `reviews-query` (read), each with its
  own store. reviews-query never opens the ingest database.
- **A contract.** The `contracts` package holds the versioned request, response, and event
  shapes both sides depend on, validated by pydantic at the boundary.
- **Sync and async.** The gateway calls services synchronously; the read model is updated
  asynchronously by consuming the `review-received` event, idempotently.
- **Resilience.** Calls have a timeout, retry with backoff, and a circuit breaker; the gateway
  degrades cleanly when a service is down.
- **Observability.** A correlation id is stamped per request and threaded across services.

The broker here is a small file-backed stand-in so the lab needs no external service; in
production the `publish` and `drain` seam is swapped for a real broker. Each service is one
package for readability; in production each would be its own repository and image.
