"""Page large collections (Level 1.5): a list endpoint returns a window, never the whole table.

The concept, in plain words:
    A collection can hold thousands of rows. Returning all of them in one response is slow, heavy,
    and often useless to the caller. A list endpoint takes a limit and an offset and hands back one
    page: a small slice of items, plus the total count so the caller knows how far it can go.

Why a fresher should care:
    "Give me everything" is the request that quietly takes a service down as the data grows. Paging
    is the standard fix, and callers expect the same three knobs everywhere: limit, offset, total.
    Building it once by hand makes the shape obvious.

What this demo shows:
    A tiny app with GET /v1/reviews?limit=&offset= over an in-memory list of 25 reviews, driven by
    TestClient. We fetch a page and print that it holds the right items, the right total, and the
    limit and offset it echoed back, and that its length is the page size, not the whole list.

Run:  poetry run python demo_pagination.py
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

# A stand-in collection: 25 product reviews, more than fits comfortably in one response.
ALL_REVIEWS: list[dict[str, object]] = [
    {"review_id": f"R-{i:04d}", "product_id": f"P{i % 5}", "rating": (i % 5) + 1}
    for i in range(25)
]


def create_app() -> FastAPI:
    """Build the API. The collection is shared read-only, so each instance behaves the same."""
    app = FastAPI(title="reviews-insight", version="0.5.0")

    @app.get("/v1/reviews")
    def list_reviews(limit: int = 10, offset: int = 0) -> dict[str, object]:
        # Slice out one window and report the knobs, so the caller can walk the rest itself.
        window = ALL_REVIEWS[offset : offset + limit]
        return {
            "items": window,
            "total": len(ALL_REVIEWS),
            "limit": limit,
            "offset": offset,
        }

    return app


def main() -> None:
    # TestClient drives the app in-process: real routing, no network involved.
    client = TestClient(create_app())

    # Ask for the second page of five: items 5 through 9.
    page = client.get("/v1/reviews", params={"limit": 5, "offset": 5}).json()

    print("total in collection :", page["total"])
    print("limit echoed back   :", page["limit"])
    print("offset echoed back  :", page["offset"])
    print("items on this page  :", len(page["items"]), "(not the whole list)")
    print("first id on page    :", page["items"][0]["review_id"])
    print("last id on page     :", page["items"][-1]["review_id"])


if __name__ == "__main__":
    main()
