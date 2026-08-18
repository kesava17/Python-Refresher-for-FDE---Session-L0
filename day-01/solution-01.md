# Solution 01 · Build a telemetry-insight service

> The full worked solution for Assignment 01. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

This walks the whole build, step by step, with the exact commands and the full content of
every file. Follow it top to bottom and you'll end with a working `telemetry-insight`
service that passes every gate. Use `poetry run` for everything, since Poetry 2.x doesn't
put an `activate` step in your way.

The end state prints this:

```
[dev] telemetry-insight
readings: 5
devices : 3
```

Let's build it.

## Step 1: scaffold the project with Poetry

Create the project with a src layout:

```bash
poetry new --src telemetry-insight
cd telemetry-insight
```

`poetry new --src` builds a project where your package lives under `src`, which is the
layout that keeps your tests honest: they import the installed package, not loose files in
the repo root. Poetry gives you a `pyproject.toml`, a `src/telemetry_insight` package
folder, and a `tests` folder. Note the names: the project is `telemetry-insight` with a
hyphen, but the package folder is `telemetry_insight` with an underscore, because a
hyphen isn't legal in a Python import.

## Step 2: replace pyproject.toml

Open `pyproject.toml` and replace its contents with this:

```toml
[tool.poetry]
name = "telemetry-insight"
version = "0.1.0"
description = "A data-to-insight service, built step by step."
authors = ["GuildTrek <hello@guildtrek.com>"]
packages = [{ include = "telemetry_insight", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
python-dotenv = "^1.0"

[tool.poetry.group.dev.dependencies]
ruff = ">=0.6"
mypy = ">=1.11"
pytest = ">=8.0"
pre-commit = ">=3.7"

[tool.poetry.scripts]
telemetry = "telemetry_insight.cli:main"

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

This one file carries most of the enterprise shape. The runtime dependency is just
`python-dotenv` for reading a local `.env` in dev. The dev group holds ruff, mypy,
pytest, and pre-commit, so the quality tools are declared but never ship to production.
The `packages` line points Poetry at the src layout. The `[tool.poetry.scripts]` table is
what turns `main` into a runnable command called `telemetry`. And mypy is set to
`strict = true`, which is the whole point of the exercise: real type checking, not the
loose kind.

## Step 3: install

```bash
poetry install
```

Poetry reads `pyproject.toml`, resolves the dependency tree, writes a `poetry.lock` so the
install is reproducible, and installs your package in editable mode. After this, the
`telemetry` command exists inside the project's environment.

## Step 4: the package version

Set the package version marker in `src/telemetry_insight/__init__.py`:

```python
__version__ = "0.1.0"
```

Small, but it keeps the package's declared version in one obvious place.

## Step 5: config from the environment

Create `src/telemetry_insight/config.py`:

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

# config.py lives at src/telemetry_insight/config.py, so parents[2] is the project root.
# Anchoring the default data path there lets the command run from any directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = str(_PROJECT_ROOT / "data" / "telemetry_sample.csv")


@dataclass(frozen=True)
class Config:
    app_name: str
    data_path: str
    environment: str

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            app_name=os.environ.get("APP_NAME", "telemetry-insight"),
            data_path=os.environ.get("DATA_PATH", _DEFAULT_DATA),
            environment=os.environ.get("APP_ENV", "dev"),
        )
```

Config comes from the environment, with defaults, so nothing is hard coded into the logic.
The `Config` is a frozen dataclass, so once built it can't be changed by accident. The
`try` around the `dotenv` import means the code still runs even where python-dotenv isn't
installed, which is exactly how you want production to behave: it reads real environment
variables and skips the dev convenience.

## Step 6: load the data

Create `src/telemetry_insight/data.py`:

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

`csv.DictReader` reads each row into a dict keyed by the header, so a row becomes
`{"device_id": "D1", "ts": "...", "value": "21.5"}`. The existence check up front means a
missing file fails with a clear `FileNotFoundError` and a helpful message, not a confusing
error deeper in the stack.

## Step 7: the summary and the CLI

Create `src/telemetry_insight/cli.py`:

```python
"""Command line entry point."""

from __future__ import annotations

import argparse

from telemetry_insight.config import Config
from telemetry_insight.data import load_records


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """A first, tiny summary: how many readings, and how many devices."""
    devices = {record["device_id"] for record in records}
    return {"readings": len(records), "devices": len(devices)}


def main() -> None:
    parser = argparse.ArgumentParser(description="telemetry-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    args = parser.parse_args()

    config = Config.from_env()
    records = load_records(config.data_path)

    if args.command == "summary":
        result = summarize(records)
        print(f"[{config.environment}] {config.app_name}")
        print(f"readings: {result['readings']}")
        print(f"devices : {result['devices']}")


if __name__ == "__main__":
    main()
```

