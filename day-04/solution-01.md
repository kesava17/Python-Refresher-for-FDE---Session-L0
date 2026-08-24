# Solution 01 · Make telemetry-insight interoperable

> The full worked solution for Assignment 01. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your `telemetry-insight` project, green, with the Day 3 maintainable layers in place.
This solution adds the Day 5 interoperable layer: a native routine that reaches across the language
boundary into compiled C, a versioned and validated HTTP API in front of the service, a `serve`
command that starts it, and contract tests that prove the API keeps its promise. Use `poetry run`
for everything.

The result you are after: the summary behaviour is unchanged, `telemetry summary` still prints five
valid readings, three devices, and two rejected rows, but the service now has an HTTP surface that
validates input at the edge and a native routine beside it, so other systems can talk to it and a
hot loop can drop into C when it needs to.

## Step 1: the web dependencies

The API needs three runtime dependencies. FastAPI is the framework, `httpx` is what the test client
rides on, and `uvicorn` is the server the `serve` command runs. FastAPI pulls pydantic in itself, so
we do not add it by hand.

```bash
poetry add fastapi httpx uvicorn
```

**`pyproject.toml`** (the parts that change for Day 5)

```toml
[tool.poetry]
name = "telemetry-insight"
version = "0.5.0"
description = "IoT telemetry insight. Day 5: interoperable, with a versioned validated API and a native numeric routine."

[tool.poetry.dependencies]
python = "^3.11"
python-dotenv = "^1.0"
fastapi = "^0.141.1"
httpx = "^0.28.1"
uvicorn = "^0.52.3"
```

The version moves to `0.5.0` so the package version tracks the day. `httpx` belongs in the runtime
dependencies, not the dev group, because FastAPI's `TestClient` uses it under the hood.

## Step 2: the native boundary

The two-language boundary, in miniature. First a direct call across it: Python hands a byte buffer to
the C library's `strlen` and gets a length back. That shows marshaling (a Python `str` must be
encoded to bytes before it can cross) and the `argtypes`/`restype` declarations that make the
crossing safe. Second, one hot step done two ways: a pure-Python CRC32, and the standard library's
`zlib.crc32`, which is the same algorithm written in C. The two must agree on every input, and timing
them shows why you push a hot loop down into compiled code.

**`src/telemetry_insight/native.py`**

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

The crossing is only safe once the types are declared: `strlen` takes a `char*` (bytes) and returns a
`size_t` (an unsigned integer), so `argtypes` and `restype` say exactly that. `native_strlen` has to
encode to bytes first, because a Python `str` cannot cross into C until it is bytes; that is
marshaling. The two CRC32 routines are the same algorithm on two sides of the boundary: one runs the
loop in the interpreter, the other in compiled C, and they must return the same number for any input.

## Step 3: the validated, versioned API

The service becomes interoperable here. FastAPI plus pydantic give the two habits at the edge for
free: the pydantic model validates incoming JSON at the boundary, so a value of 999 is rejected with
a 422 before any of our code runs, and the `/v1` prefix versions the contract. FastAPI also generates
an OpenAPI document at `/openapi.json`, which is the machine-readable contract other teams build
against. The insight route reuses the Day 3 `summarize_rows`, so the API and the CLI count the same
way.

**`src/telemetry_insight/api.py`**

