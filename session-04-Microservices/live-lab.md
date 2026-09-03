# Microservices Live Lab: Split reviews-insight Into Two Services

## What we're building

You already have `reviews-insight` as a monolith: one deployable that ingests reviews, computes
aggregates, and serves queries, all behind one process and one database. In this lab you meet that
same capability redesigned into a small system of services, and you drive it end to end on your own
laptop.

The project already exists in the coder repo, built by driving a coding agent against the design from
the deck. Your job here is not to retype it from a blank page. It is to understand the shape, run every
part, and prove the properties that make it a real microservice architecture and not a distributed
monolith. You read the code that is there, run the commands, and watch the system behave.

The redesign splits the monolith along one clean capability seam:

- **reviews-ingest** is the write side. It validates a submitted review, stores it in its own sqlite
  database, and publishes a `review-received` event. It never serves aggregates.
- **reviews-query** is the read side. It consumes those events into its own read store and serves the
  rollup for a product. It never opens the ingest database.
- **A gateway** is the single front door. It forwards a submit to reviews-ingest and shapes one tailored
  dashboard call to reviews-query, degrading cleanly when a service behind it is down.
- **A shared contract** is the one set of typed models both sides agree on, so a change on one side
  cannot silently break the other.
- **A common layer** holds the plumbing every service repeats: config from the environment, a
  correlation id and a health route, a file-backed event broker, and a guarded HTTP client with a
  timeout, retry, and circuit breaker.

The whole thing runs fully offline by default. A small file-backed broker stands in for a real message
broker, so the asynchronous path works with nothing external installed. In production that seam is
swapped for a real broker (for example Redis or a queue), and each service would be its own repository
and its own image. The interface stays the same, which is exactly why the swap is safe.

Work in order. Read the file each step names, then copy, paste, run. After each step there is one line
on what happened and why it matters.

Ground rules: every Python command runs through `poetry run`, and you run every command from inside the
`liveLab/` project folder. Nothing here needs the network.

---

## Step 0: Set up and run it offline

Install the dependencies, then run the three gates. If the suite is green, ruff is clean, and mypy is
strict-clean before you change anything, then any red later is something you did, not something you
inherited.

```bash
cd liveLab
poetry install
poetry run pytest
poetry run ruff check src tests
poetry run mypy src
```

You should see:

```text
16 passed
All checks passed!
Success: no issues found
```

The **16 tests** cover every seam of the system: the contract shapes both services rely on, the ingest
write path, the query read path and its idempotency, the gateway degrading when a downstream is down,
the correlation id, and the circuit breaker opening and recovering. ruff and mypy strict both pass.

Notice that not one of those tests opens a socket or reaches the network. FastAPI's `TestClient` runs
each service in the same process, and the broker is a file, so the full asynchronous path (ingest
publishes, query consumes) runs on a laptop with nothing installed but the Python dependencies.

**What happened.** The project is on version `1.0.0`, all 16 tests pass, and the two static gates are
clean. That is the "green before you start" baseline the rest of the lab builds on, and it proves the
system runs completely offline.

---

## Step 1: The shared contract both services depend on

Open `src/contracts/review.py`. This one file is the agreement. Read it, do not retype it.

It holds four pydantic models:

- `ReviewIn` is the submitted review, validated at the boundary: a non-empty `product_id`, a `rating`
  constrained to the range 1 to 5, and a non-empty `text`. A body outside those rules is rejected with a
  `422` before any service logic runs.
- `ReviewCreated` is the response when a review is stored: just the new `id`.
- `Aggregate` is the read model reviews-query serves: `product_id`, `count`, and `average_rating`.
- `ReviewReceived` is the one event. reviews-ingest publishes it after storing a review, and
  reviews-query consumes it. It carries exactly `id`, `product_id`, and `rating`.

```python
class ReviewReceived(BaseModel):
    """The event reviews-ingest publishes after storing a review, consumed by reviews-query."""

    id: int
    product_id: str
    rating: int
```

Why does one file matter so much? Because both services import from it. reviews-ingest builds a
`ReviewReceived` when it publishes; reviews-query reads the same fields when it consumes. The contract
is the real product boundary between the two teams. A backwards-compatible change (add an optional
field) is safe; a breaking change (rename or remove `rating`) would break the read side, which is
precisely why the contract has its own test.

`tests/test_contract.py` pins the shapes and runs one end-to-end path through a shared broker, so a
change on one side that violates the agreement fails the suite rather than surfacing in production.

