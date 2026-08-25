"""Bound a cache to keep memory flat (reliability): unbounded growth is a slow crash.

The concept, in plain words:
    A long-running service handles a stream of requests for hours. If it caches results
    in a plain dict keyed by an ever-changing value, that dict never stops growing:
    every new key adds an entry that is never reused and never freed. Memory climbs
    until the process is killed. A bounded cache (functools.lru_cache with a maxsize)
    keeps only the most recent entries and evicts the rest, so memory settles at a flat
    ceiling no matter how long the service runs.

Why a fresher should care:
    This kind of leak passes every quick test and only shows up in a soak: a long run
    under steady load. Bounding the cache is a one-line habit that prevents a class of 3
    a.m. outages.

What this demo shows:
    The same core loop run many times against a unique key each iteration. The unbounded
    dict grows with every iteration; the lru_cache(maxsize=128) holds steady.
    tracemalloc (standard library) reports memory at intervals so you can watch one
    climb while the other stays flat.

Run:  poetry run python demo_soak_flat.py
"""

from __future__ import annotations

import tracemalloc
from functools import lru_cache

ITERATIONS = 20000

# The unbounded cache: a plain dict that we never prune. It grows without limit.
_unbounded: dict[int, str] = {}


def score_unbounded(review_id: int) -> str:
    # Cache the computed score forever. Every new id adds an entry that is never freed.
    if review_id not in _unbounded:
        _unbounded[review_id] = f"score-of-{review_id}"
    return _unbounded[review_id]


@lru_cache(maxsize=128)
def score_bounded(review_id: int) -> str:
    # Same computation, but lru_cache keeps at most 128 entries and evicts the oldest.
    return f"score-of-{review_id}"


def current_kib() -> float:
    """Return the current traced memory in kibibytes."""
    current, _peak = tracemalloc.get_traced_memory()
    return current / 1024


def main() -> None:
    tracemalloc.start()
    print(f"soak of {ITERATIONS} iterations, unique key each time")
    print(f"{'iteration':>10} {'unbounded entries':>18} {'bounded entries':>16}")

    for i in range(1, ITERATIONS + 1):
        score_unbounded(i)  # feeds the dict that keeps growing
        score_bounded(i)  # feeds the capped cache that stays flat
        if i % 5000 == 0:
            # The bounded cache holds at most 128 entries, so its footprint
            # barely moves.
            bounded = score_bounded.cache_info().currsize
            print(f"{i:>10} {len(_unbounded):>18} {bounded:>16}")

    print(f"\ntraced total now: {current_kib():.1f} KiB")
    print(
        f"unbounded dict holds {len(_unbounded)} entries and keeps climbing; "
        f"bounded cache holds {score_bounded.cache_info().currsize} and stays flat."
    )
    tracemalloc.stop()


if __name__ == "__main__":
    main()
