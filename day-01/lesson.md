# Day 1 · Python in Context, and a Real Environment

> Before you write a line of application code, get two things straight: what Python
> actually is, and how a real project is set up. A demo runs once on a laptop. An
> enterprise app has to ship, survive a second year, and be handed to a team. Day 1 is
> about the second kind.

This is the master chapter for Day 1. It's self-contained, so you don't need any other
reference to follow it. The topic is simple to name and easy to underrate: Python in
context, and a real environment. Most developers skip this. They install Python, they
pip install a few things, and they start coding. Then six months later the project only
runs on one machine, nobody can rebuild it, and a version bump breaks everything. This
chapter is how you avoid all of that from the first commit.

We'll do it in three moves. First, Python in context: what it is, why you'd use it, why
you sometimes shouldn't, and how the runtime really behaves. Second, the target and the
toolchain: what production actually looks like, brought early so you build toward it, and
the modern tools that make a project reproducible. We standardize on **Poetry**, wire in
a **quality gate** that blocks bad commits, and see **containers** for real dev and prod
parity. Third, the build: a real starter project, the reviews-insight service skeleton,
with every file quoted and every command verified.

Throughout, watch for the **enterprise lens**. After each big idea, there's a short note
on why it matters for an app that has to scale and be handed to a team. That's the thread
that ties the whole day together, and it's the whole point of Day 1: a real environment,
a locked dependency graph, an enforced quality gate, and container parity are what
separate a system that ships from a demo that ran once.

## Objective

After this chapter you can:

- Explain what Python really is: how it compiles to bytecode and runs, and where it fits.
- Say honestly when Python is the right tool and when it isn't, and explain the GIL.
- Describe what production actually looks like, and why it differs from your laptop.
- Say why pip and `requirements.txt` fall short, and use Poetry with a committed lockfile.
- Name the isolation tools (Poetry, conda, pyenv, uv) and say when each one fits.
- Wire a quality gate (ruff and mypy through pre-commit) that blocks a bad commit.
- Build and run the reviews-insight skeleton with Poetry, run its command, pass its test.

You don't need to memorize commands. You need a clear picture of the machine, a project
layout you can trust, and a toolchain that keeps you honest.

## Coverage

Day 1 has three levels:

1. **Python in context.** What Python is, how it runs, why AI runs on it, and the honest
   trade, including a clear GIL explainer.
2. **The target and the toolchain.** What production really is, then Poetry, the quality
   gate, containers, project structure, config, and Git. Dev now, prod in mind.
3. **The build.** Walk the reviews-insight skeleton file by file, build it with Poetry,
   run it, test it, lint it, type check it, and guard it with a commit hook.

At the end there's a recap, a pointer to the live lab, and two offline assignments.

## Level 1: Python in context

### 1.1 Where Python fits, and why you'd use it

Python is a general purpose language that wins in a specific way: it's where
**engineering time is the scarce resource**. It reads almost like English, it has a huge
standard library, and it has the deepest third party ecosystem of any language for data
and AI. You reach for Python when you want to go from an idea to a working thing fast, and
when the heavy number crunching, if there is any, can be handed off to fast libraries.

The places Python genuinely shines:

- **AI, machine learning, and data science.** This is home turf. NumPy, pandas,
  scikit-learn, and the deep learning frameworks all live here.
- **Automation, scripting, and glue.** Tying systems together and moving data between
  tools. Often the shortest path from a problem to a working script.
- **Web and API backends.** Mature frameworks serve real traffic, especially where the
  bottleneck is input and output, not raw computation.
- **Data engineering pipelines.** Extract, transform, load. The exact work this program
  is about.
- **Prototyping and research.** When the goal is to find out whether an idea works at all,
  Python's speed of iteration is hard to beat.

The common thread: Python is the calm, readable surface, and the fast work happens in
libraries underneath.

**Enterprise lens.** Engineering time is the most expensive thing in a company, more than
servers. A language that lets a team ship and change software quickly is worth a lot, even
if it's slower per line than C. For an app that has to keep evolving for years, the speed
that matters is the speed of the next change, not the speed of one loop.

### 1.2 Why NOT Python: the honest trade

A senior engineer is known as much for what they refuse to build in a tool as for what
they build. Python is a great general purpose language, not a universal one. Be honest
about where it's the wrong choice:

- **Hard real time and very low latency.** When a response has to arrive within
  microseconds every single time, an interpreted language with a garbage collector is the
  wrong base. Think trading cores or engine control units.
- **CPU bound work that must use all cores in one process.** In standard Python, a single
  lock (more on it in 1.6) lets only one thread run Python code at a time. There are
  workarounds, but if saturating all cores in one process is the whole point, pick another
  language.
- **Systems programming.** Operating systems, device drivers, and firmware need low level
  control Python doesn't offer.
- **Mobile and browser front ends.** Other languages own those runtimes.
- **Tiny or memory constrained devices.** Standard Python's footprint is too big, though
  MicroPython fills that niche.

None of these are Python failing. They're mismatches. Wrong tool for the job, not a broken
tool.

The move that makes most of Python's weaknesses disappear in practice: **Python is the
orchestration layer that calls fast native code for the heavy work.** You write the
readable high level logic in Python, and the numeric inner loops run in C, C++, or CUDA
under the hood, exposed as Python libraries. When you multiply two large arrays with
NumPy, almost no time is spent in Python. So "Python is slow" always deserves the
follow-up: slow for what, and can the hot part be handed to a library that isn't slow at
all?

It helps to place Python on a stack, from the metal up:

| Level | Languages | What lives here |
| --- | --- | --- |
| Hardware and CPU | machine code | The processor understands only binary instructions. |
| Operating system and drivers | C, C++, Rust | Compiled straight to machine code, manual memory control. Ultra low latency and embedded systems. |
| Virtual machine and JIT | Java, C#, Go | Compiled to bytecode, run on a managed runtime. High concurrency backends. |
| Interpreted and scripting | Python, Ruby, JavaScript | Highest abstraction, memory managed for you. Built for developer speed and for gluing the layers below. |

Python sits at the top and reaches down. That's its whole character: it isn't the fastest
layer, it's the layer that commands the fast ones.

**Enterprise lens.** Knowing the weak spots is not pessimism, it's risk management. If one
part of your system truly needs microsecond latency or full core saturation, you plan for
it early: a native module, a separate service in another language, or a queue of worker
processes. Discovering that limit in production, under load, is how outages happen.

