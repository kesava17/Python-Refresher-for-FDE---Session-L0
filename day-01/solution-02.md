# Day 1 · Solution 02 · transactions-insight, worked step by step (Poetry)

> The complete answer to Assignment 02. Every command, every file, and why each
> piece is there. Read this after you've tried, or when you're stuck at a level.

This walks the whole build from an empty folder to a green quality gate and a
first commit. Use `poetry run` for everything so you're always inside the
project's environment. This was verified end to end on Poetry 2.x with Python
3.11.

## What you'll end up with

```text
transactions-insight/
├── pyproject.toml
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── docker-compose.yml
├── data/
│   └── transactions_sample.csv
├── src/
│   └── transactions_insight/
│       ├── __init__.py
│       ├── config.py
│       ├── data.py
│       └── cli.py
└── tests/
    └── test_summary.py
```

## Level 1: Scaffold the project

Create the project with Poetry's src layout, then move into it:

```bash
poetry new --src transactions-insight
cd transactions-insight
```

`poetry new --src` builds the standard skeleton: a `pyproject.toml`, a package
under `src/transactions_insight/`, and a `tests/` folder. The src layout keeps
your importable package in one place and stops the tests from accidentally
importing loose files from the project root. It's the layout every serious
Python project uses.

Now replace the generated `pyproject.toml` with the full version below.

### pyproject.toml

```toml
[tool.poetry]
name = "transactions-insight"
version = "0.1.0"
description = "A data-to-insight service, built step by step."
authors = ["GuildTrek <hello@guildtrek.com>"]
packages = [{ include = "transactions_insight", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
python-dotenv = "^1.0"

[tool.poetry.group.dev.dependencies]
ruff = ">=0.6"
mypy = ">=1.11"
pytest = ">=8.0"
pre-commit = ">=3.7"

[tool.poetry.scripts]
transactions = "transactions_insight.cli:main"

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
strict = true
ignore_missing_imports = true

[build-system]
requires = ["poetry-core>=1.9.0"]
build-backend = "poetry.core.masonry.api"
```

This one file carries a lot. The `packages` line points Poetry at the src layout.
The runtime depends only on `python-dotenv`, kept separate from the dev group
(`ruff`, `mypy`, `pytest`, `pre-commit`) so a production install can skip the dev
tools. The `[tool.poetry.scripts]` table is what turns `transactions` into a real
command: `poetry run transactions` calls `main` in `cli.py`. The ruff and mypy
tables configure the quality gate, and `strict = true` turns on mypy's full set
of checks.

Install everything, which also creates the virtual environment:

```bash
poetry install
```

## Level 2: Config from the environment

Configuration comes from environment variables, never hard coded. Here's
`src/transactions_insight/config.py`:

```python
"""Application configuration, read from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()  # load a local .env in dev; a no-op if the file is absent
except ImportError:  # python-dotenv is a dev convenience; prod uses real env vars
    pass

# config.py lives at src/transactions_insight/config.py, so parents[2] is the project root.
# Anchoring the default data path there lets the command run from any directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = str(_PROJECT_ROOT / "data" / "transactions_sample.csv")


@dataclass(frozen=True)
class Config:
    app_name: str
    data_path: str
    environment: str

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            app_name=os.environ.get("APP_NAME", "transactions-insight"),
            data_path=os.environ.get("DATA_PATH", _DEFAULT_DATA),
            environment=os.environ.get("APP_ENV", "dev"),
        )
```

The dataclass is frozen, so config is read only once it's built. `from_env` reads
three variables with sensible defaults, which is why the app runs out of the box
without a `.env`. Loading `python-dotenv` is wrapped in a `try` so the code still
works if the package isn't there: in production you set real environment
variables and skip the `.env` file entirely.

Commit an example of the variables, but never the real file. Here's
`.env.example`:

```bash
APP_NAME=transactions-insight
APP_ENV=dev
DATA_PATH=data/transactions_sample.csv
DATABASE_URL=postgresql://transactions_admin:change_me_in_prod@localhost:5432/transactions_db
```

The `.env.example` documents which variables exist and is safe to commit. The
real `.env`, with real secrets, stays out of Git (see the `.gitignore` in Level
7). The placeholder `DATABASE_URL` shows the shape a real connection string would
take, with an obvious `change_me_in_prod` so nobody mistakes it for a real
secret.

## Level 3: Load the data

The sample data lives at `data/transactions_sample.csv`:

```csv
account_id,amount,currency
A1,250.00,INR
A1,90.50,INR
A2,1200.00,INR
A2,60.00,INR
A3,15.75,INR
```

And `src/transactions_insight/data.py` reads it:

```python
"""Load records from a CSV file."""

from __future__ import annotations

import csv
from pathlib import Path


def load_records(path: str) -> list[dict[str, str]]:
    """Read the CSV file into a list of dicts. Fail clearly if it is missing."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"data file not found: {path}")
    with file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{key: str(value) for key, value in row.items()} for row in reader]
```

`csv.DictReader` turns each row into a dict keyed by the header names, so a row
becomes `{"account_id": "A1", "amount": "250.00", "currency": "INR"}`. The
explicit `FileNotFoundError` check means a missing file gives a clear message that
names the path, instead of a confusing error deeper in the stack. Note the return
type: `list[dict[str, str]]`. Every value is a string at this point, because CSV
is text. Converting `amount` to a number happens in the summary, on purpose.

## Level 4: The summary and the CLI

Here's the feature, in `src/transactions_insight/cli.py`:

