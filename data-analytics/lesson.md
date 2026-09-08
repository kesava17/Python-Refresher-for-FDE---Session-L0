# Data Analytics with Python

> Data analytics is turning raw data into understanding a person can act on: load it, clean
> it, explore it, compute what matters, and present the finding. This chapter teaches that end
> to end in Python, worked on real-shaped market data, in a Jupyter notebook.
>
> **The concepts are in this chapter and on the slides; the complete analysis runs in the live
> lab notebook.** By the end you have one reproducible notebook that takes a basket of tickers
> from raw prices to a presented finding.

This is the chapter for the Data Analytics topic. You can read it on its own. The idea is
simple to state: most of the value in working with data is not a clever model, it is getting
the data into shape, asking a sharp question, computing the right summary, and presenting the
answer so a decision-maker acts on it. That is analytics, and Python is the language it is done
in.

We work on **stock and market data**, because a price series is a rich, intuitive time series
that everyone can reason about: prices go up and down, some move together, some are steadier
than others. The tickers are fictional (ACME, GLOBEX, INITECH) and the prices are synthetic, so
nothing here is market advice. This chapter is **descriptive and exploratory analytics, and
presentation**. It does not predict a price and does not recommend a trade; prediction is
machine learning, a later topic.

As you read, look for the **Try it** notes. Each points at a cell in the live lab notebook
(`code/data-analytics/liveLab/notebook.ipynb`). Stop, run the cell, and watch the idea happen
on real data. Run the notebook top to bottom from a clean kernel (Kernel then Restart and Run
All); a notebook that only works in a secret cell order is not a result.

## Objective

After this chapter you can:

- Work in a **Jupyter notebook** reproducibly: cells, the kernel, and restart-and-run-all.
- Use **NumPy and pandas** (and know when to reach for **Polars**) to load, clean, transform,
  reshape, and aggregate real data.
- Recognise the main **database technologies** and reason about which store to pick for a need,
  with the pros and cons.
- Run **time-series analytics** on stock data: returns, resampling, rolling windows, moving
  averages, volatility, and correlations.
- Choose and build the **right chart**, and turn an analysis into a **presentation**: a clean,
  narrated notebook and an exported report.

## Coverage

Five levels, each answering a question the previous one raises, on one running dataset:

1. **The analytics workflow and the notebook.** What analytics is, the path from question to
   finding, and Jupyter as the place it happens.
2. **Managing data with the Python libraries.** NumPy and pandas: load, clean, reshape, and the
   time-series moves.
3. **Database technologies and the architecture decision.** Where the data lives, the families,
   and how to pick one.
4. **Analytics on stock data.** Returns, moving averages, volatility, and correlations.
5. **Presentation.** The right chart, presentation design, and the notebook as a report.

At the end there is a recap, the live lab, and two offline assignments.

---

## Level 1: The analytics workflow and the notebook

### 1.1 What data analytics is

It helps to place analytics next to its neighbours. **Data engineering** moves data from where
it is produced into a clean, queryable shape; it is the plumbing. **Machine learning** predicts
the unseen: what will happen next. **Data analytics** sits between them: it explores and
describes what the data already says, so a person understands it and decides. This chapter is
analytics, and only analytics.

The output of an analysis is not a table. It is a **claim a decision-maker can read**, backed
by a clear chart. "INITECH grew the most last year but swung the hardest; GLOBEX was the
steadiest." That sentence is the analysis; the numbers and the chart back it up.

### 1.2 The analytics workflow

