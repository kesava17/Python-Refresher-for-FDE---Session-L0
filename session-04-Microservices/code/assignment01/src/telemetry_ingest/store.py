"""The write store owned by telemetry-ingest. No other service opens this database."""

from __future__ import annotations

import sqlite3

from contracts.reading import ReadingIn


class IngestStore:
    """A small sqlite store for submitted readings, private to telemetry-ingest."""

    def __init__(self, db_path: str) -> None:
        """Open (and create if needed) the readings table at the given path."""
        self._db_path = db_path
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS readings("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT, value REAL, ts TEXT)"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a connection to this service's own database file."""
        return sqlite3.connect(self._db_path)

    def save(self, reading: ReadingIn) -> int:
        """Insert a validated reading and return its new id."""
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO readings(device_id, value, ts) VALUES (?, ?, ?)",
                (reading.device_id, reading.value, reading.ts),
            )
            return int(cursor.lastrowid or 0)
