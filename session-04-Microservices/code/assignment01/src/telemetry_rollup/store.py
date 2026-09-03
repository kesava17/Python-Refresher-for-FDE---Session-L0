"""The read store owned by telemetry-rollup: a rollup per device, updated from events.

telemetry-rollup never touches the ingest database. Its read model is built only from the
events it consumes, which is what keeps the two services independent.
"""

from __future__ import annotations

import sqlite3

from contracts.reading import Rollup


class RollupStore:
    """A sqlite read model holding the count and running value sum per device."""

    def __init__(self, db_path: str) -> None:
        """Open (and create if needed) the rollups table at the given path."""
        self._db_path = db_path
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS rollups("
                "device_id TEXT PRIMARY KEY, count INTEGER, sum_value REAL)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a connection to this service's own database file."""
        return sqlite3.connect(self._db_path)

    def apply_reading(self, device_id: str, value: float) -> None:
        """Fold one reading into the device's rollup (insert or update)."""
        with self._connect() as db:
            row = db.execute(
                "SELECT count, sum_value FROM rollups WHERE device_id=?", (device_id,)
            ).fetchone()
            if row is None:
                db.execute(
                    "INSERT INTO rollups(device_id, count, sum_value) VALUES (?, 1, ?)",
                    (device_id, value),
                )
            else:
                db.execute(
                    "UPDATE rollups SET count=?, sum_value=? WHERE device_id=?",
                    (row[0] + 1, row[1] + value, device_id),
                )

    def rollup(self, device_id: str) -> Rollup | None:
        """Return the rollup for a device, or None if no readings have been seen for it."""
        with self._connect() as db:
            row = db.execute(
                "SELECT count, sum_value FROM rollups WHERE device_id=?", (device_id,)
            ).fetchone()
        if row is None or row[0] == 0:
            return None
        return Rollup(device_id=device_id, count=row[0], average_value=round(row[1] / row[0], 2))
