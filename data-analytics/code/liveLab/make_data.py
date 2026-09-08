"""Regenerate data/prices.csv: synthetic daily prices for three fictional tickers.

Deterministic (fixed seed), business days only, with one deliberate gap to practise
forward-fill. This is synthetic teaching data, not real market data. Running it produces a
fresh series from its own seed; the CSV shipped with the lab was generated the same way.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260906
N_DAYS = 260
TICKERS = {
    "ACME": {"p0": 98.0, "mu": 0.0004, "sig": 0.014},
    "GLOBEX": {"p0": 51.0, "mu": 0.0002, "sig": 0.010},
    "INITECH": {"p0": 210.0, "mu": 0.0009, "sig": 0.020},
}


def build() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range("2023-01-02", periods=N_DAYS)
    columns = {}
    for name, cfg in TICKERS.items():
        shocks = cfg["mu"] + cfg["sig"] * rng.standard_normal(N_DAYS)
        columns[name] = np.round(cfg["p0"] * np.cumprod(1 + shocks), 2)
    frame = pd.DataFrame(columns, index=dates)
    frame.index.name = "date"
    frame.iloc[40, frame.columns.get_loc("INITECH")] = np.nan  # a gap to forward-fill
    return frame


if __name__ == "__main__":
    prices = build()
    out = Path(__file__).parent / "data" / "prices.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(out)
    print(f"wrote {len(prices)} rows to {out}")
