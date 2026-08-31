**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 1 (Triage)**
**Worksheet 1 of 4 — Pareto analysis**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-10 |

---

## Prompt (from the worksheet)

> Count the support tickets by question type, sort them highest first, and read the cumulative share.
> Which types are the vital few? What does that tell you to build, and what to leave alone?
> Data: `liveLab/data/support_tickets.csv` (one week, 4,000 tickets).
> Reproduce with: `python liveLab/analysis/pareto.py`.

Ran the script:  **[x] yes**   [ ] no

## My analysis

Pasted from the script output, then marked up:

| Rank | Question type | Count | Share | Cumulative | Vital few? |
| --- | --- | --- | --- | --- | --- |
| 1 | order_status | 1,214 | 30.4% | 30.4% | yes |
| 2 | return | 735 | 18.4% | 48.7% | yes |
| 3 | warranty_simple | 479 | 12.0% | 60.7% | yes |
| 4 | delivery_delay | 226 | 5.7% | 66.3% | |
| 5 | product_info | 212 | 5.3% | 71.7% | |
| 6 | account_login | 150 | 3.8% | 75.4% | |
| 7 | payment_issue | 133 | 3.3% | 78.7% | |
| 8 | warranty_dispute | 125 | 3.1% | 81.8% | |
| 9+ | long tail (11 more types) | 726 | 18.2% | 100.0% | |

_Note to self: order_status alone is nearly a third of everything. That is where I start._

## What I read from it

- **Where the volume is:** the top three types, about 60.7% of all tickets (~2,428 of 4,000). Answer
  those three well and I move most of the load with one focused build.
- **What to leave alone:** the long tail. Many rare types, high effort for little aggregate return,
  and rare varied cases are where an automated answer is most likely to be wrong. Safest with humans.
- **Cost check (not just volume):** warranty_dispute is only 3.1% by count but has a high handle time
  and escalation rate (see `liveLab/data/support_tickets.csv`). Keep it out of scope on risk, not volume.

## Self-check

- [x] Sorted highest-first; cumulative reaches 100%
- [x] Named the vital few (three types, 60.7%)
- [x] Said what NOT to build (the long tail)
- [x] Checked the tail for hidden cost before dropping it

## Handoff

Output of this worksheet: the vital few (**order_status, return, warranty_simple**). Feeds Worksheet 2
(RICE scoring).

Filled by: A. Menon
