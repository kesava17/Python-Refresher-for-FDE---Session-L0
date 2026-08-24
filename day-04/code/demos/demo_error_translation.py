"""Translate boundary errors (Level 3.5): turn a low-level failure into a clear domain error.

The concept, in plain words:
    Code at a boundary calls into something that can fail in its own vocabulary: a JSON parser
    raises JSONDecodeError, a driver raises a driver error. Leaking that raw error to your callers
    forces them to know about your internals. Instead, catch it and re-raise a domain error that
    says what went wrong in your terms, keeping the original attached as the cause.

Why a fresher should care:
    "raise NewError(...) from exc" is the whole trick: callers get a clean, named error they can
    handle, and you keep the original for the logs. It is the difference between an error that
    reads like your system and one that reads like a stranger's stack trace.

What this demo shows:
    parse_review takes a raw JSON payload. Good input parses to a dict. Bad input makes json.loads
    raise JSONDecodeError, which we catch and re-raise as ApiBoundaryError, with the cause chained.

Run:  poetry run python demo_error_translation.py
"""

from __future__ import annotations

import json
from typing import Any


class ApiBoundaryError(Exception):
    """A clear, domain-level error for anything that fails while reading input at the boundary."""


def parse_review(payload: str) -> dict[str, Any]:
    """Parse a raw JSON payload, translating any low-level parse failure into a domain error."""
    try:
        return dict(json.loads(payload))
    except json.JSONDecodeError as exc:
        # Re-raise in our own vocabulary, but keep the original attached with "from exc" so the
        # cause is preserved for logs and debugging.
        raise ApiBoundaryError("review payload was not valid JSON") from exc


def main() -> None:
    # A well-formed payload crosses the boundary cleanly.
    good = parse_review('{"product_id": "P1", "rating": 4}')
    print("parsed good payload :", good)

    # A broken payload raises the low-level error inside, which we present as a clean domain error.
    try:
        parse_review('{"product_id": "P1", rating: }')  # not valid JSON
    except ApiBoundaryError as exc:
        print("domain error        :", exc)
        print("underlying cause    :", type(exc.__cause__).__name__)


if __name__ == "__main__":
    main()
