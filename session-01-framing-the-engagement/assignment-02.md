# Assignment 2: The brownfield twist (re-qualify under new facts)

Sunrise is greenfield, so you chose freely. Real engagements rarely stay that clean. Three weeks after
your GO on Sunrise support deflection, two facts land that were not on the table when you decided. Your
job is to re-run the moves the facts touch and decide whether the GO holds, changes shape, or flips.

This assignment tests three disciplines the session builds: **brownfield thinking** (what already
exists changes the answer), **dynamic re-evaluation** (a decision is not frozen when the facts move),
and the **no-conditions** (you named exactly what would flip you; now check whether it fired).

## The new facts

1. **There is already a chatbot.** Sunrise has run a rules-based FAQ bot on its website for two years.
   Customers dislike it (it dead-ends and rarely answers the real question), and agents route around it.
   It is live, it is wired into the website, and someone owns it. This is a brownfield system you have
   to account for, not a blank slate.
2. **Legal has tightened.** After a recent consumer-court ruling, Legal now requires a human in the
   loop for **any** warranty answer, including the simple cases you had in scope. Automated warranty
   answers are off the table for now.

## Your task

Re-run only the moves these facts touch, and produce an updated decision. Use the blank worksheets in
`liveLab/templates/`.

- **Frame.** Does the option set change now that a chatbot already exists? Re-read the three options
  (deflect, route, assist) against a live legacy bot. Is the move now "replace," "sit beside," or
  "assist"? State it.
- **Discover.** Update the brief: add the legacy bot as a system and a stakeholder (who owns it, what
  it costs to replace or integrate), and update the constraint list with the new Legal rule.
- **Qualify.** This is the heart of it. One of your original no-conditions was "we would say NO if
  Legal forbade warranty answers." It has partly fired. Re-score:
  - Recompute the business case with simple-warranty removed from automated scope. (Hint: in-scope
    volume drops from about 60 percent to about 49 percent of tickets. Recompute the deflected volume,
    the run-rate saving, and the payback. Factor any cost of replacing the legacy bot into the TCO.)
  - Re-run DVF and the four gates.
  - Decide: does the GO hold, hold with a narrower scope, or flip to NO-GO? Defend it.

## Deliverables

1. An **updated qualification memo** (`qualification-memo.md`) with the new decision, evidence,
   assumptions, and no-conditions.
2. A short **change log** (half a page): what changed in Frame, Discover, and Qualify, and why. For
   each change, name the fact that drove it.

## What good looks like

You are not graded on whether the GO survives. You are graded on whether your re-qualification is
honest and defensible: the numbers are recomputed (not hand-waved), the legacy bot is accounted for as
a real cost and constraint, and the memo says clearly what changed and what would flip it now. A
well-argued narrowed GO and a well-argued NO-GO can both earn full marks. See `solution-02.md` for a
worked reference.
