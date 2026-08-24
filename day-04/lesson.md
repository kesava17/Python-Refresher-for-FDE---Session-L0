# Day 5 · Interoperable

> An enterprise-class application is judged on seven qualities: performant, scalable, reliable,
> maintainable, interoperable, trustworthy, and secure. Day 1 lays the foundation they rest on,
> and Days 2 to 7 build them one at a time.
>
> **This chapter builds: interoperable.** Day 1 set up the environment, and Days 2 to 4 made the
> app fast, reliable, and maintainable; today we connect it to the world, exposing interfaces
> other systems can use, consuming theirs, and where needed calling other languages in the same
> process.

This is the chapter for Day 5. You can read it on its own. The topic is what it means for a
program to work together with other programs, which is what the word "interoperable" means: able
to operate together. Almost no real application stands alone. It sits among other services and
other languages, and a large part of its usefulness comes from how cleanly it connects to them.
A program that does its own job perfectly but cannot talk to anything else has limited value in a
company, where dozens of systems have to cooperate.

There are two very different places where this connecting happens, and it helps to picture them
as two levels stacked on top of each other. The higher level is the **network boundary**: your
program and another program run as separate processes, often on separate machines, and they talk
by sending messages back and forth over the network. This is the level of web APIs. The lower
level is the **code boundary**: inside a single running program, Python code calls a function that
was written in another language, such as C, Rust, Java, or C#, with no network in between. This
is how much of the fast Python world is actually built. The popular numerical and data libraries
are a thin, readable Python surface sitting on top of a fast core written in a lower-level
language.

The plan of the chapter follows those two levels, and we go from the top down, because the higher
level is the one you meet first and the lower level is the one you reach for less often but need
to understand:

1. **Interfaces at the API level.** We start at the network boundary. First the single most
   important idea, that an interface is a promise you make to your callers, and then the common
   ways to expose one: REST, GraphQL, gRPC, and messaging, plus how you build an interface whose
   shape is checked automatically.
2. **Interop at the code level.** Then we go one level lower, into the same process, where Python
   calls straight into code written in another language. We cover why this pattern exists and how
   Python reaches into C, C++, Rust, Java, and .NET.
3. **Designing a safe boundary.** Finally, the design rules that apply to both levels: crossing
   any boundary has a cost and can go wrong, so we look at how to keep the crossings cheap and how
   to handle memory and errors across them.

After the three levels we put them together on the `reviews-insight` service from earlier days,
giving it a real interface and a fast native path, so the result is something you can run and
measure, not just a claim.

As you read, look for two recurring notes. The **enterprise lens** explains why an idea matters
once separate systems and separate teams have to work together. The **common trap** shows a
mistake that is easy to make when connecting systems, so you can catch it in your own code and
when you review someone else's.

Alongside this chapter is a `demos/` folder of short, runnable scripts, one per idea below.
Wherever you reach a **Try it** note, stop and run the named script and watch the idea for
yourself. The `demos/` folder is its own small Poetry project, so you run the demos the same way
as everything else in this course: from that folder, run `poetry install` once, then each **Try
it** is `poetry run python <name>.py`. (Day 5 uses a few installed packages, `fastapi` and
`httpx`, which `poetry install` pulls in for you.)

## Objective

After this chapter you can:

- Treat an interface as a contract: check incoming requests at the edge, put a version on it, and
  make it fail with a clear error.
- Explain, in plain terms, what REST, GraphQL, gRPC, and messaging are, and when each one fits.
- Build a small typed API whose request and response shapes are checked automatically at the
  boundary, and write the contract down as an OpenAPI schema with pydantic.
- Test an API by hand with a tool like Postman and automatically with a test client, and follow the
  REST and GraphQL design rules.
- Explain the two-language pattern and how Python calls into C, Rust, Java, and .NET code.
- Design a boundary that crosses in a few large steps, and reason about the cost of moving data,
  the GIL, and who owns memory.

## Coverage

Day 5 has three levels, and they move from the network down into the code:

1. **Interfaces at the API level.** The interface as a contract, REST in practice, the contract in
   code with pydantic and OpenAPI, GraphQL in practice, real-time with WebSockets and SSE, testing
   with Postman and a test client, API design dos and don'ts, gRPC, messaging, and webhooks, and what
   surrounds the API: identity and the gateway.
2. **Interop at the code level.** The two-language pattern, calling C and C++, Rust, Java, and
   .NET, why installed libraries ship pre-compiled as wheels, and the difference between extending
   and embedding.
3. **Designing a safe boundary.** Crossing in a few large steps, the cost of moving data, the GIL
   across the boundary, who owns the memory, translating errors, and tracing a request across
   services.

At the end there is a recap, a pointer to the live lab, and two offline assignments.

