"""The domain model, new on Day 3: a Reading as a frozen value object.

New this day (Day 2 passed plain dicts around): the reading now has an explicit, named shape, and
`frozen=True` makes it a value object that cannot change after it is built. Checking the values
(a value in range, a non-empty id) is added later, on Day 4.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    device_id: str
    value: float


def parse_reading(row: dict[str, str]) -> Reading:
    """Turn a raw CSV row into a Reading value object."""
    return Reading(device_id=row["device_id"], value=float(row["value"]))
