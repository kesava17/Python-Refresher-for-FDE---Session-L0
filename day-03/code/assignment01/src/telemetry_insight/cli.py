"""Command line entry point (new on Day 3: a thin composition root).

New this day: the CLI no longer holds the logic. It builds the concrete source, injects it into
the service, and prints. All the real work lives in the service.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from telemetry_insight.config import Config
from telemetry_insight.service import DeviceSummaryService
from telemetry_insight.sources import CsvReadingSource


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    readings = 0
    devices: set[str] = set()
    for record in records:
        readings += 1
        devices.add(record["device_id"])
    return {"readings": readings, "devices": len(devices)}


def main() -> None:
    parser = argparse.ArgumentParser(description="telemetry-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    parser.parse_args()

    config = Config.from_env()

    # Composition root: build the source, inject it into the service, run it.
    source = CsvReadingSource(config.data_path)
    service = DeviceSummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"readings: {result['readings']}")
    print(f"devices : {result['devices']}")


if __name__ == "__main__":
    main()
