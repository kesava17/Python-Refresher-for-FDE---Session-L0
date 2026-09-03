"""Configuration read from the environment, with offline defaults anchored to the project root.

No secret is hard-coded. A real deployment sets the service URLs and store paths in the
environment; the defaults here let the whole system run on a laptop with nothing configured.
"""

from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]  # the assignment01 project root
_DATA = _ROOT / "data"


def _store(env: str, default_name: str) -> str:
    """Return a store path from the environment, or a default under the project's data folder."""
    return os.environ.get(env, str(_DATA / default_name))


class Settings:
    """The resolved settings for a service. One instance is shared as `settings`."""

    def __init__(self) -> None:
        """Read settings from the environment, creating the data folder if needed."""
        _DATA.mkdir(parents=True, exist_ok=True)
        self.ingest_db: str = _store("INGEST_DB", "ingest.db")
        self.rollup_db: str = _store("ROLLUP_DB", "rollup.db")
        self.broker_path: str = _store("BROKER_PATH", "broker.jsonl")
        self.ingest_url: str = os.environ.get("INGEST_URL", "http://localhost:8001")
        self.rollup_url: str = os.environ.get("ROLLUP_URL", "http://localhost:8002")
        self.http_timeout: float = float(os.environ.get("HTTP_TIMEOUT", "2.0"))


settings = Settings()
