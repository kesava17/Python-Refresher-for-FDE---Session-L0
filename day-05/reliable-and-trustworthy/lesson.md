# Dependable · Reliable and Trustworthy

> An enterprise-class application is judged on seven qualities: performant, scalable, reliable,
> maintainable, interoperable, trustworthy, and secure. The foundation lays the ground they rest
> on, and the chapters that follow build them one at a time.
>
> **This chapter builds two that are one job: reliable and trustworthy.** We have made the app fast,
> scalable, maintainable, and, in the last chapter, interoperable. Now we make it *dependable*: it
> holds up on real input, we can prove it holds up, and we keep proving it while it runs.

This is the master chapter for the Dependable topic, and you can read it on its own. Interoperability
gave the service clean boundaries to the outside world. Those boundaries are exactly where a service
is now expected to keep a promise: to be up, to be fast enough, to not lose data, to recover when a
dependency fails. This chapter is about making and keeping that promise. It joins two qualities that
are meaningless apart. **Reliable** is the promise itself, measured in numbers. **Trustworthy** is
how you set the number, prove you meet it, and watch it in production. You cannot claim one without
the other.

## Objective

After this chapter you can:

- Define reliability and trustworthiness, and explain why neither works without the other.
- Read the reliability metrics with their acceptable ranges, and say in plain terms what a number
  like "five nines" or "p99 under 200 ms" actually means for users.
- For each metric, describe what engineering must build to hit it, and demonstrate it.
- For each metric, describe what the architecture must decide to make it possible, with a scenario.
- Show how a real service is shaped by these, running each concern through the same loop: define the
  target, defend it by demonstration, and operate it with continuous monitoring.

## Coverage

The topic moves in a straight line, from meaning to build to proof:

1. **Define the two qualities** and how they interlock, for both the engineer and the solution
   architect.
2. **The metrics**, each with acceptable ranges and what the number means.
3. **Level 1, the engineering standpoint.** What each metric needs from the code, with a demo that
   demonstrates it.
4. **Level 2, the architecture standpoint.** What each metric needs from the system's shape, with a
   scenario.
5. **Level 3, the live lab.** How `reviews-insight` is shaped by all of it, running every scenario
   through define, defend by demonstration, and operate with continuous monitoring.

At the end there is a recap, a pointer to the live lab, and two offline assignments. Alongside this
chapter is a `demos/` folder of short runnable scripts. Wherever you reach a **Try it** note, run the
named script. As before it is its own small Poetry project: `poetry install` once, then `poetry run
python <name>.py` (or `poetry run pytest <name>.py` for the tests). Watch for the **enterprise lens**
(why an idea matters in production) and the **common trap** (a mistake that is easy to miss).

---

## Reliability and trustworthiness: two qualities, one job

### Reliability is the promise, in numbers

**Reliability** is the property that a running application keeps producing correct results, stays
available, and does not lose or corrupt data, under real conditions: when a dependency it calls is
slow or down, when it has been running for weeks, and when the load is many times the demo. The key
word is *running*. Earlier we made the code correct in the small (types, memory, safe structures,
honest errors). Reliability in the large asks a different question: not "is this answer correct" but
"does this service keep giving correct answers, and stay up, when things around it go wrong."

Because it is about the running whole, reliability is **measured, not asserted**. "It is reliable" is
not a statement you can check. "It serves 99.9 percent of requests successfully, p99 under 300 ms,
loses no accepted record, and recovers in under five minutes" is. The metrics section below is that
vocabulary of numbers.

### Trustworthiness is how you set, prove, and watch the number

**Trustworthiness** is the discipline that turns a reliability number from a hope into a guarantee.
It has three moves, and they recur through the whole chapter:

- **Define.** Agree the acceptable target up front and write it down: the service level objective
  (SLO). A target nobody set is a target nobody can be held to.
- **Defend.** Demonstrate that the service meets the target, with evidence: a test, a benchmark, a
  fault-injection run, a soak. Proof before it ships.
- **Operate.** Keep proving it while it runs, with continuous monitoring: the signals, the
  dashboards, and the alert that fires when the target is at risk.

Trustworthiness is not a separate feature bolted on at the end. It is the loop you wrap around every
reliability metric: **define the target, defend it by demonstration, operate it with monitoring.**

### Why they are interconnected

Reliability without trustworthiness is an unproven claim: fragile confidence that works until the day
it does not. Trustworthiness without reliability is proving the wrong thing: a green dashboard over a
service that falls over on the first real fault. They are two halves of one job. Every metric in this
chapter lives inside the define, defend, operate loop, and that loop is exactly trustworthiness
applied to reliability. That is why we teach them together, and it is the shape of the live lab at
the end.

### Why both an engineer and a solution architect must own it

Dependability is the one quality neither role can hold alone, because a reliability metric has a line
on both sides of a contract:

- The **solution architect** sets the target and the shape: the SLO the business is promised, the
  redundancy, the topology, the delivery guarantee, the deployment and recovery strategy. They own
  *what dependable means here* and *how the system is arranged to allow it*.
- The **engineer** builds to that target and emits the signals that prove it: the timeouts, the
  idempotency, the health endpoints, the metrics and logs. They own *the code that hits or misses the
  number*.