### 1.3 What Python actually is: compiled to bytecode, then interpreted

People argue about whether Python is "compiled" or "interpreted" as if it must be one. The
real answer is both, in a specific way: **Python is compiled to bytecode, then interpreted
by a virtual machine.**

When you run a program, the interpreter first compiles your source into **bytecode**, a
compact, lower level instruction set that is not tied to your specific processor. It then
hands that bytecode to a **virtual machine**, a loop written in C that runs the bytecode
one instruction at a time. So there is a compile step, but it's quick, automatic, and
invisible. And the thing that finally runs is an interpreter loop, not your processor
directly.

This one fact explains a lot. The fast startup and the interactive feel come from the
light compile step. The runtime cost, Python being slower than C on a tight numeric loop,
comes from the interpreter loop running bytecode instead of the processor running machine
code. It also explains a folder you'll see everywhere: the first time a module is
imported, its compiled bytecode is cached in a `__pycache__` folder as a `.pyc` file so
the next run can skip the compile step. Those files are safe to delete and belong in your
ignore file, not in version control.

**Enterprise lens.** This is the honest picture of why your code starts fast but crawls in
a tight loop, and it points at the real fix: move hot work into compiled libraries rather
than tuning Python line by line. For a service that must scale, you profile, find the hot
path, and hand it to native code. You don't rewrite the whole thing in a faster language
out of panic.

### 1.4 CPython versus the language, and why you pin the version

Here's a distinction most developers miss: **the Python language and the Python program
you install are not the same thing.** Python is a specification, a document that says how
the language should behave. When you download Python from python.org, you get **CPython**,
the reference program that runs Python code, written in C. Almost everyone uses it, but
it's not the only one.

| Implementation | Written in | Why it exists |
| --- | --- | --- |
| CPython | C | The reference. What you get by default. Widest library support. |
| PyPy | Python (RPython) | A just in time compiler for much faster pure Python. |
| Jython | Java | Runs Python on the Java Virtual Machine. |
| IronPython | C# | Runs Python on the .NET runtime. |
| MicroPython | C | A tiny Python for microcontrollers and embedded devices. |

In this program, "Python" means CPython 3.11 or newer. When your code is slow, it's
CPython that's slow, not "Python", and sometimes another implementation runs the same code
faster. CPython's real superpower is its C interface: it can call into C and C++ libraries
directly, which is exactly why the AI and data stack chose it. More on that in 1.7.

Now the version itself. A version like `3.11.5` has three parts. The first two, `3.11`,
are the language level, and each new minor level (3.11, 3.12, 3.13) is effectively a
slightly different language, with new features and the occasional removal. The third part,
`5`, is a patch release with bug and security fixes only, and it's always safe to take the
latest. Python 2 is a separate, retired language.

You **pin the version** so every person and every machine runs the exact same language
level. You declare it once, for example in `pyproject.toml` where Poetry reads it as
`python = "^3.11"`, and everyone uses it instead of guessing. Two tools solve two different
halves of the version problem, and you use both: a **version manager picks which
interpreter** (pyenv on macOS and Linux, the `py` launcher or pyenv-win on Windows), and a
**project manager isolates and locks which packages** (Level 2).

**Enterprise lens.** An unpinned version is a time bomb. The app runs today on 3.11,
someone rebuilds next year on 3.13, a dependency behaves differently, and now a bug shows
up in production that nobody can reproduce locally. Pinning the version is the cheapest
insurance you'll ever buy for a system that has to last.

### 1.5 Memory is managed for you

You never call `free` in Python. Two mechanisms handle memory together, and knowing them
at a high level is part of the engineer's model.

- **Reference counting.** Every object keeps a count of how many names and containers
  refer to it. When the count reaches zero, the object is destroyed and its memory freed
  right away. Simple, predictable, and most of what keeps memory in check.
- **The cyclic garbage collector.** Reference counting alone can't free a **cycle**, where
  object A refers to B and B refers back to A. A separate collector runs now and then to
  find and free those unreachable cycles.

In practice most objects are freed the instant they're no longer used, which is why Python
memory usage is usually fine without effort. But you can still leak memory by holding
references you forgot about: a growing cache, a global list, a closure that captures a
large object.

**Enterprise lens.** It tells you why you never free memory by hand, and, more usefully,
how you can still leak it. That's the difference between a service whose memory stays flat
for months and one that grows until it falls over at 3am.

### 1.6 The GIL, and why threads don't speed up CPU work

Here is the single most important runtime fact about CPython: the **Global Interpreter
Lock**, or GIL. It's a single lock inside the interpreter, and it lets **only one thread
run Python bytecode at a time**. The lock keeps the interpreter simple and makes single
threaded code fast, but it shapes how you get work done in parallel, so learn it now.

The key is to split work into two kinds:

- **I/O bound work** spends most of its time *waiting*: for a network reply, a database
  query, a file to read. While a thread waits, it releases the GIL, so other threads run.
  For this kind of work, **threads help**. You can have many requests in flight at once,
  each mostly waiting.
- **CPU bound work** spends its time *computing*: crunching numbers, parsing, transforming
  data. Only one thread can hold the GIL and run Python at a time, so adding more threads
  does **not** speed it up. They just take turns on the one lock, and can even slow things
  down from the overhead of switching.

So how do you use all your cores for heavy computation? You **use processes, not threads**.
Python's `multiprocessing` starts separate processes, each with its own interpreter and
its own GIL, and they run truly in parallel. The other escape hatch is native code: a
library like NumPy releases the GIL while it runs its C loops, so the heavy work happens
outside the lock entirely.

A quick way to remember it: **threads for waiting, processes for computing.**

**Enterprise lens.** This explains a real and expensive mistake. A team notices a data job
is slow, adds a thread pool, and sees no speedup or a slowdown, because the job was CPU
bound and the GIL let only one thread compute at a time. Knowing the split up front tells
you the right tool: a process pool for the heavy transform, threads for the many small
waits on a network or database.

### 1.7 Why AI and data run on Python

Python's dominance in AI and data isn't fashion. Several forces built up over time, and
together they're hard to unseat:

- **A native accelerated numerical core.** NumPy gave Python a fast, memory efficient
  array backed by native code, and a whole ecosystem grew on top: pandas for tables,
  scikit-learn for classical machine learning, and the deep learning frameworks. Data code
  reads like Python but runs like C. This is CPython's C interface from 1.4, paying off.
