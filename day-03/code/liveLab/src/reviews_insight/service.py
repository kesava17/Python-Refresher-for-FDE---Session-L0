"""The service layer, new on Day 3: the summary logic, with its data source injected.

New this day: the counting logic moves into one place (`summarize_rows`), and `SummaryService`
receives a `ReviewSource` from outside (dependency injection) instead of building one. That seam
lets a test feed in-memory rows while the real app feeds a CSV file, with the logic unchanged.
"""

from __future__ import annotations

from collections.abc import Iterator

from reviews_insight.decorators import timed
from reviews_insight.models import parse_review
from reviews_insight.sources import ReviewSource


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count reviews and distinct products from a stream of rows."""
    reviews = 0
    products: set[str] = set()
    for row in rows:
        review = parse_review(row)
        reviews += 1
        products.add(review.product_id)
    return {"reviews": reviews, "products": len(products)}


class SummaryService:
    """Summarizes reviews from any ReviewSource. The source is injected, not built here."""

    def __init__(self, source: ReviewSource) -> None:
        # The service depends on the ReviewSource contract, not on a file or a database.
        self._source = source

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())
