# Dependable demos: a run cookbook

Ten tiny, self-contained demos, one idea each, for the Dependable topic (building software that is
reliable and trustworthy). They fall into the same flow as the lesson:

- **Define the target:** name the reliability goal and watch the error budget burn.
- **Hit each metric:** the engineering patterns behind availability, success rate, throughput,
  MTBF, MTTR, durability, and latency.
- **Operate what you shipped:** logs you can query, and a rollout that rolls itself back.

Run them in the order below to follow that flow. The exact numbers (a traced memory figure, and the
latency spread in a real system) will differ on your machine; the pattern each demo shows is the
point.

## Setup (once)

This folder is its own small Poetry project. Set it up once, then run any demo through Poetry:

```bash
poetry install
```

Eight demos are plain scripts you run with `poetry run python <name>.py`. Two are pytest files
(`demo_degrade_on_timeout.py` and `demo_crash_in_the_middle.py`); run those with `poetry run pytest
<name>.py -v`. The demos use only the standard library plus `httpx` (the degrade demo) and `pytest`
(the two test files), so run everything through Poetry, not a bare `python`.

## Run everything at once

```bash
for f in demo_slo_burn demo_retry_idempotency demo_load_shedding demo_soak_flat \
         demo_restart_resumes demo_latency_percentiles demo_structured_logging demo_rollback_gate; do
  echo "==== $f ===="; poetry run python "$f.py"; echo
done
poetry run pytest demo_degrade_on_timeout.py demo_crash_in_the_middle.py -v
```

On Windows PowerShell:

```powershell
'demo_slo_burn','demo_retry_idempotency','demo_load_shedding','demo_soak_flat','demo_restart_resumes','demo_latency_percentiles','demo_structured_logging','demo_rollback_gate' | ForEach-Object { Write-Host "==== $_ ===="; poetry run python "$_.py" }
poetry run pytest demo_degrade_on_timeout.py demo_crash_in_the_middle.py -v
```

---

## Define the target

### 1. `demo_slo_burn.py`

**Demonstrates:** an SLO and its error budget. A 99 percent objective over 1000 requests allows 10
failures; spend them faster than the window elapses and you alert before the window closes.

```bash
poetry run python demo_slo_burn.py
```

**Expect:** 40 failures against a budget of 10, so the budget is 400 percent spent by the end. The
run reports "too fast" at every checkpoint and ends with an ALERT.

```text
objective=99%  total=1000  budget=10
  at  250 requests: 10 failures, budget spent  100%, window elapsed  25% (too fast)
  at  500 requests: 20 failures, budget spent  200%, window elapsed  50% (too fast)
  at  750 requests: 30 failures, budget spent  300%, window elapsed  75% (too fast)
  at 1000 requests: 40 failures, budget spent  400%, window elapsed 100% (too fast)
final: 40 failures against a budget of 10
budget burned too fast: ALERT
```

---

## Hit each metric

### 2. `demo_degrade_on_timeout.py`

**Demonstrates:** graceful degradation for availability. When an optional insight call times out, the
page returns the plain review instead of failing, so one shaky dependency cannot take the whole page
down.

```bash
poetry run pytest demo_degrade_on_timeout.py -v
```

**Expect:** the test injects a client that always times out; the result keeps `product_id` P-77 and
comes back with `enriched` False. One test passes.

```text
demo_degrade_on_timeout.py::test_degrades_when_insight_times_out PASSED  [100%]

============================== 1 passed in 0.05s ==============================
```

### 3. `demo_retry_idempotency.py`

**Demonstrates:** an idempotency key protecting success rate. A safe retry must not apply the same
write twice; keyed by a request id, the second attempt is recognised and skipped.

```bash
poetry run python demo_retry_idempotency.py
```

**Expect:** without a key the write applies twice on retry; with a key it applies exactly once.

```text
no key   -> applied 2 times
with key -> applied exactly once (1 time)
```

### 4. `demo_load_shedding.py`

**Demonstrates:** load shedding to protect throughput. A concurrency cap admits work up to the limit
and rejects the rest immediately with a fast 429, so the accepted work stays inside its latency
target instead of everyone slowing together.

```bash
poetry run python demo_load_shedding.py
```

**Expect:** 10 requests offered against a cap of 4, so 4 are accepted (within the 50 ms target) and 6
are shed with a 429.

```text
offered  : 10 requests, concurrency limit 4
accepted : 4  -> [1, 2, 3, 4]
shed     : 6  -> ['5', '6', '7', '8', '9', '10'] (429, shed)
accepted work worst latency 40 ms vs 50 ms target: within target
```

### 5. `demo_soak_flat.py`

