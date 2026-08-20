"""Dependency injection (Level 2.3): pass a collaborator in, do not build it inside.

The concept, in plain words:
    When a class builds its own dependencies with a constructor call inside itself, it is welded to
    them: you cannot change or fake them from outside. Dependency injection means handing those
    collaborators in from the outside, so the same class can run with a real one in production and
    a simple fake in a test.

Why a fresher should care:
    Injected dependencies are what make code testable and flexible. It is the difference between a
    class you can exercise in isolation and one you can only run with the whole system attached.

What this demo shows:
    BadService builds its own source and is stuck with it. GoodService receives a source, so the
    same logic runs against a real source or a controlled fake with no change.

Run:  poetry run python demo_dependency_injection.py
"""

from __future__ import annotations

from typing import Protocol


# The small contract for the collaborator: something that can hand over a list of numbers.
class NumberSource(Protocol):
    def values(self) -> list[int]:
        ...


class RealSource:
    def values(self) -> list[int]:
        return [10, 20, 30]


class FakeSource:
    def values(self) -> list[int]:
        return [1, 1, 1]


# Hard to test: it constructs its own dependency inside __init__, so you cannot swap it.
class BadService:
    def __init__(self) -> None:
        self._source = RealSource()

    def total(self) -> int:
        return sum(self._source.values())


# Easy to test: the dependency is handed in, so any NumberSource can be used.
class GoodService:
    def __init__(self, source: NumberSource) -> None:
        self._source = source

    def total(self) -> int:
        return sum(self._source.values())


def main() -> None:
    # BadService can only ever use the real source it built inside itself.
    print("bad service (fixed source) :", BadService().total())  # 60

    # GoodService runs the same logic against whatever source we inject.
    print("good service (real source) :", GoodService(RealSource()).total())  # 60
    print("good service (fake source) :", GoodService(FakeSource()).total())  # 3


if __name__ == "__main__":
    main()
