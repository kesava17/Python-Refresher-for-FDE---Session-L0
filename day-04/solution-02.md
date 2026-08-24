# Solution 02 · Make transactions-insight interoperable, and prove bad requests fail safely

> The full worked solution for Assignment 02. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your Day 4 `transactions-insight` project, green, with its `LedgerService`, its
injected source and swappable strategy, the `timed` decorator, and a thin CLI composition root. This
solution adds the Day 5 interoperable layer: a native checksum routine that crosses into C, a typed
and versioned HTTP API whose scoring endpoint leans on that checksum, and a `serve` command so another
process can reach it. The maintainable layer from Day 3 is reused untouched. Use `poetry run` for
everything.

## Step 1: the web dependencies

The service needs a web framework, an in-process test client, and a server to run behind the CLI. Add
all three at once:

```bash
poetry add fastapi httpx uvicorn
```

FastAPI brings pydantic with it, so the request model needs no separate install. httpx is what
FastAPI's `TestClient` drives the app with in-process, so the contract tests run with no server to
start. uvicorn is the real server the `serve` command launches. With the packages in place, the new
imports in the next steps resolve cleanly.

## Step 2: the native checksum interop routine

The scoring endpoint needs one stable number per request, computed the same way every time and cheap
to run. Open a narrow, well-typed boundary into C and put the checksum there. Create
`src/transactions_insight/native.py`:

**`src/transactions_insight/native.py`**