---

## Level 1: Interfaces at the API level

We begin at the higher of the two levels from the introduction, the network boundary, because it
is where most integration happens: your service exposes an interface, and other services call it
over the network. Before we look at any particular technology for doing this, we need the one idea
that sits underneath all of them. That idea is not REST or GraphQL or any tool; it is that an
interface is a **contract**. Everything else in this level is a way of writing that contract down.

### 1.1 The interface as a contract

Start with what a contract is here, in plain terms. An interface is a promise to everyone who
calls it. The promise says three things: these are the inputs I accept, this is the shape of what
I hand back, and this is how I behave. The important consequence is that once other teams have
written their own code against your promise, you can no longer change it casually, because their
code is relying on exactly what you said you would do. Three habits keep a contract trustworthy:

- **Validate at the edge.** Check every incoming request the moment it arrives, and reject bad
  input with a clear error before it ever reaches your real logic. The boundary is the place where
  you stop trusting the outside world, so it is the place to check.
- **Version deliberately.** Put a version into the contract, such as a `/v1` at the front of the
  URL or a version in a header. That way you can later ship a `/v2` with changes while `/v1` keeps
  working unchanged for the callers who still depend on it. Never quietly change what an existing
  version means, because that breaks callers who did nothing wrong.
- **Fail clearly.** When something goes wrong, return a specific, documented error and status code,
  not a generic "server error." A caller needs to be able to tell "you sent me a bad request" apart
  from "my server broke," so it can react in the right way.

**Retiring a version.** Versioning only helps if you can eventually turn the old one off without
breaking people. Do it on a lifecycle, not overnight. First **log who still calls `/v1`**, so you
know who would be affected. Then **announce the change** and mark the old version deprecated (the HTTP
`Deprecation` header is a standard way to signal it in each response). Give callers a clear
**timeline** to move. Only then return `410 Gone` for the retired version. Never switch a version off
with no warning.

**Enterprise lens.** The interface is the seam between two teams. A clear, versioned, checked
contract is exactly what lets two teams work on either side of it at the same time without
tripping over each other, and it is what stops one team's change from silently breaking another
team's system.

> **Try it.** Run `poetry run python demo_edge_validation.py`. A `pydantic` model with `rating`
> constrained to 1 to 5 accepts a valid review, then rejects `rating: 11` with a clear
> `ValidationError` at the moment of construction. That is validate-at-the-edge, before any of your
> logic runs.

Now that we know an interface is a contract, the next question is which style of contract to use.
The most common one on the web is REST, so we look at it first.

### 1.2 REST in practice

REST is the usual default for web APIs, the style most public web services follow. It is a set of
conventions, not a strict standard, and a few practical rules make an API that others find easy to
use.

**Name resources, not actions.** The URL names a thing (a noun), and the HTTP verb says what to do
with it. Design the paths around resources and collections:

```text
GET    /v1/reviews          # list reviews (a collection)
POST   /v1/reviews          # create a new review
GET    /v1/reviews/42       # read one review by its id
PUT    /v1/reviews/42       # replace review 42
PATCH  /v1/reviews/42       # update part of review 42
DELETE /v1/reviews/42       # remove review 42
```

A URL like `/v1/createReview` or `/v1/getReviews` is a sign you are naming actions instead of
resources. Move the action into the verb and keep the path a noun.

**Be stateless.** The server keeps no memory of a particular client between requests; each request
carries everything needed to handle it. That is what lets you run many identical copies behind a
load balancer, because any copy can handle any request (the production picture from Day 1).

**Use status codes honestly.** Every response carries a numeric status code with an agreed meaning.
Return the right one, and never a `200` with an error hidden in the body.

| Code | Meaning | When to use it |
| --- | --- | --- |
| `200` | OK | a successful read or update |
| `201` | Created | a POST that made a new resource |
| `204` | No Content | a successful DELETE, nothing to return |
| `400` | Bad Request | the request itself is malformed |
| `401` / `403` | Unauthorized / Forbidden | not logged in / not allowed |
| `404` | Not Found | no resource at that id |
| `422` | Unprocessable | the shape is right but a value is invalid |
| `429` | Too Many Requests | the caller is being rate-limited |
| `500` | Server Error | your code failed |

**Version the contract.** Put a version in the path (`/v1/...`) or a header, so you can ship a `/v2`
later while `/v1` keeps working for callers who still depend on it. Never change what an existing
version means.

**Page and filter large collections.** A list endpoint should not return everything at once. Accept
query parameters for paging and filtering, and return one page at a time:

```text
GET /v1/reviews?product_id=P100&limit=20&offset=40
```

