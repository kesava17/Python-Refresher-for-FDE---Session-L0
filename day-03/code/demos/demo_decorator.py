"""Decorators (Level 3.1): add a cross-cutting concern in one place, used sparingly.

The concept, in plain words:
    A decorator wraps a function to add behaviour around it, without editing the function itself.
    It is the right tool for concerns that many functions share but none should be cluttered with,
    such as timing, logging, or caching. Used sparingly, it keeps that concern in one place.

Why a fresher should care:
    Copy-pasting the same logging or timing into twenty functions is a maintenance trap: change it
    once and you have nineteen stale copies. A decorator gives you one place to change.

What this demo shows:
    A traced() decorator prints a line before and after any function it wraps. Applying it to add()
    adds the tracing with no change to add() itself.

Run:  poetry run python demo_decorator.py
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

# ParamSpec captures the wrapped function's argument types and TypeVar its return type, so the
# decorated function keeps the exact same signature for the type checker.
P = ParamSpec("P")
R = TypeVar("R")


# The decorator: it takes a function and returns a wrapped version with tracing around it.
def traced(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)  # keep the wrapped function's name and docstring
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"-> calling {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} returned {result}")
        return result

    return wrapper


# Applying @traced adds the behaviour; add() itself stays a plain, focused function.
@traced
def add(a: int, b: int) -> int:
    return a + b


def main() -> None:
    # The call is wrapped, so you see the trace lines around the real work.
    total = add(2, 3)
    print("result:", total)  # 5


if __name__ == "__main__":
    main()
