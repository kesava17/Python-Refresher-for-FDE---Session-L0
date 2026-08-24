# Day 5 Live Lab: Make reviews-insight Interoperable

## What we're building

You already have the Day 4 `reviews-insight` service: the summary logic sits in one place, its data
source is injected behind a Protocol, one decorator carries the timing, and the CLI just wires the
pieces together. It is maintainable, but it only talks to itself. Nothing outside the process can send
it a review, and nothing inside it runs faster than the interpreter allows. In the next 30 minutes you
make it **interoperable** at both ends, and you prove it with numbers:

1. Add a **typed API at the edge**: a `ReviewIn` pydantic model that validates every request at the
   boundary, a `ReviewAccepted` response model that validates every response on the way out, a `/v1`
   prefix that versions the contract, and a `/health` liveness route.
2. Show the **contract is real**: a request with a rating of 11 is rejected with a 422 before any of
   your logic runs, and FastAPI publishes the machine-readable contract at `/openapi.json`.
3. Add the **pieces a real API needs**: a paginated `GET /v1/reviews` that returns one page plus a
   total (never the whole collection), a signed `POST /v1/webhooks/rating` that verifies an HMAC
   signature and refuses a forged one with a 401, and a trace-id middleware that echoes an
   `x-trace-id` header so one request can be followed across services.
4. Add a **native fast path**: a `ctypes` call into C `strlen` that shows marshaling across the
   boundary, and a CRC32 written two ways, pure Python versus zlib's C implementation.
5. Add a **safe, coarse boundary**: one native call over the whole blob, measurably faster than the
   pure-Python loop. That is the proof at the code level.
6. **Serve it**: `reviews serve` starts the versioned API so another process can actually reach it.

Work in order. Copy, paste, run. After each step there is one line on what happened and why it
matters. Start from your Day 4 project folder (`reviews-insight`), with everything green.

Ground rules, same as before: everything Python runs through `poetry run`; run commands from
inside the project folder.

---

## Step 1: A typed API at the edge

The service can count rows, but the outside world has no way in. Give it an HTTP surface where every
request is checked at the door, every response is checked on the way out, and the contract is versioned
from day one. This same file also carries the pieces a real API needs in practice: a paginated list, a
signed webhook, and a trace id. Create `src/reviews_insight/api.py`:

```python
"""The API at the edge (Day 5): a versioned, validated HTTP surface over the service.

FastAPI plus pydantic give us the habits from the lesson for free: request and response models
checked at the edge, a versioned path, a generated OpenAPI document, plus the practical pieces a
real API needs: a paginated list, a signed webhook we can trust, and a trace id that ties a
request's logs together as it crosses services.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from reviews_insight.service import summarize_rows

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class ReviewIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)  # a value outside 1 to 5 is rejected with a 422


class ReviewAccepted(BaseModel):
    """The response contract, checked on the way out."""

    status: str


class ReviewOut(BaseModel):
    """One review as returned in a listing."""

    product_id: str
    rating: int


class ReviewPage(BaseModel):
    """A single page of reviews, plus the paging information to fetch the next one."""

    items: list[ReviewOut]
    total: int
    limit: int
    offset: int


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="reviews-insight", version="0.5.0")
    store: list[dict[str, str]] = []

    @app.middleware("http")
    async def add_trace_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Reuse the caller's trace id if it sent one, otherwise start a new one. Passing it back
        # (and, in real code, logging it) lets one request be followed across every service.
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        response = await call_next(request)
        response.headers["x-trace-id"] = trace_id
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        # A liveness route so other systems can check the service is up.
        return {"status": "ok"}

    @app.post("/v1/reviews", status_code=201, response_model=ReviewAccepted)
    def submit(review: ReviewIn) -> ReviewAccepted:
        # By the time we reach here, review is already valid: the edge rejected any bad input.
        store.append({"product_id": review.product_id, "rating": str(review.rating)})
        return ReviewAccepted(status="accepted")

    @app.get("/v1/reviews", response_model=ReviewPage)
    def list_reviews(limit: int = 20, offset: int = 0) -> ReviewPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [ReviewOut(product_id=row["product_id"], rating=int(row["rating"])) for row in page]
        return ReviewPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        # Summarize whatever has been submitted so far, reusing the Day 3 shared logic.
        return summarize_rows(iter(store))

    @app.post("/v1/webhooks/rating", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        store.append({"product_id": str(payload["product_id"]), "rating": str(payload["rating"])})
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "reviews_insight.api:app".
app = create_app()
```

