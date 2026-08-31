# Assignment 1: Drive your own account (Capstone L1, Frame stage)

You watched the Sunrise engagement, and you filled the Sunrise worksheets with the answer key beside
you. Now you drive a fresh account on your own, with no answer key. This is the Frame stage of your
**Capstone L1**: take a vague brief, run the four moves, and produce the four artifacts that a board
could act on.

## What to do

1. **Pick your account.** Use the default below (**Pinnacle Bank**), or substitute your own vertical
   (healthcare, retail, manufacturing, logistics, insurance, the public sector, or your own client
   context), always set in Bharat. If you use your own, write a vague brief of the same messy shape
   first.
2. **Run the four moves** (Triage, Frame, Discover, Qualify), in order, using the blank worksheets in
   `liveLab/templates/`. Fill them as you go.
3. **Produce the four deliverables:** the problem-selection note, the problem statement with options,
   the discovery brief, and the qualification memo.
4. **Defend it.** Be ready to present the GO (or NO-GO) and answer "why this, not that."

## The default account: Pinnacle Bank

**Pinnacle Bank** is a fictional mid-size retail bank in Bharat: about 120 branches, a fast-growing
mobile app, and a contact centre under strain. Leadership wants to "use AI this year." Greenfield: no
AI in production.

The brief, from **Rohan Desai, Head of Digital Banking** (your sponsor):

> The board wants AI in customer service this year. Everything I am hearing:
>
> - The contact centre is swamped with routine queries (balance, transaction status, card block, how
>   do I do X). I want AI to take that off my agents.
> - The fraud team wants AI to catch fraud in real time.
> - Lending wants a bot that checks loan eligibility and cross-sells.
> - Marketing and the CEO want AI to write our campaigns and help content.
> - Compliance says whatever we do has to be fully auditable, and customer data must stay in Bharat.
> - Finance wants something to show the board by quarter-end, and the budget is tight.

One direction, many agendas, no owner, no value analysis. Untangle it.

### Ground data (for your analysis)

**Contact volume by query type** (one week, about 8,000 contacts). Run a Pareto by hand on this:

| Query type | Share |
| --- | --- |
| Transaction / payment status | 22% |
| Card services (block, replace, limit) | 20% |
| Balance and statement queries | 18% |
| Netbanking / app login help | 9% |
| Charges and fee disputes | 8% |
| Loan and EMI queries | 7% |
| KYC and account update | 6% |
| Branch, IFSC, ATM info | 4% |
| Fraud report (urgent) | 3% |
| Everything else (long tail) | 3% |

**Stakeholders** (for the Power-Interest grid and RACI):

| Stakeholder | Role | Notes |
| --- | --- | --- |
| Rohan Desai | Head of Digital Banking (sponsor) | holds budget, board-facing |
| Compliance | Regulatory and audit | can veto; residency and auditability |
| IT / Core banking | Systems and data | owns integration and access |
| Contact-centre agents | Front line | adoption decides success |
| Fraud team | Risk | wants the fraud project |
| Marketing | Brand | wants content generation |
| CEO | Executive | enthusiastic, low day-to-day interest |
| Finance | Budget | wants a quarter-end proof |

**Cost assumptions** (for the business case):

| Parameter | Value |
| --- | --- |
| Contacts per week | 8,000 |
| Routine, in-scope share | ~60% |
| Target deflection rate (conservative) | 50% |
| Cost per contact | Rs 90 |
| Build + first-year run (TCO) | Rs 30 lakh |

### A hint, not the answer

Fraud detection is a different kind of project (real-time data science, not document grounding). Loan
cross-sell carries trust and regulatory weight. Content generation has a different owner and brand
risk. Compliance and residency are constraints, not asks. Somewhere in the routine queries is one
groundable, high-frequency, high-value problem. Find it, and defend the choice.

## Deliverables

Submit the four filled artifacts (from the blank templates), in one folder:

1. `problem-selection-note.md` (Triage)
2. `problem-statement-and-options.md` (Frame)
3. `discovery-brief.md` (Discover)
4. `qualification-memo.md` (Qualify)

Plus the supporting tool worksheets (Pareto, RICE, MoSCoW, JTBD, HMW, 5 Whys, Power-Interest, RACI,
journey map, DVF, business case, value-driver tree).

## How you are assessed

See `solution-01.md` for the rubric. In short: the chain has to hold (each move's output is the next
move's input), the decision has to be defensible on evidence (numbers, not adjectives), and the
qualification memo has to name its assumptions and the exact no-conditions that would flip it.
