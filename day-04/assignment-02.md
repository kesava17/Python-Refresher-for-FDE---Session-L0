# Assignment 02 · Make transactions-insight interoperable, and prove bad requests fail safely

> Offline practice for Day 5. You made `reviews-insight` interoperable in class, giving it a
> validated, versioned HTTP surface at one end and a native fast path at the other. Now do the same
> Day 5 layer on your `transactions-insight` service, and add the one thing money code always needs
> at its edge: a scoring endpoint whose bad requests are turned away at the door.

This is a do-it-yourself assignment. Day 5 is about being **interoperable**. Your Day 4
transactions service is maintainable: the summary logic lives in one place, the data source is
injected behind a Protocol, the categorization rule is swappable, one decorator carries the timing,
and the CLI just wires the pieces together. But it only talks to itself. Nothing outside the process
can send it a transaction to score, and nothing inside it reaches into compiled code for a step that
should be fast and stable. You will open both ends: a typed HTTP contract at the edge that validates
every request before your code runs, and a native checksum routine that turns a validated request
into one stable number.

Start from your Day 4 `transactions-insight` project, green, with its `LedgerService`, its two
seams, and the `timed` decorator all in place.

## The goal

1. Add a **typed API at the edge**: a `TransactionIn` pydantic model that validates every request at
   the boundary (a non-empty `account_id`, a positive `amount`, a currency of exactly three
   letters), a `/v1` prefix that versions the contract, and a `/health` liveness route.
2. Add a **versioned scoring endpoint**, `POST /v1/score`, that returns a stable score for a valid
   transaction and publishes itself in the machine-readable contract at `/openapi.json`.
3. Add a **native checksum interop routine**: a `ctypes` call into C `strlen` that shows marshaling
   across the boundary, and a CRC32 written two ways, pure Python versus zlib's C implementation.
4. **Wire the score to the native checksum**: fold the three validated fields into one byte string
   and score it as `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`, so the same
   request always yields the same number.
5. **Serve it**: a `transactions serve` command starts the versioned API so another process can
   actually reach it.
6. **Prove the contract fails safely** with tests: a negative `amount`, a too-short `currency`, or an
   empty `account_id` each come back as a `422` before any of your logic runs. That is the
   deliverable.

Then add the four things any real API grows next to a scoring route, each proven by its own test:

7. **A response model on the scoring endpoint**: a `ScoreOut(account_id, score)` pydantic model set as
   the `response_model` on `POST /v1/score`, so the response is validated on the way out, not just the
   request on the way in. The score formula is unchanged.
8. **A paginated transactions list**: an in-memory store, a `POST /v1/transactions` that validates with
   `TransactionIn` and returns `201`, and a `GET /v1/transactions?limit=20&offset=0` that returns one
   page as a `TransactionPage(items, total, limit, offset)` rather than the whole collection.
9. **A signed webhook**, `POST /v1/webhooks/transaction`: verify an `x-signature` HMAC-SHA256 header
   over the raw request body against a shared secret with `hmac.compare_digest`, answer `401` on a
   mismatch, and store the transaction only once the signature checks out.
10. **A trace-id middleware**: an HTTP middleware that reuses an incoming `x-trace-id` header or
    generates a new `uuid.uuid4().hex`, and echoes it on the response, so one request can be followed
    across services.

By the end you have an interoperable service: a validated, versioned contract at the edge, a native
checksum routine feeding a stable score, a contract test that proves a bad request is refused at the
door, and the four routine edge pieces (a checked response, a paginated list, a signed webhook, and a
trace id) every real HTTP service needs.

## The starting point

You already have the Day 4 transactions service: a validated `Transaction` model (frozen, money in
paise), an honest reject path, a trustworthy `AccountLedger`, a `LedgerService` handed both its
source and its strategy, the `timed` decorator, and a thin CLI composition root. Reuse all of it
unchanged. Day 5 does not touch the maintainable layer; it adds two new edges around it.

Keep your `transactions-insight` sample CSV (`account_id,ts,amount,currency`) with its five good INR
rows across three accounts plus the two bad rows. The batch summary target stays exactly the same:
`transactions: 5`, `accounts    : 3`, `rejected    : 2`.

## What you have to build

1. **The web dependencies.** Add `fastapi`, `httpx`, and `uvicorn` to the project: FastAPI and its
   bundled pydantic for the typed contract, httpx for the in-process test client, uvicorn for the
   real server behind the `serve` command.
2. **A native interop module.** A `native.py` that loads the C standard library with `ctypes`,
   declares `strlen`'s argument and return types, exposes `native_strlen(text)` that crosses the
   boundary once, and gives a CRC32 two ways: `crc32_python(data)` with the loop in the interpreter
   and `crc32_native(data)` from `zlib.crc32`, the same algorithm written in C.