The metric is the shared contract between them, and it fails at the seam whenever one side assumes
the other has it. Two failure modes name that seam:

- **The band-aid.** Engineering ships a call that can fail and shrugs, "the platform will retry it."
  If the operation is not idempotent, the retry runs it twice; on the money track it double-charges.
  A concern that had to be co-owned was offloaded, and the offload made the bug.
- **The premature build.** Engineering builds a retry queue before architecture has fixed the
  delivery guarantee and the backpressure policy, then tears out the wrong thing later.

The rule for the rest of the chapter: **architecture sets the targets and shapes, engineering builds
to them and emits the signals, and the product carries the evidence.** You will see both columns
filled for every metric.

---

## The metrics, and what the numbers mean

You cannot design for a target you have not stated, and you cannot state one without knowing what the
number means. Here is each reliability metric, its acceptable ranges, and what a given value actually
buys you.

### Availability: the nines

Availability is the fraction of time the service is up and serving correctly. It is quoted in
"nines," and each extra nine is roughly ten times harder and more expensive than the last.

| Target | Name | Downtime per year | Per month | Per day | Who aims here |
| --- | --- | --- | --- | --- | --- |
| 99% | two nines | 3.65 days | 7.3 hours | 14.4 min | internal tools, batch jobs |
| 99.9% | three nines | 8.8 hours | 43.8 min | 1.44 min | a typical business service |
| 99.99% | four nines | 52.6 min | 4.4 min | 8.6 s | important customer-facing service |
| 99.999% | five nines | 5.26 min | 26 s | 0.86 s | critical infrastructure (payments, telecom) |

**What it means.** Five nines means the service may be unavailable for at most about five minutes
across an entire *year*. That is extraordinarily hard: it requires full redundancy, automatic
failover, and no manual step anywhere in recovery, because a single human paging and logging in
already costs more than five minutes. Most business applications target three or four nines. The
honest engineering move is to pick the lowest number the business actually needs, because each nine
multiplies the cost.

### Latency: percentiles, not averages

How fast the service responds. Never state this as an average, because an average hides the slow
requests that hurt most. Use percentiles: p50 (the median), p95, p99, and p99.9.

**What it means.** "p99 = 200 ms" means 99 of every 100 requests finish within 200 ms and the slowest
1 percent take longer. That slow 1 percent is not nothing: at a million requests a day it is ten
thousand real requests, often the users with the most data. Acceptable ranges depend on the surface:
for an interactive API, p50 under 100 ms, p95 under 300 ms, and p99 under about 1 second are healthy;
a batch or reporting path can be far slower. The tail (p99, p99.9) is where reliability problems
show up first, so it is the number to watch.

### Success rate and the error budget

The fraction of requests that succeed, stated as an SLO like "99.9 percent of requests succeed over
30 days." The part you are allowed to fail is the **error budget**.

**What it means.** At 99.9 percent over a million requests a month, you may fail about a thousand
before you breach. That budget is a tool, not just a limit: while there is budget left you can ship
features; when it is nearly spent you stop shipping and fix reliability instead. It turns "how
reliable is reliable enough" from an argument into a number both roles agreed to.

### Throughput and capacity headroom

The sustained load the service handles while still holding its latency and success SLOs, measured in
requests per second (or rows per second for a pipeline).

**What it means.** The important number is not the maximum; it is how much headroom you keep. The
rule of thumb is to run at 60 to 70 percent of measured capacity, so a traffic burst or the loss of
one instance still fits. A service run at 100 percent of capacity has no room for the next spike, so
the next spike is an outage.

### MTBF and MTTR, and how they make availability

**MTBF**, mean time between failures, is how long the service runs on average before it fails (hours,
days, months). **MTTR**, mean time to recovery, is how long it takes to get back to healthy. They
combine into availability:

> Availability = MTBF / (MTBF + MTTR)

**What it means.** Recovery time matters as much as failure rate, and often more, because everything
fails eventually. Cutting MTTR from one hour to one minute raises availability far more cheaply than
doubling MTBF. Acceptable ranges: well-run services target automated recovery in minutes; the
industry's elite-performer benchmark for restoring service is under one hour. Design for fast
recovery first, rare failure second.

### Durability, RPO, and RTO

**Durability** is the probability that data you have accepted is never lost or corrupted, also quoted
in nines. Cloud object stores advertise eleven nines, meaning you would expect to lose about one
object in a hundred billion per year. **RPO**, recovery point objective, is the most data you can
afford to lose in a disaster. **RTO**, recovery time objective, is how long a full restore may take.

**What it means.** For our service, durability means no accepted review is ever silently dropped or
duplicated. RPO and RTO are business decisions with sharp edges: on the money track RPO is zero (lose
no committed transaction) and RTO is tight; on the telemetry track an RPO of five minutes may be
fine. RPO drives how often you back up or replicate; RTO drives how the recovery is designed.

### Delivery metrics: the reliability of change

Reliability is not only about the running service; it is also about how safely you change it. The
four widely used delivery metrics are deployment frequency, lead time for a change, **change failure
rate** (the fraction of deploys that cause a problem, with an elite benchmark under 15 percent), and
time to restore service.

