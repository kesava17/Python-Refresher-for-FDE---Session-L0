"""Command line entry point."""

from __future__ import annotations

import argparse

from transactions_insight.config import Config
from transactions_insight.data import load_records


def summarize(records: list[dict[str, str]]) -> dict[str, float]:
    """A first, tiny summary: count, distinct accounts, and total amount."""
    accounts = {record["account_id"] for record in records}
    total = round(sum(float(record["amount"]) for record in records), 2)
    return {"transactions": len(records), "accounts": len(accounts), "total": total}


def main() -> None:
    parser = argparse.ArgumentParser(description="transactions-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    args = parser.parse_args()

    config = Config.from_env()
    records = load_records(config.data_path)

    if args.command == "summary":
        result = summarize(records)
        print(f"[{config.environment}] {config.app_name}")
        print(f"transactions: {int(result['transactions'])}")
        print(f"accounts    : {int(result['accounts'])}")
        print(f"total       : {result['total']:.2f}")


if __name__ == "__main__":
    main()
