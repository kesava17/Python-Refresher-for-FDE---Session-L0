"""A timeout on every call, and a retry with backoff for transient failures.

Two guards a service needs on a remote call: a timeout so it fails fast instead of hanging,
and a retry with growing backoff so a passing blip becomes a success. Standard library only.

Run:  poetry run python demo_timeout_retry.py
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class Flaky:
    """A dependency that fails the first `fail_times` calls, then succeeds."""

    def __init__(self, fail_times: int) -> None:
        """Configure how many leading calls should fail."""
        self.calls = 0
        self.fail_times = fail_times

    def __call__(self) -> str:
        """Fail while under the threshold, then return a result."""
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionError("transient failure")
        return "ok"


def call_with_retry(fn: Callable[[], str], attempts: int = 3, backoff: float = 0.1) -> str:
    """Call fn, retrying transient failures with a growing backoff."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except ConnectionError as exc:
            wait = backoff * attempt
            print(f"  attempt {attempt} failed ({exc}); retrying in {wait:.1f}s")
            time.sleep(wait)
    raise RuntimeError("all attempts failed")


def with_timeout(fn: Callable[[], T], timeout: float) -> T:
    """Run fn in a thread and raise TimeoutError if it outlives the timeout."""
    box: dict[str, T] = {}
    thread = threading.Thread(target=lambda: box.setdefault("result", fn()), daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TimeoutError(f"call exceeded {timeout}s")
    return box["result"]


def main() -> None:
    """Show a retry turning a blip into success, and a timeout bounding a slow call."""
    print("A dependency that fails twice, then works:")
    flaky = Flaky(fail_times=2)
    result = call_with_retry(flaky)
    print(f"  succeeded on attempt {flaky.calls} -> {result}\n")

    def slow_call() -> str:
        """A dependency that takes a full second to answer."""
        time.sleep(1.0)
        return "slow answer"

    print("A slow dependency, bounded by a timeout:")
    try:
        with_timeout(slow_call, timeout=0.3)
    except TimeoutError as exc:
        print(f"  {exc}; we fail fast instead of hanging with it\n")

    print("Retry hides a transient failure; the timeout stops one slow call from holding a")
    print("request open. Together they keep a caller alive when a dependency misbehaves.")


if __name__ == "__main__":
    main()
