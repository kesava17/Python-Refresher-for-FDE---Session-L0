"""Dataclasses for data (Level 1.2): let Python write the boilerplate for plain data.

The concept, in plain words:
    Many classes exist only to hold a few fields. Writing __init__, __repr__, and __eq__ by hand
    for them is repetitive and easy to get wrong. The @dataclass decorator generates all of that
    from the field declarations. Adding frozen=True makes the object immutable and hashable, a safe
    value object.

Why a fresher should care:
    Less hand-written boilerplate means fewer places for bugs to hide and less code to maintain. A
    dataclass also says "this is data" at a glance.

What this demo shows:
    A hand-written Point and a @dataclass Point behave the same for printing and equality, but the
    dataclass needed a fraction of the code. A frozen dataclass then refuses to be changed.

Run:  poetry run python demo_dataclass.py
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass


# The hand-written version: three methods just to store two numbers, print them, and compare them.
class PointManual:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"PointManual(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PointManual):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)


# The dataclass version: the same readable repr and value equality, generated from the two fields.
@dataclass
class Point:
    x: int
    y: int


# frozen=True makes a value object: it cannot be changed after it is built.
@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int


def main() -> None:
    # Same readable output and value equality, from far less code.
    print("manual   :", PointManual(1, 2), PointManual(1, 2) == PointManual(1, 2))
    print("dataclass:", Point(1, 2), Point(1, 2) == Point(1, 2))

    # A frozen dataclass rejects any change, so it is safe to share.
    point = FrozenPoint(1, 2)
    try:
        point.x = 9  # type: ignore[misc]  # frozen: assignment is not allowed
    except FrozenInstanceError:
        print("frozen point cannot be changed after construction")


if __name__ == "__main__":
    main()