- **A glue language for a mixed stack.** Modern AI mixes C, C++, CUDA, and specialized
  hardware. Python is the calm surface that ties them together, which is why the frameworks
  chose it as their front end even though their engines are native. The GIL barely matters
  here, because the heavy loops release it and run in native code.
- **Readability for a mixed audience.** Much of this work is done by people whose first
  expertise is statistics, science, or a domain, not software engineering. Python's clarity
  lowers the barrier, and research code becomes shareable code.
- **The notebook workflow.** Exploratory data work is a back and forth with the data: try
  something, see a number or a chart, adjust. Notebooks make that loop natural.
- **The network effect.** The tutorials, models, courses, and new research releases are
  Python first. The frontier model providers ship Python software development kits first.
  The pull feeds itself.

The honest summary: Python is rarely the fastest language for a single task, but it's the
one where the whole pipeline, from a quick experiment to a served model, is smoothest.

**Enterprise lens.** A deep ecosystem is a hiring and maintenance advantage. You can staff
a Python data team, and almost any problem you hit has an answer and a library already. For
a system that must be handed to a team and kept alive for years, "boring and well
supported" beats "clever and niche" almost every time.

## Level 2: The toolchain, dev now and prod in mind

You have the machine. Now the toolchain. There is not one "Python" you install and you are
done. There is a small stack of tools, each doing one job, from the editor you type in at
the top down to the container that runs your code at the bottom. This level maps that stack
first, then sets it up from the top down, starting at the IDE and working toward the
runtime. And it does all of it with one eye on production, because almost every setup choice
only makes sense once you have seen what development is building toward.

### 2.1 The Python ecosystem: a stack of tools, by job

Before installing anything, get the map. Here is the toolchain by function, from the surface
you touch down to what actually runs your code:

| Layer (what it does) | Tool you will use | Its job |
| --- | --- | --- |
| Where you work | VS Code (or PyCharm) | write, navigate, and debug code |
| Code quality | ruff, mypy, pre-commit | keep code correct, typed, and consistent |
| Dependencies and the project | Poetry | declare and lock what the project depends on |
| Native and GPU libraries | conda or mamba | install system C, CUDA, and BLAS that pip cannot |
| Environment isolation | venv | keep each project's packages separate |
| Python versions | pyenv | install and pin the interpreter version |
| The interpreter | CPython | actually runs your bytecode |
| Package and ship | Docker | one image that runs the same everywhere |

None of this is busywork. Each tool is here because a real thing breaks without it, and we
set them up in this order, top to bottom. At each layer, note one thing: how development and
production differ. That contrast is the reason the choices are what they are, so we look at
it next.

### 2.2 Development and production are two different worlds

A script on your laptop and a service in production are not the same thing running on a
bigger machine. They are different worlds, and the differences drive every setup choice
below. Here is the honest picture of production:

- **Immutable and ephemeral.** The app runs inside a container built from a fixed image. You
  **cannot SSH in to fix a file**. If a container misbehaves, the orchestrator destroys it
  and starts a fresh one from the same image. Anything written to its local disk is gone the
  moment it restarts. State lives in a database or object store, never on the container.
- **Orchestration and autoscaling.** A system like Kubernetes or a managed container service
  decides how many copies of your app run. When traffic spikes it starts more copies across
  more machines, and when traffic falls it stops them. Your app has to be fine with many
  identical copies running at once, and with any one of them vanishing.
- **Structured logging.** Nobody is watching your terminal. There is no terminal. Your app
  emits logs as structured records, usually JSON, that stream to a central system where a
  team searches and alerts on them. A bare `print` is invisible in that world.
- **No dev tools inside.** The production image carries only what it needs to run. The
  linter, the formatter, the type checker, the test runner: all of those ran earlier, in the
  pipeline, and none of them ship in the image.
- **CI and CD gates.** Code does not reach production because someone copied it to a server.
  It reaches production only after passing automated gates: the tests run, the linter and
  type checker pass, the image builds, and only then does it deploy. Continuous integration
  is the checking, continuous delivery is the shipping.

**Enterprise lens.** Every one of these constraints is a design instruction you can act on
today. Immutable and ephemeral means read config from the environment, not a file you plan
to edit later. Autoscaling means do not keep important state in a local variable across
requests. Structured logging means reach for a logger, not `print`. CI and CD gates mean the
quality tools below are not optional polish, they are the gate your code has to clear to
ship. Keep this picture in view as we set up development, because each dev tool below has a
matching production reality.

### 2.3 The IDE: where you work

Start at the top of the stack, the editor. This is where you spend your day, so it is worth
setting up once, well.

- **VS Code** is the common enterprise choice: free, light, and highly extensible, with
  Remote SSH and Dev Containers that let you edit locally while your code runs on a remote
  GPU box. **PyCharm** is a heavier, Python-purpose-built IDE with deep inspection; it is a
  fine choice, just heavier.
- **Extensions do the real work**, and it helps to name them by job: the **Python** extension
  for language support and running code, **Ruff** for lint and format on save, **mypy**
  (through Pylance or the mypy extension) for type feedback as you type, and **Jupyter** for
  notebooks. An AI assistant is optional.
- **Commit the team settings.** A `.vscode/settings.json` in the repository makes everyone's
  editor behave the same: format on save with Ruff, and point at the project's own
  interpreter. New teammates get the house behaviour for free, without configuring anything.

**Enterprise lens.** The IDE is a pure development tool. Production has no editor, no
format-on-save, no debugger attached. Everything the IDE does for you has to be reproduced by
tools that run without it: the formatter and type checker as a commit gate and in CI, the
interpreter and dependencies baked into an image. The editor makes you fast; it is not what
keeps the system correct. That job belongs to the layer right below it.

### 2.4 Code quality: ruff, mypy, and the pre-commit gate

Level 1 named a cost of Python: many mistakes show up at runtime rather than at a compile
step. The quality gate is how you buy those guarantees back, and it is three tools working
together, sitting right under the editor.

- **ruff** is a linter and formatter written in Rust. A linter flags mistakes and bad
  patterns (an unused import, a variable you never use); a formatter rewrites your code to one
  consistent style (line length, quotes, spacing) so nobody argues about it. Ruff is so fast
  it runs on every save without you noticing, and it replaces a stack of older tools (flake8
  for linting, black for formatting, isort for import order) with one.
