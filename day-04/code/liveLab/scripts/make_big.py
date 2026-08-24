"""Generate a large reviews CSV so memory and speed differences are visible."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

WORDS = ["great", "good", "average", "poor", "excellent", "broke", "fantastic", "ok"]


def main(rows: int, path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["product_id", "rating", "text"])
        for i in range(rows):
            product = f"P{i % 500}"  # 500 distinct products
            writer.writerow(
                [product, (i % 5) + 1, f"{WORDS[i % len(WORDS)]} product number {i}"]
            )
    print(f"wrote {rows} rows to {path}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    main(count, "data/reviews_big.csv")
