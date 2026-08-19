"""Generators (Level 3.1): a generator expression streams and is single-use.

The concept, in plain words:
    A list comprehension with square brackets builds and stores every value right
    away. The same expression with round brackets is a generator: it stores no
    values, only a recipe for producing them on demand. Because a generator has no
    stored contents, it is tiny in memory. And because it produces its values by
    running through once, it is single-use: after you have consumed it, it is
    empty and yields nothing more.

Why a fresher should care:
    The two forms look almost identical (just brackets), so it is easy to reach
    for the wrong one. Knowing that a generator is nearly free in memory but can
    only be walked once saves you from two classic surprises: needless memory use,
    and a "second pass" that mysteriously sees no data.

What this demo shows:
    sys.getsizeof reports the list comprehension as hundreds of thousands of bytes
    (it holds every value) versus a couple hundred bytes for the generator (it
    holds none). Then summing the generator twice: the first pass gives the real
    total, and the second gives 0 because the generator is already spent.

Run:  poetry run python demo_generator_expr.py
"""

from __future__ import annotations

import sys


def main() -> None:
    # Square brackets: builds and stores all 100000 squared values immediately.
    list_comp = [x * x for x in range(100_000)]  # builds the whole list
    # Round brackets: a generator expression. Nothing is computed or stored yet;
    # it only remembers how to produce the values when asked.
    gen_expr = (x * x for x in range(100_000))  # builds nothing yet

    # The list carries all its values, so it is large. The generator carries none,
    # so it is tiny (a fixed few hundred bytes regardless of the range size).
    print(f"list comprehension size : {sys.getsizeof(list_comp):>8} bytes")
    print(f"generator expression size: {sys.getsizeof(gen_expr):>8} bytes")

    # First pass: sum() walks the generator to the end, producing every value once
    # and adding them up. This gives the real total.
    print(f"first pass sum : {sum(gen_expr)}")
    # Second pass: the generator is now exhausted (it was walked to the end above),
    # so there is nothing left to yield and sum() of an empty generator is 0.
    print(f"second pass sum: {sum(gen_expr)}  (0: a generator is single-use, now spent)")


if __name__ == "__main__":
    main()