- **mypy** is a static type checker. Python lets you annotate types, and mypy reads those
  annotations and checks that your code actually respects them, **without running it**. In
  **strict mode**, which this program uses, it insists every function is typed and catches a
  whole class of bugs (a wrong type passed, a `None` you did not handle) before the code ever
  runs.
- **pre-commit** is the enforcer. It is a framework that runs checks **before** a `git
  commit` is allowed to complete. You list ruff and mypy as hooks, install it once, and from
  then on every commit runs them. If ruff finds a problem or mypy finds a type error, the
  commit is **blocked**. You fix the issue, commit again, and it passes.

That last piece is what turns good intentions into a guarantee. A linter you have to remember
to run is a linter you will forget. A linter wired into the commit means broken code
physically cannot enter the repository. You will see this happen for real in Level 3: we
introduce a type error, the commit is refused by the mypy hook, we fix it, and the commit
goes through.

**Enterprise lens.** This is the same gate the CI pipeline runs, just moved earlier, onto
your machine, so problems are caught in seconds instead of minutes after a push. A repository
where every commit has passed the same ruff and mypy checks stays uniform no matter how many
people touch it. New engineers do not have to learn the house style, the tools enforce it,
and code review can be about design instead of spacing.

### 2.5 Dependencies and the project: Poetry, not pip

Under the tools sits the project itself: what it depends on, and how those dependencies are
pinned. When you need code you did not write, you install a package. **pip** is the default
installer, pulling from the **Python Package Index (PyPI)**. For years the common way to
record a project's needs was `pip freeze > requirements.txt`. It works, but it has a real
weakness.

The problem is **transitive dependencies**. Your app declares it needs package A. A needs B,
and B needs C. You never asked for B or C, but they get installed. A plain `requirements.txt`
mixes the packages you chose with the ones they dragged in, with nothing to tell them apart,
and often does not lock them. So when B ships a new version next month with a subtle bug, a
fresh install quietly picks it up, your build changes under you, and "it worked yesterday"
becomes a debugging session.

What you actually want is two separate things: a file where you **declare** the handful of
packages you truly depend on, and a file that **locks** the exact resolved version of every
package in the whole graph, direct and transitive. `requirements.txt` blurs those two jobs
into one.

**Poetry** is the standard tool for this program, and it keeps the two jobs in two files:

- **`pyproject.toml`** holds your **declared** dependencies: the packages you chose, with
  version ranges you allow. You edit it, or let `poetry add` edit it.
- **`poetry.lock`** holds the **exact resolved graph**: every package, direct and transitive,
  pinned to one version with a checksum. Poetry generates it, you never edit it by hand, and
  you **commit it to Git**. That committed lockfile is what makes an install repeatable on
  every machine and every deploy.

The daily workflow is small, and on Poetry 2.x you run project commands through it:

```bash
poetry add python-dotenv          # add a dependency, update pyproject.toml and the lock
poetry add --group dev ruff mypy  # add tools to the dev group, not the shipped deps
poetry install                    # create the venv and install the exact locked graph
poetry run pytest -q              # run a command inside the project's environment
```

Two Poetry 2.x notes that trip people up. You run tools with `poetry run <cmd>`, which
executes inside the project's environment without activating anything. If you do want an
activated shell, the command is now `poetry env activate`; the old `poetry shell` was
removed, so do not reach for it.

One line on the alternative: **uv**, from Astral, written in Rust, does the same
declare-and-lock job much faster and is gaining ground quickly. We use Poetry here because it
is mature and widely taught, and the concepts carry straight over to uv.

**Enterprise lens.** A committed lockfile is the line between "we can rebuild this exactly"
and "we hope it still builds". When a security patch drops, or you need to reproduce a bug
from three months ago, the lock rebuilds the precise environment that was running. Splitting
declared deps from the locked graph also means a human reads a short, honest list in
`pyproject.toml`, while the machine trusts the exact graph in the lock. A company treats
dependencies as a controlled input, not something that drifts between one deploy and the next.

### 2.6 conda versus pip: a different problem

New engineers get confused about when to use conda instead of pip or Poetry, so here is the
clean rule: they solve different problems.

- **pip and Poetry install Python packages.** They pull Python code (as wheels) from PyPI.
  When a package needs a bit of compiled C, it usually ships a prebuilt wheel and you never
  notice. This covers the large majority of projects, including everything in this program.
- **conda installs system level things pip cannot.** Some data and AI libraries lean on heavy
  native pieces: CUDA drivers for a GPU, BLAS for fast linear algebra, GDAL for geospatial
  work. Those are not Python, they are system C and C++ libraries, and pip has no way to
  install them. **conda is an operating system level package manager** that installs Python,
  the packages, and those underlying native libraries together in one isolated environment.

So the rule is: use Poetry by default, and reach for conda only when the wheel is not enough,
meaning you need a native stack (a particular CUDA, a specific BLAS) that pip cannot provide.
A few names you will meet there: **Miniconda** is the small install with just the package
manager and Python. **Mamba** is a much faster reimplementation of conda's solver in C++.
**Micromamba** is a tiny standalone version that does not even need a base Python to run. Same
idea, tuned for speed.

**Enterprise lens.** Picking the right manager is picking the right problem. Most services
never touch conda, and using it "just in case" drags in a heavier environment than they need.
But a GPU training job that needs an exact CUDA and BLAS will fight pip forever, and conda
solves it cleanly. Knowing which world you are in saves a team days of dependency pain.

### 2.7 pyproject.toml, the single source of truth

Python projects used to scatter configuration across a pile of files in the root: `setup.py`
for packaging, `setup.cfg`, `.flake8` for the linter, `tox.ini`, and more. A standard, PEP
518, replaced that mess with one file: **`pyproject.toml`**. It is now the single source of
truth for a project, and it holds three kinds of thing in one place:

- **Metadata.** The project's name, version, and description.
- **Dependencies.** What the project needs to run, and a separate dev group for the tools it
  needs only while you build it.
- **Tool configuration.** The settings for your quality tools, ruff and mypy and pytest, live
  under their own `[tool.*]` tables in the same file, instead of one dotfile each.

You will see all three in the reviews-insight `pyproject.toml` in Level 3: the Poetry
metadata and dependency groups, the console command, and the `[tool.ruff]` and `[tool.mypy]`
tables that configure the gate.