**Make retries safe (idempotency).** An operation is idempotent when doing it again has the same
effect as doing it once. `GET`, `PUT`, and `DELETE` are naturally safe to retry; a plain `POST` is
not, because a retry could create a second copy. For a create that must be safe to retry, accept an
**idempotency key** (a unique id the client sends) and return the same result if you see that key
twice. This matters the moment a network is involved, because a request that looks like it failed
may actually have gone through.

REST tells you the shape of the contract. It does not, by itself, check that requests match it, or
write the contract down. In Python you get both for free, which is the next step.

### 1.3 The contract in code: pydantic and OpenAPI

The practical question is how to build a REST API in Python so the checking from Section 1.1 happens
automatically, and so the contract is written down in a form other teams and tools can read. The
answer is a **typed framework**: you declare the request and response shapes as types, the framework
validates incoming data against them at the edge, and it publishes the contract for you. `FastAPI`
with `pydantic` is the common choice.

**Design the request and the response, not just the request.** A contract has two halves: what you
accept, and what you return. Declare both as pydantic models. FastAPI validates the incoming body
against the request model, and with `response_model` it checks and documents what you send back.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="reviews-insight")


class ReviewIn(BaseModel):                        # the request contract
    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)               # 0 or 11 is rejected at the edge


class ReviewAccepted(BaseModel):                  # the response contract
    status: str
    id: int


@app.post("/v1/reviews", status_code=201, response_model=ReviewAccepted)
def submit(review: ReviewIn) -> ReviewAccepted:
    # By the time we are here, review is already valid.
    return ReviewAccepted(status="accepted", id=42)
```

A request that sends `rating: 11` never reaches the body of your function; the framework compares it
to `ReviewIn`, sees that 11 is outside the allowed range of 1 to 5, and returns a `422` on its own
with a message that names the bad field. This is the same "check input at the boundary" habit from
Day 4, applied here at the outermost boundary of all.

**The OpenAPI spec is the written contract.** From those models and routes, FastAPI generates an
**OpenAPI document**: a machine-readable description of every path, its request and response shapes,
and its status codes. It is served at `/openapi.json`, with an interactive page at `/docs`. That
document is the contract other teams build against and other tools read: you can import it into a
tool like Postman, feed it to a client-code generator, or check it in a test.

There are two ways to work with it. **Code-first** (what we do here): write the pydantic models and
let FastAPI produce the spec. **Design-first**: write the OpenAPI spec by hand, agree it with the
callers, then generate stubs and check your implementation matches. Design-first is worth the extra
step when another team needs the contract before your code exists.

> **Try it.** Run `poetry run python demo_rest_contract.py`. It builds a small FastAPI app and
> exercises it with a test client: `GET /health` returns `{"status": "ok"}`, a valid `POST
> /v1/reviews` returns `201`, a `rating: 11` returns `422`, and `GET /openapi.json` contains the
> `/v1/reviews` path. The versioned, checked contract is real and machine-readable.

REST with a typed framework covers the common case well, but it is not the only shape a contract can
take. The next section is a different one, built around letting the caller choose what it gets back.

### 1.4 GraphQL in practice

GraphQL is an alternative where the **client shapes the query**. Instead of many fixed endpoints,
there is usually one endpoint, and the caller sends a query that names exactly the fields it wants
and gets back exactly those, no more and no less.

You define a **schema** (the types and their fields), and a **resolver** for each field (the small
function that fetches its value). A query then reads like the shape of the data you want back:

```graphql
# the schema is the contract
type Review { productId: String!, rating: Int! }
type Query { reviews(productId: String!): [Review!]! }

