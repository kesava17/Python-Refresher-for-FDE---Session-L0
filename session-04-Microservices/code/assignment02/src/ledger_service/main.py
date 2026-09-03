"""ledger-service: serve per-account summaries, kept fresh by consuming transaction-recorded events.

Run it with:  poetry run uvicorn ledger_service.main:app --port 8002

For the lab the read model is drained on demand (before a read, and via /internal/drain). In
production a background worker would consume the stream continuously.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from common import observability
from common.broker import FileBroker
from common.config import settings
from contracts.transaction import AccountSummary

from .consumer import drain_events
from .store import LedgerStore


def create_app(store: LedgerStore | None = None, broker: FileBroker | None = None) -> FastAPI:
    """Build the ledger-service app. Tests inject a temp store and broker; production uses defaults."""
    store = store or LedgerStore(settings.ledger_db)
    broker = broker or FileBroker(settings.broker_path)
    app = FastAPI(title="ledger-service", version="1.0")
    observability.install(app, "ledger-service")

    @app.post("/internal/drain")
    def drain() -> dict[str, int]:
        """Consume any pending events into the read model. Returns how many were applied."""
        return {"applied": drain_events(store, broker)}

    @app.get("/v1/accounts/{account_id}/summary", response_model=AccountSummary)
    def get_summary(account_id: str) -> AccountSummary:
        """Return the summary for an account, draining new events first to stay fresh."""
        drain_events(store, broker)
        summary = store.summary(account_id)
        if summary is None:
            raise HTTPException(status_code=404, detail="no data for account")
        return summary

    return app


app = create_app()
