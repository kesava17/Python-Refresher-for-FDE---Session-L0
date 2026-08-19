"""Command line entry point for telemetry-insight."""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from telemetry_insight.config import Config
from telemetry_insight.data import open_records


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Summarize a stream without holding the rows, in constant memory."""
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
    with open_records(config.data_path) as stream:
        result = summarize_stream(stream)

    print(f"[{config.environment}] {config.app_name}")
    print(f"readings: {result['readings']}")
    print(f"devices : {result['devices']}")


if __name__ == "__main__":
    main()
