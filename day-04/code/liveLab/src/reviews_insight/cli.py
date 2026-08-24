"""Command line entry point (Day 5: adds a `serve` command for the HTTP API).

The CLI stays a thin surface. `summary` runs the batch summary as before; `serve` starts the
versioned HTTP API from api.py. All the real logic still lives in the service and the API.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from reviews_insight.config import Config
from reviews_insight.service import SummaryService, summarize_rows
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


def summarize_validated(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 4: parse and reject bad rows. A thin alias over the service's shared logic."""
    return summarize_rows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="reviews-insight")
    parser.add_argument("command", choices=["summary", "serve"], help="what to do")
    parser.add_argument("--port", type=int, default=8000, help="port for the serve command")
    args = parser.parse_args()

    if args.command == "serve":
        # Imported lazily: only the serve path needs the web server, so the summary path stays light.
        import uvicorn

        print(f"serving reviews-insight on http://127.0.0.1:{args.port} (press Ctrl+C to stop)")
        uvicorn.run("reviews_insight.api:app", host="127.0.0.1", port=args.port)
        return

    config = Config.from_env()
    source = CsvReviewSource(config.data_path)
    service = SummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"reviews : {result['reviews']}")
    print(f"products: {result['products']}")
    print(f"rejected: {result['rejected']}")


if __name__ == "__main__":
    main()
