"""reviews-ingest service: POST a review, store it, publish a review-received event.

Run it with:  poetry run uvicorn reviews_ingest.main:app --port 8001
"""

from __future__ import annotations

from fastapi import FastAPI

from common import observability
from common.broker import FileBroker
from common.config import settings
from contracts.review import ReviewCreated, ReviewIn, ReviewReceived

from .store import IngestStore


def create_app(store: IngestStore | None = None, broker: FileBroker | None = None) -> FastAPI:
    """Build the reviews-ingest app. Tests inject a temp store and broker; production uses defaults."""
    store = store or IngestStore(settings.ingest_db)
    broker = broker or FileBroker(settings.broker_path)
    app = FastAPI(title="reviews-ingest", version="1.0")
    observability.install(app, "reviews-ingest")
    log = observability.configure_logging("reviews-ingest")

    @app.post("/v1/reviews", status_code=201, response_model=ReviewCreated)
    def create_review(review: ReviewIn) -> ReviewCreated:
        """Store a validated review and publish an event for the read side to consume."""
        review_id = store.save(review)
        broker.publish(
            "review-received",
            ReviewReceived(id=review_id, product_id=review.product_id, rating=review.rating).model_dump(),
        )
        log.info(f"stored review {review_id} for {review.product_id}")
        return ReviewCreated(id=review_id)

    return app


app = create_app()
