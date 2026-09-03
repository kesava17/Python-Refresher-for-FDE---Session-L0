# Demos cookbook: microservices architecture

Six short, standard-library demos, one per idea, in the order the session teaches them: a call
across a boundary, synchronous versus asynchronous, the two guards on a remote call (timeout
and retry), the circuit breaker, an idempotent consumer, and data per service. Each shows the
command, the output you should see (captured from a real run), and what to watch for.

Setup once:

```bash
cd demos
poetry install
```

The habit that makes the ideas stick: do not just read the output. **Change the input, predict
what will happen, run it, and check.**

---

## 1. `demo_two_services.py`: a call across a boundary

**Concept:** in a microservice system a call between services is an HTTP request, not a
function call. That boundary is what makes each service independently deployable, and what a
timeout has to guard.

```bash
poetry run python demo_two_services.py
```

**Output:**

```text
inventory service listening on 127.0.0.1:62700
orders service called inventory over HTTP -> {'sku': 'A-100', 'in_stock': 7}

The call crossed a real HTTP boundary, not a function call. That boundary is
what lets the two services deploy on their own, and what a timeout has to guard.
```

**Watch for:** a real port number, and a real HTTP response. In the monolith this was a
function call; now it is a request that can be slow or fail.

---

## 2. `demo_sync_vs_async.py`: wait, or hand off

**Concept:** a synchronous call blocks the caller until the callee returns; an asynchronous
handoff puts a message on a queue and returns at once, letting a worker do the work later.

```bash
poetry run python demo_sync_vs_async.py
```

**Output:**

```text
SYNCHRONOUS (the caller waits):
  got 36 after 0.20s of waiting

ASYNCHRONOUS (the caller hands off and returns):
  handed off in 0.0000s; the worker runs in the background
  worker finished later: {6: 36}
```

**Watch for:** the sync call costs the full 0.20s of waiting; the async handoff returns in
almost no time and the result appears later. Sync couples the two in time; async decouples
them.

---

## 3. `demo_timeout_retry.py`: the two guards on a remote call

**Concept:** a timeout so a call fails fast instead of hanging, and a retry with growing
backoff so a passing blip becomes a success.

```bash
poetry run python demo_timeout_retry.py
```

**Output:**

```text
A dependency that fails twice, then works:
  attempt 1 failed (transient failure); retrying in 0.1s
  attempt 2 failed (transient failure); retrying in 0.2s
  succeeded on attempt 3 -> ok

A slow dependency, bounded by a timeout:
  call exceeded 0.3s; we fail fast instead of hanging with it
```

**Watch for:** the retry hiding the first two failures, and the timeout cutting off the slow
call at 0.3s. A call with no timeout is the classic way one slow service takes its callers
down.

---

## 4. `demo_circuit_breaker.py`: stop calling a dead dependency

**Concept:** after a run of failures the breaker opens, so the caller fails fast instead of
throwing every request into a dead service; after a cooldown it half-opens to try again.

```bash
poetry run python demo_circuit_breaker.py
```

**Output:**

```text
three failures in a row open the circuit:
  failure 1: open=False
  failure 2: open=False
  failure 3: open=True
  the caller now fails fast, without even trying the dead dependency

after the cooldown, the circuit half-opens for a trial:
  open=False (a trial call is allowed again)
```

**Watch for:** the circuit flipping to open on the third failure, then half-opening once the
clock advances past the cooldown. The breaker protects the caller, not the callee.

---

## 5. `demo_idempotent_consumer.py`: duplicates are normal

**Concept:** at-least-once delivery means an event can arrive twice. An idempotent consumer
keys on the event id and skips the duplicate, so the running total stays correct.

```bash
poetry run python demo_idempotent_consumer.py
```

**Output:**

```text
consuming a stream that redelivers event 1:
  event 1: applied (count=1, total=10)
  event 2: applied (count=2, total=15)
  event 1: duplicate, skipped
  event 3: applied (count=3, total=22)

final: 3 events applied, total 22. The duplicate did not double-count,
because the consumer is idempotent on the event id.
```

**Watch for:** the redelivery of event 1 being skipped, so the total is 22, not 32. This is
the property that makes asynchronous messaging safe to build on.

---

## 6. `demo_data_per_service.py`: each service owns its store

**Concept:** each service keeps its own store; shared state moves by event, not by a shared
table. The read side never opens the write side's store.

```bash
poetry run python demo_data_per_service.py
```

**Output:**

```text
ingest store rows:      {1: ('p1', 5), 2: ('p1', 3)}
query average for p1:   4.0

The query side never opened the ingest store. It built its own view from the event,
which is what lets each service own and evolve its data independently.
```

**Watch for:** two separate stores, and a query view built only from events. This is the
boundary that lets each service change its data model without breaking the other.
