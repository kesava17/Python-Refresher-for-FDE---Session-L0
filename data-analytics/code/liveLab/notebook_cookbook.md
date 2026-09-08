# Notebook Cookbook

> New to Jupyter notebooks? Start here. This explains what a notebook is, how it works, and how
> to install, start, and work through the exercises in this live lab. Read it once before you
> open `notebook.ipynb`.

---

## 1. What is a notebook?

A **notebook** is a single document that mixes three things:

1. **Runnable code** (Python), in blocks you can run one at a time.
2. **The output** of that code (numbers, tables, charts), shown right below it.
3. **Written explanation** (formatted text), so the document reads like a report.

That makes it perfect for **data analytics**: you explore the data step by step, see each
result immediately, and the finished notebook doubles as the report you share. The file has the
extension `.ipynb`. Under the hood it is a JSON file, but you never edit that by hand: you work
in the Jupyter interface.

---

## 2. How a notebook works

**Cells.** A notebook is a stack of **cells**. Two kinds matter:

- **Code cells** run Python. When you run one, its code is sent to the kernel and the result
  appears below the cell.
- **Markdown cells** hold formatted text: headings, lists, and notes that tell the story.

**The kernel.** Behind the notebook runs a **kernel**: a live Python process. It remembers
everything you have run so far in this session, your imports, your variables, your loaded data,
for as long as it stays alive. Running a code cell sends its code to that kernel.

**Execution order.** Cells can be run in **any order**, and the number in the brackets, like
`In [7]`, shows the order they were run, not their position on the page. This is powerful for
exploring, and it is the number-one trap: a notebook can show a result its code no longer
produces.

**The golden habit: Restart and Run All.** Before you trust or share a notebook, restart the
kernel (wipe its memory) and run every cell top to bottom. If it runs clean start to finish, it
is a real result. If it only works in some secret order, it is not.

**Outputs are saved.** The results are stored inside the `.ipynb`, so someone opening your
notebook sees the charts and tables without re-running anything.

---

## 3. Keyboard basics

You switch between two modes with **Esc** and **Enter**:

- **Edit mode** (you are typing in a cell).
- **Command mode** (the cell is selected but not being edited).

| Do this | Keys |
| --- | --- |
| Run the cell, move to the next | Shift + Enter |
| Run the cell, stay on it | Ctrl + Enter |
| Run the cell, insert one below | Alt + Enter |
| Add a cell above / below | A / B (command mode) |
| Delete a cell | D D (press D twice) |
| Make it a markdown cell / code cell | M / Y (command mode) |
| Save | Ctrl + S |

---

## 4. Install and start (Poetry)

This lab is managed with **Poetry**, like the other labs in the course.

**Prerequisites:** Python 3.11 or newer, and Poetry installed.

From this `liveLab` folder:

```bash
poetry install                          # creates the environment, installs the libraries
poetry run jupyter lab notebook.ipynb   # launches Jupyter and opens the notebook
```

Then in the notebook: **Kernel → Restart Kernel and Run All Cells**. It should run top to bottom
and draw the charts.

Prefer the simpler classic interface? Use `poetry run jupyter notebook` instead of `jupyter
lab`.

---

## 5. What is in this lab

| File | What it is |
| --- | --- |
| `notebook.ipynb` | The guided live lab: load and clean, store-aware, analyse, present. |
| `data/prices.csv` | The sample dataset: daily prices for three fictional tickers (ACME, GLOBEX, INITECH). |
| `make_data.py` | Regenerates the sample data. Run with `poetry run python make_data.py`. |
| `pyproject.toml` | The Poetry project and its dependencies. |
| `README.md` | The short run card. |

The prices are **synthetic**, for teaching. This is a descriptive analysis, **not investment
advice**.

---

## 6. Start the exercises

1. **Open** `notebook.ipynb` and read the first markdown cell.
2. **Run the cells in order** (Shift + Enter through them, or Kernel → Run All Cells). Watch each
   output appear: the loaded prices, the returns, the summary, the charts.
3. **Work stage by stage**, the way the notebook is laid out:
   - **Load and clean** the prices, and derive returns.
   - **Store-aware**: save to Parquet and scan it with DuckDB.
   - **Analyse**: summary stats, moving averages, rolling volatility, correlation, rebasing.
   - **Present**: the correlation heatmap and the rebased performance chart.
   - **Write the finding** in the final markdown cell.
4. **Then the assignments** (from the topic):
   - *Single-ticker deep dive*: fully analyse one ticker and present it.
   - *Multi-ticker comparison*: compare the basket with a correlation heatmap and rebased
     performance.
   Make a **copy** of the live lab notebook for each assignment (right-click the file, Duplicate)
   and adapt it, or start a fresh notebook.
5. **Keep the cheatsheets open** as you work: `numpy_cheatsheet.md`, `pandas_cheatsheet.md`, and
   the others, plus the topic-wide `analytics-cheatsheet.md`, live alongside the lesson content.

---

## 7. Tips and habits

- **Restart and Run All** before you trust or share a notebook.
- **Start Jupyter from this folder** so the relative path `data/prices.csv` resolves.
- Keep cells **small and in order**; one idea per cell reads far better later.
- **Save often** (Ctrl + S). Jupyter also keeps periodic **checkpoints** you can revert to.
- Add markdown cells as you go: a sentence before a chart turns an analysis into a report.

---

## 8. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError` (e.g. no pandas) | You are outside the Poetry environment. Use `poetry run jupyter lab`, or run `poetry install` first. |
| `FileNotFoundError: data/prices.csv` | Wrong working directory. Start Jupyter from the `liveLab` folder, or run `poetry run python make_data.py` to (re)create the data. |
| The kernel is stuck or died | **Kernel → Restart Kernel**, then run the cells again. |
| Results look wrong or inconsistent | Cells ran out of order. **Kernel → Restart Kernel and Run All Cells**. |
| The notebook got messed up | **File → Revert to Checkpoint**, or close without saving and reopen (that discards unsaved changes). If needed, the notebook can be regenerated from the course scaffold. |
| A chart does not show | Make sure the cell ran (a number appears in `In [ ]`), and that earlier cells ran first. |

---

Once you are comfortable here, the same workflow (a notebook, a kernel, restart and run all)
carries into every data and AI project you will do in Python.