**Enterprise lens.** One declarative file that every Python tool understands is what lets a
new teammate or a build server set the project up without tribal knowledge. There is no
README step that says "and also configure the linter like this". The project describes
itself, top to bottom, in a format the whole ecosystem reads.

### 2.8 Isolation and the interpreter: venv and pyenv

Two layers sit below the package manager: the isolated environment your packages live in, and
the interpreter version that runs them.

- **A virtual environment (venv)** is an isolated, per-project set of packages, separate from
  the system Python and from every other project. This is why upgrading one project cannot
  break another. You do not create it by hand in this program: **Poetry creates and manages a
  venv for each project** and installs the locked graph into it. The rule that never changes:
  never install project packages into the system Python.
- **pyenv** installs and switches Python versions. Different projects can need different
  versions, and you should not depend on whatever the operating system happens to ship. You
  pick a supported version on purpose (this program uses 3.11 or newer) and pin it, so every
  machine runs the same interpreter.

**Enterprise lens.** Isolation and a pinned version are the same reproducibility idea from
two angles. In development, a venv per project plus a pinned interpreter means "works on my
machine" actually means something. In production, the container is the isolation: it carries
one exact Python and one exact set of packages, and nothing else on the host can interfere.
Dev and prod agree because both pin the same two things.

### 2.9 Containers, and why prod differs

At the bottom of the stack is the container, and it is what makes development and production
genuinely the same. A virtual environment isolates packages on one machine. A **container**
goes further: it packages the interpreter, the dependencies, and your code into one **image**
that runs the same on any machine. This is how you get real parity, and how "but it works on
my machine" finally goes away.

Two words carry the idea:

- An **image** is a built, read-only snapshot in layers: a base operating system, a specific
  Python, your dependencies, and your code.
- A **container** is a running instance of an image, isolated from the host. This is the
  immutable, ephemeral unit from the production picture above.

For local development you often need more than the app: a database, a cache, a message queue.
**Docker Compose** declares those supporting services in one file and starts them together.
The reviews-insight project ships a small `docker-compose.yml` that defines a Postgres
database, so your laptop runs the same database engine production will:

```bash
docker compose up -d
```

The `-d` runs it in the background. On Day 1 the app itself does not need the database yet, it
reads a CSV, so this is here for you to see and to have ready, not because today's code
touches it. It is the shape of things: your environment includes its dependencies as real
services, not "install Postgres by hand and hope it matches prod".

**Enterprise lens.** Production is not development on a bigger machine. Development optimizes
for a fast, honest inner loop: quick feedback, live edits, a REPL. Production optimizes for
reproducibility, security, and reliability: the exact image, no secrets baked in, no dev tools
inside. A Compose file that runs the same Postgres version as production means a query that
works on your laptop works on the server, and the class of "it behaved differently in prod"
bugs shrinks. That parity is worth building toward from Day 1, even before today's code needs
the database.

### 2.10 Project structure that scales

A demo is one `app.py`. A real project has a shape, because a shape is what lets it grow and
be handed over. The layout below is the one the reviews-insight project uses, and it's the
one to reach for:

```
reviews-insight/
  pyproject.toml           # metadata, declared dependencies, and tool config
  poetry.lock              # the exact resolved dependency graph, committed
  .gitignore               # what never gets committed
  .env.example             # a template for local config, safe to commit
  .pre-commit-config.yaml  # the commit gate: ruff and mypy hooks
  docker-compose.yml       # supporting services, a Postgres database
  src/
    reviews_insight/       # the actual package, importable code
      __init__.py
      config.py            # settings, read from the environment
      data.py              # data loading
      cli.py               # the command line entry point
  tests/
    test_summary.py        # automated tests, kept separate from the code
  data/
    reviews_sample.csv     # sample data
```

Four ideas are doing the work here:

- **A `src/` layout.** The importable code lives under `src/`, in a package folder. This
  isn't decoration. It stops accidental imports of your code before it's installed, so the
  tests exercise the package the same way a user would, installed. It's the layout that
  catches packaging mistakes early, and it's what `poetry new --src` gives you.
- **Tests are separate.** `tests/` sits beside the source, not inside it. Tests are a first
  class part of the project, not an afterthought, and keeping them separate keeps the shipped
  package clean.
- **Config is its own module.** `config.py` is the one place settings are read. Nothing else
  in the code reads the environment directly.
- **Everything is declared.** `pyproject.toml` says what the project is and what it needs,
  `poetry.lock` pins the exact graph, and the dotfiles declare the gate and the services.

**Enterprise lens.** Structure is how a project survives being handed to a team. A new
engineer can look at this layout and know, without asking, where the code is, where the tests
are, how config is read, and what has to pass before a commit. A flat pile of scripts with no
shape is readable only by the person who wrote it, and only until they forget. Structure is
documentation that can't go stale.

### 2.11 Config and secrets from the environment, not the code

Never hard code settings, and never, ever commit secrets. Configuration that changes between
environments (a database URL, an API key, which data file to read) comes from **environment
variables**, read in one place, so the same code runs in dev, test, and prod with only the
environment changing.

The pattern the project uses: a `config.py` module reads environment variables into a small,
frozen settings object. In dev, a local `.env` file (which is never committed) supplies those
variables for convenience. In prod, the real environment or a secrets manager supplies them,
which is exactly the immutable, ephemeral world from the production picture above where there
is no file to edit. You commit a `.env.example` as a template so a new developer knows which
variables exist, without ever seeing a real secret.

This is why the ignore file lists `.env`. The template is safe to share; the real file never
leaves the machine.

**Enterprise lens.** A secret committed to Git is a secret leaked, permanently, because Git
remembers everything. Reading config from the environment is also what lets one build
artifact, one image, run in every environment: you don't rebuild to move from staging to
prod, you just change the environment it runs in. That single-artifact discipline is the
backbone of a reliable deployment pipeline.

### 2.12 Git from the first commit

Every project in this program lives in a Git repository, and it starts as one before there's
much to commit. Git is how you track changes, work with others, and recover from mistakes, and
it's what the CI and CD gates from the production picture above hang off. The habit to form: a
repository from the first commit, a sensible `.gitignore`, the pre-commit gate installed
early, and small, frequent commits.

The starting moves are short flags, nothing fancy:

```bash
git init
git add .
git commit -m "initial project setup"
```

