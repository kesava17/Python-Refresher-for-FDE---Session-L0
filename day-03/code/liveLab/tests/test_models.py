"""Tests for the Day 3 value object: a frozen Review."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from reviews_insight.models import Review, parse_review


def test_review_is_frozen() -> None:
    review = Review(product_id="P1", rating=5)
    with pytest.raises(FrozenInstanceError):
        review.rating = 4  # type: ignore[misc]  # frozen: cannot reassign


def test_reviews_compare_by_value() -> None:
    assert Review("P1", 5) == Review("P1", 5)
    assert Review("P1", 5) != Review("P1", 4)


def test_parse_builds_a_review() -> None:
    assert parse_review({"product_id": "P1", "rating": "5"}) == Review("P1", 5)