```python
"""The API at the edge (Day 5): a versioned, validated HTTP surface over the service.

FastAPI plus pydantic give us the two habits from Section 1.1 for free. The pydantic model
validates incoming JSON at the boundary (a value of 999 is rejected with a 422 before our code
runs), and the `/v1` prefix versions the contract. FastAPI also generates an OpenAPI document at
`/openapi.json`, which is the machine-readable contract other teams build against. On top of that
sit the practical pieces a real API needs: a paginated list, a signed webhook we can trust, and a
trace id that ties a request's logs together as it crosses services.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from telemetry_insight.service import summarize_rows

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class ReadingIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    device_id: str = Field(min_length=1)
    value: float = Field(ge=-50, le=150)  # a value outside -50 to 150 is rejected with a 422


class ReadingAccepted(BaseModel):
    """The response contract, checked on the way out."""

    status: str


class ReadingOut(BaseModel):
    """One reading as returned in a listing."""

    device_id: str
    value: float


class ReadingPage(BaseModel):
    """A single page of readings, plus the paging information to fetch the next one."""

    items: list[ReadingOut]
    total: int
    limit: int
    offset: int


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="telemetry-insight", version="0.5.0")
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

    @app.post("/v1/readings", status_code=201, response_model=ReadingAccepted)
    def ingest(reading: ReadingIn) -> ReadingAccepted:
        # By the time we reach here, reading is already valid: the edge rejected any bad input.
        store.append({"device_id": reading.device_id, "value": str(reading.value)})
        return ReadingAccepted(status="accepted")

    @app.get("/v1/readings", response_model=ReadingPage)
    def list_readings(limit: int = 20, offset: int = 0) -> ReadingPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [ReadingOut(device_id=row["device_id"], value=float(row["value"])) for row in page]
        return ReadingPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        # Summarize whatever has been ingested so far, reusing the Day 3 shared logic.
        return summarize_rows(iter(store))

    @app.post("/v1/webhooks/reading", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        store.append({"device_id": str(payload["device_id"]), "value": str(payload["value"])})
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "telemetry_insight.api:app".
app = create_app()
```

The `ReadingIn` model is the whole input edge: `device_id` must be at least one character, and `value`
must sit in the range `-50` to `150`. Anything outside that is rejected with a 422 before `ingest`
runs, so the handler only ever sees valid data. Keeping the `store` inside `create_app()` makes each
app instance independent, which is exactly what lets every test start from a clean store. The
module-level `app` exists so a server can load it by import path.

Four practical pieces sit on top of that basic surface:

- **A response model on create.** `POST /v1/readings` declares `response_model=ReadingAccepted` and
  returns `ReadingAccepted(status="accepted")`. The request model validates input on the way in; the
  response model validates and documents the output on the way out.
- **A paginated list.** A second `GET /v1/readings` route takes `limit` and `offset` query parameters,
  slices the store with `store[offset : offset + limit]`, and returns a `ReadingPage` with the page of
  `ReadingOut` rows plus the `total`, so a caller can page through instead of pulling the whole store.
- **A signed webhook.** `POST /v1/webhooks/reading` reads the raw body, computes an HMAC-SHA256 over
  it with the shared secret, and compares it to the `x-signature` header with `hmac.compare_digest`. A
  bad signature is refused with a 401 before the payload is parsed, because a webhook comes from a
  system we do not control. The signature is over the raw bytes, not the parsed JSON, because
  re-serializing could change the bytes and break the check, and `compare_digest` is used rather than
  `==` so the comparison does not leak timing information.
- **A trace-id middleware.** An `@app.middleware("http")` handler reuses an incoming `x-trace-id`
  header or generates one with `uuid.uuid4().hex`, then echoes it on the response. In real code the
  same id goes into every log line for the request, so one call can be followed across services.

## Step 4: the serve command

The CLI stays a thin surface. `summary` reads configuration, builds the concrete pieces, wires them
together, and prints the result, exactly as it did on Day 4. `serve` starts the versioned HTTP API
from `api.py`. All the real logic still lives in the service and the API.

**`src/telemetry_insight/cli.py`**

```python
"""Command line entry point (Day 5: adds a `serve` command for the HTTP API).

The CLI stays a thin surface. `summary` reads configuration, builds the concrete pieces (a
CSV source and the service that uses it), wires them together, and prints the result. `serve`
starts the versioned HTTP API from api.py. All the real logic still lives in the service and
the API, so this surface stays small and easy to read.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from telemetry_insight.config import Config
from telemetry_insight.service import DeviceSummaryService, summarize_rows
from telemetry_insight.sources import CsvReadingSource


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    readings = 0
    devices: set[str] = set()
    for record in records:
        readings += 1
        devices.add(record["device_id"])
    return {"readings": readings, "devices": len(devices)}


def summarize_validated(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 4: parse and reject bad rows. Now a thin alias over the service's shared logic."""
    return summarize_rows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="telemetry-insight")
    parser.add_argument("command", choices=["summary", "serve"], help="what to do")
    parser.add_argument("--port", type=int, default=8000, help="port for the serve command")
    args = parser.parse_args()

    if args.command == "serve":
        # Imported lazily: only the serve path needs the web server, so the summary path stays light.
        import uvicorn

        print(f"serving telemetry-insight on http://127.0.0.1:{args.port} (press Ctrl+C to stop)")
        uvicorn.run("telemetry_insight.api:app", host="127.0.0.1", port=args.port)
        return

    config = Config.from_env()

    # Composition root: build the concrete source, inject it into the service, run it.
    source = CsvReadingSource(config.data_path)
    service = DeviceSummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"readings: {result['readings']}")
    print(f"devices : {result['devices']}")
    print(f"rejected: {result['rejected']}")


if __name__ == "__main__":
    main()
```

