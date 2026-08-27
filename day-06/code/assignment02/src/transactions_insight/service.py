"""The service layer (Day 3): the summary logic, with its store and strategy injected.

This is the heart of the maintainable refactor. The counting logic lives in one place,
`summarize_rows`. The `LedgerService` holds a TransactionSource and a CategoryStrategy that
are handed to it from outside (dependency injection), so it never decides where the data
comes from nor how a transaction is categorized. Those two seams are what let a test feed
in-memory rows and swap the strategy, while the logic stays untouched in both cases.
"""

from __future__ import annotations

from collections.abc import Iterator

from transactions_insight.decorators import timed
from transactions_insight.models import (
    AccountLedger,
    TransactionParseError,
    parse_transaction,
)
from transactions_insight.sources import TransactionSource
from transactions_insight.strategies import CategoryStrategy


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count valid transactions and distinct accounts, rejecting bad rows honestly (from Day 4)."""
    transactions = 0
    accounts: set[str] = set()
    rejected = 0
    for row in rows:
        try:
            txn = parse_transaction(row)
        except TransactionParseError:
            rejected += 1  # count it and move on, instead of crashing
            continue
        transactions += 1
        accounts.add(txn.account_id)
    return {"transactions": transactions, "accounts": len(accounts), "rejected": rejected}


class LedgerService:
    """Summarizes and categorizes transactions from any source, using an injected strategy.

    Both the source and the strategy are injected, not built here. The service depends on the
    two contracts only, so swapping either one needs no change to the logic below.
    """

    def __init__(self, source: TransactionSource, strategy: CategoryStrategy) -> None:
        self._source = source
        self._strategy = strategy
        self._last_total = 0  # paise applied by the most recent categorize_all call

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())

    def categorize_all(self) -> dict[str, int]:
        """Apply each valid transaction to a fresh ledger and count categories via the strategy."""
        ledger = AccountLedger()
        counts: dict[str, int] = {}
        for row in self._source.rows():
            try:
                txn = parse_transaction(row)
            except TransactionParseError:
                continue  # bad rows never reach the ledger or the tally
            ledger.apply(txn)
            # The strategy is the only thing that decides the bucket; the loop stays the same.
            label = self._strategy.categorize(txn)
            counts[label] = counts.get(label, 0) + 1
        # The ledger total is a by-product available to callers that need the invariant.
        self._last_total = ledger.total()
        return counts

    def last_total(self) -> int:
        """Return the ledger total from the most recent categorize_all call, in paise."""
        return self._last_total
