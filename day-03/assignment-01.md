# Assignment 01 · Make telemetry-insight maintainable

> Offline practice for Day 3. In class you took a working service apart along its seams: a
> source behind a small contract, the logic in a service that receives that source, a
> cross-cutting concern lifted into a decorator, and a CLI that only wires the pieces
> together. Now do the Day 3 layer on your `telemetry-insight` service: refactor it into
> clean, maintainable layers, mirroring the `reviews-insight` liveLab.

This is a do-it-yourself assignment. The point is to feel the difference a seam makes: once the
service depends on a `ReadingSource` contract instead of a file, you can swap the source for a
mock with no change to the logic, and the same code you ship is the code your test exercises.
Nothing about the behaviour changes. Everything about how easy it is to change and test does.

Start from your `telemetry-insight` project, green, with the Day 2 streaming service in place.

## The goal

One thing, done honestly: take the working-but-tangled service and separate its layers, so the
counting logic no longer knows where its rows come from. At the end, `telemetry summary` prints
exactly the same three numbers it did before, but now the service receives its data source from
outside, and a test can hand it in-memory rows instead of a file.

The behaviour is unchanged. The target output is still:

```text
readings: 5
devices : 3
```

## What you have to build

1. **A `ReadingSource` contract with two implementations.** A `Protocol` that describes a source
   by its shape: anything with a `rows()` method that yields telemetry rows counts as a
   `ReadingSource`, with no base class to inherit. Back it two ways: a `CsvReadingSource` that
   streams rows from a file on disk, and an `InMemoryReadingSource` that hands over a list already
   in memory.
2. **A `DeviceSummaryService` that receives its source.** Move the counting logic into a
   `summarize_rows` function, then a service class that holds a `ReadingSource` handed to it from
   outside (dependency injection) and drives it through that shared logic. The service must never
   decide where the data comes from.
3. **A `timed` decorator as a cross-cutting concern.** Lift timing into one decorator that prints
   how long a call took, and apply it to the service's `summarize` by name, without cluttering the
   logic it wraps.
4. **A CLI that is a thin composition root.** Have `main` read configuration, build the concrete
   `CsvReadingSource`, inject it into the service, run it, and print the result. No real logic
   should live in the CLI any more.
5. **A test that swaps the reader with no change to the service.** Feed the same data two ways,
   once from a CSV file and once from an in-memory list, and assert both give the identical
   result. This is the deliverable proof.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the source seam

Write `sources.py`. Define a `ReadingSource` `Protocol` with a single `rows()` method that returns
an `Iterator[dict[str, str]]`. Then write `CsvReadingSource`, which takes a path and yields rows by
streaming the file, and `InMemoryReadingSource`, which takes a sequence of rows and hands back an
iterator over them.

Hint: a `Protocol` is a structural contract. Neither source subclasses it; they simply have a
`rows()` method of the right shape, and that is enough. For the CSV source, reuse the streaming
context manager you already have and `yield from` it inside the `with` block, so the file stays
open only while it is being read.

### Level 2: the service that receives its source

Write `service.py`. Move your row-counting loop into a free function `summarize_rows(rows)` that
returns the three numbers. Then write `DeviceSummaryService`, whose `__init__` takes a
`ReadingSource` and stores it, and whose `summarize()` method just runs the stored source's
`rows()` through `summarize_rows`.

Hint: the service should type its parameter as `ReadingSource`, not as a concrete class. That one
choice is the whole seam: the service depends on the contract, so anything satisfying the contract
can be injected.

### Level 3: the cross-cutting concern

Write `decorators.py`. Define `timed(label)` that returns a decorator, which wraps a function so it
prints how long the call took, tagged with `label`. Apply it to the service's `summarize` method.

Hint: time the call around a `try`/`finally` so the elapsed time is reported whether the call
returns or raises. Use `functools.wraps` to keep the wrapped function's name and docstring, and
`ParamSpec` plus `TypeVar` in the signature so the wrapped function's type is preserved and mypy
still checks callers exactly as before.

### Level 4: the thin composition root

Rewrite `main` in the CLI as a composition root: read config, build a `CsvReadingSource` from the
data path, inject it into a `DeviceSummaryService`, call `summarize()`, and print the three lines
in the same order as before.

Hint: the CLI should read like a wiring diagram. If you can see the logic of counting in `main`,
it has not moved far enough. The only new code in `main` is building the source and the service and
asking for the result.

### Level 5: prove it by swapping the source

Write a test that builds the service twice over the same data: once with a `CsvReadingSource`
pointed at a small CSV file you write to a temporary path, and once with an `InMemoryReadingSource`
over the equivalent list. Assert that both `summarize()` calls return the identical result, and
that it matches the counts you expect. Add a second, simpler test that the in-memory source alone
gives the right counts, so the mock path stands on its own.

Hint: use pytest's `tmp_path` fixture to write the CSV file, so the test cleans up after itself.
The point of the assertion is that the service logic was never touched between the two runs; only
the injected source differed.

### Level 6: green gate and commit

Run pytest, ruff, and mypy strict, then commit the Day 3 maintainable refactor on top of your
telemetry project.

## Done when

- [ ] A `ReadingSource` `Protocol` exists, with a `CsvReadingSource` and an `InMemoryReadingSource`
  that both satisfy it without inheriting from it.
- [ ] `DeviceSummaryService` receives its source through its constructor and never decides where
  the data comes from; `summarize_rows` holds the counting logic in one place.
- [ ] A `timed` decorator adds timing to `summarize` without touching the counting logic, and mypy
  still checks callers as before.
- [ ] `main` is a thin composition root: it builds the source, injects it into the service, runs
  it, and prints the result.
- [ ] `telemetry summary` still prints `readings: 5`, `devices : 3`.
- [ ] A test swaps a CSV source for an in-memory source with no change to the service, and both
  give the same result.
- [ ] `pytest`, `ruff check`, and `mypy src` are all green, and the layer is committed.

When every box is ticked, you have shown the Day 3 point: separating a program along its seams
leaves the behaviour identical but makes the code easy to change and easy to test, because the
logic no longer depends on where its data lives. The worked solution is in `solution-01.md` if you
want to compare, but try first.