`summarize` does the real work in one place, so the test can call it directly. The set
comprehension over `device_id` collects the distinct devices, and `len` on that set is the
device count. `main` reads config, loads the data, runs the summary, and prints the three
lines. Mind the spacing in `devices :`, which lines the colons up with the `readings:`
line above it.

## Step 8: the sample data

Create the `data` folder and a file `data/telemetry_sample.csv` with this content:

```
device_id,ts,value
D1,2026-01-01T00:00:00,21.5
D1,2026-01-01T00:01:00,21.7
D2,2026-01-01T00:00:00,48.0
D2,2026-01-01T00:01:00,49.2
D3,2026-01-01T00:00:00,7.1
```

Five reading rows, three distinct devices (D1, D2, D3). That's what makes the summary come
out as `readings: 5` and `devices : 3`.

## Step 9: the test

Create `tests/test_summary.py`:

```python
"""Tests for the telemetry-insight summary."""

from __future__ import annotations

from pathlib import Path

from telemetry_insight.cli import summarize
from telemetry_insight.data import load_records


def test_load_and_summarize(tmp_path: Path) -> None:
    csv_text = "device_id,ts,value\nD1,2026-01-01T00:00:00,1.0\nD1,2026-01-01T00:01:00,2.0\nD2,2026-01-01T00:00:00,3.0\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"readings": 3, "devices": 2}
```

This test proves the whole pipeline in one shot. It writes a tiny CSV into pytest's
`tmp_path`, a temporary folder cleaned up for you, loads it, and checks both the record
count and the summary. It uses its own three-row fixture, so it doesn't depend on the
sample file, which keeps the test self-contained.

## Step 10: the environment example and ignore file

Create `.env.example` so the variable names are documented without leaking anything real:

```
APP_NAME=telemetry-insight
APP_ENV=dev
DATA_PATH=data/telemetry_sample.csv
DATABASE_URL=postgresql://telemetry_admin:change_me_in_prod@localhost:5432/telemetry_db
```

The real `.env` stays out of Git. The example shows the shape, with an obvious
`change_me_in_prod` placeholder so nobody mistakes it for a real secret.

Create `.gitignore`:

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

This keeps the environment, the bytecode cache, your real secrets, the build output, and
the tool caches out of the repo. You commit the description of the environment, not the
built result.

## Step 11: run it

```bash
poetry run telemetry summary
```

You should see exactly:

```
[dev] telemetry-insight
readings: 5
devices : 3
```

`poetry run` runs the command inside the project's environment, so there's no separate
activation step to remember.

## Step 12: run the test

```bash
poetry run pytest -q
```

You should see:

```
1 passed
```

## Step 13: run the quality gates

```bash
poetry run ruff check .
```

Expected:

```
All checks passed!
```

Then the type checker in strict mode:

```bash
poetry run mypy src
```

Expected:

```
Success: no issues found
```

Both clean. The strict mypy pass is only possible because every function has its argument
and return types, and each module opens with `from __future__ import annotations` so the
modern type syntax works on Python 3.11.

## Step 14: the pre-commit hook

Add a `.pre-commit-config.yaml` at the repo root so the gates run automatically before a
commit lands:

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

Then install the hook into your local Git so it fires on every commit:

```bash
poetry run pre-commit install
```

Using `local` system hooks that call `poetry run` keeps one source of truth: the hook runs
the exact same ruff and mypy your project already declares, so what passes locally is what
the commit gate checks.

## Step 15: the docker-compose stub

Add a `docker-compose.yml` at the repo root. It's a stub, so it just describes running the
service in a container:

```yaml
services:
  telemetry:
    build: .
    environment:
      APP_NAME: telemetry-insight
      APP_ENV: dev
      DATA_PATH: data/telemetry_sample.csv
    command: poetry run telemetry summary
```

This names one service, passes config through environment variables rather than baking it
in, and runs the summary command. It's enough to show the container shape without turning
the assignment into a Docker exercise.

## Step 16: the first Git commit

Initialize the repo, stage everything, and make one clean commit:

```bash
git init
git add .
git commit -m "initial telemetry-insight service"
```

Because the `.gitignore` is already in place, `git add .` skips `.venv`, `__pycache__`,
and `.env`. Your first commit captures the source, the config example, the tests, and the
tooling, but none of the built or secret files.

## Done

Run through the checklist:

- `poetry install` completes with no errors.
- `poetry run telemetry summary` prints the three target lines.
- `poetry run pytest -q` shows `1 passed`.
- `poetry run ruff check .` shows `All checks passed!`.
- `poetry run mypy src` shows `Success: no issues found`.
- The pre-commit config exists and its hooks run.
- The `docker-compose.yml` stub exists and is valid.
- `git log` shows one clean initial commit, with `.venv`, `__pycache__`, and `.env`
  untracked.

That's the enterprise shape, end to end, on a new domain. Same skeleton you built in
class, now yours to repeat from memory.
