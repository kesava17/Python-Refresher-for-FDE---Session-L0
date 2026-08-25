"""The categorization seam (Day 3): a Protocol, and two interchangeable strategies.

Categorizing a transaction is a decision that may change often: today by size, tomorrow by
currency, later by something else. A strategy captures that one decision behind a small
contract so the service can hold whichever rule it was handed, without an `if` for each
variant. This is the swappable part: a test can pass one strategy, production another, and
the surrounding logic never changes.
"""

from __future__ import annotations

from typing import Protocol

from transactions_insight.models import Transaction

# One rupee is 100 paise; 10000 paise is 100 rupees, our default "large" threshold.
_DEFAULT_LARGE_PAISE = 10000


class CategoryStrategy(Protocol):
    """The contract the service depends on: turn one Transaction into a category label."""

    def categorize(self, txn: Transaction) -> str:
        """Return the category label this transaction belongs to."""
        ...


class BySizeStrategy:
    """Categorize by amount: 'large' at or above the threshold, 'small' below it."""

    def __init__(self, threshold_paise: int = _DEFAULT_LARGE_PAISE) -> None:
        self._threshold_paise = threshold_paise

    def categorize(self, txn: Transaction) -> str:
        return "large" if txn.amount_paise >= self._threshold_paise else "small"


class ByCurrencyStrategy:
    """Categorize by currency code, so each currency becomes its own bucket."""

    def categorize(self, txn: Transaction) -> str:
        return txn.currency
