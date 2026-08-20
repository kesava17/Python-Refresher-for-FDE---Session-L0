"""Protocols (Level 2.2): depend on a shape, not a base class (structural typing).

The concept, in plain words:
    A Protocol describes what an object must be able to DO, for example "has a format(value)
    method", without requiring it to inherit from anything. Any class with a matching method
    satisfies the Protocol automatically. This is duck typing that the type checker can verify: if
    it has the right shape, it fits.

Why a fresher should care:
    Depending on a small contract instead of a concrete class means you can pass in anything that
    fits, including a simple fake in a test. It keeps modules loosely coupled, which is what lets
    them change independently.

What this demo shows:
    Two unrelated classes, Money and Percent, each have a format() method, so both satisfy the
    Formatter protocol with no shared base class. One show() function accepts either.

Run:  poetry run python demo_protocol.py
"""

from __future__ import annotations

from typing import Protocol


# The contract: anything with this format() method is a Formatter, whatever its class.
class Formatter(Protocol):
    def format(self, value: float) -> str:
        ...


# Two independent classes. Neither inherits from Formatter; they just match its shape.
class Money:
    def format(self, value: float) -> str:
        return f"Rs {value:.2f}"


class Percent:
    def format(self, value: float) -> str:
        return f"{value:.0f}%"


# This function depends only on the Formatter contract, so it accepts either class.
def show(formatter: Formatter, value: float) -> str:
    return formatter.format(value)


def main() -> None:
    # Both calls type-check and run, because both classes fit the Formatter shape.
    print("money  :", show(Money(), 1234.5))  # Rs 1234.50
    print("percent:", show(Percent(), 87))  # 87%


if __name__ == "__main__":
    main()
