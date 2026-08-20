"""Command line entry point (new on Day 3: a thin composition root).

The CLI's only jobs now are to read configuration, build the concrete pieces (a CSV source,
a default strategy, and the service that uses them), wire them together, and print the
result. All the real logic lives in the service, so this surface stays small and easy to read.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from transactions_insight.config import Config
from transactions_insight.service import LedgerService
from transactions_insight.sources import CsvTransactionSource
from transactions_insight.strategies import BySizeStrategy


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    transactions = 0
    accounts: set[str] = set()
    for record in records:
        transactions += 1
        accounts.add(record["account_id"])
    return {"transactions": transactions, "accounts": len(accounts)}


def main() -> None:
    parser = argparse.ArgumentParser(description="transactions-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    parser.parse_args()

    config = Config.from_env()

    # Composition root: build the concrete source and strategy, inject them, run the service.
    source = CsvTransactionSource(config.data_path)
    strategy = BySizeStrategy()
    service = LedgerService(source, strategy)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"transactions: {result['transactions']}")
    print(f"accounts    : {result['accounts']}")


if __name__ == "__main__":
    main()
