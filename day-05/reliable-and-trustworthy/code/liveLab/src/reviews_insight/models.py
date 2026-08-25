"""The validated domain model: a Review that cannot exist in a bad state (Day 4)."""

from __future__ import annotations

from dataclasses import dataclass


class ReviewParseError(ValueError):
    """Raised when a raw row cannot be turned into a valid Review."""


@dataclass(frozen=True)
class Review:
    product_id: str
    rating: int

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ValueError("product_id must not be empty")
        if not 1 <= self.rating <= 5:
            raise ValueError(f"rating out of range: {self.rating}")


def parse_review(row: dict[str, str]) -> Review:
    """Turn a raw CSV row into a validated Review, or raise ReviewParseError."""
    try:
        return Review(product_id=row["product_id"], rating=int(row["rating"]))
    except (KeyError, ValueError) as exc:
        raise ReviewParseError(f"bad row: {row}") from exc