**What happened.** You saw the single typed contract that lets two independently deployable services
exchange data safely, and why every shape lives in one place both sides depend on.

---

## Step 2: reviews-ingest, the write side

Open the two files under `src/reviews_ingest/`.

`store.py` is the write store, private to this service. It is a small sqlite table of submitted reviews,
and the comment on it says the important part out loud: no other service opens this database. The
`save` method inserts a validated review and returns its new autoincrement id.

`main.py` is the service. It builds a FastAPI app, installs the shared observability (the correlation id
middleware and `/health`), and exposes one route: `POST /v1/reviews`. Here is the handler:

```python
@app.post("/v1/reviews", status_code=201, response_model=ReviewCreated)
def create_review(review: ReviewIn) -> ReviewCreated:
    """Store a validated review and publish an event for the read side to consume."""
    review_id = store.save(review)
    broker.publish(
        "review-received",
        ReviewReceived(id=review_id, product_id=review.product_id, rating=review.rating).model_dump(),
    )
    log.info(f"stored review {review_id} for {review.product_id}")
    return ReviewCreated(id=review_id)
```

Read that flow top to bottom. The `review: ReviewIn` parameter means validation already happened at the
boundary, so by the time the body runs, the rating is known to be in range. The review is saved to this
service's own store. Then a `review-received` event is published to the broker and the handler returns
immediately. It does not wait for anyone to consume the event. That is the write side doing exactly one
job: accept, store, announce.

Notice what is not here. There is no aggregate computation, no read model, no call to reviews-query.
Ingest is write-heavy and spiky; it stays small and fast because it hands the follow-up work to an
event and returns.

**What happened.** reviews-ingest validates against the contract, writes to its own sqlite store, and
publishes one event, then returns without blocking, which is the whole write capability isolated behind
one route.

---

## Step 3: reviews-query, the read side

Open the three files under `src/reviews_query/`.

`store.py` is the read model, a sqlite table of `count` and `sum_rating` per product. It is built only
from events, never from the ingest database. The core method folds one review into a product's rollup,
inserting the first time and updating after:

```python
def apply_review(self, product_id: str, rating: int) -> None:
    """Fold one review into the product's rollup (insert or update)."""
    with self._connect() as db:
        row = db.execute(
            "SELECT count, sum_rating FROM aggregates WHERE product_id=?", (product_id,)
        ).fetchone()
        if row is None:
            db.execute(
                "INSERT INTO aggregates(product_id, count, sum_rating) VALUES (?, 1, ?)",
                (product_id, rating),
            )
        else:
            db.execute(
                "UPDATE aggregates SET count=?, sum_rating=? WHERE product_id=?",
                (row[0] + 1, row[1] + rating, product_id),
            )
```

`consumer.py` is the bridge from the event stream to that store. It is deliberately tiny: it hands every
not-yet-seen event to `apply_review` and returns how many it applied.

```python
def drain_events(store: QueryStore, broker: FileBroker) -> int:
    """Apply every not-yet-seen review-received event to the read store. Returns the count."""

    def handle(event: dict[str, Any]) -> None:
        store.apply_review(event["product_id"], int(event["rating"]))

    return broker.drain("review-received", handle)
```

`main.py` serves the read. `GET /v1/aggregates/{product_id}` drains any new events first so the answer
is fresh, then returns the rollup. If the product has no reviews, it raises a clear `404` rather than
guessing a zero. There is also a `POST /internal/drain` so you can consume events on demand. The
comment notes that in production a background worker would consume the stream continuously; for the lab,
draining on read keeps it simple and observable.

The idempotency lives in the broker, which Step 4 covers, but the effect shows here: a redelivered
event with an id the consumer has already applied is skipped, so the count does not move. That is what
lets the read side survive at-least-once delivery without double counting.

**What happened.** reviews-query builds its own read model purely from consumed events, drains new ones
before each read to stay fresh, and answers `404` for an unknown product, all without ever touching the
ingest store.

---

## Step 4: the common infrastructure every service shares

Open the four files under `src/common/`. This is the plumbing that would otherwise be copied into every
service. Read each one; you do not write any of it.

**`config.py`** reads settings from the environment with offline defaults anchored to the project root:
the two store paths, the broker path, the two service URLs, and an HTTP timeout. No secret is hard-coded,
and with nothing configured the whole system runs on a laptop, because every default points under the
project's own `data` folder.

**`observability.py`** is the shared cross-cutting layer. `install` adds two things to any service. First,
a middleware that stamps each request with a correlation id, taken from the incoming `X-Correlation-ID`
header or generated, and echoes it back on the response:

