"""The write store owned by transactions-service. No other service opens this database.

Amounts are held as integer minor units in an INTEGER column, so a stored balance can never
drift the way a float total would.
"""

from __future__ import annotations

import sqlite3

from contracts.transaction import TransactionIn, TransactionRecorded


class TransactionStore:
    """A small sqlite store for submitted transactions, private to transactions-service."""

    def __init__(self, db_path: str) -> None:
        """Open (and create if needed) the transactions table at the given path."""
        self._db_path = db_path
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS transactions("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, account_id TEXT, "
                "amount_cents INTEGER, kind TEXT)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a connection to this service's own database file."""
        return sqlite3.connect(self._db_path)

    def save(self, transaction: TransactionIn) -> int:
        """Insert a validated transaction and return its new id."""
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO transactions(account_id, amount_cents, kind) VALUES (?, ?, ?)",
                (transaction.account_id, transaction.amount_cents, transaction.kind),
            )
            return int(cursor.lastrowid or 0)

    def list_for_account(self, account_id: str) -> list[TransactionRecorded]:
        """Return every stored transaction for one account, oldest first."""
        with self._connect() as db:
            rows = db.execute(
                "SELECT id, account_id, amount_cents, kind FROM transactions "
                "WHERE account_id=? ORDER BY id",
                (account_id,),
            ).fetchall()
        return [
            TransactionRecorded(id=row[0], account_id=row[1], amount_cents=row[2], kind=row[3])
            for row in rows
        ]
