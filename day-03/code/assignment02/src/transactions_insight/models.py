"""The domain model, new on Day 3: a Transaction value object and an account ledger.

New this day (Day 2 passed plain dicts around): the transaction now has an explicit, named
shape, and `frozen=True` makes it a value object that cannot change after it is built. The
ledger applies transactions and tracks a balance per account, in paise. Checking the values
(a positive amount, a supported currency, a non-empty id) is added later, on Day 4.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:  # new this day: a named, frozen value object (Day 2 used plain dicts)
    account_id: str
    amount_paise: int  # money in the smallest unit (paise), to avoid float rounding
    currency: str


def parse_transaction(row: dict[str, str]) -> Transaction:
    """Turn a raw CSV row into a Transaction value object."""
    rupees = float(row["amount"])
    return Transaction(
        account_id=row["account_id"],
        amount_paise=round(rupees * 100),
        currency=row["currency"],
    )


class AccountLedger:  # new this day: applies transactions and tracks a balance per account
    """Applies transactions and tracks a balance per account, in paise."""

    def __init__(self) -> None:
        self._balances: dict[str, int] = {}

    def apply(self, txn: Transaction) -> None:
        self._balances[txn.account_id] = self._balances.get(txn.account_id, 0) + txn.amount_paise

    def balance(self, account_id: str) -> int:
        return self._balances.get(account_id, 0)

    def total(self) -> int:
        return sum(self._balances.values())
