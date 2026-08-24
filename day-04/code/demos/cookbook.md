# Interoperable demos: a run cookbook

Twelve tiny, self-contained demos, one idea each, for the Interoperable topic (making Python talk
to the world safely). They fall into the same three levels as the lesson:

- **Level 1, the API edge:** a validated, versioned HTTP contract.
- **Level 2, the code boundary:** calling native code in the same process.
- **Level 3, a safe boundary:** crossing either boundary cheaply and safely.

Run them in the order below to follow that flow. The exact numbers (timings, speedups, uuids) will
differ on your machine; the pattern each demo shows is the point.

## Setup (once)

This folder is its own small Poetry project. Set it up once, then run any demo through Poetry:

```bash
poetry install
```

The API demos (`demo_edge_validation`, `demo_rest_contract`, `demo_response_model`,
`demo_pagination`, `demo_webhook_signature`) use `fastapi` and its test client, so run them through
Poetry, not a bare `python`. The rest use only the standard library. The API demos print one benign
`StarletteDeprecationWarning` on stderr; it does not affect the result and is safe to ignore.

## Run everything at once

```bash
for f in demo_edge_validation demo_rest_contract demo_response_model demo_pagination \
         demo_n_plus_one demo_webhook_signature demo_trace_id demo_json_interop \
         demo_ctypes_call demo_native_speed demo_coarse_vs_fine demo_error_translation; do
  echo "==== $f ===="; poetry run python "$f.py"; echo
done
```

On Windows PowerShell:

```powershell
'demo_edge_validation','demo_rest_contract','demo_response_model','demo_pagination','demo_n_plus_one','demo_webhook_signature','demo_trace_id','demo_json_interop','demo_ctypes_call','demo_native_speed','demo_coarse_vs_fine','demo_error_translation' | ForEach-Object { Write-Host "==== $_ ===="; poetry run python "$_.py" }
```

---

## Level 1, the API edge

### 1. `demo_edge_validation.py`

**Demonstrates:** validating input at the edge. A request model checks the incoming data before any
of your code runs, so a bad value is refused right at the boundary.

```bash
poetry run python demo_edge_validation.py
```

**Expect:** a valid dict builds a `ReviewIn`; a rating of 11 (outside 1 to 5) is caught as a pydantic
`ValidationError`, not passed through.

```text
valid review built : product_id='P1' rating=4
rejected at the edge: 1 error(s)
1 validation error for ReviewIn
rating
  Input should be less than or equal to 5 ...
```

### 2. `demo_rest_contract.py`

**Demonstrates:** a real, versioned REST contract. Honest status codes, and a machine-readable
OpenAPI spec other teams can build against.

```bash
poetry run python demo_rest_contract.py
```

**Expect:** health returns 200, a valid create returns 201, an invalid rating returns 422, and the
versioned route appears in the generated OpenAPI document.

```text
GET /health         : 200 {'status': 'ok'}
POST valid review   : 201 {'status': 'accepted'}
POST rating 11      : 422 (unprocessable)
/v1/reviews in spec : True
```

### 3. `demo_response_model.py`

**Demonstrates:** validating the response, not just the request. The API checks what it sends back,
so a malformed response is caught before it leaves the service.

```bash
poetry run python demo_response_model.py
```

**Expect:** a complete response builds; a dict missing `review_id` is rejected with a caught
`ValidationError` before it could be sent.

```text
valid response built : status='accepted' review_id='R-1001'
rejected before send : 1 error(s)
1 validation error for ReviewAccepted
review_id
  Field required ...
```

### 4. `demo_pagination.py`

**Demonstrates:** paging a large collection. A list endpoint returns one page plus the total, never
the whole collection, so the caller can walk the rest.

```bash
poetry run python demo_pagination.py
```

**Expect:** over 25 reviews, one page returns 5 items and echoes back the total, limit, and offset it
was given.

```text
total in collection : 25
limit echoed back   : 5
offset echoed back  : 5
items on this page  : 5 (not the whole list)
first id on page    : R-0005
last id on page     : R-0009
```

### 5. `demo_n_plus_one.py`

