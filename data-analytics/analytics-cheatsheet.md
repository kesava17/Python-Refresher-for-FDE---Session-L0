# Data Analytics with Python: Cheatsheet

> A copy-paste reference for the topic. Every scenario has a minimal working example. It
> assumes the bundled `prices.csv` (a date index with one close-price column per ticker:
> ACME, GLOBEX, INITECH). Fictional tickers, synthetic data, for teaching. Not investment
> advice.

## Setup

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

prices = pd.read_csv("prices.csv", parse_dates=["date"], index_col="date")
```

The five levels of the topic map to the sections below: choose the store, work the notebook,
manage data with the libraries, analyse, present.

---

## 1. Load and inspect

| Scenario | Example |
| --- | --- |
| Read a CSV, index by date | `pd.read_csv("prices.csv", parse_dates=["date"], index_col="date")` |
| First and last rows | `prices.head()` , `prices.tail()` |
| Shape and dtypes | `prices.shape` , `prices.dtypes` |
| Quick summary | `prices.describe()` |
| One column (Series) | `prices["ACME"]` |
| A date slice | `prices.loc["2023-06"]` |

```python
prices.head()
prices.describe()
prices.loc["2023-06", "ACME"]      # ACME closes in June 2023
```

---

## 2. Clean and prepare

```python
prices = prices.sort_index()                 # order by date
prices = prices.dropna(how="all")            # drop fully empty days
prices = prices.ffill()                      # carry the last price over a gap
prices = prices.drop_duplicates()            # remove duplicate rows
# prices["ACME"] = prices["ACME"].astype(float)   # fix a column read as text
```

| Scenario | Example |
| --- | --- |
| Sort by the date index | `prices.sort_index()` |
| Drop empty days | `prices.dropna(how="all")` |
| Fill a gap forward | `prices.ffill()` (or `bfill`) |
| Remove duplicates | `prices.drop_duplicates()` |
| Fix a dtype | `prices["ACME"].astype(float)` |

---

## 3. Core analytics scenarios (pandas)

The heart of the topic. Each recipe is one or two lines on the `prices` frame.

### Returns

```python
returns = prices.pct_change().dropna()                 # simple daily returns
log_returns = np.log(prices / prices.shift(1)).dropna() # log returns
```

### Cumulative return (growth of the period)

```python
cumulative = (1 + returns).cumprod() - 1
```

### Moving averages (trend)

```python
sma_50 = prices["ACME"].rolling(50).mean()                  # simple
ema_20 = prices["ACME"].ewm(span=20, adjust=False).mean()   # exponential
```

### Rolling volatility (annualised)

```python
roll_vol = returns["ACME"].rolling(21).std() * np.sqrt(252)
```

### Resample daily to monthly

```python
monthly_price = prices.resample("M").last()
monthly_return = prices.resample("M").last().pct_change().dropna()
```

### Correlation across tickers

```python
corr = returns.corr()          # -1 to 1, how the tickers move together
```

### Rebased performance (fair comparison, start = 100)

```python
rebased = prices / prices.iloc[0] * 100
```

### Drawdown (worst drop from a peak)

```python
cum = (1 + returns["ACME"]).cumprod()
drawdown = cum / cum.cummax() - 1
max_drawdown = drawdown.min()
```

### Summary table (rank the basket)

```python
summary = pd.DataFrame({
    "mean_return": returns.mean(),
    "volatility": returns.std(),
    "ann_return": returns.mean() * 252,
    "ann_vol": returns.std() * np.sqrt(252),
}).sort_values("ann_vol")
```

### Best and worst days

```python
returns["ACME"].nlargest(5)      # five best days
returns["ACME"].nsmallest(5)     # five worst days
```

### Group by a calendar period

```python
by_month = returns.groupby(returns.index.to_period("M")).mean()
```

---

## 4. Presentation scenarios

| Question | Chart | Example |
| --- | --- | --- |
| Movement over time | line | `prices["ACME"].plot()` |
| A few compared | bar | `summary["ann_vol"].plot.bar()` |
| Distribution of returns | histogram | `returns["ACME"].hist(bins=50)` |
| Do they move together | heatmap | `sns.heatmap(returns.corr(), annot=True, cmap="vlag", vmin=-1, vmax=1)` |
| Fair performance compare | line (rebased) | `rebased.plot()` |

```python
# a titled, presentation-ready correlation heatmap
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(returns.corr(), annot=True, cmap="vlag", vmin=-1, vmax=1, ax=ax)
ax.set_title("How the basket moves together (daily-return correlation)")
plt.tight_layout()