```python
"""The two-language boundary (Day 5): a Python surface over native C code.

Two ideas live here. First, a direct call across the boundary with `ctypes`: Python hands a
byte buffer to the C library's `strlen` and gets a length back. That shows marshaling (a
Python str must be encoded to bytes before it can cross) and the argtypes/restype declarations
that make the crossing safe. Second, a checksum done two ways: a pure-Python CRC32, and the
standard library's `zlib.crc32`, which is the same algorithm written in C. The native CRC32 is
the validation routine our scoring endpoint leans on to turn a request into a stable number.
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

`_load_libc` finds the C standard library wherever the platform keeps it, so the same code runs on
Windows, Linux, and macOS. The two `_LIBC.strlen` lines are the crossing's safety rails: `argtypes`
and `restype` tell ctypes that `strlen` takes a `char*` and returns a `size_t`, and getting those
wrong yields garbage or a crash. `native_strlen` shows marshaling: a Python `str` has no native form C
understands, so it is encoded to `bytes` before it can cross. Then the two-language pattern:
`crc32_python` computes a CRC32 with the loop running in the interpreter one byte at a time, while
`crc32_native` gets the identical result from `zlib.crc32`, the same algorithm written in C. That
native call is the one the scoring endpoint will lean on for a stable number.

## Step 3: the API at the edge, with a scoring endpoint

The service can summarize a file, but nothing outside the process can hand it a transaction to score.
Give it an HTTP surface where every request is checked at the door and the contract is versioned from
day one. Create `src/transactions_insight/api.py`:

**`src/transactions_insight/api.py`**

```python
"""The API at the edge (Day 5): a versioned, validated HTTP surface over the service.

FastAPI plus pydantic give us the two habits from Section 1.1 for free. The pydantic model
validates incoming JSON at the boundary (a non-positive amount is rejected with a 422 before
our code runs), and the `/v1` prefix versions the contract. The scoring route then leans on the
native CRC32 from native.py to turn a validated request into one stable, checksum-derived number.
FastAPI also generates an OpenAPI document at `/openapi.json`, the machine-readable contract
other teams build against. Beyond scoring, a real API needs a few more practical pieces: a
response model checked on the way out, a paginated list, a signed webhook we can trust, and a
trace id that ties one request's logs together as it crosses services.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from transactions_insight.native import crc32_native

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class TransactionIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    account_id: str = Field(min_length=1)  # an empty account id is rejected with a 422
    amount: float = Field(gt=0)  # money in rupees; a non-positive amount is rejected with a 422
    currency: str = Field(min_length=3, max_length=3)  # a code like "US" (too short) fails here


class ScoreOut(BaseModel):
    """The scoring response contract, checked on the way out."""

    account_id: str
    score: int


class TransactionOut(BaseModel):
    """One accepted transaction as returned in a listing."""

    account_id: str
    amount: float
    currency: str


class TransactionPage(BaseModel):
    """A single page of transactions, plus the paging information to fetch the next one."""

    items: list[TransactionOut]
    total: int
    limit: int
    offset: int


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="transactions-insight", version="0.5.0")
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

    @app.post("/v1/score", response_model=ScoreOut)
    def score(txn: TransactionIn) -> ScoreOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        # We fold the three fields into one byte string and hand it to the native checksum,
        # so the same request always yields the same score. This is the interop routine at work.
        payload = f"{txn.account_id}:{txn.amount}:{txn.currency}".encode()
        return ScoreOut(account_id=txn.account_id, score=crc32_native(payload) % 1000)

    @app.post("/v1/transactions", status_code=201, response_model=TransactionOut)
    def submit(txn: TransactionIn) -> TransactionOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        store.append(
            {"account_id": txn.account_id, "amount": str(txn.amount), "currency": txn.currency}
        )
        return TransactionOut(account_id=txn.account_id, amount=txn.amount, currency=txn.currency)

    @app.get("/v1/transactions", response_model=TransactionPage)
    def list_transactions(limit: int = 20, offset: int = 0) -> TransactionPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [
            TransactionOut(
                account_id=row["account_id"],
                amount=float(row["amount"]),
                currency=row["currency"],
            )
            for row in page
        ]
        return TransactionPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.post("/v1/webhooks/transaction", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        store.append(
            {
                "account_id": str(payload["account_id"]),
                "amount": str(payload["amount"]),
                "currency": str(payload["currency"]),
            }
        )
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "transactions_insight.api:app".
app = create_app()
```

`TransactionIn` is the request contract, and FastAPI checks every incoming request against it at the
edge. Three `Field` constraints do the validation: `min_length=1` rejects an empty `account_id`,
`gt=0` rejects a non-positive `amount`, and `min_length=3, max_length=3` forces the `currency` to be
exactly three characters, so a code like `"US"` is refused. By the time `score` runs, `txn` is already
known good, so the handler never guesses whether its input is sane. It folds the three fields into one
byte string and hands that to `crc32_native`, taking the result modulo 1000, so the same request
always produces the same number in the range 0 to 999. The `/v1` prefix versions the contract, and the
module-level `app` at the bottom is the instance a real server loads.

Four more edge pieces sit on the same app, each the kind of thing a real HTTP service grows next to a
scoring route:

- **A response model.** `POST /v1/score` now declares `response_model=ScoreOut` and returns a
  `ScoreOut(...)`. The score formula is unchanged; the difference is that FastAPI validates the
  response on the way out too, so a route that drifted from its own contract fails loudly instead of
  shipping the wrong shape to callers.
- **A paginated list.** An in-memory `store` lives inside `create_app()`, so each app instance is
  independent. `POST /v1/transactions` validates its body with the same `TransactionIn`, appends to the
  store, and returns `201`. `GET /v1/transactions` returns one `TransactionPage`: the
  `store[offset : offset + limit]` slice as `items`, plus the full `total`, `limit`, and `offset`, so a
  caller can page through instead of pulling the whole collection at once.
- **A signed webhook.** `POST /v1/webhooks/transaction` is a request from a system we do not control,
  so arriving is not the same as being trusted. It recomputes the HMAC-SHA256 of the raw body under the
  shared `_WEBHOOK_SECRET` and compares it to the `x-signature` header with `hmac.compare_digest`, the
  constant-time compare. A mismatch raises `HTTPException(status_code=401)` before the body is parsed;
  only a verified request reaches the store.
- **A trace-id middleware.** `add_trace_id` runs for every route: it reuses an incoming `x-trace-id` or
  generates a fresh `uuid.uuid4().hex`, then sets that value on the response header, so one request can
  be followed across services (and, in real code, tied together in the logs).

## Step 4: the serve command

The API is written, but interoperable means another program can reach it over the network. Give the
CLI a `serve` command that starts the API on a real port. Open
`src/transactions_insight/cli.py`:

**`src/transactions_insight/cli.py`**

```python
"""Command line entry point (Day 5: adds a `serve` command for the HTTP API).