# a client query: ask for only the fields you need
query {
  reviews(productId: "P100") { rating }
}
```

This fits when many different clients each need a different slice of the same data, so a fixed REST
response would either send too much or force a new endpoint per client.

**The cost to know about: the N+1 problem.** Because a query can ask for nested data, one query can
quietly become hundreds of calls. Say a client asks for 100 reviews and, for each one, the author's
name, which lives in a separate users table. A naive resolver runs **1** query to fetch the 100
reviews, then **1 more query per review** to look up each author: **101** database calls for one
request. That is the N+1 problem, one query plus N more. The fix is **batching**: collect the 100
author ids and fetch them in a single query, usually with a helper called a DataLoader. Real GraphQL
servers also **limit query depth and cost**, so one caller cannot send an enormous query that
overloads the server.

Reach for GraphQL when flexible field selection is a genuine, repeated need. For a simple, stable
API, REST is easier to build, cache, and reason about.

### 1.5 Real-time: WebSockets and server-sent events

REST, GraphQL, and gRPC are all request-and-reply: the client asks, the server answers, and the
exchange is done. Some features need the server to push updates to the client as they happen, such as
a live dashboard, a chat, or a progress bar. **Polling** (asking `GET /status` every second) works
but does not scale, because most of those requests come back with no change, and the load grows with
every client. A **persistent connection**, held open between client and server, solves it. There are
two shapes:

- **Server-sent events (SSE).** A one-way stream: the client opens a connection and the server keeps
  sending updates down it. Simple, runs over ordinary HTTP, and is the right fit when only the server
  has news to push (live prices, a job's progress).
- **WebSockets.** A two-way, always-open connection: either side can send a message at any time. Use
  it when the client also needs to send continuously, such as a chat or a collaborative editor.

**Enterprise lens.** A persistent connection removes the wasteful polling, but it adds state: the
server now holds an open connection per client, which is harder to scale and to load-balance than
stateless requests. Reach for it when real-time genuinely matters, and prefer SSE when a one-way push
is all you need.

### 1.6 Testing the API: Postman and code

An API is only trustworthy if you can exercise it, both by hand while you build it and automatically
in the gate. Use both.

**By hand, while building.** A tool like **Postman** (or Insomnia, or the command-line tools `curl`
and `httpie`) lets you send a request and see the exact response and status code without writing a
client. In Postman you group the requests for one service into a **collection**, save an example for
each endpoint, and share it with the team. Because FastAPI publishes the OpenAPI spec, you can
**import `/openapi.json` straight into Postman** and get a request for every endpoint already filled
in. The interactive `/docs` page does the same thing in the browser.

```bash
# the command-line equivalent of one Postman request
curl -X POST http://127.0.0.1:8000/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{"product_id": "P100", "rating": 5}'
```

**Automatically, in the gate.** Testing by hand proves it works once; a test proves it keeps
working. FastAPI ships a `TestClient` that calls the app in the same process, with no server and no
network, so a test can check the whole contract fast: the happy path returns `201`, bad input returns
`422`, and the OpenAPI document lists the versioned route. This is what Day 6 wires into the quality
gate.

> **Try it.** Run `poetry run python demo_json_interop.py`. A small record is turned into a JSON
> string, sent across to another side, and rebuilt from the string on the far end. JSON is the
> language-neutral format that lets two systems, in any languages, agree on the shape they exchange,
> and it is exactly what Postman shows you and what a `TestClient` sends.

### 1.7 API design: dos and don'ts

The habits above come down to a short set of rules. Keep these in view when you design or review an
interface.

**REST**

| Do | Don't |
| --- | --- |
| Name resources with nouns (`/v1/reviews/42`) | Put actions in the URL (`/getReview`) |
| Return the right status code, honestly | Return `200` with an error inside the body |
| Version the contract (`/v1`) from the start | Change what an existing version means |
| Retire an old version on a published timeline | Switch off `/v1` with no warning |
| Put auth and rate limiting at the gateway | Re-implement them in every service |
| Validate the request at the edge with pydantic | Trust the body and check it deep in the code |
| Page and filter large collections | Return the whole table in one response |
| Make creates safe to retry (idempotency key) | Assume every request arrives exactly once |
| Return a clear, documented error shape | Leak a stack trace or a raw database error |

**GraphQL**

| Do | Don't |
| --- | --- |
| Design a typed schema and agree it first | Expose your database tables one to one |
| Batch nested lookups with a DataLoader | Let each field run its own query (N+1) |
| Limit query depth and cost | Accept any query a client sends |
| Return typed errors in the response | Fail the whole query for one bad field |
| Use it when clients need different slices | Reach for it as the default for a simple API |

**Enterprise lens.** A clear, versioned, checked contract, written down as an OpenAPI schema and
exercised by tests, is what lets two teams build on either side of an interface at the same time
without breaking each other. These rules are how you keep that contract easy to use and safe to
change.

GraphQL and REST both run over the same web machinery, aimed at many kinds of client. The next two
shapes are for different situations again: fast calls between your own services, and work that does
not need an answer right away.

### 1.8 gRPC, messaging, and webhooks

Three more shapes are worth knowing, each suited to a case the web-facing styles handle less well.

**gRPC: fast typed calls between services.** gRPC is a typed, binary, high-throughput protocol meant
for calls **between your own services**. You write the contract once in a schema file (a format
called protobuf), and the tooling generates matching client and server code in each language, so both
sides are guaranteed to agree on the shape:

```proto
message Review { string product_id = 1; int32 rating = 2; }
service Reviews { rpc Submit(Review) returns (Ack); }
```

It is faster than JSON over REST for two reasons: the payload is a compact binary format, so **fewer
bytes travel over the wire**, and both sides read those bytes straight into typed structures, so
**parsing is faster** than reading and validating text. The cost is that the messages are not
human-readable, so you cannot eyeball them in a browser. Choose gRPC for internal, high-volume calls
where speed and a strict, generated contract matter more than being easy to call from a browser.

**Messaging: a queue or an event stream.** So far every style has been a direct call where the caller
waits for the reply. Messaging works differently: the sender leaves a message and moves on, and a
consumer handles it later. This **decouples** the two sides, so neither has to be running or fast at
the same moment, and it absorbs traffic spikes. There are two flavours, and they mean different
things:

- **A message queue** (for example RabbitMQ) carries a **command**: do this piece of work. One
  consumer takes each message, and it is handled once. Use it to hand a task off to a worker, such as
  "send this email".
- **An event stream** (for example Kafka) carries a **fact**: this happened. The event stays on the
  stream, and **many** consumers can read it, each at its own pace. Use it when several parts of the
  system need to react to the same event, such as "an order was placed".

**Webhooks: letting a third party call you.** The shapes above are you calling others. A **webhook**
is the reverse: you give a third party a URL, and they send you an HTTP request when something happens
on their side, such as a payment provider telling you a payment succeeded. It is how you receive
events from a system you do not control.

**The trap (webhooks).** Trusting a webhook just because it arrived. Anyone who learns the URL can
post to it. A real provider signs each webhook, and you must **verify that signature** before acting
on it, so a forged request cannot make your system do something. (Security like this is Day 7; here,
just know the boundary has to be verified.)

### 1.9 What surrounds the API: identity and the gateway

Two things sit around a real API that a small FastAPI app does not show on its own. Both get a full
treatment on a later day; know the shape now so the picture is complete.

**Identity: who is calling.** When two systems interoperate, the callee needs to know who the caller
is (**authentication**) and what they are allowed to do (**authorization**). The `401` and `403`
codes from Section 1.2 are how you say "not logged in" and "not allowed". The common ways to carry
identity across the boundary:

- **An API key**, a long secret string the caller sends in a header, for machine-to-machine calls.
- **OAuth2 and OIDC**, the standard for letting a user grant an app limited access through a trusted
  identity provider, without handing over their password.
- **A JWT (JSON Web Token)**, a signed token the caller sends on each request that carries who they
  are, so the server can trust it without a database lookup.

**The trap.** Sending plain passwords across the boundary, or inventing your own login and token
scheme. Use a standard (API keys, OAuth2, OIDC, JWT) and a trusted identity provider; hand-rolled
security is where breaches come from. Day 7 covers this in full.

**The gateway in front.** In an enterprise you rarely expose a Python app straight to the public
internet. An **API gateway** (such as Nginx, Kong, or a cloud API gateway) sits in front of it and
handles the cross-cutting concerns: **rate limiting** (capping how many requests a caller may make,
so one abuser cannot overwhelm you), **TLS termination** (handling the HTTPS encryption), routing,
and often authentication. That lets your Python service focus on the business logic and trust that
the gateway has already dealt with the traffic-shaping and the encryption.

**The trap.** Returning `200 OK`, which announces success, while tucking an error message into the
body, or shipping a contract with no version at all. The first forces every caller to dig through
the response body to find out whether it actually failed; the second means your very first breaking
change breaks everyone at once, with no `/v1` still standing for them to fall back on. In review,
treat the status code and the version as part of the contract itself, not as afterthoughts.

We have now covered the network boundary: the contract idea and the common ways to write it down.
That was the higher of our two levels. Now we go one level lower, into the same process, where the
connecting happens not over a network but as a direct function call into another language. That is
Level 2.

---

## Level 2: Interop at the code level

In Level 1 the two programs were separate processes talking over a network. Now we drop below the
network entirely. The other kind of interoperability is calling code written in another language
**inside the same running process**. There is no network hop and no message on a wire; it is an
ordinary function call that happens to cross from Python into, say, compiled C. Understanding this
matters because it is how much of the fast Python ecosystem actually works underneath.

### 2.1 The two-language pattern

The pattern behind the popular numerical library NumPy, and most of the data stack, has a name
worth learning: the **two-language pattern**. The idea is **a readable Python surface over a fast
native core**. You write the orchestration, the part that is easy to read and easy to change, in
Python; and the heavy inner loops, the part that has to be fast, run in a lower-level compiled
language such as C, C++, Rust, or CUDA, exposed to you as functions that look like ordinary Python.
When you multiply two large arrays with NumPy, almost no time is actually spent running Python; the
real work happens in compiled code that the library calls into on your behalf. This is also the
answer to the CPU-bound problem from Day 2: you push the hot loop down into native code that runs
fast and releases the GIL while it does so.

Having seen why the pattern exists, the natural next question is how Python actually reaches into
that native code. We start with the most common target, C and C++.

### 2.2 Calling C and C++

There are several tools for this, and it helps to see them ordered from the lowest level (closest
to the raw machinery, most manual) to the highest level (most convenient):

- **`ctypes`.** Part of the standard library, so nothing to install. It lets you call functions in
  a shared library that already exists (a `.so` file on Linux or a `.dll` on Windows) by declaring
  each function's argument and return types yourself. Good when you already have a compiled C
  library and just want to call it.
- **`cffi`.** A friendlier way to bind to C, driven by the C header file rather than by hand-written
  type declarations.
- **Cython.** You write Python-like code with a few type annotations, and it compiles that down to
  a C extension. Good for taking a hot Python loop and turning it into fast compiled code with only
  small changes to the original.
- **pybind11.** The modern, well-kept way to expose a C++ library to Python, with a clean API.

```python
import ctypes

