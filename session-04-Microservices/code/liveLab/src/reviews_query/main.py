"""reviews-query service: serve aggregates, kept fresh by consuming review-received events.

Run it with:  poetry run uvicorn reviews_query.main:app --port 8002

For the lab the read model is drained on demand (before a read, and via /internal/drain). In
production a background worker would consume the stream continuously.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from common import observability
from common.broker import FileBroker
from common.config import settings
from contracts.review import Aggregate

from .consumer import drain_events
from .store import QueryStore


def create_app(store: QueryStore | None = None, broker: FileBroker | None = None) -> FastAPI:
    """Build the reviews-query app. Tests inject a temp store and broker; production uses defaults."""
    store = store or QueryStore(settings.query_db)
    broker = broker or FileBroker(settings.broker_path)
    app = FastAPI(title="reviews-query", version="1.0")
    observability.install(app, "reviews-query")

    @app.post("/internal/drain")
    def drain() -> dict[str, int]:
        """Consume any pending events into the read model. Returns how many were applied."""
        return {"applied": drain_events(store, broker)}

    @app.get("/v1/aggregates/{product_id}", response_model=Aggregate)
    def get_aggregate(product_id: str) -> Aggregate:
        """Return the rollup for a product, draining new events first to stay fresh."""
        drain_events(store, broker)
        aggregate = store.aggregate(product_id)
        if aggregate is None:
            raise HTTPException(status_code=404, detail="no data for product")
        return aggregate

    return app


app = create_app()
