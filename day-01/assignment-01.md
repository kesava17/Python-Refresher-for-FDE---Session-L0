# Assignment 01 · Build a telemetry-insight service

> Offline practice for Day 1. You built the reviews-insight service in class. Now build
> the same enterprise shape on your own, for a different kind of data: IoT sensor
> telemetry.

This is a do-it-yourself assignment. There's no new theory here. The point is to walk
the whole path again, by yourself, so the moves stick: a Poetry project, a src layout,
config from the environment, a small CLI, a test, the quality gates, a pre-commit hook,
a docker-compose stub, and a first Git commit. When you're done you'll have a tiny
service that reads a CSV of sensor readings and prints a one-line summary.

Do it end to end without copying the class code. Struggle a little. That's where the
learning is. The solution file is there when you're truly stuck, but try first.

## The goal

Build a command line service called `telemetry-insight`. It reads a CSV file of device
readings and, when you run its `summary` command, prints how many readings there are and
how many distinct devices reported them. Same enterprise skeleton as the class lab, new
domain.

By the end, running the service should print exactly this:

```
[dev] telemetry-insight
readings: 5
devices : 3
```

Everything else in the assignment exists to get you to that output the professional way,
not the quick-and-dirty way.

## The data

The service reads a small CSV. You create it yourself. It has three columns:

- `device_id`: which sensor sent the reading, for example `D1`.
- `ts`: the timestamp of the reading, an ISO style string.
- `value`: the number the sensor reported.

Make a `data` folder in your project and put a file called `telemetry_sample.csv` in it.
Give it a header row and five reading rows, across three different devices. Something
like this shape (use your own numbers if you want, but keep it to five rows and three
devices so your output matches the target above):

```
device_id,ts,value
D1,...,...
D1,...,...
D2,...,...
D2,...,...
D3,...,...
```

Five rows means `readings: 5`. Three distinct `device_id` values (D1, D2, D3) means
`devices : 3`. That's the whole trick to hitting the expected output.

## What you have to build

Build every one of these. This is the enterprise shape, and skipping a piece defeats the
purpose.

1. **A Poetry project with a src layout.** Create it with `poetry new --src`. The package
   lives under `src`, not at the repo root.
2. **Dependencies, split into runtime and dev.** One small runtime dependency for reading
   config, and a dev group for the quality tools.
3. **A src and tests layout.** Your package code under `src`, your test under `tests`.
4. **Config read from the environment.** App name, environment, and the path to the data
   file all come from environment variables, with sensible defaults. No secrets or paths
   hard coded in the logic.
5. **A CLI with a `summary` command.** Running it prints the environment and app name on
   one line, then the readings count, then the distinct device count, matching the target
   output.
6. **One test.** It builds a tiny CSV, loads it, summarizes it, and checks the counts.
7. **ruff clean.** `ruff check` passes with no complaints.
8. **mypy strict clean.** Type checking in strict mode passes with no issues.
9. **A pre-commit hook.** So ruff and mypy run automatically before a commit lands.
10. **A docker-compose stub.** A small compose file that describes running the service in
    a container. It doesn't have to do anything fancy. It just has to be there and be
    valid.
11. **A first Git commit.** Initialize a repo, add a sensible ignore file, and make one
    clean initial commit.

## Staged guidance

Work in small stages and check each one before moving on. Don't write the whole thing and
then try to run it.

### Level 1: scaffold the project

Use Poetry to create the project with a src layout. Look at what it generates: a
`pyproject.toml`, a `src` folder with your package inside, and a `tests` folder. Get
comfortable with where things landed before you touch anything.

Hint: the command is `poetry new --src` followed by the project name. The project name
uses a hyphen; the package folder Poetry creates uses an underscore. That difference
matters later when you write imports.

### Level 2: declare dependencies and install