**What it means.** A service that ships small changes often, fails less than 15 percent of the time,
and recovers in under an hour is more dependable than one that rarely changes and breaks hard when it
does. This is where trustworthiness and deployability meet reliability: safe, frequent, reversible
change is itself a reliability property.

**Enterprise lens.** These numbers are how reliability becomes a line in a contract instead of a
feeling. "It is reliable" cannot be reviewed or promised. "99.9 percent availability, p99 under
300 ms, RPO zero, MTTR under five minutes, change failure rate under 15 percent" can be promised,
measured, and defended.

---

## Level 1: Each metric from the engineering standpoint

For each metric, this is what the code must do to hit it, and a demo that demonstrates it. This is
the "build" half of the contract, and the resilience patterns are its vocabulary.

### How Python supports reliable applications

Reliability is not something you write from scratch every time. Python gives you language constructs
built for it, and a mature ecosystem of libraries that package the common patterns. The rest of this
level builds the core of these by hand so you understand what each one does; in production you reach
for the tools below.

**Built-in language constructs.** The language itself carries a lot of the load:

- `try / except / else / finally` for graceful failure and guaranteed cleanup (a connection is closed
  whether or not the call raised).
- `contextlib` and `@contextmanager` with the `with` statement, to make setup and teardown safe.
- `asyncio.gather(..., return_exceptions=True)`, so one failed task does not bring down a whole
  concurrent batch.
- `typing` plus `@dataclass(frozen=True)`, for static type analysis and immutable values that cannot
  be mutated into a bad state.
- `logging` and `warnings`, for structured logs and deprecation signals.

**Type safety, checked before the code runs.** A type hint is only a comment until a checker enforces
it. `mypy` in strict mode reads the hints and fails the build on a type error, moving a whole class of
failure out of production and into your editor. It is the cheapest reliability win there is, which is
why the gate in Level 2 runs `mypy` strict. `pydantic` (below) does the same kind of check at runtime,
on data arriving from outside.

**Testing and contracts, to prove behavior.** `pytest` is the base. `hypothesis` generates edge-case
inputs automatically to find the boundary bugs you would not think to write by hand. `icontract` and
`deal` let you state preconditions, postconditions, and invariants that are checked at runtime.
Together they turn "it worked on my one example" into "it holds across many inputs, and it states its
own rules."

**Resilience and fault tolerance.** `tenacity` (retry with exponential backoff and jitter), `stamina`
(a production wrapper over tenacity for HTTP and API clients), `pybreaker` (the circuit breaker
pattern), and `aiolimiter` (rate limiting and concurrency throttling). These are the resilience-kit
patterns of this level, packaged and tested.

**Data validation.** `pydantic` parses and validates data at the boundary from your type hints,
dropping malformed input before it reaches your logic. `pandera` validates dataframe schemas, value
ranges, and types for pandas or Polars pipelines. `great_expectations` checks data quality, freshness,
and completeness across an ETL process.

**Observability.** `opentelemetry` for standardized distributed traces, metrics, and logs across
services; the `prometheus_client` to expose counters, gauges, and histograms; and `structlog` for
structured, context-rich JSON logs. These are the Operate step of Level 3, done with standard tools.

**AI output reliability (awareness, for the work this course feeds).** When the service calls a model,
the same discipline applies to its output: `guardrails-ai` and `instructor` enforce a JSON schema on a
model's response, while `deepeval`, `ragas`, and `trulens` measure hallucination rate and answer
quality. Structured, validated, and measured: reliability applied to a probabilistic dependency.

**The ecosystem at a glance.**

| Focus area | Key libraries | Primary reliability benefit |
| --- | --- | --- |
| Fault tolerance | tenacity, stamina, pybreaker | handles transient failures, prevents cascading crashes |
| Data integrity | pydantic, pandera, great_expectations | blocks bad input, enforces structural consistency |
| Type safety | mypy, typing | catches a class of bug before the code runs |
| Edge-case testing | pytest, hypothesis, icontract | finds hidden boundary conditions before production |
| Observability | opentelemetry, prometheus_client, structlog | lowers MTTR through tracing and visibility |
| AI output safety | guardrails-ai, instructor, deepeval | enforces schemas, mitigates hallucinations |

With that map in hand, the rest of this level builds the core mechanisms by hand, one metric at a
time, so you understand what a library does before you depend on it.

### 1.1 Availability: timeouts, fallback, and honest readiness

Availability is lost most often not when a dependency crashes, but when it gets slow and the code
waits forever. Engineering hits the availability number with three things: a timeout on every
outbound call, a fallback so a failed call degrades instead of failing the whole request, and a
readiness endpoint that tells the truth about capacity.

```python
import httpx

# A timeout turns "wait forever on a slow dependency" into "fail fast and decide what to do."
async def enrich(review: dict, client: httpx.AsyncClient) -> dict:
    response = await client.post("http://enrichment/insight", json=review, timeout=1.0)
    return response.json()


async def enrich_or_degrade(review: dict, client: httpx.AsyncClient) -> dict:
    try:
        return await enrich(review, client)
    except (httpx.TimeoutException, httpx.HTTPError):
        # The enrichment is slow or down. The review is still useful without it, so we serve it
        # plain rather than failing the whole request. This is graceful degradation.
        return {**review, "insight": None, "enriched": False}
```

