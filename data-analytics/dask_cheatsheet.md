# Dask Cheatsheet

> A full reference for Dask in data-analytics work, **ordered by how often you reach for it**.
> Dask scales NumPy and pandas across cores and a cluster with **lazy task graphs**: you build
> a graph with a familiar API, then `.compute()` runs it in parallel. The mental model to hold
> first: nothing runs until you compute or persist. Assumes `import dask.dataframe as dd`.

```python
import dask.dataframe as dd
import dask.array as da
```

---

## 1. Setup and scheduler

```python
# threads/processes on one machine work with no setup. For a cluster + dashboard:
from dask.distributed import Client, LocalCluster
client = Client()                 # local cluster, dashboard at http://localhost:8787
client = Client("scheduler:8786") # connect to a remote cluster
```

---

## 2. Load

```python
ddf = dd.read_csv("prices-*.csv", parse_dates=["date"])   # many files -> partitions
ddf = dd.read_parquet("prices/")                          # preferred: typed, columnar
ddf = dd.from_pandas(pandas_df, npartitions=8)            # split a pandas frame
x = da.from_array(np_array, chunks=(1000, 1000))          # chunked array
x = da.random.random((10000, 10000), chunks=(1000, 1000))
```

---

## 3. Inspect (mind what triggers work)

```python
ddf.head()             # cheap: reads the first partition only
ddf.dtypes; ddf.columns
ddf.npartitions        # number of partitions
ddf.tail()
len(ddf); ddf.shape[0].compute()   # counting rows triggers a full pass
```

---

## 4. The lazy model

```python
result = ddf.groupby("ticker").ret.mean()   # a graph, nothing has run
result.compute()                            # run it, return a pandas/numpy result
ddf = ddf.persist()                         # run and keep in cluster memory (reuse)
result.visualize()                          # draw the task graph
```

- **compute()** runs the graph and returns concrete pandas/numpy.
- **persist()** runs it and keeps the result distributed for reuse.

---

## 5. Select and filter (pandas-like)

```python
ddf["ret"]; ddf[["ret", "close"]]
ddf[ddf["ret"] > 0]
ddf.loc[ddf["ticker"] == "ACME"]
ddf.assign(up=ddf["ret"] > 0)
ddf["ret"] = ddf["close"] / ddf["close"].shift(1) - 1
```

---

## 6. Group and aggregate

```python
ddf.groupby("ticker")["ret"].mean().compute()
ddf.groupby("ticker").agg({"ret": ["mean", "std"]}).compute()
ddf.groupby("ticker")["ret"].mean(split_out=4)   # spread the output shuffle
# custom parallel aggregation
agg = dd.Aggregation("range", lambda s: (s.max(), s.min()),
                     lambda mx, mn: mx.max() - mn.min())
ddf.groupby("ticker")["close"].agg(agg).compute()
```

---

## 7. Joins

```python
dd.merge(left, right, on="key", how="inner")
# joins and rolling are far faster on a sorted index:
ddf = ddf.set_index("date")          # expensive shuffle, do it once
```

---

## 8. Custom parallel work

```python
# apply a pandas function to every partition (fast, no shuffle)
ddf.map_partitions(lambda pdf: pdf.assign(z=(pdf.ret - pdf.ret.mean())))

# arbitrary parallelism with delayed
import dask
@dask.delayed
def load_and_score(path):
    return score(pd.read_csv(path))
results = dask.compute(*[load_and_score(p) for p in paths])
```

---

## 9. Time series and rolling

```python
ddf = ddf.set_index("date")               # rolling/resample need a sorted index
ddf["close"].rolling(50).mean()           # per-partition windows
ddf["close"].resample("1M").last().compute()
```

---

## 10. Arrays (chunked NumPy)

```python
x = da.random.random((100000, 100), chunks=(10000, 100))
x.mean(axis=0).compute()
(x @ x.T).compute()                       # blocked matrix multiply
da.linalg.norm(x).compute()
```

---

## 11. Partitions and index

```python
ddf.repartition(npartitions=16)           # fewer/more partitions
ddf.repartition(partition_size="128MB")
ddf.set_index("date", sorted=True)        # skip the shuffle if already sorted
ddf.map_partitions(len).compute()         # rows per partition
```

Aim for partitions around 100MB: too many adds overhead, too few loses parallelism.

---

## 12. Persist and memory

```python
ddf = ddf.persist()                       # keep hot data in cluster memory
client.rebalance()                        # spread it across workers
from dask import compute
a2, b2 = compute(a, b)                    # compute several graphs together (share work)
```

---

## 13. Save

```python
ddf.to_parquet("out/", write_index=True)  # one file per partition
ddf.to_csv("out-*.csv", index=False)
```

---

## 14. Distributed extras

```python
future = client.submit(fn, arg)           # run a function on the cluster
client.gather(future)                      # collect the result
big = client.scatter(large_object)         # send shared data to workers once
```

---

## 15. Analytics recipes (scaled pandas)

```python
# a folder of daily files too big for one machine's RAM
ddf = dd.read_parquet("prices/")                     # partitioned
ddf["ret"] = ddf.groupby("ticker")["close"].apply(
    lambda s: s.pct_change(), meta=("ret", "f8"))

# mean and vol per ticker, computed in parallel
summary = (ddf.groupby("ticker")["ret"]
              .agg(["mean", "std"])
              .compute()
              .sort_values("std"))

# scale an existing pandas pipeline with almost no change
ddf.map_partitions(existing_pandas_pipeline).to_parquet("out/")
```

---

## Golden rules

- Lazy by default: build the graph, then `compute()` once (or `persist()` to reuse).
- `set_index` once before joins, rolling, or resample; it is the expensive step.
- Size partitions near 100MB; check with `map_partitions(len)`.
- Prefer Parquet over CSV; prefer `map_partitions` over row-wise `apply`.
- If it fits in memory, plain pandas is simpler and faster; reach for Dask when it does not.
