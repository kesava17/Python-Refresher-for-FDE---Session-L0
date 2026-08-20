# Assignment 02 · Make transactions-insight maintainable, and prove the strategy swaps

> Offline practice for Day 3. You made `reviews-insight` maintainable in class, breaking it into
> a source seam, an injected service, one decorator, and a thin CLI. Now do the same Day 3 layer
> on your `transactions-insight` service, and add one more seam money code always needs: a
> swappable rule for how a transaction is categorized.

This is a do-it-yourself assignment. Day 3 is about being **maintainable**. Your Day 2
transactions service works, but it is tangled. The CLI knows where the file lives, the counting
logic sits next to the file reading, and the one decision that changes most often (how to bucket a
transaction) is nowhere you can swap it. You will pull those apart into clean layers, and you will
prove two seams with tests: the source can change with no logic change, and the categorization
rule can change while the ledger total stays identical.

Start from your `transactions-insight` project, green, with its `Transaction` model (frozen, money
in paise) and `AccountLedger` in place.

## The goal

1. Introduce a **data-source seam**: a `TransactionSource` Protocol with a CSV implementation and
   an in-memory one, so the service depends on a shape rather than a concrete file reader.
2. Introduce a **categorization seam**: a `CategoryStrategy` Protocol with two strategies, so the
   rule that labels a transaction can be swapped without touching the logic around it.
3. Move the summary logic into a **service with both its source and its strategy injected**: the
   counting lives in one place, and the service is handed its parts from outside.
4. Add **one decorator** for a cross-cutting concern (timing), applied by name, without touching
   the logic it wraps.
5. Make the **CLI a thin composition root**: build the CSV source, pick a default strategy, wire
   them into the service, print.
6. **Prove both seams** with tests: swap the source and get the same summary, then swap the
   strategy and watch the category breakdown change while the ledger total holds.

By the end you have a maintainable service built from parts that each do one thing, and two
tests that prove the seams hold.

## The starting point

You already have the `Transaction` model (frozen, money in paise), a `parse_transaction` that turns
a row into a `Transaction`, and an `AccountLedger` whose total is provably the sum of every amount
applied. Reuse all of it unchanged. Day 3 rearranges everything around these pieces into clean
seams.

Reuse your `transactions-insight` sample CSV (`account_id,ts,amount,currency`) with its five INR
rows across three accounts. The summary target stays exactly the same: `transactions: 5`,
`accounts    : 3`.

## What you have to build

1. **A `TransactionSource` Protocol, with two implementations.** A `Protocol` that names one
   method, `rows()`, yielding raw transaction rows one dictionary at a time. A `CsvTransactionSource`
   that streams from a CSV file on disk, and an `InMemoryTransactionSource` that hands back a list
   already in memory. Neither inherits from the Protocol; each satisfies it by shape.
2. **A `CategoryStrategy` Protocol, with two strategies.** A `Protocol` that names one method,
   `categorize(txn)`, returning a category label. A `BySizeStrategy` that labels each transaction
   `"large"` or `"small"` against a paise threshold (default 10000 paise, which is 100 rupees), and
   a `ByCurrencyStrategy` that labels by the currency code so each currency is its own bucket.
3. **A `LedgerService` with the source and the strategy injected.** It holds a `TransactionSource`
   and a `CategoryStrategy` handed in from outside. A `summarize()` method drives the source through
   the shared counting logic. A `categorize_all()` method applies each transaction to a fresh
   ledger and tallies the categories the strategy produces, and it remembers the ledger total so a
   caller can read it back.
4. **One `timed` decorator.** A single decorator for a cross-cutting concern, applied by name to
   `summarize()`, with typing that preserves the wrapped signature so mypy stays clean.
5. **A thin CLI composition root.** The CLI reads config, builds a `CsvTransactionSource` and a
   default `BySizeStrategy`, injects them into a `LedgerService`, runs it, and prints. All the real
   logic lives in the service.
6. **The two seam tests (the deliverable).** A source-swap test: the same data from a CSV file and
   from an in-memory list reach the service and give the same summary. A strategy-swap test: over
   the same transactions, `BySizeStrategy` gives `{"large": 2, "small": 3}` and `ByCurrencyStrategy`
   gives `{"INR": 5}`, while the ledger total is identical either way.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the source seam

Create `sources.py`. Write a `TransactionSource` Protocol with a single `rows()` method returning
`Iterator[dict[str, str]]`. Write `CsvTransactionSource(path)` that streams rows through your Day 2
`open_records` context manager, and `InMemoryTransactionSource(rows)` that stores a list and returns
`iter(...)` over it.

