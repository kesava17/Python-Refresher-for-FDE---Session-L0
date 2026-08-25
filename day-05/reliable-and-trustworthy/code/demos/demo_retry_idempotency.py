"""Retry safely with an idempotency key (reliability): never double the effect.

The concept, in plain words:
    When a call fails or its response is lost, the client retries. If the server
    actually did the work the first time but the reply went missing, a blind retry does
    the work twice: two charges, two saved reviews, two of everything. An idempotency
    key fixes this. The client sends the same key on every attempt, and the server
    records which keys it has already applied, so a repeat with a known key returns the
    first result instead of redoing the work.

Why a fresher should care:
    Networks lose responses all the time, so retries are normal. Without a key, "just
    retry" quietly duplicates side effects. With a key, a retry is safe to send as many
    times as you like.

What this demo shows:
    A flaky submit whose response is lost on the first attempt, so the client retries.
    Without a key, the effect (a stored review) is applied on every successful attempt.
    With a key, the server sees the repeat and applies it exactly once.

Run:  poetry run python demo_retry_idempotency.py
"""

from __future__ import annotations

from collections.abc import Callable


class ReviewStore:
    """A tiny server-side store that records applied idempotency keys."""

    def __init__(self) -> None:
        self.applied_count = 0  # how many times the effect actually ran
        self._seen_keys: set[str] = set()  # keys we have already applied

    def submit_without_key(self) -> None:
        # No key, so the server cannot tell a retry from a fresh request: it
        # applies every time.
        self.applied_count += 1

    def submit_with_key(self, key: str) -> None:
        # A repeat key is a known request, so we skip the effect and keep the
        # count at one.
        if key in self._seen_keys:
            return
        self._seen_keys.add(key)
        self.applied_count += 1


def run_with_lost_first_response(apply: Callable[[], None]) -> None:
    """Call apply twice to model a lost first response that forced one retry.

    The first attempt succeeds on the server but its response is lost, so the
    client cannot tell it worked and sends a second, identical attempt. Both
    attempts reach the server.
    """
    for _attempt in range(2):
        apply()


def main() -> None:
    # Without a key: the retry reaches a server that cannot dedupe, so the effect
    # lands twice.
    no_key = ReviewStore()
    run_with_lost_first_response(no_key.submit_without_key)
    print(f"no key   -> applied {no_key.applied_count} times")

    # With a key: the retry carries the same key, so the server applies it
    # exactly once.
    with_key = ReviewStore()
    run_with_lost_first_response(lambda: with_key.submit_with_key("idem-key-P-77"))
    print(f"with key -> applied exactly once ({with_key.applied_count} time)")


if __name__ == "__main__":
    main()