```python
"""Command line entry point."""

from __future__ import annotations

import argparse

from transactions_insight.config import Config
from transactions_insight.data import load_records


def summarize(records: list[dict[str, str]]) -> dict[str, float]:
    """A first, tiny summary: count, distinct accounts, and total amount."""
    accounts = {record["account_id"] for record in records}
    total = round(sum(float(record["amount"]) for record in records), 2)
    return {"transactions": len(records), "accounts": len(accounts), "total": total}


def main() -> None:
    parser = argparse.ArgumentParser(description="transactions-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    args = parser.parse_args()

    config = Config.from_env()
    records = load_records(config.data_path)

    if args.command == "summary":
        result = summarize(records)
        print(f"[{config.environment}] {config.app_name}")
        print(f"transactions: {int(result['transactions'])}")
        print(f"accounts    : {int(result['accounts'])}")
        print(f"total       : {result['total']:.2f}")


if __name__ == "__main__":
    main()
```

`summarize` does three things: it counts the rows with `len`, it collects the
distinct `account_id` values into a set (a set drops duplicates, so its length is
the distinct account count), and it sums the amounts. `main` wires it together:
parse the command, build the config, load the data, and print.

A word on rounding money. The amounts are strings from the CSV, so each is passed
through `float()` before summing. Floating point addition isn't exact, and a bare
sum can come out as something like `1616.2500000000002`. Two things fix this.
First, `round(..., 2)` rounds the total to two decimal places, which is the
natural precision for rupees. Second, the print uses `:.2f`, which formats the
number to exactly two decimals so it always reads as `1616.25`, never `1616.2` or
a long tail. Round when you compute, format when you display: both matter.

Run it:

```bash
poetry run transactions summary
```

Expected output:

```text
[dev] transactions-insight
transactions: 5
accounts    : 3
total       : 1616.25
```

## Level 5: The test

One test proves the summary is right. Here's `tests/test_summary.py`:

```python
"""Tests for the transactions-insight summary."""

from __future__ import annotations

from pathlib import Path

from transactions_insight.cli import summarize
from transactions_insight.data import load_records


def test_load_and_summarize(tmp_path: Path) -> None:
    csv_text = "account_id,amount,currency\nA1,250.00,INR\nA1,90.50,INR\nA2,1200.00,INR\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"transactions": 3, "accounts": 2, "total": 1540.5}
```

The test uses pytest's `tmp_path` fixture, which hands you a fresh temporary
directory, so the test writes its own tiny CSV and never depends on the real data
file. The expected numbers are small enough to check by hand: 3 rows, two
accounts (`A1` and `A2`), and `250.00 + 90.50 + 1200.00 = 1540.50`. A test you
can verify in your head is a test you can trust.

Run it:

```bash
poetry run pytest -q
```

Expected:

```text
1 passed
```

## Level 6: The quality gate

The ruff and mypy settings already live in `pyproject.toml` from Level 1. Now add
the pre-commit hook so the gate runs automatically before every commit. Here's
`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: poetry run ruff check .
        language: system
        pass_filenames: false
      - id: mypy
        name: mypy
        entry: poetry run mypy src
        language: system
        pass_filenames: false
```

These are `local` hooks that call the same commands you run by hand, so the gate
that runs on your machine is the exact gate that runs before a commit. Install
the hook into your repo with `poetry run pre-commit install` once the repo
exists. Then add the container stub, `docker-compose.yml`:

```yaml
services:
  transactions-insight:
    build: .
    image: transactions-insight:latest
    env_file:
      - .env
    command: poetry run transactions summary
```

This is a stub, so it describes how the service would run in a container without
building out a full stack. It reads configuration from `.env` at run time (never
baked into the image) and runs the same `summary` command. It's here to show the
shape, and you'll flesh out the `Dockerfile` it references in a later lesson.

Run the gate by hand and confirm both are clean:

```bash
poetry run ruff check .
poetry run mypy src
```

Expected:

```text
All checks passed!
```

```text
Success: no issues found in 4 source files
```

Why is mypy strict happy here? Because every function is fully annotated.
`load_records` declares `-> list[dict[str, str]]`, `summarize` declares
`-> dict[str, float]`, and `main` declares `-> None`. Strict mode refuses to let
any function go untyped, so a missing annotation would be an error, not a warning.
The typed summary is the key one: because its input and output types are spelled
out, mypy can follow the values all the way from the CSV load through the sum to
the printed result and confirm nothing is misused. Types aren't decoration here,
they're what lets the checker prove the code end to end.

## Level 7: First commit

Keep the environment, the caches, and secrets out of Git. Here's `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
.env
dist/
.mypy_cache/
.ruff_cache/
.pytest_cache/
```

This ignores the virtual environment, the bytecode cache, the built distribution,
the tool caches, and, importantly, the real `.env`. What you commit is the
description of the environment (the `pyproject.toml` and the lockfile), not the
built result or the secrets.

Now make the first commit:

```bash
git init
git add .
git commit -m "initial transactions-insight service"
```

That's the safety net in place from the first line of code. Check it with
`git log` and confirm `.env` isn't listed under `git status`.

## Recap

You built the same enterprise shape as the in-class lab, on a new domain:

- A Poetry project with a src layout and a proper `pyproject.toml`.
- Config read from the environment, with a committed `.env.example` and an
  ignored `.env`.
- A clean data loader that fails with a clear message.
- A CLI `summary` command that counts transactions and accounts and totals the
  amount, with money rounded to two decimals.
- One trustworthy test.
- A green quality gate: ruff clean, mypy strict clean.
- A pre-commit hook and a docker-compose stub.
- A first Git commit with a sensible `.gitignore`.

The feature was tiny on purpose. The scaffolding around it is the real skill, and
now you've built it twice.
