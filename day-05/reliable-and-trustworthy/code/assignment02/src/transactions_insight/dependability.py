"""The dependability layer (Assignment 2): no data loss and an exactly-once effect.

Financial transactions are correctness- and audit-critical records, so the reliability goal for
this domain is narrow and strict: never lose a write, and never apply the same write twice. A
retry that quietly double-records a payment is a real defect, not a cosmetic one. This module
holds the small, testable pieces that deliver that guarantee (an all-or-nothing append and an
idempotency-keyed store), plus the operational surface an on-call engineer needs to trust the
service: a readiness signal, structured leveled logs, and simple SLI metrics.

Everything here uses only the standard library, so a learner can read each piece end to end.
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# --- All-or-nothing writes (crash-in-the-middle safety) -----------------------------


def atomic_append(
    rows: list[dict[str, str]],
    record: dict[str, str],
    on_prepared: Callable[[], None] | None = None,
) -> None:
    """Append one record so an interruption leaves the store with all of it or none of it.

    The write has two phases. The prepare phase builds a complete, private copy of the record
    and touches nothing that a reader can see. The commit phase is a single list.append, which
    is one atomic step in CPython, so a reader ever sees either no record or the whole record,
    never a half-written one and never two.

    The on_prepared hook sits between the two phases. A test passes a function that raises there
    to simulate a crash in the middle of the write. Because the commit has not run yet, the
    exception propagates and the store is left exactly as it was.
    """
    staged = dict(record)  # prepare: a complete copy, not yet visible in the store
    if on_prepared is not None:
        on_prepared()  # a test raises here to simulate an interruption before the commit
    rows.append(staged)  # commit: one atomic step, so the record is whole or absent


# --- Exactly-once effect via idempotency keys ---------------------------------------


class TransactionStore:
    """An in-memory transaction store with exactly-once writes keyed by an idempotency key.

    Submitting the same idempotency key twice (a retry, including one caused by a response that
    was lost on the way back to the client) records exactly one transaction and returns the
    first stored result. That is the core promise of the transactions domain: a retry must never
    double-record a payment.
    """

    def __init__(self) -> None:
        self._rows: list[dict[str, str]] = []
        self._by_key: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()

    def add(
        self,
        record: dict[str, str],
        key: str | None = None,
        on_prepared: Callable[[], None] | None = None,
    ) -> tuple[dict[str, str], bool]:
        """Store one record, or return the earlier one for a repeated key.

        Returns a pair (stored_record, created). created is True on the first write for a key and
        False on every replay, so the caller can keep its response identical across a retry. The
        lookup, the append, and the key registration all happen under one lock, so a concurrent
        retry cannot slip a second row in between.
        """
        with self._lock:
            if key is not None and key in self._by_key:
                # Idempotent replay: this key already recorded a transaction, so return the first
                # result and write nothing. This is what turns a retry into an exactly-once effect.
                return self._by_key[key], False
            atomic_append(self._rows, record, on_prepared)
            stored = self._rows[-1]
            if key is not None:
                self._by_key[key] = stored
            return stored, True

    def all(self) -> list[dict[str, str]]:
        """Return a copy of every stored row, so a caller cannot mutate the store by accident."""
        with self._lock:
            return list(self._rows)

    def __len__(self) -> int:
        with self._lock:
            return len(self._rows)


# --- Readiness (capacity), distinct from liveness -----------------------------------


class Capacity:
    """Tracks in-flight requests against a limit, so readiness can report saturation.

    Liveness (health) answers "is the process up". Readiness answers "can it take more work right
    now". When in-flight work reaches the limit, readiness reports not-ready (a 503) so a load
    balancer stops sending new requests until the service drains, instead of piling on and losing
    work.
    """

    def __init__(self, limit: int = 64) -> None:
        self.limit = limit
        self._in_flight = 0
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            self._in_flight += 1

    def release(self) -> None:
        with self._lock:
            self._in_flight -= 1

    def is_ready(self) -> bool:
        with self._lock:
            return self._in_flight <= self.limit


# --- Simple SLI metrics (hand-rolled, plain text) -----------------------------------


class Metrics:
    """A tiny SLI collector: a request count, an error count, and a duration summary.

    These are the three signals you look at first when a service misbehaves: how much traffic,
    how many failures, and how slow. We keep them by hand in plain integers and floats so there
    is no heavy metrics dependency to install or run.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.requests = 0
        self.errors = 0  # counts responses with a 5xx status (a server-side failure)
        self.total_duration_ms = 0.0
        self.max_duration_ms = 0.0

    def record(self, duration_ms: float, status: int) -> None:
        with self._lock:
            self.requests += 1
            if status >= 500:
                self.errors += 1
            self.total_duration_ms += duration_ms
            self.max_duration_ms = max(self.max_duration_ms, duration_ms)

    def render(self) -> str:
        """Render the metrics as plain text, one metric per line (a Prometheus-like shape)."""
        with self._lock:
            avg = self.total_duration_ms / self.requests if self.requests else 0.0
            lines = [
                "# SLI metrics for transactions-insight (plain text, no external dependency)",
                f"requests_total {self.requests}",
                f"errors_total {self.errors}",
                f"request_duration_ms_avg {avg:.3f}",
                f"request_duration_ms_max {self.max_duration_ms:.3f}",
            ]
        return "\n".join(lines) + "\n"


# --- Structured, leveled logging with the trace id ----------------------------------


def get_logger() -> logging.Logger:
    """Return the shared logger, configured once to emit each event as a raw line."""
    logger = logging.getLogger("transactions_insight")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))  # the message is already JSON
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    trace_id: str,
    duration_ms: float,
    status: int,
) -> None:
    """Emit one JSON line for one event, carrying the trace id that ties a request together.

    One structured line per event (not free-form text) is what lets a log tool filter by trace
    id, sum by event, or alert on status, without parsing prose.
    """
    line = json.dumps(
        {
            "event": event,
            "trace_id": trace_id,
            "duration_ms": round(duration_ms, 3),
            "status": status,
        }
    )
    logger.log(level, line)


# --- A ledger invariant, for property testing ---------------------------------------


@dataclass(frozen=True)
class LedgerEntry:
    """One posting against an account, in paise: a positive amount credits, a negative debits."""

    account_id: str
    amount_paise: int


def running_balance_ok(entries: Sequence[LedgerEntry]) -> bool:
    """The ledger invariant: applied in order, no account's running balance ever goes below zero.

    A financial ledger must hold this at every step, not only at the end, so a debit can never
    take an account overdrawn. The API enforces the matching real-world rule by accepting only
    positive amounts (amount gt 0), which is why the live store can never violate it. This helper
    states the invariant on its own so a property test can generate many sequences and check it.
    """
    balances: dict[str, int] = {}
    for entry in entries:
        new_balance = balances.get(entry.account_id, 0) + entry.amount_paise
        if new_balance < 0:
            return False  # this posting would overdraw the account, so the invariant is broken
        balances[entry.account_id] = new_balance
    return True
