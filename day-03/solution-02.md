# Solution 02 · Make transactions-insight maintainable, and prove the strategy swaps

> The full worked solution for Assignment 02. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your Day 2 `transactions-insight` project, green. This solution adds the Day 3
maintainable layer: a source seam so the service depends on a shape instead of a file, a
categorization seam so the labelling rule can be swapped, a service that is handed both its source
and its strategy, one decorator for timing, and a thin CLI composition root. The `Transaction`
model and `AccountLedger` are reused untouched. Use `poetry run` for everything.

## Step 1: the source seam

Right now the service knows it reads a CSV file, and that knowledge chains the logic to the file.
Break the chain by depending on a shape. Create `src/transactions_insight/sources.py`:

**`src/transactions_insight/sources.py`**

```python
"""The data-source seam (new on Day 3): a small Protocol, and two interchangeable sources.

A Protocol describes a contract by its shape: any object that has a `rows()` method
returning transaction rows counts as a TransactionSource, with no base class to inherit.
This is what lets the service depend on the contract, not on where the data actually
comes from.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol

from transactions_insight.data import open_records


class TransactionSource(Protocol):  # new this day: the source contract the service depends on
    """The contract the service depends on: something that can hand over transaction rows."""

    def rows(self) -> Iterator[dict[str, str]]:
        """Yield raw transaction rows, one dictionary at a time."""
        ...


class CsvTransactionSource:
    """A TransactionSource backed by a CSV file on disk. Used in the real application."""

    def __init__(self, path: str) -> None:
        self._path = path

    def rows(self) -> Iterator[dict[str, str]]:
        # open_records is a context manager that streams rows and always closes the file.
        # Yielding from inside the `with` keeps the file open only while it is being read.
        with open_records(self._path) as stream:
            yield from stream


class InMemoryTransactionSource:
    """A TransactionSource backed by a list already in memory. Ideal for tests: no file needed."""

    def __init__(self, rows: Sequence[dict[str, str]]) -> None:
        self._rows = list(rows)

    def rows(self) -> Iterator[dict[str, str]]:
        return iter(self._rows)
```

`TransactionSource` names one method, `rows()`, and nothing more. Neither `CsvTransactionSource`
nor `InMemoryTransactionSource` inherits from it, yet both satisfy it because each has a matching
`rows()`. That is structural typing: an object fits the contract by its shape, not its ancestry. The
CSV source streams from disk exactly as before; the in-memory source hands back a list. Anything
that depends on `TransactionSource` can use either without knowing which it holds.

## Step 2: the categorization seam

How a transaction is bucketed is a decision that changes often: today by size, tomorrow by currency.
Capture that one decision behind a small contract so the service can hold whichever rule it was
handed, with no `if` per variant. Create `src/transactions_insight/strategies.py`:

**`src/transactions_insight/strategies.py`**

```python
"""The categorization seam (new on Day 3): a Protocol, and two interchangeable strategies.

Categorizing a transaction is a decision that may change often: today by size, tomorrow by
currency, later by something else. A strategy captures that one decision behind a small
contract so the service can hold whichever rule it was handed, without an `if` for each
variant. This is the swappable part: a test can pass one strategy, production another, and
the surrounding logic never changes.
"""

from __future__ import annotations

from typing import Protocol

from transactions_insight.models import Transaction

# One rupee is 100 paise; 10000 paise is 100 rupees, our default "large" threshold.
_DEFAULT_LARGE_PAISE = 10000


class CategoryStrategy(Protocol):  # new this day: the swappable-rule contract
    """The contract the service depends on: turn one Transaction into a category label."""

    def categorize(self, txn: Transaction) -> str:
        """Return the category label this transaction belongs to."""
        ...


class BySizeStrategy:  # new this day: one interchangeable rule
    """Categorize by amount: 'large' at or above the threshold, 'small' below it."""

    def __init__(self, threshold_paise: int = _DEFAULT_LARGE_PAISE) -> None:
        self._threshold_paise = threshold_paise

    def categorize(self, txn: Transaction) -> str:
        return "large" if txn.amount_paise >= self._threshold_paise else "small"


class ByCurrencyStrategy:  # new this day: a second rule, swapped in without touching the service
    """Categorize by currency code, so each currency becomes its own bucket."""

    def categorize(self, txn: Transaction) -> str:
        return txn.currency
```

`CategoryStrategy` is a Protocol just like the source: one method, `categorize`, and no base class.
`BySizeStrategy` compares the amount in paise against a threshold that defaults to 10000 paise (100
rupees) but can be passed in, so a test can choose its own cutoff. `ByCurrencyStrategy` returns the
currency code straight, making each currency its own bucket. Both are single-decision objects, which
is exactly what makes them swappable: the service holds one of them and never knows or cares which.