Hint: yield from inside the `with` in the CSV source, so the file stays open only while it is being
read. The in-memory source copies its input with `list(rows)` so a later change to the caller's list
cannot leak in.

### Level 2: the categorization seam

Create `strategies.py`. Write a `CategoryStrategy` Protocol with one method, `categorize(txn)`,
returning a `str`. Write `BySizeStrategy` with a threshold in paise (default 10000) that returns
`"large"` at or above the threshold and `"small"` below it, and `ByCurrencyStrategy` that returns
`txn.currency`.

Hint: keep the threshold a constructor argument with a module-level default, so a test can pass its
own threshold while production uses 10000 paise (100 rupees). The size check is one comparison;
resist adding an `if` per currency, that is exactly the branching the strategy seam removes.

### Level 3: the service with two seams injected

Create `service.py`. Move the counting logic into a module-level `summarize_rows(rows)` that
parses each row and counts transactions and distinct accounts. Write a
`LedgerService(source, strategy)` that stores both. Give it a `summarize()` that drives
`self._source.rows()` through `summarize_rows`, and a `categorize_all()` that applies each
transaction to a fresh `AccountLedger`, tallies `self._strategy.categorize(txn)` into a counts dict,
and stashes `ledger.total()` for a `last_total()` reader.

Hint: the service depends only on the two contracts, never on a file or a concrete rule.
`categorize_all` applies every transaction to the ledger and tallies the strategy's label, so the
total is the sum of all amounts.

### Level 4: one decorator, used sparingly

Create `decorators.py`. Write a `timed(label)` decorator that prints how long the wrapped call took,
using `time.perf_counter()` in a `try/finally` so the timing prints even on failure. Type it with
`ParamSpec` and `TypeVar` so the wrapped signature is preserved. Apply `@timed("summary")` to
`summarize()`.

Hint: this is **one** decorator, for a concern (timing) that genuinely cuts across methods. A stack
of decorators hides the real work; one, applied where it is genuinely needed, keeps the power without the
clutter.

### Level 5: the thin CLI

Rewrite `cli.py` as a composition root. In `main`, read the config, build a `CsvTransactionSource`
from the data path, build a default `BySizeStrategy`, inject both into a `LedgerService`, call
`summarize()`, and print the counts.

Hint: the CLI is the seam between the outside world and your code, and the riskiest place to hold
logic. The less it carries, the less can break when the entry point changes.

### Level 6: the two seam tests (the deliverable)

This is the proof. In `tests/test_service.py`, define one shared list of rows (five INR rows) and a
matching CSV text. Write a source-swap test that feeds the same data
from a temp CSV file and from the in-memory list and asserts both summaries equal
`{"transactions": 5, "accounts": 3}`. Write a strategy-swap test that runs
`categorize_all()` once with `BySizeStrategy` and once with `ByCurrencyStrategy` over the same source
and asserts the two breakdowns differ while `last_total()` matches.

Hint: the size breakdown is `{"large": 2, "small": 3}` and the currency breakdown is `{"INR": 5}`.
The ledger total is a property of the transactions, not of how you labelled them, so it is the same
56125 paise either way. That equality under a swapped rule is the whole point.

### Level 7: green gate and commit

Run ruff and mypy strict, make the seam tests and the carried tests pass, confirm the summary
output is unchanged, and commit the Day 3 layer on top of your Day 2 transactions project.

## Done when

- [ ] `TransactionSource` is a Protocol; a CSV source and an in-memory source both satisfy it by
  shape, with no base class.
- [ ] `CategoryStrategy` is a Protocol; `BySizeStrategy` labels `"large"`/`"small"` at a 10000-paise
  threshold and `ByCurrencyStrategy` labels by currency code.
- [ ] `LedgerService` is handed both its source and its strategy from outside and never builds
  either one itself.
- [ ] One `timed` decorator carries the timing, applied by name, with mypy still clean.
- [ ] The CLI is a thin composition root: build the parts, inject, print.
- [ ] The source-swap test proves the same data from a file and from memory gives the same summary.
- [ ] The strategy-swap test proves `BySizeStrategy` gives `{"large": 2, "small": 3}` and
  `ByCurrencyStrategy` gives `{"INR": 5}` over the same transactions, with the ledger total
  identical (56125 paise) either way.
- [ ] `transactions summary` still prints `transactions: 5`, `accounts    : 3`.
- [ ] `pytest`, `ruff check`, and `mypy src` are all green, and the layer is committed.

When every box is ticked, you have built the maintainable layer: the same service, now
assembled from parts that each do one thing, with two seams proven by tests. The worked solution is
in `solution-02.md` if you want to compare, but try first.