The CLI stays a thin surface. `summary` reads configuration, builds the concrete pieces (a CSV
source, a default strategy, and the service that uses them), wires them together, and prints the
result. `serve` starts the versioned HTTP API from api.py. All the real logic still lives in the
service and the API, so this surface stays small and easy to read.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from transactions_insight.config import Config
from transactions_insight.service import LedgerService, summarize_rows
from transactions_insight.sources import CsvTransactionSource
from transactions_insight.strategies import BySizeStrategy


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    transactions = 0
    accounts: set[str] = set()
    for record in records:
        transactions += 1
        accounts.add(record["account_id"])
    return {"transactions": transactions, "accounts": len(accounts)}


def summarize_validated(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 4: parse and reject bad rows. Now a thin alias over the service's shared logic."""
    return summarize_rows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="transactions-insight")
    parser.add_argument("command", choices=["summary", "serve"], help="what to do")
    parser.add_argument("--port", type=int, default=8000, help="port for the serve command")
    args = parser.parse_args()

    if args.command == "serve":
        # Imported lazily: only the serve path needs the web server, so the summary path stays light.
        import uvicorn

        print(f"serving transactions-insight on http://127.0.0.1:{args.port} (press Ctrl+C to stop)")
        uvicorn.run("transactions_insight.api:app", host="127.0.0.1", port=args.port)
        return

    config = Config.from_env()

    # Composition root: build the concrete source and strategy, inject them, run the service.
    source = CsvTransactionSource(config.data_path)
    strategy = BySizeStrategy()
    service = LedgerService(source, strategy)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"transactions: {result['transactions']}")
    print(f"accounts    : {result['accounts']}")
    print(f"rejected    : {result['rejected']}")


if __name__ == "__main__":
    main()
```

The CLI stays the same thin surface it was on Day 4: `summary` runs the batch path unchanged, and the
new `serve` branch starts the versioned API through uvicorn. Notice `import uvicorn` sits inside the
serve branch, imported lazily, so the everyday `summary` command never pays to load a web server it
does not use.

Run the batch summary, then start the server:

```bash
poetry run transactions summary
poetry run transactions serve
```

The summary prints exactly what Day 4 reported, timing line and all:

```text
[timed] summary: 0.3 ms
[dev] transactions-insight
transactions: 5
accounts    : 3
rejected    : 2
```

And `transactions serve` starts the API on `http://127.0.0.1:8000`, where `GET /health`,
`POST /v1/score`, the `GET`/`POST /v1/transactions` pair, `POST /v1/webhooks/transaction`,
`/openapi.json`, and the interactive docs at `/docs` are all live, every response carrying its
`x-trace-id`. Press Ctrl+C to stop it.

## Step 5: the contract tests (the deliverable proof)

This is the proof. One file exercises the whole edge: the liveness route answers, a valid request
scores, the versioned route is published in the contract, and, the deliverable, a bad request is
refused at the door with a `422` before any scoring logic runs. Create `tests/test_api.py`:

**`tests/test_api.py`**

