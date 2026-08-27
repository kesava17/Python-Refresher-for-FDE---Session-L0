"""A single decorator for a cross-cutting concern (Day 3): timing, used sparingly.

Timing is a concern that many methods share but none of them should be cluttered with. A
decorator lets us add it in one place and apply it by name, without editing the logic it
wraps. The typing (ParamSpec plus TypeVar) preserves the wrapped function's signature, so
mypy still checks callers exactly as before.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(label: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that prints how long the wrapped call took, labelled by `label`."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)  # keep the wrapped function's name and docstring
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                # `finally` runs whether the call returned or raised, so the timing is
                # always reported, even on failure.
                elapsed_ms = (time.perf_counter() - start) * 1000
                print(f"[timed] {label}: {elapsed_ms:.1f} ms")

        return wrapper

    return decorator
