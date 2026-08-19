# Day 2 Setup and Run Cheatsheet

Everything you need to get the Day 2 code running, on one page. The good news first: **Day 2 adds
no new software.** Every piece of Day 2 code runs on the toolchain you set up on Day 1 (Poetry,
Python 3.11 or newer, and on Windows, WSL). All the new code uses only the Python standard library
(`concurrent.futures`, `asyncio`, `threading`, `multiprocessing`, `tracemalloc`, `csv`,
`contextlib`) plus `python-dotenv`, which Poetry installs for you. Nothing else to download.

This page covers how to run the three Day 2 samples: the **concept demos**, the **live-lab**
(`reviews-insight`), and the two **assignments**. As always in this course, run everything through
`poetry run`.

---

## 0. Prerequisites (already done on Day 1)

Confirm the Day 1 toolchain is in place. If any of these is missing, go back to the Day 1 setup
cheatsheet first.

```bash
python3 -V          # Python 3.11 or newer
poetry --version    # Poetry 2.x
git version
```

- On Windows, do all of this **inside WSL** (the Ubuntu terminal), as set up on Day 1.
- **Docker is not needed for Day 2.** The Postgres stub from Day 1 is only used on a later day, so
  you do not have to start it now.
- **Additional software for Day 2: none.** It is all standard library plus Poetry.

---

## 1. The concept demos: run and execute them

Small, one-idea scripts you run while reading the lesson, at each **Try it** note. They live in the
Day 2 workspace's `demos/` folder, which is its own tiny Poetry project. Each script is heavily
commented, so open the file as you run it.

**Set up once**, from inside the `demos/` folder:

```bash
cd demos
poetry install
```

**Then run any demo** with `poetry run python <name>.py`. A plain `python <name>.py` also works,
since they use only the standard library. Here are all nine, in lesson order, with what to expect:

```bash
poetry run python demo_gil_cpu.py             # threads about the same as serial; processes faster
poetry run python demo_io_threads.py          # concurrent finishes far sooner than serial
poetry run python demo_thread_race.py         # unsafe count comes up short; the locked one is exact
poetry run python demo_async.py               # gathered concurrently far faster than one by one
poetry run python demo_async_blocking_trap.py # the blocking version is far slower: it froze the loop
poetry run python demo_timeout_retry.py       # times out and gives up in about 1s, does not hang
poetry run python demo_memory_stream.py       # eager list peak is large; generator peak near zero
poetry run python demo_generator_expr.py      # the generator is tiny and single-use (2nd pass is 0)
poetry run python demo_context_manager.py     # "closed" prints even when the block raises
```

To run them all in one go:

```bash
for f in demo_*.py; do echo "== $f =="; poetry run python "$f"; done
```

Times and sizes vary with your machine and core count; the pattern is the point, not the exact
number. `demos/README.md` has the same list in a table.

---

## 2. The live-lab: `reviews-insight`

This is the running application you make performant on Day 2 (streaming plus concurrent
enrichment). If you built it during the live lab you are already inside the `reviews-insight`
folder; if you are using the provided project, `cd` into it first.

```bash
poetry install                                   # set up the environment
poetry run reviews summary                       # runs on the small sample CSV

# generate a large file once, then prove the two results:
poetry run python scripts/make_big.py 2000000    # writes data/reviews_big.csv (~2M rows)
poetry run python scripts/measure_memory.py      # proof 1: streaming peak far below eager
poetry run python scripts/benchmark_enrich.py    # proof 2: concurrent far faster than serial

# run the summary over the big file (streaming, constant memory):
DATA_PATH=data/reviews_big.csv poetry run reviews summary
```

Run the quality gate the same way as Day 1:

```bash
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

The generated `data/reviews_big.csv` can be large and is git-ignored; delete it when you are done.

---

## 3. The offline assignments

Each is its own Poetry project. `cd` into it, `poetry install`, then run.

**Assignment 01, `telemetry-insight`** (streaming, and CPU-bound work across processes):

```bash
poetry run telemetry summary
poetry run python scripts/make_big.py 1000000       # writes data/telemetry_big.csv
poetry run python scripts/measure_memory.py         # streaming stays flat
poetry run python scripts/benchmark_transform.py    # serial vs threads vs processes
```

The process-pool benchmark shows its point best on a multi-core machine: threads roughly tie
serial (the GIL), processes are faster.

**Assignment 02, `transactions-insight`** (a safe concurrent fan-out that degrades gracefully):

```bash
poetry run transactions summary
poetry run pytest -q                                # the graceful-degradation test
poetry run python scripts/benchmark_enrich.py       # serial vs the safe concurrent fan-out
```

---

## 4. The commands you use everywhere (recap)

- `poetry install` sets up a project's own environment.
- `poetry run <cmd>` runs inside that environment. Never use a bare `python` for project code.
- `poetry run pytest -q`, `poetry run ruff check .`, `poetry run mypy src` are the quality gate.
- A big data file is generated on demand and git-ignored. Delete `data/*_big.csv` to reclaim disk.

---

## 5. Troubleshooting

- **`can't open file '...py:'`** You have a stray character (usually a `:`) on the end of the
  command. Retype it: `poetry run python demo_io_threads.py`, no trailing colon.
- **A process-pool script errors on Windows or macOS.** `ProcessPoolExecutor` needs the
  `if __name__ == "__main__":` guard; all the provided scripts have it. Run scripts by file
  (`poetry run python scripts/...`), do not paste the function into a REPL.
- **Threads do not speed up a CPU-heavy benchmark.** That is the expected result, not a bug: it is
  the GIL. Use the process version for CPU-bound work.
- **`poetry run` cannot find the command** (`reviews`, `telemetry`, `transactions`). Run
  `poetry install` in that project first; the command is defined under `[tool.poetry.scripts]`.

---

## 6. Readiness check

- [ ] `python3 -V` shows 3.11 or newer and `poetry --version` shows Poetry 2.x (from Day 1).
- [ ] In `demos/`, `poetry install` succeeds and `poetry run python demo_io_threads.py` prints a
  serial time and a much smaller concurrent time.
- [ ] The `reviews-insight` project runs `poetry run reviews summary`.
- [ ] You confirmed there is nothing new to install for Day 2: standard library plus Poetry.

If every line checks out, you can run every Day 2 sample and follow every **Try it** in the lesson.
