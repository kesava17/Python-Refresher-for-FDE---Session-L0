"""End-to-end smoke of the system, in one process, so you can see the parts talk.

It wires the two services over a shared temp broker (as docker-compose wires them over a real
one), submits transactions through the gateway to transactions-service, lets ledger-service
consume the events, and reads the account summary back through the gateway. It also runs a
reconciliation check (balance equals credits minus debits, in integer paise), shows the
idempotent consumer, and shows the gateway degrading cleanly when ledger-service is stopped.

Run:  poetry run python scripts/smoke.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from common.broker import FileBroker
from gateway.main import create_app as gateway_app
from ledger_service.main import create_app as ledger_app
from ledger_service.store import LedgerStore
from transactions_service.main import create_app as transactions_app
from transactions_service.store import TransactionStore

# A mixed run of credits and debits for one account, in integer minor units (paise).
_RUN = [
    ("credit", 100_00),
    ("debit", 30_00),
    ("credit", 5_50),
    ("debit", 1_25),
    ("credit", 12_75),
]


def _rupees(cents: int) -> str:
    """Render integer paise as a readable rupee amount, for display only."""
    return f"rupees {cents / 100:.2f}"


def main() -> None:
    """Run the full path and print what each step returns."""
    tmp = Path(tempfile.mkdtemp())
    broker = FileBroker(str(tmp / "broker.jsonl"))
    transactions = TestClient(
        transactions_app(store=TransactionStore(str(tmp / "transactions.db")), broker=broker)
    )
    ledger = TestClient(ledger_app(store=LedgerStore(str(tmp / "ledger.db")), broker=broker))

    print("health:")
    print("  transactions-service ->", transactions.get("/health").json())
    print("  ledger-service       ->", ledger.get("/health").json())

    print("\nsubmit a mixed run of transactions for acc-1 (through transactions-service):")
    for kind, amount_cents in _RUN:
        created = transactions.post(
            "/v1/transactions",
            json={"account_id": "acc-1", "amount_cents": amount_cents, "kind": kind},
        )
        print(f"  {kind:<6} {_rupees(amount_cents):>14} -> {created.status_code} {created.json()}")

    print("\nledger-service consumes the events and serves the account summary:")
    summary = ledger.get("/v1/accounts/acc-1/summary").json()
    print("  /v1/accounts/acc-1/summary ->", summary)

    print("\nreconciliation check (balance must equal credits minus debits, in paise):")
    expected = sum(c if k == "credit" else -c for k, c in _RUN)
    print(f"  expected balance = {expected} ({_rupees(expected)})")
    print(f"  ledger balance   = {summary['balance_cents']} ({_rupees(summary['balance_cents'])})")
    print(f"  reconciled       = {summary['balance_cents'] == expected}")

    print("\na duplicate event does not double-count (idempotent consumer):")
    broker.publish(
        "transaction-recorded",
        {"id": 1, "account_id": "acc-1", "amount_cents": 100_00, "kind": "credit"},
    )
    print("  /v1/accounts/acc-1/summary ->", ledger.get("/v1/accounts/acc-1/summary").json())

    print("\nunknown account escalates to a clear 404, not a guess:")
    print("  /v1/accounts/unknown/summary ->", ledger.get("/v1/accounts/unknown/summary").status_code)

    print("\nthe gateway degrades cleanly when ledger-service is down:")
    down_gateway = TestClient(
        gateway_app(
            transactions_url="http://127.0.0.1:59998",
            ledger_url="http://127.0.0.1:59999",
        )
    )
    degraded = down_gateway.get("/bff/account/acc-1")
    print(f"  /bff/account/acc-1 -> {degraded.status_code} {degraded.json()}")

    print("\nthe correlation id sent in is echoed back for tracing:")
    echoed = transactions.get("/health", headers={"X-Correlation-ID": "smoke-123"})
    print("  X-Correlation-ID ->", echoed.headers.get("X-Correlation-ID"))


if __name__ == "__main__":
    main()
