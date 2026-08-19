"""The GIL (Level 1.2): threads do not speed up CPU-bound work; processes do.

The concept, in plain words:
    CPython protects its internals with one big lock called the GIL (Global
    Interpreter Lock). Only one thread can run Python bytecode at a time, so if
    the work is pure computation, extra threads just take turns on the same
    single core and finish no sooner. Separate processes each get their own
    Python interpreter and their own GIL, so they truly run at the same time on
    different cores.

Why a fresher should care:
    Reaching for threads to "go faster" on number crunching is a classic wasted
    afternoon: you add complexity and get zero speedup. Knowing that CPU-bound
    work needs processes (not threads) saves you from that trap and points you
    at the tool that actually helps.

What this demo shows:
    The same heavy loop is run three ways over 8 tasks. "serial" and "threads"
    take roughly the same time (the GIL serialises them), while "processes"
    finishes noticeably faster because the work spreads across real cores.

Run:  poetry run python demo_gil_cpu.py
"""

from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def cpu_work(n: int) -> int:
    """Pure computation: the processor is busy the whole time (CPU-bound)."""
    # A tight arithmetic loop with no waiting. Because it never pauses for IO,
    # the GIL is held almost continuously, which is exactly why threads cannot
    # overlap this kind of work.
    total = 0
    for i in range(n):
        total += i * i
    return total


def run_serial(tasks: list[int]) -> None:
    # Baseline: do every task one after another on a single thread. Whatever this
    # takes is the "no parallelism at all" number to compare against.
    [cpu_work(n) for n in tasks]


def run_threads(tasks: list[int]) -> None:
    # Spread the tasks over a pool of 8 threads. This LOOKS parallel, but all the
    # threads share one interpreter and one GIL, so for CPU-bound work they end
    # up running one at a time anyway.
    with ThreadPoolExecutor(max_workers=8) as pool:
        # pool.map schedules cpu_work across the threads; list() forces every
        # task to actually run and finish before we return.
        list(pool.map(cpu_work, tasks))


def run_processes(tasks: list[int]) -> None:
    # Spread the same tasks over 8 separate PROCESSES. Each process is its own
    # Python with its own GIL, so they genuinely run in parallel on different
    # CPU cores. This is the right tool for CPU-bound work.
    with ProcessPoolExecutor(max_workers=8) as pool:
        list(pool.map(cpu_work, tasks))


def timed(label: str, fn: Callable[[list[int]], None], tasks: list[int]) -> None:
    # Small helper: run fn(tasks), measure how long it took with a high-resolution
    # clock, and print the label plus the elapsed seconds in a fixed-width format.
    start = time.perf_counter()
    fn(tasks)
    print(f"{label:10s}: {time.perf_counter() - start:5.2f}s")


def main() -> None:
    # Eight identical heavy tasks. Making them equal keeps the three timings easy
    # to compare side by side.
    tasks = [2_000_000] * 8
    # Run each strategy and print its timing. Expect serial and threads to land
    # close together, and processes to come in clearly lower.
    timed("serial", run_serial, tasks)
    timed("threads", run_threads, tasks)
    timed("processes", run_processes, tasks)
    print("threads are about the same as serial (the GIL); processes are faster.")


if __name__ == "__main__":
    main()
