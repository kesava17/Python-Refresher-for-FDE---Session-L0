# Solution and rubric: Assignment 1 (drive your own account)

This is a Capstone drive, so there is no single correct answer. It is assessed on whether the chain
holds and the decision is defensible. Below is the rubric, then a reference read of the Pinnacle Bank
default so a reviewer knows the shape of a strong answer.

## Rubric

| Move | What a strong answer shows | Common traps |
| --- | --- | --- |
| **Triage** | Pareto finds the vital few from the volume table; RICE scores buildable candidates only; MoSCoW names an explicit Won't. One problem chosen on evidence. | Scoring an outcome or a constraint as if it were a buildable ask; an empty Won't bucket; picking the exciting item over the high-value one. |
| **Frame** | A tool-free problem statement the sponsor would accept; JTBD and the 5 Whys reach a real root; three genuinely different options. | A statement that names a tool; three shades of one idea; stopping the 5 Whys at a symptom. |
| **Discover** | Power-Interest surfaces a quiet high-power veto; RACI gives every task one Accountable; the journey map locates the real break; constraints and residency written down. | Missing the veto-holder; two Accountables; mapping the ideal journey; ignoring residency. |
| **Qualify** | DVF green on all three lenses; a business case in money and time; a value-driver tree with owned links; a memo with named no-conditions. | Adjectives instead of numbers; hiding the run cost in TCO; a memo with no no-conditions. |
| **The chain** | Each move's output is visibly the next move's input. | Artifacts that do not connect; the memo decides something the brief never scoped. |

Full marks need all four deliverables, the supporting worksheets, and a chain that holds end to end.

## Reference read: Pinnacle Bank

A strong answer converges here (yours may differ, but should be defended as well):

- **Triage.** Pareto on the volume table: transaction status (22%) + card services (20%) + balance and
  statement (18%) are about **60 percent** of contacts. That is the vital few. RICE ranks routine-query
  deflection far above fraud (a different, data-heavy project), loan cross-sell (trust and regulatory
  weight), and content generation (different owner). MoSCoW: Must = deflect those three routine types;
  Won't this quarter = fraud detection, loan cross-sell, content generation.
- **Frame.** Problem statement, tool-free: "customers cannot get an instant, correct answer to routine
  banking questions from information the bank already holds, so they wait on agents." Options: deflect
  (self-serve answers), route (classify to the right desk), assist (draft the agent's reply).
- **Discover.** Quiet high-power veto: **Compliance** (auditability and residency). IT owns core-banking
  access. Agents own adoption. Constraint: customer data stays in Bharat; every automated answer must be
  auditable. Narrow scope: transaction status, card services, and balance queries, from existing content,
  with escalation, and an audit log on every answer.
- **Qualify.** Business case: 8,000 contacts/week, ~60% in scope = 4,800; deflect 50% = 2,400/week; at
  Rs 90 per contact, run-rate saving is about 2,400 x 52 x Rs 90 = about Rs 1.12 crore a year, against a
  TCO near Rs 30 lakh, so payback is well under six months. DVF green (customers and agents both want it;
  the saving is large; standard grounding with an audit trail). GO, scoped and auditable, with the
  no-condition: NO if Compliance cannot accept the audit and residency design.

The single most important trap to catch: a trainee who picks **fraud detection** because it sounds
impressive. Fraud is real-time anomaly detection on transaction data, not document grounding, and it
fails the feasibility and quarter-end tests. A good answer parks it with a reason.