**What happened.** `ReviewIn` is the request contract, and FastAPI checks every incoming request
against it **at the edge**: by the time `submit` runs, `review` is already known good, so the logic
never has to guess whether its input is sane. That is **validate at the edge**, the boundary discipline
that keeps bad data out of the core. `ReviewAccepted` is the matching **response contract**: with
`response_model=ReviewAccepted` on the route, FastAPI validates what you send back too, so the outgoing
shape is enforced, not just the incoming one. The `/v1` prefix on the routes is **versioning**: the
contract has a name, so you can ship a `/v2` later without breaking the callers still on `/v1`. `/health`
is a plain liveness route other systems poll to see the service is up.

Three more routes round out what a real API needs. `GET /v1/reviews` is **paginated**: it takes `limit`
and `offset`, returns one page of `ReviewOut` items in a `ReviewPage`, and reports the `total`, so a
caller can page through instead of pulling the whole collection in one response. `POST /v1/webhooks/rating`
is a **signed webhook**: because the call comes from a system you do not control, you cannot trust it just
because it arrived, so the handler recomputes the HMAC-SHA256 signature over the raw body and compares it
against the `x-signature` header with `hmac.compare_digest`, rejecting a mismatch with a `401` before the
payload is ever read. The `add_trace_id` **middleware** wraps every request: it reuses an incoming
`x-trace-id` header or generates a fresh `uuid.uuid4().hex`, and echoes it back on the response, so one
request can be followed across services. Note that `create_app` builds a fresh store inside each app, and
the module-level `app` at the bottom is the instance a real server loads.

---

## Step 2: The contract is real

An API is only interoperable if its promises are enforced and written down. Prove both: bad input is
turned away with a real status code, and the contract exists as a document other teams can read.
Create `tests/test_api.py`:

```python
"""Day 5 contract tests: the API validates at the edge and exposes a real, versioned contract."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from reviews_insight.api import create_app

_WEBHOOK_SECRET = b"shared-webhook-secret"  # must match the secret the app uses


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _sign(body: bytes) -> str:
    return hmac.new(_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()


def test_health_route() -> None:
    assert _client().get("/health").json() == {"status": "ok"}


def test_submit_valid_then_insight() -> None:
    client = _client()
    assert client.post("/v1/reviews", json={"product_id": "P1", "rating": 5}).status_code == 201
    client.post("/v1/reviews", json={"product_id": "P1", "rating": 4})
    client.post("/v1/reviews", json={"product_id": "P2", "rating": 3})
    assert client.get("/v1/insight").json() == {"reviews": 3, "products": 2, "rejected": 0}


def test_bad_input_is_rejected_at_the_edge() -> None:
    client = _client()
    # A rating of 11 is outside 1 to 5, so pydantic rejects it before our code runs.
    assert client.post("/v1/reviews", json={"product_id": "P1", "rating": 11}).status_code == 422
    # An empty product_id fails the min_length rule the same way.
    assert client.post("/v1/reviews", json={"product_id": "", "rating": 5}).status_code == 422


def test_openapi_contract_exists() -> None:
    # FastAPI generates the machine-readable contract; the versioned route is in it.
    doc = _client().get("/openapi.json").json()
    assert "/v1/reviews" in doc["paths"]


def test_list_reviews_is_paginated() -> None:
    client = _client()
    for i in range(5):
        client.post("/v1/reviews", json={"product_id": f"P{i}", "rating": 5})
    page = client.get("/v1/reviews", params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 5  # the total is reported so the caller can page through
    assert page["limit"] == 2
    assert page["offset"] == 2
    assert len(page["items"]) == 2  # only one page is returned, not all five


def test_webhook_accepts_a_valid_signature() -> None:
    client = _client()
    body = json.dumps({"product_id": "P9", "rating": 4}).encode("utf-8")
    resp = client.post("/v1/webhooks/rating", content=body, headers={"x-signature": _sign(body)})
    assert resp.status_code == 201
    assert client.get("/v1/insight").json()["reviews"] == 1


def test_webhook_rejects_a_forged_signature() -> None:
    client = _client()
    body = json.dumps({"product_id": "P9", "rating": 4}).encode("utf-8")
    resp = client.post("/v1/webhooks/rating", content=body, headers={"x-signature": "forged"})
    assert resp.status_code == 401  # a bad signature is refused before the payload is used
    assert client.get("/v1/insight").json()["reviews"] == 0


def test_trace_id_is_returned_and_echoed() -> None:
    client = _client()
    # With no trace id sent, the server generates one and returns it.
    assert client.get("/health").headers.get("x-trace-id")
    # With a trace id sent, the server echoes the same one back, so the request can be followed.
    resp = client.get("/health", headers={"x-trace-id": "abc123"})
    assert resp.headers["x-trace-id"] == "abc123"
```