## Step 3: the service with both seams injected

The counting logic should not care where rows come from nor how they are bucketed, and it should
live in one place. Create `src/transactions_insight/service.py`:

**`src/transactions_insight/service.py`**

```python
"""The service layer, new on Day 3: the summary logic, with its store and strategy injected.

New this day: the counting logic moves into one place (`summarize_rows`), and `LedgerService`
receives a `TransactionSource` and a `CategoryStrategy` from outside (dependency injection)
instead of building them. Those two seams let a test feed in-memory rows and swap the strategy
while the logic stays unchanged.
"""

from __future__ import annotations

from collections.abc import Iterator

from transactions_insight.decorators import timed
from transactions_insight.models import AccountLedger, parse_transaction
from transactions_insight.sources import TransactionSource
from transactions_insight.strategies import CategoryStrategy


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count transactions and distinct accounts from a stream of rows."""
    transactions = 0
    accounts: set[str] = set()
    for row in rows:
        txn = parse_transaction(row)
        transactions += 1
        accounts.add(txn.account_id)
    return {"transactions": transactions, "accounts": len(accounts)}


class LedgerService:  # new this day: the source and strategy are injected, not built here
    """Summarizes and categorizes transactions from any source, using an injected strategy.

    Both the source and the strategy are injected, not built here. The service depends on the
    two contracts only, so swapping either one needs no change to the logic below.
    """

    def __init__(self, source: TransactionSource, strategy: CategoryStrategy) -> None:
        self._source = source
        self._strategy = strategy
        self._last_total = 0  # paise applied by the most recent categorize_all call

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())

    def categorize_all(self) -> dict[str, int]:
        """Apply each transaction to a fresh ledger and count categories via the strategy."""
        ledger = AccountLedger()
        counts: dict[str, int] = {}
        for row in self._source.rows():
            txn = parse_transaction(row)
            ledger.apply(txn)
            # The strategy is the only thing that decides the bucket; the loop stays the same.
            label = self._strategy.categorize(txn)
            counts[label] = counts.get(label, 0) + 1
        # The ledger total is a by-product available to callers that need the invariant.
        self._last_total = ledger.total()
        return counts

    def last_total(self) -> int:
        """Return the ledger total from the most recent categorize_all call, in paise."""
        return self._last_total
```

Where each maintainable habit lives:

- **One home for the logic:** `summarize_rows` holds the counting, once, with no knowledge of
  files or strategies. Both the CLI and the service call it.
- **Two seams, both injected:** `LedgerService.__init__` takes a `TransactionSource` and a
  `CategoryStrategy` and stores them. It depends on the two contracts only, so swapping either needs
  no change to the logic below. That is dependency injection.
- **The strategy is the only branch point:** in `categorize_all`, the loop is fixed; the one line
  that decides a bucket is `self._strategy.categorize(txn)`. Change the strategy and the breakdown
  changes with the loop untouched.
- **The total is a by-product:** `categorize_all` applies each transaction to a fresh ledger
  and stashes `ledger.total()`, so `last_total()` can hand back the invariant regardless of how the
  transactions were labelled.

## Step 4: one decorator, used sparingly

Timing is a concern many methods share but none should be cluttered with. Put it in one place and
apply it by name. Create `src/transactions_insight/decorators.py`:

**`src/transactions_insight/decorators.py`**

```python
"""A single decorator for a cross-cutting concern (new on Day 3): timing, used sparingly.

Timing is a concern that many methods share but none of them should be cluttered with. A
decorator lets us add it in one place and apply it by name, without editing the logic it
wraps. The typing (ParamSpec plus TypeVar) preserves the wrapped function's signature, so
mypy still checks callers exactly as before.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(label: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that prints how long the wrapped call took, labelled by `label`."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)  # keep the wrapped function's name and docstring
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                # `finally` runs whether the call returned or raised, so the timing is
                # always reported, even on failure.
                elapsed_ms = (time.perf_counter() - start) * 1000
                print(f"[timed] {label}: {elapsed_ms:.1f} ms")

        return wrapper

    return decorator
```

`@timed("summary")` on the service turns timing on by name without a single edit to the counting
logic. Note that this is one decorator, for a concern that genuinely cuts across methods.
A stack of them hides the real work behind layers of wrapping; one, applied where it is genuinely needed,
keeps the power without the clutter. The `ParamSpec` and `TypeVar` typing preserves the wrapped
signature, so mypy still checks callers of `summarize` exactly as before.

## Step 5: the thin CLI composition root

With the logic in the service and both seams behind contracts, the CLI has almost nothing left to
do: read config, assemble the concrete pieces, print. Rewrite `src/transactions_insight/cli.py`:

**`src/transactions_insight/cli.py`**

