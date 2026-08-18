# Day 1 Live Lab: The reviews-insight Service

## What we're building

In the next 30 minutes you'll stand up a small service called **reviews-insight**.
It reads a CSV of product reviews and prints a tiny summary. That's it. The point
isn't the logic. The point is the toolchain around it: Poetry for the project and
its environment, Ruff and mypy for quality, pytest for tests, a pre-commit gate
that blocks bad commits, and a Docker Postgres stub for later.

Work through the steps in order. Copy, paste, run. After each step there's one line
on what happened and why it matters. Keep an eye out for the moment in Step 6 where
the gate stops a bad commit cold. That's the lesson that sticks.

A few ground rules for the commands:

- Everything Python runs through `poetry run`. Poetry owns the environment, so you
  never touch the system Python.
- Docker is `docker compose` (v2, with a space), not the old `docker-compose`.
- Run the commands from inside the project folder once you've scaffolded it.

---

## Step 1: Scaffold the project

Let Poetry lay out the folders for you, in the `src` layout we want.

```bash
poetry new --src reviews-insight
cd reviews-insight
```

**What happened.** Poetry created a `reviews-insight` folder with a `pyproject.toml`,
a `src/reviews_insight/` package, and a `tests/` folder. The `--src` flag puts your
code under `src/`, which keeps your package and your project root cleanly separated.
That separation is what stops your tests from importing the wrong copy of the code.

---

## Step 2: Set the project file and install

Open `pyproject.toml` and replace its whole contents with this. It names the package,
pins the dependencies, wires up the `reviews` command, and holds the Ruff and mypy
config in one place.

```toml
[tool.poetry]
name = "reviews-insight"
version = "0.1.0"
description = "A data-to-insight service, built step by step."
authors = ["GuildTrek <hello@guildtrek.com>"]
packages = [{ include = "reviews_insight", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
python-dotenv = "^1.0"

[tool.poetry.group.dev.dependencies]
ruff = ">=0.6"
mypy = ">=1.11"
pytest = ">=8.0"
pre-commit = ">=3.7"

[tool.poetry.scripts]
reviews = "reviews_insight.cli:main"

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

Now install everything into the project's own environment.

```bash
poetry install
```

**What happened.** Poetry read the file, resolved the versions, and built a virtual
environment with your app dependency (`python-dotenv`) and your dev tools (Ruff, mypy,
pytest, pre-commit). It also wrote a `poetry.lock` with the exact versions and
installed your package in editable mode, so `import reviews_insight` just works. The
lockfile is what makes the install reproducible on the next machine.

---

## Step 3: Create the source files

Create each file below with the exact content shown. A couple of these files Poetry
already made as stubs (`src/reviews_insight/__init__.py` and the `tests/` folder), so
you're filling them in.

**`src/reviews_insight/__init__.py`**

```python
__version__ = "0.1.0"
```

**`src/reviews_insight/config.py`**

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

# config.py lives at src/reviews_insight/config.py, so parents[2] is the project root.
# Anchoring the default data path there lets the command run from any directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = str(_PROJECT_ROOT / "data" / "reviews_sample.csv")


@dataclass(frozen=True)
class Config:
    app_name: str
    data_path: str
    environment: str

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            app_name=os.environ.get("APP_NAME", "reviews-insight"),
            data_path=os.environ.get("DATA_PATH", _DEFAULT_DATA),
            environment=os.environ.get("APP_ENV", "dev"),
        )
```

**`src/reviews_insight/data.py`**

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

**`src/reviews_insight/cli.py`**

```python
"""Command line entry point."""

from __future__ import annotations

import argparse

from reviews_insight.config import Config
from reviews_insight.data import load_records


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """A first, tiny summary: how many reviews, and how many products."""
    products = {record["product_id"] for record in records}
    return {"reviews": len(records), "products": len(products)}


def main() -> None:
    parser = argparse.ArgumentParser(description="reviews-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    args = parser.parse_args()

    config = Config.from_env()
    records = load_records(config.data_path)

    if args.command == "summary":
        result = summarize(records)
        print(f"[{config.environment}] {config.app_name}")
        print(f"reviews : {result['reviews']}")
        print(f"products: {result['products']}")


if __name__ == "__main__":
    main()
```

**`tests/test_summary.py`**

```python
"""Tests for the reviews-insight summary."""

from __future__ import annotations

from pathlib import Path

from reviews_insight.cli import summarize
from reviews_insight.data import load_records


def test_load_and_summarize(tmp_path: Path) -> None:
    csv_text = "product_id,rating,text\nP1,5,great\nP1,4,good\nP2,3,ok\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"reviews": 3, "products": 2}
```

**`data/reviews_sample.csv`**

```text
product_id,rating,text
P100,5,Excellent build and battery life
P100,4,Good value for the price
P200,3,Average it does the job
P200,2,Stopped working after a week
P300,5,Fantastic highly recommend
```

**`.env.example`**