```python
cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
token = _correlation_id.set(cid)
```

Second, a `/health` route that reports liveness so the gateway and the platform route only to healthy
instances. Because every service installs the same middleware, one request that spans several services
can be followed end to end through logs that share one id.

**`broker.py`** is the file-backed message broker, the seam that lets the asynchronous path run with no
external service. `publish` appends one event as a line of JSON to a file. `drain` reads the events for a
topic and hands each to a handler exactly once, tracking processed keys in a sidecar `.seen` file:

```python
key = f"{topic}:{message['event'].get('id')}"
if key in seen:
    continue
handler(message["event"])
self._mark(key)
```

Those few lines give the two teaching properties that matter. Delivery is **at-least-once**: an event
sits in the file until a consumer drains it, and a redelivery is possible. The consumer is
**idempotent**: a duplicate event, keyed by its id, is recognized as already seen and skipped. In
production this class is replaced by a real broker, and `publish` and `drain` keep the same signatures.

**`client.py`** is the guarded HTTP client for calls between services. It bundles three defenses. A
`CircuitBreaker` counts failures to a dependency, opens after a threshold so the caller stops hammering a
dead service, and half-opens after a cooldown to let it recover. `resilient_get` wraps a real call with a
timeout, a bounded retry, and that breaker:

```python
def resilient_get(url, *, timeout, breaker, correlation_id, attempts=3):
    breaker.guard()                       # raise immediately if the circuit is open

    @retry(stop=stop_after_attempt(attempts), retry=retry_if_exception_type(httpx.HTTPError), reraise=True)
    def _call():
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, headers={"X-Correlation-ID": correlation_id})
            response.raise_for_status()
            return response.json()
    ...
```

The timeout is the line that keeps one slow dependency from holding a request open until threads pile
up. The breaker is what protects the caller, not the callee: it stops a healthy service from throwing
every request into a dead one and exhausting itself waiting.

**What happened.** You read the shared layer that makes each service small: config from the environment,
a correlation id and health for observability, a file broker that gives at-least-once delivery with an
idempotent consumer, and a client that survives a dependency being slow or down.

---

## Step 5: the gateway, the single front door

Open `src/gateway/main.py`. The gateway is one entry point in front of the two services, so a client
sees a single system. It has two routes.

`POST /reviews` forwards a submission to reviews-ingest, passing the correlation id along, and turns a
failure into a clear `502` instead of a hang:

```python
@app.post("/reviews", status_code=201)
def submit_review(review: ReviewIn) -> dict[str, Any]:
    cid = observability.current_correlation_id()
    try:
        with httpx.Client(timeout=settings.http_timeout) as client:
            response = client.post(f"{ingest_url}/v1/reviews", json=review.model_dump(),
                                   headers={"X-Correlation-ID": cid})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="ingest unavailable") from exc
```

`GET /bff/dashboard/{product_id}` is a small backend-for-frontend. It makes one tailored call to
reviews-query through the guarded client and, crucially, degrades cleanly when the read side is
unreachable:

```python
@app.get("/bff/dashboard/{product_id}")
def dashboard(product_id: str) -> dict[str, Any]:
    cid = observability.current_correlation_id()
    try:
        summary = resilient_get(f"{query_url}/v1/aggregates/{product_id}",
                                timeout=settings.http_timeout, breaker=breaker, correlation_id=cid)
    except CircuitOpen:
        return {"product_id": product_id, "summary": None, "note": "temporarily unavailable"}
    except httpx.HTTPError:
        return {"product_id": product_id, "summary": None, "note": "no data yet"}
    return {"product_id": product_id, "summary": summary}
```

Read the two `except` branches. When the downstream is down, the dashboard does not hang and does not
return a `500`. It returns a `200` with `summary` set to `null` and a short `note` explaining why. That
is graceful degradation: one dependency being down is a degraded feature, not a dead page. Notice too
what the gateway does not do. It holds no business logic. It routes, forwards the correlation id, guards
the call, and shapes the response. The edge decides nothing.

`tests/test_gateway.py` pins both behaviors: the dashboard returns a note when query is unreachable, and
a submit returns `502` when ingest is unreachable. Both assert the response arrives, so neither path
hangs.

**What happened.** The gateway is one thin front door that forwards writes, shapes one dashboard read,
and turns a downstream outage into a clear, fast, degraded answer instead of a hang or a crash.

---

## Step 6: run it end to end