```python
"""Day 5 contract tests: the API validates at the edge and exposes a real, versioned contract."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from transactions_insight.api import create_app

_WEBHOOK_SECRET = b"shared-webhook-secret"  # must match the secret the app uses


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _sign(body: bytes) -> str:
    return hmac.new(_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()


def test_health_route() -> None:
    assert _client().get("/health").json() == {"status": "ok"}


def test_score_valid_returns_int_score() -> None:
    client = _client()
    response = client.post(
        "/v1/score", json={"account_id": "A1", "amount": 10.0, "currency": "INR"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["account_id"] == "A1"
    # The score is a stable, checksum-derived integer in the range 0 to 999.
    assert isinstance(body["score"], int)
    assert 0 <= body["score"] < 1000


def test_bad_input_is_rejected_at_the_edge() -> None:
    client = _client()
    # A non-positive amount fails the gt=0 rule before our code runs.
    assert (
        client.post(
            "/v1/score", json={"account_id": "A1", "amount": -5, "currency": "INR"}
        ).status_code
        == 422
    )
    # A currency code of "US" is too short for the min_length=3 rule.
    assert (
        client.post(
            "/v1/score", json={"account_id": "A1", "amount": 10.0, "currency": "US"}
        ).status_code
        == 422
    )
    # An empty account_id fails the min_length=1 rule the same way.
    assert (
        client.post(
            "/v1/score", json={"account_id": "", "amount": 10.0, "currency": "INR"}
        ).status_code
        == 422
    )


def test_openapi_contract_exists() -> None:
    # FastAPI generates the machine-readable contract; the versioned route is in it.
    doc = _client().get("/openapi.json").json()
    assert "/v1/score" in doc["paths"]


def test_list_transactions_is_paginated() -> None:
    client = _client()
    for i in range(5):
        client.post(
            "/v1/transactions", json={"account_id": f"A{i}", "amount": 10.0, "currency": "INR"}
        )
    page = client.get("/v1/transactions", params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 5  # the total is reported so the caller can page through
    assert page["limit"] == 2
    assert page["offset"] == 2
    assert len(page["items"]) == 2  # only one page is returned, not all five


def test_webhook_accepts_a_valid_signature() -> None:
    client = _client()
    body = json.dumps({"account_id": "A9", "amount": 25.0, "currency": "INR"}).encode("utf-8")
    resp = client.post(
        "/v1/webhooks/transaction", content=body, headers={"x-signature": _sign(body)}
    )
    assert resp.status_code == 201
    assert client.get("/v1/transactions").json()["total"] == 1


def test_webhook_rejects_a_forged_signature() -> None:
    client = _client()
    body = json.dumps({"account_id": "A9", "amount": 25.0, "currency": "INR"}).encode("utf-8")
    resp = client.post("/v1/webhooks/transaction", content=body, headers={"x-signature": "forged"})
    assert resp.status_code == 401  # a bad signature is refused before the payload is used
    assert client.get("/v1/transactions").json()["total"] == 0


def test_trace_id_is_returned_and_echoed() -> None:
    client = _client()
    # With no trace id sent, the server generates one and returns it.
    assert client.get("/health").headers.get("x-trace-id")
    # With a trace id sent, the server echoes the same one back, so the request can be followed.
    resp = client.get("/health", headers={"x-trace-id": "abc123"})
    assert resp.headers["x-trace-id"] == "abc123"
```

What `test_bad_input_is_rejected_at_the_edge` proves, and why it is the deliverable:

- **A negative amount is refused:** posting `amount: -5` fails the `gt=0` rule, so the API answers
  `422` and the scoring code never runs. The service is never asked to score money that is not
  positive.
- **A short currency is refused:** posting `currency: "US"` is two characters, so it fails the
  `min_length=3` rule and comes back `422`. Only a real three-letter code reaches the handler.
- **An empty account is refused:** posting `account_id: ""` fails the `min_length=1` rule and returns
  `422` the same way. A transaction with no owner never gets a score.