```python
@app.get("/health")   # liveness: is the process running at all?
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")    # readiness: can it actually serve right now?
def ready() -> dict:
    # A stuck-but-alive process must fail readiness, so the platform stops routing to it and can
    # replace it. A health check that only proves the process is alive will call a hung service ok.
    if worker_pool.free() == 0:
        raise HTTPException(status_code=503, detail="no free workers")
    return {"status": "ready"}
```

> **Try it.** Run `poetry run pytest demo_degrade_on_timeout.py -v`. A mock enrichment that times out
> is injected, and the service is asserted to return the review un-enriched rather than hang or
> raise. The availability of the core path is defended against a slow dependency.

### 1.2 Latency: control the tail

To hold a p99 target, engineering keeps slow work off the request path and bounds every wait: a
timeout caps the worst case, a cache avoids repeat work, connection pooling avoids per-call setup,
and asynchronous I/O keeps one slow call from blocking others. This is also where the Interoperable
lesson pays off: an N+1 query pattern is a classic p99 killer, and batching fixes it.

> **Try it.** Run `poetry run python demo_latency_percentiles.py`. It times many calls and prints
> p50, p95, and p99, then shows how one slow dependency lifts only the tail while the average barely
> moves, which is why you watch percentiles, not the mean.

### 1.3 Success rate: validate, retry safely, and break the circuit

To hold a success-rate SLO, engineering rejects bad input early (the reliability-in-the-small work),
retries transient failures safely, and stops hammering a dependency that is down.

```python
import asyncio
import random

async def with_retry(call, attempts: int = 3):
    for attempt in range(attempts):
        try:
            return await call()
        except httpx.HTTPError:
            if attempt == attempts - 1:
                raise
            # Backoff (wait longer each time) plus jitter (a little randomness), so many clients do
            # not retry in lockstep and flatten the recovering dependency.
            await asyncio.sleep(2**attempt + random.random())


def submit_review(review: dict, key: str, store: dict) -> dict:
    # Idempotency key: running this twice has the same effect as once, so a retry is safe. Retry and
    # idempotency are two halves of one pattern; never build one without the other.
    if key in store:
        return store[key]
    store[key] = {"status": "accepted", "review": review}
    return store[key]
```

A **circuit breaker** completes the set: after a dependency fails enough times in a row, stop calling
it for a cooldown and fail fast, then let one call through to test recovery. It turns a long outage
into a cheap, fast rejection.

**Common trap.** A retry without idempotency. Retrying a call that already succeeded but whose
response was lost applies the effect twice: a double-counted review, or on the money track a
double charge.

> **Try it.** Run `poetry run python demo_retry_idempotency.py`. Without a key the retried operation
> is applied more than once; with the key it is applied exactly once despite the retries.

### 1.4 Throughput: stream, bound, and shed

To hold throughput with headroom, engineering streams in constant memory (the Performant lesson),
gives each dependency its own bounded pool (a **bulkhead**, so one slow dependency cannot starve the
rest), and sheds load early under overload (a fast rejection beats a slow collapse).

> **Try it.** Run `poetry run python demo_load_shedding.py`. Past a set concurrency it rejects new
> work immediately with a fast 429, and the accepted work keeps meeting its latency target instead of
> everything degrading together.

### 1.5 MTBF: no leaks, over the long run

MTBF is won by the reliability-in-the-small habits carried forward: no unbounded caches, no lingering
references, bounded memory, so the process does not slowly rot and fall over.

> **Try it.** Run `poetry run python demo_soak_flat.py`. It runs the core loop for many iterations
> and prints memory at intervals; the bounded version holds flat while an unbounded cache climbs,
> which is the difference between a service that runs for months and one that dies in days.

### 1.6 MTTR: restart fast, resume cleanly

To recover fast, engineering makes restart quick and *idempotent*: coming back up must not replay or
duplicate work in flight. A health-driven platform can then replace a bad instance automatically.

> **Try it.** Run `poetry run python demo_restart_resumes.py`. It kills the worker mid-batch and
> restarts it; because progress is checkpointed and writes are idempotent, it resumes with no lost or
> duplicated record.

### 1.7 Durability: idempotency keys and transactions

To lose no data across a crash, engineering writes before it acknowledges, wraps multi-step writes in
a transaction, and uses idempotency keys and deduplication so a redelivery cannot create a second
copy.

> **Try it.** Run `poetry run pytest demo_crash_in_the_middle.py -v`. It interrupts a write partway
> and asserts the store holds either the whole record or none of it, never a half, and never two.

### 1.8 Observe: the signals the code emits

A metric you cannot see cannot be defended in production, so the engineering standpoint has one job
beyond hitting each number: emit the signals that let the running system be watched. This is the code
half of the Operate step (Level 3). Three signals matter.

- **Structured logs.** One line per event, leveled (info, warning, error) and machine-readable (a JSON
  object, not free text), each carrying the `trace_id` from the Interoperable topic, so every line for
  a single request can be pulled together with one query.
- **SLI metrics.** The request rate, error rate, and duration (the RED signals), kept as in-process
  counters and exposed at a `/metrics` endpoint. These are the SLOs, measured.