lib = ctypes.CDLL("./libfast.so")     # load a compiled C library
lib.score.argtypes = [ctypes.c_double]
lib.score.restype = ctypes.c_double
result = lib.score(3.14)              # a direct call across the C boundary
```

**Why you rarely compile any of this yourself.** A fair question: if NumPy is written in C, why does
`pip install numpy` not make you compile C code? Because the package ships as a **wheel**, a pre-built
archive that already contains the compiled binary for your platform. `pip` downloads the matching
wheel and unpacks it, so you get the fast native core without a compiler. The library author compiled
it once, per platform. You only need a toolchain when you write the native part yourself, or when no
wheel exists for your platform and pip has to build from source.

C and C++ are the most common languages on the other side of that call, but they are not the only
ones. The same in-process idea reaches into other language runtimes too, which is the next section.

> **Try it.** Run `poetry run python demo_ctypes_call.py`. It loads the C standard library, declares
> the argument and return types for `strlen`, and calls it on `b"hello"` to get back `5`. Notice the
> marshaling: the Python string is encoded to bytes before it can cross into C. That is the raw
> two-language boundary with nothing hidden.

### 2.3 Rust, Java, and .NET

- **Rust:** **PyO3** together with **maturin** is the modern, memory-safe way to write a native
  extension. Good for new native code where safety matters, because Rust prevents whole classes of
  memory mistakes at compile time.
- **Java:** **JPype** or **Py4J** connect Python to a Java virtual machine (the JVM, the runtime
  that Java code executes on), and **GraalPy** runs Python on GraalVM right alongside Java. Choose
  an in-process option (JPype, GraalVM) versus a separate bridge (Py4J) based on how much delay and
  how much data movement you can afford between the two sides.
- **.NET / C#:** **Python.NET** lets Python call into the .NET runtime (the CLR) in the same
  process, with care needed for how values are converted across the language line.

### 2.4 Extending versus embedding

There are two directions you can cross this code boundary, and it is worth being clear about which
one you are doing, because they put a different language in charge:

- **Extending:** Python calls into native code. This is everything above. Python is the program in
  charge, and it reaches down into faster code when it needs to.
- **Embedding:** the reverse. A host application written in another language, say a large C++ or
  Java program, builds the Python interpreter into itself and calls Python from there. Now the
  other language is in charge, and Python is the guest.

Most data work is extending. Embedding tends to show up when a big C++ or Java application wants to
offer Python scripting to its users inside the application.

**Enterprise lens.** Interop is a normal reality, not an exotic corner case. The systems a company
already runs are often written in Java and C#, and the fast parts of your own stack are native
code. Knowing how to cross the boundary cleanly is what lets a new Python service fit in with what
the company already has, instead of forcing an expensive rewrite of the existing systems.

We have now seen both levels where connecting happens, the network boundary and the code boundary.
A theme runs through both: every time you cross a boundary, it costs something and it can go wrong.
Level 3 pulls that theme out and turns it into design rules that apply to either kind of boundary.

---

## Level 3: Designing a safe boundary

Whether the boundary is a network API from Level 1 or an in-process native call from Level 2, the
same truth holds: crossing it is neither free nor automatically safe. The good news is that the
same handful of design questions decide whether either kind of boundary holds up under real use.
This level walks through them one at a time, starting with the cost of crossing at all.

### 3.1 Keep the boundary coarse-grained

Every crossing has a fixed cost that you pay each time, no matter how little work you get done on
the far side. The lesson that follows is to make **few, large calls** instead of many small ones,
which is what "coarse-grained" means: chunky crossings rather than fine ones. Passing a whole array
to a native function in a single call is fast. Calling that native function once per element, from
inside a Python loop, pays the crossing cost millions of times over and is often slower than never
leaving Python at all. The same holds for network APIs: one request that fetches a batch beats a
thousand requests that each fetch one item.

**The trap.** A native call or an API call sitting inside a tight loop that runs once per item. The
crossing overhead adds up until it dominates and wipes out the benefit you were chasing. In review,
a boundary crossing inside a hot loop is a signal to lift it out of the loop and cross once over
the whole batch instead.

> **Try it.** Run `poetry run python demo_coarse_vs_fine.py`. It does the same total work two ways:
> one coarse call over the whole batch, and one call per item inside a Python loop. The coarse
> version wins clearly, because it pays the crossing cost once instead of thousands of times.

Making few large crossings assumes the data going across each one is cheap to move. Often it is not,
and the amount of data becomes its own cost, which is the next question.

### 3.2 Marshaling cost

When data crosses a boundary, it usually cannot go as-is; it has to be **marshaled**, which means
packed into a transportable form on one side and rebuilt on the other. Across a network that packing
is JSON or protobuf; across a process boundary it is pickling (the same copying the process pools
did in Day 2); across a native code boundary it is copying the bytes or arranging for both sides to
share the same memory. The point is that when the payloads are large, this packing and unpacking can
become the dominant cost, outweighing the actual work. That is a second reason to design a boundary
so that each crossing does a large amount of useful work relative to the amount of data it has to
move.

> **Try it.** Run `poetry run python demo_native_speed.py`. It runs the same CRC32 checksum two
> ways over the same bytes: a pure-Python loop, and the standard library's `zlib.crc32`, which is the
> identical algorithm written in C. The native version is hundreds to thousands of times faster,
> which is exactly why the hot loop belongs in compiled code.

Cost is one concern at a boundary. Safety is the other, and the first safety question with native
code is what happens to Python's single-threaded rule, the GIL, while the native code runs.

### 3.3 The GIL across the boundary

Recall from Day 2 that the GIL lets only one thread run Python at a time. Native code is not bound by
that rule while it is running its own work, so it can **release the GIL** during the heavy section.
That is exactly what lets a native library spread work across multiple cores even though the Python
calling it looks single-threaded. When you write or call native code for a CPU-bound job, releasing
the GIL during the heavy part is what upgrades Day 2's advice from "use separate processes" to "use
threads that call into native code." What you need to know is that the well-behaved native libraries
already do this for you, and that a hand-written extension has to be written to do it on purpose, or
it will hold the GIL and lose the benefit.

Releasing the GIL keeps native code fast. The next concern is not speed but correctness: when native
code allocates memory, someone has to free it, and getting that wrong crashes the program.

### 3.4 Memory ownership

Across a native boundary, at some point one side allocates a block of memory and one side has to
free it later. The danger is that if both sides assume the other one will free it, you get either a
memory leak (nobody frees it, so it piles up) or a crash (both free it, or one frees it while the
other is still using it). The rule is to **own the contract explicitly**: decide up front which side
allocates and which side frees, and stick to that decision. A maintained binding such as Cython,
pybind11, or PyO3 handles most of this bookkeeping for you, which is a strong reason to prefer one of
them over hand-rolled `ctypes` for anything beyond the simplest call.

Memory is one thing that can go wrong on the far side of a boundary. The other is an outright error
or failure over there, which has to be turned into something your side can deal with.

### 3.5 Error translation

An error that happens on the far side of a boundary has to be converted into an error your side
understands. A crash in native code must be turned into a Python exception you can catch, not left as
a raw segfault that takes the whole process down with it. A `500` coming back from a downstream API
must become a specific exception your caller can catch and handle, not a vague failure. The rule is
to **translate errors at the boundary**, deliberately, so that a failure on the other side arrives as
something your code was written to handle, rather than as something that silently corrupts your data
or kills your program.

**Enterprise lens.** A boundary is the point where two worlds that follow different rules meet.
Designing it to cross in a few large steps, with clear memory ownership and deliberate error
translation, is what keeps a fault on one side from spilling over and becoming an outage on the
other.

> **Try it.** Run `poetry run python demo_error_translation.py`. A boundary function is handed a bad
> payload; instead of letting the low-level failure escape raw, it catches it and re-raises a clear
> domain error (with the original cause attached). The failure arrives as something your code was
> written to handle, not as a surprise from across the boundary.

### 3.6 Tracing a request across services

When system A calls B, which calls C, and something breaks, how do you find where? If each service
logs on its own, you have three separate piles of logs and no way to line them up. The fix is a
**correlation id**, also called a `trace_id`: a unique id created when a request first arrives, and
**passed along in a header** on every downstream call. Every service writes it into its logs, so you
can filter all three logs by that one id and see the whole path of a single request.

**The trap.** Logging errors independently in each service with no shared id, so one failed request
is scattered across systems with nothing tying the lines together. Generate a `trace_id` at the edge
and pass it across every boundary. (Full observability is an operations topic of its own; here, just
know the id has to cross the boundary with the request.)

### Boundary rules at a glance

The Level 3 rules, in one table to keep in view when you design any crossing:

| Rule | Why | Example |
| --- | --- | --- |
| Cross coarse-grained | Each crossing has a fixed cost | Pass the whole batch in one call, not one per item |
| Watch the marshaling | Packing and copying data can dominate | Send a few large payloads, not many tiny ones |
| Release the GIL in native code | Lets threads use many cores | A native library that frees the lock during heavy work |
| Own the memory explicitly | A double free or a leak crashes or bloats | Decide which side allocates and which frees |
| Translate errors at the edge | A far-side failure must become a local one | Turn a crash or a `500` into a Python exception |
| Pass a trace id across | Ties one request's logs together | A `trace_id` header on every downstream call |

With both levels covered and the design rules in hand, we can put everything together on the running
service and see it work at both boundaries.

---

## The build: `reviews-insight`, made interoperable

Earlier days left `reviews-insight` as a clean service you call directly from Python. On Day 5 we
give it a real interface facing the network and a fast native path down in the code, applying both
levels of this chapter at once. The live lab walks every step with commands; here is the shape.

**1. A typed API at the edge.** Wrap the service in a small FastAPI app built by a `create_app`
function: a versioned `POST /v1/reviews` to submit a review (checked by a `pydantic` model at the
edge), a `GET /v1/insight` to fetch the summary (reusing the Day 3 `summarize_rows`), and a
`GET /health` so other systems can check it is alive.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

from reviews_insight.service import summarize_rows


class ReviewIn(BaseModel):                       # the request contract
    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)


class ReviewAccepted(BaseModel):                 # the response contract, checked on the way out
    status: str


def create_app() -> FastAPI:
    app = FastAPI(title="reviews-insight", version="0.5.0")
    store: list[dict[str, str]] = []

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/reviews", status_code=201, response_model=ReviewAccepted)
    def submit(review: ReviewIn) -> ReviewAccepted:
        store.append({"product_id": review.product_id, "rating": str(review.rating)})
        return ReviewAccepted(status="accepted")

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        return summarize_rows(iter(store))

    return app
```

