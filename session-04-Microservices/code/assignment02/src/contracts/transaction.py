"""The typed contracts every service agrees on: the API models and the one event.

These are pydantic models, so a wrong shape is rejected at the boundary before any service
logic runs. Money is held as `amount_cents`, an integer count of minor units (paise for the
rupee), never a float, so no rounding drift can creep into a balance. The event
(`TransactionRecorded`) is what transactions-service publishes and ledger-service consumes,
so both sides depend on this one definition.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TransactionIn(BaseModel):
    """A transaction submitted by a client, validated at the transactions boundary."""

    account_id: str = Field(min_length=1)
    amount_cents: int = Field(gt=0)
    kind: Literal["credit", "debit"]


class TransactionCreated(BaseModel):
    """The response returned when a transaction is stored."""

    id: int


class AccountSummary(BaseModel):
    """The read model ledger-service serves: the rollup for one account."""

    account_id: str
    count: int
    balance_cents: int


class TransactionRecorded(BaseModel):
    """The event transactions-service publishes after storing a transaction.

    Consumed by ledger-service to fold the amount into the account balance: a credit adds
    and a debit subtracts, all in integer minor units.
    """

    id: int
    account_id: str
    amount_cents: int
    kind: str
