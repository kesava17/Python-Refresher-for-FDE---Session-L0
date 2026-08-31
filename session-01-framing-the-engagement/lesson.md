# Framing the Engagement

> The AI for FDE program teaches the work of a Forward Deployed Engineer one stage at a time. This
> is the first session, and it covers the first stage of every engagement: turning a customer's
> vague wish list into a defensible decision about what to build.
>
> **This chapter is a working session, not a lecture.** You play the FDE on a real account. A wish
> list lands, and you drive it through four moves, Triage, Frame, Discover, and Qualify, until you
> can defend a go or no-go to a board. The concepts and the tools are introduced as you reach for
> them, and named in full as you use them.

This is the master chapter for the Framing the Engagement session, and you can read it on its own.
Most training starts with a concept and then looks for a place to apply it. An FDE never has that
luxury. Work arrives as a mess: a senior stakeholder, a list of half-formed wishes, a deadline, and
no clear problem. So this chapter starts the same way, with a real brief, and teaches each idea at
the moment you would actually use it. By the end you will have driven one engagement from a wish
list to a committed, defended decision, and you will hold a small toolkit of standard consulting and
product instruments you can carry to any account.

A note on shape. Every move in this chapter has the same skeleton, borrowed from the way a body of
knowledge like PMBOK describes a process: **Inputs**, a **Process**, the **Tools and techniques** you
apply, and the **Outputs** it produces. We call it ITTO. The output of one move is the input to the
next, so the four moves chain into a single framework. Learn the skeleton once, and every stage in
the rest of the program will feel familiar.

## Objective

After this session you can:

- Take a vague, over-wished customer brief and reduce it to one problem worth building, on evidence
  rather than on who pushed hardest.
- Run the four moves of the Frame stage (Triage, Frame, Discover, Qualify) and produce the artifact
  each one hands forward.
- Apply twelve standard consulting and product tools by name, and say when each one fits and when it
  does not.
- Read every move as a body of knowledge with the same ITTO shape: inputs, process, tools, outputs.
- Translate a technical problem into the business value language a board funds in.
- Hold your ground with a senior, impatient stakeholder without either caving or stonewalling.

## Coverage

The session moves in a straight line, from a messy brief to a committed decision:

1. **The engagement.** The Sunrise Electronics wish list and the ground truth behind it.
2. **The FDE's first job.** The homework nobody assigns.
3. **The Frame stage.** One framework, four moves, each with an ITTO shape.
4. **Move 1, Triage.** Choose the one problem. Tools: Pareto, RICE and ICE, MoSCoW.
5. **Move 2, Frame.** Define the problem and generate options. Tools: Jobs-to-be-Done, How Might We,
   the 5 Whys.
6. **Move 3, Discover.** Ground the options in what is true. Tools: Power-Interest grid, RACI, the
   customer-journey map.
7. **Move 4, Qualify.** Decide, and defend it. Tools: DVF, the business case, the value-driver tree.
8. **The wider picture.** Business value metrics, the brownfield reality, and the delivery framework
   you start building here.

At the end there is a recap and a pointer to the live lab, where you drive your own account through
the same four moves.

---

## The engagement: Sunrise Electronics

**Sunrise Electronics** is a fictional mid-size consumer-electronics retailer in Bharat: about sixty
stores, a growing online business, and a head office in Pune. It sells phones, appliances, and
accessories, along with its own-brand range. It is profitable but stretched, and leadership has
decided that "we need to do something with AI this year." No one there has shipped an AI system
before. This is a **greenfield** account: there is no AI in production today, so you can build clean.

The brief arrives as an email from **Vikram Rao, VP of Customer Experience**, forwarded to you after
a single kickoff call. Vikram is senior, board-facing, and impatient, the kind of stakeholder an FDE
has to hold ground with. Read the shape of it carefully. It is **not** a portfolio of separate AI
projects. It is **one** initiative, "AI for customer experience," with several internal stakeholders
each bolting on a different priority:

- **Support** is drowning in the same questions all day (order status, returns, warranty) and wants
  AI to take the load off.
- **Sales** wants the same assistant to upsell and cross-sell while it talks to customers.
- **Marketing and the CEO** want it on brand, and to generate help content and campaigns too.
- **Vikram** wants CSAT lifted, because his scores slipped last quarter.
- **IT** says the company has years of data, so "this should be easy," and it must integrate and be
  secure.
- **Finance** wants something to show the board by quarter-end, on a tight budget.

One direction, six agendas, no owner, and no value analysis. That is how real briefs arrive.

An FDE does not take the brief at face value. Here is the ground truth that a first week of listening
would surface. Treat it as the answer key for the moves ahead; do not hand it to the customer up
front.

- **Support deflection is the real, painful, frequent problem.** Agents handle roughly 4,000 tickets
  a week, and about 60 percent are the same handful of questions (where is my order, how do I return
  this, is it under warranty). Complex cases wait behind them. The answers already exist in
  documents.
- **The upsell bot is a different goal that fights the first one.** A bot trying to sell erodes trust
  in its answers, has no clear success measure yet, and raises the risk of a bad experience.
- **Generated marketing content is a different problem with a different owner**, and it carries brand
  risk. Park it.
- **"Lift CSAT" is an outcome, not a problem.** You cannot build higher CSAT; you can build ticket
  deflection and measure CSAT as one of its success metrics.
- **"We have the data" is an assumption, not a fact.** The help content and years of resolved tickets
  are usable, but there is no clean data warehouse, some knowledge lives only in agents' heads, and
  customer data has residency and privacy constraints: it must stay in Bharat.
- **The real constraint** is a demo by quarter-end on a tight budget, which rewards a narrow,
  groundable, high-frequency problem and rules out any long data project.

Everything that follows drives this one engagement from the messy brief to a defended decision.

## The FDE's first job is homework

The moment a wish list like this lands, an inexperienced engineer starts building the most exciting
item. An FDE does something less glamorous and far more valuable first. Before a single line of code,
the FDE has **homework**: read past the asks to the needs, separate the stakeholders and their
competing agendas, weigh each one honestly, and reduce the noise to a single problem that can be
defended. Nobody assigns this homework. The customer will not request it, and it will not appear on a
ticket. Doing it anyway is exactly what separates an FDE from an order-taker.

That homework has a structure, and it is the rest of this chapter: **Triage, Frame, Discover,
Qualify**. Each is a move with a clear input, a process, a set of tools, and an output. You run them
in order, and at the end you hold a decision a board can trust.

## The Frame stage: one framework, four moves

The four moves together are the **Frame stage** of an FDE engagement. A later session covers the
Prototype stage (choose a model, make it reliable, ground it, ship a clickable proof of concept). For
now, the pipeline is:

**Wish list → Triage → Frame → Discover → Qualify → a committed GO.**

Each move is a small body of knowledge with the same ITTO shape. Here is the whole stage at a glance;
the sections that follow give each move, and each tool, full treatment.

| Move | Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- | --- |
| **Triage** | the wish list, ticket volumes | weigh the asks; keep the vital few | Pareto, RICE and ICE, MoSCoW | a scored list; the one problem |
| **Frame** | the chosen problem | define it; generate distinct options | Jobs-to-be-Done, How Might We, 5 Whys | a problem statement; three options |
| **Discover** | the options, stakeholders, data | separate ask from need; map who and what | Power-Interest grid, RACI, journey map | a discovery brief; a stakeholder map |
| **Qualify** | the discovery brief | score, place, and decide | DVF, business case, value-driver tree | a qualification memo; a go or no-go |

One rule holds for the whole session: we do not start with theory. You name the shape of a move, then
run it live on Sunrise, then read the result back through the same four boxes. Starting with Triage.

---

## Move 1: Triage

An FDE's first day on an account rarely begins with a clear problem. It begins with a brief like the one Vikram Rao sent Sunrise Electronics: one direction ("AI for customer experience"), six teams each bolting on their own priority, no owner, no value analysis, and a deadline. The temptation is to start building the thing everyone named. That temptation is the first mistake. Before any code, before any architecture, an FDE has to reduce the noise to one problem worth solving. That reduction is **triage**.

**Triage** is the systematic process of prioritizing incoming items by urgency, severity, and the resources you actually have. The word and the discipline come from military medicine: field surgeons in World War I, facing more wounded than they could ever treat at once, needed a fast, repeatable rule for deciding who got attention first. The French verb *trier* means to sort, and that is exactly what triage does. It does not heal anyone. It sorts the incoming stream so that scarce resources land where they change the outcome most, and so that nothing critical waits behind something trivial.

That origin gives triage a shape you will reuse for the rest of your career: the **three-bucket model**.

- **Critical / urgent.** Immediate action, needs resources now. In the ED, the trauma case. On an incident bridge, the outage taking the site down.
- **Non-critical.** Deferred or queued, low risk in waiting. The minor fracture that can wait an hour. The cosmetic bug that ships next sprint.
- **Unserviceable.** Rejected or dropped, not worth the resources. The case that cannot be helped with what you have, or the request whose cost dwarfs its value.

The single most important property of triage is this: **it routes, it does not resolve.** Triage decides what gets attention, not how to fix it. A triage nurse does not perform surgery; an on-call engineer running triage does not write the fix in that moment. They place each item in a bucket and move to the next. Confusing the two (trying to solve while you sort) is how triage breaks down, because you stop sorting and the queue behind you grows.

You already know triage, because the same move runs in every field that faces more demand than capacity:

| Domain | What is triaged | Objective | Example |
| --- | --- | --- | --- |
| **Emergency medicine** | patients arriving at the ED | stabilize the critical first | trauma treated now; a minor fracture waits |
| **Incident response (SRE)** | alerts, outages, bugs | contain blast radius, cut downtime | fix a database pool crash before a UI alignment bug |
| **Product and support** | tickets, bugs, feature requests | protect throughput and stability | a P0 auth outage now; a missing export icon later |
| **Project management** | tasks, emails, backlog items | protect focus, hit deadlines | Eisenhower: sort by urgent versus important |

The stakes change from a life to a bug ticket, but the discipline is identical: assess fast, sort into buckets, act on the vital few, re-check as things change. As the FDE on Sunrise, you are running the product-and-support row of this table, applied to an AI wish list. Vikram's six asks are your incoming stream. Your job is to sort them honestly, defend the sort, and hand forward one problem.

### Principles of effective triage

Four principles separate real triage from a gut call dressed up as a process.

**Speed and decisiveness.** Triage is fast by design. You assess an item quickly, place it, and move on. The goal is placement, not perfection: a roughly right sort delivered now beats a perfect sort delivered after the queue has overwhelmed you. For an FDE this matters because a stakeholder like Vikram is impatient and board-facing. You cannot spend three weeks studying six asks before you say anything. You need a defensible first sort in days, then refine.

