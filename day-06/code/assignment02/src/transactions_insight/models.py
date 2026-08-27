"""Validated transaction model and an account ledger (Day 4)."""

from __future__ import annotations

from dataclasses import dataclass

_ALLOWED_CURRENCIES = frozenset({"INR"})


class TransactionParseError(ValueError):
    """Raised when a raw row cannot be turned into a valid Transaction."""


@dataclass(frozen=True)
class Transaction:
    account_id: str
    amount_paise: int  # money in the smallest unit (paise), to avoid float rounding
    currency: str

    def __post_init__(self) -> None:
        if not self.account_id:
            raise ValueError("account_id must not be empty")
        if self.amount_paise <= 0:
            raise ValueError(f"amount must be positive: {self.amount_paise}")
        if self.currency not in _ALLOWED_CURRENCIES:
            raise ValueError(f"unsupported currency: {self.currency}")


def parse_transaction(row: dict[str, str]) -> Transaction:
    """Turn a raw CSV row into a validated Transaction, or raise TransactionParseError."""
    try:
        rupees = float(row["amount"])
        return Transaction(
            account_id=row["account_id"],
            amount_paise=round(rupees * 100),
            currency=row["currency"],
        )
    except (KeyError, ValueError) as exc:
        raise TransactionParseError(f"bad row: {row}") from exc


class AccountLedger:
    """Applies validated transactions and tracks a balance per account, in paise."""

    def __init__(self) -> None:
        self._balances: dict[str, int] = {}

    def apply(self, txn: Transaction) -> None:
        self._balances[txn.account_id] = self._balances.get(txn.account_id, 0) + txn.amount_paise

    def balance(self, account_id: str) -> int:
        return self._balances.get(account_id, 0)

    def total(self) -> int:
        return sum(self._balances.values())