- **Health signals.** A `/health` endpoint for liveness and a `/ready` endpoint that reflects real
  capacity, so the platform routes traffic only to instances that can actually serve.

In the live lab a single `observe` middleware does all three: it times each request, records the
SLIs, and logs a structured line with the trace id.

> **Try it.** Run `poetry run python demo_structured_logging.py`. It emits structured, leveled log
> lines carrying a `trace_id`; filter by one trace id and you see exactly that request's path, which
> is what you would do to debug it in production.

---

## Level 2: Each metric from the architecture standpoint

The same metrics, now from the other side of the contract: what the architecture must decide and
arrange so the engineering above can even reach the target. Each comes with a scenario.

### 2.1 Availability: addressed at many points

Availability is not one decision; it is redundancy applied at every layer where a single failure
could stop the service. Architecture works down the stack:

- **Redundant instances.** Run several instances of the app so no one process is critical.
  *Scenario:* one instance crashes; the load balancer stops routing to it and the others carry the
  traffic, with no user impact.
- **Spare capacity (N+1 sizing).** Size the fleet so it still meets the SLO with one instance gone.
  *Scenario:* at peak, losing an instance to a routine deploy still leaves headroom, so a deploy is
  never an outage.
- **Multiple availability zones.** Spread instances across separate zones so a zone-level failure
  (power, network) does not take all of them. *Scenario:* a zone goes dark; the other two zones keep
  serving and the SLO holds.
- **Multiple regions.** For the highest targets, run in more than one region, active-active or
  active-passive, so a whole region can be lost. *Scenario:* a regional outage; a global load
  balancer shifts users to the healthy region.
- **A load balancer reading readiness.** Route only to instances passing their readiness check, and
  pull the ones that fail. *Scenario:* an instance hangs; it fails readiness and is removed from
  rotation automatically.
- **A stateless app tier.** Keep session state out of the instance so any instance can serve any
  request and a dead one is replaced with no lost context. *Scenario:* the orchestrator kills and
  replaces a bad instance; no request was pinned to it, so users notice nothing.
- **Redundant dependencies.** The datastore and other dependencies need their own redundancy: a
  replica with automatic failover, more than one endpoint for a critical service. *Scenario:* the
  primary database fails; a standby is promoted and the app reconnects, within the SLO.
- **Degradation as an availability decision.** Decide the minimum viable service when a part is down,
  so "partly up" beats "all down." *Scenario:* enrichment is down; architecture's rule is to serve
  reviews un-enriched, so the core path's availability is unaffected.

Engineering builds the readiness endpoint and the degradation; architecture arranges the redundancy
so there is always somewhere healthy to route to.

### 2.2 Latency: addressed at many points

Holding a p99 target is about removing waiting from the request path, wherever it hides:

- **A cache tier.** Put a cache (for example Redis) in front of the store so repeated reads do not
  hit the database. *Scenario:* a hot product's reviews are read thousands of times a minute; served
  from cache, p99 drops from 400 ms to 20 ms.
- **Read replicas.** Send reads to replicas so they do not queue behind writes. *Scenario:* a heavy
  write burst no longer slows reads, because reads run on a separate replica.
- **Regional and edge deployment.** Put compute and a CDN near distant users so distance stops
  dominating. *Scenario:* far-region users saw p99 of two seconds from network latency alone; a
  regional deployment brings it back under the SLO.
- **Data locality.** Colocate compute with the data it needs, so a request does not cross the network
  many times. *Scenario:* moving the enrichment lookup into the same region as its data removes a
  cross-region hop from every call.
- **Precomputation and materialized views.** Compute expensive results ahead of time so the request
  just reads them. *Scenario:* the per-product summary is precomputed on write, so the read is a
  single fast lookup instead of an aggregation.
- **Off-path work.** Move anything not needed for the response onto a queue. *Scenario:* enrichment
  moves to an async worker; the submit response returns in tens of milliseconds and enrichment
  catches up behind it.

Engineering keeps the code fast and batches its queries; architecture decides where the data and the
compute live so the fast code is not left waiting on the network.

### 2.3 Success rate: addressed at many points

Architecture decides which failures may reach the user, and cuts them off at different layers:

- **Bulkheads.** Give each dependency its own bounded pool so one slow dependency cannot consume all
  the workers. *Scenario:* enrichment slows; because it has its own pool, the review list keeps its
  workers and keeps serving.
- **Decoupling with a queue or event stream.** Move a fragile dependency off the request path so its
  outage cannot fail the request. *Scenario:* the enrichment service is chronically flaky; the review
  is accepted and served immediately, and enrichment is applied asynchronously when it is healthy.
- **A delivery guarantee, chosen deliberately.** Decide at-least-once plus dedupe, or exactly-once,
  per data type. *Scenario:* telemetry uses at-least-once plus dedupe (cheap, a little duplication
  tolerated); money uses exactly-once (expensive, but no double effect).
- **Retry and circuit-breaking in the platform.** Centralize retry with backoff and circuit breaking
  in the gateway or service mesh, so every call gets them consistently. *Scenario:* a downstream
  flaps; the mesh breaks the circuit and fails fast for all callers, instead of each service
  reimplementing it differently.
