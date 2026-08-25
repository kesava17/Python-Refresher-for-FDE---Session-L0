# HTTP request files

Hand-run requests against the reviews-insight API, one click per request. These are
for exploring the running service by hand. The automated contract tests live in
`tests/test_api.py` and run under `poetry run pytest`.

## Prerequisites

1. Install the project once: `poetry install`
2. Start the server: `poetry run reviews serve` (listens on `http://127.0.0.1:8000`; add `--port N` to change it, then update `@host` in the files).
3. Open a `.http` file in an editor with a REST client:
   - VS Code with the "REST Client" extension, or
   - a JetBrains IDE (built-in HTTP Client).
   Click "Send Request" above each request.

## The files

| File | What it covers |
| --- | --- |
| `reviews.http` | Health, create (valid and two rejected-at-the-edge cases), pagination, insight, and the OpenAPI contract. |
| `webhook.http` | The signed webhook: a valid HMAC signature is accepted, a forged one is refused. |
| `trace-id.http` | The trace id in the response headers, both generated and echoed. |

## Note on the webhook signature

The `x-signature` in `webhook.http` is an HMAC-SHA256 over the exact request body,
so it is pinned to that body. If you change the body, recompute the signature (the
command is in the file). The shared secret is `shared-webhook-secret`.
