"""Compute the support-deflection business case from the cost assumptions.

Reads ../data/cost_assumptions.csv and prints the run-rate saving, the first-year
TCO, and the payback period. Conservative by construction.

Run:  python business_case.py
"""

from __future__ import annotations

import csv
import os

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "cost_assumptions.csv")


def load() -> dict[str, float]:
    values: dict[str, float] = {}
    with open(DATA, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                values[row["parameter"]] = float(row["value"])
            except ValueError:
                pass
    return values


def lakh(rupees: float) -> str:
    return f"Rs {rupees / 100000:.1f} lakh"


def main() -> None:
    v = load()
    deflected_per_week = v["in_scope_tickets_per_week"] * v["target_deflection_rate"]
    saving_year = deflected_per_week * v["weeks_per_year"] * v["cost_per_contact"]
    saving_month = saving_year / 12
    tco = v["tco_first_year"]
    payback_months = tco / saving_month

    print(f"Deflected per week      : {deflected_per_week:,.0f} tickets")
    print(f"Run-rate saving / year  : {lakh(saving_year)}  (Rs {saving_year:,.0f})")
    print(f"Saving / month          : {lakh(saving_month)}")
    print(f"TCO (first year)        : {lakh(tco)}")
    print(f"Payback period          : {payback_months:.1f} months")


if __name__ == "__main__":
    main()