**Demonstrates:** bounded memory for a longer MTBF. An unbounded dict keyed by a fresh value every
iteration grows without limit (the classic slow leak), while an `lru_cache` holds a fixed number of
entries and stays flat under the same soak.

```bash
poetry run python demo_soak_flat.py
```

**Expect:** over 20000 iterations the unbounded entry count climbs to 20000 while the bounded cache
holds 128. The traced total (in KiB) is a live tracemalloc reading and varies by machine.

```text
soak of 20000 iterations, unique key each time
 iteration  unbounded entries  bounded entries
      5000               5000              128
     10000              10000              128
     15000              15000              128
     20000              20000              128

traced total now: 2280.1 KiB
unbounded dict holds 20000 entries and keeps climbing; bounded cache holds 128 and stays flat.
```

### 6. `demo_restart_resumes.py`

**Demonstrates:** a checkpoint for a short MTTR. A batch that crashes partway records its progress,
so the restart resumes from the last checkpoint rather than starting over or losing rows.

```bash
poetry run python demo_restart_resumes.py
```

**Expect:** the first run crashes before record R-05 and checkpoints at 4; the restart finishes
through R-10. The final store holds all 10, with no lost and no duplicated records.

```text
first run:
  crash before record index 4 (R-05)
  checkpoint after crash: 4 (done through R-04)
restart:
  checkpoint after finish: 10

final store holds 10 records: ['R-01', 'R-02', 'R-03', 'R-04', 'R-05', 'R-06', 'R-07', 'R-08', 'R-09', 'R-10']
no lost records: True; no duplicated records: True
```

### 7. `demo_crash_in_the_middle.py`

**Demonstrates:** durability through an all-or-nothing write. A two-step write that is interrupted
must leave the store whole: either the complete record landed or nothing did, never a half-written
row.

```bash
poetry run pytest demo_crash_in_the_middle.py -v
```

**Expect:** the store ends holding 0 or 1 complete records, never a partial one. One test passes.

```text
demo_crash_in_the_middle.py::test_interruption_leaves_store_whole PASSED [100%]

============================== 1 passed in 0.01s ==============================
```

### 8. `demo_latency_percentiles.py`

**Demonstrates:** measuring latency with percentiles, because the mean hides the slow tail. p50 sits
with the fast group while p99 lands out in the tail, and the mean is dragged between them.

```bash
poetry run python demo_latency_percentiles.py
```

**Expect:** over a fixed set of 100 samples (96 fast, 4 slow), p50 stays at 41 ms while p99 jumps to
930 ms and the mean (76.2 ms) sits between. This demo uses a fixed sample set so the numbers
reproduce; in a real service the same spread shifts run to run.

```text
samples : 100 requests (96 fast, 4 slow)
mean    :   76.2 ms
p50     :     41 ms
p95     :     44 ms
p99     :    930 ms

p50 (41 ms) stays with the fast group while p99 (930 ms) exposes the slow tail; the mean (76 ms) sits between and hides it.
```

---

## Operate what you shipped

### 9. `demo_structured_logging.py`

**Demonstrates:** structured logs you can query. One JSON line per event, each carrying a trace id,
so you can filter every line for a single request instead of grepping free text.

```bash
poetry run python demo_structured_logging.py
```

**Expect:** four JSON lines for two requests, trace ids 9f2a and 3b7c, filterable by id.

```text
{"level": "info", "trace_id": "9f2a", "event": "request_received", "product_id": "P-77"}
{"level": "info", "trace_id": "9f2a", "event": "request_completed", "product_id": "P-77", "duration_ms": 12}
{"level": "info", "trace_id": "3b7c", "event": "request_received", "product_id": "P-88"}
{"level": "info", "trace_id": "3b7c", "event": "request_completed", "product_id": "P-88", "duration_ms": 34}

Filter these lines by trace_id "9f2a" to see just that request path.
```

### 10. `demo_rollback_gate.py`

**Demonstrates:** a readiness gate that auto rolls back a bad rollout. A new version has to pass a
readiness check before it stays live; when it fails, the deploy rolls back to the previous version on
its own.

```bash
poetry run python demo_rollback_gate.py
```

**Expect:** v2 fails readiness and is rolled back, so v1 is still the live version. The bad build
never stayed live.

```text
currently live: v1
rollout v2
  readiness FAIL -> auto rollback to v1

sequence: rollout v2 -> readiness FAIL -> auto rollback to v1
live version is still v1: the bad build never stayed live.
```

---

Each demo also has a matching "Try it" pointer in the lesson at the topic it illustrates, and the
same ideas are then built for real in the liveLab (`reviews-insight`).
</content>
</invoke>