The `.gitignore` is what keeps the repository honest. It lists everything that should stay
local: the virtual environment, the bytecode cache, the tool caches, the build output, and
the secrets file. Commit the description of the environment (the `pyproject.toml`, the
`poetry.lock`), never the built result (the `.venv`).

**Enterprise lens.** Version control isn't paperwork, it's the safety net that lets a team
experiment without fear. Starting from the first commit means the whole history is there:
every change is attributable, revertable, and reviewable. Wire the pre-commit gate in early
and that history is also clean, because nothing that fails the checks ever made it in.


## Level 3: The build, the reviews-insight skeleton

Now build a real thing. Not a demo, a **skeleton for an enterprise app**: a reviews-insight
service that will eventually load product reviews and report on them. Today it does one
small, honest thing, but it's shaped correctly, with a lockfile, a quality gate, and a
database service ready, so every later feature has a clean place to live. Every file below
is real and verified. We'll scaffold it with Poetry, walk each file, then run it, test it,
lint it, type check it, and guard it with a commit hook.

### 3.1 Scaffold with Poetry

Poetry can create the whole `src/` layout for you. From the folder where your projects live:

```bash
poetry new --src reviews-insight
cd reviews-insight
```

The `--src` flag is what asks for the `src/` layout from 2.10. That gives you the package
folder under `src/`, a `tests/` folder, and a starter `pyproject.toml`. Next you replace
that starter `pyproject.toml` with the verified content below, then let Poetry resolve and
install everything.

### 3.2 `pyproject.toml`, the project's identity card and its config

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

This one file is the single source of truth from 2.7. Read it top to bottom:

- `[tool.poetry]` holds the metadata and, in `packages`, tells Poetry the importable code
  lives in `reviews_insight` under `src/`. That line is what makes the `src/` layout build.
- `[tool.poetry.dependencies]` is the **declared** runtime list, and it's short on purpose:
  `python = "^3.11"` is the version pin from Level 1, and `python-dotenv` loads the local
  `.env` in dev. A short, honest dependency list is a feature, not a shortcoming.
- `[tool.poetry.group.dev.dependencies]` is the dev group: ruff, mypy, pytest, and
  pre-commit. These are the tools you build with, and they're kept separate from the runtime
  deps so they never ship in the production image, exactly the split from 2.2.
- `[tool.poetry.scripts]` says: create a console command called `reviews` that runs the
  `main` function in `reviews_insight.cli`. After install, `reviews` is a real command. That's
  how a proper tool ships, not as `python some/path/script.py`.
- `[tool.ruff]` and `[tool.mypy]` configure the gate right here in the same file. Ruff gets a
  line length of 88 and targets Python 3.11. Mypy runs in `strict = true`, the strict mode
  from 2.4 that demands full typing.
- `[build-system]` says how to build the project, using `poetry-core`.

**Enterprise lens.** Everything about how this project is built, installed, run, and checked
is declared in one standard file that every Python tool understands. The declared deps read
as a short human list, while `poetry.lock` (generated next) carries the exact graph. There's
no separate config dotfile for the linter or the type checker to drift out of sync.

### 3.3 Install and lock

With the real `pyproject.toml` in place, let Poetry resolve the whole graph, write the
lockfile, create the virtual environment, and install everything, including your own package
in editable form:

```bash
poetry install
```

That one command creates `poetry.lock`, the exact resolved graph from 2.5, which you then
commit alongside `pyproject.toml`. From here on you don't activate anything by hand; you run
project commands with `poetry run`, and Poetry uses the project's environment.

**Enterprise lens.** `poetry install` against a committed lock is the same operation your
build server runs, so the environment on your laptop and the one in the pipeline are built
from the identical pinned graph. That's reproducibility you can point at, not hope for.

### 3.4 `.gitignore`, what never gets committed

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

Small file, big job. It keeps out the environment (`.venv/`), the bytecode cache
(`__pycache__/`, `*.pyc`), the secrets (`.env`), the build output (`dist/`), and the caches
the quality tools leave behind (`.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`). Every line
is something that is either rebuildable, machine specific, or secret. None of it belongs in
version control. Note what's *not* here: `poetry.lock` is committed, because it's the
description of the exact environment, not a throwaway.

**Enterprise lens.** The ignore file is the first line of defense against the single most
common serious mistake in a young project: committing a secret. Getting it right on Day 1,
before there's a real `.env` to leak, is far easier than scrubbing a secret out of Git
history after the fact.

### 3.5 `.env.example`, the config template

```
APP_NAME=reviews-insight
APP_ENV=dev
DATA_PATH=data/reviews_sample.csv
DATABASE_URL=postgresql://reviews_admin:change_me_in_prod@localhost:5432/reviews_db
```

This is committed on purpose, because it holds no real secrets, only the names of the
settings the app reads and safe example values. A new developer copies it to `.env`, adjusts
as needed, and their real `.env` is ignored by Git. The `DATABASE_URL` line points at the
Postgres from the Compose file, so the template already documents how the app will reach its
database, even though today's code doesn't use it yet. The placeholder password says
`change_me_in_prod` for a reason: an example value is never a real credential.

**Enterprise lens.** The example file answers "what do I need to set to run this?" without a
conversation. When the real config includes an actual database password or API key, the
template shows the variable exists while the real value stays in the environment that needs
it. That's the whole config-from-environment pattern made concrete.

### 3.6 `src/reviews_insight/__init__.py`, the package marker

```python
__version__ = "0.1.0"
```

One line, two jobs. Its presence makes `reviews_insight` a real importable package. And it
records the version in code, matching the one in `pyproject.toml`, so the running program can
report its own version.

**Enterprise lens.** A program that can report its own version is a program you can debug in
production. When something misbehaves, the first question is always "which version is
running?", and this is where the answer lives.

### 3.7 `src/reviews_insight/config.py`, settings from the environment

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

This is the config-from-environment pattern from 2.11, made real. Walk it:

- The `try` block loads a local `.env` file if `python-dotenv` is installed, and shrugs if it
  isn't. That's the point of the comment: in dev the `.env` file is a convenience; in prod the
  real environment variables are already set, so dotenv isn't even needed. The same code works
  in both places.
- `from __future__ import annotations` lets the method annotate its return as `Config` cleanly,
  and it's the small touch that keeps mypy strict mode happy.
- `Config` is a **frozen dataclass**, so once built, its values can't be changed by accident.
  Settings should be read once and stay put.