**Dynamic re-evaluation.** Priorities are not fixed. An item you parked as non-critical can turn critical when context shifts: a low-volume question type becomes urgent after a product recall, or a deferred ask becomes central when a competitor ships it. Good triage builds in the habit of revisiting the sort as new facts arrive. You are not committing to the sort forever; you are committing to acting on the best sort available right now, and to updating it.

**Resource awareness.** Priority is never absolute. It is always relative to the resources you have: the engineers, the compute, the budget, the calendar. The same ask can be critical in an organization with a large team and a year, and unserviceable in one with two engineers and a quarter. Sunrise has a tight budget and a single quarter, so "can we realistically resource this now" is part of every judgment. An ask that would need a six-month data project is effectively unserviceable this quarter, regardless of how appealing it sounds.

**Route, not resolve.** This is the principle FDEs most often violate. Under pressure to look useful, an engineer starts designing the solution to an ask while still sorting the list, and the sort never finishes. Hold the line: triage produces a prioritized list and a chosen problem. It does not produce a design. The design comes later, in Frame, and only for the problem that survived triage.

### Triage as a body of knowledge (ITTO)

To run triage deliberately rather than by instinct, it helps to see it as a small body of knowledge with a fixed shape. This is the ITTO shape (Inputs, Tools and techniques, Outputs, wrapped around a Process) that PMBOK uses to describe any repeatable practice. Every move in the Frame framework has this same shape, and the output of one move becomes the input to the next. For triage, the boxes look like this:

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| Incoming demands (requests, tickets, asks) with their urgency and severity signals, plus the resources and constraints you have | Assess each item fast; score it; sort into critical, non-critical, and unserviceable; re-evaluate as context shifts | Pareto (80/20), weighted scoring (RICE or ICE), MoSCoW, the Eisenhower matrix | A ranked, scored priority list: the critical few to act on now, plus an explicit deferred set and dropped set, each with a reason |

Read the table left to right. Raw demands and your real constraints come in. The process assesses and sorts them, using the tools in the third column to make the sort defensible rather than arbitrary. A prioritized list comes out, with one problem chosen for the next move. The rest of this section works through the three tools that carry most of the weight for an FDE (Pareto, RICE and ICE, and MoSCoW), then shows all three converging on Sunrise.

### Tool: Pareto (the 80/20 rule)

**The Pareto principle**, commonly called the **80/20 rule**, states that roughly 80 percent of the effects come from about 20 percent of the causes. In prioritization terms: a small share of the items usually carries most of the impact, and a large share of the items carries very little. Find that small share first, and you have found where your resources belong.

**Origin.** The principle is named for **Vilfredo Pareto**, an Italian economist who observed around 1896 that about 80 percent of the land in Italy was owned by about 20 percent of the population, and that the same lopsided split showed up in the pea pods in his own garden. The quality engineer Joseph Juran later generalized the observation into a management tool and coined the memorable label for the small, high-impact group: the **vital few**, as opposed to the **trivial many** (also called the long tail). The exact numbers are not sacred. It might be 70/30 or 90/10 in a given dataset. What matters is the shape: impact concentrates.

**The mechanics.** Using Pareto is mechanical and fast, which is why it fits triage:

1. Pick the measure that represents impact: volume, cost, revenue, crash frequency, whatever the decision turns on.
2. List the items and their value on that measure.
3. Sort the list in descending order, largest first.
4. Read down from the top and watch where the cumulative total crosses the bulk of the effect. The items above that line are your vital few.

The output is a short head you should act on and a long tail you can safely defer or drop.

**When to use it.** Pareto is the right first tool whenever you have a long, unsorted list and need to find concentration fast: which customers, which bugs, which question types, which cost centers dominate. It answers exactly one question, "where is the impact concentrated," and it answers it cheaply. That makes it a natural opening move in triage, before you reach for anything heavier.

**When not to use it, and common pitfalls.** Pareto is a lens, not a law, and it has failure modes an FDE must respect:

- **When impact is genuinely uniform**, there is no vital few to find, and Pareto tells you nothing. Not every distribution is lopsided.
- **The long tail is not always worthless.** In some businesses (niche retail, insurance, fraud) the aggregate of many rare cases is where the money or the risk lives. Dismissing the tail on reflex can be a serious error. Always check what the tail sums to before you drop it.
- **You measured the wrong thing.** Pareto is only as good as the measure you chose. Sorting support tickets by raw volume finds the most frequent questions, but if your real goal were reducing cost, a rare ticket type that takes two hours each to resolve might outrank a common one that takes two minutes. Choose the impact measure that matches the decision.
- **Concentration can shift.** Today's vital few may not be next quarter's. Pareto is a snapshot, and it pairs with the dynamic-re-evaluation principle: re-run it when the data moves.

**Worked example: Pareto on Sunrise's tickets.** Sunrise's support agents handle roughly 4,000 tickets a week. Instead of treating that as one undifferentiated flood, break it down by question type and sort by volume, highest first.

| Question type | Share of tickets | Approx. weekly volume | In the vital few? |
| --- | --- | --- | --- |
| Where is my order | about 30 percent | about 1,200 | yes |
| How do I return this | about 18 percent | about 720 | yes |
| Is it under warranty (simple cases) | about 12 percent | about 480 | yes |
| Everything else (the long tail) | about 40 percent | about 1,600 | no: many rare, varied types |

The pattern is textbook Pareto. Three question types account for about 60 percent of every ticket that comes in (roughly 2,400 tickets a week). The remaining 40 percent is not one problem; it is a long tail of many different, infrequent question types, each rare on its own. The reading for an FDE is sharp and immediate: if you can answer those three high-volume questions well, you move most of the total volume with one focused build. Just as importantly, Pareto tells you what not to chase. Trying to handle the entire long tail with automation would mean high effort spread across dozens of rare cases for little aggregate return, and those varied edge cases are exactly where an automated answer is most likely to be wrong. Here the tail also happens to be the safest thing to leave with human agents, which reinforces the sort. Pareto has done its job: it has pointed at the concentration and told you where the first PoC should aim.

### Tool: RICE and ICE (weighted scoring)

Pareto tells you where the volume is. It does not, by itself, tell you which competing initiative is worth building, because volume is only one factor and Vikram's six asks differ on several. For that you need a **weighted scoring model**: a method that turns opinions ("I feel support matters most," "no, upsell drives revenue") into comparable numbers, so the ranking is defensible in a room full of competing priorities. The two most useful for an FDE are **RICE** and **ICE**.

**RICE.** RICE scores each candidate on four factors and combines them into one number:

> **Score = (Reach x Impact x Confidence) / Effort**

- **Reach:** how many people or events the initiative affects in a given period. Wider reach scores higher.
- **Impact:** how much it moves the outcome for each of those people or events. Bigger impact scores higher.
- **Confidence:** how sure you are of your Reach and Impact estimates, expressed as a discount on your own optimism. Lower confidence pulls the score down, which is the point: it penalizes guesses.
- **Effort:** what it costs to build and run, usually in person-time. It sits in the denominator because cost should shrink the score, not grow it.

The three numerator factors multiply, so a weakness in any one drags the whole score down, and the result is then divided by effort. The unit is arbitrary; what matters is that every candidate is scored the same way, so the numbers are comparable.

**ICE.** ICE is the lighter cousin, useful when you have less data and want a first cut quickly:

> **Score = Impact x Confidence x Ease**

It drops Reach and replaces "Effort in the denominator" with "Ease" as a positive multiplier (high ease scores high, which is just the inverse of high effort). ICE is faster to run and good enough for an early sort, but it is coarser: without an explicit Reach term it can flatter a high-impact idea that only touches a handful of users.

**How to score.** In practice you pick a simple scale (a 1 to 5 scale is common, higher is better) and rate each candidate on each factor, ideally with more than one person so the numbers are not one individual's bias. The scale should have rough anchors ("Reach 5 = affects nearly all customers, Reach 1 = affects a niche") so different people score consistently. Then compute the formula and rank. The discipline is not the arithmetic; it is being forced to state, for each ask, how many it reaches, how much it helps, how sure you are, and what it costs, out loud and in the same units as every other ask.

**When to use RICE versus ICE.** Reach for **RICE** when the candidates differ a lot in how many users they touch and you have enough information to estimate reach and effort with a straight face: it is the better model for defending a decision to a skeptical VP, because it makes reach and cost explicit. Reach for **ICE** at the very earliest stage, when you are triaging a pile of ideas quickly and lack the data for reliable reach or effort numbers. Many teams use ICE for the first pass and RICE for the finalists.

**Pitfalls.** Weighted scoring has two classic failure modes an FDE must guard against:

- **False precision.** The formula produces a number like 40, which looks objective and authoritative. It is not. It is built entirely from subjective 1-to-5 judgments. The number is a communication and comparison aid, not a measurement. Treat a score of 40 versus 38 as a tie; treat 40 versus 6 as a real signal. Never let the tidy arithmetic hide how soft the inputs are.
- **Gaming.** Because the inputs are subjective, whoever holds the pen can nudge a favored initiative up by scoring its Impact a 5 and its Effort a 1. When six stakeholders each brought their own priority, this is a live risk. The defenses are to score openly with the group, to anchor each scale to concrete definitions, and to have the person most skeptical of an ask score its optimistic factors. Confidence is your friend here: it is the honest place to record "we are not actually sure this works."

**Worked example: RICE on Sunrise's asks.** Score the three main build candidates from Vikram's brief on a 1 to 5 scale (higher is better on every factor except Effort, which divides).

| Ask | Reach | Impact | Confidence | Effort | Score |
| --- | --- | --- | --- | --- | --- |
| **Support deflection** | 5 | 4 | 4 | 2 | (5 x 4 x 4) / 2 = **40** |
| Upsell bot | 4 | 3 | 2 | 4 | (4 x 3 x 2) / 4 = 6 |
| Marketing content generation | 3 | 2 | 2 | 3 | (3 x 2 x 2) / 3 = 4 |

