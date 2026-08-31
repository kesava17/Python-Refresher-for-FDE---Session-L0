**AI for FDE · Live Lab worksheet**
**Session 1: Framing the Engagement · Move 3 (Discover)**
**Worksheet 4 of 4 — Discovery brief (Discover deliverable)**

| Field | Entry |
| --- | --- |
| Engagement | Sunrise Electronics |
| Trainee | Arjun Menon |
| Cohort | L1-2026 |
| Date | 2026-08-16 |

---

## Prompt (from the worksheet)

> Consolidate the three prior worksheets into one discovery brief: state the real need, the state of the data, the stakeholders and vetoes, the constraints, and the narrowed scope. Cross-check the data claim against the help-content inventory at `liveLab/data/help_content_inventory.csv`. This is the Discover deliverable.

Reviewed input: **[x] Worksheet 1 (Power-Interest grid) · [x] Worksheet 2 (RACI) · [x] Worksheet 3 (Journey map) · [x] liveLab/data/help_content_inventory.csv**

## My work

**Author:** Forward Deployed Engineer (Arjun Menon)
**Status:** verified against data and stakeholder interviews

### Real need

Customers cannot get an instant, correct answer to common questions from content that Sunrise already owns. (Not "an AI assistant that does everything," which was the ask.)

### Data and its state

| Source | Covers | State |
| --- | --- | --- |
| Help center (`help_content_inventory.csv`) | order status, returns, simple warranty | order and returns good; warranty partial |
| Internal KB | refunds, payments, disputes | partial, uneven |
| 12 months of resolved tickets | many types | usable as grounding and evaluation signal |
| Tribal knowledge (agents' heads) | simple-vs-dispute rules, courier quirks | **gap**: undocumented |

There is no clean data warehouse. "We have years of data" (IT's claim) is true but scattered.

### Stakeholders and vetoes

Vikram (sponsor, single accountable owner); Legal (warranty veto); IT (data and systems access); support agents (adoption). See `power-interest-grid.md` and `raci-matrix.md`.

### Constraints

- Customer data must stay in **Bharat** (residency).
- Legal permits warranty answers only for **simple** cases; **disputes** are excluded.
- Demo due at **quarter-end**; budget is tight.

### Narrowed scope

Order-status, return, and **simple**-warranty questions, answered from Sunrise's own content, with a clean escalation to a human for anything outside that boundary (including warranty disputes).

### What changed from Frame

The guesses became facts. Warranty split into simple (in) and disputes (out). The residency constraint, absent from the kickoff, is now on the page where it will shape the architecture. Scope shrank from "one AI thing that does everything" to a narrow, groundable, permitted target shippable by quarter-end.

_Note to self: the residency line felt small when I wrote it, but it is the one that will decide the hosting story. Keep it loud._

## Self-check

- [x] Real need stated as the customer's problem, not the customer's ask
- [x] Data claim checked against the help-content inventory, gaps named
- [x] Constraints and narrowed scope both on the page, with disputes explicitly out

## Handoff

The discovery brief is the input to Move 4 (Qualify): turn this grounded picture into a defensible go or no-go.

Filled by: A. Menon
