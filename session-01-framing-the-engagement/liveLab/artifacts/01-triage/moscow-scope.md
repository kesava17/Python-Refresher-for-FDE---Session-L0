**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 1 (Triage)**
**Worksheet 3 of 4 — MoSCoW scope**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-10 |

---

## Prompt (from the worksheet)

> For the chosen problem (support deflection) scope a quarter-end PoC. Using the six asks
> (`liveLab/data/asks.csv`), the Pareto result, and the RICE ranking, sort every item into Must,
> Should, Could, or Won't-this-quarter, agreed with stakeholders, and say why each lands where it does.

Reviewed input: **[x] liveLab/data/asks.csv**

## My work

| Bucket | Scope items | Why here |
| --- | --- | --- |
| **Must have** | Deflect the three high-volume question types (order status, returns, simple warranty) with grounded, correct answers from Sunrise's own content | The core problem Pareto and RICE identified; without it there is no PoC |
| **Should have** | Clean escalation to a human for anything out of scope or low-confidence | A bot with no safe exit is not shippable; high on the list |
| **Could have** | Track CSAT on deflected chats; add more question types from the long tail later | Valuable, not required to prove the concept this quarter; first to cut if time runs short |
| **Won't have this quarter** | Upsell and cross-sell in the bot (A2); generated marketing content and campaigns (A3); warranty **disputes** | Sequenced with a reason, not silently dropped, so Sales, Marketing, and the CEO see where their items went |

### Notes

- **The "Won't" is the load-bearing bucket.** Naming upsell and content generation as Won't-this-quarter,
  out loud, is what stops them creeping back into scope in week three. It is a sequencing decision, not a
  rejection: "this time" is doing real work.
- **CSAT (A4)** moved from an ask to a **Could** measure on the deflected chats, not a project.
- **Warranty splits.** Simple warranty is a Must; warranty **disputes** are a Won't, on risk grounds
  (high harm, Legal-sensitive), confirmed later in discovery.

### Conclusion

A scope every stakeholder can read, with a defined Must core that a small team can ship by quarter-end.

_Note to self: I nearly put warranty in one bucket; splitting simple from disputes is the whole trick._

## Self-check

- [x] Every one of the six asks has a home in a bucket
- [x] Each Won't item carries a reason, so nobody's ask just vanishes
- [x] The Must core is small enough to ship by quarter-end

## Handoff

The agreed scope feeds Worksheet 4 (the problem-selection note).

Filled by: A. Menon