Every analysis, however small, walks the same path: **question, acquire, clean, explore,
analyse, present.** The most common mistake is to skip the first step. A sharp question ("which
ticker was steadiest last year?") decides what to load and what to compute; without it you
drift through the data producing charts nobody asked for.

### 1.3 Jupyter: where the analysis lives

A Jupyter notebook is code, its output, and a written narrative in one document. Code cells run
against a live **kernel** that holds state (your loaded data, your variables); markdown cells
carry the story. You run a cell, look at the result, and adjust, which is exactly how
exploration feels.

That power is also the trap. Cells can be run out of order, so a notebook can show a result
that its code no longer produces. **The one discipline: restart and run all** before you trust
or share a notebook. If it does not run top to bottom from a clean kernel, it is not a result.

> **Try it.** Open the live lab notebook and run the first two cells (the imports, then the
> load). You now have a `prices` DataFrame, one row per day, one column per ticker.

---

## Level 2: Managing data with the Python libraries

Loading, cleaning, and reshaping is most of the job, and doing it well is the difference between
a trustworthy analysis and a wrong one.

### 2.1 NumPy: the numeric foundation

pandas is built on **NumPy**, whose one big idea is **vectorisation**: operate on a whole array
at once instead of looping element by element. `values * 100` is one fast operation on the whole
array. Returns, moving averages, and volatility are all whole-column math, so they are a line
each and fast on years of data.

### 2.2 pandas: Series, DataFrame, and the DatetimeIndex

A **Series** is one labelled column; a **DataFrame** is many columns sharing an index. For
market data the index is the **date**, and indexing by date is what unlocks the time-series
tools. The most common data bug is a price column read as text; check your dtypes early.

### 2.3 Cleaning, then deriving returns

Real data has gaps and disorder. Sort by date, drop empty days, and **forward-fill** a missing
price (carry the last known value over the gap). Then turn prices into **returns** with
`pct_change`. Returns are the key move: a 210-rupee ticker and a 50-rupee ticker are not
comparable in price, but their percent returns are, and returns are the unit almost everything
downstream uses.

> **Try it.** Run the clean cell and the returns cell. Notice the deliberate gap in the CSV is
> filled by `ffill`, and that `returns` has one fewer row than `prices` (the first day has no
> prior day to compare against).

### 2.4 The time-series moves: resample, roll, shift

Three pandas moves do most of the time-series work on a date-indexed frame:

- **resample** changes the frequency: `prices.resample("M").last()` turns daily into monthly.
- **rolling** applies a moving window: `prices.rolling(50).mean()` is the 50-day average.
- **shift** looks back a period: `prices / prices.shift(1) - 1` is the change since yesterday.

Moving averages, monthly returns, and volatility windows are all one of these three.

### 2.5 When data grows: Polars and DuckDB

pandas is the default. When a dataset outgrows comfort, **Polars** is a faster columnar
dataframe with a similar API, and **DuckDB** runs SQL directly on a file or a dataframe, in
process, with no server. Both keep you inside the notebook.

---

## Level 3: Database technologies and the architecture decision

Our notebook loads a CSV, but in the enterprise this data lives in a database first, and the
store shapes what is fast, what is possible, and what it costs. This level is the practical
"know the options and how to choose"; the deep treatment (modeling, master data, consistency
theory, scaling, and architecture patterns) is the AI for Data Engineers course.

### 3.1 First split: OLTP versus OLAP

Two jobs pull opposite ways. **OLTP** stores are built for many small transactions, one record
at a time, kept correct by ACID; they are the system of record behind an application, and are
row-oriented. **OLAP** stores are built for large scans and aggregates over millions of rows;
they answer questions and are columnar. This is why analytics reads from a warehouse or a
columnar copy, not the live operational database: so it never slows the system that produces
the data.

### 3.2 The database families, and how to pick

There is no best database, only the right one for four questions: the **access pattern**, the
**consistency** need, the **scale**, and the **cost**. Three headline trade-offs decide most of
it: **ACID versus BASE** (strict correctness or relaxed consistency to scale), **row versus
columnar** (whole-record reads or column scans), and **SQL versus NoSQL** (a fixed schema with
joins or a flexible shape modelled to one query). The slides give a slide per family with its
pros and cons; keep the trade-off table close when you make the call.

### 3.3 For analytics specifically

An analyst pulls from a warehouse, a columnar store, or a lake. On a laptop, the practical fast
path is an open columnar file format (**Parquet**) plus an in-process columnar engine
(**DuckDB**): warehouse-style scan speed with no server.

> **Try it.** Run the store-aware cell. It writes the returns to a Parquet file and scans them
> with DuckDB. The same numbers, from a layout built for the scan.

---

## Level 4: Analytics on stock data

With returns in hand, we describe the basket: how much each ticker moved, how steadily, and how
together.

### 4.1 Describe the returns

Two numbers frame any return series: the **mean** (the typical daily move) and the
**volatility** (how much it swings, the standard deviation). Higher volatility is a bumpier ride
for the same average return, so comparing mean against volatility is the first honest look.
Volatility is often annualised by multiplying by the square root of the number of trading days
(about 252).

### 4.2 Trend and volatility over time

A **moving average** smooths the daily noise so you can see the direction; **rolling volatility**
(the standard deviation over a moving window) spikes in turbulent stretches; **cumulative
return** shows what holding through the whole period would have done.

### 4.3 Compare the basket: correlation and rebasing

**Correlation** measures how the tickers' returns move together, from minus one to one; low
correlation is the whole idea behind not putting everything in one place. **Rebasing** sets
every series to 100 at the start so the shapes are comparable regardless of price: rebased to
100, the lines show who actually grew more.

### 4.4 Descriptive indicators, not signals

A few classic constructs (a moving-average crossover, bands around a moving average, the
**drawdown** from a running peak) describe a series more richly. We use them to describe what a
series did, never to advise a trade.

> **Try it.** Run the summary, trend, and compare cells. Read the summary table as a sentence:
> which ticker earned the most per day, and which swung the least.

---

## Level 5: Presentation

An analysis nobody understands changed nothing. The last step is a chart and a sentence a
decision-maker acts on.

### 5.1 The right chart for the question

Each question has a chart that answers it at a glance: a **line** for movement over time, a
**bar** for a few comparisons, a **histogram** for a distribution, a **heatmap** for a
correlation, and a **candlestick** for a single day's range. A correlation shown as a table of
numbers is work to read; the same thing as a heatmap is understood in a second.

### 5.2 Presentation-design principles

A chart that informs differs from one that confuses by a few habits: the title states the
**finding**, not the field name; the axes are labelled with their units; colour carries meaning,
not decoration; there is one message per chart; and the clutter (heavy gridlines, 3D, chartjunk)
is gone. Lead the reader: here is the question, here is the chart that answers it, here is the
one sentence it proves.

### 5.3 The notebook is the report

A finished notebook is already a document: narrative, code, and charts in order. `nbconvert`
turns it into HTML, PDF, or slides, so a reader needs no Python to follow the finding. For a
presentation to an audience, lift the key charts into the GuildTrek deck: the concept on the
slide, the evidence from the notebook.

> **Try it.** Run the presentation cells to produce the correlation heatmap, the rebased
> performance line, and the moving-average chart. Then write the one-paragraph finding in the
> last markdown cell.

---

## Recap

- Analytics turns data into a finding: question, acquire, clean, explore, analyse, present.
- Jupyter is where it happens; restart-and-run-all is the discipline that keeps it honest.
- NumPy and pandas load, clean, reshape, and do the time-series work; returns are the unit.
- The store matters: OLTP versus OLAP, the database families, and the pick by access pattern,
  consistency, scale, and cost; Parquet plus DuckDB is the analyst's fast local path.
- Returns, moving averages, volatility, correlation, and rebasing describe a basket honestly.
- The right chart and a few design habits turn the analysis into a report people act on.

## Live lab and assignments

The **live lab** is the notebook at `code/data-analytics/liveLab/notebook.ipynb`, run on the
bundled `data/prices.csv`. It takes the basket from raw prices to a presented finding, and runs
top to bottom from a clean kernel.

Two **assignments** carry the ideas further, each ending in a presented finding:

1. **Single-ticker deep dive.** Fully analyse one ticker: returns, moving averages, rolling
   volatility, and drawdown, presented with three clear charts and a written summary.
2. **Multi-ticker comparison.** Compare the basket: rebased performance, a correlation heatmap,
   and a ranked table of return against volatility, presented for a decision-maker.

Both must run clean end to end and read as a report a non-analyst could follow.
