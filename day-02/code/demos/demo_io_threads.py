"""Threads (Level 2.1): overlapping waits makes IO-bound work finish much sooner.

The concept, in plain words:
    IO-bound work spends most of its time WAITING, not computing: waiting for a
    network reply, a disk read, a database answer. While one thread is parked on
    such a wait, it is not using the CPU, so the GIL is free and another thread
    can run. Threads let all those idle waits overlap instead of stacking up one
    behind another.

Why a fresher should care:
    Most everyday backend work is IO-bound (calling services, reading files), and
    this is the one case where threads genuinely help in Python. Knowing that
    threads shine on waiting (and not on computing) tells you exactly when to
    reach for them.

What this demo shows:
    Twenty tasks that each wait one tenth of a second. Run one after another they
    take about 2 seconds (20 times 0.1); run on a thread pool the waits overlap
    and the whole batch finishes in roughly 0.1 second.

Run:  poetry run python demo_io_threads.py
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor


def io_work(_: int) -> None:
    """Spends its time waiting, not computing (IO-bound)."""
    # time.sleep parks this thread without using the CPU. During the sleep the
    # GIL is released, so other threads are free to run: that release is what
    # makes the waits able to overlap.
    time.sleep(0.1)  # stands in for a network reply or a disk read


def main() -> None:
    # Twenty independent tasks. The argument value is not used by io_work; we just
    # need twenty things to wait on.
    tasks = list(range(20))

    # SERIAL (slow) version: call io_work one at a time in a plain loop. Each 0.1s
    # wait finishes before the next begins, so the total is the sum of them all.
    start = time.perf_counter()
    for t in tasks:
        io_work(t)
    print(f"serial     : {time.perf_counter() - start:5.2f}s  (20 waits, one after another)")

    # CONCURRENT (fast) version: hand all twenty tasks to a pool of 20 threads.
    # They all start their 0.1s wait at nearly the same moment, so the waits
    # happen in parallel and the batch finishes in about the time of a single wait.
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=20) as pool:
        # pool.map returns results as each task completes; we only care that they
        # all run, so we loop and discard the (None) results.
        for _ in pool.map(io_work, tasks):
            pass
    print(f"concurrent : {time.perf_counter() - start:5.2f}s  (the waits overlap)")


if __name__ == "__main__":
    main()
