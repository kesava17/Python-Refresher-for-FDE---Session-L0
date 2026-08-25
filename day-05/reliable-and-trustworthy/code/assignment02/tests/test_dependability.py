"""Assignment 2 tests: no data loss and an exactly-once effect for financial transactions.

These are the dependability guarantees the transactions domain lives on. Each test names the
failure it defends against: a lost response that triggers a retry, a crash in the middle of a
write, a saturated service, and a ledger that could go negative.
"""

from __future__ import annotations

import random

import pytest
from fastapi.testclient import TestClient

from transactions_insight.api import create_app
from transactions_insight.dependability import (
    LedgerEntry,
    TransactionStore,
    running_balance_ok,
)


def _client() -> TestClient:
    # A fresh app (and a fresh store) per test, so the tests do not affect each other.
    return TestClient(create_app())


# --- Exactly-once idempotency -------------------------------------------------------


def test_same_key_twice_records_one_and_returns_the_same_result() -> None:
    # Simulate a lost response: the client sends a transaction, the reply is lost, so the client
    # retries with the same idempotency key. The service must record exactly one transaction and
    # return the same result both times, never charging the account twice.
    client = _client()
    body = {"account_id": "A1", "amount": 250.0, "currency": "INR"}
    headers = {"Idempotency-Key": "retry-key-1"}

    first = client.post("/v1/transactions", json=body, headers=headers)
    second = client.post("/v1/transactions", json=body, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()  # the retry returns the same result
    assert client.get("/v1/transactions").json()["total"] == 1  # exactly one is stored


def test_a_key_in_the_body_is_honoured_too() -> None:
    # The idempotency key may travel in the body (a per-transaction key) instead of the header.
    client = _client()
    body = {"account_id": "A2", "amount": 99.0, "currency": "INR", "idempotency_key": "body-key"}

    client.post("/v1/transactions", json=body)
    client.post("/v1/transactions", json=body)

    assert client.get("/v1/transactions").json()["total"] == 1


def test_no_key_records_each_call() -> None:
    # Without a key there is no idempotency promise, so two calls record two transactions.
    client = _client()
    body = {"account_id": "A3", "amount": 10.0, "currency": "INR"}
    client.post("/v1/transactions", json=body)
    client.post("/v1/transactions", json=body)
    assert client.get("/v1/transactions").json()["total"] == 2


# --- Crash-in-the-middle (all-or-nothing writes) ------------------------------------


class _SimulatedCrash(RuntimeError):
    """Stands in for a process interruption during a write."""


def test_crash_in_the_middle_stores_none_then_a_retry_stores_exactly_one() -> None:
    # Simulate an interruption during the write: the on_prepared hook raises after the record is
    # prepared but before it is committed. The store must be left with none of it, never a
    # partial row. A later successful write then stores exactly one, never two.
    store = TransactionStore()
    record = {"account_id": "A9", "amount": "500.0", "currency": "INR"}

    def crash() -> None:
        raise _SimulatedCrash("interrupted before commit")

    with pytest.raises(_SimulatedCrash):
        store.add(record, key="k1", on_prepared=crash)

    assert len(store) == 0  # whole or none: the interrupted write left nothing behind

    stored, created = store.add(record, key="k1")  # the retry now succeeds
    assert created is True
    assert len(store) == 1  # exactly one, never a duplicate from the failed attempt
    assert stored["account_id"] == "A9"


# --- Readiness ----------------------------------------------------------------------


def test_ready_returns_200_normally() -> None:
    # Under normal load the service is ready to take work.
    resp = _client().get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_health_stays_plain_liveness() -> None:
    # Liveness is separate from readiness and always answers a plain ok.
    assert _client().get("/health").json() == {"status": "ok"}


# --- Metrics ------------------------------------------------------------------------


def test_metrics_report_request_and_error_counts() -> None:
    client = _client()
    client.get("/health")
    text = client.get("/metrics").text
    assert "requests_total" in text
    assert "errors_total" in text
    assert "request_duration_ms_avg" in text


# --- Ledger invariant (property / parametric test) ----------------------------------


def _random_safe_sequence(rng: random.Random, length: int) -> list[LedgerEntry]:
    """Build a random posting sequence that, by construction, never overdraws an account.

    Each step either credits a random amount or debits at most the account's current balance, so
    a correct ledger must keep every running balance at or above zero.
    """
    accounts = ["A0", "A1", "A2"]
    balances = {acc: 0 for acc in accounts}
    entries: list[LedgerEntry] = []
    for _ in range(length):
        acc = rng.choice(accounts)
        if rng.random() < 0.5 or balances[acc] == 0:
            amount = rng.randint(1, 10_000)  # a credit in paise
        else:
            amount = -rng.randint(1, balances[acc])  # a debit no larger than the balance
        balances[acc] += amount
        entries.append(LedgerEntry(account_id=acc, amount_paise=amount))
    return entries


def test_ledger_invariant_holds_over_many_generated_sequences() -> None:
    # A parametric property check: over many generated valid sequences, the running balance never
    # goes below zero. hypothesis is not a direct dev dependency in the base, so we generate the
    # cases ourselves with a seeded random source (repeatable, and no new heavy dependency).
    rng = random.Random(1234)
    for _ in range(500):
        entries = _random_safe_sequence(rng, length=rng.randint(0, 40))
        assert running_balance_ok(entries) is True


def test_ledger_invariant_catches_an_overdraft() -> None:
    # The invariant must actually fire: a debit larger than the balance breaks it.
    entries = [
        LedgerEntry("A0", 500),  # credit 5 rupees
        LedgerEntry("A0", -900),  # debit 9 rupees, which would overdraw the account
    ]
    assert running_balance_ok(entries) is False
