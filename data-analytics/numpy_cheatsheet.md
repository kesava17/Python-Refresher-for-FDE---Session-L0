# NumPy Cheatsheet

> A full reference for NumPy in data-analytics work, **ordered by how often you reach for
> it**: creation, inspection, indexing, reshaping, math, and aggregation come first (daily
> use); broadcasting, logic, sorting, and linear algebra next; then random, stats, the
> copy-vs-view gotcha, dtypes, NaN handling, performance, and I/O; the analytics recipes at
> the end tie it together. Assumes `import numpy as np`.

```python
import numpy as np
```

---

## 1. Create arrays

The starting point of almost everything.

```python
np.array([1, 2, 3])                 # from a list  -> 1D
np.array([[1, 2], [3, 4]])          # nested lists -> 2D
np.arange(0, 10, 2)                 # 0 2 4 6 8   (start, stop, step)
np.linspace(0, 1, 5)                # 5 evenly spaced values on [0, 1]
np.zeros((2, 3))                    # 2x3 of 0.0
np.ones((2, 3))                     # 2x3 of 1.0
np.full((2, 3), 7)                  # 2x3 of 7
np.eye(3)                           # 3x3 identity
np.empty((2, 2))                    # uninitialised (fast, contains garbage)
np.zeros_like(a)                    # zeros with a's shape and dtype
np.tile([1, 2], 3)                  # 1 2 1 2 1 2
np.repeat([1, 2], 3)                # 1 1 1 2 2 2

rng = np.random.default_rng(42)     # the modern random generator
rng.random((2, 3))                  # random floats in [0, 1)
```

---

## 2. Inspect an array

```python
a.shape        # dimensions, e.g. (2, 3)
a.ndim         # number of dimensions
a.size         # total number of elements
a.dtype        # element type, e.g. float64
a.itemsize     # bytes per element
a.nbytes       # total bytes
len(a)         # length of the first axis
```

---

## 3. Index and slice

Basic slicing returns a **view** (see section 13); boolean and fancy indexing return a copy.

```python
a[0]; a[-1]                 # first, last
a[2:5]; a[:3]; a[3:]        # ranges
a[::2]; a[::-1]             # every 2nd; reversed
m[1, 2]                     # 2D: row 1, col 2
m[0]; m[:, 1]               # first row; second column
m[0:2, 1:3]                 # submatrix (rows 0-1, cols 1-2)
a[a > 0]                    # boolean mask (keep positives)
a[[0, 2, 4]]                # fancy indexing (pick indices)
m[[0, 1], [1, 2]]           # elements (0,1) and (1,2)
a[a > 0] = 0                # assign through a mask
np.where(a > 0, a, 0)       # conditional select without a loop
```

---

## 4. Reshape, transpose, combine

```python
a.reshape(3, 4)             # new shape (must match size); -1 infers a dim
a.reshape(-1)               # flatten to 1D (view when possible)
a.ravel()                   # flatten (view when possible)
a.flatten()                 # flatten (always a copy)
a.T                         # transpose (view)
np.transpose(a, (1, 0, 2))  # reorder axes
a[:, None]                  # add an axis (column vector); same as np.newaxis
np.expand_dims(a, axis=0)   # add an axis
np.squeeze(a)               # drop size-1 axes

np.concatenate([a, b], axis=0)   # join along an existing axis
np.vstack([a, b])                # stack rows (axis 0)
np.hstack([a, b])                # stack columns (axis 1)
np.column_stack([a, b])          # 1D arrays as columns
np.stack([a, b], axis=0)         # join along a NEW axis
np.split(a, 3); np.array_split(a, 3)   # split into parts
```

---

## 5. Element-wise math (ufuncs)

Operate on whole arrays, no loop. All are vectorised and fast.

```python
a + b, a - b, a * b, a / b, a ** 2, a % 2   # element-wise arithmetic
np.sqrt(a); np.exp(a); np.log(a); np.log1p(a); np.log10(a)
np.abs(a); np.sign(a); np.reciprocal(a)
np.round(a, 2); np.floor(a); np.ceil(a); np.trunc(a)
np.maximum(a, b); np.minimum(a, b)          # element-wise max/min of two arrays
np.clip(a, lo, hi)                          # clamp values into a range
np.sin(a); np.cos(a); np.tan(a)
np.diff(a)                                  # consecutive differences
np.gradient(a)                              # numerical gradient
```

---

## 6. Aggregate and reduce

