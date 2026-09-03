"""The read store owned by reviews-query: a rollup per product, updated from events.

reviews-query never touches the ingest database. Its read model is built only from the
events it consumes, which is what keeps the two services independent.
"""

from __future__ import annotations

import sqlite3

from contracts.review import Aggregate


class QueryStore:
    """A sqlite read model holding the count and rating sum per product."""

    def __init__(self, db_path: str) -> None:
        """Open (and create if needed) the aggregates table at the given path."""
        self._db_path = db_path
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS aggregates("
                "product_id TEXT PRIMARY KEY, count INTEGER, sum_rating INTEGER)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a connection to this service's own database file."""
        return sqlite3.connect(self._db_path)

    def apply_review(self, product_id: str, rating: int) -> None:
        """Fold one review into the product's rollup (insert or update)."""
        with self._connect() as db:
            row = db.execute(
                "SELECT count, sum_rating FROM aggregates WHERE product_id=?", (product_id,)
            ).fetchone()
            if row is None:
                db.execute(
                    "INSERT INTO aggregates(product_id, count, sum_rating) VALUES (?, 1, ?)",
                    (product_id, rating),
                )
            else:
                db.execute(
                    "UPDATE aggregates SET count=?, sum_rating=? WHERE product_id=?",
                    (row[0] + 1, row[1] + rating, product_id),
                )

    def aggregate(self, product_id: str) -> Aggregate | None:
        """Return the rollup for a product, or None if no reviews have been seen for it."""
        with self._connect() as db:
            row = db.execute(
                "SELECT count, sum_rating FROM aggregates WHERE product_id=?", (product_id,)
            ).fetchone()
        if row is None or row[0] == 0:
            return None
        return Aggregate(product_id=product_id, count=row[0], average_rating=round(row[1] / row[0], 2))
