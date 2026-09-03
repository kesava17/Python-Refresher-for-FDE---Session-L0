"""Synchronous versus asynchronous: wait for the answer, or hand the work off.

Sync: the caller blocks until the callee returns. Async: the caller puts a message on a queue
and returns at once; a worker processes it later. Standard library only.

Run:  poetry run python demo_sync_vs_async.py
"""

from __future__ import annotations

import queue
import threading
import time


def slow_work(value: int) -> int:
    """A unit of work that takes a noticeable moment."""
    time.sleep(0.2)
    return value * value


def main() -> None:
    """Contrast a blocking call with a queued handoff."""
    print("SYNCHRONOUS (the caller waits):")
    start = time.perf_counter()
    result = slow_work(6)
    print(f"  got {result} after {time.perf_counter() - start:.2f}s of waiting\n")

    print("ASYNCHRONOUS (the caller hands off and returns):")
    work: queue.Queue[int | None] = queue.Queue()
    done: dict[int, int] = {}

    def worker() -> None:
        """Process messages from the queue until told to stop."""
        while True:
            item = work.get()
            if item is None:
                work.task_done()
                return
            done[item] = slow_work(item)
            work.task_done()

    threading.Thread(target=worker, daemon=True).start()
    start = time.perf_counter()
    work.put(6)
    print(f"  handed off in {time.perf_counter() - start:.4f}s; the worker runs in the background")
    work.join()
    print(f"  worker finished later: {done}\n")

    print("Sync couples the two in time: a slow callee stalls the caller. Async decouples them")
    print("and absorbs a spike, at the cost of an answer that is ready later, not now.")


if __name__ == "__main__":
    main()