Interpret the spread. Support deflection scores **40**, an order of magnitude above the other two. Every factor points the same way: wide reach (it touches the 60 percent of tickets Pareto already flagged), real impact (freeing agents from repetitive load), high confidence (the answers already exist in Sunrise's own help content, so you are not betting on unproven capability), and low effort (a standard grounded-answer build, not a research project). The upsell bot scores a **6**: narrower reach, lower confidence (a selling bot has no clear success measure yet and may erode trust in its answers), and high effort. Marketing content generation scores a **4**: modest reach, low impact on the support pain, and unresolved brand-risk questions. The gap between 40 and single digits is not a close call you would argue about; it is a decisive separation you can put in front of Vikram on evidence, not opinion. That is the entire value of scoring: it turns "I think support matters most" into a ranked table that a board-facing VP can read and defend upward.

### Tool: MoSCoW (scope prioritization)

Pareto found the concentration and RICE ranked the candidates, but there is still one job left in triage: drawing an explicit line around what the chosen work will and will not include, agreed with the stakeholders. That is **scope prioritization**, and the standard tool is **MoSCoW**.

MoSCoW sorts every item into one of four buckets. The capital letters spell the name (the lowercase o's are just filler):

- **Must have.** The release genuinely fails without it. This is the non-negotiable core.
- **Should have.** Important and high-value, but the release survives a short delay if it slips. Painful to leave out, not fatal.
- **Could have.** Nice to include if time and budget allow. The first things cut under pressure.
- **Won't have this time.** Explicitly out of scope for this release, and named as such so it does not quietly creep back in.

**Origin.** MoSCoW was developed by **Dai Clegg** at Oracle in the 1990s and became a core prioritization technique of **DSDM** (Dynamic Systems Development Method), an agile delivery framework. It was built for exactly the situation an FDE faces: fixed time and budget, more requirements than can fit, and a need to agree scope with the business rather than impose it.

**The power of the explicit "Won't."** The Must, Should, and Could buckets are useful, but the bucket that does the real work is **Won't have this time**. Most prioritization schemes only rank what you will do; they leave everything else in a vague "later" cloud that each stakeholder privately assumes includes their pet feature. MoSCoW forces you to name, out loud and on the page, what you are deliberately not doing this round. That naming is what protects a scope from six stakeholders each pushing their own item. Two further points make the "Won't" powerful. First, it is "Won't have *this time*," not "never": it is a sequencing decision, not a rejection, which is far easier for a stakeholder to accept. Second, it converts a silent assumption into an explicit, agreed statement, so when Sales asks in week three where the upsell feature went, the answer is "we agreed together it was a Won't-this-quarter, here is why," not a fresh argument.

**Pitfalls.** MoSCoW has one dominant failure mode, and it is common: **everything becomes a Must.** When stakeholders sort their own items, each one's priority feels essential, and the Must bucket swells until it contains the entire wish list, at which point the tool has told you nothing. The disciplines that prevent this: cap the Must bucket (some teams require that Musts consume no more than about 60 percent of the available effort, leaving real room for Should and Could to absorb overruns), demand a concrete justification for every Must ("the release is pointless without it" must be literally true), and make sure the Won't bucket is not empty. A MoSCoW sort with nothing in Won't has not actually prioritized anything.

**Worked example: MoSCoW on Sunrise's scope.** Take the six competing asks and the deflection problem the earlier tools chose, and sort the scope for this quarter's PoC.

| Bucket | Scope items | Why here |
| --- | --- | --- |
| **Must have** | Deflect the three high-volume question types (order status, returns, simple warranty) with grounded, correct answers from Sunrise's own content | This is the core problem Pareto and RICE identified; without it there is no PoC |
| **Should have** | Clean escalation to a human agent for anything out of scope or low-confidence | The release survives a short delay on polish, but a bot with no safe exit is not shippable, so this is high on the list |
| **Could have** | Track CSAT on deflected chats; add further question types from the long tail later | Valuable, but not required to prove the concept this quarter; the first things to cut if time runs short |
| **Won't have this quarter** | Upsell and cross-sell inside the bot; generated marketing content and campaigns | Explicitly out of scope for this round, named so Sales, Marketing, and the CEO see their items sequenced with a reason, not silently dropped |

The result is a scope every stakeholder can read. The two asks most likely to derail a support project (Sales' upsell and Marketing's content generation) are placed in Won't-this-quarter with an explicit rationale, which is a sequencing decision they can accept, not a flat rejection they will fight. Vikram gets a shippable quarter with a defined core. And nobody's item vanished into an unspoken "later"; it is on the page, in a named bucket, agreed.

### The call: one problem, defended

The three tools were not run to please every team. They were run to make one pick you can defend, and they converge on the same answer:

- **Pareto** put the volume squarely on three repetitive question types (about 60 percent of all tickets).
- **RICE** scored support deflection at 40 against single digits for the alternatives, on reach, impact, confidence, and effort.
- **MoSCoW** made those three question types the Must, escalation the Should, and pushed upsell and content generation to Won't-this-quarter.

Three different lenses, one chosen problem: **support deflection**, answering the high-frequency order, return, and simple-warranty questions from Sunrise's own help content, with escalation to a human for everything else. Nothing was rejected on politics. Each deferred ask was sequenced with a reason a stakeholder can read: the upsell bot and generated content go to Could or Won't this quarter, and Vikram's "lift CSAT" is reframed from a project into a metric you will measure on the deflected chats. Every one of the six agendas can see where its item landed and why.

One step remains before triage hands anything forward: the **feasibility gate**. A high-scoring problem is still worthless if it cannot actually be built, so you check three things fast:

- **Is it even an AI problem?** Yes. Answering varied natural-language questions from a body of documents is squarely what modern language models plus grounding are good at. It is not a rules-engine or a reporting dashboard mislabelled as an AI ask.
- **Is the data there?** Largely yes. The help center content and years of resolved tickets exist and are usable, though "we have tons of data" is an IT assumption you will verify properly in Discover, and tribal knowledge in agents' heads is a known gap.
- **What is the risk?** Bounded. A wrong "where is my order" answer, caught by human escalation, is low harm. The one area needing care (warranty answers) is exactly why simple-warranty is scoped narrowly and escalation is a Should.

Support deflection clears the gate. That produces the output of triage: a **scored priority list with one chosen problem**, defended on evidence. That single chosen problem is the input to Move 2, Frame, where you stop sorting and start turning the ask into a sharp, tool-free problem statement with real options.

### Why triage matters

You cannot build six stakeholders' priorities at once, and building the wrong thing well is still a failure. Triage is the discipline that buys you one problem worth solving, chosen on evidence, separated from the politics piled onto it, and defensible to a VP asking hard questions. Skip it, and you try to satisfy every team at once: you spread thin, burn the quarter and the budget, and the customer's real problem is still sitting there untouched. Focus is the FDE's first act of value. Choosing well, early, is worth more than building fast.

---

## Move 2: Frame

Triage handed you one problem worth the quarter: support deflection. You walked back into the room, and before you could open your notebook Vikram said the thing every stakeholder says at this moment. "Great, so build the support bot." It is a reasonable sentence. It is also a trap, and stepping over it is the entire skill of this move.

**Framing** is the work of turning a vague ask into a sharp, tool-free problem statement plus a set of genuinely different options, before anyone picks a tool. Notice the two halves. The first half is subtraction: you strip the request down until what remains is an outcome and a person, with no product name attached. The second half is expansion: from that clean problem you deliberately generate two or three real ways to solve it, so the choice that comes later is an actual choice and not a rubber stamp on the first word someone said.

This is the define-and-ideate heart of design thinking. Design thinking runs in a loop, and framing lives across its middle two stages:

- **Empathize.** Understand the user and the job they are trying to get done. You watch the work before you word the problem.
- **Define.** State the problem as one clear sentence about an outcome and a user. This is where "build a chatbot" gets rejected and "customers cannot get an instant, correct answer" gets written.
- **Ideate.** Diverge into distinct options, so the later decision has something to decide between.

The reason framing has to be taught, rather than assumed, is that the instinct it fights is universal. Every serious field has a name for the mistake of jumping to a solution before the problem is understood:

- In **medicine**, the trap is treating the symptom that presents. A patient reports headaches; the reflex is to prescribe a painkiller. The framed version asks what underlying condition produces the headaches, because the painkiller that hides a tumor is worse than no treatment at all.
- In **engineering**, the trap is building the feature that was requested. A user asks for a faster horse, and a literal engineer breeds a faster horse. The framed version asks what job the user is trying to do, which might be "get to the next town before dark," a job a horse is only one way to serve.
- In **consulting**, the trap is answering the question exactly as the client asked it. The client asks "should we enter the Chennai market," and a junior consultant runs a Chennai market study. The framed version asks what decision the client actually faces, which might be "where do we spend next year's growth budget," a question Chennai is only one candidate answer to.
- In **AI projects**, the trap is building the bot everyone named. The stakeholder says "chatbot," the team builds a chatbot, and six weeks later it demos well and helps no one, because it was fitted to the tool instead of the problem.

The same error wears four costumes, but it is one error: mistaking the first-named solution for the problem. What makes it sharper for a Forward Deployed Engineer is that **AI has made building the wrong thing fast.** A generation ago, the cost of building the literal request was a natural brake. You could not accidentally ship a full support system in a week, so someone, somewhere, was forced to stop and think. Today you can stand up a plausible chatbot in an afternoon. The brake is gone. Speed to a working demo is now the easiest thing in the project, which means the discipline of not building yet, of holding the problem open long enough to understand it, is the scarce and valuable thing. Framing is that discipline.

### Principles of effective framing

Four principles separate a frame from a wish repeated back.

**Separate the problem from the solution.** A frame names the outcome to reach and the person it is for. It never names a tool. The test is mechanical: read your problem statement and look for a noun that is a product, a technology, or an implementation. "Chatbot," "app," "dashboard," "model," "automation" are all solution words. If one appears, you have not framed a problem; you have described a solution and hoped it matches a problem. "Build a chatbot" is a solution wearing a problem's clothes. Underneath the costume there is a real problem ("customers wait too long for answers that already exist"), and that real problem might be better served by something that is not a chatbot at all.

**Ground the frame in observation.** Frame from what you saw, not from what was reported. Vikram's email is a report, filtered through his priorities and his vocabulary. Before you trust it, you watch an agent work for an hour, read fifty real tickets, and try to find an answer in the help center yourself. Reported reality and observed reality are never the same, and the gap between them is usually where the real problem hides. An FDE frames from the ground, not from the brief.

**Diverge before you converge.** Generate distinct options first, and resist narrowing until you have them. The danger of narrowing early is invisible: you never see the option you skipped, so you never learn it would have won. If the first idea is a self-serve answerer and you commit to it immediately, you never discover that routing tickets to the right queue would have shipped faster and carried less risk. Divergence is cheap insurance against a confident early mistake.

**The test of a good frame** is two-part and both parts must hold. First, the stakeholder reads it and says "yes, exactly." That confirms you captured the real problem and not a strawman. Second, it names no tool. A statement that passes only the first test ("yes, we do need a chatbot") is a shared assumption, not a frame. When it passes both, you have a problem sharp enough to reason about and open enough to solve more than one way. If it names a tool, reframe.

### Frame as a body of knowledge (ITTO)

Like every move in this session, framing has the shape of a small body of knowledge: it takes defined inputs, runs a process on them with specific tools, and produces defined outputs. This is the same four-box structure PMBOK uses for project processes, and reading it left to right tells you what framing consumes and what it hands to the next move.

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The one problem chosen in triage; direct observation of the real work; the customer's own words and the tool they named | Understand the user and the job they hire the work to do; find the root cause behind the stated symptom; write one sharp, tool-free problem statement; then diverge into genuinely different options | Jobs-to-be-Done (JTBD); How Might We (HMW); the 5 Whys | A problem statement the stakeholder agrees with and that names no tool, plus two or three distinct options the next move can test |

The input to framing is the output of triage: one chosen problem, not six competing asks. The output of framing becomes the input to Discover: a clean problem and a short menu of options whose value is still, at this stage, a set of educated guesses. The three tools below are how you get from one to the other.

### Tool: Jobs-to-be-Done (JTBD)

**Jobs-to-be-Done** is a way of understanding demand by asking what job a person is trying to get done, rather than what product they say they want. The idea was sharpened by Harvard's Clayton Christensen, and its core claim is deceptively simple: people do not want a product, they hire it to make progress in a situation. The product is a means. When a better means shows up, they fire the old one and hire the new one, but the job itself stays the same. Christensen's teaching example is the quarter-inch drill: nobody wants a drill, they want a quarter-inch hole, and really they want the thing the hole is for (a shelf on the wall, a picture hung). The drill is disposable; the job endures.

The tool has a fixed shape, a job statement written from the user's point of view:

> **"When [situation], I want to [motivation], so I can [outcome]."**

Each clause does work. The **situation** anchors the job in a moment of real life, which keeps it concrete. The **motivation** names what the person is trying to do in that moment. The **outcome** names the deeper progress they are after, the reason the motivation matters. A well-written job statement is legible to the person it describes: they would read it and nod.

The reason JTBD is powerful in framing is that **the job is stable while tools change.** Customers have wanted a correct answer to "where is my order" since long before chatbots, and they will want it long after. Phrasing the problem as a job strips away the current fashionable tool and leaves the durable need, which is exactly the tool-free problem statement framing is trying to reach. It also protects you from building features nobody hired: if a proposed feature does not serve a real job, it is decoration.

**When to use it.** Reach for JTBD at the start of framing, when the request is phrased as a product ("a support bot," "an app") and you need to recover the underlying need. It is especially useful when several stakeholders each named a different tool, because their tools may all serve the same job, and naming the job dissolves the argument.

**Pitfalls.** Two are common. The first is writing the tool into the job by accident: "when I have a question, I want to open the chatbot, so I can get an answer" has smuggled the solution back into the situation clause. Keep tools out of all three clauses. The second is pitching the outcome too shallow. "So I can get an answer" is a restatement of the motivation, not a deeper outcome. Push one level further: why does the answer matter to them? The honest answer at Sunrise is that a waiting customer is a worried customer, and the job is as much about ending the worry as about the fact.

**Worked example on Sunrise.** The support ask actually contains two jobs, one for each person the deflection touches, and writing both is what breaks "support bot" apart.

- **The customer's job:** "When I have a question about my order, return, or warranty, I want a correct answer immediately, so I can stop worrying and not wait in a queue." The situation is a moment of uncertainty after a purchase. The motivation is a correct answer, now. The outcome is relief and the absence of a queue. Nothing in that sentence is a chatbot.
- **The agent's job:** "When routine questions flood in all day, I want them handled without me, so I can spend my time on the complex cases that actually need a person." The agent is not hiring a chatbot either. The agent is hiring anything that removes repetitive load so their skill goes where it matters.

Hold the two statements side by side and the reframe is obvious. Neither person's job is "a chatbot." Both jobs reduce to the same thing: an instant, correct answer to a common question, drawn from knowledge Sunrise already has. "Build a support bot" has become "get customers self-serve answers to common questions," which is a problem, not a product, and a problem that more than one kind of solution could serve.

### Tool: How Might We (HMW)

**How Might We** is a technique for turning a defined problem into an open, optimistic question that invites solutions. It comes from the design world, popularized by IDEO and now standard in design thinking practice, and its whole purpose is to move a room from defending a single answer to generating many. The phrasing is deliberate. "How" assumes a solution exists and asks for the path to it. "Might" keeps it tentative and permission-giving, so people offer half-formed ideas instead of only defensible ones. "We" makes it a shared effort. Put together, "how might we..." is a doorway from problem to ideas.

The shape is a single question:

> **"How might we [achieve the outcome] for [the user]?"**

optimistic, open, and free of any named tool.

The hardest part of writing a good HMW is **altitude**, meaning how broad or narrow the question is pitched. Too broad and it gives you nothing to work with: "how might we fix support" is true but useless, because every idea in the world is a valid answer and none is prompted. Too narrow and it hides the very divergence the tool exists to create: "how might we add a chatbot to the website" has smuggled the answer into the question, so the only ideas it invites are variations of one idea. A good HMW sits in the middle. It is specific enough to point at a real outcome and a real user, and open enough that several genuinely different solutions could answer it.

**When to use it.** Use HMW right after you have a clean job statement and before you brainstorm options. It is the hinge between define and ideate. It is also a fast way to check your framing: if you cannot phrase your problem as an open "how might we" without naming a tool, your problem statement is probably still a disguised solution.

**Pitfalls.** The main one is altitude, covered above, and it fails in both directions, so calibrate consciously rather than trusting your first phrasing. A second pitfall is loading the question with a constraint that is really a solution ("how might we use our knowledge base to..."), which quietly rules out options before anyone speaks. Keep constraints that are genuine (the answer must come from content Sunrise owns) and drop constraints that are just a preferred implementation.

**Worked example on Sunrise.** Take the job you recovered with JTBD and phrase it as an invitation:

> "How might we give Sunrise's customers an instant, correct answer to their most common questions, without tying up an agent?"

Check its altitude. It is not "how might we fix support" (too broad to prompt anything) and it is not "how might we build a chatbot" (too narrow, answer pre-chosen). It names the outcome (an instant, correct answer), the user (Sunrise's customers), and a real constraint (without tying up an agent), and it names no tool. That is the middle altitude, and at that altitude the question does exactly what it is meant to do: it invites more than one answer. Ask it in a room and three distinct families of solution fall out:

- **Deflect:** answer the customer directly so no ticket is ever opened.
- **Route:** if a ticket is opened, classify it and send it to the right queue so the answer arrives faster.
- **Assist:** let a human agent stay in the loop, but draft their reply for them so they answer more in less time.

Each genuinely satisfies the question, and each is a different bet. That is the sign the HMW was pitched right: the problem now has a real menu, not a foregone conclusion.

### Tool: The 5 Whys

**The 5 Whys** is a root-cause technique: you take the stated problem and ask "why" repeatedly, each answer becoming the subject of the next "why," until you pass the symptom and reach a cause you can actually act on. It originated with Sakichi Toyoda, the founder of Toyota Industries, and became a core practice of the Toyota Production System, where it is used on the factory floor to stop a defect from recurring rather than just cleaning it up each time. The number five is a guideline, not a law. Sometimes the root is three whys down, sometimes seven; the discipline is to keep going until the answer stops being a symptom.

The mechanic is iterative and strict about the chain. You do not brainstorm five separate causes; you ask why about the previous answer, so each step is one link deeper than the last. Done well, the ladder walks you from a visible complaint down to the structural cause underneath it.

**When to stop.** The signal to stop is a change in the quality of the answers. While you are still in symptom territory, each "why" yields another changeable fact ("because they all go to a human"). When you hit the root, the next "why" either produces a cause you can actually change (stop here, you have found it) or it produces "that is just how it is," a fact of nature or policy you cannot move (stop here too, you have hit the wall). The root worth framing is the last changeable cause before that wall.

**Pitfalls.** Two are worth naming. The first is **single-track thinking**: a problem can have more than one root, and a single ladder finds only one of them. If the pain plausibly has several causes, run more than one chain. The second, and the one Toyota warns about most, is **blaming people instead of systems.** When a "why" lands on "because the agent forgot" or "because support is understaffed," it is tempting to stop and assign fault. Push past it. "Understaffed" is usually a symptom of a deeper cause (too many tickets reach a human that need not), and the actionable root is in the system, not the person. A root that blames an individual almost never survives contact with reality.

**Worked example on Sunrise.** Start from Vikram's own words and ladder down:

- **"Support is drowning."** Why? Because agents answer the same handful of questions all day.
- Why do those questions reach an agent at all? Because there is no way for a customer to get the answer without opening a ticket.
- Why can the customer not self-serve? Because the answers, while they exist, live only inside help pages and years of past tickets that no one can search well.
- Why is that content not enough as it stands? Because it is not written as answers to the questions customers actually ask, and it is not available instantly at the moment of need.
- **Root:** customers cannot get an instant, correct answer to a common question from content Sunrise already owns.

Notice where the ladder does not stop. It would have been easy to halt at "support is understaffed" and conclude the answer is "hire more agents," or to halt at "no chatbot" and conclude the answer is "build a chatbot." Both are symptoms. The next "why" past each of them keeps giving changeable answers, so neither is the root. The wall appears only at unreachable answers, and that root is not a staffing problem or a missing product. It is a reachability problem, and it is exactly what a deflection option addresses. The 5 Whys did not invent the frame; it confirmed it from a third direction, which is why it belongs alongside JTBD and HMW rather than replacing them.

### The call: a sharp problem and three options

Three tools, run on the same chosen problem, converged on the same place. JTBD stripped the request to a durable job. HMW turned that job into an open question at the right altitude. The 5 Whys traced the pain to a root you can act on. Where they meet is the output of this move: one problem statement and a short menu of options.

The **problem statement**, tool-free and agreed with the stakeholder:

> "Support agents spend most of their day answering the same order, return, and warranty questions, which delays the complex cases that need a person. How might we give customers instant, correct answers to those questions from Sunrise's own content?"

Read it against the test. Vikram reads it and says "yes, exactly," because it names his real pain. And it names no tool: not a chatbot, not a model, not an app. It passes both parts.

The **three options**, each a genuinely different bet, with a first-impression read on value and readiness:

| Option | What it is | First-impression value | First-impression readiness |
| --- | --- | --- | --- |
| **Deflect** | A self-serve answerer that gives the customer a grounded answer directly, so no ticket is opened | High: it removes the volume at the source | Looks ready: the answers already exist in Sunrise's content |
| **Route** | A classifier that reads an incoming ticket and sends it to the right queue, so the answer arrives faster | Medium: it speeds resolution but does not cut volume | Has training signal: years of resolved, labelled tickets to learn from |
| **Assist** | An agent copilot that drafts a reply for a human to review and send | Medium: it makes each agent faster but keeps a human in every loop | Depends on adoption: only helps if agents actually use it |

State plainly what these reads are. **They are guesses.** "Data looks ready," "medium value," "needs adoption" are first impressions formed from Vikram's brief and an hour of watching, not facts checked against Sunrise's real content, real tickets, and real constraints. You cannot commit a quarter and a budget on first impressions. That is not a weakness in the framing; it is the reason the next move exists. This problem statement and these three options, guesses and all, are the input to **Discover**, whose entire job is to replace the guesses with facts before anyone builds.

### Why framing matters

"Build a chatbot" is a tool, and if you accept the customer's tool you commit to their guess instead of solving their problem. Framing is how you refuse that quietly and productively: you understand the job, find the root, write the problem as an outcome for a person, and put real options on the table, so the eventual solution is a choice you can reason about rather than the first word anyone happened to say. Skip it and you build the first idea; it will demo well and it will not land, because it was fitted to the tool and not to the customer. The tool must serve the problem, and framing is how you keep that order right, most of all now that AI makes building the wrong thing quick and cheap.

---

## Move 3: Discover

Framing produced options. It did not produce facts. At the end of the previous move, Sunrise Electronics had a clear problem statement about self-serve answers and three named ways to attack it (Deflect, Route, Assist), but the two things that decide whether any of them is worth building, the value and the readiness, were still first impressions. "Support deflection looks high value" was a hunch. "The data is probably usable" was a hope. "Legal will be fine with warranty answers" was an assumption nobody had checked. Discover is the move that turns those guesses into ground truth before you commit anyone's money or reputation to them.

**Discovery is functional analysis: grounding the framed options in what is actually true.** It has two jobs that run together. The first is to separate the stated ask from the real need, because the words a customer writes in a brief are a starting point, not the specification. The second is to map the terrain the solution will live inside: the stakeholders who can help or block, the data and where it really lives, the systems it must work with, and the constraints that quietly decide what is buildable. The one-line version an FDE keeps in their head is **"ask is not need."** Vikram Rao asked for one AI thing that deflects tickets, upsells, stays on brand, lifts CSAT, and ships this quarter. The need, once you look, is much narrower and much more buildable. Discovery is how you find the difference without guessing.

This is not a technique someone invented for AI projects. It is one of the oldest disciplines in professional work, and it wears different names in different fields. In software it is **requirements engineering, business analysis, and user research**: the practice of finding out what a system must actually do before anyone writes code. But the deeper pattern is universal. Before any good decision, someone does the unglamorous work of finding out what is real.

- In **medicine**, a doctor takes a history, examines the patient, and orders tests before prescribing. Skip that, and you treat the wrong condition.
- In **journalism**, a reporter sources and verifies before publishing. Skip that, and you print a false story.
- In an **audit**, the auditor traces records back to evidence before signing. Skip that, and you certify a fiction.
- In **software**, the team gathers requirements and studies real users before building. Skip that, and you ship the wrong system, correctly.

The FDE version of the rule is blunt: **a week of listening before a quarter of building.** The cost of discovery is always smaller than the cost of the wrong build, because discovery is measured in days of conversation and observation, while a wrong build is measured in a delivered system nobody can use, a vetoed launch, or a sponsor who has stopped returning your calls. Discovery is the cheapest insurance an engagement ever buys.

### Principles of effective discovery

Discovery done well follows a few disciplines that separate real grounding from a round of polite meetings.

**Go and see.** Reported reality and actual reality are never quite the same, and the gap is where projects die. Do not accept "we have years of data" as a fact about your project; ask to see the data, open a sample of resolved tickets, and read the help center the way a confused customer would. At Sunrise, "IT says we have years of data so this should be easy" is a claim. Going and seeing reveals that the data is real but scattered across a public help center, an internal knowledge base, and years of resolved tickets, with no clean warehouse tying them together and some knowledge living only in agents' heads. That is a very different starting point from "just integrate it," and you only learn it by looking.

**Follow the constraints.** Legal limits, data residency, budget, and timeline shape what is buildable more than any technical choice does. A constraint discovered late is a project killed late, after you have spent the budget. At Sunrise, three constraints reshape the whole engagement: customer data must stay in Bharat (residency), Legal will only allow warranty answers for simple, groundable cases and not disputes, and there is a quarter-end demo on a tight budget. None of these were in the technical design; all of them decide it. An FDE hunts for constraints early and treats each one as a fact to build around, not an obstacle to argue with.

**Find every veto.** Anyone who can say no is a stakeholder, whether or not they hold a title over the project. The people most likely to sink you are the quiet ones with real power who were never in the room. At Sunrise, Legal can veto warranty answers and IT controls access to the data and systems; neither wrote the brief, and both can stop the build cold. Meet every veto-holder before you commit, not after they surface in month two.

**Listen with a purpose.** Discovery is not "tell me everything." It is a directed search for the two things that decide the engagement's fate: **what would make this fail, and who could stop it.** Every interview, every data sample, every system walkthrough is aimed at those two questions. That focus is what turns weeks of listening into a short, decision-ready brief instead of a pile of notes.

### Discover as a body of knowledge (ITTO)

Like every move in this course, discovery can be described as a small process with defined inputs, a process that acts on them, the tools that do the acting, and the output it produces. Reading the table left to right: the framed problem and its options come in, observation and mapping act on them, and a grounded brief comes out. The framed options are raw material, still full of assumptions; discovery is the work that replaces those assumptions with verified facts.

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The framed problem and its options; access to people, tickets, systems, and documents; the stated ask and its implicit assumptions | Separate ask from need; interview stakeholders and find every veto; trace where the data and the answers actually live and what state they are in; map the customer journey to locate the real break; list the constraints and who owns each one | Power-Interest grid (Mendelow's matrix); RACI; customer-journey map; stakeholder interviews; document and data sampling; going and seeing | A discovery brief: the real need, the data and its state, the systems, the constraints (including residency and legal limits), the stakeholders and their vetoes, and a narrowed, permitted scope |

The three named tools in the middle column carry most of the weight, and the rest of this section treats each one in full. A Power-Interest grid tells you where to spend attention and who can block you. A RACI grid makes sure every decision has exactly one owner. A customer-journey map shows you where the pain actually sits so the solution lands on it. Together they produce the brief that Qualify will judge.

### Tool: The Power-Interest grid (Mendelow's matrix)

**Definition.** The Power-Interest grid, also called Mendelow's matrix after the analyst who popularised it, is a stakeholder-mapping tool. You list everyone the project touches, then plot each person or group on a two-by-two grid formed by two axes. The grid sorts a messy list of names into four groups, each with a clear handling strategy, so your limited attention goes where it changes the outcome.

**The two axes.** The first axis is **power**: how much ability this stakeholder has to affect the project, especially the ability to stop it. Power comes in many forms, and formal job title is only one of them. Legal has power because it can veto a whole category of answers. IT has power because it controls access to the data and the systems you need. A single senior sponsor has power because they hold the budget. The second axis is **interest**: how much this stakeholder cares about the project and its outcome, how closely they will follow it, and how much it affects their daily work. A support agent has enormous interest, because the tool will change how they spend every hour of their day, even though they hold little formal power over the decision to build it. Power and interest are independent. The whole value of the grid comes from separating them, because they call for completely different handling.

**The four quadrants.** Each stakeholder falls into one of four cells, and each cell has a standing instruction.

- **High power, high interest: manage closely.** These are the people who can both shape the project and want to. They get your steady, direct attention: regular updates, early sight of decisions, and a real voice. They are your closest partners and often your sharpest critics at the same time.
- **High power, low interest: keep satisfied.** These stakeholders can block you but are not following the day-to-day. The danger is that they lose interest right up until the moment you cross a line they care about, and then they exercise their power decisively. You keep them satisfied by getting their sign-off on the specific thing they care about early, and by not flooding them with detail they do not want.
- **Low power, high interest: keep informed.** These people cannot make or break the decision, but they care deeply and are affected daily. You keep them informed and, crucially, involve them, because their cooperation often decides whether a technically sound build actually gets used.
- **Low power, low interest: monitor.** These stakeholders neither drive the project nor are much affected by it. You keep a light eye on them in case their position changes, but you do not spend scarce attention here.

**When to use it.** Reach for the Power-Interest grid at the very start of discovery, as soon as you have a framed problem and before you plan a single meeting. It tells you who to interview first, how much of each person's time to ask for, and, most importantly, who could block the project that you have not yet spoken to. Redo it whenever the stakeholder picture changes, for example when a new executive inherits the account or a new regulation brings a new veto-holder into scope.

**Pitfalls.** The most expensive mistake is **treating a quiet high-power stakeholder as low priority because they are not making noise.** A veto-holder who is not in your meetings still holds the veto. Legal at Sunrise is exactly this trap: not loud, not in the kickoff call, medium interest at most, and able to kill the entire warranty use case. Grade stakeholders by the power they hold, not by how much they are currently participating. A second pitfall is confusing interest with power and over-investing in an enthusiastic stakeholder who cannot actually decide anything, while under-serving a bored one who can. A third is treating the grid as a one-time exercise; power and interest shift over an engagement, and a stale grid is worse than none because it gives false confidence.

**Worked example: Sunrise stakeholders.** Placing the four stakeholders the deflection PoC touches makes the strategy for each one concrete.

| Stakeholder | Power | Interest | Quadrant and strategy |
| --- | --- | --- | --- |
| **Vikram Rao (VP CX)** | High: sponsor, holds the budget, board-facing | High: it is his initiative and his CSAT problem | Manage closely. Your sponsor and your sharpest skeptic at once. Regular direct contact, early sight of every decision. |
| **Legal** | High: can veto warranty answers outright | Medium: cares about the warranty category, not the rest | Keep satisfied. Get the warranty scope defined and signed early, so the veto becomes a boundary you build inside, not a surprise at launch. |
| **IT** | High: owns the data and the systems, controls access | Medium: interested in security and integration, not the CX outcome | Keep satisfied. Agree data access and integration terms early, in writing, with dates. |
| **Support agents** | Low (formal): no say in the build decision | High: the tool reshapes their daily work; their adoption decides success | Keep informed and involve. They make or break adoption. Bring them in during discovery, not after go-live. |

The grid pays for itself here by surfacing two facts the brief hid. Legal is a high-power veto that is easy to miss because it has low visibility, and support agents have no formal power yet decide whether the built system is actually used. Both change the scope and the plan.

### Tool: RACI

**Definition.** RACI is a responsibility-assignment tool. For each task or decision in the project, it assigns four roles, one letter each:

- **R, Responsible:** the person or people who do the actual work. There can be several.
- **A, Accountable:** the single person who owns the outcome and answers for it. There is exactly one.
- **C, Consulted:** the people whose input is sought before the work is done or the decision is made. Two-way communication.
- **I, Informed:** the people who are told after the fact and kept in the loop. One-way communication.

You lay the tasks down the rows and the people across the columns, then fill each cell with R, A, C, I, or leave it blank. The result is a single grid that says, for every piece of work, who does it, who owns it, who gets a say, and who just needs to know.

**The one-Accountable rule.** The single most important discipline in RACI is that **every task has exactly one Accountable.** Not zero, not two. If two people are Accountable, then when the task slips each can point at the other, and no one truly owns it. If no one is Accountable, the task falls through the cracks with everyone assuming someone else had it. One Accountable per row is the rule that makes the whole tool work; the "I thought you had it" failure is precisely what it exists to prevent. Multiple people can be Responsible (they share the doing), but ownership of the outcome cannot be shared.

**When to use it.** Build a RACI grid during discovery, once the Power-Interest grid has told you who the players are, and specifically when the project crosses organisational boundaries. An FDE almost always works across the customer's org: the content comes from one team, the sign-off from another, the build from you, the legal boundary from a third group. RACI is how you make handoffs explicit and give every decision a named owner instead of an audience of people who all assume it is handled. It is most valuable exactly where work passes from one team to another, because that is where things get dropped.

**Pitfalls.** The two classic failures are structural. The first is **more than one Accountable on a task**, which dissolves ownership; enforce the one-A rule without exception. The second is **making everyone Consulted**, which feels inclusive and collaborative but grinds decisions to a halt, because now every choice needs a committee. Consultation is a cost; spend it only where the input genuinely changes the outcome. A related trap is a row that is all C and I with no R and no A, which means a task everyone is watching and nobody is doing. If a row has no R, the work will not happen; if it has no A, no one will notice.

**Worked example: the Sunrise deflection PoC.** Assigning roles for the key tasks in the PoC turns vague good intentions into a grid with a named owner on every line.

| Task | Vikram (VP CX) | Legal | IT | Support ops / agents | FDE (you) |
| --- | --- | --- | --- | --- | --- |
| **Approve warranty answer scope** | A | R | I | C | I |
| **Provide help content and resolved tickets** | A | I | R | C | I |
| **Build the deflection PoC** | A | I | C | C | R |
| **Sign off on go-live** | A | C | C | I | R |

Read the grid and the discipline shows. Vikram is the single Accountable on every row: one owner, board-facing, the person who answers for the whole PoC, exactly as his sponsor role demands. Legal is Responsible for defining the warranty scope and is Consulted at go-live, so the veto-holder shapes the boundary early instead of ambushing the launch. IT is Responsible for the content and ticket handoff, which turns "IT says we have the data" from a vague reassurance into an explicit, owned task that can be given a date. You, the FDE, are Responsible for the build and for driving go-live, while consulting IT and agents so the thing you build fits the systems it must live in and the people who must use it. Nothing on this project now waits on "someone."

### Tool: The customer-journey map

**Definition.** A customer-journey map lays out the steps a customer actually takes to accomplish something, end to end, and records for each step what they do, what they are trying to achieve, and where it hurts. It is a stage-by-stage picture of a real experience, drawn from the customer's side rather than the company's. Its purpose in discovery is to show, with evidence rather than intuition, exactly where a solution should sit, because the worst pain on the map is your best opportunity.

**The stage-by-stage layout.** You lay the stages of the journey left to right across the top, in the order the customer lives them. For each stage you capture three things:

- **Action:** what the customer actually does at this step.
- **Goal:** what they are trying to achieve, the outcome they want.
- **Pain:** what goes wrong, what frustrates them, where they stall or give up.

Reading across the row of pains tells you where the experience is worst. Reading down at any stage tells you what the customer wanted there and why they did not get it. A solution should sit at the stage where the pain is sharpest and where fixing it does the most good, not wherever the technology is easiest to bolt on.

**Where a solution should sit.** The map's payoff is placement. A fix dropped at the wrong stage solves a slide, not a customer. If the pain is that customers cannot find an answer, then a faster support queue treats a symptom two stages downstream while the real break goes untouched. The map forces you to put the solution at the exact stage where the journey fails, and to see the surrounding steps the solution must respect, such as the moment where a wrong answer would do real harm and an escalation to a human is mandatory.

**When to use it.** Draw the journey map during discovery, after you understand the stated problem and want to confirm from the customer's side where it actually lives. It is especially valuable for customer-facing solutions, where the whole point is to change an experience, and it pairs naturally with the framed problem: the map either confirms the frame from the customer's point of view or reveals that the real break is somewhere the frame did not expect.

**Pitfalls.** The dominant mistake is **mapping the ideal journey instead of the real one.** It is tempting to draw the experience as the company wishes it worked: the customer visits the help center, finds the answer, and leaves happy. The real journey is where the value is, and it is usually messier, full of dead ends and give-ups. Map what actually happens, drawn from real tickets and real observation, not the polished version in a strategy deck. A second pitfall is mapping only the happy path and ignoring the failure branches, which are exactly where solutions matter most. A third is stopping at emotions without tying each pain to a concrete action, which produces a map that feels insightful but points at nothing you can build.

**Worked example: a Sunrise "where is my order" question.** Tracing one common customer through the journey shows precisely where deflection belongs.

| Stage | What the customer does | Goal | Pain today |
| --- | --- | --- | --- |
| **Question arises** | Checks email, then goes to the Sunrise website | Find out where the order is, fast, on their own | No obvious place to get an instant self-serve answer |
| **Looks for help** | Scans the help pages, then gives up | Get the answer without talking to anyone | The content is written as articles, not as answers to their actual question. This is the break. |
| **Contacts support** | Opens a ticket or waits on chat | Reach a human who can tell them | Queue is backed up behind the same common questions |
| **Waits** | Checks back later for a reply | Get resolution and move on | Slow, and the answer turned out to be simple |

The sharpest pain is at **"looks for help."** The answer to "where is my order" genuinely exists in Sunrise's content, but it is unreachable because the content is not written as a direct answer to the question the customer is asking. That is exactly where deflection sits: intercept the customer at the "looks for help" stage and give them the answer that already exists, before they ever join the support queue. Everything downstream (the queue, the wait) is a consequence of the break at that one stage. The map confirms the frame from the customer's side and puts the solution on the precise point of failure.

### The call: the discovery brief

The three tools do not produce three separate documents. They converge into one artifact, the **discovery brief**, which is the single output of this move and the single input to the next one. Each tool contributes its part. The Power-Interest grid supplies the stakeholders and, critically, their vetoes. RACI turns those stakeholders into owned tasks with dates. The customer-journey map locates the real break and, with the ask-versus-need work, states the real need. Layered on top are the data reality and the constraints that going and seeing surfaced. The brief is short on purpose: it is a decision-ready summary, not a research dump.

For Sunrise, the brief reads:

- **Real need:** customers cannot get an instant, correct answer to common questions from content that Sunrise already owns. (Not "an AI assistant that does everything," which was the ask.)
- **Data and its state:** the public help center and the internal knowledge base hold the answers, and years of resolved tickets add more; all are usable. But there is no clean data warehouse tying them together, and some knowledge is tribal, living only in agents' heads. That tribal knowledge is a known gap, not a hidden surprise.
- **Stakeholders and vetoes:** Vikram (sponsor, single accountable owner), Legal (holds the warranty veto), IT (owns data and systems access), support agents (hold adoption).
- **Constraints:** customer data must stay in Bharat (residency); Legal limits warranty answers to simple, groundable cases and excludes disputes; the demo is due at quarter-end; the budget is tight.
- **Narrowed scope:** order-status, return, and simple-warranty questions, answered from Sunrise's own content, with a clean escalation to a human for anything outside that boundary (including warranty disputes).

Notice what changed. The value and readiness reads that were guesses at the end of Frame are now facts. The warranty use case, which the brief treated as one undifferentiated block, has been split by Legal into simple-and-groundable versus disputes-and-not, and only the safe half is in scope. The residency constraint that no one mentioned in the kickoff is now written down where it will shape the architecture. The scope has shrunk from "one AI thing that does everything" to a narrow, groundable, permitted target that a small team can actually ship by quarter-end. This brief is what you carry into Qualify, where a grounded picture becomes a defensible go or no-go decision.

### Why discovery matters

The ask is not the need, and the assumptions hiding inside your framed options are exactly where projects die in month two. Discovery is the move that finds them while you can still act: the veto-holder you had not met, the data messier than promised, the constraint nobody named. Skip it, and you commit on hope, then get stopped by a Legal review you never scheduled or a residency rule you never checked. Do it, and you walk into the next move knowing the customer's reality better than the customer wrote it down. That is where an FDE's credibility comes from, and it is the difference between a demo that ships and a build that stalls.

---

## Move 4: Qualify

Qualification is the move where you convert a grounded picture into a decision you can defend. Discover handed you a brief full of facts: the real need, the state of the data, the stakeholders who can veto you, the constraints you must live inside, and a scope narrowed to what is real and permitted. That brief is not yet a decision. It is the raw material for one. Qualify is where you take that material and produce a single, owned, defensible judgment: build this, or do not, and here is exactly why.

The mental model to hold is that **you are the underwriter of your own project**. An underwriter does not decide whether a loan or a policy is exciting. The underwriter decides whether the numbers, the risks, and the evidence add up to a case that will survive scrutiny, and then signs their name to that case. When you qualify an AI use case, you are writing the document a skeptical board reads *instead of* trusting your enthusiasm. Enthusiasm does not appear in that document. Evidence, numbers, assumptions, and named failure conditions do.

This gate-before-commitment pattern is universal. Every serious field puts a formal check between "this looks promising" and "we are committing real resources," and in every field the check has the same shape: assemble the evidence, weigh the upside against the downside, and let one owner make a call that can be defended later.

- **Investing** runs **due diligence** before it funds. The analyst does not fund a company because the founder is charismatic. They read the accounts, check the claims, and produce a memo that says fund or pass.
- **Medicine** runs a **risk and benefit assessment** before a major intervention. The surgeon weighs the likely benefit of operating against the risk of the operation itself, and decides to operate or not.
- **Lending** runs **credit underwriting** before it approves. The underwriter checks income, history, and collateral against the size of the loan, and approves or declines.
- **AI projects** run a **feasibility, value, and risk assessment** before the build. You check whether the thing can be built, whether it is worth building, and what could go wrong, and you produce a go or no-go.

The domain changes. The discipline does not. In each case a case is made, a decision is owned, and the reasoning is written down so it can be checked. That is what you are doing for Sunrise Electronics: turning the discovery brief on support deflection into a memo Vikram Rao can carry to his board, one that holds up when the board asks hard questions.

### Principles of effective qualification

Four principles separate real qualification from a rubber stamp on a decision you had already made.

**Try to kill your own idea.** The most valuable thing you can do at this gate is argue the *no* case as hard as you argue the *yes* case. If support deflection is a good idea, it will survive your best attempt to break it: your best argument that the data is unusable, that the saving is overstated, that Legal will block it, that adoption will fail. A go that survives your own attack is one that will survive the board's attack. A go that you never seriously challenged is a hope wearing the costume of a decision. Try to kill your idea before the customer's reality does it for you, in month two, after the budget is spent.

**Use numbers, not adjectives.** "High value," "big opportunity," and "strong fit" are opinions dressed as findings. They cannot be checked, so they cannot be defended, and a room full of stakeholders each brought their own adjectives already. A payback period measured in months is a fact. A run-rate saving in rupees is a fact. Qualify in the units the business actually runs on: money, time, tickets, hours. When you replace "support is expensive" with "payback under four months on a conservative deflection rate," you have moved from something arguable to something checkable.

**Name the no-conditions.** State, out loud and in writing, exactly what would flip your decision from go to no-go. For Sunrise that is two specific conditions: if the help content proved unusable, or if Legal forbade warranty answers. Naming the no-conditions does the opposite of what people fear. It does not weaken the yes; it makes the yes credible. A go that admits precisely what would break it reads as the product of honest analysis. A go with no stated failure conditions reads as advocacy, and a skeptical board discounts advocacy.

**Practice honesty under pressure.** Qualification is the hardest move to do well because the pressure to skip it is highest exactly when you most need it. Vikram is impatient. The board wants something to see by quarter-end. Everyone in the room would rather start building than sit through a risk assessment. That pressure is not a reason to wave the gate through. It is the reason the gate exists. The discipline of qualification is the willingness to hold the check when every incentive is pushing you past it.

### Qualify as a body of knowledge (ITTO)

Like every move in the Frame framework, qualification has a body-of-knowledge shape: named inputs come in, a defined process acts on them using specific tools, and a concrete output comes out. Reading the move this way, in the same four boxes used across the whole session, keeps it repeatable. You are not improvising a decision; you are running a process whose steps you can name and whose output you can hand forward.

The inputs to qualification are everything the earlier moves produced: the discovery brief, the set of framed options, and the constraints and deadline that bound the engagement. The process tests the surviving candidate against three lenses (do people want it, does it make business sense, can we build it), converts the value into money and time, traces the value link by link, places the candidate against its alternatives, and names the conditions that would flip the call. The tools are the ones that make each of those steps rigorous. The output is a single artifact: a qualification memo carrying a go or no-go, the evidence behind it, the assumptions it rests on, and the exact no-conditions.

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The discovery brief; the framed options; the constraints and the deadline; the ground truth about data, systems, and vetoes | Test desirability, viability, and feasibility; build the business case in money and time; trace the value link by link; place the candidate against its alternatives; name the conditions that would flip the decision | DVF (desirability, viability, feasibility); the business case (ROI, payback period, TCO, NPV); the value-driver tree; the feasibility-by-value grid | A qualification memo: a defensible go or no-go, with the evidence, the assumptions, and the exact no-conditions that would flip it |

Read it left to right. A grounded brief comes in on the left, the decision tools act on it in the middle, and a defensible memo comes out on the right. The rest of this section works through each tool in turn, then assembles the call.

### Tool: DVF (Desirability, Viability, Feasibility)

**DVF** is a three-lens test for whether an idea is worth building. It comes from the design-and-innovation tradition associated with IDEO and Tim Brown, where it is used to sort promising concepts from ones that only look promising. The claim behind it is simple and strict: a good idea has to clear three separate bars at the same time, and clearing two of the three is not a pass. Most failed projects failed not because the idea was bad on every axis, but because it was strong on two and quietly weak on the third, and nobody made the third axis explicit until it was too late. DVF forces the third axis into the open.

The three lenses ask three different questions:

- **Desirability** asks: *do the users actually want this, and will they adopt it?* This is the human question. Not "would it be useful in principle," but "will the real people in the real workflow reach for it and keep using it." A technically excellent tool that nobody adopts has zero desirability and therefore zero value, no matter how well it is built.
- **Viability** asks: *does this make business sense?* Is there enough value on the table, at an acceptable cost, to justify doing it at all? Viability is where you confront the money. An idea can be deeply desired and perfectly buildable and still fail this lens because the value does not exceed the cost of getting it.
- **Feasibility** asks: *can we actually build it, with the data, the risk tolerance, and the time we have?* This is the engineering question, and for an AI project it is specifically about whether the data exists in a usable state, whether the risk is bounded, and whether the thing can be delivered inside the deadline.

**Why all three must be green.** The three lenses catch three distinct ways to fail, and a green on one lens does nothing to cover a red on another. A desirable, feasible idea that is not viable burns money to delight people. A desirable, viable idea that is not feasible is a business case for something you cannot deliver. A viable, feasible idea that is not desirable is a well-built, affordable tool gathering dust. Only the idea that is green on all three is a real go. This is why DVF is a *test* and not a *score*: you do not average the three. Any single red is a stop.

**DVF maps directly onto the FDE's three hats.** The Forward Deployed Engineer wears the product hat, the field hat, and the engineering hat at once, and DVF is those three hats written as a decision lens:

- The **field hat** (what the customer actually needs, whether they will use it) is **desirability**.
- The **product hat** (what is worth building) is **viability**.
- The **engineering hat** (what will hold up) is **feasibility**.

So running DVF is not a separate skill bolted onto the FDE mindset. It is the FDE mindset applied at the decision gate. When you check all three lenses, you are refusing to let any one of your three hats make the call alone.

**Worked example: Sunrise support deflection through DVF.**

*Desirability: green.* Two distinct groups want this, and their jobs-to-be-done were already surfaced in Discover. Customers want an instant, correct answer to a common question (where is my order, how do I return this, is it under warranty) so they can stop worrying and skip the queue. Agents want the flood of routine questions handled without them, so their time goes to the hard cases that actually need a person. Both jobs are real, and crucially they point the same way: the customer wanting self-serve answers and the agent wanting the routine load gone are two views of the same solution. When both the end user and the internal user pull toward the same thing, desirability is strong.

*Viability: green.* Roughly half of the 4,000 weekly tickets are deflectable repetitive questions. Even on a conservative deflection assumption, the saving is real and it is set against a modest build cost. The business case (worked below) turns this into a payback under four months. That clears the viability bar comfortably.

*Feasibility: green, with one amber.* The solution is a standard grounding shape: answer common questions from content the company already owns, with escalation to a human for anything out of scope or uncertain. Sunrise's help center and its years of resolved tickets exist and are usable, so the content to ground on is there. The harm from a wrong answer is low because escalation catches the edge cases, and it is buildable by quarter-end. The one amber is that some knowledge lives only in agents' heads (tribal knowledge) rather than in any document, so a slice of answers is not yet groundable. That is a real gap, but a bounded one: it constrains scope, it does not sink the build. A single amber inside an otherwise green lens is a condition to manage, not a stop.

**The contrast that proves the tool is working.** Run the Sales team's upsell idea through the same three lenses and it fails where deflection passes. Its *desirability* is weak: a bot that is trying to sell while it answers a support question erodes trust in its answers, and customers did not ask to be sold to mid-problem. Its *viability* is weak too: there is no clear success measure for in-chat upsell yet, and the risk of a worse experience offsets the speculative revenue. Upsell might be buildable, but buildable is only one lens. DVF is what lets you tell Sales, on evidence rather than on preference, that their idea is not a go this quarter: it never cleared desirability or viability, and no amount of feasibility rescues that.

### Tool: The business case (ROI, payback, TCO, NPV)

The business case is where you translate the value out of adjectives and into the language a board actually funds in: money and time. A board does not buy "AI for support." It buys a number it can defend to whoever it answers to. Four numbers carry most of that translation.

- **ROI (return on investment)** is the return you get relative to what you spent, usually stated as a percentage or a ratio. In plain terms: for every rupee you put in, how many rupees come back. It answers "was this worth doing at all," and it is the number people quote most often, though on its own it hides *when* the return arrives.
- **Payback period** is how long it takes for the savings (or new revenue) to repay the cost of building and running the thing. It is measured in time: months or years. Payback is the number that lands hardest with a budget-conscious sponsor, because "this pays for itself in under four months" is immediately graspable in a way a percentage is not. Its limit is that it ignores everything that happens after the payback point.
- **TCO (total cost of ownership)** is the full cost of the solution across its life, not just the sticker price of building it. It includes the build *and* the run: the ongoing model and infrastructure cost, monitoring, maintenance, content upkeep, and the human escalation path. The single most common way a business case lies is by counting only the build cost and quietly ignoring the run cost. TCO is the discipline of counting both.
- **NPV (net present value)** recognizes that a rupee saved next year is worth less than a rupee saved today, because money has a time value. NPV takes the stream of future savings, discounts each year back to today's value, subtracts the cost, and gives you a single number in today's money. It is the most complete of the four and the one a CFO trusts most for a multi-year commitment, though for a first proof of concept it is usually more precision than the situation warrants.

**Rough but honest beats spuriously precise.** For a first PoC decision, you do not need NPV computed to the rupee across five years. You need numbers that are conservative, clearly labelled as estimates, and directionally right. A payback of "under four months" carries more credibility than "3.7 months," because the false precision of "3.7" invites a fight about the third significant figure that you cannot win and do not need to. State the assumption behind each number, keep the estimates conservative so the real result is likely to be better than the case, and let the size of the margin (a saving many times the cost) carry the decision. The goal is a case that is hard to argue with, not a spreadsheet that pretends to certainty it does not have.

**The two pitfalls to guard against.** First, **ignoring the run cost**: a case that counts only the build makes the payback look better than it is and sets up an unpleasant surprise when the ongoing bill arrives. Always put the first-year run into the TCO. Second, **overstating deflection**: it is tempting to assume the bot handles every repetitive ticket. It will not. Assume a deflection rate you would be comfortable defending on the low side, so that reality beats the case rather than missing it.

**Worked example: the Sunrise business case.** Start from the ground truth in the brief and build up conservatively.

| Line | Estimate | How it is derived |
| --- | --- | --- |
| Tickets per week | about 4,000 | from Discover |
| Repetitive, in-scope tickets | about 2,400 per week | 60 percent of 4,000 |
| Conservatively deflected | about 1,200 per week | roughly half of the repetitive set, deliberately cautious |
| Cost per contact saved | roughly Rs 120 | fully loaded cost per handled ticket |
| **Run-rate saving** | **about Rs 75 lakh per year** | 1,200 x 52 weeks x Rs 120 = about Rs 74.9 lakh |
| Build and first-year run (TCO) | roughly Rs 25 lakh | build cost plus the first year of running it |
| **Payback period** | **under four months** | Rs 25 lakh TCO against about Rs 6.25 lakh saved per month |

Read the two computations that matter. The run-rate saving is the deflected volume times the annual weeks times the cost per contact: about 1,200 tickets a week, over 52 weeks, at Rs 120 each, which is about Rs 75 lakh a year. Note how conservative this is: it starts from only half the repetitive tickets, and the repetitive tickets are only 60 percent of the total. The payback compares the roughly Rs 25 lakh total cost of ownership against a saving of about Rs 6.25 lakh every month, which repays the whole investment in under four months. That is the number that replaces "support is expensive" with something Vikram can put in front of a board without flinching, and it holds even if the real deflection rate lands somewhat below the assumption.

### Tool: The value-driver tree

A **value-driver tree** connects the thing you build to the financial number the business cares about, one link at a time, so that the value becomes traceable rather than asserted. At the root of the tree sits the financial outcome (the money). Branching down from it are the operational metrics that drive that outcome. At the leaf sits your solution. The point of drawing it is that **each link is a separate claim you can check**, so the whole chain from "we built a bot" to "the business made or saved money" becomes auditable instead of hand-waved.

**When to use it.** Reach for the value-driver tree whenever someone might reasonably ask "how, exactly, does this thing turn into money?" and you need an answer that survives follow-up questions. It is the tool that stands up to a CFO who does not accept "it saves money" and wants to see the mechanism. It is equally useful in the other direction: if you cannot draw a clean chain from your solution to a financial number, that is a warning that the value may not be there, and you have found it before you built rather than after.

**The pitfall to avoid: unverifiable links.** A value-driver tree is only as strong as its weakest arrow. The failure mode is a chain that looks tidy on a slide but contains a link nobody can measure, for example "better answers lead to happier customers lead to more revenue," where the middle step is real but unquantifiable in the timeframe. A link you cannot measure is a place where value can be silently inflated or quietly evaporate. The remedy is to insist that every arrow correspond to a metric someone actually owns and can report. If a link has no owner and no number, either find the number or do not lean the case on that link.

**Worked example: the Sunrise value-driver tree.** Trace the chain from the solution at the leaf to the money at the root:

**Deflection bot → tickets deflected → agent hours freed → cost to serve down → support margin up**

Now check each arrow, which is the whole discipline of the tool:

- **Deflection bot → tickets deflected.** Measurable directly. The bot's own deflection rate (how many conversations it resolves without opening a ticket) is a number the system reports.
- **Tickets deflected → agent hours freed.** Measurable from staffing data. Fewer tickets at a known average handle time converts cleanly into hours of agent time no longer spent on routine questions.
- **Agent hours freed → cost to serve down.** Measurable from the cost per contact. Freed hours at a known loaded cost is a rupee figure, the same Rs 120 per contact used in the business case.
- **Cost to serve down → support margin up.** Measurable from finance. Lower cost to serve on the same or better service level lifts the margin of the support operation.

Because every arrow maps to a metric that a real function already owns (the bot for deflection, workforce planning for hours, finance for cost and margin), the value is auditable end to end. The **deflection rate is the driving lever**: every additional point of deflection propagates down the whole chain into freed hours, lower cost to serve, and higher margin. When a CFO asks how grounded answers to common questions become support margin, you do not answer with a claim. You walk the tree, and each link is a number someone can pull.

### The call: place it, and decide

The tools have done their work. Now you make the call, and a call has three parts: score the gates, place the candidate against its alternatives, and write the memo.

**Score the four gates, with numbers.** The gates are the standing checklist for an AI use case, and you rate each honestly rather than optimistically:

| Gate | Rating | Reason |
| --- | --- | --- |
| **Feasibility** | Green | Standard grounding shape, buildable by quarter-end |
| **Data readiness** | Amber | Help content and resolved tickets are usable; tribal knowledge in agents' heads is a gap |
| **ROI** | Green | About half of 4,000 weekly tickets are deflectable; payback under four months |
| **Risk** | Green, with guardrails | Bounded and low-harm, with human escalation on anything out of scope or uncertain |

Three greens and a managed amber. The amber on data readiness is exactly why the scope is bounded to what the content can support, and it is the source of one of the no-conditions below.

**Place it on the feasibility-by-value grid.** A go is relative, not absolute: it only means "do this instead of the alternatives." Plot the candidates on two axes, feasibility across and value up:

- **Support deflection sits top-right: high value, high feasibility.** This is the "do it now" quadrant. High value from the run-rate saving, high feasibility from the standard grounding shape and existing content.
- **Upsell sits high value, low feasibility (top-left).** There may be revenue in it eventually, but it is not buildable well this quarter: weak desirability, no clear success measure, and real risk to trust in the answers.
- **Content generation sits low value (bottom).** Different problem, different owner, brand risk, and it does not move the volume that matters.

The grid makes the sequencing visible and defensible. Deflection is not chosen because it was someone's favourite; it is chosen because it is the one candidate in the top-right, and the alternatives are somewhere you would not start.

**Write the qualification memo.** This is the artifact the move produces, and it is deliberately short, because a decision a board can act on fits on a page:

> **Qualification memo: Sunrise support deflection**
>
> **Decision: GO**, scoped to order, return, and simple-warranty questions, answered from Sunrise's own help content, with escalation to a human for anything out of scope or uncertain.
>
> **Evidence:** 60 percent of 4,000 weekly tickets are in scope; the help content exists and is usable; payback is under four months on a conservative deflection rate; DVF is green on all three lenses.
>
> **Assumptions:** the help content is usable as grounding; Legal permits simple-warranty answers.
>
> **We would say NO if:** the content proved unusable in practice, or Legal forbade warranty answers.

Every part of the memo is load-bearing. The **decision** is scoped, not open-ended, so no one can quietly expand it back into the six-agenda wish list. The **evidence** is numbers and facts, not adjectives. The **assumptions** state what the go rests on, so if one turns out false, everyone knows the decision has to be revisited. The **no-conditions** name precisely what would flip the call, which is what makes a skeptical VP trust the yes: a go that admits its own failure conditions reads as analysis, not advocacy. This GO memo is the output of the Frame stage and the input to the Prototype stage, where you choose the model, make its output reliable, and ground it in Sunrise's own content.

### Why qualification matters

A "yes" you cannot defend is a liability, not a decision, and enthusiasm has never survived contact with a board. Qualification is where the FDE is willing to say no, and where a yes is built out of evidence and named conditions rather than optimism. Skip it, and you start building on hope, then discover the one risk that kills the project (unusable data, a legal block) only after the budget is gone. Run it, and you either walk into the build with a case that holds, or you save the quarter by declining the build that would have failed. Either way you are ahead, because **the cheapest solution is the one you correctly decided not to build**.

---

## Business value: the numbers a board trusts

An FDE has to speak two languages. Inside the build, you talk in tokens, latency, and grounding.
Facing the customer, you talk in the numbers the business already runs on. A board does not fund "AI
for support." It funds a number it can defend. Qualification (Move 4) introduced the financial
instruments: ROI, payback, TCO, NPV, and the value-driver tree. This section names the operational
and experience metrics that sit underneath them, so you can translate a technical result into a
business one.

**Operational metrics** describe how the support function performs:

- **Deflection rate** (or **containment rate**): the share of contacts resolved without a human. This
  is the lever the deflection PoC pulls directly.
- **Average handle time (AHT)**: the average time an agent spends per contact. Deflecting the easy
  questions raises the average difficulty but frees hours overall.
- **First-contact resolution (FCR)**: the share of issues resolved on the first contact. Grounded,
  instant answers push this up.
- **Cost per contact** (or **cost to serve**): the fully loaded cost of handling one contact. Every
  deflected contact is a cost avoided.

**Experience metrics** describe how it feels to the customer:

- **CSAT**: customer satisfaction, usually a post-interaction rating.
- **NPS**: net promoter score, the willingness to recommend.
- **CES**: customer effort score, how hard the customer had to work to get an answer.

The link between the two is the whole argument. Recall the value-driver tree from Qualify: a
deflection bot deflects tickets, which frees agent hours, which lowers cost to serve, which lifts
support margin. Each arrow is a metric you can measure, so the value is auditable from the model
output all the way to the board's number. For Sunrise, the one calculation that lands is this: about
60 percent of 4,000 weekly tickets are in scope; even a conservative deflection rate times the cost
per contact gives a run-rate saving near Rs 75 lakh a year, which sets the payback against a build
and run cost of about Rs 25 lakh at under four months. That number, not the demo, turns a skeptical
yes into a funded one.

**Common trap.** Do not present an experience metric like CSAT as if it were the project. CSAT is an
outcome you influence, not a thing you build. Frame the buildable problem (deflection), then track
CSAT as one of its success measures. This is exactly how Sunrise's "lift our CSAT" ask was reframed
in Triage.

## Brownfield: when it is not greenfield

Sunrise is greenfield, so you chose freely. Most real engagements are not. On a brownfield account,
the same four moves run, but "how it fits what already exists" stops being a footnote and becomes an
input to every decision. Keep the habit even on a clean account, so it is there when the next one is
not.

- **Triage.** Integration effort becomes part of a wish's cost, so a wish that looked cheap can drop
  down the ranking.
- **Frame.** An existing tool constrains the options. If Sunrise already ran a chatbot, "assist"
  (help the agent) might beat "deflect" (replace the ticket), because ripping out a live system is
  expensive and political.
- **Discover.** Half the discovery brief becomes the systems you must live with: the legacy support
  tool, the data warehouse of uneven quality, the change-approval process.
- **Qualify.** A build that is green on its own merits can flip to no-go on integration risk alone.

The rule: on brownfield, always ask the question the greenfield account lets you skip, "what already
exists here, and what does it cost me to work with or around it."

## The delivery framework you started

The four artifacts you produced are not one-offs. They are the first templates of an **FDE delivery
framework**, the playbook you reuse on every account:

1. A **problem-selection note** (from Triage): the scored asks, the one chosen problem, and the
   reasoning.
2. A **problem statement with options** (from Frame): the tool-free statement and the distinct ways
   to solve it.
3. A **discovery brief** (from Discover): the real need, the data and its state, the systems, the
   constraints, the stakeholders, and the narrowed scope.
4. A **qualification memo** (from Qualify): the go or no-go, the evidence, the assumptions, and the
   exact no-conditions that would flip it.

Together these four are the Frame stage of an engagement. Every later session adds a stage and a
template, until you hold a full delivery playbook you can carry into the real role.

## Recap

You drove a real engagement from a wish list to a defended decision, and you never started with
theory. You used four moves, each with the same ITTO shape and its own tools:

- **Triage** cut six competing priorities down to one problem worth building, using Pareto, RICE and
  ICE, and MoSCoW.
- **Frame** turned that problem into a sharp, tool-free statement and three real options, using
  Jobs-to-be-Done, How Might We, and the 5 Whys.
- **Discover** replaced the guesses in those options with facts, using the Power-Interest grid, RACI,
  and the customer-journey map.
- **Qualify** turned the grounded picture into a defensible go, using DVF, the business case, and the
  value-driver tree.

Two ideas run through all of it. First, the FDE owns the outcome, not the wish list: focus is the
first act of value, and adoption, not delivery, is the finish line. Second, everything you decide has
to be defensible in the language a board funds in, which is why the humble numbers matter as much as
the clever model.

## Live lab

The live lab is where you stop watching and start driving. In Week 1 you pick a vertical (banking,
healthcare, retail, manufacturing, logistics, insurance, the public sector, or your own client
context, set in Bharat) and receive a wish list of the same messy shape. You run the same four moves
on your account, one per session, and produce the same four artifacts. By the end of this session you
have the Frame stage of your Capstone L1, done for real. The wish list changes with the domain; the
way you drive it does not.
