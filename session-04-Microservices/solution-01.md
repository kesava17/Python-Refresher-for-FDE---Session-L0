# Solution 01 · Split telemetry-insight into asynchronous services

> The worked solution for Assignment 01. Try the assignment yourself first. This walks the
> reference build in `code/microservices-architecture/assignment01`, which is verified: 18
> tests pass, ruff and mypy strict are clean, and the smoke script runs end to end. There is no
> single correct set of file names; there is a correct shape, and one behaviour that must hold:
> a replayed event does not change the rollup.

The assignment is not really about the counting. It is about the seam between the write path
and the read path, and about keeping that seam correct when the transport delivers a message
twice. So the grading is on the design as much as the result: a trainee whose rollup is fed by
an event, owns its store, and skips a duplicate has learned the thing, even if their averages
differ from these.

## What a strong split shows (the rubric)

| Criterion | What earns the mark |
| --- | --- |
| **Two capabilities, split cleanly** | ingest (write) and rollup (read) are separate services, each with its own store. The rollup never opens the ingest store. |
| **A shared contract** | the request, response, and event shapes live in one `contracts` package both services import, validated by pydantic at the boundary. |
| **An event, not a shared table** | the rollup is fed by a `reading-received` event, so it can be rebuilt and can scale on its own. |
| **Idempotent consumer** | the consumer keys on the event id, so a redelivered event is skipped and the count does not double. |
| **Graceful degradation** | the gateway returns a clear note when the rollup is down, and every remote call has a timeout. |
| **Proven, not asserted** | a test replays an event and shows the rollup unchanged. |

The trap this assignment exists to catch is the consumer that trusts the transport. At-least-once
delivery is the honest default of most brokers, and a rollup that adds every event it receives
will over-count the moment one is redelivered. The discipline is to make the consumer
idempotent, so correctness does not depend on the broker never repeating itself.

## The reference build

The project mirrors the live lab, with the domain shifted to telemetry.

```
src/
  contracts/reading.py    ReadingIn, ReadingCreated, Rollup, ReadingReceived
  common/                 config, observability (correlation id, health), broker, client
  telemetry_ingest/       store.py + main.py: POST /v1/readings, store, publish reading-received
  telemetry_rollup/       store.py, consumer.py, main.py: consume idempotently, GET /v1/rollup/{id}
  gateway/main.py         POST /readings, GET /bff/device/{id}, degrades cleanly
tests/                    per-service, contract, end-to-end, resilience, observability, idempotency
scripts/smoke.py          the end-to-end run
```

**The write side.** `telemetry-ingest` validates a reading against `ReadingIn`, saves it to its
own sqlite store, and publishes a `reading-received` event carrying the id, the device id, and
the value. The publish returns at once, so ingest stays fast under a burst.

**The read side.** `telemetry-rollup` keeps, per device, the count and the sum of values. Its
consumer drains the broker: the broker hands over only the events it has not delivered before,
keyed on the event id, so a duplicate is skipped before it reaches the handler. The average is
the sum divided by the count, rounded, computed at read time. An unknown device returns a 404
rather than a guessed zero.

**The idempotency proof.** The key test publishes an event, drains it into the rollup, then
publishes the **same id again** and drains again, asserting the count and the average are
unchanged. That is the one behaviour the whole assignment turns on.

## The measured result

Running the smoke script end to end (three readings for one device, then a replay):

```text
telemetry-rollup consumes the events and serves the rollup:
  /v1/rollup/d1 -> {'device_id': 'd1', 'count': 3, 'average_value': 21.47}

a replayed event (same id) does not change the rollup (idempotent consumer):
  /v1/rollup/d1 -> {'device_id': 'd1', 'count': 3, 'average_value': 21.47}

unknown device escalates to a clear 404, not a guess:
  /v1/rollup/unknown -> 404
```

The replay line is the proof: after the same event is published again, the count stays at 3 and
the average stays at 21.47.

The full gate, from the `assignment01` folder:

```bash
poetry run pytest -q                     # 18 passed
poetry run ruff check src tests scripts  # All checks passed!
poetry run mypy src                       # Success: no issues found in 16 source files
```

## Why this is the right shape

Feeding the rollup by an event, rather than letting it read the ingest store, is what makes the
two services independent. The write side can change how it stores a reading, and the read side
can be rebuilt from the event stream, without either one reaching into the other's data. That
independence is the whole reason to split.

Keying the consumer on the event id is the small discipline that makes the asynchronous seam
safe. Without it, the split is correct only as long as the broker never repeats a message, which
is a promise no at-least-once broker makes. With it, correctness holds no matter how many times
an event is delivered.

## Going further (optional)

- Replace the file-backed broker with a real one (for example Redis) behind the same `publish`
  and `drain` interface, and confirm the tests still pass. The seam is designed for exactly this
  swap.
- Add a background consumer so the rollup updates continuously, instead of draining on read, and
  keep the idempotency guarantee.
- Add a per-device freshness check (the timestamp of the last reading folded in) so a stale
  device is visible in the rollup.
