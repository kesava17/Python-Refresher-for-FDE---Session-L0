# Microservices Architecture

> An enterprise-class application is judged on seven qualities: performant, scalable, reliable,
> maintainable, interoperable, trustworthy, and secure. The earlier chapters built these one at a
> time inside a single application. This chapter lifts the view to the whole system.
>
> **This chapter builds: a microservice architecture.** Microservices is the system-level
> architecture where all seven qualities have to be delivered together, across a set of services and
> the network between them. This chapter goes from the drivers (why you split at all), to the model
> (the shape of the system), to the engineering of each piece in FastAPI, to redesigning the running
> reviews-insight application into services front to back.

This is the master chapter for the Microservices Architecture topic, and you can read it on its own.
Everything before this taught you to make one application good. This chapter is about what happens
when one deployable is no longer enough, and you decide to split it into a system of smaller services
that ship, scale, and fail on their own. The hardest judgment here is not how to split. It is knowing
when not to, because a split you did not need is the most expensive mistake in this whole topic.

The roadmap is four moves, in order:

1. **The drivers.** Why teams leave a monolith, what a split buys, what it costs, and when the
   monolith is still the right answer.
2. **The architecture model.** What a microservice actually is, the reference picture of the whole
   system, synchronous versus asynchronous communication, and the rule that each service owns its
   own data.
3. **The pieces and their FastAPI engineering.** Each part of the system as an architecture decision
   plus the Python that builds it: the service, the contract, the gateway, resilient calls,
   messaging, observability, deployment, and tests.
4. **Redesign reviews-insight.** Take the monolith you already have and design it into two vertical
   slices behind a gateway, with a safe migration path.

The runnable demos for this topic live in the `demos/` folder, and each isolates one idea with the
standard library only. Run any of them with `poetry run python <name>.py` (for example
`poetry run python demo_two_services.py`). The live lab is where the whole system gets built: it
splits reviews-insight into two services you can run and test.

## Objective

By the end of this chapter you can explain why an application is split into services and, just as
important, when it should not be. You can describe the reference model of a microservice system,
name each piece, and build each piece in Python with FastAPI: a service, a versioned contract, a
gateway with a backend-for-frontend, resilient calls between services, asynchronous messaging with an
idempotent consumer, observability with a correlation id, and a Docker Compose deployment. Finally,
you can take a working monolith and redesign it into microservices as vertical slices, using a
strangler-fig migration that keeps the app live the whole way.

## Coverage

- The monolith, where it strains, and what a split buys and costs.
- Monolith-first, splitting by bounded context, the distributed-monolith anti-pattern.
- The frontend-monolith problem, micro-frontends, and vertical slices front to back.
- What a microservice is, the reference model, and synchronous versus asynchronous communication.
- Data per service, eventual consistency, and sagas.
- The engineering of each piece in FastAPI: service, contract, gateway, calls, messaging,
  observability, deployment, and tests.
- Redesigning reviews-insight into two services with a strangler-fig migration.

---

## Level 1: The drivers, why you split at all

Every earlier chapter improved one application. This level asks the question that sits underneath the
whole topic: should there be one application at all, or several? Microservices are a trade, not an
upgrade, so we start with the pressure that makes the trade worth taking, and we are honest about the
price.

### 1.1 The monolith you have, and why it is a good default

A **monolith** is an application whose capabilities all live in one deployable unit: one process to
run, one pipeline to ship, one database behind it. Our reviews-insight application is a monolith
today. It ingests product reviews, computes aggregates, and serves queries, all in one codebase.

A monolith is a good default, and you should not apologize for it. It is simple to build, simple to
run, and simple to reason about. There is one place to deploy, one place to debug, and no network
sitting between your own functions. A call from one part of the code to another is just a function
call: fast, reliable, and easy to trace. For most systems, most of the time, this is exactly right,
and it stays right for longer than teams expect.

**Enterprise lens.** The monolith is not the enemy. A well-structured monolith with clear internal
modules will outlast a badly split set of services. At scale, the failure mode is not "we stayed on
a monolith too long," it is "we split before we understood our own boundaries." Earn the split; do
not assume it.

**Common trap.** Treating "monolith" as a slur in a design review. When someone proposes services,
the first question is not "how do we split," it is "what pressure are we relieving that the monolith
cannot." If nobody can name it, the answer is to stay.

