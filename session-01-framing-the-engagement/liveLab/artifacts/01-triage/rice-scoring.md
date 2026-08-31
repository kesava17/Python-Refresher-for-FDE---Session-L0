**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 1 (Triage)**
**Worksheet 2 of 4 — RICE scoring**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-10 |

---

## Prompt (from the worksheet)

> Take the buildable candidates from the six asks and score each one with RICE on a 1 to 5 scale, using
> `liveLab/data/asks.csv`, the Pareto result, and your judgment from discovery so far. Score =
> (Reach x Impact x Confidence) / Effort. Rank them and say which one to build.

Reviewed input: **[x] liveLab/data/asks.csv**

## My analysis

Only three of the six asks are buildable problems. A4 (lift CSAT) is an outcome, A5 (use our data) is
an assumption, and A6 (quarter-end budget) is a constraint. Those are handled elsewhere, not scored
here.

### Scores

| Candidate (ask) | Reach | Impact | Confidence | Effort | Score | Rank |
| --- | --- | --- | --- | --- | --- | --- |
| **A1 Support deflection** | 5 | 4 | 4 | 2 | (5 x 4 x 4) / 2 = **40.0** | 1 |
| A2 Upsell bot | 4 | 3 | 2 | 4 | (4 x 3 x 2) / 4 = **6.0** | 2 |
| A3 Marketing content generation | 3 | 2 | 2 | 3 | (3 x 2 x 2) / 3 = **4.0** | 3 |

### Scoring notes (why each number)

- **A1 Support deflection.** Reach 5: it touches the 60 percent of tickets the Pareto flagged. Impact
  4: it frees agents from repetitive load. Confidence 4: the answers already exist in Sunrise content,
  so it is not a bet on unproven capability. Effort 2: a standard grounded-answer build.
- **A2 Upsell bot.** Confidence 2: no clear success measure, and selling inside a support answer can
  erode trust. Effort 4: new surface, new integration, new risk.
- **A3 Marketing content.** Impact 2 on the support pain (it is a different problem), and unresolved
  brand-risk questions keep confidence low.

### Reading

Support deflection scores **40**, an order of magnitude above the alternatives. This is not a close
call to argue about; it is a decisive separation on evidence a VP can read. Treat the gap between 40
and single digits as a real signal (a 40 versus 38 would be a tie, but this is not that).

**Caution on false precision:** the inputs are 1-to-5 judgments, not measurements. The number is a
comparison aid, not a fact. It is trustworthy only because every candidate was scored the same way,
in the open.

### Conclusion

RICE confirms the Pareto: **A1, support deflection, is the one to build.** Carry it into the scope
decision (MoSCoW).

_Note to self: kept Effort as the denominator so the low-effort build floats up; almost inverted it on the first pass._

## Self-check

- [x] Only buildable asks were scored; outcome, assumption, and constraint were set aside
- [x] Every candidate scored on the same 1-to-5 rubric, in the open
- [x] Winner and its margin are clear enough for a VP to read

## Handoff

The chosen candidate (A1, support deflection) feeds Worksheet 3 (MoSCoW).

Filled by: A. Menon
