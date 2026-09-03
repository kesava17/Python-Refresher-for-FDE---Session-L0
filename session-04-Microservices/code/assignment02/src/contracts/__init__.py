"""Shared API and event contracts for the transactions system.

In a full multi-repo setup each service would keep its own copy of the contract it depends
on. Here one small package holds them, so the lab stays readable and a contract change is
visible to both sides at once. The path is versioned (`/v1`), so a later, incompatible shape
can ship alongside this one rather than breaking existing callers.
"""

from contracts.transaction import (
    AccountSummary,
    TransactionCreated,
    TransactionIn,
    TransactionRecorded,
)

__all__ = ["AccountSummary", "TransactionCreated", "TransactionIn", "TransactionRecorded"]
