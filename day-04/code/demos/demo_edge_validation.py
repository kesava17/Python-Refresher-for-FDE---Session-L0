"""Validate at the edge (Level 1.1): reject bad input where it arrives, not deep inside.

The concept, in plain words:
    A service takes input from the outside world, and the outside world sends malformed data. The
    edge is the one place to check it: if a value is wrong, refuse it immediately with a clear
    error, so the rest of the code can trust that everything it sees is already valid.

Why a fresher should care:
    A pydantic BaseModel turns a wall of hand-written if-checks into one declared shape. Fields
    carry their own rules (a rating must be 1 to 5), and building the model either succeeds with
    clean data or raises a precise, readable error naming the offending field.

What this demo shows:
    ReviewIn declares its rules once. A valid dict builds a model with no fuss. A rating of 11
    fails the model's own constraint and raises a ValidationError, which we catch and print.

Run:  poetry run python demo_edge_validation.py
"""

from __future__ import annotations

import pydantic
from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    """The request contract. Each field carries its own rule, checked when the model is built."""

    product_id: str = Field(min_length=1)  # an empty product id is meaningless, so reject it
    rating: int = Field(ge=1, le=5)  # a value outside 1 to 5 is out of contract


def main() -> None:
    # A well-formed payload builds cleanly, and from here on the data can be trusted.
    good = ReviewIn(product_id="P1", rating=4)
    print("valid review built :", good)

    # A rating of 11 breaks the ge/le rule. pydantic raises before any of our logic runs.
    try:
        ReviewIn(product_id="P1", rating=11)
    except pydantic.ValidationError as exc:
        # The error is precise: it names the field (rating) and why it failed.
        print("rejected at the edge:", exc.error_count(), "error(s)")
        print(exc)


if __name__ == "__main__":
    main()
