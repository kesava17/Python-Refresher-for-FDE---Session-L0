**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 3 (Discover)**
**Worksheet 1 of 4 — Power-Interest grid**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-16 |

---

## Prompt (from the worksheet)

> Plot each stakeholder from the intake list on Mendelow's matrix by power (ability to affect or stop the project) and interest (how much they care and are affected). Use the four quadrants to pick a handling strategy for each, then call out anyone the written brief let slip. Work from `liveLab/data/stakeholders.csv`.

Reviewed input: **[x] liveLab/data/stakeholders.csv**

## My work

**Method:** plot each stakeholder by power (ability to affect or stop the project) and interest (how much they care and are affected). Four quadrants, four strategies.

### Placement

| Stakeholder | Power | Interest | Quadrant | Strategy |
| --- | --- | --- | --- | --- |
| Vikram Rao (VP CX) | High | High | Manage closely | Sponsor and skeptic; regular direct contact, early sight of decisions |
| CEO | High | Low | Keep satisfied | Enthusiastic but not day-to-day; a short periodic update |
| Legal | High | Medium | Keep satisfied | Get warranty scope signed early; the veto becomes a boundary, not a surprise |
| IT | High | Medium | Keep satisfied | Agree data access and integration in writing, with dates |
| Support ops lead | Medium | High | Keep informed / involve | Owns queues and SLAs; a partner in rollout |
| Finance | Medium | Medium | Keep informed | Budget holder; wants the quarter-end proof |
| Support agents | Low | High | Keep informed / involve | Adoption depends on them; bring them in during discovery |
| Sales | Low | Medium | Monitor | Wants upsell; not on the critical path this quarter |
| Marketing | Low | Low | Monitor | Wants content; out of scope this quarter |

### Text-diagram

```
 high  |  Support ops lead        |  Vikram Rao
       |  Support agents          |
 INT   |--------------------------+--------------------------
       |  Marketing               |  Legal   IT   CEO
 low   |  Sales (mid)             |  Finance (mid)
       +--------------------------+--------------------------
          low            POWER            high
```

### Two facts the brief hid

1. **Legal is a high-power veto that is easy to miss.** Not loud, not in the kickoff, medium interest, and able to kill the entire warranty use case. Grade by power held, not by noise made.
2. **Support agents have no formal power yet decide adoption.** A technically sound build they will not use is a failed build. Involve them now.

_Note to self: nearly plotted Legal as low-power because they said so little in the kickoff. Power is not volume._

## Self-check

- [x] Every stakeholder from the CSV placed in exactly one quadrant with a strategy
- [x] Named the quiet high-power veto (Legal) instead of grading by how loud they were
- [x] Flagged the no-formal-power group that still decides adoption (support agents)

## Handoff

The stakeholders and vetoes feed Worksheet 2 (RACI) and the discovery brief.

Filled by: A. Menon
