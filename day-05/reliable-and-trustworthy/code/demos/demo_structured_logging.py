"""Emit structured, leveled logs with a trace id (trustworthiness): machine-filterable.

The concept, in plain words:
    A line like "handled review, took a while" reads fine to a human but a machine
    cannot search or group it. Structured logging writes one JSON object per line
    instead, with named fields: a level, an event, a trace_id, and whatever else
    matters. Now you can filter by level, group by trace_id, and chart durations, all
    without fragile text parsing. The trace_id is the key field: it ties every line from
    one request together so you can read that request's whole path.

Why a fresher should care:
    When something breaks in production, logs are often all you have. Structured lines
    turn a log search from guesswork over free text into a precise query: every line for
    this trace id.

What this demo shows:
    Two requests, each with a fixed trace_id ("9f2a" and "3b7c"). Each emits an info
    line when it starts and an info line when it finishes, as JSON objects carrying
    event, product_id, and a fixed duration_ms. Filtering the output by one trace id
    shows exactly that request's path.

Run:  poetry run python demo_structured_logging.py
"""

from __future__ import annotations

import json
from typing import Any


def log_line(level: str, trace_id: str, event: str, **fields: Any) -> None:
    """Print one structured log line: one JSON object, standard fields first."""
    record = {"level": level, "trace_id": trace_id, "event": event, **fields}
    print(json.dumps(record))


def handle_request(trace_id: str, product_id: str, duration_ms: int) -> None:
    """Handle one request: a start line and a finish line under the same trace id."""
    log_line("info", trace_id, "request_received", product_id=product_id)
    # (real work would happen here; the duration is fixed so the output never varies)
    log_line(
        "info",
        trace_id,
        "request_completed",
        product_id=product_id,
        duration_ms=duration_ms,
    )


def main() -> None:
    # Two requests with fixed ids and fixed durations, so the output is
    # identical every run.
    handle_request(trace_id="9f2a", product_id="P-77", duration_ms=12)
    handle_request(trace_id="3b7c", product_id="P-88", duration_ms=34)
    print('\nFilter these lines by trace_id "9f2a" to see just that request path.')


if __name__ == "__main__":
    main()