**What happened.** This is **the first proof, at the network level**, and it now covers all eight
contract tests. `test_bad_input_is_rejected_at_the_edge` posts a review with a rating of 11, and the API
answers **422** before any counting logic runs: pydantic turned the request away at the boundary, exactly
as the contract promised. An empty `product_id` fails the `min_length` rule the same way. Meanwhile
`test_openapi_contract_exists` fetches `/openapi.json`, the document FastAPI generates for free, and finds
`/v1/reviews` in it. That document is the **machine-readable contract**: another team can generate a
client from it without reading your code. The four new tests pin down the practical routes.
`test_list_reviews_is_paginated` submits five reviews, asks for a two-item window at offset two, and
checks that it gets exactly one page back with the full `total` reported, not all five rows.
`test_webhook_accepts_a_valid_signature` signs the raw body with the shared secret and confirms the
webhook stores the review, while `test_webhook_rejects_a_forged_signature` sends a bad `x-signature` and
confirms the `401` lands and nothing is stored. `test_trace_id_is_returned_and_echoed` checks the
middleware both generates a trace id when none is sent and echoes back the one it was given. The
`TestClient` drives the app in-process, so these are real HTTP round trips with no server to start.

---

## Step 3: A native fast path

Some work is too hot for the interpreter, one byte at a time. The answer is not to rewrite the service
in C; it is to open a narrow, well-typed boundary and push just the hot step across it. Create
`src/reviews_insight/native.py`:

```python
"""The two-language boundary (Day 5): a Python surface over native C code.

Two ideas live here. First, a direct call across the boundary with `ctypes`: Python hands a
byte buffer to the C library's `strlen` and gets a length back. That shows marshaling (a
Python str must be encoded to bytes before it can cross) and the argtypes/restype declarations
that make the crossing safe. Second, a hot step done two ways: a pure-Python CRC32, and the
standard library's `zlib.crc32`, which is the same algorithm written in C. Timing the two shows
why you push a hot loop down into compiled code.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys
import zlib


def _load_libc() -> ctypes.CDLL:
    # The C standard library sits in different places per platform: msvcrt on Windows, and the
    # library named "c" on Linux and macOS. Loading it lets us call C functions directly.
    if sys.platform == "win32":
        return ctypes.CDLL("msvcrt")
    name = ctypes.util.find_library("c")
    if name is None:  # every POSIX system ships a C library; this is a defensive guard
        raise OSError("could not locate the C standard library")
    return ctypes.CDLL(name)


_LIBC = _load_libc()
# Declaring the argument and return types is how ctypes marshals values correctly: strlen takes
# a char* (bytes) and returns a size_t (an unsigned integer). Get these wrong and you get
# garbage or a crash, which is the boundary discipline this whole chapter is about.
_LIBC.strlen.argtypes = [ctypes.c_char_p]
_LIBC.strlen.restype = ctypes.c_size_t


def native_strlen(text: str) -> int:
    """Count the bytes in text by calling C strlen across the boundary, in one coarse crossing."""
    # Marshaling: a Python str is encoded to bytes before it can cross into C.
    return int(_LIBC.strlen(text.encode("utf-8")))


def crc32_python(data: bytes) -> int:
    """A pure-Python CRC32: correct, but the loop runs in the interpreter, one byte at a time."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            # Shift down, and XOR the polynomial only when the low bit was set.
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1))
    return crc ^ 0xFFFFFFFF


def crc32_native(data: bytes) -> int:
    """The same CRC32, computed by zlib's C implementation in a single call across the boundary."""
    return zlib.crc32(data)
```

**What happened.** `_load_libc` finds the C standard library wherever the platform keeps it, so the
same code runs on Windows, Linux, and macOS. The two `_LIBC.strlen` lines are the crossing's safety
rails: `argtypes` and `restype` tell ctypes that `strlen` takes a `char*` and returns a `size_t`, and
getting those wrong yields garbage or a crash. `native_strlen` shows **marshaling**: a Python `str`
has no native form C understands, so it is encoded to `bytes` before it can cross. Then comes the
**two-language pattern**: `crc32_python` computes a CRC32 with the loop running in the interpreter, one
byte at a time, while `crc32_native` gets the identical result from `zlib.crc32`, the same algorithm
written in C. Same answer, two very different amounts of work, which sets up the next step.