- `from_env` reads each setting from the environment, with a sensible default if it's missing.
  Every environment variable is read here and nowhere else.

**Enterprise lens.** One config module is the difference between settings you can reason about
and settings scattered through the code as `os.environ` calls nobody can find. When the app has
forty settings and runs in four environments, this single, frozen, one-place pattern is what
keeps configuration from becoming a source of production surprises.

### 3.8 `src/reviews_insight/data.py`, loading data with a clear failure

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

The data layer, kept deliberately small and honest:

- It uses `pathlib.Path`, the modern way to handle file paths, which works the same on Windows
  and Linux.
- It checks the file exists first and **raises a clear error** if it doesn't. A missing data
  file produces `data file not found: <path>`, not a cryptic stack trace. Failing clearly is a
  feature.
- It reads the CSV with an explicit `encoding="utf-8"`, never leaving the encoding to chance.
- The return type is spelled out fully: `list[dict[str, str]]`. The comprehension coerces every
  value to `str` so the data genuinely matches that annotation, which is what lets mypy strict
  mode sign off. The type isn't decoration, the code makes it true.

**Enterprise lens.** The clear error message is the enterprise touch. When this runs on a
server at 2am and the data file is missing, the log says exactly what's wrong. Explicit
encoding matters for the same reason: a system that has to run for years will eventually meet a
file with an accented character in it, and "it depends on the machine's default encoding" is
how you get a bug that only appears on one server.

### 3.9 `src/reviews_insight/cli.py`, the entry point

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

This is the `main` that the `reviews` command in `pyproject.toml` points at. It ties the
pieces together:

- `summarize` is the actual logic, and it's kept separate from the printing. It takes records
  and returns a dict: how many reviews, and how many distinct products (a set comprehension on
  `product_id` gives the unique count). It's fully typed, `list[dict[str, str]]` in and
  `dict[str, int]` out, so mypy can check it, and because it's a plain function that takes data
  and returns data, it's trivial to test, which is exactly what the test file does.
- `main` parses the command with `argparse`, reads config, loads the data, and prints the
  result. Notice it reads `config.environment` and `config.app_name`, so the output announces
  which environment it ran in.
- The `if __name__ == "__main__"` guard lets you run the file directly during development,
  while the installed `reviews` command calls `main` too. Same code, two ways in.

The separation of `summarize` (logic) from `main` (wiring) is the important habit. Logic you
can test lives apart from input and output you can't easily test.

**Enterprise lens.** Keeping the logic in a pure function, apart from the argument parsing and
the printing, is what makes an app testable and reusable. Today `summarize` is called from the
command line. Tomorrow the same function is called from a web endpoint or a scheduled job, with
no change, because it doesn't know or care where its records came from. That reuse is only
possible because the logic was never tangled up with the plumbing.

### 3.10 `tests/test_summary.py`, proving it works

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

One test, but it proves the core path end to end:

- It uses pytest's `tmp_path`, a temporary folder pytest creates and cleans up, so the test
  writes its own tiny CSV and never depends on a file on disk. A test that manages its own data
  is a test that runs anywhere.
- It writes three rows across two products, loads them, summarizes, and asserts the exact
  result: three reviews, two products. If `load_records` or `summarize` ever breaks, this test
  goes red.
- Even the test is typed, `tmp_path: Path` and `-> None`, so it passes the same strict mypy gate
  as the rest of the code. The standard is uniform, tests included.

**Enterprise lens.** A test from Day 1 sets the expectation that code comes with proof. This one
is small, but it's the seed of a safety net: every future change runs against it, so a refactor
that breaks the summary is caught in seconds, not in production. The habit, not the size, is the
point. A project with tests can be changed with confidence; a project without them can only be
changed with luck.

### 3.11 `data/reviews_sample.csv`, the sample data

```
product_id,rating,text
P100,5,Excellent build and battery life
P100,4,Good value for the price
P200,3,Average it does the job
P200,2,Stopped working after a week
P300,5,Fantastic highly recommend
```

Five reviews across three products (P100, P200, P300). It's realistic enough to be meaningful
and small enough to read at a glance. This is the file `DATA_PATH` points at by default.

### 3.12 `docker-compose.yml`, the database service

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

This is the supporting service from 2.9. It declares one Postgres database, pinned to
`postgres:16` (a fixed version, not `latest`, for the same reproducibility reason you pin
Python). The credentials and database name match the `DATABASE_URL` in `.env.example`, and the
named volume `reviews_pgdata` keeps the data alive across restarts. Start it in the background
with:

```bash
docker compose up -d
```

Today's code reads a CSV and never touches this database, so you don't need it to run Day 1's
command. It's here so you can see the shape of a real environment and have the database ready
for the days that will use it.

**Enterprise lens.** Declaring the database as a pinned, version controlled service is parity
in practice. Every engineer on the team gets the same Postgres 16 with one command, and it's
the same major version production runs, so a query or a migration that works locally works on
the server. The alternative, everyone installing their own database by hand, is exactly how "it
worked on my machine" bugs are born.

### 3.13 Run it

With `poetry install` done, run the console command through Poetry:

```bash
poetry run reviews summary
```

The verified output is exactly:

```
[dev] reviews-insight
reviews : 5
products: 3
```

Read that output against the code. `[dev]` is `config.environment`, `reviews-insight` is
`config.app_name`, and the two counts are `summarize` over the five sample rows across three
products. Every piece of it traces back to a line you just read. If you'd rather work in an
activated shell than prefix each command, that's `poetry env activate` on Poetry 2.x, but
`poetry run` is the habit to build.

### 3.14 Test it, lint it, type check it

Now put the code through the gate from 2.4, each tool run through Poetry.

Run the test:

```bash
poetry run pytest -q
```

Verified output:

```
1 passed
```

Lint with ruff, then let it format:

```bash
poetry run ruff check .
poetry run ruff format .
```

`ruff check .` scans the project and reports:

```
All checks passed!
```

`ruff format .` rewrites any file that doesn't match the style. On this project everything is
already clean.

Type check with mypy, pointed at the source:

```bash
poetry run mypy src
```

Verified output:

```
Success: no issues found
```

Three green results: the test passes, the linter is clean, and strict type checking finds
nothing wrong. That's the code half of the gate satisfied. Next we make it automatic.

### 3.15 `.pre-commit-config.yaml`, the gate that blocks a bad commit

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

