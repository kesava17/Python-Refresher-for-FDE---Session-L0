# Live Lab: Data Analytics with Python

The end-to-end stock-analytics notebook for the "Data Analytics with Python" topic. Load and
clean, make it store-aware (Parquet + DuckDB), analyse, and present, all in one reproducible
notebook. Managed with **Poetry**, like the other labs in this course.

## Run it

1. Install the dependencies (creates the project's virtual environment):
   ```bash
   poetry install
   ```
2. Launch Jupyter inside the environment and open the notebook:
   ```bash
   poetry run jupyter lab notebook.ipynb
   ```
3. In the notebook: **Kernel then Restart and Run All.** It should run top to bottom and
   produce the charts.

## Files

- `notebook.ipynb` : the live lab.
- `data/prices.csv` : bundled sample of daily prices for three fictional tickers (ACME,
  GLOBEX, INITECH), offline and reproducible.
- `make_data.py` : optional, regenerates a fresh sample dataset. Run with
  `poetry run python make_data.py`.
- `pyproject.toml` : the Poetry project and its dependencies.

## Notes

- Fictional tickers and synthetic prices. This is a **descriptive** analysis for teaching,
  **not investment advice**.
- The CSV has one deliberate gap so the notebook can show forward-fill.
- Optional exercise: swap the bundled CSV for live data from an API (for example `yfinance`);
  add it with `poetry add yfinance`.
