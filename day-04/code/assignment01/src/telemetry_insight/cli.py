"""Command line entry point (Day 5: adds a `serve` command for the HTTP API).

The CLI stays a thin surface. `summary` reads configuration, builds the concrete pieces (a
CSV source and the service that uses it), wires them together, and prints the result. `serve`
starts the versioned HTTP API from api.py. All the real logic still lives in the service and
the API, so this surface stays small and easy to read.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from telemetry_insight.config import Config
from telemetry_insight.service import DeviceSummaryService, summarize_rows
from telemetry_insight.sources import CsvReadingSource


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    readings = 0
    devices: set[str] = set()
    for record in records:
        readings += 1
        devices.add(record["device_id"])
    return {"readings": readings, "devices": len(devices)}


def summarize_validated(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 4: parse and reject bad rows. Now a thin alias over the service's shared logic."""
    return summarize_rows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="telemetry-insight")
    parser.add_argument("command", choices=["summary", "serve"], help="what to do")
    parser.add_argument("--port", type=int, default=8000, help="port for the serve command")
    args = parser.parse_args()

    if args.command == "serve":
        # Imported lazily: only the serve path needs the web server, so the summary path stays light.
        import uvicorn

        print(f"serving telemetry-insight on http://127.0.0.1:{args.port} (press Ctrl+C to stop)")
        uvicorn.run("telemetry_insight.api:app", host="127.0.0.1", port=args.port)
        return

    config = Config.from_env()

    # Composition root: build the concrete source, inject it into the service, run it.
    source = CsvReadingSource(config.data_path)
    service = DeviceSummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"readings: {result['readings']}")
    print(f"devices : {result['devices']}")
    print(f"rejected: {result['rejected']}")


if __name__ == "__main__":
    main()