```env
APP_NAME=reviews-insight
APP_ENV=dev
DATA_PATH=data/reviews_sample.csv
DATABASE_URL=postgresql://reviews_admin:change_me_in_prod@localhost:5432/reviews_db
```

**`.gitignore`**

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

**What happened.** You now have a real, if tiny, service. `config.py` reads settings
from the environment, `data.py` loads the CSV, and `cli.py` ties them together behind
the `reviews` command. The `.env.example` is the template you share. The real `.env`
holds secrets, so it's in `.gitignore` and never gets committed. Notice there's no
`.env` yet, and the app still runs, because `config.py` has sensible defaults.

---

## Step 4: Run the app

```bash
poetry run reviews summary
```

You should see exactly:

```text
[dev] reviews-insight
reviews : 5
products: 3
```

**What happened.** `poetry run` ran the `reviews` command inside the project
environment. It found five rows across three product IDs in the sample CSV and printed
the summary. The `[dev]` tag comes from the `APP_ENV` default in `config.py`. That's
your whole read-to-insight path working end to end.

---

## Step 5: Run the checks

Now run the quality tools, one at a time.

```bash
poetry run pytest -q
```

Expect `1 passed`.

```bash
poetry run ruff check .
```

Expect `All checks passed!`.

```bash
poetry run ruff format .
```

This formats the code in place. On a clean project it reports the files left
unchanged.

```bash
poetry run mypy src
```

Expect `Success: no issues found`.

**What happened.** Four different guards, each catching a different class of problem.
pytest proved the summary logic is correct. Ruff checked for lint issues and then
formatted the code to one consistent style. mypy checked the type hints and found the
code type-safe under strict mode. Green across all four is the bar every commit has to
clear.

---

## Step 6: Wire the quality gate

Passing the checks by hand is good. Making them impossible to skip is better. Add a
pre-commit config so the same tools run automatically before every commit.

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
```

Install the hook into Git:

```bash
poetry run pre-commit install
```

Now the memorable part. Break the code on purpose so mypy has something to catch. Open
`src/reviews_insight/cli.py` and change the `summarize` return line to hand back a
string where an int is promised:

```python
    return {"reviews": len(records), "products": "three"}
```

Stage it and try to commit:

```bash
git add src/reviews_insight/cli.py
git commit -m "break the types on purpose"
```

The commit is blocked. The mypy hook fails with a type error, roughly:

```text
error: Dict entry 1 has incompatible type "str": "str"; expected "str": "int"
```

The commit did not go through. Undo the change (put `len(products)` back):

```python
    return {"reviews": len(records), "products": len(products)}
```

**What happened.** The gate did its job. A change that broke the type contract never
made it into history, and it never had to reach a teammate or a build server to get
caught. That's the whole idea of an enforced gate: the bad commit stops at your
machine, in seconds, for free. Once the types are correct again, the same commit will
sail through in Step 8.

---

## Step 7: Bring up the infra stub

The service will need a database eventually. Add a Postgres service now so it's ready.
It runs alongside the app, but the app doesn't depend on it today.

Create `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: reviews_admin
      POSTGRES_PASSWORD: change_me_in_prod
      POSTGRES_DB: reviews_db
    ports:
      - "5432:5432"
    volumes:
      - reviews_pgdata:/var/lib/postgresql/data

volumes:
  reviews_pgdata:
```

Start it in the background, then check it:

```bash
docker compose up -d
docker compose ps
```

**What happened.** Docker pulled the Postgres 16 image and started a container mapped
to port 5432, with its data kept in a named volume so it survives a restart. `docker
compose ps` shows it running. The app still runs fine without touching it: this is the
stub you'll connect to on a later day. Note there's no `version:` key at the top of the
file. Compose v2 dropped it, and leaving it in only earns a warning.

---

## Step 8: First Git commit

With the types fixed and everything green, save the skeleton.

```bash
git init
git add .
git commit -m "day 1: enterprise project skeleton"
```

**What happened.** `git init` started the repository, `git add .` staged the project
(minus everything in `.gitignore`), and the commit ran the pre-commit hooks one more
time. This time Ruff and mypy pass, so the commit goes through. Your first commit is
clean by construction, because the gate would not have let it be anything else.

---

## You should see

Run through this recap. If each line matches, Day 1 is done.

- `poetry run reviews summary` prints:

  ```text
  [dev] reviews-insight
  reviews : 5
  products: 3
  ```

- `poetry run pytest -q` prints `1 passed`.
- `poetry run ruff check .` prints `All checks passed!`.
- `poetry run mypy src` prints `Success: no issues found`.
- A deliberate type error is blocked by the mypy pre-commit hook, and the commit
  fails until you fix it.
- `docker compose ps` shows the `postgres` service running.
- `git commit` on the fixed code succeeds, and the hooks pass on the way in.

That's the whole enterprise loop in miniature: one environment per project via Poetry,
quality tools you can't skip, an infra stub ready to grow, and a first commit that was
clean before it was ever made.
