"""Context managers (Level 3.2): a with block cleans up even when the body raises.

The concept, in plain words:
    A `with` block guarantees setup and teardown around some code. On entering the
    block Python calls the manager's __enter__ (open the resource); on leaving it,
    for ANY reason, Python calls __exit__ (close the resource). "Any reason"
    includes the body raising an error, so the cleanup still happens on the way
    out. You can write your own manager as a class, or more simply with the
    @contextmanager decorator around a generator that yields once.

Why a fresher should care:
    Forgetting to close files, connections, or locks (especially when an error
    interrupts the code) is a common source of leaks and stuck resources. A
    context manager makes correct cleanup automatic, so you cannot skip it by
    accident on the error path.

What this demo shows:
    The normal path prints opened, working, closed. The error path raises inside
    the block, yet "closed" still prints BEFORE the error is caught: proof that
    __exit__ ran during unwinding. Finally, a custom @contextmanager timer wraps a
    short sleep and reports how long the block took.

Run:  poetry run python demo_context_manager.py
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Self


class Resource:
    # A minimal context manager written as a class. The two special methods below
    # are what the `with` statement calls.
    def __enter__(self) -> Self:
        # Runs when the `with` block is entered. Here it stands in for acquiring a
        # resource. Returning self is what `as` would bind to.
        print("  opened")
        return self

    def __exit__(self, *exc: object) -> None:
        # Runs when the `with` block is left, whether it finished normally or an
        # exception is propagating out. The *exc parameters carry the exception
        # details (unused here). Returning None means "do not suppress the error".
        print("  closed")  # runs no matter what happened inside the block


@contextmanager
def timer(label: str) -> Iterator[None]:
    # A context manager written the short way: a generator with @contextmanager.
    # Everything before `yield` is the setup, everything after is the teardown.
    start = time.perf_counter()
    try:
        # `yield` hands control to the body of the `with` block; execution pauses
        # here until that block finishes.
        yield
    finally:
        # `finally` guarantees this teardown runs even if the block raised, so the
        # elapsed time is always printed.
        print(f"  {label}: {time.perf_counter() - start:.3f}s")


def main() -> None:
    # NORMAL PATH: enter, run the body, exit. Prints opened, working, closed.
    print("normal path:")
    with Resource():
        print("  working")

    # ERROR PATH: the body raises ValueError. Even so, __exit__ runs during the
    # unwinding, so "closed" prints before the except block catches the error.
    print("error path (it still closes):")
    try:
        with Resource():
            print("  working")
            raise ValueError("boom")
    except ValueError:
        # By the time we get here, "closed" has already been printed, which proves
        # the cleanup happened on the error path too.
        print("  caught ValueError, and notice 'closed' printed before this")

    # CUSTOM MANAGER: the timer wraps the block, measures its duration, and prints
    # it in the teardown after the sleep completes.
    print("a custom context manager (a timer):")
    with timer("slept"):
        time.sleep(0.05)


if __name__ == "__main__":
    main()
