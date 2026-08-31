"""Pareto analysis of the Sunrise support tickets.

Reads ../data/support_tickets.csv, counts tickets by question_type, sorts
them highest first, and prints each type's share and the running cumulative
share. The "vital few" are the types above the 60-to-80 percent cumulative
line. No third-party libraries required.

Run:  python pareto.py
"""

from __future__ import annotations

import csv
import os
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "support_tickets.csv")


def main() -> None:
    counts: Counter[str] = Counter()
    with open(DATA, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            counts[row["question_type"]] += 1

    total = sum(counts.values())
    print(f"{'question_type':<20}{'count':>7}{'share':>9}{'cumulative':>12}")
    print("-" * 48)
    cumulative = 0
    for qtype, count in counts.most_common():
        cumulative += count
        share = 100 * count / total
        cum_share = 100 * cumulative / total
        marker = "  <- vital few" if cum_share <= 62 else ""
        print(f"{qtype:<20}{count:>7}{share:>8.1f}%{cum_share:>11.1f}%{marker}")

    print("-" * 48)
    print(f"{'TOTAL':<20}{total:>7}")


if __name__ == "__main__":
    main()
