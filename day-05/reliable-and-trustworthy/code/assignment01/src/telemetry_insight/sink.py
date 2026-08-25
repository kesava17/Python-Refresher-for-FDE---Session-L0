"""A downstream sink with a timeout and graceful degradation (the dependability layer).

Ingest must not fail just because a downstream system is slow or down. `forward_or_buffer`
tries to forward one reading to a configured sink URL with a short timeout. If the sink
times out or returns an error, we degrade gracefully: buffer the reading locally (here we
mark it as not forwarded and return it) instead of failing the request. A slow sink then
slows nothing upstream, and the caller still gets its reading accepted.
"""

from __future__ import annotations

import os

import httpx

# Where to forward readings. In real code this comes from configuration, not a default here.
SINK_URL = os.environ.get("SINK_URL", "http://localhost:9999/sink")

# A short timeout so a slow sink cannot hold up ingest. One second is generous for a
# same-datacenter hop and short enough to protect throughput.
_TIMEOUT_SECONDS = 1.0


async def forward_or_buffer(
    reading: dict[str, object], client: httpx.AsyncClient
) -> dict[str, object]:
    """Forward the reading within the timeout, or buffer it locally on any failure.

    On success the returned dict carries `forwarded: True`. On an `httpx.TimeoutException`
    (the sink was too slow) or any other `httpx.HTTPError` (connection refused, 5xx, and so
    on) we return the reading with `forwarded: False` rather than raising. The caller treats
    a buffered reading as accepted, so ingest keeps meeting its target under a failing sink.
    """
    try:
        response = await client.post(SINK_URL, json=reading, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
    except (httpx.TimeoutException, httpx.HTTPError):
        # Graceful degradation: keep the reading locally instead of failing the request.
        return {**reading, "forwarded": False}
    return {**reading, "forwarded": True}