This file wires ruff and mypy into Git as commit hooks. The ruff hook runs with `--fix` so it
auto-corrects what it safely can, `ruff-format` enforces the formatting, and the mypy hook type
checks. Each repo is pinned to an exact `rev`, so the gate itself is reproducible: everyone runs
the same tool versions. Install the hooks once:

```bash
poetry run pre-commit install

```

From now on, every `git commit` runs these checks first. Watch it work. Suppose you edit
`cli.py` and introduce a type error, say you return a string where a number is expected. You
stage it and try to commit. The mypy hook runs, finds the mismatch, and the commit is
**blocked**: the error prints and nothing is recorded. You fix the type, stage again, commit,
and this time every hook passes and the commit goes through.

That's the whole idea from 2.4 made concrete. The check isn't a thing you remember to run, it's
a gate the broken code cannot get past.

**Enterprise lens.** This is the CI pipeline's gate from 2.2, pulled onto your laptop so a
failure costs seconds instead of a rejected pull request minutes later. A repository guarded
this way stays uniformly clean and typed no matter how many hands touch it, and the pinned
`rev` values mean the gate behaves identically for every engineer and on the build server.

### 3.16 What you built

That's a real, installed, tested Python application, not a script that happened to run once. It
has a declared identity and a locked dependency graph, isolated dependencies managed by Poetry,
config read from the environment, a clean `src/` layout, a passing test, a clean linter, a
strict type check, a commit hook that enforces all of it, and a pinned database service ready
for the days ahead.

**Enterprise lens.** Scaffolding with Poetry, locking the graph, and getting a real `reviews`
command is the moment this stops being a demo. It installs the way a production build installs,
it runs the way a user runs it, it's tested and checked the way a pipeline tests and checks it,
and its environment is declared down to the database version. The gap between "it ran on my
laptop" and "it ships" is exactly the set of habits you just practiced, and you practiced all of
them on the very first project.

## What we learnt

- Python fits where engineering time is scarce and heavy work can go to fast libraries. It owns
  AI and data. It's the wrong tool for hard real time, single process CPU saturation, systems
  programming, and mobile or browser front ends, and knowing that is a strength.
- Python is compiled to bytecode, then interpreted by a virtual machine. That middle position
  explains its fast, interactive feel and its cost on tight numeric loops. The fix is native
  libraries, not line by line tuning.
- CPython is the reference implementation, distinct from the language spec, and its C interface
  is why AI and data run on Python. You pin the version, and this program targets 3.11 or newer.
- The GIL lets only one thread run Python bytecode at a time. Threads help I/O bound work, which
  spends its time waiting; they don't speed up CPU bound work, which needs processes to use all
  cores.
- Production is immutable and ephemeral: containers you can't SSH into, autoscaling, structured
  logs, no dev tools inside, and CI and CD gates. Seeing the target early shapes every choice.
- pip and `requirements.txt` blur declared deps with the transitive graph and drift silently. We
  standardize on Poetry: `pyproject.toml` declares, `poetry.lock` locks the exact graph, and the
  lock is committed. uv is the fast rising alternative.
- conda solves a different problem from Poetry: system level C, CUDA, and BLAS that pip can't
  install. Use conda only when the wheel isn't enough, otherwise Poetry.
- `pyproject.toml` is the single source of truth (PEP 518): metadata, dependencies, and tool
  config in one file. The quality gate is ruff and mypy strict, wired through pre-commit so a bad
  commit is blocked.
- You scaffolded reviews-insight with `poetry new --src`, installed and locked it, ran `poetry
  run reviews summary` for the verified output, passed the test, cleared ruff and mypy, and
  installed a commit hook that enforces it all.

## Live lab

Do the live lab now, with an instructor on hand. You'll build the reviews-insight skeleton
exactly as walked through above, on your own machine: run `poetry new --src reviews-insight`,
replace `pyproject.toml` with the verified content, add each file, run `poetry install`, then
`poetry run reviews summary` and confirm the exact output. Run `poetry run pytest -q` for `1
passed`, `poetry run ruff check .` for `All checks passed!`, and `poetry run mypy src` for
`Success: no issues found`. Then add `.pre-commit-config.yaml`, run `poetry run pre-commit
install`, introduce a type error, watch the commit get blocked by the mypy hook, fix it, and see
the commit pass. If you want, bring the database up with `docker compose up -d` just to see it
run. The goal is to feel the whole loop, from empty folder to installed, running, tested,
checked, and guarded app, with help right there when something on your machine misbehaves.

## Offline assignments

Two assignments to do on your own before Day 2. Each one reuses the exact shape of the
reviews-insight project, so you're not inventing structure, you're proving you can apply it to
new data. Use Poetry for both, commit the lockfile, and wire the same ruff and mypy gate.

1. **IoT telemetry.** Build the same skeleton for a device telemetry service. The data is a CSV
   of sensor readings (a `device_id`, a `reading`, a timestamp). Reuse the layout: `config.py`
   reads the data path from the environment, `data.py` loads the CSV with a clear error if it's
   missing, and `cli.py` has a `summary` command that reports how many readings there are and how
   many distinct devices. Add one test that proves the summary, using pytest's `tmp_path`. Run
   `poetry run ruff check .` and `poetry run mypy src` until both are clean. Money, where it
   appears, is in rupees. Everything runs offline, with no paid APIs, and any secret is read from
   an environment variable.

2. **Financial transactions.** Same skeleton, different domain. The data is a CSV of transactions
   (an `account_id`, an `amount` in rupees, a description). Your `summary` command reports the
   number of transactions and the number of distinct accounts, and, as a small extension, the
   total amount in rupees. Keep the logic in a pure function, separate from the printing, so your
   test can call it directly. One test, own data via `tmp_path`, clean ruff and strict mypy,
   offline, secrets from the environment.

Both assignments are checked on the same standard as the build: a Poetry project with a committed
lock, config from the environment, a clean layout, a passing test, and a clean quality gate. The
domain changes; the discipline doesn't.

## Next: Day 2 overview

Day 1 gave you the machine and a real environment. Day 2 puts that environment to work on data
itself. You'll refresh the pipeline shape every data and AI task follows (extract, massage,
transform, slice and dice, load, present), handle data too large to fit in memory by streaming
it, and reach for the right library at each step. Where Day 1 was about the project that holds
the code, Day 2 is about the moves you'll run on data every day.
