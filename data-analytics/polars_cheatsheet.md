# Polars Cheatsheet

> A full reference for Polars in data-analytics work, **ordered by how often you reach for
> it**. Polars is a fast, multi-threaded, columnar DataFrame with a lazy engine. The one idea
> to internalise first is the **expression** (`pl.col(...)...`): you describe the computation,
> and the engine runs it, in parallel and optimised. Assumes `import polars as pl`. `df` is a
> DataFrame, `lf` a LazyFrame; analytics recipes use `prices`.

```python
import polars as pl
```

---

## 1. Create and load

```python
pl.read_csv("f.csv")                       # eager (into memory now)
pl.scan_csv("f.csv")                        # lazy (a plan, run on collect)
pl.read_parquet("f.parquet"); pl.scan_parquet("f.parquet")
pl.DataFrame({"a": [1, 2], "b": [3, 4]})
pl.from_pandas(pandas_df); pl.from_numpy(arr)
```

Prefer `scan_*` (lazy) for large data: the engine optimises the whole query before running.

---

## 2. Inspect

```python
df.head(); df.tail(); df.glimpse()
df.shape; df.columns; df.dtypes; df.schema
df.describe()
df.estimated_size()
```

---

## 3. Expressions (the core idea)

An expression is a recipe applied to columns. The four verbs that use them:

```python
df.select(pl.col("a"), pl.col("b"))            # pick / compute columns
df.with_columns((pl.col("a") * 2).alias("a2")) # add / replace columns
df.filter(pl.col("a") > 0)                     # keep rows
df.group_by("k").agg(pl.col("a").mean())       # aggregate

# expressions compose
pl.col("close").pct_change().alias("ret")
pl.col("ret").mean().over("ticker")            # window (see section 13)
pl.when(pl.col("ret") > 0).then("up").otherwise("down").alias("dir")
```

---

## 4. Select and filter

```python
df.select("a", "b")
df.select(pl.col("^ret.*$"))                   # regex column selection
df.select(pl.exclude("date"))                  # all but
df.filter((pl.col("a") > 0) & (pl.col("b") < 5))
df.filter(pl.col("ticker").is_in(["ACME", "GLOBEX"]))
df.filter(pl.col("a").is_between(0, 10))
```

---

## 5. Column operations

```python
df.with_columns(
    (pl.col("close").pct_change()).alias("ret"),
    (pl.col("close") * 2).alias("double"),
    pl.col("close").cast(pl.Float32).alias("close32"),
)
df.rename({"close": "px"})
df.drop("volume")
df.with_columns(pl.col("ret").fill_null(0))
```

---

## 6. Aggregate

```python
df.select(pl.col("ret").mean(), pl.col("ret").std())
df.select(pl.col("ret").sum(), pl.col("ret").min(), pl.col("ret").max())
df.select(pl.col("ret").quantile(0.9))
df.select(pl.count(), pl.col("ticker").n_unique())
```

---

## 7. Group by

```python
df.group_by("ticker").agg(
    pl.col("ret").mean().alias("mean_ret"),
    pl.col("ret").std().alias("vol"),
    pl.count().alias("n"),
)
# time-based grouping
df.group_by_dynamic("date", every="1mo").agg(pl.col("close").last())
# rolling by a time window
df.rolling(index_column="date", period="21d").agg(pl.col("ret").std())
```

---

## 8. Join and concat

```python
left.join(right, on="key", how="inner")        # inner/left/outer/semi/anti
left.join(right, left_on="a", right_on="b")
pl.concat([df1, df2])                           # stack rows
pl.concat([df1, df2], how="horizontal")         # stack columns
left.join_asof(right, on="time")                # nearest-earlier
```

---

## 9. Reshape

```python
df.pivot(values="close", index="date", columns="ticker")   # long to wide
df.melt(id_vars="date", variable_name="ticker", value_name="close")
df.explode("list_col")
df.transpose()
```

---

## 10. Sort and top

```python
df.sort("ret", descending=True)
df.sort(["ticker", "date"])
df.top_k(5, by="ret"); df.bottom_k(5, by="ret")
df.with_columns(pl.col("ret").rank(descending=True).alias("rank"))
```

---

## 11. Strings and dates

```python
# strings (the .str namespace)
pl.col("name").str.to_lowercase()
pl.col("name").str.contains("AI")
pl.col("name").str.replace("-", "_")
pl.col("date").str.to_date("%Y-%m-%d")

# dates (the .dt namespace)
pl.col("date").dt.year(); pl.col("date").dt.month()
pl.col("date").dt.weekday(); pl.col("date").dt.truncate("1mo")
```

---

## 12. Missing data

```python
df.drop_nulls(); df.drop_nulls(subset=["ret"])
df.with_columns(pl.col("ret").fill_null(0))
df.with_columns(pl.col("close").forward_fill())
df.null_count()
df.filter(pl.col("ret").is_not_null())
```

---

## 13. Window functions

```python
# compute per group, keep the row count (like SQL OVER)
df.with_columns(
    pl.col("ret").mean().over("ticker").alias("mean_by_ticker"),
    pl.col("close").rolling_mean(50).alias("sma_50"),
    pl.col("ret").rolling_std(21).alias("roll_vol"),
    pl.col("ret").cum_sum().alias("cum_ret"),
)
```

---

## 14. Lazy execution

```python
lf = pl.scan_csv("prices.csv")           # a plan, nothing runs yet
out = (
    lf.with_columns(pl.col("ACME").pct_change().alias("ret"))
      .group_by(pl.col("date").dt.month())
      .agg(pl.col("ret").mean())
      .collect()                          # run, optimised across the whole plan
)
lf.explain()                              # inspect the query plan
out = lf.collect(streaming=True)          # stream a larger-than-memory scan
```

---

## 15. Convert and save

```python
df.to_pandas(); df.to_numpy(); df.to_dicts()
df.write_csv("out.csv")
df.write_parquet("out.parquet")
```

---

## 16. Analytics recipes (stock data)

```python
prices = pl.read_csv("prices.csv", try_parse_dates=True)

# returns and rolling stats with expressions
out = prices.with_columns(
    pl.col("ACME").pct_change().alias("ret"),
    pl.col("ACME").rolling_mean(50).alias("sma_50"),
)

# summary per ticker (long format)
long = prices.melt(id_vars="date", variable_name="ticker", value_name="close")
summary = (
    long.sort(["ticker", "date"])
        .with_columns(pl.col("close").pct_change().over("ticker").alias("ret"))
        .group_by("ticker")
        .agg(pl.col("ret").mean().alias("mean"),
             pl.col("ret").std().alias("vol"))
        .sort("vol")
)

# monthly mean return
monthly = (
    long.with_columns(pl.col("close").pct_change().over("ticker").alias("ret"))
        .group_by_dynamic("date", every="1mo", group_by="ticker")
        .agg(pl.col("ret").mean())
)
```

---

## Golden rules

- Think in **expressions**: `pl.col(...).op()`, composed inside `select` / `with_columns` /
  `filter` / `group_by().agg`.
- Prefer **lazy** (`scan_*` + `collect`) so the engine optimises the whole query.
- Use `over(...)` for per-group calculations that keep every row (SQL windows).
- `group_by_dynamic` and `rolling` handle time windows.
- `collect(streaming=True)` for larger-than-memory scans; `to_pandas()` to hand off.