Before you time anything, confirm the two implementations actually agree, so the benchmark is comparing
correct code against correct code. Create `tests/test_native.py`:

```python
"""Day 5 native-boundary tests: the compiled path agrees with the pure-Python one."""

from __future__ import annotations

import zlib

from reviews_insight.native import crc32_native, crc32_python, native_strlen


def test_crc32_python_matches_native() -> None:
    # The pure-Python CRC32 and zlib's C CRC32 are the same algorithm, so they must agree.
    for text in ["", "hello", "reviews-insight", "P100,5,great"]:
        data = text.encode("utf-8")
        assert crc32_python(data) == zlib.crc32(data) == crc32_native(data)


def test_native_strlen_matches_len_for_ascii() -> None:
    # Across the ctypes boundary, C strlen counts the same bytes Python does for ASCII text.
    assert native_strlen("hello") == 5
    assert native_strlen("") == 0
```

**What happened.** These tests pin the boundary down before you trust it for speed. `test_crc32_python_matches_native`
checks that the pure-Python CRC32, `zlib.crc32`, and `crc32_native` all return the same value for a
handful of inputs: if the fast path ever drifts from the slow one, a green benchmark would be a lie, and
this test catches it. `test_native_strlen_matches_len_for_ascii` confirms the ctypes crossing counts
the same bytes Python does. Correctness first, speed second: only once the two paths agree is it honest
to ask which is faster.

---

## Step 4: A safe, coarse boundary

The whole point of the native path is speed, so measure it, and measure it fairly. The rule is one
coarse crossing over the whole blob, not a million tiny ones. Create `scripts/benchmark_native.py`:

```python
"""Benchmark the pure-Python CRC32 against zlib's native C one, over the sample review text.

This is the second Day 5 proof: pushing a hot loop down into compiled code is measurably
faster. The crossing is coarse-grained, one call over the whole blob, so the boundary cost is
paid once and the C code does the heavy per-byte work.
"""

from __future__ import annotations

import time
from pathlib import Path

from reviews_insight.native import crc32_native, crc32_python


def main() -> None:
    # Read the sample file and repeat it, so there is enough data to time meaningfully.
    sample = Path(__file__).resolve().parents[1] / "data" / "reviews_sample.csv"
    blob = sample.read_bytes() * 400

    start = time.perf_counter()
    crc32_python(blob)
    python_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    crc32_native(blob)
    native_ms = (time.perf_counter() - start) * 1000

    print(f"bytes hashed      : {len(blob)}")
    print(f"pure-Python CRC32 : {python_ms:8.1f} ms")
    print(f"native (zlib) CRC : {native_ms:8.3f} ms")
    speedup = python_ms / native_ms if native_ms else float("inf")
    print(f"speedup           : about {speedup:.0f}x faster in native C")


if __name__ == "__main__":
    main()
```

Run the benchmark:

```bash
poetry run python scripts/benchmark_native.py
```

You will see something like this (the exact numbers vary by machine):

```text
bytes hashed      :   ...
pure-Python CRC32 :    118.0 ms
native (zlib) CRC :    0.050 ms
speedup           : about 1000x faster in native C
```

**What happened.** This is **the second proof, at the code level**. The pure-Python CRC32 grinds through
the blob one byte at a time in the interpreter and takes roughly 118 ms; the native call hands the same
blob to zlib's C code once and returns in about 0.05 ms, on the order of a thousand times faster. The
number that matters is not the raw speedup, it is *why* the crossing is safe: the native call runs
**once over the whole blob**, a **coarse-grained** boundary, so the fixed cost of crossing into C is paid
a single time and the C code does all the per-byte work. Cross the boundary a million times for one byte
each and the crossing cost would swamp any gain. One coarse call, verified correct in Step 3, is the
pattern that pays off.

---

## Step 5: Serve it

The API is written and tested in-process, but interoperable means another program can actually reach it
over the network. Give the CLI a `serve` command that starts the API on a real port. Open
`src/reviews_insight/cli.py` and make it read:

