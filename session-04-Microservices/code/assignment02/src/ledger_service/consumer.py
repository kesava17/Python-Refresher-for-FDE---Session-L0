"""Consume transaction-recorded events and fold them into the read model, idempotently."""

from __future__ import annotations

from typing import Any

from common.broker import FileBroker

from .store import LedgerStore


def drain_events(store: LedgerStore, broker: FileBroker) -> int:
    """Apply every not-yet-seen transaction-recorded event to the ledger. Returns the count."""

    def handle(event: dict[str, Any]) -> None:
        store.apply_transaction(event["account_id"], int(event["amount_cents"]), event["kind"])

    return broker.drain("transaction-recorded", handle)
