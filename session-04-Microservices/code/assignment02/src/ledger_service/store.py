"""The read store owned by ledger-service: a running summary per account, updated from events.

ledger-service never touches the transactions database. Its read model is built only from the
events it consumes, which is what keeps the two services independent. The balance is an
INTEGER of minor units: a credit adds, a debit subtracts, so the total is always exact.
"""

from __future__ import annotations

import sqlite3

from contracts.transaction import AccountSummary


class LedgerStore:
    """A sqlite read model holding the transaction count and running balance per account."""

    def __init__(self, db_path: str) -> None:
        """Open (and create if needed) the summaries table at the given path."""
        self._db_path = db_path
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS summaries("
                "account_id TEXT PRIMARY KEY, count INTEGER, balance_cents INTEGER)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a connection to this service's own database file."""
        return sqlite3.connect(self._db_path)

    def apply_transaction(self, account_id: str, amount_cents: int, kind: str) -> None:
        """Fold one transaction into the account's summary (insert or update).

        A credit adds the amount to the balance; a debit subtracts it. Everything stays in
        integer minor units, so the running total never drifts.
        """
        signed = amount_cents if kind == "credit" else -amount_cents
        with self._connect() as db:
            row = db.execute(
                "SELECT count, balance_cents FROM summaries WHERE account_id=?", (account_id,)
            ).fetchone()
            if row is None:
                db.execute(
                    "INSERT INTO summaries(account_id, count, balance_cents) VALUES (?, 1, ?)",
                    (account_id, signed),
                )
            else:
                db.execute(
                    "UPDATE summaries SET count=?, balance_cents=? WHERE account_id=?",
                    (row[0] + 1, row[1] + signed, account_id),
                )

    def summary(self, account_id: str) -> AccountSummary | None:
        """Return the summary for an account, or None if no transactions have been seen for it."""
        with self._connect() as db:
            row = db.execute(
                "SELECT count, balance_cents FROM summaries WHERE account_id=?", (account_id,)
            ).fetchone()
        if row is None:
            return None
        return AccountSummary(account_id=account_id, count=row[0], balance_cents=row[1])
