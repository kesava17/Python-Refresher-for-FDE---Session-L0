"""The data-source seam (new on Day 3): a small Protocol, and two interchangeable sources.

A Protocol describes a contract by its shape: any object that has a `rows()` method
returning transaction rows counts as a TransactionSource, with no base class to inherit.
This is what lets the service depend on the contract, not on where the data actually
comes from.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol

from transactions_insight.data import open_records


class TransactionSource(Protocol):  # new this day: the source contract the service depends on
    """The contract the service depends on: something that can hand over transaction rows."""

    def rows(self) -> Iterator[dict[str, str]]:
        """Yield raw transaction rows, one dictionary at a time."""
        ...


class CsvTransactionSource:
    """A TransactionSource backed by a CSV file on disk. Used in the real application."""

    def __init__(self, path: str) -> None:
        self._path = path

    def rows(self) -> Iterator[dict[str, str]]:
        # open_records is a context manager that streams rows and always closes the file.
        # Yielding from inside the `with` keeps the file open only while it is being read.
        with open_records(self._path) as stream:
            yield from stream


class InMemoryTransactionSource:
    """A TransactionSource backed by a list already in memory. Ideal for tests: no file needed."""

    def __init__(self, rows: Sequence[dict[str, str]]) -> None:
        self._rows = list(rows)

    def rows(self) -> Iterator[dict[str, str]]:
        return iter(self._rows)
