# transactions-insight, as microservices (assignment 02)

A financial `transactions-insight` system, built as a microservice design: two vertical slices
behind one gateway, each owning its store, talking over a versioned contract and an event. The
focus of this assignment is a **versioned contract** plus **resilience** (timeout, retry,
circuit breaker, graceful degradation) and **correlation-id** propagation.

```
src/
  contracts/             the shared API and event models (one Answer both sides agree on)
  common/                config, observability (correlation id, health), the broker, the resilient client
  transactions_service/  the write slice: POST a transaction, store it, publish transaction-recorded
  ledger_service/        the read slice: serve a per-account summary, updated by consuming events
  gateway/               the front door and a small backend-for-frontend
tests/                   per-service tests, a contract test, resilience, degradation, reconciliation, observability
scripts/smoke.py         an end-to-end run you can read
```

Money is held everywhere as `amount_cents`, an integer count of minor units (paise for the
rupee), never a float. A balance built from integers reconciles to the paise; a balance built
from floats would drift. In this system a credit adds to an account balance and a debit
subtracts from it.

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
# gateway on http://localhost:8000, transactions-service on 8001, ledger-service on 8002
```

Then submit a transaction through the gateway and read the account view (amounts are in paise,
so 500 is rupees 5.00):

```bash
curl -X POST http://localhost:8000/transactions \
  -H "content-type: application/json" \
  -d '{"account_id": "acc-1", "amount_cents": 500, "kind": "credit"}'

curl http://localhost:8000/bff/account/acc-1
```

## What the design shows

- **Two vertical slices.** `transactions-service` (write) and `ledger-service` (read), each with
  its own store. ledger-service never opens the transactions database.
- **A versioned contract.** The `contracts` package holds the versioned request, response, and
  event shapes both sides depend on, validated by pydantic at the boundary, served under `/v1`
  so the contract can evolve without breaking existing callers.
- **Sync and async.** The gateway calls services synchronously; the read model is updated
  asynchronously by consuming the `transaction-recorded` event, idempotently, so a redelivered
  event never double-counts a balance.
- **Resilience.** Calls have a timeout, retry with backoff, and a circuit breaker; the gateway
  degrades cleanly (a clear note, status 200) when the ledger is down, and returns 502 when
  transactions-service is down, rather than hanging with a failing dependency.
- **Reconciliation.** The ledger balance equals the sum of credits minus debits across the
  recorded transactions, checked as a test and in the smoke run, all in integer paise.
- **Observability.** A correlation id is stamped per request and threaded across services, so one
  request that spans both can be followed end to end through logs that share one id.

The broker here is a small file-backed stand-in so the lab needs no external service; in
production the `publish` and `drain` seam is swapped for a real broker. Each service is one
package for readability; in production each would be its own repository and image.