`uvicorn` is imported inside the `serve` branch, not at the top of the file, so the summary path stays
light and never pays for a web server it does not use. `uvicorn.run` points at the app by its import
string, `"telemetry_insight.api:app"`, which is why `api.py` exposes a module-level `app`. The
`summary` path is untouched from Day 4.

## Step 5: run it

```bash
poetry run telemetry summary
```

```text
[timed] summary: 0.2 ms
[dev] telemetry-insight
readings: 5
devices : 3
rejected: 2
```

The same five valid readings, three devices, and two rejected rows as before. The interoperable layer
did not change what the summary does; it added new ways to reach the service. To see the API for
yourself, start it and open the generated contract:

```bash
poetry run telemetry serve
# then visit http://127.0.0.1:8000/openapi.json in another terminal or a browser
```

## Step 6: the contract tests

The deliverable proof, eight tests in all. A `TestClient` drives the API the way a real caller would,
and each test builds a fresh app so the in-memory store never leaks between them. Health works, a
valid reading returns 201, an out-of-range value returns 422 at the edge, insight returns the counts,
the generated OpenAPI document lists the versioned route, the list route pages, the signed webhook is
accepted and a forged one refused, and the trace id is generated and echoed.

**`tests/test_api.py`**

```python
"""Day 5 contract tests: the API validates at the edge and exposes a real, versioned contract."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from telemetry_insight.api import create_app

_WEBHOOK_SECRET = b"shared-webhook-secret"  # must match the secret the app uses


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _sign(body: bytes) -> str:
    return hmac.new(_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()


def test_health_route() -> None:
    assert _client().get("/health").json() == {"status": "ok"}


def test_ingest_valid_then_insight() -> None:
    client = _client()
    assert client.post("/v1/readings", json={"device_id": "D1", "value": 20.5}).status_code == 201
    client.post("/v1/readings", json={"device_id": "D1", "value": 21.0})
    client.post("/v1/readings", json={"device_id": "D2", "value": 19.0})
    assert client.get("/v1/insight").json() == {"readings": 3, "devices": 2, "rejected": 0}


def test_bad_input_is_rejected_at_the_edge() -> None:
    client = _client()
    # A value of 999 is outside -50 to 150, so pydantic rejects it before our code runs.
    assert client.post("/v1/readings", json={"device_id": "D1", "value": 999}).status_code == 422
    # An empty device_id fails the min_length rule the same way.
    assert client.post("/v1/readings", json={"device_id": "", "value": 20.0}).status_code == 422


def test_openapi_contract_exists() -> None:
    # FastAPI generates the machine-readable contract; the versioned route is in it.
    doc = _client().get("/openapi.json").json()
    assert "/v1/readings" in doc["paths"]


def test_list_readings_is_paginated() -> None:
    client = _client()
    for i in range(5):
        client.post("/v1/readings", json={"device_id": f"D{i}", "value": 20.0})
    page = client.get("/v1/readings", params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 5  # the total is reported so the caller can page through
    assert page["limit"] == 2
    assert page["offset"] == 2
    assert len(page["items"]) == 2  # only one page is returned, not all five


def test_webhook_accepts_a_valid_signature() -> None:
    client = _client()
    body = json.dumps({"device_id": "D9", "value": 22.0}).encode("utf-8")
    resp = client.post("/v1/webhooks/reading", content=body, headers={"x-signature": _sign(body)})
    assert resp.status_code == 201
    assert client.get("/v1/insight").json()["readings"] == 1


def test_webhook_rejects_a_forged_signature() -> None:
    client = _client()
    body = json.dumps({"device_id": "D9", "value": 22.0}).encode("utf-8")
    resp = client.post("/v1/webhooks/reading", content=body, headers={"x-signature": "forged"})
    assert resp.status_code == 401  # a bad signature is refused before the payload is used
    assert client.get("/v1/insight").json()["readings"] == 0


def test_trace_id_is_returned_and_echoed() -> None:
    client = _client()
    # With no trace id sent, the server generates one and returns it.
    assert client.get("/health").headers.get("x-trace-id")
    # With a trace id sent, the server echoes the same one back, so the request can be followed.
    resp = client.get("/health", headers={"x-trace-id": "abc123"})
    assert resp.headers["x-trace-id"] == "abc123"
```

