"""The typed contracts every service agrees on: the API models and the one event.

These are pydantic models, so a wrong shape is rejected at the boundary before any service
logic runs. The event (`ReadingReceived`) is what telemetry-ingest publishes and
telemetry-rollup consumes, so both sides depend on this one definition.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReadingIn(BaseModel):
    """A device reading submitted to the platform, validated at the ingest boundary."""

    device_id: str = Field(min_length=1)
    value: float
    ts: str = Field(min_length=1)


class ReadingCreated(BaseModel):
    """The response returned when a reading is stored."""

    id: int


class Rollup(BaseModel):
    """The read model telemetry-rollup serves: the rollup for one device."""

    device_id: str
    count: int
    average_value: float


class ReadingReceived(BaseModel):
    """The event telemetry-ingest publishes after storing a reading, consumed by telemetry-rollup."""

    id: int
    device_id: str
    value: float
