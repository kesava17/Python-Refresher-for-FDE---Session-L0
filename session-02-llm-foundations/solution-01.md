# Solution 01 · Compare three model configurations and defend a pick

> The worked solution for Assignment 01. Try the assignment yourself first. This is here to check your
> work, or to unstick you when you are truly stuck. There is no single correct row of numbers; there is
> a correct **method**, and a recommendation that follows from it. This solution shows both: a rubric
> for what a strong comparison looks like, and a reference recommendation for the Sunrise case.

The assignment is not really about the three candidates. It is about the habit: choose a model by
running a fair test and reading the result, not by reputation. So the grading is on the method as much
as the answer. A trainee who picks the right model for the wrong reasons has not learned the thing; a
trainee who runs a clean comparison and defends the pick in the job's terms has, even if their numbers
differ from these.

## What a strong comparison shows (the rubric)

Score your own work against these. The first four are the method; the last two are the traps.

| Criterion | What earns the mark |
| --- | --- |
| **Same golden set for all three** | Every candidate is scored on the one shared golden set, so the capability column is comparable. Different questions per candidate is theatre, not evidence. |
| **Scored, not asserted** | Capability is a number from the golden run (correct and grounded answers out of the total), not a claim copied from a blog post or a leaderboard. |
| **Weighs the factors that matter** | The recommendation weighs capability, cost at real volume, and latency together, not capability alone. A model you cannot afford or that keeps a customer waiting is not the best model. |
| **Honours the hard constraints** | Residency and clean warranty escalation are treated as gates, not weighted scores. A model that cannot keep the data in Bharat, or that decides warranty on its own, is out before any factor is weighed. |
| **Defends the pick** | The paragraph names the winner and says, in Sunrise's terms, why it beat each of the other two. A reader who disagreed could argue with the reasons, because the reasons are on the table. |
| **Avoids the fame trap** | The pick is the fit-for-purpose model, and the write-up explains why the strongest, most famous candidate was passed over. Picking the big name because it is the big name loses the mark even when the big name happens to score well. |

The trap in the last row is the one this assignment exists to catch. The strongest model on the
leaderboard is a real temptation, and on a narrow support job it is usually the wrong buy: you pay top
price and top latency for capability the job never uses, and it may not even be allowed to hold the
data. The discipline is to let the job, and the test, decide.

## The reference comparison

Here is a representative run of the three candidates from the assignment against the shared golden set.
Your numbers may differ; the shape and the reasoning are what matter.

```text
candidate  capability   cost/1k   latency   residency        warranty
A          5/8          Rs 0.20   210 ms    Bharat           escalates
B          8/8          Rs 0.50   380 ms    Bharat           escalates
C          8/8          Rs 2.00   910 ms    outside Bharat   escalates
```

Read the table before reading the recommendation, and the pick almost writes itself:

- **Candidate C is out on a hard gate.** It is hosted outside Bharat, so it cannot legally hold
  Sunrise's customer data. That rules it out no matter how well it answers, and it is also the most
  expensive and the slowest. Fame did not save it.
- **Candidate A clears the gates but is too weak.** It stays in Bharat and escalates warranty cleanly,
  and it is the cheapest and fastest. But 5 of 8 on the golden set means it gets basic support
  questions wrong, which is the one thing the bot exists to get right.
- **Candidate B clears the gates and does the job.** It matches the top capability score on this job,
  stays in Bharat, escalates warranty cleanly, costs a quarter of C, and answers well within a wait a
  customer will tolerate.

## The reference recommendation

> **Pick Candidate B.** It is the model that clears both hard constraints and then wins on the factors
> that matter. On residency it runs in Bharat, so Sunrise's customer data stays where it must; on
> safety it escalates the warranty question to a human instead of deciding it, which is the behaviour
> Legal requires. Among the candidates that clear those gates, B answers the golden set as well as the
> far more expensive Candidate C (8 of 8, correct and grounded), at a quarter of the cost per token and
> less than half the latency, which matters at thousands of tickets a week with a customer waiting on
> each one. Candidate A is cheaper and faster still, but it misses three golden questions, and getting
> basic order and return answers right is the whole point of the bot. Candidate C is the strongest name
> on paper, but it is hosted outside Bharat and so is disqualified on residency before cost or speed is
> even weighed. The evidence points one way: B is the fit-for-purpose model, and the table is the proof.

Notice the order of the argument. The hard gates (residency, warranty) come first and eliminate C
outright; only then are capability, cost, and latency weighed among the survivors. That order is what
makes the recommendation defensible rather than a preference. A recommendation that led with "C has the
best capability" and worked backward would have buried the fact that C was never eligible.

## Done when

- Three meaningfully different candidates ran against the one shared golden set, offline, with no key.
- Capability is a score from the run, cost and latency are read at real volume, and residency and
  warranty escalation are treated as hard gates.
- The recommendation names one winner and defends it against both other candidates in Sunrise's terms.
- The write-up says plainly why the strongest, most famous candidate was not the pick.

You have run the honest version of a decision teams usually make by reputation: a fair test, a scored
table, and a recommendation whose reasons are on the table for anyone to check. That is the instrument
Sunrise needs, and it is the one an interviewer wants to hear you describe: not "we used the popular
model", but "we ran three on our golden set and chose the one that fit the job, the budget, and the
rules".