3. **A typed API with a scoring endpoint.** An `api.py` with a `create_app()` factory, a
   `TransactionIn` pydantic model whose fields validate at the edge (`account_id` min length 1,
   `amount` greater than 0, `currency` exactly three characters), a `/health` route, and a
   `POST /v1/score` route that returns `{"account_id": ..., "score": ...}` where the score is the
   native CRC32 of `f"{account_id}:{amount}:{currency}"` modulo 1000. Then four more edge pieces on the
   same app: a `ScoreOut` response model on `POST /v1/score`, an in-memory store behind a
   `POST /v1/transactions` (201) and a paginated `GET /v1/transactions` (with `TransactionOut` and
   `TransactionPage` models), a signed `POST /v1/webhooks/transaction` that verifies an HMAC-SHA256
   `x-signature`, and a trace-id middleware that echoes an `x-trace-id` header.
4. **The `serve` command.** Extend the CLI so `transactions serve` starts the versioned API through
   uvicorn on a real port, with the web server imported lazily so the everyday `summary` path stays
   light.
5. **The contract tests (the deliverable).** A `test_api.py` of eight tests: it checks the `/health`
   route, checks a valid score comes back as an integer in range, proves a bad request fails safely
   with a `422` (negative amount, too-short currency, empty account), confirms the versioned route is
   in `/openapi.json`, and then covers the four new edge pieces (pagination reports a `total` and
   returns one page, the webhook accepts a valid signature and refuses a forged one, and the trace id
   is generated and echoed). Plus a `test_native.py` that pins the two CRC32 paths to the same answer
   before anyone trusts the fast one.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the web dependencies

Add the three packages so the imports resolve:

```bash
poetry add fastapi httpx uvicorn
```

Hint: pydantic arrives bundled with FastAPI, so you do not add it separately. httpx is what FastAPI's
`TestClient` drives the app with in-process, so the contract tests need no running server.

### Level 2: the native checksum routine

Create `native.py`. Load the C standard library with a small helper that returns `msvcrt` on Windows
and the library named `c` elsewhere. Declare `strlen`'s `argtypes` as `[ctypes.c_char_p]` and its
`restype` as `ctypes.c_size_t`, then write `native_strlen(text)` that encodes the string to bytes and
calls across once. Add `crc32_python(data)` with the classic bit-by-bit loop and `crc32_native(data)`
that returns `zlib.crc32(data)`.

Hint: the encoding step is the marshaling. A Python `str` has no native form C understands, so it is
encoded to `bytes` before it can cross. The two CRC32 functions are the same algorithm; the whole
point is that they must agree, which is what makes the native one safe to lean on.

### Level 3: the API with a scoring endpoint

Create `api.py`. Write a `TransactionIn(BaseModel)` with `account_id: str = Field(min_length=1)`,
`amount: float = Field(gt=0)`, and `currency: str = Field(min_length=3, max_length=3)`. Write a
`create_app()` factory that builds a `FastAPI` instance, adds a `GET /health` returning
`{"status": "ok"}`, and adds a `POST /v1/score` that folds the validated fields into one byte string
and returns `{"account_id": txn.account_id, "score": crc32_native(payload) % 1000}`. Expose a
module-level `app = create_app()` at the bottom so a server can load it by name.

Hint: by the time `score` runs, `txn` is already valid. The edge rejected any bad input, so the
handler never has to check whether its input is sane; it just computes the number. That is validate
at the edge, and the `/v1` prefix is the versioning that lets you ship a `/v2` later without breaking
today's callers.

Now add the four edge pieces to the same `create_app()`. Build them one at a time and re-run the
tests after each:

1. **Response model.** Add a `ScoreOut(BaseModel)` with `account_id: str` and `score: int`, set it as
   `response_model=ScoreOut` on `POST /v1/score`, and return a `ScoreOut(...)`. The formula does not
   change; now the response is validated on the way out too.
2. **Pagination.** Create an in-memory `store` list inside the factory (so each app instance is
   independent). Add `TransactionOut` and `TransactionPage(items, total, limit, offset)` models. Add
   `POST /v1/transactions` (`status_code=201`, body validated by `TransactionIn`) that appends to the
   store, and `GET /v1/transactions` with `limit: int = 20` and `offset: int = 0` that returns the
   `store[offset : offset + limit]` slice plus the full `total`, so a caller can page through.
3. **Signed webhook.** Add an async `POST /v1/webhooks/transaction` that reads the raw body, computes
   `hmac.new(secret, raw, hashlib.sha256).hexdigest()`, compares it to the `x-signature` header with
   `hmac.compare_digest`, raises `HTTPException(status_code=401)` on a mismatch, and only then stores
   the transaction. Keep the shared secret in a module constant (in real code it comes from
   configuration, never hard-coded).
4. **Trace-id middleware.** Add an `@app.middleware("http")` function that reads `x-trace-id` from the
   request or falls back to `uuid.uuid4().hex`, calls `call_next`, and sets the same value on the
   response's `x-trace-id` header.

Hint: the webhook cannot trust its caller, so it verifies the signature over the raw body before it
parses anything. `hmac.compare_digest` is the constant-time compare that avoids leaking, byte by byte,
how much of a forged signature was right. The middleware runs for every route, so even `/health`
answers with a trace id.

### Level 4: the serve command

