"""Generators (Level 3.1): streaming keeps memory flat; building a big list does not.

The concept, in plain words:
    A list comprehension builds every value and holds them all in memory at once.
    A generator produces one value at a time, hands it to whoever is consuming,
    and forgets it before making the next. When you only need to pass values
    through (for example, to add them up), a generator lets you process a huge
    sequence while keeping almost nothing in memory.

Why a fresher should care:
    Loading a whole dataset into a list is the easy habit that quietly blows up
    memory on real, large inputs. Streaming with a generator processes the same
    data with a flat, tiny memory footprint, which is often the difference
    between code that runs and code that crashes.

What this demo shows:
    Both functions sum the numbers 0 up to 5 million and return the same total.
    tracemalloc measures peak memory: the eager list version peaks at hundreds of
    megabytes (the whole list is resident), while the generator version peaks near
    zero because it never holds more than one value at a time.

Run:  poetry run python demo_memory_stream.py
"""

from __future__ import annotations

import tracemalloc
from collections.abc import Callable


def eager_sum(n: int) -> int:
    # EAGER: the list comprehension materialises all n numbers before summing.
    # Every value exists in memory at the same moment, so peak memory grows with n.
    data = [i for i in range(n)]  # the whole list is held in memory at once
    return sum(data)


def stream_sum(n: int) -> int:
    # STREAMING: the parentheses make a generator expression. sum() pulls one
    # value at a time and adds it; each value is discarded before the next is
    # made, so nothing large is ever held. Same total, flat memory.
    return sum(i for i in range(n))  # a generator: one value at a time, nothing held


def peak_mb(fn: Callable[[int], int], n: int) -> float:
    # Measure the peak memory used while fn(n) runs. tracemalloc.start() begins
    # tracking allocations, and get_traced_memory() reports the (current, peak)
    # byte counts; we return the peak converted to megabytes.
    tracemalloc.start()
    fn(n)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1_000_000


def main() -> None:
    # Five million numbers: big enough that holding them all is clearly visible.
    n = 5_000_000
    # The eager version's peak is large (the full list is resident at once).
    print(f"eager list peak : {peak_mb(eager_sum, n):7.1f} MB")
    # The generator version's peak stays near zero (one value at a time).
    print(f"generator peak  : {peak_mb(stream_sum, n):7.1f} MB")
    print("same answer, but the generator never holds the data, so memory stays flat.")


if __name__ == "__main__":
    main()