The workhorses of analysis. Use `axis` to reduce along rows or columns.

```python
a.sum(); a.mean(); a.std(); a.var()
a.min(); a.max(); a.prod()
a.argmin(); a.argmax()                 # index of the min / max
np.median(a); np.percentile(a, 90); np.quantile(a, 0.9)
np.ptp(a)                              # peak to peak (max - min)

a.sum(axis=0)      # reduce down the rows -> one value per column
a.mean(axis=1)     # reduce across columns -> one value per row
a.sum(axis=0, keepdims=True)   # keep the reduced axis (for broadcasting)

a.cumsum(); a.cumprod()                # running totals
np.nansum(a); np.nanmean(a); np.nanstd(a)   # ignore NaNs
```

| Reduce | Function |
| --- | --- |
| Total, mean, spread | `sum`, `mean`, `std`, `var` |
| Extremes and their location | `min`, `max`, `argmin`, `argmax` |
| Order stats | `median`, `percentile`, `quantile` |
| Running | `cumsum`, `cumprod` |
| NaN-safe | `nansum`, `nanmean`, `nanstd` |

---

## 7. Broadcasting

How arrays of different shapes combine. Dimensions align from the right; a size-1 (or
missing) dimension stretches to match.

```python
a * 2                         # scalar broadcasts over the whole array
col = np.array([[1], [2], [3]])   # shape (3, 1)
row = np.array([10, 20, 30])      # shape (3,)
col + row                     # -> (3, 3) grid

# normalise each column of a matrix (subtract the column mean)
centered = m - m.mean(axis=0)                 # (n, k) - (k,) works
z = (m - m.mean(axis=0)) / m.std(axis=0)      # standardise columns
```

Rule of thumb: shapes are compatible when each aligned dimension is equal or one of them is 1.

---

## 8. Logic, comparison, and selection

```python
a > 0; a == b; (a > 0) & (a < 10)      # element-wise (use & | ~, not and/or)
np.all(a > 0); np.any(a > 0)           # all / any true
np.count_nonzero(a > 0)                # how many pass
np.where(cond, x, y)                   # pick x where cond else y
np.where(cond)                         # indices where cond is true
np.isnan(a); np.isinf(a); np.isfinite(a)
np.logical_and(x, y); np.logical_or(x, y); np.logical_not(x)
np.isclose(a, b); np.allclose(a, b)    # float-safe equality
np.select([c1, c2], [v1, v2], default=0)   # multi-condition pick
```

---

## 9. Sort, search, unique

```python
np.sort(a)                    # sorted copy
a.sort()                      # sort in place
np.argsort(a)                 # indices that would sort a
np.sort(m, axis=0)            # sort each column
np.unique(a)                  # sorted distinct values
np.unique(a, return_counts=True)   # values and their counts
np.searchsorted(sorted_a, v)  # insertion index to keep order
np.nonzero(a); np.argwhere(a) # indices of non-zeros
np.isin(a, [1, 2, 3])         # membership mask
np.partition(a, 5)            # k smallest in front (faster than full sort)
```

---

## 10. Linear algebra

```python
a @ b; np.matmul(a, b); np.dot(a, b)   # matrix / dot product
np.linalg.inv(m)                       # inverse
np.linalg.solve(A, b)                  # solve Ax = b (prefer over inv)
np.linalg.det(m)                       # determinant
np.linalg.eig(m)                       # eigenvalues and eigenvectors
np.linalg.svd(m)                       # singular value decomposition
np.linalg.norm(v)                      # vector / matrix norm
np.linalg.matrix_rank(m)               # rank
np.trace(m); np.diagonal(m)            # trace, diagonal
np.outer(u, v); np.cross(u, v)         # outer, cross product
```

---

## 11. Random (the modern Generator API)

```python
rng = np.random.default_rng(seed=42)   # reproducible
rng.random((3, 2))                     # floats in [0, 1)
rng.normal(loc=0, scale=1, size=1000)  # gaussian
rng.uniform(-1, 1, size=5)             # uniform range
rng.integers(0, 10, size=5)            # ints in [0, 10)
rng.choice([1, 2, 3], size=10)         # sample with replacement
rng.choice(a, size=10, replace=False)  # sample without replacement
rng.shuffle(a)                         # shuffle in place
rng.permutation(a)                     # shuffled copy
```

Prefer `default_rng` over the legacy `np.random.seed` / `np.random.rand` / `randn`.

---

