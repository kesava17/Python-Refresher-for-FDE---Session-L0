"""Structured logging and simple SLI metrics (the dependability layer).

Two dependability habits live here, both built on the standard library so nothing heavy
is pulled in:

- Structured, leveled logging: one JSON line per event, always carrying the trace id, so a
  single request can be followed across services and machines. We use only `logging` and
  `json`. The line records `event`, `trace_id`, `duration_ms`, and `status`.
- Simple SLI (service level indicator) metrics: a request count, an error count, and a
  duration summary, hand rolled so the `/metrics` route needs no metrics library.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

# One named logger for the whole package. Handlers are attached once in configure_logging.
_logger = logging.getLogger("telemetry_insight")


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a single stream handler once, so each event becomes one line on stderr.

    Guarded by the handler check so repeated calls (a fresh app per test) do not stack
    duplicate handlers.
    """
    if _logger.handlers:
        return
    handler = logging.StreamHandler()
    # We format each record ourselves as JSON, so the handler passes the message through as-is.
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(level)
    _logger.propagate = False


def log_event(
    event: str, trace_id: str, duration_ms: float, status: int, **extra: object
) -> None:
    """Emit one structured JSON line. The trace id ties the line to a single request."""
    record: dict[str, object] = {
        "event": event,
        "trace_id": trace_id,
        "duration_ms": round(duration_ms, 3),
        "status": status,
    }
    record.update(extra)
    # Leveled: a server error (5xx) logs at ERROR, everything else at INFO.
    level = logging.ERROR if status >= 500 else logging.INFO
    _logger.log(level, json.dumps(record))


@dataclass
class Metrics:
    """A tiny in-memory SLI collector: two counts plus a running duration total."""

    requests: int = 0
    errors: int = 0
    duration_ms_sum: float = 0.0

    def record(self, duration_ms: float, status: int) -> None:
        # Called once per request. A 5xx counts as an error; shed (429) and 4xx do not.
        self.requests += 1
        if status >= 500:
            self.errors += 1
        self.duration_ms_sum += duration_ms

    def render(self) -> str:
        """Render the metrics as plain text in a Prometheus-like shape (easy to scrape)."""
        avg = self.duration_ms_sum / self.requests if self.requests else 0.0
        lines = [
            f"telemetry_requests_total {self.requests}",
            f"telemetry_errors_total {self.errors}",
            f"telemetry_request_duration_ms_sum {self.duration_ms_sum:.3f}",
            f"telemetry_request_duration_ms_avg {avg:.3f}",
        ]
        return "\n".join(lines) + "\n"
