"""asyncio (Level 2.3): one thread runs many waits at once with an event loop.

The concept, in plain words:
    asyncio runs on a single thread with an "event loop": a scheduler that keeps
    a list of jobs. When a job hits an `await` on something that waits, it hands
    control back to the loop, which starts or resumes another job in the
    meantime. No extra threads or processes are involved; the loop just fills the
    idle time of one waiting job with the work of others.

Why a fresher should care:
    async is how modern Python handles thousands of network calls at once without
    the memory cost of thousands of threads. The catch is that overlap only
    happens when you actually let the waits run together (gather), not when you
    `await` them strictly one at a time.

What this demo shows:
    Fifty tasks that each wait one tenth of a second. Awaited one by one they add
    up to a few seconds; gathered so their waits overlap, the whole batch
    finishes in roughly the time of a single wait (about 0.1 second).

Run:  poetry run python demo_async.py
"""

from __future__ import annotations

import asyncio
import time


async def io_work(_: int) -> None:
    # `await asyncio.sleep(0.1)` waits a tenth of a second WITHOUT blocking the
    # thread: at the await point this coroutine steps aside and the event loop is
    # free to run other coroutines until the timer is up.
    await asyncio.sleep(0.1)  # non-blocking: hands control back to the loop while it waits


async def main() -> None:
    # Fifty independent units of waiting work.
    tasks = range(50)

    # SLOW pattern: await each coroutine one at a time. Because we do not move on
    # until the current wait finishes, the loop has nothing else to overlap, so
    # the times add up just like a plain serial loop.
    start = time.perf_counter()
    for t in tasks:
        await io_work(t)
    print(f"awaited one by one   : {time.perf_counter() - start:5.2f}s")

    # FAST pattern: asyncio.gather starts all fifty coroutines and lets the loop
    # interleave them. All fifty waits are in flight at once, so the batch
    # finishes in about the length of one wait.
    start = time.perf_counter()
    await asyncio.gather(*(io_work(t) for t in tasks))
    print(f"gathered concurrently: {time.perf_counter() - start:5.2f}s")


if __name__ == "__main__":
    # asyncio.run starts the event loop, runs main() to completion, then shuts the
    # loop down. It is the standard entry point into async code.
    asyncio.run(main())
