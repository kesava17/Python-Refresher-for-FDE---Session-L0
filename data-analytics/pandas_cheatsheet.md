# pandas Cheatsheet

> A full reference for pandas in data-analytics work, **ordered by how often you reach for
> it**: load, inspect, select, clean, derive, group, and combine come first (daily use);
> reshape, sort, time series, and stats next; then strings, categoricals, MultiIndex,
> performance, and I/O; the analytics recipes at the end. Assumes `import pandas as pd` and
> `import numpy as np`. `df` is a DataFrame; analytics recipes use `prices` (a date index with
> one close-price column per ticker).

```python
import pandas as pd
import numpy as np
```

---

## 1. Create and load

```python
pd.read_csv("f.csv", parse_dates=["date"], index_col="date")
pd.read_parquet("f.parquet"); pd.read_excel("f.xlsx"); pd.read_json("f.json")
pd.read_sql("select * from t", conn)
pd.DataFrame({"a": [1, 2], "b": [3, 4]})       # from a dict
pd.DataFrame(rows, columns=["a", "b"])         # from rows
pd.Series([1, 2, 3], name="x")
```

---

## 2. Inspect

```python
df.head(); df.tail(); df.sample(5)
df.shape; df.columns; df.index; df.dtypes
df.info(); df.describe(); df.describe(include="all")
df.memory_usage(deep=True)
```

---

## 3. Select and filter

```python
df["a"]; df[["a", "b"]]           # column(s)
df.loc[row_label, "a"]            # label-based
df.iloc[0:5, 0:3]                 # position-based
df.at[label, "a"]; df.iat[0, 0]   # single value, fast
df[df["a"] > 0]                   # boolean mask
df[(df["a"] > 0) & (df["b"] < 5)] # combine with & | ~
df.query("a > 0 and b < 5")       # string query
df[df["a"].isin([1, 2, 3])]
df[df["a"].between(0, 10)]
df.filter(like="ret")             # columns whose name contains
```

---

## 4. Clean

```python
df.dropna(); df.dropna(subset=["a"]); df.dropna(how="all")
df.fillna(0); df["a"].fillna(df["a"].mean())
df.ffill(); df.bfill()                       # carry forward / back
df.drop_duplicates(subset=["a"], keep="first")
df.astype({"a": "float64", "b": "category"})
df.rename(columns={"a": "alpha"})
df.replace({"?": np.nan})
df.drop(columns=["a"]); df.drop(index=[0, 1])
df["s"].str.strip().str.lower()              # tidy text
```

---

## 5. Derive columns

```python
df["ret"] = df["close"].pct_change()
df = df.assign(ret=lambda d: d["close"].pct_change(),
               up=lambda d: d["ret"] > 0)
df["cat"] = np.where(df["ret"] > 0, "up", "down")   # vectorised if-else
df["b"] = df["a"].map({1: "x", 2: "y"})             # map values
df["b"] = df["a"].apply(some_func)                  # last resort (slow)
df.pipe(clean).pipe(add_features)                   # chain steps
```

---

## 6. Group and aggregate

```python
df.groupby("ticker")["ret"].mean()
df.groupby("ticker").agg(mean=("ret", "mean"), vol=("ret", "std"))  # named agg
df.groupby("ticker").agg({"ret": ["mean", "std"], "vol": "sum"})
df.groupby("ticker")["ret"].transform("mean")      # broadcast back to rows
df.groupby("ticker").filter(lambda g: len(g) > 100)
df.pivot_table(index="ticker", columns="month", values="ret", aggfunc="mean")
pd.crosstab(df["ticker"], df["signal"])
df.groupby(df.index.to_period("M"))["ret"].mean()  # group by calendar period
```

---

## 7. Combine (merge, join, concat)

```python
pd.merge(left, right, on="key", how="inner")       # inner/left/right/outer
pd.merge(left, right, left_on="a", right_on="b")
left.join(right, how="left")                       # join on the index
pd.concat([df1, df2], axis=0)                       # stack rows
pd.concat([df1, df2], axis=1)                       # stack columns
pd.merge_asof(trades, quotes, on="time")           # nearest-earlier key
```

---

## 8. Reshape

```python
df.pivot(index="date", columns="ticker", values="close")   # long to wide
df.melt(id_vars="date", var_name="ticker", value_name="close")  # wide to long
df.stack(); df.unstack()                            # move a level
df.explode("list_col")                              # one row per list item
df.T                                                # transpose
```

---

## 9. Sort and rank

