"""Tests for the Day 4 reliability layer: validated Review and honest parsing."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from reviews_insight.cli import summarize_validated
from reviews_insight.models import Review, ReviewParseError, parse_review


def test_review_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        Review(product_id="P1", rating=11)  # rating out of range
    with pytest.raises(ValueError):
        Review(product_id="", rating=5)  # empty product id


def test_review_is_frozen() -> None:
    review = Review(product_id="P1", rating=5)
    with pytest.raises(FrozenInstanceError):
        review.rating = 4  # type: ignore[misc]  # frozen: cannot reassign


def test_parse_rejects_malformed_rows() -> None:
    with pytest.raises(ReviewParseError):
        parse_review({"product_id": "P1", "rating": "eleven"})  # not an int
    with pytest.raises(ReviewParseError):
        parse_review({"product_id": "P1"})  # missing rating


def test_summarize_counts_good_and_rejects_bad() -> None:
    rows = [
        {"product_id": "P1", "rating": "5"},
        {"product_id": "P1", "rating": "4"},
        {"product_id": "P2", "rating": "11"},  # bad: out of range
        {"product_id": "", "rating": "3"},  # bad: empty id
    ]
    result = summarize_validated(iter(rows))
    assert result == {"reviews": 2, "products": 1, "rejected": 2}