The two 422 cases are the heart of the input proof: a value of 999 and an empty `device_id` are both
turned away at the edge, before `ingest` runs, so bad data never reaches the logic. The insight test
shows the API and the Day 3 `summarize_rows` counting the same way, and the OpenAPI test shows the
versioned contract is real and machine-readable, not just a convention in the code. The pagination
test posts five readings and asks for a two-row page at offset two, checking the `total` and that only
one page comes back. The two webhook tests are the same input proof for a caller we do not control: a
body signed with the shared secret is accepted and stored, while a forged signature is refused with a
401 and nothing is stored. The trace-id test shows the middleware generating an id when none is sent
and echoing the caller's id back unchanged when one is.

**`tests/test_native.py`**

```python
"""Day 5 native-boundary tests: the compiled path agrees with the pure-Python one."""

from __future__ import annotations

import zlib

from telemetry_insight.native import crc32_native, crc32_python, native_strlen


def test_crc32_python_matches_native() -> None:
    # The pure-Python CRC32 and zlib's C CRC32 are the same algorithm, so they must agree.
    for text in ["", "hello", "telemetry-insight", "D100,20.5"]:
        data = text.encode("utf-8")
        assert crc32_python(data) == zlib.crc32(data) == crc32_native(data)


def test_native_strlen_matches_len_for_ascii() -> None:
    # Across the ctypes boundary, C strlen counts the same bytes Python does for ASCII text.
    assert native_strlen("hello") == 5
    assert native_strlen("") == 0
```

The CRC32 test loops over a few strings and asserts the pure-Python path, `zlib.crc32`, and
`crc32_native` all return the same number, so a single disagreement anywhere would fail the test. The
`strlen` test shows the value that came back across the ctypes boundary is the same byte count Python
would compute for ASCII text, which is the sign the marshaling and the type declarations are right.

## Step 7: green gate and commit

```bash
poetry run pytest -q          # 19 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "day 5: give telemetry-insight a versioned validated API and a native routine"
```

The eight Day 5 API tests and the two native tests join the tests carried forward from earlier days,
for 19 in all. A single `StarletteDeprecationWarning` from the test client is expected and harmless;
the gate is 19 passing.

## Done when

- `fastapi`, `httpx`, and `uvicorn` are dependencies, and the project version is `0.5.0`.
- `native.py` calls C `strlen` across the `ctypes` boundary and offers a pure-Python and a native
  CRC32 that agree on every input.
- `api.py` has a `create_app()` factory with a `ReadingIn` model, a `/health` route, a
  `POST /v1/readings` returning 201, and a `GET /v1/insight` returning the counts.
- `POST /v1/readings` uses `response_model=ReadingAccepted`, `GET /v1/readings` is paginated with
  `ReadingOut` and `ReadingPage`, `POST /v1/webhooks/reading` verifies an HMAC-SHA256 signature and
  refuses a forged one with a 401, and an `http` middleware reuses or generates and echoes an
  `x-trace-id`.
- A value of 999 is rejected with 422 and an empty `device_id` is rejected with 422, both at the edge.
- The CLI has a `serve` command that starts the API, and `telemetry summary` still prints
  `readings: 5`, `devices : 3`, `rejected: 2`.
- Contract tests with a `TestClient` (eight in `tests/test_api.py`) prove health, ingest, the 422
  rejection, insight, the OpenAPI contract, pagination, the signed webhook, and the trace id; the
  native tests prove the two CRC32 paths agree.
- `pytest` (19 passed), `ruff`, and `mypy` are all green, and the layer is committed.

You have shown the Day 5 point: a service becomes interoperable when it speaks a versioned contract
other systems can build against and validates input at its edge, and when it can drop a hot routine
into compiled code across a language boundary. The behaviour your CLI prints did not change; the
number of things that can now talk to your service did.
