"""Validate the response too (Level 1.4): a model checks what you send back, not only what comes in.

The concept, in plain words:
    Edge validation usually guards the request. But the response is a contract too: callers parse
    what you send back, and a missing or misspelled field breaks them just as badly as bad input
    breaks you. A pydantic model on the outbound side proves the payload is complete before it
    leaves the building.

Why a fresher should care:
    It is easy to hand-build a response dict and forget a field. If a response model constructs
    cleanly, the shape is guaranteed. If it cannot, you find out on your side, at build time, with
    a precise error, instead of the caller finding out in production.

What this demo shows:
    ReviewAccepted requires a status and a review_id. Building it with both succeeds. Building it
    from a dict that is missing review_id raises a pydantic ValidationError, which we catch and
    print.

Run:  poetry run python demo_response_model.py
"""

from __future__ import annotations

import pydantic
from pydantic import BaseModel, Field


class ReviewAccepted(BaseModel):
    """The response contract for an accepted review. Every field here must be present."""

    status: str = Field(min_length=1)  # a human-readable outcome, for example "accepted"
    review_id: str = Field(min_length=1)  # the id the caller uses to fetch the review later


def main() -> None:
    # A complete response builds cleanly, so we know it is safe to send back.
    good = ReviewAccepted(status="accepted", review_id="R-1001")
    print("valid response built :", good)

    # A hand-built dict that forgot review_id looks fine until the model checks it.
    incomplete = {"status": "accepted"}
    try:
        ReviewAccepted(**incomplete)
    except pydantic.ValidationError as exc:
        # The model refuses to build, naming the missing field, so the gap never reaches the caller.
        print("rejected before send :", exc.error_count(), "error(s)")
        print(exc)


if __name__ == "__main__":
    main()