- **A degradation policy and feature flags.** Pre-decide what to turn off under stress, and wire a
  flag to do it instantly. *Scenario:* under a partial outage, a flag disables the non-essential
  enrichment path so the essential submit and read paths hold their success rate.

Engineering builds the timeout, retry, idempotency, and breaker; architecture decides which
dependencies are isolated, which are decoupled, and what the delivery guarantee is.

### 2.4 Throughput: addressed at many points

Architecture decides how the system grows and how it protects itself under load:

- **Horizontal autoscaling.** Add instances automatically as an SLI (duration, queue depth) rises,
  and remove them when it falls. *Scenario:* a campaign lifts traffic; autoscaling adds instances as
  p99 climbs, holding the SLO.
- **Partitioning and sharding.** Split the data across nodes so no single node is the write
  bottleneck. *Scenario:* review writes are sharded by product, so ten times the writes spread across
  ten shards instead of overwhelming one.
- **Queue-based load leveling.** Put a queue between the front door and the workers so a spike is
  buffered, not dropped. *Scenario:* a burst arrives faster than it can be processed; the queue
  absorbs it and the workers drain it steadily.
- **Load shedding and rate limiting at the gateway.** Reject or throttle beyond capacity at the edge,
  cheaply, before the work reaches the backend. *Scenario:* traffic exceeds safe capacity; the
  gateway returns fast 429s to the excess, and the accepted load keeps meeting its SLO.
- **Caching and read/write splitting.** Absorb read load in a cache and on replicas so the primary
  handles writes only. *Scenario:* a viral product's reads are served from cache, leaving the primary
  free for the write path.

Engineering streams in constant memory and sheds load in the code; architecture decides the scaling
policy, the partitioning, and where the buffers and caches sit.

### 2.5 MTBF and MTTR: addressed at many points

Most outages come from change, so architecture owns how change reaches production and how the system
heals:

- **A progressive rollout.** Canary to a small slice, or blue-green with two environments, or a
  rolling replacement, so a bad change is caught before it reaches everyone. *Scenario:* a bad
  release fails the canary's health check and never reaches the fleet.
- **An automatic rollback gate.** Make going back the default when a deploy fails its post-deploy
  check. *Scenario:* a config typo ships; the gate fails and rolls back to the last good version in
  seconds, with no human.
- **Health-driven self-healing.** Let the orchestrator restart or replace an instance that fails its
  health check. *Scenario:* an instance wedges; it fails health, is killed and replaced
  automatically, and MTTR is seconds.
- **Backward-compatible migrations (expand, then contract).** Roll out a schema change in two steps so
  old and new code run side by side during the deploy. *Scenario:* a new column is added and
  backfilled first, and the old one is dropped only later, so no rollout step breaks the running
  version. (This is the deprecation lifecycle from the Interoperable lesson.)
- **Kill switches and runbooks.** A flag to disable a failing path instantly, and a written procedure
  for each known failure. *Scenario:* a dependency degrades; on-call flips the flag from the runbook
  and restores service before the fix ships.
- **Chaos practice.** Inject failures on purpose, in a safe window, to find weak spots (raising future
  MTBF) and rehearse recovery (lowering MTTR). *Scenario:* a monthly game-day kills a zone in staging
  and times the recovery, so the real event is a drill the team has already run.

Engineering makes restart fast and idempotent and emits the health signal; architecture owns the
rollout strategy, the rollback path, and the recovery practice.

### 2.6 Durability, RPO, and RTO: addressed at many points

Architecture decides how data survives failure, and the answer is a spectrum with a cost and a
recovery time attached:

- **Replication, synchronous or asynchronous.** Keep copies of the data on other nodes. Synchronous
  replication loses nothing on failover but costs write latency; asynchronous is faster but can lose
  the last few writes. *Scenario:* money uses synchronous replication (RPO zero); telemetry uses
  asynchronous (a few seconds of RPO, much cheaper).
- **Write-ahead durability before acknowledging.** Commit to a durable log or queue before telling
  the client "accepted," so a crash right after cannot lose an accepted write. *Scenario:* the
  process dies the instant after accepting a review; on restart the write is replayed from the log,
  and nothing is lost.
- **Idempotency and dedupe at the boundary.** Paired with an at-least-once guarantee, this removes
  the duplicates that at-least-once would otherwise create. *Scenario:* a redelivered message carries
  the same key, is recognized as a duplicate, and is dropped.
- **Backups with point-in-time restore, sized to RPO.** Back up often enough that the worst-case data
  loss meets the RPO. *Scenario:* continuous backup with a five-minute RPO means a total-loss event
  loses at most five minutes of the least critical data.
- **A disaster-recovery strategy, sized to RTO.** Choose along the cost-versus-recovery-time
  spectrum: backup-and-restore (cheapest, hours), pilot-light, warm-standby, or active-active (most
  expensive, seconds). *Scenario:* a region is lost; a warm standby in a second region takes over
  within the one-hour RTO, where active-active would have made it seconds.

Engineering writes durably, wraps multi-step writes in transactions, and dedupes at the boundary;
architecture sets the replication, the backup cadence, the delivery guarantee, and the DR strategy.

