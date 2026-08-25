"""Tests for the Day 4 reliability layer: validated Reading and honest parsing."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from telemetry_insight.cli import summarize_validated
from telemetry_insight.models import Reading, ReadingParseError, parse_reading


def test_reading_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        Reading(device_id="D1", value=999.0)  # out of range
    with pytest.raises(ValueError):
        Reading(device_id="", value=20.0)  # empty device id


def test_reading_is_frozen() -> None:
    reading = Reading(device_id="D1", value=20.0)
    with pytest.raises(FrozenInstanceError):
        reading.value = 21.0  # type: ignore[misc]


def test_parse_rejects_malformed_rows() -> None:
    with pytest.raises(ReadingParseError):
        parse_reading({"device_id": "D1", "value": "warm"})  # not a number
    with pytest.raises(ReadingParseError):
        parse_reading({"device_id": "D1"})  # missing value


def test_summarize_counts_good_and_rejects_bad() -> None:
    rows = [
        {"device_id": "D1", "value": "21.4"},
        {"device_id": "D2", "value": "4.1"},
        {"device_id": "D3", "value": "999.0"},  # bad: out of range
        {"device_id": "", "value": "20.0"},  # bad: empty id
    ]
    result = summarize_validated(iter(rows))
    assert result == {"readings": 2, "devices": 2, "rejected": 2}
