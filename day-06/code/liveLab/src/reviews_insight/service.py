"""The service layer (Day 3): the summary logic, with its data source injected.

This is the heart of the maintainable refactor. The counting logic lives in one place,
`summarize_rows`. The `SummaryService` holds a ReviewSource that is handed to it from
outside (dependency injection), so it never decides where the data comes from. That single
seam is what lets a test feed in-memory rows while the real application feeds a CSV file,
with the logic untouched in both cases.
"""

from __future__ import annotations

from collections.abc import Iterator

from reviews_insight.decorators import timed
from reviews_insight.models import ReviewParseError, parse_review
from reviews_insight.sources import ReviewSource


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count valid reviews and distinct products, rejecting bad rows honestly (from Day 4)."""
    reviews = 0
    products: set[str] = set()
    rejected = 0
    for row in rows:
        try:
            review = parse_review(row)
        except ReviewParseError:
            rejected += 1  # count it and move on, instead of crashing
            continue
        reviews += 1
        products.add(review.product_id)
    return {"reviews": reviews, "products": len(products), "rejected": rejected}


class SummaryService:
    """Summarizes reviews from any ReviewSource. The source is injected, not built here."""

    def __init__(self, source: ReviewSource) -> None:
        # The service depends on the ReviewSource contract, not on a file or a database.
        # Whatever satisfies the protocol can be passed in.
        self._source = source

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())
