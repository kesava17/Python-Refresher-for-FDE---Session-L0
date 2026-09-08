---
marp: true
size: 16:9
paginate: true
title: Data Analytics with Python
author: GuildTrek
---
<style>
/* GuildTrek brand: indigo -> emerald gradient, amber accent, cool ink on a
   cool off-white. Fonts: Space Grotesk / Inter / JetBrains Mono.
   Story deck: a marketing/sales narrative version of the course deck. */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
  --ink: #0F172A;
  --ink-soft: #334155;
  --primary: #4F46E5;
  --primary-600: #4338CA;
  --neon: #10B981;
  --neon-600: #059669;
  --accent: #F59E0B;
  --muted: #64748B;
  --bg: #F8FAFC;
  --panel: #FFFFFF;
  --panel-cool: #EEF2FF;
  --border: #E2E8F0;
}

section {
  font-family: 'Inter', "Segoe UI", system-ui, sans-serif;
  font-size: 21px;
  color: var(--ink);
  background: var(--bg);
  padding: 46px 60px;
  line-height: 1.4;
}

h1, h2, h3, .big { font-family: 'Space Grotesk', 'Inter', sans-serif; letter-spacing: -0.02em; }
h1 { font-size: 42px; color: var(--ink); margin: 0 0 10px; font-weight: 600; }
h2 {
  font-size: 30px; color: var(--ink); margin: 0 0 14px; font-weight: 600; display: inline-block;
  padding-bottom: 8px; border-bottom: 3px solid transparent;
  border-image: linear-gradient(90deg, var(--primary), var(--neon)) 1;
}
h3 { font-size: 19px; color: var(--primary-600); margin: 0 0 6px; font-weight: 600; }
strong { color: var(--ink); }
a { color: var(--primary-600); }
ul, ol { margin: 4px 0; padding-left: 22px; }
li { margin: 4px 0; }
li::marker { color: var(--neon-600); }
em { color: var(--muted); font-style: italic; }

