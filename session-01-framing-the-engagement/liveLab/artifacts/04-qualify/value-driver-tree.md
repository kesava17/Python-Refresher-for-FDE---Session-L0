**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 4 (Qualify)**
**Worksheet 3 of 4 — Value-driver tree**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-19 |

---

## Prompt (from the worksheet)

> Draw the value-driver tree that connects the deflection bot to the board number, one checkable link at a time. Every arrow must map to a metric that a real function already owns. No unmeasurable links.

Worked from the business case and the discovery brief: **[x] yes**

## My work

### Value-driver tree: from bot to board number

**Engagement:** Sunrise Electronics, support deflection
**Method:** connect the solution to the financial outcome, one checkable link at a time. Each arrow must map to a metric someone owns.

#### The chain

```
Deflection bot
    -> tickets deflected            (metric: deflection rate, owned by the bot)
        -> agent hours freed        (metric: tickets x avg handle time, owned by workforce planning)
            -> cost to serve down   (metric: hours x cost per contact, owned by finance)
                -> support margin up (metric: cost to serve vs service level, owned by finance)
```

#### Each link, and who can check it

| Link | Metric | Owner |
| --- | --- | --- |
| Deflection bot to tickets deflected | deflection / containment rate | the bot (reported directly) |
| Tickets deflected to agent hours freed | tickets x average handle time | workforce planning |
| Agent hours freed to cost to serve down | freed hours x Rs 120 cost per contact | finance |
| Cost to serve down to support margin up | cost to serve vs service level | finance |

#### Reading

The **deflection rate is the driving lever**: every additional point of deflection propagates down the chain into freed hours, lower cost to serve, and higher margin. Because every arrow maps to a metric a real function already owns, the value is auditable end to end. When a CFO asks how grounded answers become margin, you walk the tree; each link is a number someone can pull, not a claim.

**Pitfall avoided:** there is no unmeasurable link here (no "happier customers lead to more revenue" hand-wave). Every step has an owner and a number.

_Note to self: the deflection rate is the one lever I own directly, so that is the number I will report on first._

## Self-check

- [x] Every arrow maps to a named metric
- [x] Every metric has a real function as its owner
- [x] No unmeasurable link is left in the chain

## Handoff

The audit-ready value chain feeds the qualification memo.

Filled by: A. Menon