Each of these is a bad request failing safely: pydantic turns it away at the boundary with a clear,
machine-readable status, instead of letting it through to produce a wrong number or a crash.
`test_score_valid_returns_int_score` fences the good path, confirming a valid request scores to an
integer in range, and `test_openapi_contract_exists` confirms `/v1/score` is published in
`/openapi.json`, the contract another team can build a client against without reading your code. The
`TestClient` drives the app in-process, so these are real HTTP round trips with no server to start.

Four more tests cover the new edge pieces, for eight in `test_api.py` in all:

- **`test_list_transactions_is_paginated`** posts five transactions, then asks for
  `limit=2, offset=2`. It asserts the page reports `total == 5` but returns only two `items`, so the
  list hands back one page at a time rather than the whole collection.
- **`test_webhook_accepts_a_valid_signature`** signs the body with the shared secret, posts it, and
  asserts `201` and that the store now holds one transaction. A correctly signed request is trusted.
- **`test_webhook_rejects_a_forged_signature`** posts the same body with `x-signature: "forged"` and
  asserts `401` and that the store is still empty. `hmac.compare_digest` refuses the forgery before the
  body is parsed, so an untrusted caller cannot write to the store.
- **`test_trace_id_is_returned_and_echoed`** checks that a request with no trace id still comes back
  with one the server generated, and that a request carrying `x-trace-id: "abc123"` gets the same value
  echoed, so one request can be followed across services.

Note the shared `_sign` helper and `_WEBHOOK_SECRET` mirror what the app computes: the test signs a
body exactly as the real sender would, which is the only way a genuine `201` is possible.

## Step 6: the native agreement tests

Before the scoring endpoint trusts the native checksum, pin the two CRC32 paths to the same answer, so
the number the endpoint returns is provably the same one the pure-Python routine would compute. Create
`tests/test_native.py`:

**`tests/test_native.py`**

```python
"""Day 5 native-boundary tests: the compiled path agrees with the pure-Python one."""

from __future__ import annotations

import zlib

from transactions_insight.native import crc32_native, crc32_python, native_strlen


def test_crc32_python_matches_native() -> None:
    # The pure-Python CRC32 and zlib's C CRC32 are the same algorithm, so they must agree.
    for text in ["", "hello", "transactions-insight", "A1:10.0:INR"]:
        data = text.encode("utf-8")
        assert crc32_python(data) == zlib.crc32(data) == crc32_native(data)


def test_native_strlen_matches_len_for_ascii() -> None:
    # Across the ctypes boundary, C strlen counts the same bytes Python does for ASCII text.
    assert native_strlen("hello") == 5
    assert native_strlen("") == 0
```

`test_crc32_python_matches_native` checks that the pure-Python CRC32, `zlib.crc32`, and `crc32_native`
all return the same value for a handful of inputs, including `"A1:10.0:INR"`, the exact shape of a
scored payload. If the native path ever drifted from the pure one, the score would silently change,
and this test catches that. `test_native_strlen_matches_len_for_ascii` confirms the ctypes crossing
counts the same bytes Python does. Correctness first: only once the two paths agree is it honest for
the endpoint to lean on the native one.

## Step 7: the carried reliability tests

Keep your Day 4 reliability tests exactly as they were. They still pass unchanged, because Day 5 only
added two edges around the model and the ledger, it did not alter them.

**`tests/test_models.py`**

