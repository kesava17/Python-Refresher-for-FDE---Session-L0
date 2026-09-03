"""The write store owned by reviews-ingest. No other service opens this database."""

from __future__ import annotations

import sqlite3

from contracts.review import ReviewIn


class IngestStore:
    """A small sqlite store for submitted reviews, private to reviews-ingest."""

    def __init__(self, db_path: str) -> None:
        """Open (and create if needed) the reviews table at the given path."""
        self._db_path = db_path
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS reviews("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT, rating INTEGER, text TEXT)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a connection to this service's own database file."""
        return sqlite3.connect(self._db_path)

    def save(self, review: ReviewIn) -> int:
        """Insert a validated review and return its new id."""
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO reviews(product_id, rating, text) VALUES (?, ?, ?)",
                (review.product_id, review.rating, review.text),
            )
            return int(cursor.lastrowid or 0)
