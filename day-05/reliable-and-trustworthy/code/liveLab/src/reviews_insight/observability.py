"""Observability plumbing for a dependable service: structured logging, SLI metrics, capacity.

None of this changes what the API returns for a valid request. It makes the service operable:
you can read its request rate, error rate, and latency (the SLIs), follow one request across
services by its trace id, and let it report honestly whether it still has room to take work.
Everything here uses only the standard library, so there is no heavy dependency to carry.
"""

from __future__ import annotations

import json
import logging
import sys


def get_logger(name: str = "reviews_insight") -> logging.Logger:
    """Return a logger that writes one JSON object per line to stdout.

    Structured logs (one JSON object per line) are easy for a machine to parse and query. We
    configure the logger once; repeated calls return the same logger without adding handlers.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))  # the message is already JSON
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    logger.propagate = False  # do not also print through the root logger
    return logger


def log_request(
    logger: logging.Logger,
    *,
    event: str,
    trace_id: str,
    duration_ms: float,
    status: int,
) -> None:
    """Write one structured log line for a request, carrying the trace id from the middleware.

    The trace id is the same value the trace-id middleware echoes in the response header, so a
    log line and a client-visible request can be matched up when something goes wrong.
    """
    logger.info(
        json.dumps(
            {
                "event": event,
                "trace_id": trace_id,
                "duration_ms": round(duration_ms, 2),
                "status": status,
            }
        )
    )


class Metrics:
    """In-process SLI counters: request count, error count, and a request-duration summary.

    These are the three golden signals for request-driven work: rate (request count over time),
    errors (error count), and duration (latency). They are kept in plain in-memory counters and
    rendered as plain text at GET /metrics, so no external metrics library is needed.
    """

    def __init__(self) -> None:
        self.requests = 0
        self.errors = 0
        self.duration_ms_total = 0.0

    def observe(self, *, status: int, duration_ms: float) -> None:
        """Record one finished request. A 5xx status counts as a service error."""
        self.requests += 1
        if status >= 500:
            self.errors += 1
        self.duration_ms_total += duration_ms

    def render(self) -> str:
        """Render the counters as a tiny plain-text exposition, one metric per line."""
        avg = self.duration_ms_total / self.requests if self.requests else 0.0
        lines = [
            f"requests_total {self.requests}",
            f"errors_total {self.errors}",
            f"request_duration_ms_sum {self.duration_ms_total:.2f}",
            f"request_duration_ms_avg {avg:.2f}",
        ]
        return "\n".join(lines) + "\n"


class Capacity:
    """A gauge of in-flight requests, so readiness can reflect real capacity.

    The event loop runs request handlers cooperatively on one thread, so a plain integer is
    safe here: increment when a request starts, decrement when it finishes. When in-flight work
    reaches the limit the service has no free capacity, and readiness returns 503.
    """

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.in_flight = 0

    def acquire(self) -> None:
        self.in_flight += 1

    def release(self) -> None:
        self.in_flight -= 1

    def has_free(self) -> bool:
        return self.in_flight < self.limit