```python
"""Command line entry point (new on Day 3: a thin composition root).

The CLI's only jobs now are to read configuration, build the concrete pieces (a CSV source,
a default strategy, and the service that uses them), wire them together, and print the
result. All the real logic lives in the service, so this surface stays small and easy to read.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from transactions_insight.config import Config
from transactions_insight.service import LedgerService
from transactions_insight.sources import CsvTransactionSource
from transactions_insight.strategies import BySizeStrategy


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    transactions = 0
    accounts: set[str] = set()
    for record in records:
        transactions += 1
        accounts.add(record["account_id"])
    return {"transactions": transactions, "accounts": len(accounts)}


def main() -> None:
    parser = argparse.ArgumentParser(description="transactions-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    parser.parse_args()

    config = Config.from_env()

    # Composition root: build the concrete source and strategy, inject them, run the service.
    source = CsvTransactionSource(config.data_path)
    strategy = BySizeStrategy()
    service = LedgerService(source, strategy)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"transactions: {result['transactions']}")
    print(f"accounts    : {result['accounts']}")


if __name__ == "__main__":
    main()
```

`main` now does four small things: read the config, build a `CsvTransactionSource`, pick a default
`BySizeStrategy`, and inject both into a `LedgerService` before printing. That is a composition root:
the one place that decides which concrete pieces to assemble. The surface stays small
on purpose, because the CLI is the seam between the outside world and the code, and the less logic it
carries, the less can break when the entry point changes.

Run the summary:

```bash
poetry run transactions summary
```

The timing line prints, and the counts are the same as before: five transactions across three
accounts.

```text
[timed] summary: 0.3 ms
[dev] transactions-insight
transactions: 5
accounts    : 3
```

## Step 6: the two seam tests (the deliverable proof)

This is the proof. One file exercises both seams. First the source: a CSV file and an in-memory list
reach the same service and produce the same summary. Then the strategy, the deliverable proof: the
same transactions, categorized two ways, yield different breakdowns while the ledger total stays
identical, because only the labelling changed.

**`tests/test_service.py`**

```python
"""Day 3 proof: the service works with any source, and the strategy is swappable.

Two seams are exercised here. First, the data source: a CSV file and an in-memory list reach
the same service and produce the same summary. Second, the categorization strategy: the same
transactions, categorized two different ways, yield different breakdowns while the ledger
total stays identical, because only the labelling changed.
"""

from __future__ import annotations

from pathlib import Path

from transactions_insight.service import LedgerService
from transactions_insight.sources import (
    CsvTransactionSource,
    InMemoryTransactionSource,
)
from transactions_insight.strategies import ByCurrencyStrategy, BySizeStrategy

# Five valid INR rows over three accounts, mirroring the shape of the sample file.
ROWS = [
    {"account_id": "A1", "amount": "120.50", "currency": "INR"},  # 12050 paise: large
    {"account_id": "A1", "amount": "80.00", "currency": "INR"},  # 8000 paise: small
    {"account_id": "A2", "amount": "15.00", "currency": "INR"},  # 1500 paise: small
    {"account_id": "A2", "amount": "300.00", "currency": "INR"},  # 30000 paise: large
    {"account_id": "A3", "amount": "45.75", "currency": "INR"},  # 4575 paise: small
]
CSV_TEXT = (
    "account_id,ts,amount,currency\n"
    "A1,2026-01-01T09:15:00,120.50,INR\n"
    "A1,2026-01-01T11:02:00,80.00,INR\n"
    "A2,2026-01-01T12:40:00,15.00,INR\n"
    "A2,2026-01-01T18:20:00,300.00,INR\n"
    "A3,2026-01-01T20:05:00,45.75,INR\n"
)
EXPECTED_SUMMARY = {"transactions": 5, "accounts": 3}


def test_service_with_in_memory_source() -> None:
    # No file, no disk: the in-memory source satisfies the same TransactionSource contract.
    service = LedgerService(InMemoryTransactionSource(ROWS), BySizeStrategy())
    assert service.summarize() == EXPECTED_SUMMARY


def test_swapping_source_keeps_the_same_result(tmp_path: Path) -> None:
    # The same data reaches the service two ways: from a CSV file, and from memory.
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    from_file = LedgerService(CsvTransactionSource(str(sample)), BySizeStrategy()).summarize()
    from_memory = LedgerService(InMemoryTransactionSource(ROWS), BySizeStrategy()).summarize()

    # The seam works: the service logic was untouched; only the injected source differed.
    assert from_file == from_memory == EXPECTED_SUMMARY


def test_swapping_strategy_changes_breakdown_not_the_total() -> None:
    # Same source, same transactions; only the injected strategy differs between the two runs.
    source = InMemoryTransactionSource(ROWS)

    by_size = LedgerService(source, BySizeStrategy())
    by_currency = LedgerService(source, ByCurrencyStrategy())

    size_breakdown = by_size.categorize_all()
    currency_breakdown = by_currency.categorize_all()

    # The breakdowns differ: size splits large from small, currency buckets by code.
    assert size_breakdown == {"large": 2, "small": 3}
    assert currency_breakdown == {"INR": 5}
    assert size_breakdown != currency_breakdown

    # The ledger total is a property of the transactions, not of how we labelled them, so it
    # is identical no matter which strategy was injected.
    expected_total = 12050 + 8000 + 1500 + 30000 + 4575
    assert by_size.last_total() == by_currency.last_total() == expected_total
```

