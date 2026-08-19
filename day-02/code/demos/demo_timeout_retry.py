"""Safety (Level 2.5): a timeout stops us waiting forever; a bounded retry gives up cleanly.

The concept, in plain words:
    When you call something that might get stuck, you should never wait for it
    without a limit. A timeout says "wait at most this long, then move on". A
    bounded retry says "try a few times, and if none work, stop and report"
    instead of hanging or looping forever. Together they keep a slow or dead
    dependency from freezing your whole program.

Why a fresher should care:
    Real dependencies (networks, services, disks) do get stuck. Code that waits
    with no timeout is how an outage in one service silently hangs everything that
    calls it. A timeout plus a capped number of retries is the standard, defensive
    way to stay responsive and fail predictably.

What this demo shows:
    The dependency is deliberately stuck for 3 seconds, but each call is given
    only 0.3 second. So all three attempts time out, and after the third the code
    gives up cleanly. The total elapsed is about 1 second (three short waits), NOT
    the 3 seconds a single unbounded call would have cost.

Run:  poetry run python demo_timeout_retry.py
"""

from __future__ import annotations

import threading
import time


def slow_dependency(result: list[str]) -> None:
    """A dependency that is stuck for a long time."""
    # Simulates a call that hangs: it sleeps a full 3 seconds before finally
    # producing its answer. Our caller will not be willing to wait that long.
    time.sleep(3.0)
    result.append("ok")


def call_once(timeout: float) -> str | None:
    """Call the dependency but wait at most `timeout` seconds, then abandon it."""
    # `box` is a shared list the worker thread will drop its result into.
    box: list[str] = []
    # Run the slow call on a separate thread. daemon=True means this thread will
    # not keep the program alive: if we walk away, Python can kill it at exit.
    worker = threading.Thread(target=slow_dependency, args=(box,), daemon=True)
    worker.start()
    # join(timeout) waits for the worker, but only up to `timeout` seconds, then
    # returns whether it finished or not. This is what enforces the time limit.
    worker.join(timeout)
    if worker.is_alive():
        # Still running after the timeout: give up on it. The daemon thread is
        # left behind (abandoned) and gets killed when the program exits.
        return None  # timed out; the daemon thread is abandoned and killed at exit
    # It finished in time, so the result is sitting in the box.
    return box[0]


def main() -> None:
    start = time.perf_counter()
    # Bounded retry loop: try at most 3 times. Each call waits only 0.3s.
    for attempt in range(1, 4):
        result = call_once(timeout=0.3)
        if result is not None:
            # A real success would break out here. It never happens in this demo
            # because the dependency always outlasts the 0.3s budget.
            print(f"succeeded on attempt {attempt}: {result}")
            break
        print(f"attempt {attempt}: timed out after 0.3s")
    else:
        # The `for ... else` runs only if the loop finished without a `break`, so
        # this is the "all attempts failed, give up cleanly" path.
        print("gave up cleanly after 3 attempts (did not hang for 3s)")
    # Total is roughly 3 times 0.3s, about 1 second: far less than the 3 seconds a
    # single unbounded call would have taken.
    print(f"total elapsed: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
