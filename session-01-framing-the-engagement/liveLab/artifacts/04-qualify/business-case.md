**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 4 (Qualify)**
**Worksheet 2 of 4 — Business case**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-19 |

---

## Prompt (from the worksheet)

> Turn the deflection idea into a board-ready business case. Feed the cost inputs from `liveLab/data/cost_assumptions.csv` into `liveLab/analysis/business_case.py`, then write up the run-rate saving, the first-year TCO, and the payback in money-and-time language. Keep every estimate conservative and clearly labelled.

Ran the script: **[x] yes**   (`python liveLab/analysis/business_case.py`, inputs from `data/cost_assumptions.csv`)

## My work

### Business case: support deflection

**Engagement:** Sunrise Electronics
**Input:** `data/cost_assumptions.csv`
**Reproduce:** `python analysis/business_case.py`
**Principle:** conservative, clearly labelled estimates, in the money-and-time language a board funds in.

#### The numbers

| Line | Estimate | Derivation |
| --- | --- | --- |
| Tickets per week | 4,000 | support ops |
| Repetitive, in-scope | 2,400 / week | 60% of 4,000 (Pareto) |
| Conservatively deflected | 1,200 / week | 50% of in-scope, deliberately cautious |
| Cost per contact | Rs 120 | fully loaded cost to serve |
| **Run-rate saving** | **Rs 74.9 lakh / year** | 1,200 x 52 x Rs 120 = Rs 74,88,000 |
| Monthly saving | Rs 6.24 lakh | Rs 74.88 lakh / 12 |
| Build (one-time) | Rs 17 lakh | PoC build |
| First-year run | Rs 7 lakh | model, infra, monitoring, content upkeep, escalation |
| **TCO (first year)** | **Rs 24 lakh** | build + run |
| **Payback period** | **under four months** | Rs 24 lakh / Rs 6.24 lakh per month = 3.8 months |

#### Reading

The run-rate saving (near Rs 75 lakh a year) is set against a first-year total cost of ownership of about Rs 24 lakh, which repays the whole investment in **under four months**. The case is deliberately conservative: it counts only half the repetitive tickets, and the repetitive tickets are only 60 percent of the total, so reality is likely to beat the case rather than miss it.

#### Two honesty checks

- **Run cost is counted.** TCO includes the first year of running it, not just the build. A case that hides the run cost lies about the payback.
- **Deflection is understated on purpose.** A 50 percent deflection rate is defensible on the low side.

This replaces "support is expensive" with a number Vikram can put in front of a board without flinching.

_Note to self: the script matched my hand figure of Rs 74,88,000 exactly, so I trust the payback of 3.8 months._

## Self-check

- [x] Every line traces to an input or a stated derivation
- [x] Run cost is inside TCO, not hidden outside the payback
- [x] The deflection rate is conservative and labelled as such

## Handoff

The payback feeds the qualification memo.

Filled by: A. Menon
