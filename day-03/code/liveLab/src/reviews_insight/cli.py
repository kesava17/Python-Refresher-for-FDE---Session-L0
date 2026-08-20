"""Command line entry point (new on Day 3: a thin composition root).

New this day: the CLI no longer holds the logic. It builds the concrete source, injects it into
the service, and prints. All the real work lives in the service.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from reviews_insight.config import Config
from reviews_insight.service import SummaryService
from reviews_insight.sources import CsvReviewSource


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """Day 1: summarize a list of records held in memory."""
    products = {record["product_id"] for record in records}
    return {"reviews": len(records), "products": len(products)}


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    reviews = 0
    products: set[str] = set()
    for record in records:
        reviews += 1
        products.add(record["product_id"])
    return {"reviews": reviews, "products": len(products)}


def main() -> None:
    parser = argparse.ArgumentParser(description="reviews-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    parser.parse_args()

    config = Config.from_env()

    # Composition root: build the source, inject it into the service, run it.
    source = CsvReviewSource(config.data_path)
    service = SummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"reviews : {result['reviews']}")
    print(f"products: {result['products']}")


if __name__ == "__main__":
    main()
