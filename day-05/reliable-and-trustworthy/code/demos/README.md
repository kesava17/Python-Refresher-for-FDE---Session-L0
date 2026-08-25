# Dependable demos: run the ideas, do not just read them

Each script is a tiny, self-contained demonstration of one idea from the Dependable topic (building
software that is reliable and trustworthy: SLOs and error budgets, graceful degradation, safe
retries, load shedding, bounded memory, crash recovery, structured logs, and gated rollouts). This
folder is its own small Poetry project, so you run the demos the same way as everything else in this
course. Set it up once, then run any demo:

```bash
poetry install                           # once, from this demos/ folder
poetry run python demo_slo_burn.py
```

Two of the demos are pytest files, so run those with pytest instead of a bare `python`:

```bash
poetry run pytest demo_degrade_on_timeout.py -v
poetry run pytest demo_crash_in_the_middle.py -v
```

The demos use only the standard library, plus `httpx` (the degrade demo) and `pytest` (the two test
files); both are declared here, so run everything through Poetry.

| Demo | What it shows | Expected |
| --- | --- | --- |
| `demo_slo_burn.py` | error budget burn against a 99 percent SLO | 40 failures spend four times a budget of 10, so it ends "budget burned too fast: ALERT" |
| `demo_degrade_on_timeout.py` | degrade to a plain review when the insight call times out | pytest: 1 passed, the result has enriched False and keeps product_id P-77 |
| `demo_latency_percentiles.py` | percentiles expose the slow tail the mean hides | p50 stays at 41 ms while p99 jumps to 930 ms (mean 76 ms sits between) |
| `demo_retry_idempotency.py` | an idempotency key makes a retry safe | "no key -> applied 2 times" and "with key -> applied exactly once" |
| `demo_load_shedding.py` | a concurrency cap sheds excess with a fast 429 | 10 offered, 4 accepted within the 50 ms target, 6 shed |
| `demo_soak_flat.py` | a bounded cache stays flat while an unbounded dict climbs | unbounded entry count climbs to 20000, the lru_cache holds 128 |
| `demo_restart_resumes.py` | a checkpoint resumes a crashed batch with no loss | crash after R-04, restart finishes R-10; no lost True, no duplicated True |
| `demo_crash_in_the_middle.py` | a two-step write is all-or-nothing | pytest: 1 passed, the store holds 0 or 1 complete records, never a partial |
| `demo_structured_logging.py` | one JSON log line per event, keyed by trace id | four JSON lines, trace ids 9f2a and 3b7c, filterable by id |
| `demo_rollback_gate.py` | a readiness gate auto rolls back a bad rollout | "rollout v2 -> readiness FAIL -> auto rollback to v1", v1 stays live |

The exact numbers do not matter; the pattern is the point. The lesson points you to each of these
with a "Try it" note at the matching topic.
