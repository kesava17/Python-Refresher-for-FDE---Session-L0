"""A real REST contract (Levels 1.2 and 1.3): versioned routes with a machine-readable spec.

The concept, in plain words:
    REST is a small set of habits for talking over HTTP: nouns as paths, verbs as methods, status
    codes that mean something. Versioning the path (a /v1 prefix) lets the contract change later
    without breaking today's callers. FastAPI turns all of this into a live app plus an OpenAPI
    document, which is the contract other teams actually build against.

Why a fresher should care:
    The contract is not a wiki page that drifts out of date: it is generated from the code, so it
    is always true. TestClient lets you exercise the whole HTTP surface in-process, no server and
    no network, which is exactly how you would test it in CI.

What this demo shows:
    A tiny app with GET /health and POST /v1/reviews. Health returns a status object, a valid
    review returns 201, a rating of 11 returns 422 (rejected at the edge), and the generated
    OpenAPI document lists the versioned route.

Run:  poetry run python demo_rest_contract.py
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    """The request contract for a submitted review, validated by FastAPI at the edge."""

    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)  # a value outside 1 to 5 is rejected with a 422


def create_app() -> FastAPI:
    """Build the API. The store lives inside, so each app instance is independent."""
    app = FastAPI(title="reviews-insight", version="0.5.0")
    store: list[dict[str, str]] = []

    @app.get("/health")
    def health() -> dict[str, str]:
        # A liveness route so other systems can check the service is up.
        return {"status": "ok"}

    @app.post("/v1/reviews", status_code=201)
    def submit(review: ReviewIn) -> dict[str, str]:
        # By the time we reach here, review is already valid: the edge rejected any bad input.
        store.append({"product_id": review.product_id, "rating": str(review.rating)})
        return {"status": "accepted"}

    return app


def main() -> None:
    # TestClient drives the app in-process: real routing and validation, no network involved.
    client = TestClient(create_app())

    # The liveness route answers with a simple, predictable body.
    health = client.get("/health")
    print("GET /health         :", health.status_code, health.json())

    # A well-formed review is accepted and reported with 201 Created.
    ok = client.post("/v1/reviews", json={"product_id": "P1", "rating": 4})
    print("POST valid review   :", ok.status_code, ok.json())

    # A rating of 11 fails the contract, so FastAPI answers 422 before our handler runs.
    bad = client.post("/v1/reviews", json={"product_id": "P1", "rating": 11})
    print("POST rating 11      :", bad.status_code, "(unprocessable)")

    # The OpenAPI document is generated from the code, so the versioned route is really there.
    spec = client.get("/openapi.json").json()
    print("/v1/reviews in spec :", "/v1/reviews" in spec["paths"])


if __name__ == "__main__":
    main()
