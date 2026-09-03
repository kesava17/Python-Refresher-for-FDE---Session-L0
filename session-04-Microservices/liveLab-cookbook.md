# Microservices liveLab: run it, then explore it

This is the `reviews-insight` liveLab for the Microservices Architecture topic. The idea of the day is
that the same service can be reshaped from one deployable into a small system of independent parts: two
vertical slices behind a gateway, each owning its own store, talking over a versioned contract and one
event. The behaviour a customer sees is unchanged; what changes is the shape, and with it the ways the
system can be scaled, deployed, and kept running when a part is slow or down. Run the project first so
you see the parts talking, then work through the explore prompts to feel where the seams are.

The topic frames the redesign through a few ideas you can point at in the running code: **a service
owns its data** (reviews-query never opens the ingest database), **synchronous where you must and
asynchronous where you can** (the gateway calls a service and waits, the read model is updated by
consuming an event), and **resilience at every call** (a timeout, a retry, and a circuit breaker, so
one service being down does not take its caller down with it). Keep these in mind; the code you run
below is those ideas made concrete.

Code lives at
`shared/repoCoder/base/guildtrek/trainings/courses/buildingEnterpriseAppsWithPython/code/microservices-architecture/liveLab`.
Open a terminal there.

---

## Part 1: Run the project

### Set it up (once)

This is a standard Poetry project. Install its dependencies once:

```bash
poetry install
```

### Run the checks (offline, no servers)

Prove the whole thing is green before touching it. The tests wire the services together in-process over
a shared temporary broker, so nothing needs to be listening:

```bash
poetry run pytest              # 16 passed
poetry run ruff check src tests   # All checks passed!
poetry run mypy src            # Success: no issues found
```

The 16 tests spread across the seams the design introduces: `test_contract.py` (3) pins the event and
aggregate shapes both services agree on, plus one end-to-end path where ingest publishes and query
consumes; `test_ingest.py` (4) and `test_query.py` (3) cover each slice on its own; `test_gateway.py`
(2) proves the gateway degrades cleanly when a downstream service is unreachable; `test_resilience.py`
(2) opens and recovers the circuit breaker; and `test_observability.py` (2) shows the correlation id is
honoured and echoed.

### See it end to end in one process

The smoke script wires all three parts over one shared temporary broker (the same way docker compose
wires them over a real one), submits reviews through reviews-ingest, lets reviews-query consume the
events, and reads the aggregate back. Run it and read it side by side:

```bash
poetry run python scripts/smoke.py
```

Expect output like this (the ids and the average are what matter):

```text
submit three reviews for p1 (through reviews-ingest):
  rating 5 -> 201 {'id': 1} ... rating 4 -> 201 {'id': 3}
reviews-query consumes the events and serves the aggregate:
  /v1/aggregates/p1 -> {'product_id': 'p1', 'count': 3, 'average_rating': 4.0}
a duplicate event does not double-count -> {'product_id': 'p1', 'count': 3, 'average_rating': 4.0}
unknown product -> 404
```

Read that top to bottom: three reviews go in through the write slice, the read slice builds its own
rollup by consuming the events (count 3, average 4.0), a replayed event does not double-count because
the consumer is idempotent, and an unknown product is answered with an honest 404 rather than a guess.

### Run the whole system with Docker Compose

To see the parts as real, separate processes on their own ports, each with its own database volume and
a shared broker volume, bring the system up with Compose:

```bash
docker compose up --build
# gateway on http://localhost:8000, reviews-ingest on 8001, reviews-query on 8002
```

One image is built and run three times with a different command, which is the "one image per service"
idea in the small. Leave this running in its own terminal for Part 2.

---

## Part 2: Hit the endpoints by hand

With the Compose stack up, drive the system two ways: through the gateway (the front door a client
uses), and against each service directly (to see the slice on its own). The `tests/http/` folder holds
these same calls as `.http` files you can send from an editor's REST client (VS Code REST Client or the
JetBrains HTTP client); start with `reviews.http` (through the gateway), then `services.http` (each
service directly).

### Through the gateway

Submit a review, then read the dashboard fragment the gateway assembles for it:

```bash
curl -s -X POST http://localhost:8000/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "p1", "rating": 5, "text": "great"}'
# -> {"id": 1}

curl -s http://localhost:8000/bff/dashboard/p1
# -> {"product_id": "p1", "summary": {"product_id": "p1", "count": 1, "average_rating": 5.0}}
```

