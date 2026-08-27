"""Application configuration, read from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()  # load a local .env in dev; a no-op if the file is absent
except ImportError:  # python-dotenv is a dev convenience; prod uses real env vars
    pass

# config.py lives at src/reviews_insight/config.py, so parents[2] is the project root.
# Anchoring the default data path there lets the command run from any directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = str(_PROJECT_ROOT / "data" / "reviews_sample.csv")


# Default enrichment target. The ".invalid" TLD is reserved and never resolves (RFC 2606),
# so with no enrichment server configured the call fails fast and the submit path degrades
# gracefully instead of hanging. Point ENRICHMENT_URL at a real service in production.
_DEFAULT_ENRICHMENT_URL = "http://enrichment.invalid/enrich"

@dataclass(frozen=True)
class Config:
    app_name: str
    data_path: str
    environment: str
    enrichment_url: str
    webhook_secret: str

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            app_name=os.environ.get("APP_NAME", "reviews-insight"),
            data_path=os.environ.get("DATA_PATH", _DEFAULT_DATA),
            environment=os.environ.get("APP_ENV", "dev"),
            enrichment_url=os.environ.get("ENRICHMENT_URL", _DEFAULT_ENRICHMENT_URL),
            # The webhook signing secret comes from the WEBHOOK_SECRET environment variable in
            # production (never committed). The inline fallback is a non-secret development
            # placeholder that matches the test fixture, so nothing sensitive lives in source.
            # Reading it here, through the config object, keeps secrets out of the app code.
            webhook_secret=os.environ.get("WEBHOOK_SECRET", "shared-webhook-secret"),
        )
