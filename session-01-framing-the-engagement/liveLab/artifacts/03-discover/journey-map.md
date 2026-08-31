**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 3 (Discover)**
**Worksheet 3 of 4 — Customer-journey map**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-16 |

---

## Prompt (from the worksheet)

> Take a common "where is my order" question sampled from the ticket data and trace the real steps a customer takes. For each stage record the action, the goal, and the pain. Mark the stage where the journey breaks. Sample from `liveLab/data/support_tickets.csv`.

Reviewed input: **[x] liveLab/data/support_tickets.csv**

## My work

**Method:** trace the real steps a customer takes, with action, goal, and pain at each stage. The sharpest pain is the opportunity.

| Stage | What the customer does | Goal | Pain today |
| --- | --- | --- | --- |
| **Question arises** | Checks email, then the Sunrise website | Find out where the order is, fast, alone | No obvious instant self-serve answer |
| **Looks for help** | Scans help pages, then gives up | Get the answer without talking to anyone | Content is written as articles, not answers. **This is the break.** |
| **Contacts support** | Opens a ticket or waits on chat | Reach a human who can tell them | Queue backed up behind the same common questions |
| **Waits** | Checks back later for a reply | Get resolution and move on | Slow, and the answer was simple |

### Reading

The answer to "where is my order" genuinely exists in Sunrise's content, but it is **unreachable** at the "looks for help" stage because the content is not written as a direct answer to the question. That is exactly where deflection sits: intercept the customer there, before they ever join the support queue. Everything downstream (the queue, the wait) is a consequence of the one break.

The map confirms the frame from the customer's side and puts the solution on the precise point of failure. It also marks the stage where a wrong answer would do harm, which is why escalation is mandatory, not optional.

_Note to self: my first instinct was to fix the queue. The queue is a symptom; the break is one stage earlier._

## Self-check

- [x] Every stage has an action, a goal, and a pain
- [x] Marked the single stage where the journey breaks (looks for help)
- [x] Tied the downstream pain back to the one break, not treated as separate problems

## Handoff

The break location feeds the discovery brief.

Filled by: A. Menon