The `POST /reviews` call is synchronous: the gateway forwards it to reviews-ingest and waits for the
new id. The `GET /bff/dashboard/{product_id}` call is a small backend-for-frontend: the gateway makes
one tailored, guarded call to reviews-query and shapes the answer for a dashboard tile. Submit two or
three more reviews for `p1` and watch the count and average move.

### Against each service directly

The gateway is just a front door; each slice is a service in its own right. Talk to them straight:

```bash
# reviews-ingest: create a review
curl -s -X POST http://localhost:8001/v1/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "p2", "rating": 4, "text": "solid"}'

# reviews-query: the aggregate for that product
curl -s http://localhost:8002/v1/aggregates/p2

# liveness of each service
curl -s http://localhost:8001/health
curl -s http://localhost:8002/health
```

Note the split: reviews-ingest owns the write path and its `ingest.db`; reviews-query owns the read
path and its `query.db`, and it builds that read model only from the events it consumes. It never opens
the ingest database. That is a service owning its data, which is what lets the two be deployed, scaled,
and changed independently.

---

## Part 3: Explore prompts

Now change something and watch the system respond. Each of these makes one design property visible.

### Stop reviews-query and watch the gateway degrade

In the terminal running Compose, stop just the read slice (from a second terminal):

```bash
docker compose stop reviews-query
curl -s http://localhost:8000/bff/dashboard/p1
# -> {"product_id": "p1", "summary": null, "note": "temporarily unavailable"}
```

The dashboard does not hang and does not return a 500. The gateway's call to reviews-query fails, the
circuit breaker opens after repeated failures, and the backend-for-frontend returns a clear note with a
null summary instead. This is graceful degradation: a down dependency becomes a smaller answer, not an
outage. Bring it back with `docker compose start reviews-query` and the dashboard fills in again once
the cooldown lets the breaker half-open.

### Stop reviews-ingest and watch a write fail fast

```bash
docker compose stop reviews-ingest
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/reviews \
  -H "content-type: application/json" \
  -d '{"product_id": "p1", "rating": 5, "text": "great"}'
# -> 502
```

A write cannot be faked, so the gateway does the honest thing: it fails fast with a 502 rather than
hanging on a service that is not there. Compare that with the read path, which can still answer with a
degraded note. The two behaviours are deliberate, and they are pinned by `test_gateway.py`. Restart the
service with `docker compose start reviews-ingest`.

### Replay an event and see the idempotent consumer skip it

The read model is built from an at-least-once event stream, so a duplicate must not double-count. The
smoke script shows this directly: after three reviews it publishes the very first event again and the
aggregate stays at count 3, average 4.0. To see it yourself, run `scripts/smoke.py` and watch the two
`/v1/aggregates/p1` lines match:

```text
reviews-query consumes the events and serves the aggregate:
  /v1/aggregates/p1 -> {'product_id': 'p1', 'count': 3, 'average_rating': 4.0}
a duplicate event does not double-count -> {'product_id': 'p1', 'count': 3, 'average_rating': 4.0}
```

The broker tracks a key per event id in a sidecar file; on the second delivery the key is already seen,
so the handler is skipped. That is what keeps the consumer safe under redelivery.

### Send a correlation id and see it threaded through

Every service stamps each request with a correlation id (from the incoming header or freshly generated)
and echoes it back, so one request that spans several services can be followed through logs that share
one id. Send your own and watch it come back:

```bash
curl -s -D - -o /dev/null http://localhost:8001/health -H "X-Correlation-ID: my-trace-123"
# response headers include: x-correlation-id: my-trace-123
```

Now submit a review through the gateway with the same header and look at the Compose logs: the gateway
forwards the id to reviews-ingest, and both services print structured log lines carrying
`"cid":"my-trace-123"`. Omit the header and each service generates its own id instead, so a request is
always traceable.

---

## What to take away

The service did the same job before and after this topic; what changed is its shape. One deployable
became two slices and a gateway, one database became a store per service, and a function call became an
HTTP call plus an event. In exchange you get parts that can be deployed, scaled, and owned separately,
and you take on the work of making the calls between them survive: a contract both sides agree on, a
gateway that degrades instead of hanging, an event consumer that is idempotent under redelivery, and a
correlation id that threads a request across the whole system. Run the project, stop a service, replay
an event, send a trace id, and watch each property hold. That is a microservice design doing its job,
and it is exactly the trade the topic asks you to weigh: more moving parts, in exchange for
independence and resilience.