### 1.2 Where the monolith strains

Building on 1.1, a monolith does eventually strain, but the trouble is rarely size on its own. It is
when one part of the system holds the rest hostage. Two kinds of coupling are the tell.

The first is **coupling of change.** A one-line fix in one corner means redeploying the whole
application. One team's release is blocked by another team's unfinished work sitting in the same
build. The whole system is locked to one technology choice, because everything ships together.

The second is **coupling of failure and scale.** A single memory leak or crash in one feature can
take everything down, because it is all one process. One hot path forces you to scale the entire
application to serve it, not just the busy part, so you pay for capacity you do not need. And the one
shared database becomes a single point of contention that every feature fights over.

**Common trap.** Reaching for microservices to fix a messy monolith. If the boundaries are unclear
inside one process, they will be far worse across a network, where every unclear line becomes a slow,
failable call. Clean up the internal modules first, find the real seams, and split along those.

### 1.3 What a split buys, the costs, and the honest trade

Building on the strain in 1.2, here is what a split gives you in return. Every benefit is really the
same word: independence. The parts stop holding each other back.

- **Independent deploy.** Ship one service without redeploying the rest, so releases become small,
  frequent, and low-risk.
- **Independent scale.** Give more machines to the one busy service and leave the quiet ones small.
  You pay for what is hot, not for the whole application.
- **Team ownership.** A team owns a service end to end and moves at its own pace, behind a clear
  contract, without coordinating every change with everyone else.
- **Fault isolation.** One service failing is a degraded feature, not a dead system, if you designed
  for it.
- **Technology fit.** A service can use the language or store that suits its job, as long as it
  honours its contract.

Now the price, and it is real. The network is now in the middle of your application. Everything that
was a function call is a request that can be slow, fail, or arrive twice. You take on **latency and
partial failure** (calls cross the wire and can time out), **distributed data** (no single database,
so no easy join or transaction), **operational load** (many deployables to run, watch, and secure),
and **harder debugging** (one request now spans several services).

The honest trade, in one line: microservices exchange in-process simplicity for independence, at the
cost of distributed-system complexity. You only come out ahead when the independence is worth more
than the complexity it buys. That leads to the rule that governs the whole topic: **monolith first.**
Split only when a real pressure appears that you can name: a team that must ship independently, a path
that must scale alone, a fault that must be contained.

> **Try it.** Run `poetry run python demo_sync_vs_async.py`. You should see a synchronous call cost
> the full 0.20 seconds of waiting while an asynchronous handoff returns almost instantly, which shows
> the network timing that a split introduces into what used to be a plain function call.

### 1.4 When to split, and when not

Building on the trade in 1.3, the next question is where the split line goes. The unit of a good split
is a **business capability**, not a technical layer. Cut along what the system does, not how it is
coded.

The clean way to name a capability is a **bounded context**: a slice of the domain with its own data
and its own rules, such as "ingest reviews" or "serve aggregates." Each service should be one
capability, whole, so that a typical change touches one service and stays inside it.

The failure mode to avoid is the **distributed monolith**: a set of services that cannot deploy or
change without each other. You paid the full network cost and kept none of the independence, which is
the worst of both worlds. It is what you get when you split by technical layer instead of by
capability, for example a "controller service" and a "database service" that must always ship
together.

**Common trap.** Splitting by technical layer (a controller tier, a data tier) rather than by
capability. It scatters one business change across every service and couples them tightly, so you end
up with a distributed monolith wearing microservice clothes. Split so that a typical change touches
one service.

### 1.5 The frontend monolith, micro-frontends, and vertical slices

Building on the bounded-context idea in 1.4, here is where most "microservice" migrations stop half
done. Teams split the backend into services and leave one large frontend sitting in front of them
all.

That leftover frontend is a hidden bottleneck. Every backend team now waits on one frontend: one
codebase, one release train, one team. The independence you paid for at the back is lost at the
front, because a change to any single capability still has to ship through a shared user interface.