# rebased performance, one message per chart
rebased.plot(title="Rebased performance (start = 100)")
```

### Interactive (plotly)

```python
import plotly.express as px
px.line(rebased, title="Rebased performance").show()
```

### Candlestick (needs OHLC data, not the close-only sample)

```python
import mplfinance as mpf
mpf.plot(ohlc_df, type="candle", volume=True)   # ohlc_df: open, high, low, close, volume
```

### The notebook as a report

```bash
jupyter nbconvert --to html notebook.ipynb     # also: --to pdf, --to slides
```

---

## 5. Library quick reference

The same tasks, per library, with the call that does them. Reach up the ladder as data grows.

### NumPy (numeric arrays, one machine)

| Task | NumPy |
| --- | --- |
| Descriptive stats | `mean`, `median`, `std`, `var`, `percentile` |
| Aggregation (per axis) | `sum`, `min`, `max`, `cumsum`, `cumprod` |
| Element-wise math | vectorised `+ - * /`, `log`, `exp`, `sqrt` |
| Filter and mask | boolean masks, `where`, `clip` |
| Reshape and combine | `reshape`, `transpose`, `concatenate`, `stack` |
| Correlation and covariance | `corrcoef`, `cov` |
| Linear algebra | `dot`, `matmul`, `linalg.inv`, `linalg.svd` |
| Sort and search | `sort`, `argsort`, `unique`, `searchsorted` |
| Histogram and bins | `histogram`, `digitize`, `bincount` |

```python
arr = prices["ACME"].to_numpy()
rets = arr[1:] / arr[:-1] - 1                  # vectorised returns
ann_vol = rets.std() * np.sqrt(252)
c = np.corrcoef(returns.to_numpy().T)          # correlation matrix
```

### pandas (labelled tables, one machine)

| Task | pandas |
| --- | --- |
| Load and save | `read_csv`, `read_parquet`, `to_csv`, `to_parquet` |
| Clean | `dropna`, `fillna`, `ffill`, `drop_duplicates` |
| Select and filter | `loc`, `iloc`, `query`, boolean masks |
| Group and aggregate | `groupby().agg`, `pivot_table`, `transform` |
| Join and reshape | `merge`, `concat`, `pivot`, `melt` |
| Time series | `resample`, `rolling`, `shift`, `ewm` |
| Descriptive stats | `describe`, `mean`, `std`, `corr` |

```python
returns = prices.pct_change().dropna()
monthly = prices.resample("M").last()
sma_50 = prices["ACME"].rolling(50).mean()
top = returns["ACME"].nlargest(5)
```

### Polars (fast columnar, many cores, lazy)

| Task | Polars |
| --- | --- |
| Load (lazy or eager) | `scan_csv`, `scan_parquet`, `read_csv` |
| Select and filter | `select`, `filter`, `with_columns` |
| Group and aggregate | `group_by().agg` |
| Expressions | `pl.col(...).mean()`, `over(...)`, `when/then` |
| Time series and windows | `group_by_dynamic`, `rolling_mean` |
| Run the query | `collect()` (optimised) |

```python
import polars as pl
out = (
    pl.scan_csv("prices.csv")
      .with_columns(pl.col("ACME").pct_change().alias("ret"))
      .select(pl.col("ret").mean().alias("mean_ret"),
              pl.col("ret").std().alias("vol"))
      .collect()
)
```

### Dask (parallel and out-of-core, scales pandas and numpy)

| Task | Dask |
| --- | --- |
| Load many files | `dd.read_csv`, `dd.read_parquet` (globs) |
| Filter and select | pandas-like `loc`, boolean masks |
| Group and aggregate | `groupby().agg` (parallel) |
| Join | `merge` (partition-aware) |
| Custom parallel | `map_partitions`, `dask.delayed` |
| Run it | `compute()` |

```python
import dask.dataframe as dd
ddf = dd.read_csv("prices-*.csv", parse_dates=["date"])   # many files, lazy
mean_ret = ddf.groupby("ticker")["ret"].mean().compute()  # parallel
```

### PySpark (distributed, big data)

| Task | PySpark |
| --- | --- |
| Load | `spark.read.csv / parquet / jdbc` |
| Select and filter | `select`, `filter` / `where`, `withColumn` |
| Group and aggregate | `groupBy().agg`, `F.mean`, `F.sum` |
| Join | `join` (broadcast and shuffle) |
| Window functions | `Window` with `F.lag`, `F.row_number` |
| SQL | `spark.sql`, `createOrReplaceTempView` |

```python
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet("s3://lake/prices/")
(df.groupBy("ticker")
   .agg(F.mean("ret").alias("mean_ret"), F.stddev("ret").alias("vol"))
   .show())
```

---

## 6. Choosing a store (Level 1 quick reference)

| Need | Store family |
| --- | --- |
| System of record, transactions, joins | Relational (RDBMS) |
| Cache, fast lookup by key | Key-value |
| Flexible, evolving records | Document |
| Very high write volume at scale | Wide-column |
| Relationship and path queries | Graph |
| High-rate timestamped metrics | Time-series |
| Full-text search and filtering | Search |
| Analytics and aggregates (OLAP) | Columnar / warehouse |
| Relational at global scale | Distributed SQL (NewSQL) |
| Cheap, huge, open raw data | Object storage + Parquet |
| Similarity search on embeddings | Vector |

**The decision:** match the store to the access pattern, the consistency need, the scale,
and the cost. Analytics usually reads from a columnar or warehouse store (or Parquet on a
lake through DuckDB), not the live operational database.

---

## Golden rules

- Work on **returns**, not prices, when comparing across tickers.
- **Rebase** to a common start (100) for a fair performance comparison.
- Annualise volatility with `* np.sqrt(252)`.
- Keep the notebook reproducible: **restart and run all** before you trust or share it.
- Title every chart with the finding, label the axes, one message per chart.
- Reach up the library ladder only when the data outgrows the current tool.