## 12. Statistics and binning

```python
np.corrcoef(m)                    # correlation matrix (rows are variables)
np.cov(m)                         # covariance matrix
np.average(a, weights=w)          # weighted mean
np.histogram(a, bins=20)          # counts and bin edges
np.bincount(labels)               # counts of non-negative ints
np.digitize(a, bins)              # which bin each value falls in
```

---

## 13. Copies vs views (the top gotcha)

```python
b = a[2:5]          # a VIEW: changing b changes a
b = a[2:5].copy()   # an independent copy
np.may_share_memory(a, b)   # check if they share data
```

- Basic slicing and `reshape`/`ravel`/`T` return a **view** when possible.
- **Boolean and fancy indexing** return a **copy**.
- Write `.copy()` when you need to modify without touching the original.

---

## 14. Data types and casting

```python
a.dtype                       # e.g. float64
a.astype(np.float32)          # cast (makes a copy)
np.array([1, 2], dtype=np.int64)
np.array([1, 0, 1], dtype=bool)
```

- Common: `int32`, `int64`, `float32`, `float64`, `bool`, `datetime64[ns]`.
- `np.nan` and `np.inf` are floats: an int array cannot hold NaN.
- Fixed-width ints overflow silently; cast up if values may be large.

---

## 15. Missing values (NaN)

```python
np.isnan(a)                   # mask of NaNs
np.nanmean(a); np.nansum(a)   # aggregate ignoring NaNs
a[np.isnan(a)] = 0            # replace NaNs
np.nan_to_num(a, nan=0.0)     # replace NaN / inf in one call
np.where(np.isnan(a), 0, a)   # conditional replace
```

---

## 16. Vectorise and go fast

```python
# GOOD: vectorised, runs in C
out = a * 100 + b

# AVOID: an explicit Python loop over elements
out = np.array([x * 100 + y for x, y in zip(a, b)])

np.vectorize(f)(a)            # convenience wrapper (NOT a speedup)
np.einsum("ij,jk->ik", A, B)  # expressive, fast contractions (advanced)
```

- Replace loops with whole-array operations and broadcasting.
- Keep arrays contiguous; avoid growing arrays in a loop (`np.append` is O(n)).
- `np.frompyfunc` and `np.vectorize` are for convenience, not performance.

---

## 17. Save and load

```python
np.save("a.npy", a); a = np.load("a.npy")            # single array, binary
np.savez("data.npz", x=x, y=y)                        # many arrays
np.savez_compressed("data.npz", x=x, y=y)             # compressed
data = np.load("data.npz"); data["x"]
np.savetxt("a.csv", a, delimiter=","); np.loadtxt("a.csv", delimiter=",")
```

---

## 18. Analytics recipes (put it together)

```python
# standardise (z-score) each column
z = (m - m.mean(axis=0)) / m.std(axis=0)

# min-max scale each column to [0, 1]
scaled = (m - m.min(axis=0)) / m.ptp(axis=0)

# returns from a price series
returns = prices[1:] / prices[:-1] - 1

# annualised volatility of daily returns
ann_vol = returns.std() * np.sqrt(252)

# simple moving average (window w) via cumulative sum
csum = np.cumsum(np.insert(prices, 0, 0))
sma = (csum[w:] - csum[:-w]) / w

# rolling windows without a loop (NumPy >= 1.20)
from numpy.lib.stride_tricks import sliding_window_view
windows = sliding_window_view(prices, w)        # shape (n-w+1, w)
roll_mean = windows.mean(axis=1)

# one-hot encode integer labels
onehot = np.eye(n_classes)[labels]

# clip outliers to the 1st and 99th percentile
lo, hi = np.percentile(a, [1, 99])
a_clipped = np.clip(a, lo, hi)

# pairwise differences (broadcasting)
diff = a[:, None] - a[None, :]
```

---

## 19. Constants and display

```python
np.pi; np.e; np.inf; np.nan; np.newaxis
np.set_printoptions(precision=3, suppress=True)   # tidy float printing
```

---

## Golden rules

- Think in whole arrays, not loops: vectorise with ufuncs and broadcasting.
- `axis=0` reduces down the rows (per column); `axis=1` reduces across columns (per row).
- Slicing gives a view; boolean and fancy indexing give a copy. Use `.copy()` when unsure.
- Use `default_rng` for random, and a seed for reproducibility.
- NaN needs float arrays and the `nan*` aggregations; guard with `np.isnan`.
