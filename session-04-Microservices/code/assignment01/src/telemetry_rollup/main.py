"""telemetry-rollup service: serve per-device rollups, kept fresh by consuming reading-received events.

Run it with:  poetry run uvicorn telemetry_rollup.main:app --port 8002

For the lab the read model is drained on demand (before a read, and via /internal/drain). In
production a background worker would consume the stream continuously.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from common import observability
from common.broker import FileBroker
from common.config import settings
from contracts.reading import Rollup

from .consumer import drain_events
from .store import RollupStore


def create_app(store: RollupStore | None = None, broker: FileBroker | None = None) -> FastAPI:
    """Build the telemetry-rollup app. Tests inject a temp store and broker; production uses defaults."""
    store = store or RollupStore(settings.rollup_db)
    broker = broker or FileBroker(settings.broker_path)
    app = FastAPI(title="telemetry-rollup", version="1.0")
    observability.install(app, "telemetry-rollup")

    @app.post("/internal/drain")
    def drain() -> dict[str, int]:
        """Consume any pending events into the read model. Returns how many were applied."""
        return {"applied": drain_events(store, broker)}

    @app.get("/v1/rollup/{device_id}", response_model=Rollup)
    def get_rollup(device_id: str) -> Rollup:
        """Return the rollup for a device, draining new events first to stay fresh."""
        drain_events(store, broker)
        rollup = store.rollup(device_id)
        if rollup is None:
            raise HTTPException(status_code=404, detail="no data for device")
        return rollup

    return app


app = create_app()
