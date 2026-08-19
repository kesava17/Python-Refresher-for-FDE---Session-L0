# Assignment 01 · Make telemetry-insight scale (CPU-bound)

> Offline practice for Day 2. In class you made `reviews-insight` stream and enrich
> concurrently, where the enrichment was IO-bound. Now do the Day 2 layer on your Day 1
> `telemetry-insight` service, but with a twist: the heavy work here is CPU-bound, so the
> right tool is different.

This is a do-it-yourself assignment. The point is to feel, on your own machine, the
difference the workload type makes: streaming keeps memory flat regardless, but for the heavy
compute, threads do almost nothing (the GIL) and processes are what actually speed it up. You
will prove all of it with numbers.

Start from your Day 1 `telemetry-insight` project, green.

## The goal

Two things, both measured:

1. Summarize a large telemetry file by **streaming** it, so memory stays flat no matter how big
   the file gets.
2. Run a **CPU-bound transform** over the readings, once with a thread pool and once with a
   process pool, and show that the process pool is the one that actually parallelizes it.

By the end you have a short report (printed numbers are fine) that shows a flat streaming memory
profile and a serial-versus-threads-versus-processes benchmark, with a sentence explaining why
threads did not help.

## The data

Generate a large readings CSV yourself (a script like the lab's `make_big.py`, adapted to the
telemetry columns `device_id,ts,value`). Aim for one to two million rows across a few hundred
devices, so the memory and speed differences are visible.

## What you have to build

1. **A streaming summary.** A context-managed reader that yields one reading at a time, and a
   summary that folds the stream into counts (readings, distinct devices) in constant memory.
   The `with` must close the file even on error.
2. **A CPU-bound transform.** A function that does real computation per reading or per chunk.
   Make it genuinely CPU-heavy, not a `sleep`: for example, for each device compute a smoothed
   series or a rolling statistic over its values, or run a deliberately costly numeric function
   many times. The point is that the CPU is busy, not waiting.
3. **Three runs of the transform**, timed: serial, through a `ThreadPoolExecutor`, and through a
   `ProcessPoolExecutor`. Print all three times.
4. **A memory measurement** of the eager load versus the streaming summary, with `tracemalloc`.
5. **A one-line written explanation** in the output (or a comment) of why the thread pool did
   not beat serial but the process pool did.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: generate volume

Adapt the lab's generator to write `device_id,ts,value` rows. Confirm the file exists and has
the row count you expect.

Hint: keep the device count small (a few hundred) so the distinct-device set stays tiny, which
is what keeps the streaming summary flat.

### Level 2: stream and summarize in constant memory

Add a context-managed streaming reader and a `summarize_stream` that keeps only a counter and a
set of device ids. Run it against the big file.

Hint: this is the same shape as the live lab. The set holds distinct devices (hundreds), never
the rows (millions).

### Level 3: prove the memory is flat

With `tracemalloc`, measure the peak of the eager `load_records` path against the streaming
path on the big file. Print both peaks and the ratio.

Hint: `tracemalloc.start()`, run the eager path, read `get_traced_memory()`, `reset_peak()`, run
the streaming path, read again. The eager peak grows with the file; the streaming peak does not.

### Level 4: a genuinely CPU-bound transform

Write a transform that computes, not waits. A good option: group readings by device, then for
each device compute a rolling mean or an exponentially smoothed series over its values, or apply
a deliberately expensive per-value function. Make sure it is heavy enough to take a noticeable
amount of time over the whole dataset.

Hint: if you are not sure it is CPU-bound, ask whether a faster network would help. If not, it
is CPU-bound.

### Level 5: serial, threads, processes

Run the transform three ways and time each: a plain loop, a `ThreadPoolExecutor`, and a
`ProcessPoolExecutor`. Use chunks of readings as the unit of work so each task does real
computation.

Hint: the process pool must be able to pickle its input and output, so pass plain data (lists,
dicts, numbers), not open files or generators. Keep the per-task data modest so serialization
does not dominate.

### Level 6: read the result and explain it

You should see the thread pool roughly tie the serial run (sometimes slightly slower), and the
process pool beat both, up to the number of cores. Write the one-line reason in your output: the
transform is CPU-bound, and the GIL lets only one thread run Python at a time, so threads cannot
parallelize it, while separate processes each have their own GIL.

### Level 7: green gate and commit

Add a small test (the streaming summary matches the eager one on a tiny sample), run ruff and
mypy strict, and commit the Day 2 layer on top of your Day 1 telemetry project.

## Done when

- [ ] A streaming summary runs over a million-plus-row file without a memory spike.
- [ ] `tracemalloc` shows the streaming peak far below the eager peak.
- [ ] The CPU-bound transform runs serial, threaded, and process-parallel, with all three times
  printed.
- [ ] The process pool is clearly faster than serial; the thread pool is not.
- [ ] Your output states, in one line, why threads did not help but processes did.
- [ ] `pytest`, `ruff check`, and `mypy src` are all green, and the layer is committed.

When every box is ticked, you have shown the Day 2 point on CPU-bound work: streaming is always
right for memory, but for compute you must escape the GIL with processes. The worked solution is
in `solution-01.md` if you want to compare, but try first.