```python
df.sort_values("ret", ascending=False)
df.sort_values(["ticker", "date"])
df.sort_index()
df.nlargest(5, "ret"); df.nsmallest(5, "ret")
df["ret"].rank(ascending=False)
```

---

## 10. Time series

```python
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()
df.resample("M").last()                 # daily to monthly (D, W, M, Q, Y)
df.resample("W").agg({"close": "last", "volume": "sum"})
df["close"].rolling(50).mean()          # rolling window
df["close"].ewm(span=20).mean()         # exponential window
df["close"].shift(1)                     # lag by one period
df["close"].pct_change()                 # period-over-period change
df.asfreq("D").ffill()                   # regular frequency, fill gaps
df.tz_localize("UTC").tz_convert("Asia/Kolkata")
df.loc["2023-06"]                        # partial-string date slice
df.between_time("09:15", "15:30")        # intraday window
```

---

## 11. Descriptive stats

```python
df.mean(); df.std(); df.median(); df.var()
df.quantile([0.25, 0.5, 0.75])
df["ret"].value_counts(); df["ret"].value_counts(normalize=True)
df.corr(); df.cov()                       # correlation / covariance matrix
df["a"].corr(df["b"])
df["ret"].cumsum(); (1 + df["ret"]).cumprod()
df["ret"].nunique(); df["ret"].idxmax()
```

---

## 12. Strings, categoricals, MultiIndex

```python
# strings (the .str namespace)
s.str.lower(); s.str.contains("AI"); s.str.replace("-", "_")
s.str.split(",", expand=True); s.str.extract(r"(\d+)")

# categoricals (memory and speed for repeated labels)
df["ticker"] = df["ticker"].astype("category")

# MultiIndex
df.set_index(["ticker", "date"])
df.xs("ACME", level="ticker")             # cross-section
df.groupby(level=0).mean()
```

---

## 13. Missing data

```python
df.isna(); df.isna().sum()                # count NaNs per column
df.notna()
df.dropna(thresh=2)                       # keep rows with >= 2 non-NaN
df.interpolate()                          # fill by interpolation
df.fillna(method="ffill", limit=3)
```

---

## 14. Performance

```python
# prefer vectorised operations over apply/iterrows
df["c"] = df["a"] * df["b"]               # fast
df.eval("c = a * b")                      # fast expression engine
df.query("a > b")                         # fast filter engine

df["ticker"] = df["ticker"].astype("category")   # shrink repeated strings
pd.to_numeric(df["x"], downcast="float")         # smaller dtypes
```

Avoid `df.iterrows()` and `apply` on large frames; reach for vectorised ops, `groupby`, or
`merge`. For data beyond one machine, move up to Polars, Dask, or PySpark.

---

## 15. Save and output

```python
df.to_csv("out.csv", index=False)
df.to_parquet("out.parquet")             # columnar, fast, typed
df.to_excel("out.xlsx", sheet_name="data")
df.to_sql("t", conn, if_exists="replace", index=False)
```

---

## 16. Analytics recipes (stock data)

```python
prices = pd.read_csv("prices.csv", parse_dates=["date"], index_col="date").ffill()

returns = prices.pct_change().dropna()                 # daily returns
cumulative = (1 + returns).cumprod() - 1               # cumulative return
sma_50 = prices["ACME"].rolling(50).mean()             # trend
roll_vol = returns["ACME"].rolling(21).std() * np.sqrt(252)   # rolling vol
monthly = prices.resample("M").last().pct_change()     # monthly returns
corr = returns.corr()                                  # correlation matrix
rebased = prices / prices.iloc[0] * 100                # fair comparison

# drawdown
cum = (1 + returns["ACME"]).cumprod()
drawdown = cum / cum.cummax() - 1

# rank the basket
summary = pd.DataFrame({"mean": returns.mean(),
                        "vol": returns.std()}).sort_values("vol")

# best and worst days
returns["ACME"].nlargest(5); returns["ACME"].nsmallest(5)
```

---

## Golden rules

- Use `loc`/`iloc` for clear label vs position selection; avoid chained `df[...][...]`.
- Combine masks with `& | ~` and parentheses, not `and`/`or`.
- Vectorise: prefer column math, `groupby`, and `merge` over `apply`/`iterrows`.
- Set a `DatetimeIndex` to unlock `resample`, `rolling`, and date slicing.
- Work on returns, not prices; annualise volatility with `* np.sqrt(252)`.
- Use `category` dtype and Parquet to save memory and time.