```python
"""Command line entry point (Day 5: adds a `serve` command for the HTTP API).

The CLI stays a thin surface. `summary` runs the batch summary as before; `serve` starts the
versioned HTTP API from api.py. All the real logic still lives in the service and the API.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from reviews_insight.config import Config
from reviews_insight.service import SummaryService, summarize_rows
from reviews_insight.sources import CsvReviewSource


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """Day 1: summarize a list of records held in memory."""
    products = {record["product_id"] for record in records}
    return {"reviews": len(records), "products": len(products)}


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    reviews = 0
    products: set[str] = set()
    for record in records:
        reviews += 1
        products.add(record["product_id"])
    return {"reviews": reviews, "products": len(products)}


def summarize_validated(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 4: parse and reject bad rows. A thin alias over the service's shared logic."""
    return summarize_rows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="reviews-insight")
    parser.add_argument("command", choices=["summary", "serve"], help="what to do")
    parser.add_argument("--port", type=int, default=8000, help="port for the serve command")
    args = parser.parse_args()

    if args.command == "serve":
        # Imported lazily: only the serve path needs the web server, so the summary path stays light.
        import uvicorn

        print(f"serving reviews-insight on http://127.0.0.1:{args.port} (press Ctrl+C to stop)")
        uvicorn.run("reviews_insight.api:app", host="127.0.0.1", port=args.port)
        return

    config = Config.from_env()
    source = CsvReviewSource(config.data_path)
    service = SummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"reviews : {result['reviews']}")
    print(f"products: {result['products']}")
    print(f"rejected: {result['rejected']}")


if __name__ == "__main__":
    main()
```

Confirm the batch path still works, then run the gate, then start the server:

```bash
poetry run reviews summary
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
poetry run reviews serve
```

The summary prints exactly as it did on Day 4:

```text
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
rejected: 2
```

And `reviews serve` starts the API on `http://127.0.0.1:8000`, where `GET /health`, `POST /v1/reviews`,
the paginated `GET /v1/reviews`, `GET /v1/insight`, the signed `POST /v1/webhooks/rating`,
`/openapi.json`, and the interactive docs at `/docs` are all live. Every response carries an
`x-trace-id` header, whether you sent one in or the server generated it. Press Ctrl+C to stop it.

**What happened.** The CLI stays the same thin surface it was on Day 4: `summary` runs the batch path
unchanged, and the new `serve` branch starts the versioned API through uvicorn. Notice `import uvicorn`
sits **inside** the serve branch, imported lazily, so the everyday `summary` command never pays to load
a web server it does not use. One `reviews serve` and the contract you wrote and tested in Steps 1 and 2
is reachable over the network: another process can `POST` a review, `GET` the insight, and read
`/openapi.json` to learn the shape without ever seeing your source. That is interoperability at the
edge, matching the native fast path at the other end.

---

## You should see

Run through this recap. If each line matches, Day 5's lab is done.

- `poetry run reviews summary` still prints the timing line and the counts from Day 4, with no crash:

  ```text
  [timed] summary: 0.3 ms
  [dev] reviews-insight
  reviews : 5
  products: 3
  rejected: 2
  ```

- `poetry run pytest -q` reports **19 passed**: the Day 4 tests still pass, plus the 8 API contract
  tests (in `test_api.py`) and the 2 native tests. A single `StarletteDeprecationWarning` is expected
  and harmless.
- `poetry run ruff check .` and `poetry run mypy src` are both clean.
- A review with a bad rating is **rejected with a 422 at the edge**, before any counting logic runs, and
  `/openapi.json` carries the versioned `/v1/reviews` route as the machine-readable contract.
- The API is **validated on the way out too**: `POST /v1/reviews` returns a `ReviewAccepted` response
  model, and `GET /v1/reviews` returns one `ReviewPage` (items plus the total) rather than the whole
  collection.
- The **webhook refuses a forged signature**: `POST /v1/webhooks/rating` answers `401` when the
  `x-signature` header does not match the HMAC over the raw body, before the payload is read.
- Every response carries an **`x-trace-id`** header, reusing the one the caller sent or generating a
  fresh one, so a request can be followed across services.
- The **native CRC32 step is far faster than pure Python** (roughly a thousand times, numbers vary by
  machine), because one coarse crossing pushes the hot loop into C, and the two paths were proven to
  agree first.

That is the Day 5 layer: the same small service is now interoperable at both ends. At the edge it speaks
a validated, versioned HTTP contract that turns bad input away at the door and publishes itself as
OpenAPI; down in the code it opens a narrow, well-typed boundary into C for the one step that is hot,
and pays the crossing cost once. The design choices (validate at the edge, version the contract, cross
into native code coarsely and only where it is worth the cost, and prove correctness before speed) are
what let this service work alongside other programs, in other languages, without giving up the reliability
the earlier days paid for.
