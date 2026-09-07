# Setup and run cheatsheet

Everything you need to get the Artificial Neural Networks introduction code running, on one page.
This is a setup-and-run guide, not a recap of the ideas. It covers how to run all four samples: the
six **concept demos**, the **live lab** (`tinynn`), and the two **assignments** that build on it.

The good news for this topic: there is almost nothing to install. Every sample is pure Python with no
third-party libraries, so everything runs fully offline. You need only Python and Poetry.

---

## 0. Prerequisites

Confirm two things are on your PATH. If either is missing, install it before you go further.

```bash
python --version    # Python 3.11 or newer
poetry --version    # Poetry (2.x is fine)
```

- **Python 3.11 or newer.** The projects declare `python = "^3.11"`.
- **Poetry.** Used to create each project's isolated environment. Install it from the official Poetry
  instructions if `poetry --version` fails.
- **Nothing else.** No PyTorch, no NumPy, no network access. The code is pure standard library on
  purpose, so you can read every weight update line by line.

---

## 1. How these projects are laid out

Each folder below is a standard Poetry project with its own `pyproject.toml`. The one-time step in every
folder is the same:

```bash
poetry install     # run once per folder, sets up that project's environment
```

After that, you run code with `poetry run <command>`, which runs inside that project's environment.

One convenience specific to this topic: because the **demos use only the standard library**, each demo
also runs with a plain `python demo_x.py`, with no Poetry environment at all. Poetry is still the
recommended path (it also gives you `ruff` and `mypy`), but the bare-Python option is there if you want
the shortest possible loop while reading the deck.

The live lab and the two assignments are `src`-layout packages, so you run them as modules with
`poetry run python -m ...`, not as loose scripts.

---

## 2. The concept demos

Six tiny, self-contained scripts, one idea each. Run them while reading the lesson at each **Try it**
note. They live in the `demos/` folder, which is its own small Poetry project.

Set up once, from inside `demos/`:

```bash
cd demos
poetry install
poetry run python demo_perceptron_or.py
```

Then run any of the six with `poetry run python <name>.py`. Here they are in lesson order:

```bash
poetry run python demo_neuron.py             # a neuron acting as OR, then as AND, by changing the bias
poetry run python demo_perceptron_or.py      # a perceptron learning OR to 100 percent (1958)
poetry run python demo_xor_fails.py          # one perceptron stuck at 75 percent on XOR (the 1969 wall)
poetry run python demo_xor_mlp.py            # a 2-2-1 network reaching 4/4 on XOR (backpropagation, 1986)
poetry run python demo_gradient_descent.py   # a good learning rate converging, a large one diverging
poetry run python demo_embeddings.py         # similar words scoring near 1.0, unrelated ones near 0.0
```

Each script is heavily commented, so open the file as you run it. The exact numbers do not matter; the
pattern is the point. `demos/README.md` and `demos/cookbook.md` have the same list with what to watch
for and what to change.

Because these are standard library only, any demo also runs without Poetry:

```bash
python demo_perceptron_or.py
```

---

## 3. The live lab: `tinynn`

A tiny neural network built from scratch in pure Python. It trains a perceptron on OR, shows it fail on
XOR, then crosses the wall with a two-layer network and backpropagation. `cd` in, install, run, test.

```bash
cd liveLab
poetry install
poetry run python -m tinynn.run     # the whole story in three lines of output
poetry run pytest                   # 8 tests
```

`poetry run python -m tinynn.run` prints three lines: the perceptron converging on OR, the same
perceptron unable to reach 100 percent on XOR, and the two-layer network reaching 100 percent on XOR.
`poetry run pytest` runs the **8 tests** (perceptron, mlp, and dataset). You can also run the checks:

```bash
poetry run ruff check src tests
poetry run mypy src
```

---

## 4. Assignment 1: the perceptron and the wall

This project carries the same `tinynn` package from the live lab, plus an `experiments` module that runs
the perceptron across AND, OR, and XOR and reports where it converges.

```bash
cd assignment01
poetry install
poetry run python -m tinynn.experiments
poetry run pytest                   # 2 tests
```

---

## 5. Assignment 2: cross the wall, and size the hidden layer

Same shape as assignment 1. Its `experiments` module solves XOR with a hidden layer and explores how
many hidden neurons it takes.

```bash
cd assignment02
poetry install
poetry run python -m tinynn.experiments
poetry run pytest                   # 3 tests
```

---

## 6. Troubleshooting

- **`poetry: command not found`.** Poetry is not installed or not on your PATH. Install it from the
  official Poetry instructions, then open a fresh terminal and check `poetry --version`.
- **The wrong Python gets picked up** (for example Poetry uses 3.9). Point the project at 3.11 with
  `poetry env use python3.11`, then run `poetry install` again. On some systems the interpreter is named
  `python3.11` or `python3`; use whichever your machine has.
- **`ModuleNotFoundError: tinynn`.** You are running a loose script instead of the module. Use
  `poetry run python -m tinynn.run` (or `-m tinynn.experiments`), from inside that project folder.
- **`pytest` reports no tests, or an import error.** Make sure you ran `poetry install` in that folder
  first, and that you are inside the correct project folder when you run `poetry run pytest`.
- **A demo prints slightly different numbers each run.** That is expected for the learning demos; the
  behaviour (converge, fail, diverge) is what to watch, not the exact figures.

---

## 7. Readiness check

You are ready when this passes cleanly:

```bash
cd liveLab
poetry install
poetry run pytest       # a green run of all 8 tests
```

A green `poetry run pytest` in `liveLab` means Python 3.11, Poetry, and the `tinynn` package are all
working, and every other sample in this topic will run the same way.
