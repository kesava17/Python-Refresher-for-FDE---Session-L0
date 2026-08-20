"""Generate a large telemetry CSV so memory and speed differences are visible."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


def main(rows: int, path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["device_id", "ts", "value"])
        for i in range(rows):
            device = f"D{i % 200}"  # 200 distinct devices
            value = round(20.0 + 10.0 * math.sin(i / 100.0), 3)
            writer.writerow([device, f"2026-01-01T00:{(i % 60):02d}:00", value])
    print(f"wrote {rows} rows to {path}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    main(count, "data/telemetry_big.csv")
