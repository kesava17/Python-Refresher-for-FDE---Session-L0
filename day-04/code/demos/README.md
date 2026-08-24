# Day 5 demos: run the ideas, do not just read them

Each script is a tiny, self-contained demonstration of one idea from the Day 5 lesson (making
Python interoperable: a validated API at the edge, and the two-language boundary to native code).
This folder is its own small Poetry project, so you run the demos the same way as everything else
in this course. Set it up once, then run any demo:

```bash
poetry install                           # once, from this demos/ folder
poetry run python demo_edge_validation.py
```

The API demos need `fastapi` and `httpx` (both declared here), so run them through Poetry rather
than a bare `python`. The rest use only the standard library.

| Demo | Lesson topic | What you should see |
| --- | --- | --- |
| `demo_edge_validation.py` | 1.1 validate at the edge | a valid dict builds a ReviewIn; a rating of 11 is rejected with a caught pydantic ValidationError |
| `demo_rest_contract.py` | 1.2 / 1.3 REST, versioned, real contract | health returns ok, a valid POST returns 201, rating 11 returns 422, and the OpenAPI spec lists /v1/reviews |
| `demo_ctypes_call.py` | 2.1 / 2.2 the two-language boundary | Python calls C strlen across the boundary and prints 5, after marshaling the string to bytes |
| `demo_native_speed.py` | 3.2 push a hot loop into compiled code | a pure-Python CRC32 and zlib.crc32 agree, and the C version is far faster (printed speedup) |
| `demo_coarse_vs_fine.py` | 3.1 keep the boundary coarse-grained | one coarse call over the whole blob beats the same work split into thousands of per-chunk calls |
| `demo_error_translation.py` | 3.5 translate boundary errors | a bad payload turns a low-level JSONDecodeError into a clean ApiBoundaryError, cause preserved |
| `demo_json_interop.py` | JSON as the lingua franca | a frozen dataclass serializes to a JSON string and rebuilds identically after the round trip |
| `demo_response_model.py` | 1.4 validate the response too | a complete ReviewAccepted builds; a dict missing review_id is rejected with a caught pydantic ValidationError |
| `demo_pagination.py` | 1.5 page large collections | a page over 25 reviews returns 5 items, total 25, and the limit and offset it was given, never the whole list |
| `demo_n_plus_one.py` | 1.6 the N+1 problem and batching | a naive resolver over 5 reviews makes 6 calls; the batched version makes 2, with the same names |
| `demo_webhook_signature.py` | 1.7 verify webhook signatures | a correct HMAC-SHA256 signature is accepted and a forged one rejected, compared with hmac.compare_digest |
| `demo_trace_id.py` | 1.8 correlate logs with a trace id | one uuid minted at the edge threads through two service calls, so all log lines for a request share one id |

The exact numbers do not matter; the pattern is the point. The lesson points you to each of these
with a "Try it" note at the matching topic.
