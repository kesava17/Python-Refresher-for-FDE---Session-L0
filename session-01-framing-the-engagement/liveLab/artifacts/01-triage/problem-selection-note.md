**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 1 (Triage)**
**Worksheet 4 of 4 — Problem-selection note (Triage deliverable)**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-10 |

---

## Prompt (from the worksheet)

> Consolidate the Triage move into one problem-selection note a VP can read. Pull the three prior
> worksheets together (Pareto, RICE, MoSCoW), state the one problem you will build, show where every
> other ask went, and record the feasibility gate. Status: agreed with Vikram Rao (VP CX).

Reviewed inputs: **[x] pareto-analysis.md**  **[x] rice-scoring.md**  **[x] moscow-scope.md**

## My work

**Engagement:** Sunrise Electronics, "AI for customer experience"
**Author:** Forward Deployed Engineer
**Date:** 2026-08-10
**Status:** agreed with Vikram Rao (VP CX)

### The decision

Of the six asks in the brief, we will build **one**: **support deflection**, answering the
high-frequency order, return, and simple-warranty questions from Sunrise's own help content, with
escalation to a human for everything else.

### How we chose (evidence, not opinion)

- **Pareto** (`pareto-analysis.md`): three question types are 60.7 percent of 4,000 weekly tickets.
- **RICE** (`rice-scoring.md`): support deflection scores 40, against 6 (upsell) and 4 (content).
- **MoSCoW** (`moscow-scope.md`): those three types are the Must; upsell and content are Won't-this-quarter.

### Where every other ask went

| Ask | Disposition | Reason |
| --- | --- | --- |
| A2 Upsell bot | Deferred (Won't this quarter) | Erodes answer trust; no success measure yet |
| A3 Marketing content | Deferred (Won't this quarter) | Different problem, different owner, brand risk |
| A4 Lift CSAT | Reframed as a metric | An outcome; we measure it on deflected chats |
| A5 Use our data | Sent to discovery | An assumption to verify, not a fact |
| A6 Quarter-end budget | Kept as a constraint | Shapes scope, favours a narrow build |

### Feasibility gate (passed)

- **Is it an AI problem?** Yes: answering natural-language questions from documents.
- **Is the data there?** Largely: help center and resolved tickets exist; to be verified in discovery.
- **What is the risk?** Bounded: wrong low-harm answers caught by escalation; disputes kept out of scope.

### Next

Frame the chosen problem into a tool-free problem statement and real options.

_Note to self: Vikram signed off fast once he saw A5 hadn't been dropped, just routed to discovery._

## Self-check

- [x] One problem named, not a shortlist
- [x] Every other ask has a visible disposition and reason
- [x] Feasibility gate recorded and passed before committing

## Handoff

The one chosen problem (support deflection) is the input to Move 2 (Frame).

Filled by: A. Menon
