"""The typed contracts every service agrees on: the API models and the one event.

These are pydantic models, so a wrong shape is rejected at the boundary before any service
logic runs. The event (`ReviewReceived`) is what reviews-ingest publishes and reviews-query
consumes, so both sides depend on this one definition.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    """A review submitted by a customer, validated at the ingest boundary."""

    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=1)


class ReviewCreated(BaseModel):
    """The response returned when a review is stored."""

    id: int


class Aggregate(BaseModel):
    """The read model reviews-query serves: the rollup for one product."""

    product_id: str
    count: int
    average_rating: float


class ReviewReceived(BaseModel):
    """The event reviews-ingest publishes after storing a review, consumed by reviews-query."""

    id: int
    product_id: str
    rating: int