Now watch the parts talk. The smoke script wires the two services over one shared temporary broker,
exactly as docker compose wires them over a real one, submits reviews through reviews-ingest, lets
reviews-query consume the events, and reads the aggregate back.

```bash
poetry run python scripts/smoke.py
```

You should see this exact output:

```text
health:
  reviews-ingest -> {'status': 'ok', 'service': 'reviews-ingest'}
  reviews-query  -> {'status': 'ok', 'service': 'reviews-query'}

submit three reviews for p1 (through reviews-ingest):
  rating 5 -> 201 {'id': 1}
  rating 3 -> 201 {'id': 2}
  rating 4 -> 201 {'id': 3}

reviews-query consumes the events and serves the aggregate:
  /v1/aggregates/p1 -> {'product_id': 'p1', 'count': 3, 'average_rating': 4.0}

a duplicate event does not double-count (idempotent consumer):
  /v1/aggregates/p1 -> {'product_id': 'p1', 'count': 3, 'average_rating': 4.0}

unknown product escalates to a clear 404, not a guess:
  /v1/aggregates/unknown -> 404
```

Walk the output against what you read. Both services report healthy. Three reviews for `p1` are stored
by reviews-ingest, each returning a `201` and its new id. Then reviews-query, which never saw those HTTP
calls, consumes the three events and serves the correct rollup: count 3, average 4.0 (the mean of 5, 3,
and 4). The next block republishes an event with an id the consumer already applied; the count stays at
3, because the consumer is idempotent. Finally, an unknown product returns a clear `404` rather than a
guessed zero. Every line of that run is one of the properties you read in Steps 1 to 5, proven at
runtime.

Optionally, bring the real system up in containers. One image runs three times with a different command,
which is the "one image per service" idea in the small:

```bash
docker compose up --build
```

Compose builds the image, starts the gateway on port 8000, reviews-ingest on 8001, and reviews-query on
8002, each with its own database volume and the two write and read services sharing the event broker
volume. Once they are up, both `GET /health` routes report ok, and you can submit through the gateway
and read the dashboard back. This is the local parity the lab is built to give you: the whole system on
a laptop, catching integration bugs before production. Press Ctrl+C to stop, and `docker compose down`
to clean up.

**What happened.** The full request path ran end to end: three writes through reviews-ingest, three
events consumed by reviews-query, a correct aggregate, a duplicate that did not double-count, and a
clean `404`, with the same system runnable in containers over docker compose.

---

## You should see

Run through this recap. If each line matches, the microservices lab is done.

- `poetry run pytest` reports **16 passed**, and `poetry run ruff check src tests` and
  `poetry run mypy src` are both clean, on version `1.0.0`.
- The whole suite runs fully **offline**: `TestClient` runs each service in process and the broker is a
  file, so no test opens a socket.
- **The contract (`src/contracts/review.py`)** is the one typed agreement both services import:
  `ReviewIn`, `ReviewCreated`, `Aggregate`, and the `ReviewReceived` event.
- **reviews-ingest** validates against the contract, writes to its own sqlite store, publishes one
  `review-received` event, and returns without blocking.
- **reviews-query** builds its read model only from consumed events, drains before each read, and
  returns `404` for an unknown product, never opening the ingest store.
- **The common layer** gives every service config from the environment, a correlation id and `/health`,
  a file broker with at-least-once delivery and an idempotent consumer, and a client with a timeout,
  retry, and circuit breaker.
- **The gateway** forwards a submit to reviews-ingest (a clear `502` when it is down) and shapes one
  dashboard read from reviews-query, returning `summary: null` with a note when the read side is down
  rather than hanging.
- **`poetry run python scripts/smoke.py`** prints healthy services, three `201` writes, the aggregate
  `{'count': 3, 'average_rating': 4.0}`, a duplicate that keeps the count at 3, and a `404` for the
  unknown product.
- **`docker compose up --build`** brings the services up healthy, each as its own container with its own
  store, sharing the event broker.

That is the redesign made real: one monolith split by capability into two independently deployable
services, each owning its data, talking through one versioned contract and one event, behind a single
gateway that stays up when a service behind it goes down. The proof is concrete. The contract and
end-to-end tests pass, the smoke run shows the write side and the read side agreeing through events, and
stopping a service makes the gateway degrade cleanly instead of hanging. In production the file broker
becomes a real broker and each service becomes its own repository and image, but the seams you ran here,
the contract, the event, the guarded call, and the health route, are exactly the ones that stay.