What `test_swapping_strategy_changes_breakdown_not_the_total` proves, and why it is the deliverable:

- **The breakdown follows the rule:** `BySizeStrategy` splits the five transactions into
  `{"large": 2, "small": 3}` (the 12050 and 30000 paise rows clear the 10000-paise threshold; the
  8000, 1500, and 4575 paise rows fall under it), while `ByCurrencyStrategy` buckets all five as
  `{"INR": 5}`. Same transactions, different labels, because only the injected strategy changed.
- **The total does not:** `last_total()` is `12050 + 8000 + 1500 + 30000 + 4575`, which is 56125
  paise, identical under both strategies. The ledger total is a property of the money applied, not of
  how it was labelled, so swapping the rule cannot move it. That equality under a swapped rule is the
  proof the seam is clean.

The source-swap test fences the other seam in: the same data from a real CSV file on disk and from an
in-memory list reaches the service and gives the identical summary, with the service code untouched
between the two runs.

## Step 7: the carried model tests

Keep your `Transaction` model tests exactly as they were. They still pass unchanged, because Day 3
only rearranged the code around the model and the ledger, it did not alter them.

**`tests/test_models.py`**

```python
"""Tests for the Day 3 value object and the account ledger."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from transactions_insight.models import AccountLedger, Transaction, parse_transaction


def test_transaction_is_frozen() -> None:
    txn = Transaction(account_id="A1", amount_paise=100, currency="INR")
    with pytest.raises(FrozenInstanceError):
        txn.amount_paise = 200  # type: ignore[misc]  # frozen: cannot reassign


def test_transactions_compare_by_value() -> None:
    assert Transaction("A1", 100, "INR") == Transaction("A1", 100, "INR")
    assert Transaction("A1", 100, "INR") != Transaction("A1", 200, "INR")


def test_parse_builds_a_transaction() -> None:
    row = {"account_id": "A1", "amount": "120.50", "currency": "INR"}
    assert parse_transaction(row) == Transaction("A1", 12050, "INR")


def test_ledger_total_equals_sum_of_applied() -> None:
    ledger = AccountLedger()
    txns = [
        Transaction("A1", 100, "INR"),
        Transaction("A1", 250, "INR"),
        Transaction("A2", 500, "INR"),
    ]
    for txn in txns:
        ledger.apply(txn)
    # The invariant: the ledger total is exactly the sum of every amount applied.
    assert ledger.total() == sum(txn.amount_paise for txn in txns)
    assert ledger.balance("A1") == 350
    assert ledger.balance("A2") == 500
```

That the model tests pass with no edit is itself a small proof of the refactor: the model and the
ledger kept working while everything around them moved into seams.

## Step 8: green gate and commit

```bash
poetry run pytest -q          # 9 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "day 3: source seam, swappable strategy, injected service, one decorator, thin CLI"
```

## Done when

- `TransactionSource` is a Protocol; a CSV source and an in-memory source both satisfy it by shape,
  with no base class.
- `CategoryStrategy` is a Protocol; `BySizeStrategy` labels `"large"`/`"small"` at a 10000-paise
  threshold and `ByCurrencyStrategy` labels by currency code.
- `LedgerService` is handed both its source and its strategy from outside and never builds either.
- One `timed` decorator carries the timing, applied by name, with mypy still clean.
- The CLI is a thin composition root: build the parts, inject, print.
- The source-swap test proves the same data from a file and from memory gives the same summary.
- The strategy-swap test proves `BySizeStrategy` gives `{"large": 2, "small": 3}` and
  `ByCurrencyStrategy` gives `{"INR": 5}` over the same transactions, with the ledger total identical
  (56125 paise) either way.
- `transactions summary` still prints `transactions: 5`, `accounts    : 3`.
- `pytest`, `ruff`, and `mypy` are all green, and the layer is committed.

You have built the maintainable layer: the same service, now assembled from parts that each
do one thing. The source sits behind a Protocol, the categorization rule sits behind another, the
logic sits in a service handed both of them, one decorator carries the timing, and the CLI just wires
the pieces together. The two seam tests prove it: the source swaps with no logic change, and the
strategy swaps while the ledger total holds to the paisa.