**Demonstrates:** the N+1 problem and the batching fix. A naive resolver runs one query per row; a
batched loader collects the ids and fetches them in one call.

```bash
poetry run python demo_n_plus_one.py
```

**Expect:** the naive version makes 6 calls (1 list read plus 5 author lookups); the batched version
makes 2, with the identical result.

```text
naive calls   : 6 (1 list read + 5 author lookups)
batched calls : 2 (1 list read + 1 batched lookup)
same result   : True
```

### 6. `demo_webhook_signature.py`

**Demonstrates:** verifying a webhook signature. A request from a system you do not control is
trusted only if its HMAC signature matches, compared with `hmac.compare_digest`.

```bash
poetry run python demo_webhook_signature.py
```

**Expect:** a genuine signature is accepted and a forged one is rejected. The signature value itself
varies with the payload.

```text
genuine call   : accepted
forged call    : rejected
```

### 7. `demo_trace_id.py`

**Demonstrates:** correlating logs with a trace id. One id minted at the edge is passed through every
service call, so all the log lines for a single request share it.

```bash
poetry run python demo_trace_id.py
```

**Expect:** two requests, each with its own uuid threaded through the edge, rating, and summary log
lines. Filter by one trace id and you see just that request's path. The uuids are random each run.

```text
--- request one ---
trace=<uuid-1> service=edge     received request for P1
trace=<uuid-1> service=rating   averaging ratings for P1
trace=<uuid-1> service=summary  building summary for P1 (avg 4.2)
result: P1: 4.2 stars
--- request two ---
trace=<uuid-2> service=edge     received request for P2
...
```

### 8. `demo_json_interop.py`

**Demonstrates:** JSON as the common language between systems. An object serializes to a JSON string
and rebuilds identically on the other side.

```bash
poetry run python demo_json_interop.py
```

**Expect:** a frozen dataclass goes out as a JSON string and comes back equal after the round trip.

```text
on the wire (str)   : {"product_id": "P1", "rating": 4}
restored object     : Review(product_id='P1', rating=4)
round trip matches  : True
```

---

## Level 2, the code boundary

### 9. `demo_ctypes_call.py`

**Demonstrates:** the two-language boundary. Python calls a C function directly, once you declare the
types and marshal the data across.

```bash
poetry run python demo_ctypes_call.py
```

**Expect:** Python calls C `strlen` and gets 5, after the string is encoded to bytes to cross the
boundary.

```text
native strlen of 'hello' -> 5
```

---

## Level 3, a safe boundary

### 10. `demo_native_speed.py`

**Demonstrates:** pushing a hot loop into compiled code. The same checksum in pure Python versus C.

```bash
poetry run python demo_native_speed.py
```

**Expect:** both agree, and the C version is far faster. The exact speedup depends on your machine
(often in the thousands).

```text
results match       : True
pure Python (s)     : 0.3406
zlib in C   (s)     : 0.000061
speedup             : ~5500x faster in C   (varies by machine)
```

### 11. `demo_coarse_vs_fine.py`

**Demonstrates:** keeping the boundary coarse-grained. One large crossing beats the same work split
into thousands of tiny crossings, because each crossing has a fixed cost.

```bash
poetry run python demo_coarse_vs_fine.py
```

**Expect:** one coarse call over the whole blob is several times faster than many per-chunk calls.
The exact ratio varies by machine.

```text
one coarse call (s) : 0.000210
4096 fine calls (s) : 0.000582
coarse is           : ~3x faster for the same work
```

### 12. `demo_error_translation.py`

**Demonstrates:** translating errors at the boundary. A low-level failure on the far side is turned
into a clean domain error your caller can handle, with the original cause preserved.

```bash
poetry run python demo_error_translation.py
```

**Expect:** a bad payload turns a raw `JSONDecodeError` into a clear domain error, keeping the
underlying cause.

```text
parsed good payload : {'product_id': 'P1', 'rating': 4}
domain error        : review payload was not valid JSON
underlying cause    : JSONDecodeError
```

---

Each demo also has a matching "Try it" pointer in the lesson at the topic it illustrates, and the
same ideas are then built for real in the liveLab (`reviews-insight`).