```python
"""Tests for the Day 4 reliability layer: validated Transaction and the account ledger."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from transactions_insight.cli import summarize_validated
from transactions_insight.models import (
    AccountLedger,
    Transaction,
    TransactionParseError,
    parse_transaction,
)


def test_transaction_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        Transaction(account_id="A1", amount_paise=-5, currency="INR")  # not positive
    with pytest.raises(ValueError):
        Transaction(account_id="A1", amount_paise=100, currency="USD")  # unsupported
    with pytest.raises(ValueError):
        Transaction(account_id="", amount_paise=100, currency="INR")  # empty id


def test_transaction_is_frozen() -> None:
    txn = Transaction(account_id="A1", amount_paise=100, currency="INR")
    with pytest.raises(FrozenInstanceError):
        txn.amount_paise = 200  # type: ignore[misc]


def test_parse_rejects_malformed_rows() -> None:
    with pytest.raises(TransactionParseError):
        parse_transaction({"account_id": "A1", "amount": "free", "currency": "INR"})
    with pytest.raises(TransactionParseError):
        parse_transaction({"account_id": "A1", "amount": "10.0"})  # missing currency


def test_ledger_total_equals_sum_of_applied() -> None:
    ledger = AccountLedger()
    txns = [
        Transaction("A1", 100, "INR"),
        Transaction("A1", 250, "INR"),
        Transaction("A2", 500, "INR"),
    ]
    for txn in txns:
        ledger.apply(txn)
    # The invariant: the ledger total is exactly the sum of every amount applied.
    assert ledger.total() == sum(txn.amount_paise for txn in txns)
    assert ledger.balance("A1") == 350
    assert ledger.balance("A2") == 500


def test_summarize_counts_good_and_rejects_bad() -> None:
    rows = [
        {"account_id": "A1", "amount": "10.00", "currency": "INR"},
        {"account_id": "A2", "amount": "5.00", "currency": "INR"},
        {"account_id": "A3", "amount": "-5.00", "currency": "INR"},  # bad: not positive
        {"account_id": "A4", "amount": "10.00", "currency": "USD"},  # bad: unsupported
    ]
    result = summarize_validated(iter(rows))
    assert result == {"transactions": 2, "accounts": 2, "rejected": 2}
```

That the Day 4 model tests, and the Day 3 seam tests in `tests/test_service.py`, keep passing with no
edit is itself a small proof of the refactor: the reliability and maintainable layers went on working
while two new edges grew around them.

## Step 8: green gate and commit

```bash
poetry run pytest -q          # 20 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "day 5: versioned scoring endpoint, native checksum interop, serve command"
```

The 20 come together as the two new interop files (eight contract tests in `test_api.py`, two agreement
tests in `test_native.py`) on top of the carried Day 3 and Day 4 tests, all still green. A single
`StarletteDeprecationWarning` is expected and harmless; the run is clean otherwise.

## Done when

- `TransactionIn` validates at the edge: `account_id` non-empty, `amount` greater than 0, `currency`
  exactly three letters.
- `POST /v1/score` returns `{"account_id", "score"}` with the score derived from the native CRC32, and
  `/health` answers `{"status": "ok"}`.
- `native.py` crosses into C `strlen` once with declared argtypes and restype, and its two CRC32 paths
  return the same value.
- The score is `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`, stable for a given
  request.
- `transactions serve` starts the versioned API, with uvicorn imported lazily.
- The contract test proves a bad request fails safely: a negative amount, a too-short currency, and an
  empty account each return `422` before any logic runs.
- `/openapi.json` carries the versioned `/v1/score` route as the machine-readable contract.
- `POST /v1/score` declares a `ScoreOut` response model, `GET`/`POST /v1/transactions` give a paginated
  `TransactionPage` over an in-memory store, `POST /v1/webhooks/transaction` verifies an HMAC-SHA256
  `x-signature` and answers `401` on a mismatch, and the trace-id middleware echoes `x-trace-id` on
  every response.
- `transactions summary` still prints `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- `pytest` reports 20 passed (eight in `test_api.py`), and `ruff` and `mypy` are both clean, and the
  layer is committed.

You have built the interoperable layer: the same maintainable service, now reachable over a validated,
versioned HTTP contract at one edge and leaning on a native checksum routine at the other. The edge
speaks a contract that turns bad input away at the door and publishes itself as OpenAPI; down in the
code, a narrow, well-typed boundary into C computes one stable score per request. The deliverable
proof is small and sharp: send a negative amount, a two-letter currency, or an empty account, and each
is refused with a `422` before a single line of scoring logic runs. That is a bad request failing
safely, which is exactly what money code at an open edge must guarantee.
