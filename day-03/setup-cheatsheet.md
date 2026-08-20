# Day 3 Setup and Run Cheatsheet

Everything you need to get the Day 3 code running, on one page. The good news first: **Day 3 adds
no new software.** Every piece of Day 3 code runs on the toolchain you set up on Day 1 (Poetry,
Python 3.11 or newer, and on Windows, WSL). All the new code uses only the Python standard library
(`dataclasses`, `typing`, `functools`, `time`, `csv`) plus Poetry, which installs the tooling for
you. Nothing else to download.

This page covers how to run the three Day 3 samples: the **concept demos**, the **live-lab**
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
- **Docker is not needed for Day 3.** The Postgres stub from Day 1 is only used on a later day, so
  you do not have to start it now.
- **Additional software for Day 3: none.** It is all standard library plus Poetry.

---

## 1. The concept demos: run and execute them

Small, one-idea scripts you run while reading the lesson, at each **Try it** note. They live in the
Day 3 workspace's `demos/` folder, which is its own tiny Poetry project. Each script is heavily
commented, so open the file as you run it.

**Set up once**, from inside the `demos/` folder:

```bash
cd demos
poetry install
```

**Then run any demo** with `poetry run python <name>.py`. A plain `python <name>.py` also works,
since they use only the standard library. Here are all seven, in lesson order, with what to expect:

```bash
poetry run python demo_class_vs_function.py    # a one-method class and a function give the same answer; a class is the right choice for shared state
poetry run python demo_dataclass.py            # a dataclass matches a hand-written class with far less code; a frozen one cannot be changed
poetry run python demo_dict_vs_dataclass.py    # a dict typo is a runtime KeyError or silent junk; a dataclass has one explicit shape
poetry run python demo_composition.py          # swapping the formatter changes the output with no change to Report
poetry run python demo_protocol.py             # two unrelated classes satisfy one Protocol by shape; a function accepts either
poetry run python demo_dependency_injection.py # the service that receives its source runs with a real or a fake source
poetry run python demo_decorator.py            # a traced() decorator prints around a call without changing the function
```

To run them all in one go:

```bash
for f in demo_*.py; do echo "== $f =="; poetry run python "$f"; done
```

Times and sizes vary with your machine; the pattern is the point, not the exact number.
`demos/README.md` has the same list in a table.

---

## 2. The live-lab: `reviews-insight`

This is the running application you make maintainable on Day 3 (clear shapes with dataclasses, a
swappable data source behind a Protocol, and cross-cutting concerns pulled into decorators). If you
built it during the live lab you are already inside the `reviews-insight` folder; if you are using
the provided project, `cd` into it first.

```bash
cd reviews-insight     # or wherever the Day 3 liveLab project is
poetry install
poetry run reviews summary
```

The summary prints a small count block. The first line comes from the `@timed` decorator, a
cross-cutting concern kept out of the service logic, so the exact millisecond figure varies with
your machine:

```
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
```

The sample has five reviews across three products. Run the quality gate the same way as Day 1:

```bash
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

Eight tests pass. The key Day 3 proof is one test that swaps the data source (from the CSV file to an
in-memory source) with no change to the service logic. That is the seam working: the service depends
on the shape of a source, not on where the data comes from.

---

## 3. The offline assignments

Each is its own Poetry project. `cd` into it, `poetry install`, then run.

**Assignment 01, `telemetry-insight`** (a device readings feed refactored to inject a Protocol-based
source):

```bash
poetry run telemetry summary
```

It prints the same shape of count block:

```
readings: 5
devices : 3
```

**Assignment 02, `transactions-insight`** (an account transactions feed refactored to inject a
Protocol-based source and a swappable categorization strategy):

```bash
poetry run transactions summary
```

It prints the same shape of count block:

```
transactions: 5
accounts    : 3
```

---

## 4. The commands you use everywhere (recap)

- `poetry install` sets up a project's own environment.
- `poetry run <cmd>` runs inside that environment. Never use a bare `python` for project code.
- `poetry run pytest -q`, `poetry run ruff check .`, `poetry run mypy src` are the quality gate.
- `poetry run reviews summary` runs the live-lab; the source-swap test is the Day 3 proof.

---

## 5. Troubleshooting

- **`can't open file '...py:'`** You have a stray character (usually a `:`) on the end of the
  command. Retype it: `poetry run python demo_class_vs_function.py`, no trailing colon.
- **The counts look wrong.** The sample has five reviews across three products, so `reviews : 5`
  and `products: 3`. If the numbers differ, check that you are pointing at the sample CSV in `data/`.
- **The source-swap test fails.** That means the service is still reaching for the CSV file directly
  instead of accepting a source. A correct build takes its source as an argument, so a real source
  and an in-memory one are interchangeable with no change to the service logic.
- **`poetry run` cannot find the command** (`reviews`, `telemetry`, `transactions`). Run
  `poetry install` in that project first; the command is defined under `[tool.poetry.scripts]`.

---

## 6. Readiness check

- [ ] `python3 -V` shows 3.11 or newer and `poetry --version` shows Poetry 2.x (from Day 1).
- [ ] In `demos/`, `poetry install` succeeds and `poetry run python demo_class_vs_function.py`
  prints its expected output.
- [ ] The `reviews-insight` project runs `poetry run reviews summary` and shows `reviews : 5`,
  `products: 3`, with a `[timed] summary:` line above it.
- [ ] `poetry run pytest -q` passes all eight tests, including the source-swap test.
- [ ] You confirmed there is nothing new to install for Day 3: standard library plus Poetry.

If every line checks out, you can run every Day 3 sample and follow every **Try it** in the lesson.
