"""A tiny file-backed message broker, so the asynchronous path runs with no external service.

`publish` appends an event to a JSONL file; `drain` reads the events for a topic and hands
each to a handler exactly once, tracking processed ids in a sidecar file. This gives the two
teaching properties that matter: at-least-once delivery, and an idempotent consumer that
skips a duplicate. In production this seam is swapped for a real broker (for example Redis or
a queue); the `publish` and `drain` interface stays the same.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any


class FileBroker:
    """A JSONL-file broker with idempotent draining, shared by producer and consumer."""

    def __init__(self, path: str) -> None:
        """Create a broker over the given JSONL file, plus a sidecar file of processed ids."""
        self._path = Path(path)
        self._seen_path = Path(f"{path}.seen")
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def publish(self, topic: str, event: dict[str, Any]) -> None:
        """Append one event on a topic. Returns immediately; a consumer processes it later."""
        line = json.dumps({"topic": topic, "event": event})
        with self._lock, self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def _seen(self) -> set[str]:
        """Return the set of already-processed event keys."""
        if not self._seen_path.exists():
            return set()
        return set(self._seen_path.read_text(encoding="utf-8").split())

    def _mark(self, key: str) -> None:
        """Record an event key as processed."""
        with self._seen_path.open("a", encoding="utf-8") as handle:
            handle.write(key + "\n")

    def drain(self, topic: str, handler: Callable[[dict[str, Any]], None]) -> int:
        """Hand every not-yet-processed event on the topic to the handler, once. Returns the count.

        A redelivered or duplicate event (same id) is skipped, which is what keeps the
        consumer idempotent under at-least-once delivery. For a ledger this matters: a
        double-counted credit or debit would corrupt the balance.
        """
        if not self._path.exists():
            return 0
        seen = self._seen()
        handled = 0
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            message = json.loads(line)
            if message["topic"] != topic:
                continue
            key = f"{topic}:{message['event'].get('id')}"
            if key in seen:
                continue
            handler(message["event"])
            self._mark(key)
            seen.add(key)
            handled += 1
        return handled
