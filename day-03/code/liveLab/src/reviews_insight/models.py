"""The domain model, new on Day 3: a Review as a frozen value object.

New this day (Day 2 passed plain dicts around): the review now has an explicit, named shape, and
`frozen=True` makes it a value object that cannot change after it is built. Checking the values
(a valid rating, a non-empty id) is added later, on Day 4.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Review:
    product_id: str
    rating: int


def parse_review(row: dict[str, str]) -> Review:
    """Turn a raw CSV row into a Review value object."""
    return Review(product_id=row["product_id"], rating=int(row["rating"]))
