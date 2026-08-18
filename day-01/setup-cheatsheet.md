# Day 1 Setup Cheatsheet

Everything you need to get your machine ready for this program, on one page. Set up
Python first, install the tools, confirm each one, learn the handful of Poetry commands
you'll use every day, and follow the golden rules. Keep this open while you work offline.

The whole toolchain runs through Poetry. You never install project packages into the
system Python, and you never run tools with a bare `python`. It's always `poetry run`. On
Windows, do all of this inside WSL (see the prerequisite below).

---

## On Windows: set up WSL first (skip this on macOS or Linux)

This program uses Poetry, Docker, and a Linux-style toolchain. On Windows the smoothest
path by far is **WSL**, the Windows Subsystem for Linux: a real Ubuntu Linux running
inside Windows. Docker Desktop uses it as its backend, and Python, Poetry, and the tools
behave exactly as they do on Linux. Do all the setup below inside WSL, not in PowerShell.

1. Open **PowerShell as Administrator** and install WSL with Ubuntu:

   ```bash
   wsl --install
   ```

   Reboot if it asks you to.

2. Launch **Ubuntu** from the Start menu. The first time, it asks you to create a Linux
   username and password. Remember them.

3. Update the Linux packages:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. From here on, run every command in this cheatsheet inside the **Ubuntu (WSL)**
   terminal, not PowerShell. Keep your project files under your Linux home (for example
   `~/projects`), not under `/mnt/c`, so file access stays fast.

5. In VS Code, install the **WSL** extension and open your project with "Connect to WSL",
   so the editor runs against your Linux environment.

---

## 1. Set up Python

Get Python 3.11 or newer running, then confirm it. This is the first thing to get right;
the whole toolchain sits on top of it.

- **macOS:** install from python.org, or `brew install python@3.12`.
- **Linux and WSL (Ubuntu):** `sudo apt install -y python3 python3-venv`, or use pyenv to
  install and pin an exact version. You do not install system pip: Poetry manages
  packages, and each project's virtual environment ships its own pip. Keep `python3-venv`
  though, since Poetry's installer needs it to create environments on Ubuntu.
- **Windows without WSL (not recommended):** install from python.org and tick "Add Python
  to PATH" in the installer.

Confirm the version:

```bash
python3 -V
```

Expect a line like `Python 3.11.x` or newer. An older version or a "not found" message
means fix this before anything else. Managing several versions? `pyenv` installs them
side by side and pins one per project.

---

## 2. Install and confirm the rest of the tools

Install each tool, then run the confirm command. If a version prints, you're good.

**Git.** Install from git-scm.com.

```bash
git version
```

**Poetry 2.x.** This is your project and dependency manager. Install it with the
official installer (the command below works in PowerShell on Windows too), then confirm.
You may need to add Poetry's bin folder to your PATH and open a fresh terminal.

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
```

Expect `Poetry (version 2.x.x)`.

**Docker Desktop.** Get it from docker.com. It runs the local Postgres you'll use
later.

```bash
docker --version
docker compose version
```

Note the second command is `docker compose` with a space. That's Compose v2. The old
`docker-compose` with a hyphen is retired.

**An editor.** Use VS Code (the reference for this program), with two extensions:

- **Python** (`ms-python.python`): running, debugging, interpreter selection.
- **Ruff** (`charliermarsh.ruff`): lint and format as you type.

Point the editor at your project's Poetry environment so it uses the right Python. In
VS Code, open the Command Palette and run **Python: Select Interpreter**, then pick the
interpreter inside the project's virtual environment. PyCharm is a fine alternative if
you prefer a heavier all-in-one IDE.

---

## 3. The Poetry workflow

Four commands cover almost everything you'll do.

**Scaffold a new project** in the `src` layout:

```bash
poetry new --src lab01
cd lab01
```

This creates the folder, a `pyproject.toml`, a `src/` package, and a `tests/` folder.

**Install dependencies** into the project's own environment:

```bash
poetry install
```

Poetry builds the virtual environment, installs your app and dev dependencies, and
writes a `poetry.lock` with exact versions. To add a package later, use `poetry add`
for a runtime dependency or `poetry add --group dev <pkg>` for a tool.

**Run anything** through Poetry, so it uses the project environment and never the
system Python:

```bash
poetry run reviews summary
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

**Open a shell** in the environment, when you want an activated prompt:

```bash
poetry env activate
```

This prints the activation command for your shell. Note: the old `poetry shell` was
removed in Poetry 2.x, so don't reach for it. For one-off commands you don't need a
shell at all. Just prefix with `poetry run`.

---

## 4. The golden rules

These five habits prevent most of the pain beginners hit.

- **One environment per project, via Poetry.** Every project gets its own isolated set
  of packages. Projects never fight over versions.
- **Never build on the system Python.** Leave the operating system's copy for the
  operating system. Poetry manages yours.
- **Secrets come from the environment.** Read keys and connection strings from
  environment variables or a `.env` file that you never commit. Never hard-code a
  secret in the source. Share a `.env.example` template instead.
- **Commit the lockfile.** `poetry.lock` pins exact versions, direct and indirect, so
  the environment you tested is the one that runs elsewhere. Commit it. Don't commit
  `.venv`, `__pycache__`, or `.env`.
- **Let the tools run, don't skip them.** Ruff, mypy, and pytest are cheap. Run them
  often, and wire them into a gate so they can't be forgotten.

---

## 5. Quality config and the pre-commit gate

The Ruff and mypy settings live in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
strict = true
ignore_missing_imports = true
```

`strict = true` turns on the full set of mypy checks. `ignore_missing_imports = true`
keeps it quiet about third-party packages that ship no type hints.

The pre-commit hook runs those same tools before every commit. Put this in
`.pre-commit-config.yaml`:

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

Install the hook once per clone:

```bash
poetry run pre-commit install
```

From now on, `git commit` runs Ruff and mypy first. If either fails, the commit is
blocked until you fix the problem. That's the gate: bad code never reaches history.

Keep secrets and clutter out of Git with a `.gitignore`:

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

---

## 6. Readiness check

Before Day 1's lab, tick off this list:

- On Windows, WSL is installed and you are working inside the Ubuntu terminal.
- `python3 -V` shows 3.11 or newer.
- `git version` prints a version.
- `poetry --version` shows Poetry 2.x.
- `docker --version` and `docker compose version` both print a version.
- Your editor has the Python and Ruff extensions installed.
- You know the four Poetry moves: `poetry new --src`, `poetry install`, `poetry run`,
  and `poetry env activate`.

If every line checks out, you're ready to build the reviews-insight service in the
live lab.
