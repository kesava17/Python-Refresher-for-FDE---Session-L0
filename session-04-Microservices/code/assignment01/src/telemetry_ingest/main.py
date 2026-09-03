"""telemetry-ingest service: POST a reading, store it, publish a reading-received event.

Run it with:  poetry run uvicorn telemetry_ingest.main:app --port 8001
"""

from __future__ import annotations

from fastapi import FastAPI

from common import observability
from common.broker import FileBroker
from common.config import settings
from contracts.reading import ReadingCreated, ReadingIn, ReadingReceived

from .store import IngestStore


def create_app(store: IngestStore | None = None, broker: FileBroker | None = None) -> FastAPI:
    """Build the telemetry-ingest app. Tests inject a temp store and broker; production uses defaults."""
    store = store or IngestStore(settings.ingest_db)
    broker = broker or FileBroker(settings.broker_path)
    app = FastAPI(title="telemetry-ingest", version="1.0")
    observability.install(app, "telemetry-ingest")
    log = observability.configure_logging("telemetry-ingest")

    @app.post("/v1/readings", status_code=201, response_model=ReadingCreated)
    def create_reading(reading: ReadingIn) -> ReadingCreated:
        """Store a validated reading and publish an event for the read side to consume."""
        reading_id = store.save(reading)
        broker.publish(
            "reading-received",
            ReadingReceived(id=reading_id, device_id=reading.device_id, value=reading.value).model_dump(),
        )
        log.info(f"stored reading {reading_id} for {reading.device_id}")
        return ReadingCreated(id=reading_id)

    return app


app = create_app()
