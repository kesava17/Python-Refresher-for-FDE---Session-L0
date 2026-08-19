"""Threads (Level 2.1, the catch): shared changing data across threads loses updates.

The concept, in plain words:
    When several threads read and update the same value with no coordination, two
    of them can read the same starting number, both add one, and both write back
    the same result. One of the two increments is silently lost. This is a "race
    condition": the answer depends on the accidental timing of which thread runs
    when. A lock fixes it by letting only one thread touch the value at a time.

Why a fresher should care:
    Lost-update bugs are invisible in a quick test (small runs often look right)
    and then corrupt counters, balances, or tallies in production under load.
    They are hard to reproduce because they depend on timing. Knowing to guard
    shared mutable state with a lock is a core safety habit.

What this demo shows:
    Eight threads each add one 5000 times, so the correct total is 40000. The
    unguarded version comes out well short of 40000 (updates were lost); the
    lock-guarded version lands on exactly 40000 every time.

Run:  poetry run python demo_thread_race.py
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Eight workers, each doing 5000 increments, so a correct run totals 40000.
WORKERS = 8
PER_WORKER = 5_000
EXPECTED = WORKERS * PER_WORKER


def main() -> None:
    # UNSAFE version. Every worker reads the value, then writes it back, with no
    # lock. The tiny time.sleep(0) is a yield: it lets another thread run in the
    # gap between the read and the write, which is exactly the window where a real
    # race loses updates. It does not create the bug; it just makes the bug show
    # up every time instead of only sometimes.
    unsafe = {"n": 0}

    def add_unsafe(_: int) -> None:
        for _ in range(PER_WORKER):
            current = unsafe["n"]  # read the current value
            time.sleep(0)  # yield to another thread right in the vulnerable gap
            unsafe["n"] = current + 1  # write back a possibly-stale value

    # Run all eight unsafe workers together; list() waits for them all to finish.
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(add_unsafe, range(WORKERS)))
    # The printed total is below 40000 because concurrent read-then-write pairs
    # overwrote each other. The exact shortfall varies run to run.
    print(f"unsafe : {unsafe['n']:>7}  (expected {EXPECTED}: many updates were lost)")

    # SAFE version. A lock makes the read-then-write step atomic: while one thread
    # holds the lock, no other thread can read or write, so nothing is lost.
    safe = {"n": 0}
    lock = threading.Lock()

    def add_safe(_: int) -> None:
        for _ in range(PER_WORKER):
            # The `with lock:` block acquires the lock on entry and releases it on
            # exit, so the whole increment happens as one indivisible step.
            with lock:
                safe["n"] += 1

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(add_safe, range(WORKERS)))
    # With the lock in place the total is exactly 40000 on every run.
    print(f"locked : {safe['n']:>7}  (expected {EXPECTED}: exact, nothing lost)")


if __name__ == "__main__":
    main()