Edit `pyproject.toml` so it has one runtime dependency for loading config from a `.env`
file, and a dev dependency group holding ruff, mypy, pytest, and pre-commit. Add a script
entry so `summary` is reachable through a short command name. Then install.

Hint: `poetry add` and `poetry add --group dev` can add dependencies for you, or you can
write them into `pyproject.toml` by hand and run `poetry install`. Either way, the dev
tools go in a dev group so they don't ship to production. The `[tool.poetry.scripts]`
table is what turns your function into a runnable command.

### Level 3: config from the environment

Write a small config module. It reads the app name, the environment, and the data path
from environment variables, and falls back to defaults when they're absent. Keep it a
plain, frozen data holder with a method that builds it from the environment.

Hint: `os.environ.get("NAME", "default")` is all you need to read a variable with a
fallback. Load a local `.env` in dev with python-dotenv, but wrap the import so the code
still runs when the package isn't installed. Never put a real secret in the code. Add an
`.env.example` that shows the variable names with placeholder values, and keep the real
`.env` out of Git.

### Level 4: load the data

Write a function that reads the CSV into a list of dictionaries. If the file is missing,
fail with a clear error rather than a confusing one.

Hint: the standard library `csv.DictReader` gives you one dict per row, keyed by the
header. Use `pathlib.Path` to check the file exists first, and raise
`FileNotFoundError` with a helpful message if it doesn't.

### Level 5: the summary and the CLI

Write the summary logic: given the list of records, return the count of readings and the
count of distinct devices. Then wire a CLI around it that reads config, loads the data,
runs the summary, and prints the three lines.

Hint: a set comprehension over `device_id` gives you the distinct devices in one line;
`len` on it is the device count. Use `argparse` with a single `summary` choice so the
command is explicit. Print the environment and app name on the first line, then the two
counts. Watch the spacing in `devices :` so your output matches the target exactly.

### Level 6: the test

Write one test that proves the pipeline. It should create a small CSV in a temporary
folder, load it, summarize it, and assert the counts are what you expect.

Hint: pytest gives you a `tmp_path` fixture, a temporary directory that's cleaned up for
you. Write a few rows of CSV text into a file there, then run your load and summarize
functions against it. Assert both the number of records and the summary dict.

### Level 7: the quality gates

Run ruff and mypy in strict mode and fix whatever they flag until both are clean. Then
add a pre-commit config so they run automatically before each commit.

Hint: turn on `strict = true` for mypy in `pyproject.toml`, and set a target Python
version for ruff. Strict mypy wants your functions annotated, so give every function its
argument and return types. A `from __future__ import annotations` line at the top of each
module keeps the modern type syntax working on 3.11.

### Level 8: containerize and commit

Add a `docker-compose.yml` stub that describes the service. Then write a `.gitignore`
that keeps the environment, caches, and secrets out of the repo, and make your first
commit.

Hint: the compose file can be minimal. It just needs to be valid and name the service.
The ignore file should list at least `.venv/`, `__pycache__/`, `*.pyc`, `.env`, and the
tool caches. Then `git init`, `git add`, and one `git commit`.

## Done when

Tick every box. If one fails, that's your next task, not something to skip.

- [ ] `poetry install` completes with no errors.
- [ ] `poetry run telemetry summary` prints exactly:
  ```
  [dev] telemetry-insight
  readings: 5
  devices : 3
  ```
- [ ] `poetry run pytest -q` shows `1 passed`.
- [ ] `poetry run ruff check .` shows `All checks passed!`.
- [ ] `poetry run mypy src` shows `Success: no issues found`.
- [ ] A pre-commit config exists and its hooks run.
- [ ] A `docker-compose.yml` stub exists and is valid.
- [ ] `git log` shows one clean initial commit, and `.venv`, `__pycache__`, and `.env`
  are not tracked.

When all eight boxes are ticked, you've rebuilt the enterprise shape by yourself. That's
the win. The worked solution is in `solution-01.md` if you want to compare, but only open
it after you've tried.