### 2.7 Observe: monitor, alert, and close the loop

Signals are only useful if someone watches them against a target and is told the moment it slips, and
arranging that is an architecture decision, the system half of the Operate step.

- **Dashboards against the SLO.** Chart each SLI against its objective, so "how are we doing" is a
  glance and the error budget is visible as it burns.
- **Burn-rate alerts.** Page a human when the error budget is burning fast enough to threaten the
  objective, not on every slow request. Alerting on noise trains people to ignore alerts, which is a
  reliability risk of its own.
- **Cross-service visibility.** Distributed tracing (for example OpenTelemetry) ties one request's
  path across services, and a synthetic check calls the deployed service on a schedule to catch a
  failure before a user does.

And the loop closes: an alert leads to a runbook, a runbook to fast recovery, and every incident
becomes a regression test, so a failure seen once in production is guarded against forever.
Engineering emits the signals (Section 1.8); architecture decides what is watched, what pages, and
what happens next.

### The handshake in one table

Reading both levels together, one row per concern, this is the contract the two roles sign:

| Concern | Architecture decides (target and shape) | Engineering builds (code and signal) | The product defends (evidence) |
| --- | --- | --- | --- |
| Availability | SLO, redundancy, failure domains | health and readiness, degradation | uptime versus SLO, a synthetic check |
| Latency | topology, cache tier, regions | timeouts, caching, batching | p99 dashboard against the SLO |
| Success rate | isolation, decoupling, delivery guarantee | validation, retry, idempotency, breaker | error-rate SLO, a fault-injection test |
| Throughput | scaling and partitioning policy | streaming, bulkheads, load shedding | a load test at target volume |
| MTBF | resource limits, isolation | no leaks, bounded memory | a soak run held flat |
| MTTR | rollout and rollback strategy | fast, idempotent restart | a timed recovery drill |
| Durability | replication, consistency, backups, DR | idempotency keys, transactions | crash-in-the-middle and DR-restore tests |

If a row is empty in the middle column it is a band-aid waiting to fail; if engineering is filling
the left column alone it is building ahead of a decision that is not final. A dependable service has
both columns filled, agreed before the code starts.

---

## Validating a change: A/B testing

A change is the most common cause of an outage, so the safest way to ship one is to prove it on real
traffic before it reaches everyone. **A/B testing** does exactly that: send some users the current
version (A, the control) and some the new version (B, the variant), measure both against the same
signals, and keep the winner. It is the define, defend, operate loop applied to a single change:
define the hypothesis and the guardrails, defend by measuring on a slice, operate by watching the
result and rolling forward or back.

The reliability of it lives in the guardrails. Alongside whatever business metric the experiment is
chasing, you watch reliability **guardrail metrics** on the B slice, the error rate, p99 latency, and
success rate, and a guardrail breach stops the experiment automatically. Because only a slice sees B,
a bad change is caught on a few users instead of all of them, and it is reversible by design.

This is how A/B testing improves both reliability and trust:

- **Reliability.** A smaller blast radius, so a bad change hits few rather than all; automatic
  rollback when a guardrail regresses; a lower change failure rate (the delivery metric from the
  metrics section); and an SLO that is protected during the rollout, not just after it.
- **Trust.** Decisions come from measured evidence rather than opinion, backed by enough samples to
  tell signal from noise (statistical significance); the reliability guardrails stay sacred while a
  business metric is chased; and the change leaves an auditable trail of what changed, what it did,
  and why it shipped.

**Enterprise lens.** A/B testing, canary releases, and feature flags are one idea at different grains:
expose a change to a little of production, measure it against reliability guardrails, and expand only
when the evidence says it is safe. Progressive delivery of this kind turns "we think this is better
and safe" into "we measured that it is, and it can be pulled in seconds."

---

## Level 3: The live lab, `reviews-insight` shaped by all of it

Now we put it on the running service. `reviews-insight` takes reviews over its versioned API and
calls an external enrichment service for each one. We take four concrete scenarios and run each
through the same loop the whole chapter has been building toward: **define** the target, **defend** it
by demonstration, and **operate** it with continuous monitoring. This loop is trustworthiness applied
to a reliability metric, and it is exactly what shapes the code.

Before the scenarios, the tool that guards every change is the **review checklist**, run over every
change whoever or whatever wrote it. The first twelve questions are correctness and quality; the last
five are the operability questions this topic adds:

1. Correct. 2. Readable. 3. Bad input. 4. At scale. 5. Leaks. 6. Error handling. 7. Testable.
8. Over-abstracted. 9. Assumptions. 10. Debuggable. 11. Production-ready. 12. Covered.
13. **Observable** (can you find the cause of a failure from the signals it already emits?).
14. **Degradable** (does it degrade when a dependency is down, not fail whole?).
15. **Reversible** (can the change be rolled back, and are migrations backward-compatible?).
16. **Retry-safe** (is the effect of a retried operation the same as running it once?).
17. **Bounded wait** (does every outbound call have a timeout?).

### Scenario A: the enrichment dependency is slow or down (availability, degradation)

- **Define.** The SLO is 99.9 percent availability on the core path. The rule: if enrichment is slow
  or down, serve the review un-enriched. The timeout on the enrichment call is one second.
