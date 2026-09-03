"""Observability shared by every service: a correlation id and a health endpoint.

A middleware stamps each request with a correlation id (taken from the incoming header or
generated) and puts it on every log line, so one request that spans several services can be
followed end to end through logs that share one id. `install` also adds the `/health` route
the gateway and the platform poll.
"""

from __future__ import annotations

import contextvars
import logging
import sys
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="-")


class _CorrelationFilter(logging.Filter):
    """Attach the current correlation id to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Set record.correlation_id and keep the record."""
        record.correlation_id = _correlation_id.get()
        return True


def configure_logging(service: str) -> logging.Logger:
    """Return a logger that emits one structured JSON line per record, tagged with the id."""
    logger = logging.getLogger(service)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                f'{{"service":"{service}","cid":"%(correlation_id)s",'
                '"level":"%(levelname)s","msg":"%(message)s"}}'
            )
        )
        handler.addFilter(_CorrelationFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def current_correlation_id() -> str:
    """Return the correlation id for the request being handled."""
    return _correlation_id.get()


def install(app: FastAPI, service: str) -> None:
    """Add the correlation-id middleware and the /health route to a service's app."""

    @app.middleware("http")
    async def add_correlation_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Stamp the request with a correlation id and echo it back on the response."""
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        token = _correlation_id.set(cid)
        try:
            response = await call_next(request)
        finally:
            _correlation_id.reset(token)
        response.headers["X-Correlation-ID"] = cid
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        """Report liveness so the gateway and platform route only to healthy instances."""
        return {"status": "ok", "service": service}
