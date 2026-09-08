# PySpark Cheatsheet

> A full reference for PySpark in data-analytics work, **ordered by how often you reach for
> it**. PySpark is the Python API for Apache Spark: distributed DataFrames across a cluster.
> The model to hold first: **transformations are lazy** (select, filter, groupBy build a
> plan); **actions** (show, count, collect, write) trigger the distributed job. Assumes the
> imports below.

```python
from pyspark.sql import SparkSession, functions as F, Window
```

---

## 1. SparkSession

```python
spark = SparkSession.builder.appName("analytics").getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", 200)   # tune shuffle width
spark.stop()
```

---

## 2. Create and load

```python
df = spark.read.csv("prices.csv", header=True, inferSchema=True)
df = spark.read.parquet("prices/")                    # preferred: typed, columnar
df = spark.read.json("f.json")
df = spark.read.format("jdbc").option("url", url).option("dbtable", "t").load()
df = spark.createDataFrame(pandas_df)
df = spark.range(0, 1000)                              # a test frame
```

---

## 3. Inspect

```python
df.show(5); df.show(5, truncate=False)
df.printSchema(); df.dtypes; df.columns
df.count()                              # action: counts across the cluster
df.describe().show(); df.summary().show()
df.explain()                            # the physical plan
```

---

## 4. Select and filter

```python
df.select("ticker", "close")
df.select(F.col("close"), (F.col("close") * 2).alias("double"))
df.filter(F.col("ret") > 0); df.where("ret > 0")
df.filter((F.col("ret") > 0) & (F.col("close") < 100))
df.withColumn("up", F.col("ret") > 0)
df.withColumnRenamed("close", "px")
df.drop("volume")
df.selectExpr("ticker", "close * 2 as double")
```

---

## 5. Column functions

```python
F.col("x"); F.lit(1); F.expr("close * 2")
F.when(F.col("ret") > 0, "up").otherwise("down")
F.col("close").cast("double")
F.round("ret", 4); F.abs("ret"); F.sqrt("x"); F.log("x")
F.coalesce("a", "b"); F.greatest("a", "b"); F.least("a", "b")
```

---

## 6. Group and aggregate

```python
df.groupBy("ticker").agg(
    F.mean("ret").alias("mean_ret"),
    F.stddev("ret").alias("vol"),
    F.count("*").alias("n"),
)
df.groupBy("ticker").count()
df.agg(F.mean("ret"), F.max("close"))                 # whole-frame aggregate
df.groupBy("ticker").pivot("month").agg(F.mean("ret"))
```

---

## 7. Joins

```python
df.join(other, on="ticker", how="inner")              # inner/left/right/outer/semi/anti
df.join(other, df.k == other.k, "left")
df.join(F.broadcast(small_df), "ticker")              # broadcast a small side (fast)
```

---

## 8. Window functions

```python
w = Window.partitionBy("ticker").orderBy("date")
df = df.withColumn("prev_close", F.lag("close", 1).over(w))
df = df.withColumn("ret", F.col("close") / F.col("prev_close") - 1)
df = df.withColumn("row", F.row_number().over(w))
df = df.withColumn("rank", F.rank().over(w))

# running / rolling with a frame
wr = w.rowsBetween(-49, 0)
df = df.withColumn("sma_50", F.avg("close").over(wr))
```

---

## 9. Sort and limit

```python
df.orderBy(F.col("ret").desc())
df.orderBy("ticker", "date")
df.limit(100)
df.orderBy(F.col("ret").desc()).limit(5)              # top 5
```

---

## 10. Strings and dates

```python
F.lower("name"); F.upper("name"); F.trim("name")
F.regexp_replace("name", "-", "_"); F.split("csv", ",")
F.to_date("date", "yyyy-MM-dd"); F.to_timestamp("ts")
F.year("date"); F.month("date"); F.date_trunc("month", "date")
F.datediff("d2", "d1"); F.date_add("date", 7)
```

---

## 11. Missing data

```python
df.na.drop(); df.na.drop(subset=["ret"])
df.na.fill(0); df.na.fill({"ret": 0, "name": "n/a"})
df.dropDuplicates(["ticker", "date"])
df.filter(F.col("ret").isNotNull())
```

---

## 12. SQL

```python
df.createOrReplaceTempView("prices")
spark.sql("""
    select ticker, avg(ret) as mean_ret
    from prices group by ticker order by mean_ret desc
""").show()
```

---

## 13. User-defined functions

```python
# pandas_udf is vectorised and fast (prefer it over a plain udf)
from pyspark.sql.functions import pandas_udf

@pandas_udf("double")
def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std()

df.withColumn("z", zscore("ret"))

# a plain (row-at-a-time) udf: flexible but slow, use as a last resort
@F.udf("double")
def times100(x):
    return x * 100
```

---

## 14. Reshape

```python
df.groupBy("date").pivot("ticker").agg(F.first("close"))   # long to wide
df.select("date", F.explode("list_col").alias("item"))     # one row per element
df.withColumn("arr", F.array("a", "b", "c"))
```

---

## 15. Partitions, cache, repartition

```python
df.repartition(200, "ticker")            # widen + partition by key (before a big join)
df.coalesce(1)                            # shrink partitions (before a small write)
df.cache(); df.persist()                  # keep a reused frame in memory
df.rdd.getNumPartitions()
```

---

## 16. Convert and collect

```python
df.toPandas()                             # bring to the driver (small results only)
df.collect()                              # list of Rows (small results only)
df.take(5); df.first()
df.rdd                                    # drop to the RDD API
```

---

## 17. Save

```python
df.write.mode("overwrite").parquet("out/")
df.write.partitionBy("ticker").parquet("out/")     # partitioned output
df.write.mode("append").csv("out/", header=True)
df.write.saveAsTable("db.prices")
```

---

## 18. Analytics recipes (big data)

```python
df = spark.read.parquet("prices/")                 # ticker, date, close

w = Window.partitionBy("ticker").orderBy("date")
df = (df.withColumn("ret", F.col("close") / F.lag("close").over(w) - 1)
        .withColumn("sma_50", F.avg("close").over(w.rowsBetween(-49, 0))))

summary = (df.groupBy("ticker")
             .agg(F.mean("ret").alias("mean"),
                  F.stddev("ret").alias("vol"))
             .orderBy("vol"))
summary.show()

# hand a small result to pandas for charting
pdf = summary.toPandas()
```

---

## Golden rules

- Transformations are lazy; an **action** (show, count, collect, write) runs the job.
- Never `collect()` or `toPandas()` a large frame to the driver; aggregate first.
- `broadcast()` the small side of a join with a big side.
- Prefer `pandas_udf` (vectorised) over a plain `udf`; better still, use built-in `F.*`.
- `cache()` a frame you reuse; `partitionBy` on write for large, queryable output.
- Prefer Parquet; tune `spark.sql.shuffle.partitions` for your data size.