The completing idea is that a true microservice architecture splits **front to back.** If a capability
is a service, its slice of the user interface belongs with it, owned and deployed by the same team.
You decompose the interface along the same capability boundaries into **micro-frontends**, then
compose the fragments into one experience behind an **app shell**. The app shell hosts the fragments
and owns the shared concerns: routing, authentication, and the design system. Fragments can compose at
build time (packages, simple but it re-couples releases), at the edge (server-side assembly), or at
runtime (module federation, web components, or iframes for true independent deploy).

The result is the **vertical slice**: one team owns a capability front to back, the UI fragment, the
service, and its data, shipped together. The split is vertical (by capability), not horizontal (by
tier). That is what makes the independence real.

**Enterprise lens.** A monolithic UI over microservices re-couples them at the edge. The frontend
becomes the new single point of contention, and the organization quietly splits back into a "frontend
team" and a "backend team," which is exactly the horizontal divide microservices were meant to end.

**Common trap.** Runtime micro-frontends carry real cost: shared state across fragments, a versioned
design system, and duplicated dependencies. Like the backend split, do it only when a pressure
justifies it, and let the app shell absorb the shared concerns.

This level named the drivers and the traps. The next level turns to the model: what a microservice is,
how the pieces connect, and how each one is engineered in Python.

---

## Level 2: The architecture model and the pieces

Level 1 answered why and when to split. This level answers what you get when you do, and how you build
it. We start with the picture of the whole system, then walk each piece twice: the architecture
decision (the design), and the engineering (the FastAPI code that makes it real). A design without the
engineering is a diagram; engineering without the design is an accident. Every piece carries both.

### 2.1 What a microservice is

A microservice is defined by four properties that hold together. Drop any one and it becomes something
else.

- **Small and single-purpose.** It owns one capability and does it well. You can hold its whole job in
  your head.
- **Independently deployable.** It ships on its own, without a coordinated release of the whole
  system.
- **Owns its data.** It has its own store, and no other service reaches into that database.
- **Talks over a contract.** It is reached only through a defined interface, never by sharing
  internals.

**Enterprise lens.** "Independently deployable" and "owns its data" are the two that teams skip under
pressure, and skipping them is precisely how a set of services quietly becomes a distributed monolith.

### 2.2 The reference model

Building on the four properties in 2.1, here is how the pieces connect. Clients load an app shell that
composes the interface from micro-frontend fragments. Behind one **API gateway**, each service owns
its capability and its store. Services talk synchronously when a caller needs an answer now, and
through events over a **broker** when the work can happen later. A shared observability plane collects
logs, metrics, and traces, and configuration comes from the environment.

The request path reads left to right: clients, then the app shell and its fragments, then the gateway,
then the individual services, each with its own store. Alongside that synchronous path runs an
asynchronous plane where services publish and consume events, and a cross-cutting plane for
observability and config. Hold this picture; every piece below is one box in it.

### 2.3 Synchronous and asynchronous communication

Building on the reference model in 2.2, there are two ways for services to talk, and the choice comes
down to one question: does the caller need the answer right now?

**Synchronous** communication is request and response. The caller asks and waits for the reply. It is
simple and immediate, but it couples the two services in time: if the callee is slow or down, the
caller feels it directly. Use it when you need the answer to continue.

**Asynchronous** communication is events and messages. The caller publishes a message and moves on; a
consumer handles it later. It decouples the two services in time and absorbs load spikes, at the cost
of results that are eventual rather than immediate. Use it when the work can happen later.

**Common trap.** Making everything synchronous because it is easier to reason about, then watching one
slow service stall a whole chain of callers. Reach for async whenever a step does not need to block
the response.

> **Try it.** Run `poetry run python demo_two_services.py`. You should see an orders service call an
> inventory service over a real local HTTP port, which shows that a call between services is now a
> network request, not a function call.

### 2.4 Data per service, eventual consistency, and sagas

Building on the communication choice in 2.3, the rule that makes services independent is also the one
that makes them hard: each service owns its data. There is no single database holding the whole truth.

Each service keeps its own database or schema, and no other service touches it. That is what lets a
service change its data model without breaking anyone else. The price is that you lose the easy
transaction and join across services. State becomes **eventually consistent**: correct in a moment,
not in the same instant. When a single business action spans several services, it is coordinated by a
**saga**: a sequence of local steps, each with a compensating undo step, so that a failure partway
through can be rolled back by running the undos rather than by one atomic transaction that no longer
exists.

