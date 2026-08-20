"""Class versus function (Level 1.1): a class with one method is usually better as a function.

The concept, in plain words:
    Use a class when it bundles data with behaviour, or holds state that several methods share.
    If a class only stores a value in __init__ and has one method that uses it, a
    plain function does the same job with less ceremony. Reaching for a class by reflex is a common
    source of needless structure.

Why a fresher should care:
    Extra structure is not free: every class is one more thing to read, name, and keep in sync.
    Knowing when a function is enough keeps code small and easy to change, which is the whole point
    of "maintainable".

What this demo shows:
    A one-method Discounter class and a discounted() function give the identical result, so the
    class adds nothing. Then a small Tally class shows the opposite case, where real shared state
    makes a class the right choice.

Run:  poetry run python demo_class_vs_function.py
"""

from __future__ import annotations


# A class with one method and a constructor. It stores one value and uses it in one place.
class Discounter:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def apply(self, price: float) -> float:
        return price * (1 - self.rate)


# The same behaviour as a plain function. There is no object to build and nothing to keep in sync.
def discounted(price: float, rate: float) -> float:
    return price * (1 - rate)


# A class that IS worth having: it holds state (a running total) that more than one method
# reads and changes. Shared state across methods is exactly what a class is for.
class Tally:
    def __init__(self) -> None:
        self._total = 0

    def add(self, amount: int) -> None:
        self._total += amount

    def result(self) -> int:
        return self._total


def main() -> None:
    # Both forms give the same answer, so here the class is just a heavier function.
    print("class   :", Discounter(0.1).apply(100))  # 90.0
    print("function:", discounted(100, 0.1))  # 90.0

    # The Tally keeps state across calls, which a single function cannot do cleanly.
    tally = Tally()
    tally.add(10)
    tally.add(5)
    print("a class is the right choice here:", tally.result())  # 15


if __name__ == "__main__":
    main()
