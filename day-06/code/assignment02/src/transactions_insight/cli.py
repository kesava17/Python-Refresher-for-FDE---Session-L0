"""Command line entry point (Day 5: adds a `serve` command for the HTTP API).

The CLI stays a thin surface. `summary` reads configuration, builds the concrete pieces (a CSV
source, a default strategy, and the service that uses them), wires them together, and prints the
result. `serve` starts the versioned HTTP API from api.py. All the real logic still lives in the
service and the API, so this surface stays small and easy to read.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from transactions_insight.config import Config
from transactions_insight.service import LedgerService, summarize_rows
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


def summarize_validated(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 4: parse and reject bad rows. Now a thin alias over the service's shared logic."""
    return summarize_rows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="transactions-insight")
    parser.add_argument("command", choices=["summary", "serve"], help="what to do")
    parser.add_argument("--port", type=int, default=8000, help="port for the serve command")
    args = parser.parse_args()

    if args.command == "serve":
        # Imported lazily: only the serve path needs the web server, so the summary path stays light.
        import uvicorn

        print(f"serving transactions-insight on http://127.0.0.1:{args.port} (press Ctrl+C to stop)")
        uvicorn.run("transactions_insight.api:app", host="127.0.0.1", port=args.port)
        return

    config = Config.from_env()

    # Composition root: build the concrete source and strategy, inject them, run the service.
    source = CsvTransactionSource(config.data_path)
    strategy = BySizeStrategy()
    service = LedgerService(source, strategy)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"transactions: {result['transactions']}")
    print(f"accounts    : {result['accounts']}")
    print(f"rejected    : {result['rejected']}")


if __name__ == "__main__":
    main()
