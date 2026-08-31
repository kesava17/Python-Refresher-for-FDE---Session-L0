# Assignment 01 · Compare three model configurations and defend a pick

> Offline practice for the LLM foundations topic. In the live lab you built the model layer (one
> interface, `generate` and `embed`, an offline mock behind it) and the comparison harness. Now use
> them the way a working FDE does: put three candidate model configurations on the same golden set,
> score them, and write one short recommendation that names a winner and defends it. The skill this
> builds is the one Sunrise is paying for: turning "which model?" from an opinion into an answer you
> can show. Everything runs offline. No API key, no network, no cost.

This is a do-it-yourself assignment. The point is to feel the difference between picking a model by
reputation and picking one by evidence. A stronger, more famous model is not automatically the right
one. The job decides, and for Sunrise the job is narrow: answer order, return, and simple-warranty
questions from provided text, cheaply, fast, in region, and escalate the sensitive warranty case
cleanly instead of guessing. You will find that the fit-for-purpose model beats the famous one on this
job, and you will have the table that proves it.

Start from your live-lab project, green, with the model layer and the comparison harness in place. The
harness runs offline against the shared golden question set:

```bash
cd liveLab
poetry run python -m model_layer.compare
```

The model interface is `model_layer.model` with `generate(prompt)` and `embed(text)`. The backing
model is selected by the `LLM_MODEL` environment variable and defaults to the offline mock, so nothing
here reaches a network or needs a key.

## The goal

One thing, done honestly: three candidate configurations, one golden set, one scored table, and one
defended paragraph. The recommendation must name the winner and give the reasons in Sunrise's terms:
capability on the golden set, cost at real volume, latency, and whether it can run where the data must
stay. Evidence, not vibes.

You produce two deliverables:

1. **The comparison table**, the raw output of the harness across all three candidates.
2. **A one-paragraph recommendation** that names the winner and defends the pick against the other two.

## The three candidates

Configure three candidates that differ in ways that matter to Sunrise, so the trade-off is real and
not cosmetic. A good set looks like this:

| Candidate | What it stands for | Capability level | Price (Rs / 1k tokens) | Hosting region |
| --- | --- | --- | --- | --- |
| A | A small on-prem model | low | 0.20 | Bharat |
| B | A mid on-prem model | good | 0.50 | Bharat |
| C | A large, famous hosted model | top | 2.00 | outside Bharat |

You can express the differences as three mock capability levels (as above), or as three
prompt-and-temperature settings on the same mock, whichever your harness supports. What must stay true:
all three run against the **same golden set**, and the hosting region is part of each candidate's
configuration, because residency is a hard rule for Sunrise, not a nice-to-have.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: set the three candidates

Edit the candidate list your comparison harness reads (name, capability level or temperature, price per
1,000 tokens, and hosting region for each). Keep A, B, and C meaningfully different: A is the cheapest
and smallest, B is a solid in-region middle, C is the strongest and most expensive and is hosted
outside Bharat. Do not tune the golden set to flatter any one of them.

Hint: the hosting region is a declared fact about where the model runs, not something the harness
measures. Carry it in the candidate config so it lands in the table beside the scores. A model that
cannot legally hold Sunrise's data is out regardless of how well it answers, so the table has to show
that fact next to the capability score.

### Level 2: run all three against the same golden set

Run the harness. It puts every candidate through the same golden questions (a handful of real order,
return, and warranty questions with known good answers) and reports, per candidate: the capability
score (how many golden answers were correct and grounded), the token cost at the price you set,
a latency figure, the hosting region, and the safety result on the warranty question.

```bash
poetry run python -m model_layer.compare
```

Your output is a table with one row per candidate. Something like:

```text
candidate  capability   cost/1k   latency   residency        warranty
A          5/8          Rs 0.20   210 ms    Bharat           escalates
B          8/8          Rs 0.50   380 ms    Bharat           escalates
C          8/8          Rs 2.00   910 ms    outside Bharat   escalates
```

Hint: the same golden set for all three is what makes the capability numbers comparable. If each
candidate is scored on a different set of questions, the column is theatre, not evidence. Reuse the one
golden set the whole phase uses.

### Level 3: read cost and latency at real volume

Capability is not the only axis. Sunrise runs thousands of tickets a week, so a price that looks small
per request adds up, and a customer is waiting on every answer. Read the cost column as a monthly bill,
not a per-call rounding error, and read latency as a person sitting on hold. Note where the candidates
separate: A is cheapest and fastest, C is the most expensive and slowest, B sits in the middle.

Hint: this is where the famous model usually loses on a narrow job. Top capability you do not need,
paid for at four times the price and twice the wait, is not a win. Weigh cost and latency against what
the job actually requires, which for Sunrise is "answer these support questions well", not "answer any
question in the world".

### Level 4: check the safety behaviour on warranty

Warranty is the sensitive category. Legal is not comfortable with a bot deciding warranty on its own,
so the model must not answer a warranty question as if it were settled fact. It must hand the decision
to a human with the context. Confirm each candidate escalates the warranty question cleanly rather than
inventing a warranty decision. A candidate that answers a warranty query confidently on its own is
disqualified, however well it scores elsewhere.

Hint: this is a pass or fail gate, like residency, not a weighted score. The demo model already answers
the warranty question cautiously and defers to a human; your job is to confirm each candidate you
picked does the same, and to treat a candidate that does not as out.

### Level 5: write the recommendation

Write one paragraph. Name the winner. Give the reasons in order of what decides the case: first the
hard constraints (residency and clean warranty escalation), then the weighed factors (capability on the
golden set, cost at volume, latency). Say explicitly why you did not pick each of the other two. A good
recommendation reads like the example the session gave: "model B, because it matched the golden set,
costs a quarter of C, and stays in Bharat."

Hint: hard constraints come first because they are gates. A model that fails residency or mishandles
warranty is out before capability or price is even weighed, no matter how strong it is. Only among the
candidates that clear the gates do you weigh capability, cost, and latency. Writing it in that order is
what makes the recommendation defensible instead of a preference.

## Done when

- [ ] Three candidates are configured and meaningfully different (capability, cost, and hosting region
  all vary), and all three run against the **same** golden set.
- [ ] The harness output table is captured, with one row per candidate showing capability, cost,
  latency, hosting region, and the warranty safety result.
- [ ] Capability is **scored** from the golden run, not asserted from reputation.
- [ ] The recommendation names one winner and defends it against both other candidates in Sunrise's
  terms: capability, cost at volume, latency, and residency.
- [ ] Residency is treated as a hard gate: a model that cannot keep Sunrise's data in Bharat is ruled
  out, not merely marked down.
- [ ] Warranty escalation is treated as a hard gate: a candidate that decides warranty on its own is
  ruled out.
- [ ] The winner is chosen for fit to this job, not for fame, and the paragraph says why the famous,
  strongest candidate was not the pick.

When every box is ticked, you have done the thing the session is really about: you turned "which model?"
into a scored answer you can defend to a room. The strongest model on paper was available the whole
time; you passed on it on purpose, and you can show the table that says why. The worked solution is in
`solution-01.md` if you want to compare, but try first.
