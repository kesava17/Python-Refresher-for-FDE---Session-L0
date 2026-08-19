"""asyncio (Level 2.3, the trap): a blocking call inside async freezes the whole loop.

The concept, in plain words:
    The async event loop shares one thread among all its jobs, and that sharing
    only works if every job gives control back with `await` while it waits. If a
    coroutine calls a plain blocking function (like time.sleep) instead of
    awaiting, it holds the single thread the entire time and nobody else can run.
    One badly written call stalls every other job on the loop.

Why a fresher should care:
    This is the number one async mistake: mixing a normal blocking library into
    async code. It quietly destroys all the concurrency you thought you had, and
    the symptom (everything is mysteriously slow) is easy to misread. The rule is
    to use async-aware waits inside async code.

What this demo shows:
    The same 20 tasks are run two ways. The "good" version awaits asyncio.sleep,
    so the waits overlap and finish in about 0.1 second. The "bad" version calls
    the blocking time.sleep, so each 0.1s wait freezes the loop in turn and the
    total climbs to roughly 2 seconds.

Run:  poetry run python demo_async_blocking_trap.py
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable, Coroutine
from typing import Any


async def good(_: int) -> None:
    # Correct: awaiting asyncio.sleep yields to the event loop, so while this
    # coroutine waits its tenth of a second, the loop runs the other coroutines.
    await asyncio.sleep(0.1)  # non-blocking: the loop runs the others meanwhile


async def bad(_: int) -> None:
    # WRONG on purpose: time.sleep is a plain blocking call. It does not yield to
    # the loop, so this coroutine holds the one thread for the full 0.1s and every
    # other task has to wait its turn. This is the bug the demo is exposing.
    # The noqa: ASYNC251 marker below silences the linter rule that flags a
    # blocking sleep inside async code, because here we are demonstrating it.
    time.sleep(0.1)  # noqa: ASYNC251


async def run(fn: Callable[[int], Coroutine[Any, Any, None]], label: str) -> None:
    # Run the given coroutine function over 20 items via gather (which tries to
    # overlap them) and print how long the whole batch took.
    start = time.perf_counter()
    await asyncio.gather(*(fn(i) for i in range(20)))
    print(f"{label:24s}: {time.perf_counter() - start:5.2f}s")


async def main() -> None:
    # The good version overlaps cleanly because every wait yields the loop.
    await run(good, "await asyncio.sleep")  # about 0.1s: the waits overlap
    # The bad version cannot overlap: each blocking sleep froze the loop in turn,
    # so the 20 waits stacked up to roughly 2 seconds.
    await run(bad, "blocking time.sleep")  # about 2.0s: each one froze the loop
    print("the blocking version is far slower: one bad call stalls everything.")


if __name__ == "__main__":
    # Start the event loop and run main() to completion.
    asyncio.run(main())
