"""Tests for the Day 3 value object: a frozen Reading."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from telemetry_insight.models import Reading, parse_reading


def test_reading_is_frozen() -> None:
    reading = Reading(device_id="D1", value=20.0)
    with pytest.raises(FrozenInstanceError):
        reading.value = 21.0  # type: ignore[misc]  # frozen: cannot reassign


def test_readings_compare_by_value() -> None:
    assert Reading("D1", 20.0) == Reading("D1", 20.0)
    assert Reading("D1", 20.0) != Reading("D1", 21.0)


def test_parse_builds_a_reading() -> None:
    assert parse_reading({"device_id": "D1", "value": "20.0"}) == Reading("D1", 20.0)
