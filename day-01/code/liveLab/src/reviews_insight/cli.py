"""Command line entry point."""

from __future__ import annotations

import argparse

from reviews_insight.config import Config
from reviews_insight.data import load_records


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """A first, tiny summary: how many reviews, and how many products."""
    products = {record["product_id"] for record in records}
    return {"reviews": len(records), "products": len(products)}


def main() -> None:
    parser = argparse.ArgumentParser(description="reviews-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    args = parser.parse_args()

    config = Config.from_env()
    records = load_records(config.data_path)

    if args.command == "summary":
        result = summarize(records)
        print(f"[{config.environment}] {config.app_name}")
        print(f"reviews : {result['reviews']}")
        print(f"products: {result['products']}")


if __name__ == "__main__":
    main()
