"""transactions-service: POST a transaction, store it, publish a transaction-recorded event.

Run it with:  poetry run uvicorn transactions_service.main:app --port 8001

The path is versioned (`/v1`), so the contract can evolve without breaking existing callers.
"""

from __future__ import annotations

from fastapi import FastAPI

from common import observability
from common.broker import FileBroker
from common.config import settings
from contracts.transaction import TransactionCreated, TransactionIn, TransactionRecorded

from .store import TransactionStore


def create_app(store: TransactionStore | None = None, broker: FileBroker | None = None) -> FastAPI:
    """Build the transactions-service app. Tests inject a temp store and broker; production uses defaults."""
    store = store or TransactionStore(settings.transactions_db)
    broker = broker or FileBroker(settings.broker_path)
    app = FastAPI(title="transactions-service", version="1.0")
    observability.install(app, "transactions-service")
    log = observability.configure_logging("transactions-service")

    @app.post("/v1/transactions", status_code=201, response_model=TransactionCreated)
    def create_transaction(transaction: TransactionIn) -> TransactionCreated:
        """Store a validated transaction and publish an event for the ledger to consume."""
        transaction_id = store.save(transaction)
        broker.publish(
            "transaction-recorded",
            TransactionRecorded(
                id=transaction_id,
                account_id=transaction.account_id,
                amount_cents=transaction.amount_cents,
                kind=transaction.kind,
            ).model_dump(),
        )
        log.info(f"stored transaction {transaction_id} for {transaction.account_id}")
        return TransactionCreated(id=transaction_id)

    @app.get("/v1/transactions/{account_id}", response_model=list[TransactionRecorded])
    def list_transactions(account_id: str) -> list[TransactionRecorded]:
        """List an account's stored transactions, oldest first."""
        return store.list_for_account(account_id)

    return app


app = create_app()