**Enterprise lens.** Data ownership is the decision that most shapes a microservice design. Get the
boundaries right and most calls stay inside one service; get them wrong and every request becomes a
distributed transaction, which is slow, fragile, and hard to reason about.

> **Try it.** Run `poetry run python demo_data_per_service.py`. You should see the query side build its
> own view purely from events, without ever opening the ingest store, which shows how state moves by
> event rather than by a shared table.

### 2.5 The service, in FastAPI

Now we move from the model to the engineering, piece by piece. The unit of the whole architecture is
the service: one capability, deployable on its own. In Python that is a small FastAPI app over a `src`
layout, with config read from the environment and a health endpoint the platform can poll.

```python
from fastapi import FastAPI

from common import observability
from common.config import settings

app = FastAPI(title="reviews-ingest", version="1.0")
observability.install(app, "reviews-ingest")   # adds /health and the correlation-id middleware

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

In the live lab, `reviews_ingest/main.py` builds its app through a `create_app` factory so a test can
inject a temporary store and broker while production uses the defaults from `settings`. The health
route matters because the gateway and the container platform poll it to route only to healthy
instances and to restart a sick one.

**Common trap.** A service that reads another service's database "just for now." That one shortcut
couples their data models permanently. Reach only through the contract.

### 2.6 The contract, in pydantic

Building on the service in 2.5, a service is only ever seen through its interface, and that interface
is a promise you version and keep. The architecture decision is a versioned, validated boundary; the
engineering is pydantic models plus a versioned route, from which FastAPI generates an OpenAPI schema
for free.

```python
from pydantic import BaseModel, Field

class ReviewIn(BaseModel):
    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=1)

@app.post("/v1/reviews", status_code=201)
def create_review(review: ReviewIn) -> ReviewCreated:
    review_id = store.save(review)          # already validated at the boundary
    return ReviewCreated(id=review_id)
```

The live lab keeps every shared shape in one `contracts` package: `ReviewIn`, `ReviewCreated`,
`Aggregate`, and the `ReviewReceived` event. Both sides depend on that one definition, so a wrong shape
is rejected before any service logic runs. A rating of 7 is rejected with a 422 at the boundary; the
versioned path `/v1` lets the contract grow without breaking callers; and `/docs` is generated from
the same code.

**Enterprise lens.** The contract is the real product boundary between teams. Backwards-compatible
changes (adding a field) are safe; breaking changes (removing or renaming) need a new version and a
deprecation window, because a caller you cannot see is depending on the old shape.

### 2.7 The gateway and the backend-for-frontend

Building on the contract in 2.6, many services need one front door, so clients see a single system and
cross-cutting concerns live in one place. The **API gateway** routes each request to the right service
and holds the concerns every service would otherwise repeat: authentication, rate limiting, and TLS
termination. A **backend-for-frontend** (BFF) is a thin endpoint that shapes one service's data for one
UI fragment, so the fragment makes one tailored call instead of orchestrating several services in the
browser.

```python
@app.get("/bff/dashboard/{product_id}")
def dashboard(product_id: str) -> dict[str, Any]:
    cid = observability.current_correlation_id()
    try:
        summary = resilient_get(
            f"{query_url}/v1/aggregates/{product_id}",
            timeout=settings.http_timeout, breaker=breaker, correlation_id=cid,
        )
    except CircuitOpen:
        return {"product_id": product_id, "summary": None, "note": "temporarily unavailable"}
    return {"product_id": product_id, "summary": summary}
```

The live lab gateway forwards a submitted review to reviews-ingest and serves the dashboard from
reviews-query, guarding both calls and degrading cleanly when a service is down.

**Common trap.** Putting business logic in the gateway. The edge routes and guards; it does not decide.
Logic in the gateway recreates the monolith at the front door.

### 2.8 Resilient calls: timeout, retry, circuit breaker

Building on the gateway in 2.7, when one service must call another synchronously, the call crosses the
network, so it has to assume the network fails. Three guards make the difference between a contained
failure and a cascade: a **timeout** on every call, a **retry with backoff** for transient errors, and
a **circuit breaker** that stops calling a dependency after repeated failures and lets it recover.

```python
import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0),
       retry=retry_if_exception_type(httpx.HTTPError), reraise=True)
