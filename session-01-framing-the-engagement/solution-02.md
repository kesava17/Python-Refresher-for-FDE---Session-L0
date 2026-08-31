# Solution: Assignment 2 (the brownfield twist)

A worked reference. A trainee's answer can differ and still be right if it is honest and defensible.
The point of the exercise is that a named no-condition fired, and a good FDE re-qualifies rather than
either clinging to the old GO or panicking into a NO-GO.

## What changes, move by move

### Frame

The three options do not disappear, but a live legacy bot reweights them. "Deflect" is still the goal,
but it now means **replace** the old rules-based bot with a grounded answerer, not add a second bot
beside it. Two bots on one website is a worse experience, not a better one. So the framed option
becomes: replace the legacy FAQ bot with a grounded deflection assistant, and keep the "assist" path in
reserve for the questions that must stay with a human.

### Discover

Update the brief:

- **New system:** the legacy rules-based bot. Owner: the web team. It is wired into the site, customers
  dislike it, and agents route around it. Replacing it has a cost and a small migration risk, but
  removing a disliked bot is also a benefit.
- **New constraint:** Legal now requires a human in the loop for any warranty answer, simple or not. So
  simple-warranty leaves the automated scope and becomes a routed-to-human case.
- **Revised scope:** order-status and return questions, answered from Sunrise content, replacing the
  legacy bot, with warranty and everything else escalated to a human.

### Qualify

The no-condition "NO if Legal forbade warranty answers" has fired, partially. Warranty was 12 percent
of tickets; it is now out of automated scope. But the core (order and return) is untouched, so the
right move is to re-score, not to abandon.

Recompute the business case with simple-warranty removed:

| Line | Before | After |
| --- | --- | --- |
| In-scope share | ~60% (order + return + simple warranty) | ~49% (order + return only) |
| In-scope tickets / week | ~2,400 | ~1,950 |
| Conservatively deflected (50%) | ~1,200 | ~975 |
| Run-rate saving / year (at Rs 120) | ~Rs 74.9 lakh | ~Rs 60.9 lakh |
| TCO (first year) | ~Rs 24 lakh | ~Rs 30 lakh (adds legacy-bot replacement) |
| Payback | under four months | about six months |

DVF stays green: customers and agents still want it (desirability), the saving is still well above cost
(viability), and it is still buildable, now including a bot replacement (feasibility). The four gates
hold, with data readiness still amber.

## The decision

**GO holds, with a narrower scope.** Order-status and return deflection, replacing the legacy bot, with
warranty and out-of-scope questions routed to a human. Payback moves from under four months to about six
months, still comfortably positive. Updated no-conditions: NO if the legacy-bot replacement cannot be
delivered by quarter-end, or if order and return content proves unusable.

The teaching point: a fired no-condition is a trigger to re-decide, not an automatic NO. Here the core
value survives without the warranty slice, so the GO narrows rather than collapses. A trainee who flips
to a full NO-GO can still earn full marks if they show the core no longer pays, but with these numbers
it clearly still does, so the stronger answer is the defended, narrower GO.

## Change log (the second deliverable, illustrated)

- **Frame:** option shifts from "add a deflection bot" to "replace the legacy bot." Driver: fact 1
  (a chatbot already exists).
- **Discover:** added the legacy bot as a system and stakeholder with a replacement cost; moved
  simple-warranty from in-scope to escalation. Drivers: facts 1 and 2.
- **Qualify:** recomputed the business case (in-scope 60% to 49%, payback about six months), added the
  legacy replacement to TCO, updated the memo scope and no-conditions. Drivers: facts 1 and 2.
