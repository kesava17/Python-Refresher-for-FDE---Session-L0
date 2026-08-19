"""Command line entry point for transactions-insight."""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from transactions_insight.config import Config
from transactions_insight.data import open_records


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Summarize a stream without holding the rows, in constant memory."""
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
    with open_records(config.data_path) as stream:
        result = summarize_stream(stream)

    print(f"[{config.environment}] {config.app_name}")
    print(f"transactions: {result['transactions']}")
    print(f"accounts    : {result['accounts']}")


if __name__ == "__main__":
    main()
