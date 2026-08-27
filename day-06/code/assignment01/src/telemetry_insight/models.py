"""The validated telemetry model: a Reading that cannot exist in a bad state (Day 4)."""

from __future__ import annotations

from dataclasses import dataclass


class ReadingParseError(ValueError):
    """Raised when a raw row cannot be turned into a valid Reading."""


@dataclass(frozen=True)
class Reading:
    device_id: str
    value: float

    def __post_init__(self) -> None:
        if not self.device_id:
            raise ValueError("device_id must not be empty")
        if not -50.0 <= self.value <= 150.0:
            raise ValueError(f"value out of range: {self.value}")


def parse_reading(row: dict[str, str]) -> Reading:
    """Turn a raw CSV row into a validated Reading, or raise ReadingParseError."""
    try:
        return Reading(device_id=row["device_id"], value=float(row["value"]))
    except (KeyError, ValueError) as exc:
        raise ReadingParseError(f"bad row: {row}") from exc
