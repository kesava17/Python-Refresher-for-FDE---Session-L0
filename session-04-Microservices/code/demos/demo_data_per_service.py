"""Data per service: each service owns its store; state moves by event, not a shared table.

Two services keep their own store. The query side never opens the ingest store; it builds its
own view from the event it consumes, which is what lets each side change its data model
without breaking the other. Standard library only.

Run:  poetry run python demo_data_per_service.py
"""

from __future__ import annotations


class IngestStore:
    """The write side's private store of submitted reviews."""

    def __init__(self) -> None:
        """Start with an empty store."""
        self.rows: dict[int, tuple[str, int]] = {}

    def save(self, review_id: int, product_id: str, rating: int) -> None:
        """Record a review by id."""
        self.rows[review_id] = (product_id, rating)


class QueryStore:
    """The read side's private rollup, built only from events."""

    def __init__(self) -> None:
        """Start with an empty rollup."""
        self.agg: dict[str, tuple[int, int]] = {}

    def apply(self, product_id: str, rating: int) -> None:
        """Fold one review into the product's rollup."""
        count, total = self.agg.get(product_id, (0, 0))
        self.agg[product_id] = (count + 1, total + rating)

    def average(self, product_id: str) -> float | None:
        """Return the average rating for a product, or None if unseen."""
        count, total = self.agg.get(product_id, (0, 0))
        return round(total / count, 2) if count else None


def main() -> None:
    """Ingest owns its rows and publishes events; query builds its own view from them."""
    ingest = IngestStore()
    query = QueryStore()

    for review_id, (product_id, rating) in enumerate([("p1", 5), ("p1", 3)], start=1):
        ingest.save(review_id, product_id, rating)
        # ingest publishes a review-received event; the query side consumes it and updates
        # its own store. It never reads the ingest store directly.
        query.apply(product_id, rating)

    print(f"ingest store rows:      {ingest.rows}")
    print(f"query average for p1:   {query.average('p1')}")
    print("\nThe query side never opened the ingest store. It built its own view from the event,")
    print("which is what lets each service own and evolve its data independently.")


if __name__ == "__main__":
    main()