- **Defend by demonstration.** A fault-injection test slows and then fails the enrichment mock, and
  asserts the API still returns the review with `enriched: false`, never hanging or erroring. The
  core path's availability is proven against a dead dependency.
- **Operate with continuous monitoring.** Emit the enrichment call's error rate and duration as
  metrics, show them against the SLO on a dashboard, and alert on the error-budget burn rate, so a
  real enrichment slowdown pages someone in about a minute instead of going unseen.

### Scenario B: the same review is submitted twice (durability, exactly-once)

- **Define.** Submitting a review with the same idempotency key twice must have exactly one effect.
  RPO for accepted reviews is zero.
- **Defend by demonstration.** A test submits the same key twice, once with a simulated lost response
  and retry, and asserts the store holds exactly one review and returns the same result both times.
- **Operate with continuous monitoring.** Count duplicate-key hits as a metric; a rising duplicate
  rate is an early signal that a client or the network is misbehaving, visible on the dashboard
  before it becomes a support ticket.

### Scenario C: the service runs for weeks (MTBF, no leak)

- **Define.** Memory and latency stay flat over a long run; no cache grows without bound.
- **Defend by demonstration.** A soak run drives the core loop for many iterations and shows a flat
  memory profile, next to an unbounded version that climbs, proving the bound is what holds MTBF.
- **Operate with continuous monitoring.** Export process memory and the duration SLI as metrics with
  an alert on a slow upward trend, so drift is caught days before it would exhaust the process.

### Scenario D: a bad change is deployed (MTTR, change failure rate)

- **Define.** Deploys go out as a canary with an automatic rollback, gated on the readiness endpoint.
  Target MTTR for a bad deploy is under a minute, with no human in the loop.
- **Defend by demonstration.** A rollback-gate demo ships a version that fails its readiness check
  and shows the gate returning traffic to the previous version automatically, rather than leaving the
  bad version live.
- **Operate with continuous monitoring.** A post-deploy synthetic smoke test and the deployment
  metrics (frequency, change failure rate) feed the dashboard, and every real incident becomes a new
  regression test, closing the loop back to Defend so the same failure cannot return unseen.

**Enterprise lens.** Notice that observability, deployment, and incident response are not extra
topics here; they are simply the **Operate** step of the loop. Structured logs carrying the
`trace_id` from the Interoperable lesson, metrics as the SLIs, traces, the canary and rollback, the
burn-rate alert, the incident-to-regression loop: each one is how a defined-and-defended target keeps
being met in production.

> **Try it.** Run `poetry run python demo_structured_logging.py` to see leveled, structured log lines
> carrying a `trace_id` so one request can be followed end to end, then `poetry run python
> demo_rollback_gate.py` to watch a failed deploy roll itself back. Together they are the Operate step
> made concrete.

The live lab walks all four scenarios with commands and expected output. When you finish,
`reviews-insight` does not just work; for every scenario it carries a defined target, a demonstration
that defends it, and a monitor that keeps it honest in production.

---

## Recap

Read the chapter back as one line of thought:

- **Reliability is the promise, in numbers.** Availability (the nines), latency (percentiles, watch
  the tail), success rate and the error budget, throughput with headroom, MTBF and MTTR (recovery
  time drives availability), durability with RPO and RTO, and the delivery metrics. Each has an
  acceptable range and a plain meaning, and picking the right number is itself an engineering
  decision.
- **Trustworthiness is the loop around each number:** define the target (the SLO), defend it by
  demonstration (test, benchmark, fault injection, soak), and operate it with continuous monitoring
  (signals, dashboard, burn-rate alert). Reliability without this loop is an unproven claim; the loop
  without reliability proves the wrong thing.
- **Engineering builds to the number** with timeouts, fallback, validation, retry with idempotency,
  bulkheads, load shedding, bounded memory, and transactions, and demonstrates each.
- **Architecture makes the number possible** with redundancy, topology, decoupling, scaling and
  partitioning, deployment and rollback strategy, and disaster recovery, and reasons about each with
  a scenario.
- **The live lab runs every scenario through define, defend, operate**, which is how the code is
  actually shaped, and where observability, deployability, and incident response show up as the
  Operate step.

The review lens for the whole topic: given a service, ask what each reliability target is and who set
it, which dependency can fail and what happens when it does, whether every outbound call has a
timeout and every write is retry-safe, whether you could find the cause of a production failure from
its signals, and, for each target, where the demonstration is that defends it and the monitor that
watches it. Those questions turn "it ran in the demo" into "it will hold up in production, and we can
prove it, continuously."

And the through-line: **dependability is co-owned.** The metric is the contract; architecture sets it
and shapes the system to allow it, engineering builds to it and emits the signals, and the product
carries the evidence. Neither role can hand the whole of it to the other; where one tries, that gap
is where the next incident happens.

**Next:** the [live lab](live-lab.md) shapes `reviews-insight` scenario by scenario, defining each
target, defending it with a demonstration, and wiring the monitoring that operates it. Then two
offline assignments run the same loop on IoT telemetry (durability and throughput under high volume)
and on financial transactions (no data loss and an exactly-once effect).