Open `cli.py` and add `serve` to the command choices, plus a `--port` argument defaulting to 8000. In
`main`, branch on `serve` first: import uvicorn lazily inside the branch, print a one-line "serving"
notice, and call `uvicorn.run("transactions_insight.api:app", host="127.0.0.1", port=args.port)`. The
`summary` path stays exactly as it was on Day 4.

Hint: put `import uvicorn` inside the serve branch, not at the top of the file, so the everyday
`summary` command never pays to load a web server it does not use. The CLI stays the thin surface it
has always been.

### Level 5: the contract tests (the deliverable)

This is the proof. In `tests/test_api.py`, build a fresh app per test with `TestClient(create_app())`.
Assert `/health` returns `{"status": "ok"}`. Assert a valid `POST /v1/score` returns `200` with an
integer score in the range 0 to 999. Then the deliverable: assert that a negative `amount`, a
`currency` of `"US"`, and an empty `account_id` each return `422`. Finally, assert `/v1/score` is a
key in `/openapi.json`'s `paths`.

Then add four more tests for the new edge pieces, for eight tests in `test_api.py` in all:

- **Pagination.** POST five transactions, `GET /v1/transactions?limit=2&offset=2`, and assert
  `total == 5`, `limit == 2`, `offset == 2`, and that only two `items` come back, not all five.
- **Webhook accepts a valid signature.** Sign a JSON body with the shared secret, POST it with that
  `x-signature`, and assert `201` and that the store now holds one transaction.
- **Webhook refuses a forged signature.** POST the same body with `x-signature: "forged"` and assert
  `401` and that the store is still empty (a bad signature is refused before the payload is used).
- **Trace id.** Assert a request with no `x-trace-id` still comes back with one, and a request that
  sends `x-trace-id: "abc123"` gets the same value echoed back.

Hint: the `422` is the whole point. pydantic turns the bad request away at the boundary before any
scoring code runs, so a caller that sends garbage gets a clear, machine-readable refusal instead of a
wrong number or a crash. That is a bad request failing safely. The webhook test is the same idea for a
caller you do not control: a forged signature is turned away with a `401` before the body is trusted.

### Level 6: the native agreement tests

In `tests/test_native.py`, loop over a handful of inputs and assert
`crc32_python(data) == zlib.crc32(data) == crc32_native(data)` for each, so the fast path is proven to
match the slow one. Add a check that `native_strlen` counts the same bytes Python does for ASCII text.

Hint: correctness before trust. Only once the two CRC32 paths agree is it honest to lean on the native
one inside the scoring endpoint.

### Level 7: green gate and commit

Run ruff and mypy strict, make the new interop tests and the carried Day 3 and Day 4 tests pass,
confirm the batch summary output is unchanged, then commit the Day 5 layer on top of your Day 4
transactions project.

## Done when

- [ ] `TransactionIn` validates at the edge: `account_id` non-empty, `amount` greater than 0,
  `currency` exactly three letters.
- [ ] `POST /v1/score` returns `{"account_id", "score"}` with the score derived from the native
  CRC32, and `/health` answers `{"status": "ok"}`.
- [ ] `native.py` crosses into C `strlen` once with declared argtypes and restype, and its two CRC32
  paths return the same value.
- [ ] The score is `crc32_native(f"{account_id}:{amount}:{currency}".encode()) % 1000`, stable for a
  given request.
- [ ] `transactions serve` starts the versioned API, with uvicorn imported lazily.
- [ ] The contract test proves a bad request fails safely: a negative amount, a too-short currency,
  and an empty account each return `422` before any logic runs.
- [ ] `/openapi.json` carries the versioned `/v1/score` route as the machine-readable contract.
- [ ] `POST /v1/score` declares a `ScoreOut` response model, so the response is validated on the way
  out as well as the request on the way in.
- [ ] `GET /v1/transactions?limit=&offset=` returns one `TransactionPage` (`items`, `total`, `limit`,
  `offset`), and `POST /v1/transactions` validates with `TransactionIn` and returns `201`.
- [ ] `POST /v1/webhooks/transaction` verifies the `x-signature` HMAC-SHA256 with `hmac.compare_digest`
  and answers `401` on a mismatch, storing the transaction only when the signature checks out.
- [ ] The trace-id middleware reuses an incoming `x-trace-id` or generates a `uuid.uuid4().hex`, and
  echoes it on the response for every route.
- [ ] `test_api.py` holds eight tests: health, valid score, the `422` deliverable, the OpenAPI
  contract, pagination, the webhook accept and refuse pair, and the trace id.
- [ ] `transactions summary` still prints `transactions: 5`, `accounts    : 3`, `rejected    : 2`.
- [ ] `pytest` reports 20 passed (one `StarletteDeprecationWarning` is expected), and `ruff check` and
  `mypy src` are both clean, and the layer is committed.

When every box is ticked, you have built the interoperable layer: the same maintainable service, now
reachable over a validated, versioned HTTP contract at one edge and leaning on a native checksum
routine at the other. The deliverable proof is small and sharp: send it a bad request, and it is
refused at the door with a `422`, before a single line of your scoring logic runs. The worked solution
is in `solution-02.md` if you want to compare, but try first.