table { border-collapse: collapse; width: 100%; font-size: 17px; margin-top: 4px; }
th { background: var(--ink); color: #EEF2FF; text-align: left; padding: 7px 12px; font-weight: 600; }
td { border-bottom: 1px solid var(--border); padding: 7px 12px; vertical-align: top; }
tr:nth-child(even) td { background: var(--panel-cool); }

blockquote {
  border: none; border-left: 5px solid var(--neon); background: var(--panel-cool);
  padding: 12px 17px; color: var(--ink-soft); font-size: 19px; border-radius: 6px; margin: 10px 0;
}

section::after { color: #A9B2C4; font-size: 14px; font-weight: 600; }

.kicker {
  font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.22em;
  font-size: 15px; text-transform: uppercase;
  background: linear-gradient(100deg, var(--primary), var(--neon)); -webkit-background-clip: text;
  background-clip: text; color: transparent;
}
.grad {
  background: linear-gradient(100deg, var(--neon), var(--primary) 70%); -webkit-background-clip: text;
  background-clip: text; color: transparent;
}
.muted { color: var(--muted); }
.big { font-size: 44px; line-height: 1.08; margin: 12px 0; font-weight: 600; }

.columns { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.columns3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
.card {
  background: var(--panel); border: 1px solid var(--border); border-left: 5px solid var(--primary);
  border-radius: 8px; padding: 12px 16px;
}
.card.neon { border-left-color: var(--neon); }
.card.amber { border-left-color: var(--accent); }
.card h3 { margin-top: 0; }
.card p { margin: 5px 0 0; }
.card ul { margin: 4px 0 0; }

.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 16px; }
.stat { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 15px 10px; text-align: center; }
.stat b {
  display: block; font-family: 'Space Grotesk', sans-serif; font-size: 34px; line-height: 1; margin-bottom: 5px;
  background: linear-gradient(120deg, var(--neon), var(--primary)); -webkit-background-clip: text; background-clip: text; color: transparent;
}
.stat span { color: var(--muted); font-size: 14px; }

.pill { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--primary-600); background: var(--panel-cool); border: 1px solid var(--border); border-radius: 999px; padding: 3px 12px; margin-bottom: 8px; }

.flow { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin: 12px 0; }
.flow .step { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 7px 13px; font-weight: 600; font-size: 15px; }
.flow .step.hot { border-color: var(--neon); color: var(--neon-600); }
.flow .step.human { border-color: var(--accent); color: #B45309; background: #FFFBEB; }
.flow .arrow { color: var(--primary); font-weight: 800; font-size: 18px; }

.chips { display: flex; flex-wrap: wrap; gap: 7px; margin: 10px 0; align-items: center; }
.chip {
  background: var(--panel-cool); border: 1px solid var(--border); color: var(--ink-soft);
  border-radius: 999px; padding: 6px 12px; font-weight: 600; font-size: 15px;
}
.chip.hot { background: linear-gradient(100deg, rgba(79,70,229,.12), rgba(16,185,129,.12)); border-color: rgba(79,70,229,.35); color: var(--primary-600); }
.tag { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-right: 2px; }

.proof { border: none; border-left: 5px solid var(--accent); background: #FFFBEB; padding: 9px 15px; border-radius: 6px; font-size: 17px; color: var(--ink-soft); margin-top: 10px; }
.proof b { color: #B45309; font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; display: inline-block; margin-right: 6px; }

.horizon { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-top: 10px; }
.hz { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; border-top: 5px solid var(--primary); color: var(--ink-soft); }
.hz ul, .hz li { color: var(--ink-soft); }
.hz:nth-child(2) { border-top-color: var(--neon); }
.hz:nth-child(3) { border-top-color: var(--accent); }
.hz .when { font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.hz h3 { margin: 4px 0 8px; }
.hz ul { padding-left: 17px; font-size: 17px; }

.ladder { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
.rung { display: grid; grid-template-columns: 150px 1fr; gap: 12px; align-items: center; background: var(--panel); border: 1px solid var(--border); border-left: 5px solid var(--primary); border-radius: 8px; padding: 8px 13px; }
.rung:nth-child(3n+2) { border-left-color: var(--neon); }
.rung:nth-child(3n) { border-left-color: var(--accent); }
.rung .stage { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px; }
.rung .stage small { display: block; font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
.rung .what { font-size: 16px; color: var(--ink-soft); }

.rolemix { display: flex; flex-direction: column; gap: 7px; margin-top: 10px; }
.role { display: grid; grid-template-columns: 220px 1fr 46px; gap: 12px; align-items: center; }
.role .rn { font-weight: 600; font-size: 15px; color: var(--ink); }
.role .rn small { color: var(--muted); font-weight: 500; }
.role .rbar { height: 15px; background: var(--panel-cool); border: 1px solid var(--border); border-radius: 999px; overflow: hidden; }
.role .rfill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--neon)); border-radius: 999px; }
.role .rpct { font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 14px; color: var(--primary-600); text-align: right; }

.learn { display: flex; flex-direction: column; gap: 5px; margin-top: 6px; }
.lrow { display: grid; grid-template-columns: 168px 1fr; gap: 12px; align-items: center; background: var(--panel); border: 1px solid var(--border); border-left: 4px solid var(--primary); border-radius: 8px; padding: 6px 12px; }
.lrow:nth-child(3n+2) { border-left-color: var(--neon); }
.lrow:nth-child(3n) { border-left-color: var(--accent); }
.lrow .topic { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px; line-height: 1.15; }
.lrow .topic small { display: block; font-family: 'JetBrains Mono', monospace; font-size: 9.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-top: 1px; }
.lrow .body { font-size: 14px; color: var(--ink-soft); }
.lrow .tks { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.tk { display: inline-flex; align-items: center; gap: 5px; background: var(--panel-cool); border: 1px solid var(--border); border-radius: 6px; padding: 2px 8px; font-size: 12px; font-weight: 600; color: var(--ink-soft); }
.tk::before { content: ''; width: 9px; height: 9px; border-radius: 2px; background: var(--d, #4F46E5); display: inline-block; }

.split { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 22px; align-items: start; margin-top: 6px; }
.wallcap { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin: 2px 0 10px; }
.logowall { display: flex; flex-wrap: wrap; gap: 12px 13px; align-content: flex-start; }
.logo { display: flex; flex-direction: column; align-items: center; gap: 5px; width: 76px; }
.logo .mark { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 19px; color: #fff; background: var(--d, #4F46E5); box-shadow: 0 3px 8px rgba(15,23,42,.16); letter-spacing: -.02em; }
.logo .ln { font-size: 11.5px; color: var(--ink-soft); font-weight: 600; text-align: center; line-height: 1.1; }
.logo .mark.img { background: #fff; border: 1px solid var(--border); box-shadow: 0 2px 6px rgba(15,23,42,.10); }
.logo .mark.img img { max-width: 38px; max-height: 34px; width: auto; height: auto; display: block; }

.piewrap { display: grid; grid-template-columns: 270px 1fr; gap: 28px; align-items: center; margin-top: 14px; }
.pie { width: 240px; height: 240px; border-radius: 50%; margin: 0 auto; border: 1px solid var(--border); box-shadow: 0 5px 18px rgba(15,23,42,.12); }
.legend { display: flex; flex-direction: column; gap: 10px; }
.lg { display: grid; grid-template-columns: 16px 1fr 50px; gap: 11px; align-items: center; font-size: 16px; }
.lg .dot { width: 15px; height: 15px; border-radius: 4px; }
.lg .lbl { color: var(--ink); font-weight: 600; }
.lg .lbl small { color: var(--muted); font-weight: 500; display: block; font-size: 12px; }
.lg .pct { font-family: 'JetBrains Mono', monospace; color: var(--primary-600); font-weight: 700; text-align: right; font-size: 17px; }

section.lead, section.divider, section.dark {
  background:
    radial-gradient(120% 120% at 85% 12%, rgba(79,70,229,0.30), transparent 46%),
    radial-gradient(120% 120% at 8% 92%, rgba(16,185,129,0.22), transparent 50%),
    linear-gradient(135deg, #0B1020 0%, #131A31 55%, #0A0E1A 100%);
  color: #E6EAF5;
}
section.lead h1, section.divider h1, section.dark h1,
section.lead h2, section.divider h2, section.dark h2 { color: #fff; border: none; padding: 0; }
section.divider h2, section.dark h2 {
  border-bottom: 3px solid transparent;
  border-image: linear-gradient(90deg, var(--primary), var(--neon)) 1;
  padding-bottom: 8px; display: inline-block;
}
section.lead strong, section.divider strong, section.dark strong { color: #fff; }
section.lead .muted, section.divider .muted, section.dark .muted { color: #AEB6CC; }
section.lead::after, section.divider::after, section.dark::after { color: #6B7488; }
section.divider .pill, section.dark .pill { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.18); color: #C7D2FE; }
section.dark .card, section.divider .card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); }
section.dark .card h3, section.divider .card h3 { color: #C7D2FE; }
section.dark li { margin: 6px 0; }
section.dark li::marker { color: var(--neon); }
section.dark .stat, section.divider .stat { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); }

.deck-logo { height: 50px; display: block; margin-bottom: 18px; }
.brandmark { position: absolute; top: 32px; right: 54px; height: 27px; opacity: .9; }
.brandlite { color: #A5B4FC; font-weight: 700; }
section.lead h3, section.divider h3, section.dark h3 { color: #C7D2FE; }

section.dark blockquote, section.divider blockquote, section.lead blockquote { color: var(--ink-soft); }
section.dark blockquote strong, section.divider blockquote strong, section.lead blockquote strong { color: var(--ink); }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Python for AI and Data Engineering &middot; Data Analytics</span>

# Data Analytics with Python

### <span class="muted">Turn raw data into understanding and a presentation,</span> <span class="brandlite">with the Python data stack, in Jupyter, on real market data.</span>

<p class="muted" style="font-size: 22px; max-width: 52ch; margin-top: 14px;">The concepts are on these slides. The complete analysis runs live in a Jupyter notebook, one we build end to end on a basket of stocks.</p>

---

## What we will learn today

<div class="chips">
<span class="tag">five levels</span>
<span class="chip hot">Databases + the pick</span>
<span class="chip hot">Workflow + Jupyter</span>
<span class="chip">The data libraries</span>
<span class="chip">Analytics</span>
<span class="chip">Presentation</span>
</div>

<div class="learn">
<div class="lrow"><div class="topic">Level 1<small>Databases + the pick</small></div><div class="body">The database technologies behind the data, and the architecture decision, which to pick, pros and cons.</div></div>
<div class="lrow"><div class="topic">Level 2<small>Workflow + the notebook</small></div><div class="body">What analytics is, the workflow from question to finding, and Jupyter as the place it happens.</div></div>
<div class="lrow"><div class="topic">Level 3<small>The data libraries</small></div><div class="body">NumPy and pandas to load, clean, reshape, and aggregate, with Polars for scale.</div></div>
<div class="lrow"><div class="topic">Level 4<small>Analytics on stock data</small></div><div class="body">Returns, moving averages, volatility, and correlations across a basket of tickers.</div></div>
<div class="lrow"><div class="topic">Level 5<small>Presentation</small></div><div class="body">The right chart, presentation design, and the notebook as a shareable report.</div></div>
</div>

---

## How this runs: slides teach, the notebook does

<p class="muted">Two surfaces, one story. The slide gives the concept; the notebook runs the analysis on real data. By the end we have <strong>one complete stock-analytics notebook</strong>.</p>

<div class="columns">
<div class="card"><h3>On the slide</h3><p>The concept, the choice, and the shape of the code: what to do and why.</p></div>
<div class="card neon"><h3>In the notebook</h3><p>The same idea, run on the data, with the output and the chart in front of you.</p></div>
</div>

<div class="proof"><b>Watch for the tag</b> A <span class="pill" style="margin:0">notebook</span> slide means "open the notebook and run this cell." The data is a bundled sample of daily prices for a basket of fictional tickers (ACME, GLOBEX, INITECH), so nothing here is market advice.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Level 1 &middot; Databases and the architecture decision</span>

## The stores behind the data, and how to pick

<p class="muted">Before we load a thing, know where enterprise data lives and how an architect chooses a store: it shapes what is fast, what is possible, and what it costs.</p>

---

## First split: OLTP vs OLAP

<p class="muted">Two jobs pulling opposite ways, which is why analytics rarely reads from the live application database.</p>

<div class="columns">
<div class="card"><h3>OLTP: transactions</h3><p>Many small reads and writes, one record at a time, kept correct by ACID. The system of record behind the app.</p><p class="muted">Row-oriented. "Record this trade."</p></div>
<div class="card neon"><h3>OLAP: analytics</h3><p>Large scans and aggregates over millions of rows. Built to answer questions, not record transactions.</p><p class="muted">Columnar. "Average return by month."</p></div>
</div>

<div class="proof"><b>The rule of thumb</b> Analytics reads from a warehouse, a columnar store, or a lake, a copy shaped for scans, so it never slows the operational system that produces the data.</div>

---

## The database landscape: relational to specialized

<p class="muted">From RDBMS all the way up. Every one is a source you read or a target you write; pick by the access pattern.</p>

| Family | Built for | Example |
| --- | --- | --- |
| Relational (RDBMS) | System of record, ACID, SQL | PostgreSQL, MySQL, SQLite |
| Key-value | Speed, scale, caching | Redis, DynamoDB |
| Document | Flexible, varying record shapes | MongoDB |
| Wide-column | Very high write volume | Cassandra, Bigtable |
| Graph | Connected, relationship queries | Neo4j |
| Time-series | Timestamped measurements at rate | InfluxDB, TimescaleDB |
| Search | Full-text and fast filtering | Elasticsearch |
| Columnar / warehouse | Large analytical scans | DuckDB, ClickHouse, BigQuery, Snowflake |
| Distributed SQL | Relational, scaled horizontally | CockroachDB, Spanner |
| Object store + formats | Cheap raw storage for a lake | S3 with Parquet |
| Vector | Similarity search on embeddings | pgvector, Milvus |

---

## Relational (RDBMS)

<p class="muted">Tables with a fixed schema, related by keys, queried with SQL, kept correct by ACID transactions. The default system of record.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>System of record for structured, related data</li><li>Transactions that must be correct (orders, ledgers)</li><li>Ad-hoc querying and reporting in SQL</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Normalise the schema, then index for reads</li><li>Model relationships with keys and constraints</li><li>Plan migrations for schema change</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> correctness, joins, mature tooling.</p><p><strong>Con:</strong> horizontal write scaling is hard; the schema is rigid.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> PostgreSQL, MySQL, SQLite, Oracle, SQL Server.</p>

---

## Key-value

<p class="muted">A simple map from a key to a value, built for speed and scale.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Caching and session storage</li><li>Feature flags and configuration</li><li>Anything fetched fast by a known key</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Design the key namespace deliberately</li><li>Set TTLs for expiry</li><li>Store what you read (the value is opaque)</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> microsecond lookups, simple, scales.</p><p><strong>Con:</strong> no queries or joins; fetch by key only.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> Redis, DynamoDB, Memcached.</p>

---

## Document

<p class="muted">Schema-flexible, JSON-like documents; each record can vary in shape.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Catalogs, user profiles, content, CMS</li><li>Evolving or varied record shapes</li><li>Read or write a whole object at a time</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Embed vs reference (keep together or link)</li><li>Model to your read pattern, not the entity</li><li>Design for the aggregate you fetch</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> flexible shapes, whole-object reads.</p><p><strong>Con:</strong> weak joins; easy to model badly; duplication.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> MongoDB, Couchbase, Firestore.</p>

---

## Wide-column

<p class="muted">Rows with flexible columns, spread across many machines for very high write volume.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Event logs and IoT at scale</li><li>Messaging and activity feeds</li><li>Time-partitioned, high-write data</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Model the table to the query first</li><li>Choose partition and clustering keys</li><li>Denormalise per access path</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> huge write throughput, linear scale.</p><p><strong>Con:</strong> no ad-hoc joins; patterns fixed up front.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> Cassandra, HBase, Bigtable.</p>

---

## Graph

<p class="muted">Data as nodes and the relationships (edges) between them.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Fraud rings and network analysis</li><li>Social graphs and recommendations</li><li>Knowledge graphs</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Model nodes, edges, and properties</li><li>Shape edges for the traversals you run</li><li>Index the traversal start points</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> fast, expressive relationship traversals.</p><p><strong>Con:</strong> niche; poor at bulk scans and aggregates.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> Neo4j, Amazon Neptune.</p>

---

## Time-series

<p class="muted">Tuned for timestamped measurements arriving at a high rate.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Metrics and monitoring</li><li>Sensor and IoT telemetry</li><li>Market ticks and any time-stamped feed</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Choose tags and timestamp granularity</li><li>Set retention and downsampling</li><li>Batch the writes</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> fast ingest, range and rollup queries, great compression.</p><p><strong>Con:</strong> narrow; only time-stamped data.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> InfluxDB, TimescaleDB, Prometheus.</p>

---

## Search

<p class="muted">Inverted-index stores for full-text search and fast filtering and ranking.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Site and product search</li><li>Log and observability analytics</li><li>Faceted filtering</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Design the index mapping and analyzers</li><li>Denormalise documents for search</li><li>Keep the source of truth elsewhere</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> full-text relevance, fast filtering at scale.</p><p><strong>Con:</strong> eventually consistent; not a system of record.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> Elasticsearch, OpenSearch.</p>

---

## Columnar and warehouse

<p class="muted">Data stored by column for large analytical scans and aggregates. The analyst's home (OLAP).</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Analytics, dashboards, and BI</li><li>Aggregates over large history</li><li>Where this topic's work lives</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Dimensional model (star schema)</li><li>Partition and cluster for scans</li><li>Load in batches, not row by row</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> fast large scans and aggregates, strong compression.</p><p><strong>Con:</strong> not for many small writes or point lookups.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> DuckDB, ClickHouse, BigQuery, Snowflake, Redshift.</p>

---

## Distributed SQL (NewSQL)

<p class="muted">Relational and ACID, but scaled horizontally across many machines.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Global, always-on applications</li><li>Relational correctness beyond one machine</li><li>High-availability systems of record</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Pick a key that spreads load evenly</li><li>Place data by region</li><li>Accept consensus latency on writes</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> ACID at horizontal scale, high availability.</p><p><strong>Con:</strong> operational complexity; write latency.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> CockroachDB, Spanner, YugabyteDB.</p>

---

## Object storage and file formats

<p class="muted">Cheap, effectively unlimited file storage, with open columnar formats (Parquet) as the data layer of a lake.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>The data lake: raw and large data</li><li>Cheap, open storage for analytics</li><li>Storage decoupled from compute</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Partition the layout (usually by date)</li><li>Pick a columnar format (Parquet)</li><li>Add a table format (Iceberg, Delta) for ACID</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> cheap, open, unlimited scale.</p><p><strong>Con:</strong> needs a query engine; no transactions without a table format.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> Amazon S3, Azure Blob, with Parquet, ORC, or Avro.</p>

---

## Vector

<p class="muted">Stores embeddings (vectors) and finds the nearest ones by similarity.</p>

<div class="columns3">
<div class="card"><h3>Right use cases</h3><ul><li>Semantic search</li><li>Retrieval for AI (RAG)</li><li>Recommendations by similarity</li></ul></div>
<div class="card neon"><h3>Design choices</h3><ul><li>Pick the embedding model and dimension</li><li>Choose the index (HNSW or IVF) and metric</li><li>Tune recall against latency</li></ul></div>
<div class="card amber"><h3>Pros and cons</h3><p><strong>Pro:</strong> fast similarity search over embeddings.</p><p><strong>Con:</strong> approximate; a storage choice, not a model; often paired.</p></div>
</div>

<p class="muted"><span class="tag">examples</span> pgvector, Milvus, Pinecone, Weaviate.</p>

---

## The architecture decision: how to pick

<p class="muted">There is no best database, only the right one for four questions. Answer them, and the family follows.</p>

<div class="flow">
  <span class="step hot">Access pattern</span>
  <span class="step hot">Consistency</span>
  <span class="step hot">Scale</span>
  <span class="step hot">Cost</span>
</div>

<div class="columns3">
<div class="card"><h3>ACID vs BASE</h3><p>Strict correctness on every write, or relaxed consistency to scale and stay available. Money wants ACID; a feed can accept BASE.</p></div>
<div class="card neon"><h3>Row vs columnar</h3><p>Read whole records (operational), or scan a few columns over millions of rows (analytics). It decides read speed.</p></div>
<div class="card amber"><h3>SQL vs NoSQL</h3><p>A fixed schema and joins, or a flexible shape modelled to one query. Structure and querying vs flexibility and scale.</p></div>
</div>

<div class="proof"><b>One line to carry</b> Match the store to the access pattern and the correctness need first; scale and cost then narrow the choice within a family.</div>

---

## Pros and cons by family

<p class="muted">The short version an architect keeps in their head.</p>

| Family | Best for | Watch out for |
| --- | --- | --- |
| Relational | Correctness, joins, the default | Scaling writes horizontally is hard |
| Key-value | Blazing lookups, caching | No rich queries; you fetch by key |
| Document | Flexible, evolving shapes | Easy to model badly; weak joins |
| Wide-column | Huge write throughput at scale | Query patterns must be designed up front |
| Graph | Relationship and path queries | Niche; not for bulk scans |
| Time-series | High-rate metrics and telemetry | Narrow; only for time-stamped data |
| Columnar / warehouse | Analytics, aggregates, BI | Not for many small writes |
| Object + Parquet | Cheap, open, huge raw data | Needs an engine on top to query |

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Level 2 &middot; Workflow and the notebook</span>

## What analytics is, and where it happens

<p class="muted">Before a single chart, the shape of the work, and the tool it is done in.</p>

---

## What data analytics is

<p class="muted">Analytics turns raw data into understanding a person can act on. It is neither moving data nor predicting it.</p>

<div class="columns3">
<div class="card"><h3>Data engineering</h3><p>Gets data from where it is into a clean, reliable, queryable shape. The plumbing.</p><p class="muted">Not this topic.</p></div>
<div class="card neon"><h3>Data analytics</h3><p>Explores and describes: what happened, and what the data says. The understanding.</p><p class="muted">This topic.</p></div>
<div class="card amber"><h3>Machine learning</h3><p>Predicts the unseen: what will happen next. A model, trained.</p><p class="muted">A later topic, not here.</p></div>
</div>

<div class="proof"><b>Our lane</b> Descriptive and exploratory analytics, and presenting it. No prediction, and no trading or investment advice.</div>

---

## The analytics workflow

<p class="muted">Every analysis, however small, walks the same path. Naming it keeps a notebook honest.</p>

<div class="flow">
  <span class="step">question</span><span class="arrow">&rarr;</span>
  <span class="step">acquire</span><span class="arrow">&rarr;</span>
  <span class="step">clean</span><span class="arrow">&rarr;</span>
  <span class="step hot">explore</span><span class="arrow">&rarr;</span>
  <span class="step">analyse</span><span class="arrow">&rarr;</span>
  <span class="step">present</span>
</div>

<div class="columns">
<div class="card"><h3>Start with the question</h3><p>"Which ticker was steadiest last year?" A sharp question decides what to load and what to compute.</p></div>
<div class="card neon"><h3>End with the finding</h3><p>The output is not a table; it is a claim a decision-maker can read, backed by a clear chart.</p></div>
</div>

---

## Jupyter: where the analysis lives

<p class="muted">A notebook is code, its output, and a written narrative in one document. It is built for exploring, and it doubles as the report.</p>

<div class="columns">
<div class="card"><h3>Cells and the kernel</h3><p>Code cells run against a live <strong>kernel</strong> that holds state; markdown cells carry the story. You run, look, and adjust.</p></div>
<div class="card amber"><h3>The one discipline</h3><p>Cells can run out of order, so results can lie. <strong>Restart and run all</strong> before you trust or share a notebook.</p></div>
</div>

<div class="proof"><b>Reproducible or it did not happen</b> A notebook that only works if you run the cells in a secret order is not a result. Top to bottom, from a clean kernel, every time.</div>

---

## The Python data stack, mapped

<p class="muted">A handful of libraries, each with a job. Know which reaches for which.</p>

<div class="columns">
<div class="card"><h3>Manage the data</h3><ul><li><strong>NumPy</strong>: fast numeric arrays, the foundation</li><li><strong>pandas</strong>: labelled tables and time series</li><li><strong>Polars</strong>: a faster dataframe for scale</li></ul></div>
<div class="card neon"><h3>Present the data</h3><ul><li><strong>matplotlib</strong>: full control over a chart</li><li><strong>seaborn</strong>: quick statistical charts</li><li><strong>plotly</strong>: interactive exploration</li></ul></div>
</div>

<div class="proof"><b>Notebook first</b> All of it runs inside Jupyter, so the manage step and the present step sit in the same document as the finding.</div>

---

## notebook &middot; load the prices

<span class="pill">notebook</span>

<p class="muted"><strong>The move:</strong> read daily prices from a bundled CSV, parse the dates, and index by date so it is a real time series.</p>

```python
import pandas as pd

prices = pd.read_csv("prices.csv", parse_dates=["date"], index_col="date")
prices.head()
```

```text
            ACME   GLOBEX  INITECH
date
2023-01-03  98.20   51.10   210.4
2023-01-04  99.05   50.75   208.9
2023-01-05  97.80   51.60   212.3
```

<div class="proof"><b>What we have</b> A DataFrame, one row per day, one column per ticker, indexed by a DatetimeIndex. Everything after this is a transform on that shape.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Level 3 &middot; The data libraries</span>

## Five libraries, from one array to a cluster

<p class="muted">NumPy, pandas, Polars, Dask, and PySpark: each with what it is, its use cases and trade-offs, and a working example. The same ideas, at growing scale.</p>

---

## From one array to a cluster

<p class="muted">Five libraries, one progression. As data grows past memory and past one machine, you move up the ladder: the ideas stay, the engine changes.</p>

<div class="flow">
  <span class="step">NumPy</span><span class="arrow">&rarr;</span>
  <span class="step">pandas</span><span class="arrow">&rarr;</span>
  <span class="step hot">Polars</span><span class="arrow">&rarr;</span>
  <span class="step">Dask</span><span class="arrow">&rarr;</span>
  <span class="step">PySpark</span>
</div>

| Library | Scale | Model | Reach for it when |
| --- | --- | --- | --- |
| NumPy | one core, in memory | numeric arrays | array and matrix math |
| pandas | one core, in memory | labelled tables | everyday analytics and time series |
| Polars | many cores, in memory | columnar, lazy | pandas is too slow or memory-tight |
| Dask | out of core, cluster | parallel pandas and numpy | data bigger than RAM, scale your code |
| PySpark | distributed cluster | big-data DataFrame | very large data, enterprise pipelines |

---

## NumPy

<p class="muted">The numeric foundation: n-dimensional arrays and vectorised math. Every other library here sits on it.</p>

<div class="columns3">
<div class="card"><h3>Use cases</h3><ul><li>Array and matrix math</li><li>Linear algebra</li><li>The numeric backend for pandas, scikit-learn, and tensors</li></ul></div>
<div class="card neon"><h3>Pros</h3><ul><li>Extremely fast vectorised operations</li><li>Memory-compact</li><li>Universal, the base of numeric Python</li></ul></div>
<div class="card amber"><h3>Cons</h3><ul><li>One homogeneous type per array</li><li>No labels or columns</li><li>One machine, in memory</li></ul></div>
</div>

---

## NumPy: analytical tasks

<p class="muted">The data-analytics work you can do with NumPy, and the calls that do it.</p>

| Task | NumPy |
| --- | --- |
| Descriptive stats | mean, median, std, var, percentile, quantile |
| Aggregation | sum, prod, min, max, cumsum, cumprod (per axis) |
| Element-wise math | vectorised +, -, *, /, log, exp, sqrt |
| Filter and mask | boolean masks, where, clip, nonzero |
| Reshape and combine | reshape, transpose, concatenate, stack, split |
| Correlation and covariance | corrcoef, cov |
| Linear algebra | dot, matmul, linalg.inv, eig, svd, solve |
| Sort and search | sort, argsort, unique, searchsorted |
| Random and sampling | random.normal, choice, permutation |
| Bin and histogram | histogram, digitize, bincount |

---

## NumPy in practice

<span class="pill">practical</span>

<p class="muted"><strong>Vectorised returns and volatility</strong> on a price array, with no Python loop.</p>

```python
import numpy as np

prices = np.array([98.2, 99.0, 97.8, 98.6, 100.1])
returns = prices[1:] / prices[:-1] - 1          # whole-array math
ann_vol = returns.std() * np.sqrt(252)          # annualised volatility
```

<p class="muted"><span class="tag">top scenarios</span> element-wise math over millions of values &middot; matrix and linear-algebra work &middot; the fast array backend under pandas and ML.</p>

---

## pandas

<p class="muted">Labelled tables (Series and DataFrame) for real tabular and time-series data. The workhorse of analytics.</p>

<div class="columns3">
<div class="card"><h3>Use cases</h3><ul><li>Loading and cleaning</li><li>Reshaping, joins, and groupby</li><li>Time series and exploratory analysis</li></ul></div>
<div class="card neon"><h3>Pros</h3><ul><li>Rich, mature API and huge ecosystem</li><li>Excellent time-series tools</li><li>The default everyone knows</li></ul></div>
<div class="card amber"><h3>Cons</h3><ul><li>One machine, in memory</li><li>Slow and memory-hungry on large data</li><li>Eager: runs each step at once</li></ul></div>
</div>

---

## pandas: analytical tasks

<p class="muted">The data-analytics work you can do with pandas, and the calls that do it.</p>

| Task | pandas |
| --- | --- |
| Load and save | read_csv, read_parquet, read_sql, to_csv, to_parquet |
| Clean | dropna, fillna, ffill, drop_duplicates, astype |
| Select and filter | loc, iloc, query, boolean masks |
| Derive columns | assign, apply, map, pct_change |
| Group and aggregate | groupby().agg, transform, pivot_table |
| Join and combine | merge, join, concat |
| Reshape | pivot, melt, stack, unstack |
| Time series | resample, rolling, shift, asfreq |
| Descriptive stats | describe, mean, std, corr, value_counts |
| Window and rank | rolling, expanding, ewm, rank |

---

## pandas in practice

<span class="pill">practical</span>

<p class="muted"><strong>The returns pipeline</strong>: load prices, derive returns, and do the time-series moves. This is where the notebook creates <code>returns</code>.</p>

```python
import pandas as pd

prices = pd.read_csv("prices.csv", parse_dates=["date"], index_col="date").ffill()
returns = prices.pct_change().dropna()       # daily returns, the comparable unit
monthly = prices.resample("M").last()        # resample daily to monthly
sma_50 = prices["ACME"].rolling(50).mean()   # rolling window
```

<p class="muted"><span class="tag">top scenarios</span> clean and reshape messy data &middot; groupby and pivot &middot; join datasets &middot; resample and roll over time.</p>

---

## Polars

<p class="muted">A fast, multi-threaded, columnar DataFrame built in Rust, with lazy execution. A modern pandas alternative.</p>

<div class="columns3">
<div class="card"><h3>Use cases</h3><ul><li>Large single-machine datasets</li><li>Heavy ETL</li><li>When pandas is too slow or runs out of memory</li></ul></div>
<div class="card neon"><h3>Pros</h3><ul><li>Very fast and multi-core</li><li>A lazy engine that optimises the whole query</li><li>Lower memory use</li></ul></div>
<div class="card amber"><h3>Cons</h3><ul><li>Smaller ecosystem than pandas</li><li>A different API to learn</li><li>Younger, fewer integrations</li></ul></div>
</div>

---

## Polars: analytical tasks

<p class="muted">The data-analytics work you can do with Polars, and the calls that do it.</p>

| Task | Polars |
| --- | --- |
| Load (lazy or eager) | scan_csv, scan_parquet, read_csv |
| Select and filter | select, filter, with_columns |
| Expressions | pl.col(...).mean / sum / over, when/then |
| Group and aggregate | group_by().agg |
| Join and combine | join, concat |
| Reshape | pivot, melt, explode |
| Time series | group_by_dynamic, rolling, upsample |
| Window functions | over(), rolling_mean, rolling_std |
| Descriptive stats | describe, mean, std, corr |
| Lazy optimisation | lazy, collect, streaming collect |

---

## Polars in practice

<span class="pill">practical</span>

<p class="muted"><strong>A lazy scan and grouped aggregate</strong>: nothing runs until <code>collect()</code>, so the engine optimises the whole query.</p>

```python
import polars as pl

out = (
    pl.scan_csv("prices.csv")                              # lazy, nothing runs yet
      .with_columns(pl.col("ACME").pct_change().alias("ret"))
      .group_by(pl.col("date").dt.month())
      .agg(pl.col("ret").mean())
      .collect()                                           # now it runs, optimised
)
```

<p class="muted"><span class="tag">top scenarios</span> fast ETL on big single-machine files &middot; replacing slow pandas steps &middot; streaming a larger-than-memory scan.</p>

---

## Dask

<p class="muted">Parallel and out-of-core computing that scales NumPy and pandas across cores and a cluster, using lazy task graphs.</p>

<div class="columns3">
<div class="card"><h3>Use cases</h3><ul><li>Data bigger than RAM</li><li>Parallelising existing pandas or numpy code</li><li>Moderate clusters without a rewrite</li></ul></div>
<div class="card neon"><h3>Pros</h3><ul><li>Familiar pandas and numpy API</li><li>Scales past memory and onto clusters</li><li>Lazy and parallel</li></ul></div>
<div class="card amber"><h3>Cons</h3><ul><li>Overhead on small data</li><li>Partition tuning matters</li><li>Not as fast as Spark at the top end</li></ul></div>
</div>

---

## Dask: analytical tasks

<p class="muted">The data-analytics work you can do with Dask, and the calls that do it.</p>

| Task | Dask |
| --- | --- |
| Load many files | dd.read_csv, dd.read_parquet (globs) |
| Select and filter | pandas-like loc and boolean masks |
| Group and aggregate | groupby().agg (parallel) |
| Join | merge (partition-aware) |
| Descriptive stats | mean, std, describe (lazy) |
| Rolling and time series | rolling, resample per partition |
| Custom parallel | map_partitions, dask.delayed |
| Array analytics | dask.array, chunked numpy |
| Scale out | compute(), distributed cluster |
| Bigger than memory | out-of-core execution |

---

## Dask in practice

<span class="pill">practical</span>

<p class="muted"><strong>A pandas-like read over many files</strong>, computed in parallel and only when you ask.</p>

```python
import dask.dataframe as dd

ddf = dd.read_csv("prices-*.csv", parse_dates=["date"])   # many files, lazy
mean_ret = ddf.groupby("ticker")["ret"].mean().compute()  # runs in parallel
```

<p class="muted"><span class="tag">top scenarios</span> process a folder too big for RAM &middot; parallelise a slow groupby or apply &middot; scale existing pandas with few changes.</p>

---

## PySpark

<p class="muted">The Python API for Apache Spark: distributed data processing across a cluster, for big data.</p>

<div class="columns3">
<div class="card"><h3>Use cases</h3><ul><li>Very large datasets</li><li>Distributed ETL and data-lake pipelines</li><li>Enterprise-scale scheduled jobs</li></ul></div>
<div class="card neon"><h3>Pros</h3><ul><li>Massive horizontal scale</li><li>Mature, with SQL and DataFrame APIs</li><li>A rich ecosystem</li></ul></div>
<div class="card amber"><h3>Cons</h3><ul><li>Cluster and JVM overhead</li><li>Heavier to set up and operate</li><li>Latency on small data</li></ul></div>
</div>

---

## PySpark: analytical tasks

<p class="muted">The data-analytics work you can do with PySpark, and the calls that do it.</p>

| Task | PySpark |
| --- | --- |
| Load | spark.read.csv, read.parquet, read.jdbc |
| Select and filter | select, filter / where, withColumn |
| Group and aggregate | groupBy().agg, F.mean, F.sum, F.count |
| Join | join (broadcast and shuffle) |
| Window functions | Window with F.row_number, lag, rank |
| SQL | spark.sql, createOrReplaceTempView |
| Descriptive stats | describe, summary, corr |
| User functions | udf, pandas_udf (vectorised) |
| Reshape | groupBy().pivot |
| Scale out | distributed across the cluster |

---

## PySpark in practice

<span class="pill">practical</span>

<p class="muted"><strong>Read Parquet and aggregate on a cluster</strong>, the same DataFrame idea at big-data scale.</p>

```python
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet("s3://lake/prices/")        # distributed read
(df.groupBy("ticker")
   .agg(F.mean("ret").alias("mean_ret"))
   .show())
```

<p class="muted"><span class="tag">top scenarios</span> terabyte-scale ETL &middot; joining huge datasets &middot; scheduled cluster pipelines feeding a warehouse.</p>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Level 4 &middot; Analytics on stock data</span>

## Now, the analysis

<p class="muted">Returns in hand, we describe the basket: how much each ticker moved, how steadily, and how together.</p>

---

## Describe the returns

<p class="muted">Two numbers frame any return series: the <strong>mean</strong> (typical move) and the <strong>volatility</strong> (how much it swings, the standard deviation).</p>

<div class="columns">
<div class="card"><h3>The idea</h3><p>Higher volatility means a bumpier ride for the same average return. Comparing mean against volatility is the first honest look at a basket.</p></div>
<div class="card neon"><h3>In the notebook</h3>

```python
summary = pd.DataFrame({
    "mean":  returns.mean(),
    "vol":   returns.std(),
}).sort_values("vol")
```
</div>
</div>

<div class="proof"><b>Read it as a claim</b> "INITECH earned the most per day but swung the most; GLOBEX was the steadiest." That sentence is the analysis; the table backs it.</div>

---

## notebook &middot; trend and volatility over time

<span class="pill">notebook</span>

<p class="muted"><strong>The move:</strong> a <strong>moving average</strong> to see the trend through the noise, and <strong>rolling volatility</strong> to see when the ride got rough.</p>

```python
prices["ACME_sma50"]  = prices["ACME"].rolling(50).mean()      # trend
roll_vol = returns["ACME"].rolling(21).std()                   # ~1-month volatility
cumulative = (1 + returns).cumprod() - 1                       # growth of 1 unit
```

<div class="proof"><b>What each tells you</b> The 50-day average smooths the line to show direction; the 21-day rolling volatility spikes in turbulent stretches; cumulative return shows what holding through the period would have done.</div>

---

## Compare the basket: correlation and rebasing

<p class="muted">Two comparisons answer "do these move together?" and "which actually led?".</p>

<div class="columns">
<div class="card"><h3>Correlation</h3><p>How the tickers' returns move together, from -1 to 1. Low correlation is the whole idea behind not putting everything in one place.</p>

```python
returns.corr()
```
</div>
<div class="card neon"><h3>Rebasing</h3><p>Set every series to 100 at the start so the <strong>shapes</strong> are comparable regardless of price.</p>

```python
(prices / prices.iloc[0] * 100)
```
</div>
</div>

<div class="proof"><b>Fair comparison</b> You cannot compare a 210-rupee ticker and a 50-rupee ticker by price. Rebased to 100, the lines show who actually grew more.</div>

---

## Descriptive indicators (not signals)

<p class="muted">A few classic constructs describe a series more richly. We use them to <strong>describe</strong>, never to advise a trade.</p>

<div class="columns3">
<div class="card"><h3>MA crossover</h3><p>A short average crossing a long one, a common way to mark a shift in trend.</p></div>
<div class="card neon"><h3>Bands</h3><p>An envelope around a moving average showing how far price has strayed from its recent normal.</p></div>
<div class="card amber"><h3>Drawdown</h3><p>The drop from a running peak: the worst dip an series took, a plain risk read.</p></div>
</div>

<div class="proof"><b>Framing</b> These are descriptions of what a series did, taught as analytics. This topic makes no prediction and gives no investment advice.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Level 5 &middot; Presentation</span>

## Make the finding land

<p class="muted">An analysis nobody understands changed nothing. The last step is a chart and a sentence a decision-maker acts on.</p>

---

## The right chart for the question

<p class="muted">Each question has a chart that answers it at a glance. Match them and the reader needs no explanation.</p>

| The question | The chart |
| --- | --- |
| How did it move over time? | Line |
| How do a few compare? | Bar |
| How are returns distributed? | Histogram |
| Do they move together? | Heatmap (correlation) |
| What did a day trade like? | Candlestick (OHLC) |

<div class="proof"><b>Wrong chart, lost reader</b> A correlation shown as a table of numbers is work to read; the same thing as a heatmap is understood in a second.</div>

---

## Presentation-design principles

<p class="muted">The difference between a chart that informs and one that confuses is a few habits.</p>

<div class="columns">
<div class="card"><h3>Make it readable</h3><ul><li>Title says the finding, not the field name</li><li>Label the axes and their units</li><li>Colour with meaning, not decoration</li></ul></div>
<div class="card amber"><h3>Remove the noise</h3><ul><li>One message per chart</li><li>Drop gridlines, 3D, and clutter</li><li>Start an axis at zero unless there is a reason</li></ul></div>
</div>

<div class="proof"><b>Story, not dump</b> Lead the reader: here is the question, here is the chart that answers it, here is the one sentence it proves.</div>

---

## notebook &middot; a presentation chart

<span class="pill">notebook</span>

<p class="muted"><strong>The move:</strong> the correlation heatmap, titled with the finding, ready to drop into the report.</p>

```python
import seaborn as sns
import matplotlib.pyplot as plt

ax = sns.heatmap(returns.corr(), annot=True, cmap="vlag", vmin=-1, vmax=1)
ax.set_title("How the basket moves together (daily-return correlation)")
plt.tight_layout()
```

<div class="proof"><b>From analysis to artefact</b> A clear title, a diverging colour scale centred at zero, and the values on the cells. This chart needs no caption to be understood.</div>

---

## The notebook is the report

<p class="muted">A finished notebook is already a document: narrative, code, and charts in order. Share it as one.</p>

<div class="flow">
  <span class="step">restart and run all</span><span class="arrow">&rarr;</span>
  <span class="step">clean the narrative</span><span class="arrow">&rarr;</span>
  <span class="step hot">export</span>
</div>

<div class="columns">
<div class="card"><h3>Export it</h3><p><code>nbconvert</code> turns the notebook into HTML, PDF, or slides, so a reader needs no Python to read the finding.</p></div>
<div class="card neon"><h3>Or lift the charts</h3><p>Pull the key charts into the GuildTrek deck for a presentation to an audience, the concepts on the slide, the evidence from the notebook.</p></div>
</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Live Lab &middot; the build</span>

## One notebook, end to end

<p class="muted">The whole topic is one running notebook on the basket: load, manage, analyse, present. It runs top to bottom from a clean kernel.</p>

<div class="ladder">
<div class="rung"><div class="stage">Load and clean<small>Levels 1-2</small></div><div class="what">Read prices from CSV, index by date, handle gaps, derive returns.</div></div>
<div class="rung"><div class="stage">Store-aware<small>Level 3</small></div><div class="what">Save returns to Parquet and scan them with DuckDB, the analyst's fast path.</div></div>
<div class="rung"><div class="stage">Analyse<small>Level 4</small></div><div class="what">Summary stats, moving averages, rolling volatility, correlation, and rebased performance.</div></div>
<div class="rung"><div class="stage">Present<small>Level 5</small></div><div class="what">A titled heatmap and a rebased-performance line, a narrative, exported to a report.</div></div>
</div>

<div class="proof"><b>Proof</b> Restart and run all produces the charts and the written finding, and the notebook reads as a report a non-analyst could follow.</div>

---

## Assignments

<p class="muted">Two notebooks, each ending in a presented finding.</p>

<div class="columns">
<div class="card neon"><h3>1 &middot; single-ticker deep dive</h3><p>Fully analyse one ticker: returns, moving averages, rolling volatility, and drawdown, presented with three clear charts and a written summary.</p><p class="muted">Proof: runs clean end to end and reads as a report.</p></div>
<div class="card amber"><h3>2 &middot; multi-ticker comparison</h3><p>Compare the basket: rebased performance, a correlation heatmap, and a ranked table of return against volatility, presented for a decision-maker.</p><p class="muted">Proof: the comparison is fair (rebased) and the charts self-explain.</p></div>
</div>

---

## What we covered

<div class="columns">
<div class="card"><h3>Manage and choose</h3><ul><li>The workflow, and Jupyter done reproducibly</li><li>NumPy and pandas: load, clean, reshape, time-series</li><li>The database families and the pick, with the trade-offs</li><li>Parquet and DuckDB for fast notebook analytics</li></ul></div>
<div class="card neon"><h3>Analyse and present</h3><ul><li>Returns, moving averages, volatility, correlation</li><li>Rebasing for a fair comparison</li><li>The right chart, and presentation design</li><li>The notebook as a shareable report</li></ul></div>
</div>

<div class="proof"><b>The analyst's lens</b> What is the question? Is the notebook reproducible? Right store for the read? Returns, not prices? Fair comparison? Does the chart make the finding obvious?</div>

---

<!-- _class: lead -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Data Analytics with Python &middot; Complete</span>

# <span class="grad">Data becomes a finding you can run.</span>

<p class="muted" style="font-size: 22px; max-width: 50ch; margin-top: 12px;">Ask the question, manage the data, pick the right store, analyse it, and present it, all in one reproducible notebook. The slide taught the concept; the notebook proved it on real data.</p>

### <span class="brandlite">Next: the AI and ML libraries, where analytics turns into prediction.</span>
