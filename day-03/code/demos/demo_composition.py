"""Composition over inheritance (Level 2.1): build behaviour by combining parts you can swap.

The concept, in plain words:
    Inheritance ties a class to a parent and spreads behaviour across a tree, which grows rigid
    fast. Composition instead gives an object another object to do a job, a "has a" relationship,
    so you can swap that part without touching the rest. Most of the time, composition is the more
    flexible and more maintainable choice.

Why a fresher should care:
    Deep inheritance trees are hard to follow and hard to change: one edit near the top ripples
    everywhere. Composition keeps parts small and independent, which is easier to test and evolve.

What this demo shows:
    A Report is given a formatter to use. Swapping a plain formatter for a bullet formatter changes
    the output with no change to Report itself. The behaviour is composed, not inherited.

Run:  poetry run python demo_composition.py
"""

from __future__ import annotations

from typing import Protocol


# The small contract for the part the Report will use. Anything with this method fits.
class Formatter(Protocol):
    def format(self, rows: list[str]) -> str:
        ...


# Two small, independent formatters. Each does one job: turn rows into text.
class PlainFormatter:
    def format(self, rows: list[str]) -> str:
        return ", ".join(rows)


class BulletFormatter:
    def format(self, rows: list[str]) -> str:
        return "\n".join(f"- {row}" for row in rows)


# The Report HAS a formatter (composition). It does not inherit from one, and it does not care
# which formatter it was given, only that it can format rows.
class Report:
    def __init__(self, formatter: Formatter) -> None:
        self._formatter = formatter

    def render(self, rows: list[str]) -> str:
        return self._formatter.format(rows)


def main() -> None:
    rows = ["alpha", "beta", "gamma"]

    # Same Report code, two different behaviours, chosen by the part we hand it.
    print("plain:")
    print(Report(PlainFormatter()).render(rows))
    print("bullets:")
    print(Report(BulletFormatter()).render(rows))


if __name__ == "__main__":
    main()
