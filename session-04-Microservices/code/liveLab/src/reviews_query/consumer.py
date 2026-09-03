"""Consume review-received events and fold them into the read model, idempotently."""

from __future__ import annotations

from typing import Any

from common.broker import FileBroker

from .store import QueryStore


def drain_events(store: QueryStore, broker: FileBroker) -> int:
    """Apply every not-yet-seen review-received event to the read store. Returns the count."""

    def handle(event: dict[str, Any]) -> None:
        store.apply_review(event["product_id"], int(event["rating"]))

    return broker.drain("review-received", handle)
