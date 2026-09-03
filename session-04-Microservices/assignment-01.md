# Assignment 01 · Split telemetry-insight into asynchronous services

> Offline practice for the Microservices Architecture topic. In class you split
> `reviews-insight` into two services behind a gateway, with a versioned contract, a store per
> service, synchronous calls, and an event that keeps a read model fresh. Now run the same
> redesign on your `telemetry-insight` service, with the emphasis the telemetry domain calls
> for: readings arrive fast and in bursts, so the write path and the read path want to scale
> differently, and the link between them is best made asynchronous. The pressure is not a clever
> answer, it is making the split hold up when a message is delivered twice.

This is a do-it-yourself assignment. The point is to feel why the asynchronous seam needs an
idempotent consumer: a broker that promises at-least-once delivery will, sooner or later, hand
you the same event again, and a rollup that double-counts it is quietly wrong. The counting
logic itself is simple. What is new is that the count now lives in a separate service, fed by
an event, and must stay correct when that event is redelivered.

Start from the `telemetry-insight` domain: a reading is a device id, a numeric value, and a
timestamp. Build the split as its own project, mirroring the reference structure from the live
lab, and keep everything offline: a file-backed broker stands in for a real message broker, so
nothing here needs a server beyond the two services themselves.

## The goal

One thing, done honestly: two services and a shared contract, joined by an event, with an
idempotent consumer. A `telemetry-ingest` service accepts and stores a reading and publishes a
`reading-received` event. A `telemetry-rollup` service consumes those events into its own read
store and serves a per-device rollup (the count and the average value). A gateway sits in
front. The proof of the assignment is a single behaviour: a replayed event does not change the
rollup.

The target behaviour, from the end-to-end run, is:

```text
telemetry-rollup consumes the events and serves the rollup:
  /v1/rollup/d1 -> {'device_id': 'd1', 'count': 3, 'average_value': 21.47}

a replayed event (same id) does not change the rollup (idempotent consumer):
  /v1/rollup/d1 -> {'device_id': 'd1', 'count': 3, 'average_value': 21.47}

unknown device escalates to a clear 404, not a guess:
  /v1/rollup/unknown -> 404
```

Run the redesign through the chapter's lens. For each piece, hold both halves in view:

- **Architecture.** The write path (ingest) and the read path (rollup) are separate
  capabilities, each owning its store. The link between them is an event, not a shared table,
  so the rollup can be rebuilt and can scale on its own. At-least-once delivery is a fact of
  the transport, so the consumer must be idempotent.
- **Engineering.** Make the code hold the design: each service is its own FastAPI app with its
  own sqlite store, the contract is a set of pydantic models both sides import, and the rollup
  consumer keys on the event id so a duplicate is skipped.

## What you have to build

One Poetry project with a `src` layout and these packages, mirroring the live lab:

1. **The contract (`contracts/`).** `ReadingIn{device_id, value, ts}`, `ReadingCreated{id}`,
   `Rollup{device_id, count, average_value}`, and the event `ReadingReceived{id, device_id,
   value}`. Validate at the boundary with pydantic.
2. **The shared infrastructure (`common/`).** Config from the environment, a correlation-id
   middleware with a health route, a file-backed broker with an idempotent `drain`, and a
   resilient client with a timeout, a retry, and a circuit breaker. You may carry these forward
   from the live lab unchanged.
3. **`telemetry-ingest`.** `POST /v1/readings` validates a reading, stores it in its own store,
   and publishes a `reading-received` event. It has a health route.
4. **`telemetry-rollup`.** Consumes `reading-received` events idempotently into its own read
   store (count and running average per device), and serves `GET /v1/rollup/{device_id}`,
   returning a 404 for a device it has never seen.
5. **The gateway.** `POST /readings` forwards to ingest, and `GET /bff/device/{device_id}`
   reads the rollup, degrading cleanly when the rollup service is down.
6. **Tests** that prove each service alone, the contract and the end-to-end path, resilience,
   observability, and, above all, idempotency.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the contract and the stores

Define the four pydantic models, then give each service its own sqlite store. The ingest store
keeps the raw readings; the rollup store keeps, per device, the count and the sum of values, so
the average is a simple division at read time. The rollup store never opens the ingest store.

Hint: keeping the count and the sum, rather than a list of values, is what lets the rollup fold
in one event at a time and answer in constant work. It is also what makes a duplicate easy to
ignore: you only add to the sum when the event is new.

### Level 2: telemetry-ingest publishes an event

Build the ingest app. `POST /v1/readings` validates the reading, saves it, and publishes a
`reading-received` event carrying the id, the device id, and the value. Return the new id. The
publish returns at once; the rollup will consume the event on its own time.

Hint: the event carries the id. That id is the key the consumer will use to recognize a
duplicate, so it must travel with every event.

### Level 3: telemetry-rollup consumes idempotently

Build the rollup app. Draining the broker hands each not-yet-seen event to a handler that folds
it into the read store. The broker tracks the ids it has already delivered, so a redelivered
event is skipped before it reaches your handler. `GET /v1/rollup/{device_id}` returns the count
and the average, or a 404 for an unknown device.

Hint: this is the whole point of the assignment. At-least-once delivery means duplicates are
normal, not exceptional. Idempotency on the event id is what keeps the count honest when they
happen.

### Level 4: the gateway and graceful degradation

Add the gateway: `POST /readings` to ingest, and `GET /bff/device/{device_id}` to the rollup
through the resilient client. When the rollup service is down, the dashboard returns a clear
note with a null summary, status 200, rather than hanging or failing hard.

Hint: the timeout is the line that matters. A call with no timeout holds the request open when
the rollup is slow, and one slow service takes its callers down with it.

### Level 5: prove it, especially idempotency

Write the tests. Alongside per-service, contract, end-to-end, resilience, and observability
tests, write the one that defines the assignment: publish an event, drain it, then publish the
**same id again**, drain again, and assert the rollup is unchanged (the count and the average
stay put). A second useful assertion: a replay-only drain reports that it applied zero events.

Hint: build a fresh store and broker per test with a temp path, so tests do not leak state into
each other. Share one broker between the two services in the end-to-end test, the way
docker-compose shares one broker between the containers.

### Level 6: green gate

Run the quality gate and the smoke script.

```bash
poetry run pytest -q                     # all green
poetry run ruff check src tests scripts  # All checks passed!
poetry run mypy src                       # Success: no issues found
poetry run python scripts/smoke.py        # the end-to-end run
```

## Done when

- [ ] Two services, `telemetry-ingest` and `telemetry-rollup`, each with its own store, plus a
  gateway, in one Poetry project with a `src` layout.
- [ ] The contract lives in a `contracts` package both services import; inputs are validated by
  pydantic at the boundary.
- [ ] Ingest publishes a `reading-received` event carrying the id; the rollup consumes it into
  its own read store and never opens the ingest store.
- [ ] `GET /v1/rollup/{device_id}` returns the count and the average, and a 404 for an unknown
  device.
- [ ] A **replayed event with the same id does not change the rollup**, proven by a test.
- [ ] The gateway degrades cleanly when the rollup service is down (a null summary with a note,
  status 200), and a call has a timeout.
- [ ] `pytest`, `ruff check`, and `mypy src` are all green, and `scripts/smoke.py` prints the
  rollup as `count 3, average_value 21.47` and the same after a replay.

When every box is ticked, you have run the chapter's redesign over the telemetry domain: a
write path and a read path split into their own services, joined by an event, with the
idempotent consumer that keeps the split correct under at-least-once delivery. The worked
solution is in `solution-01.md` if you want to compare, but try first.