def _call() -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:      # never without a timeout
        response = client.get(url, headers={"X-Correlation-ID": correlation_id})
        response.raise_for_status()
        return response.json()
```

In the live lab, `common/client.py` combines these into `resilient_get`, backed by a `CircuitBreaker`
class that opens after a threshold of failures and half-opens after a cooldown to try again.

**Enterprise lens.** The circuit breaker protects the caller, not the callee. It stops a healthy
service from throwing every request into a dead one and exhausting its own resources waiting for
replies that will never come.

**Common trap.** A call with no timeout. One slow dependency then holds a request open, threads pile
up, and a single slow service takes down its callers. A timeout is not optional.

> **Try it.** Run `poetry run python demo_timeout_retry.py`, then `poetry run python demo_circuit_breaker.py`.
> The first shows two failures retried to success and a slow call cut off at 0.3 seconds; the second
> shows the circuit opening on the third failure and half-opening after the cooldown, which shows the
> breaker protecting the caller.

### 2.9 Asynchronous messaging and idempotency

Building on the synchronous guards in 2.8, when work does not need to block the response, hand it off
through a broker and let a consumer do it later. The producer publishes an event and returns; the
consumer processes it on its own time, which absorbs spikes and survives a consumer being briefly down.

The catch is delivery. Real brokers give **at-least-once** delivery, which means an event can arrive
twice. So the consumer must be **idempotent**: processing the same event twice must give the same
result as processing it once. You get that by keying on the event id, using a set of processed ids or
an upsert.

```python
# producer: after saving a review, publish an event and return
broker.publish("review-received",
               ReviewReceived(id=review_id, product_id=review.product_id, rating=review.rating).model_dump())

# consumer: drain applies each not-yet-seen event exactly once, tracked by id
def drain_events(store: QueryStore, broker: FileBroker) -> int:
    def handle(event: dict[str, Any]) -> None:
        store.apply_review(event["product_id"], int(event["rating"]))
    return broker.drain("review-received", handle)
```

In the live lab, `common/broker.py` is a small file-backed stand-in that gives the two teaching
properties (at-least-once delivery, and an idempotent drain that skips a duplicate by id). In
production the `publish` and `drain` seam is swapped for a real broker; the interface stays the same.

**Enterprise lens.** At-least-once means duplicates will happen, not might. Idempotency (a processed-id
set, or an upsert keyed by event id) is what keeps the result correct when they do.

> **Try it.** Run `poetry run python demo_idempotent_consumer.py`. You should see a redelivered event
> skipped so the total lands at 22 rather than 32, which shows idempotency keeping an at-least-once
> stream correct.

### 2.10 Observability across services

Building on messaging in 2.9, one request now spans several services, so if you cannot follow it across
them you cannot debug the system. The architecture decision is to see across the whole system; the
engineering is a **correlation id** threaded through every call and stamped on every log line, plus a
health endpoint and metrics per service.

```python
@app.middleware("http")
async def add_correlation_id(request, call_next):
    cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    token = _correlation_id.set(cid)
    try:
        response = await call_next(request)
    finally:
        _correlation_id.reset(token)
    response.headers["X-Correlation-ID"] = cid
    return response
```

In the live lab, `common/observability.py` installs this middleware and the `/health` route on every
service, and its logger writes one structured JSON line per record carrying the id, so the logs of
every service share one id for a request. The gateway generates the id if the client did not send one
and forwards it on every downstream call.

**Common trap.** Plain text logs with no correlation id. When a request fails halfway across three
services, you cannot stitch the story together. The correlation id is what makes the separate logs one
story.

### 2.11 Deployment: one image per service

Building on observability in 2.10, independent deployment is a promise the packaging has to keep. Each
service ships as its own image with uvicorn as the entry point, and Docker Compose brings the whole
system up locally so a developer can see the services talk on a laptop.

```dockerfile
FROM python:3.12-slim
RUN pip install poetry
COPY . .
RUN poetry install --only main
CMD ["poetry", "run", "uvicorn", "reviews_ingest.main:app", "--host", "0.0.0.0"]
```

The live lab ships a `docker-compose.yml` that runs the gateway on port 8000, reviews-ingest on 8001,
and reviews-query on 8002, with config from the environment.

**Enterprise lens.** Local parity matters more with many services than with one. Compose lets a
developer bring the whole system up and watch it work, which is where most integration bugs surface
early, on a laptop rather than in production.

### 2.12 Testing services and the contract

Building on deployment in 2.11, with the network in the middle two things need testing: each service
alone, and the contract between services. FastAPI's `TestClient` runs a service in process with no
network, so tests stay fast and precise about which service broke.

```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_create_review_validates():
    ok = client.post("/v1/reviews", json={"product_id": "p1", "rating": 5, "text": "great"})
    assert ok.status_code == 201
    bad = client.post("/v1/reviews", json={"product_id": "p1", "rating": 7, "text": "x"})
    assert bad.status_code == 422        # the contract rejects rating 7
