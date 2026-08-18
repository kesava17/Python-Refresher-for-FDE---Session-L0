# Day 1 · Assignment 02 · Build a transactions-insight service (Poetry)

> Offline practice. Take the enterprise shape you built in class and rebuild it
> from scratch for a new domain: financial transactions. Same rigor, new data.

In the in-class lab you built `reviews-insight`: a Poetry project with a src
layout, config read from the environment, a CLI `summary` command, one test,
ruff and mypy strict passing, a pre-commit gate, a Docker Compose stub, and a
first Git commit. That's the enterprise shape. This assignment asks you to build
the same shape again, on your own, for a different domain. Building it a second
time is how it sticks.

You'll write the answer yourself. This file gives you the goal, the data, the
required pieces, and staged hints. The full worked solution lives in
`solution-02.md`, but don't open it until you've tried. The point is the doing.

## Goal

Build a small service called `transactions-insight`. It reads a CSV of financial
transactions and prints a short summary: how many transactions there are, how
many distinct accounts appear, and the total amount. Amounts are in rupees. That
is the whole feature. The value of this exercise isn't the feature, it's the
professional scaffolding around it.

## The data

You work with a tiny CSV so you can check the numbers by hand. It has three
columns:

- `account_id`: which account the transaction belongs to (a short string like `A1`).
- `amount`: the transaction amount in rupees (a decimal number).
- `currency`: the currency code (always `INR` here).

Create this sample yourself as `data/transactions_sample.csv`:

```csv
account_id,amount,currency
A1,250.00,INR
A1,90.50,INR
A2,1200.00,INR
A2,60.00,INR
A3,15.75,INR
```

Read it by eye first. There are 5 rows, so 5 transactions. The accounts are
`A1`, `A2`, and `A3`, so 3 distinct accounts. The amounts add up to
`250.00 + 90.50 + 1200.00 + 60.00 + 15.75`, which is `1616.25`. Those three
numbers are what your summary has to print. Knowing the answer before you code it
is the honest way to test yourself.

## Required pieces

Build all of these. Each one is a habit you'll use on every real project.

1. **A Poetry project with a src layout.** Create it with `poetry new --src
   transactions-insight`. The package lives under `src/transactions_insight/`.
2. **Dependencies declared in `pyproject.toml`.** A runtime dependency on
   `python-dotenv` (for loading a local `.env`), and a dev group with `ruff`,
   `mypy`, `pytest`, and `pre-commit`.
3. **A src and tests layout.** Package code under `src/transactions_insight/`,
   tests under `tests/`.
4. **Config read from the environment.** A small `Config` object built from
   environment variables (app name, data path, environment name), with sensible
   defaults. Secrets and paths come from the environment, never hard coded.
5. **A CLI `summary` command.** Running `poetry run transactions summary` reads
   the CSV and prints the transaction count, the distinct account count, and the
   total amount.
6. **One test.** A pytest test that builds a tiny CSV, loads it, and asserts the
   summary numbers are right.
7. **ruff and mypy strict passing.** `poetry run ruff check .` reports no issues,
   and `poetry run mypy src` passes under strict mode.
8. **A pre-commit hook.** A `.pre-commit-config.yaml` that runs ruff and mypy, so
   the quality gate runs automatically before each commit.
9. **A docker-compose stub.** A `docker-compose.yml` that describes how the
   service would run in a container. It's a stub, so it doesn't have to launch a
   full stack, but it should be valid.
10. **A first Git commit.** Initialize a repo, add a `.gitignore`, and make one
    clean initial commit.

## Staged guidance

Work in this order. Don't jump ahead. Each level leaves you with something that
runs.

### Level 1: Scaffold and install

Create the project with `poetry new --src transactions-insight` and move into it.
Look at what Poetry generated: a `pyproject.toml`, a `src/transactions_insight/`
package, and a `tests/` folder. Replace the generated `pyproject.toml` with your
own that declares the name, the src package, the dependencies, the dev group, and
the CLI script entry. Then run `poetry install` to create the environment and
install everything.

Hint: the CLI script is wired in the `[tool.poetry.scripts]` table. A line like
`transactions = "transactions_insight.cli:main"` makes `poetry run transactions`
call the `main` function in `cli.py`.

### Level 2: Config from the environment

Write `config.py`. Define a small frozen dataclass with three fields (app name,
data path, environment), and a classmethod that builds it from `os.environ` with
defaults. Load a local `.env` with `python-dotenv` if it's present, but make the
code work fine when it's absent too. Add a `.env.example` so a teammate knows
which variables exist, and make sure your real `.env` is git-ignored.

Hint: the golden rule from the lesson is never hard code configuration or
secrets. Read them from the environment. The `.env.example` is committed, the
`.env` is not.

### Level 3: Load the data

Write `data.py` with a `load_records` function that reads the CSV into a list of
dicts. Fail clearly if the file is missing, with a message that names the path.
Use the standard library `csv.DictReader`. No third party data library is needed
for this.

Hint: raise `FileNotFoundError` with a helpful message rather than letting a
confusing lower level error escape. A good error message saves the next person
ten minutes.

### Level 4: The summary and the CLI

Write the `summarize` function and the `main` entry point in `cli.py`. The
summary counts the rows, counts the distinct `account_id` values with a set, and
sums the `amount` values. Parse the command line with `argparse` and accept a
single `summary` command. Print the environment tag and app name, then the three
numbers.

Hint on money: never leave a raw floating point sum as your total. Floating point
addition can produce a trailing tail like `1616.2500000000002`. Round the total
to two decimal places, and format it to two decimals when you print it. Two
decimals is the natural precision for rupees.

### Level 5: The test

Write one test under `tests/`. Build a tiny CSV in a temporary directory (pytest
gives you a `tmp_path` fixture), load it, and assert the summary matches the
numbers you worked out by hand. Run it with `poetry run pytest -q` and get a
green result.

Hint: keep the test data small enough that you can compute the expected numbers
in your head. That's what makes the assertion trustworthy.

### Level 6: The quality gate

Configure ruff and mypy in `pyproject.toml` (line length, target version, and
`strict = true` for mypy). Add type hints everywhere so mypy strict is happy.
Then add a `.pre-commit-config.yaml` that runs ruff and mypy, and a
`docker-compose.yml` stub. Run the gate by hand: `poetry run ruff check .` and
`poetry run mypy src` should both be clean.

Hint on mypy strict: strict mode wants every function annotated, including the
return type. A function that returns nothing is annotated `-> None`. Give your
summary a clear return type so mypy can check it end to end.

### Level 7: First commit

Add a `.gitignore` that keeps the virtual environment, the bytecode cache, the
caches, and your `.env` out of the repo. Then `git init`, `git add .`, and make
one clean initial commit. This is the safety net from the first line of code.

## Done when

You're finished when all of these are true:

- `poetry run transactions summary` prints exactly:

  ```text
  [dev] transactions-insight
  transactions: 5
  accounts    : 3
  total       : 1616.25
  ```

- `poetry run pytest -q` reports `1 passed`.
- `poetry run ruff check .` reports `All checks passed!`.
- `poetry run mypy src` reports `Success: no issues found`.
- `.pre-commit-config.yaml` and `docker-compose.yml` exist and are valid.
- `git log` shows one clean initial commit, and `.env` is not tracked.

Get all six and you've rebuilt the enterprise shape on your own. When you're
done, or if you get stuck at a level, compare against `solution-02.md`.