**2. The contract is real.** FastAPI generates an OpenAPI document (served at `/docs`) that is the
machine-readable contract, and a request with `rating: 11` is rejected at the edge with a `422`
before it ever reaches the logic. That is the first proof, at the network level: the boundary checks
its input and the contract genuinely exists.

**3. A native fast path.** Now we drop to the code level. Take the hot text-processing step (cleaning
and splitting review text into words at volume) and push it into a compiled routine, with Cython or a
small C function called through `ctypes`, invoked **once over the whole batch** rather than once per
character, so the crossing is coarse-grained by design. Then benchmark it against the pure-Python
version. That is the second proof: the native step is measurably faster.

**4. A safe boundary.** The native call takes the whole batch and returns the result in a single
crossing, turns a bad input into a clear Python error, and leaves memory ownership to the maintained
binding, so the new fast path does not become a new source of crashes.

The live lab does all of this with real commands and expected output. When you finish, the same small
service now speaks a versioned, validated API to the outside world and calls native code for its hot
path, cleanly, at both boundaries.

---

## Recap

Reading the three levels back as one connected idea, the day descends from the network down into the
code and then draws the design rules that hold at both depths:

- **An interface is a contract.** Check input at the edge, put a version on it, and fail with a clear
  error, so that separate systems and teams can work on either side of it independently.
- **Know the shapes.** REST for resource-oriented web APIs, GraphQL for queries the client shapes,
  gRPC for typed calls between your own services, and messaging to decouple two sides and absorb
  traffic spikes.
- **Build APIs typed**, so the request and response shapes are checked at the boundary for you and an
  OpenAPI contract is generated automatically.
- **The two-language pattern** is how the fast stack works: a readable Python surface over a native
  core, reached with ctypes, Cython, pybind11, PyO3, and the JVM and .NET bridges.
- **Design the boundary.** Cross in a few large steps, watch the cost of moving data, release the GIL
  in native code, decide who owns the memory, and translate errors as they cross.

The review lens for the whole day: given an interface, ask whether input is checked at the edge,
whether it is versioned, whether errors and status codes are meaningful, and, for any native or
cross-language call, whether the boundary crosses in a few large steps and who owns the memory and
the errors. Those questions turn "it connects" into "it connects safely and will keep working."

**Next:** the [live lab](live-lab.md) puts a versioned, validated API on `reviews-insight` and a
benchmarked native fast path behind it. Then two offline assignments apply the same
interoperability layer to IoT telemetry and to financial transactions.