```

The live lab pairs per-service tests with a `test_contract.py` that pins the request and response
shapes both sides rely on, so a change on one side cannot silently break the other.

**Common trap.** Relying only on end-to-end tests. They are slow, flaky, and vague about which service
broke. Test each service alone, guard the contract with a contract test, and keep just a few
end-to-end checks for the critical path.

This level gave you the model and the engineering of each piece. The next level puts them all together
on the application you already have.

---

## Level 3: Redesigning reviews-insight into microservices

Level 2 built the pieces in isolation. This level assembles them into a redesign of the running
reviews-insight application. It is not a rewrite. It is a deliberate, safe redesign of a live app into
services, and it is where every decision from Level 2 gets applied to one concrete system.

### 3.1 The reviews-insight monolith today

Building on the pieces from Level 2, start by being fair to what exists. Today reviews-insight is one
deployable that does three jobs behind one process and one database: it ingests reviews, computes
aggregates, and serves queries. It is simple to run and reason about, and for its current size that is
a reasonable place to be. This redesign is a design exercise, not a rescue.

The pressure worth modelling is that two of those jobs want to behave differently. Ingest is
write-heavy and spiky. Query is read-heavy and latency-sensitive. They want to scale differently, and
they form a clean capability boundary. That is the seam to split along.

### 3.2 The target: two vertical slices behind a gateway

Building on the seam in 3.1, the target splits reviews-insight into two services, each owning its
store, behind one gateway, with the read model kept fresh by an event.

- **The reviews-ingest slice.** A submit-a-review UI fragment, the service that validates and writes
  to its own store, and a `review-received` event it publishes. One team, front to back.
- **The reviews-query slice.** A dashboard UI fragment, the service that serves aggregates from a read
  store it owns, updated by consuming the ingest event. Reads never touch the ingest database.

The request path is: client, app shell, gateway, then the two services with their own stores. There is
a versioned contract between them, a synchronous read path through the gateway, and an asynchronous
update path where reviews-query consumes the `review-received` event to rebuild its aggregates. Each
slice scales, deploys, and fails independently.

**Enterprise lens.** These are two vertical slices, each from UI fragment to service to store, behind
one app shell and one gateway. That is what turns "we have services" into "we have independence."

### 3.3 The migration: strangler fig

Building on the target in 3.2, you do not stop the world and rewrite. You grow the new services around
the monolith and retire it a slice at a time, staying live throughout. This is the **strangler-fig**
pattern, named for the vine that grows around a tree until it can stand on its own.

The steps: put a gateway in front of the monolith so traffic can be routed. Carve out reviews-query
first, because reads are the safest thing to move: point the read traffic at the new service, prove it
against the old path, and keep the old path as a fallback. Then move its data into the read store it
owns. Then repeat for reviews-ingest. The monolith shrinks with each extraction until it is gone.

**Common trap.** The big-bang rewrite: stop feature work, rebuild everything as services, and cut over
at the end. It is the highest-risk option, because there is no working system until the last day and
every problem lands at once. The strangler keeps a working app at every step, with a rollback at each
one.

**Enterprise lens.** The migration is itself an application of the seven qualities: each extraction is
small (maintainable), independently shipped (deployable), and gated by tests and a rollback
(reliable). You are not pausing quality to migrate; you are migrating by practising it.

### 3.4 The redesign decisions, mapped

Building on the migration in 3.3, here is every piece from Level 2 applied to reviews-insight. This
table is the design.

| Piece | Decision for reviews-insight |
| --- | --- |
| Vertical slices | two capabilities, each owned front to back: UI fragment, service, and store |
| Services | `reviews-ingest` (write) and `reviews-query` (read), split by capability |
| User interface | a submit fragment and a dashboard fragment, composed in one app shell |
| Contract | versioned REST, pydantic-validated, `/v1/reviews` and `/v1/aggregates` |
| Gateway | one front door, routing plus auth and rate limiting at the edge, and a BFF dashboard endpoint |
| Sync call | a guarded httpx client with timeout, retry, and circuit breaker where the gateway reads query |
| Async | a `review-received` event updates the read model through an idempotent consumer |
| Data | a write store and a read store, each private to its service |
| Resilience | timeouts, a circuit breaker, and a clear fallback note when a service is down |
| Observability | health per service, a correlation id across the call, structured logs |
| Deployment | one image per service, one `docker-compose.yml` for the whole system |
| Testing | per-service tests plus a contract test that guards the shared shapes |

This level took a working monolith and designed it into services front to back. The build turns that
design into runnable, verified code.

---

## The build

The live lab is where the redesign becomes runnable code. You split reviews-insight into two vertical
slices, `reviews-ingest` and `reviews-query`, behind a `gateway`, with a shared `contracts` package
and a `common` package (config, observability, broker, and the resilient client). Each service owns
its store, the read model is updated by consuming the `review-received` event idempotently, and the
gateway guards its calls and degrades cleanly when a service is down.

The proof is in the verification, run offline with no servers:

```bash
poetry run pytest            # 16 tests: per-service, the contract, resilience, and observability
poetry run ruff check src tests
poetry run mypy src
```

Then stand the whole system up together:

```bash
docker compose up --build    # gateway on 8000, reviews-ingest on 8001, reviews-query on 8002
```

Submit a review through the gateway and read the dashboard, and you can watch one request cross the
gateway into a service, an event flow to the read side, and the aggregate come back. Stop
reviews-ingest and the dashboard returns a clear note instead of hanging, which is the resilience
design doing its job. The system carries its own evidence: the tests pin the contract, `ruff` and
`mypy` keep it clean and typed, and Compose proves the services talk.

---

## Recap

Read the chapter back as one idea: **microservices trade in-process simplicity for independence, so
you split by capability into vertical slices owned front to back, give each service its own data and
contract, design for partial failure, and migrate a slice at a time, only when a real pressure makes
the trade worth it.**

- **The drivers.** A monolith is a good default; split only when you can name the pressure (independent
  deploy, independent scale, contained failure). The costs are latency, distributed data, operational
  load, and harder debugging.
- **The traps.** The distributed monolith (services that cannot ship without each other), splitting by
  technical layer instead of capability, and the frontend monolith that re-couples everything at the
  edge. The fix for the last one is micro-frontends and vertical slices.
- **The model.** A microservice is small, independently deployable, owns its data, and talks over a
  contract. Services communicate synchronously when the caller needs an answer now and asynchronously
  when the work can wait. Each owns its store, so state is eventually consistent and multi-service
  actions are coordinated by sagas.
- **The engineering.** A FastAPI service with a health route, a pydantic-validated versioned contract,
  a gateway with a BFF, resilient calls (timeout, retry, circuit breaker), idempotent messaging over a
  broker, a correlation id for observability, one image per service with Compose, and per-service plus
  contract tests.
- **The redesign.** reviews-insight becomes two vertical slices behind a gateway, migrated with the
  strangler-fig pattern that keeps the app live the whole way.

The review lens for the whole topic, the questions to ask of any proposed split: is there a named
pressure that justifies leaving the monolith? Is the split by capability, so a typical change touches
one service? Does each service own its data and talk only through its contract? Is every remote call
guarded with a timeout, and is every consumer idempotent? Can one request be followed across services
by a correlation id? And is the migration incremental, with a working system at every step? Those
questions turn "we built services" into "we built independence worth the complexity it cost."

**Next:** the [live lab](live-lab.md) splits reviews-insight into `reviews-ingest` and `reviews-query`
behind a gateway, verified with `poetry run pytest` (16 tests), `ruff`, `mypy`, and `docker compose up`.
Then two offline assignments apply the same architecture to IoT telemetry (a high-volume ingest and
rollup) and to financial transactions (a ledger with reconciliation), where the data is higher-volume
and the correctness stakes are higher.
