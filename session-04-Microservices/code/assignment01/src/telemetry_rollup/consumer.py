"""Consume reading-received events and fold them into the read model, idempotently."""

from __future__ import annotations

from typing import Any

from common.broker import FileBroker

from .store import RollupStore


def drain_events(store: RollupStore, broker: FileBroker) -> int:
    """Apply every not-yet-seen reading-received event to the read store. Returns the count.

    The broker skips any event whose id was already processed, so a replayed event under
    at-least-once delivery leaves the rollup (count and average) unchanged.
    """

    def handle(event: dict[str, Any]) -> None:
        store.apply_reading(event["device_id"], float(event["value"]))

    return broker.drain("reading-received", handle)
