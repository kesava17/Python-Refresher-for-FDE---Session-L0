# Assignment 02 · Fan out transaction lookups, and degrade gracefully

> Offline practice for Day 2. You made `reviews-insight` enrich concurrently in class. Now do
> the Day 2 layer on your Day 1 `transactions-insight` service, with the focus on the part that
> matters most in production: staying safe and bounded when a dependency is slow.

This is a do-it-yourself assignment. The enrichment here is IO-bound (an external lookup per
transaction), so concurrency helps, but the real lesson is safety: a **concurrency cap**, a
**rate limit**, and a **timeout**, so that when the dependency slows to a crawl your service
degrades gracefully instead of piling up unbounded work or hanging forever. You will prove the
graceful degradation with a test.

Start from your Day 1 `transactions-insight` project, green.

## The goal

1. Enrich each transaction with a **lookup** from a simulated external service (for example a
   merchant-risk or category lookup), fanned out concurrently.
2. Make the fan-out **safe**: a cap on how many lookups run at once, a rate limit, and a timeout
   on every call.
3. Prove **graceful degradation**: when the dependency is made slow, the run still completes in
   bounded time, never exceeds the cap, and never hangs. A test demonstrates this.

By the end you have a concurrent enrichment that behaves well under a healthy dependency and,
more importantly, still behaves under a sick one.

## The data

Reuse or generate a transactions CSV (`account_id,ts,amount,currency` or similar). A few
thousand rows is plenty; this assignment is about the behavior of the fan-out, not raw volume.

## What you have to build

1. **A simulated external lookup** with controllable latency. A function `lookup(txn)` that
   sleeps for a configurable delay (stand-in for a network call) and returns a small result. You
   must be able to make it slow on demand, to simulate a struggling dependency.
2. **A safe concurrent enricher.** Fan the lookups out with:
   - a **concurrency cap** (at most N in flight), so you never flood the dependency,
   - a **rate limit** (at most R calls started per second), and
   - a **timeout** on each call, so a hung lookup is abandoned, not waited on forever.
3. **A serial baseline**, so you can show the concurrent version is faster on a healthy
   dependency.
4. **A degradation test.** With the dependency made slow, assert that the run: completes within
   a bounded time (thanks to timeouts), never had more than the cap in flight, and returns a
   result for every transaction (a real value or a clean "unavailable" fallback for the ones
   that timed out).

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the controllable dependency

Write `lookup(txn, delay)` that sleeps `delay` seconds and returns a small dict. Being able to
dial `delay` up is what lets you simulate a slow dependency later.

Hint: keep the return value tiny and picklable. The delay is the whole knob.

### Level 2: concurrent fan-out with a cap

Enrich all transactions through a `ThreadPoolExecutor` with `max_workers` set to your cap. The
work is IO-bound (it sleeps), so threads overlap the waits.

Hint: `max_workers` is your concurrency cap. Collect results by returning them from the worker,
not by mutating a shared list from inside it.

### Level 3: add a timeout on every call

Wrap each call so it cannot wait longer than a timeout. On timeout, return a clean fallback
(for example `{"risk": "unavailable"}`) rather than raising, so one slow lookup does not sink the
batch.

Hint: `future.result(timeout=...)` raises `TimeoutError`; catch it and substitute the fallback.
Decide your policy on purpose: fallback, or a bounded retry then fallback.

### Level 4: add a rate limit

Cap the rate at which new calls start (say R per second), independent of the concurrency cap.
This protects a dependency that cares about requests-per-second, not just simultaneous
connections.

Hint: a simple token or a small sleep between submissions works for the assignment. The point is
that you can name and control the rate, not that it is production-grade.

### Level 5: the healthy-dependency benchmark

With a small delay (a fast dependency), time serial versus your safe concurrent enricher. The
concurrent version should win clearly.

Hint: same benchmark shape as the live lab: `time.perf_counter()` around each run.

### Level 6: the degradation test

This is the deliverable. Set the dependency slow (a delay well above your timeout). Assert that:

- the whole run finishes within a bounded wall-clock time (timeouts kick in, so it does not hang),
- the number of concurrent calls never exceeded your cap (instrument a counter),
- every transaction has a result: a real one, or the clean "unavailable" fallback.

Hint: to check the cap, increment a shared counter on entry and decrement on exit, guarded by a
lock, and record the maximum seen. Assert the maximum is at most your cap. This is the proof that
the fan-out stays bounded under stress.

### Level 7: green gate and commit

Run ruff and mypy strict, make the degradation test pass, and commit the Day 2 layer on top of
your Day 1 transactions project.

## Done when

- [ ] Concurrent enrichment beats serial on a healthy (fast) dependency, timed.
- [ ] Every external call has a timeout and returns a clean fallback when it fires.
- [ ] Concurrency never exceeds your cap (a test asserts the observed maximum).
- [ ] With the dependency made slow, the run still completes in bounded time and returns a
  result for every transaction.
- [ ] `pytest`, `ruff check`, and `mypy src` are all green, and the layer is committed.

When every box is ticked, you have built the part that keeps a service alive in production: a
fan-out that is fast when the dependency is healthy and stays bounded and responsive when it is
not. The worked solution is in `solution-02.md` if you want to compare, but try first.
