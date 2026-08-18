"""Command line entry point."""

from __future__ import annotations

import argparse

from telemetry_insight.config import Config
from telemetry_insight.data import load_records


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """A first, tiny summary: how many readings, and how many devices."""
    devices = {record["device_id"] for record in records}
    return {"readings": len(records), "devices": len(devices)}


def main() -> None:
    parser = argparse.ArgumentParser(description="telemetry-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    args = parser.parse_args()

    config = Config.from_env()
    records = load_records(config.data_path)

    if args.command == "summary":
        result = summarize(records)
        print(f"[{config.environment}] {config.app_name}")
        print(f"readings: {result['readings']}")
        print(f"devices : {result['devices']}")


if __name__ == "__main__":
    main()
