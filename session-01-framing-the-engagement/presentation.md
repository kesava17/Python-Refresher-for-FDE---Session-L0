---
marp: true
size: 16:9
paginate: true
title: Framing the Engagement
author: GuildTrek
---
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
  --ink: #0F172A;
  --ink-soft: #334155;
  --primary: #4F46E5;
  --primary-600: #4338CA;
  --neon: #10B981;
  --neon-600: #059669;
  --accent: #F59E0B;
  --muted: #64748B;
  --bg: #F8FAFC;
  --panel: #FFFFFF;
  --panel-cool: #EEF2FF;
  --border: #E2E8F0;
}

section {
  font-family: 'Inter', "Segoe UI", system-ui, sans-serif;
  font-size: 21px;
  color: var(--ink);
  background: var(--bg);
  padding: 46px 60px;
  line-height: 1.4;
}

h1, h2, h3, .big { font-family: 'Space Grotesk', 'Inter', sans-serif; letter-spacing: -0.02em; }
h1 { font-size: 42px; color: var(--ink); margin: 0 0 10px; font-weight: 600; }
h2 {
  font-size: 30px; color: var(--ink); margin: 0 0 14px; font-weight: 600; display: inline-block;
  padding-bottom: 8px; border-bottom: 3px solid transparent;
  border-image: linear-gradient(90deg, var(--primary), var(--neon)) 1;
}
h3 { font-size: 19px; color: var(--primary-600); margin: 0 0 6px; font-weight: 600; }
strong { color: var(--ink); }
a { color: var(--primary-600); }
ul, ol { margin: 4px 0; padding-left: 22px; }
li { margin: 4px 0; }
li::marker { color: var(--neon-600); }
em { color: var(--muted); font-style: italic; }

table { border-collapse: collapse; width: 100%; font-size: 15px; margin-top: 4px; }
th { background: var(--ink); color: #EEF2FF; text-align: left; padding: 6px 11px; font-weight: 600; }
td { border-bottom: 1px solid var(--border); padding: 6px 11px; vertical-align: top; }
tr:nth-child(even) td { background: var(--panel-cool); }

blockquote {
  border: none; border-left: 5px solid var(--neon); background: var(--panel-cool);
  padding: 12px 17px; color: var(--ink-soft); font-size: 18px; border-radius: 6px; margin: 10px 0;
}

section::after { color: #A9B2C4; font-size: 14px; font-weight: 600; }

.kicker {
  font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.22em;
  font-size: 15px; text-transform: uppercase;
  background: linear-gradient(100deg, var(--primary), var(--neon)); -webkit-background-clip: text;
  background-clip: text; color: transparent;
}
.grad {
  background: linear-gradient(100deg, var(--neon), var(--primary) 70%); -webkit-background-clip: text;
  background-clip: text; color: transparent;
}
.muted { color: var(--muted); }
.big { font-size: 44px; line-height: 1.08; margin: 12px 0; font-weight: 600; }

.columns { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.columns3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
.card {
  background: var(--panel); border: 1px solid var(--border); border-left: 5px solid var(--primary);
  border-radius: 8px; padding: 12px 16px;
}
.card.neon { border-left-color: var(--neon); }
.card.amber { border-left-color: var(--accent); }
.card.brownfield { border-left-color: #B45309; }
.card h3 { margin-top: 0; }
.card p { margin: 5px 0 0; }
.card ul { margin: 4px 0 0; }

.pill { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--primary-600); background: var(--panel-cool); border: 1px solid var(--border); border-radius: 999px; padding: 3px 12px; margin-bottom: 8px; }
.pill.field { color: var(--neon-600); }
.pill.brown { color: #B45309; background: #FFFBEB; }

.flow { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin: 12px 0; }
.flow .step { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 7px 13px; font-weight: 600; font-size: 15px; color: var(--ink); }
.flow .step.hot { border-color: var(--neon); color: var(--neon-600); }
.flow .arrow { color: var(--primary); font-weight: 800; font-size: 18px; }

.chips { display: flex; flex-wrap: wrap; gap: 7px; margin: 10px 0; align-items: center; }
.chip { background: var(--panel-cool); border: 1px solid var(--border); color: var(--ink-soft); border-radius: 999px; padding: 6px 12px; font-weight: 600; font-size: 14px; }
.chip.hot { background: linear-gradient(100deg, rgba(79,70,229,.12), rgba(16,185,129,.12)); border-color: rgba(79,70,229,.35); color: var(--primary-600); }
.tag { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-right: 2px; }

.proof { border: none; border-left: 5px solid var(--accent); background: #FFFBEB; padding: 9px 15px; border-radius: 6px; font-size: 17px; color: var(--ink-soft); margin-top: 10px; }
.proof b { color: #B45309; font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; display: inline-block; margin-right: 6px; }

.drive { border: none; border-left: 5px solid var(--neon); background: var(--panel-cool); padding: 9px 15px; border-radius: 6px; font-size: 17px; color: var(--ink-soft); margin-top: 10px; }
.drive b { color: var(--neon-600); font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; display: inline-block; margin-right: 6px; }

.note { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; font-size: 17px; color: var(--ink-soft); }
.note .from { font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }

.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 16px; }
.stat { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 15px 10px; text-align: center; }
.stat b { display: block; font-family: 'Space Grotesk', sans-serif; font-size: 26px; line-height: 1; margin-bottom: 5px; background: linear-gradient(120deg, var(--neon), var(--primary)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.stat span { color: var(--muted); font-size: 13px; }

section.lead, section.divider, section.dark {
  background:
    radial-gradient(120% 120% at 85% 12%, rgba(79,70,229,0.30), transparent 46%),
    radial-gradient(120% 120% at 8% 92%, rgba(16,185,129,0.22), transparent 50%),
    linear-gradient(135deg, #0B1020 0%, #131A31 55%, #0A0E1A 100%);
  color: #E6EAF5;
}
section.lead h1, section.divider h1, section.dark h1,
section.lead h2, section.divider h2, section.dark h2 { color: #fff; border: none; padding: 0; }
section.divider h2, section.dark h2 { border-bottom: 3px solid transparent; border-image: linear-gradient(90deg, var(--primary), var(--neon)) 1; padding-bottom: 8px; display: inline-block; }
section.lead strong, section.divider strong, section.dark strong { color: #fff; }
section.lead .muted, section.divider .muted, section.dark .muted { color: #AEB6CC; }
section.lead::after, section.divider::after, section.dark::after { color: #6B7488; }
section.dark .card, section.divider .card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); }
section.dark .card h3, section.divider .card h3 { color: #C7D2FE; }
section.dark li { margin: 6px 0; }
section.dark li::marker { color: var(--neon); }
section.dark .note { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); color: #E6EAF5; }
section.dark .stat, section.divider .stat { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); }

.deck-logo { height: 50px; display: block; margin-bottom: 18px; }
.brandmark { position: absolute; top: 32px; right: 54px; height: 27px; opacity: .9; }
.brandlite { color: #A5B4FC; font-weight: 700; }
section.lead h3, section.divider h3, section.dark h3 { color: #C7D2FE; }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">AI for FDE &middot; Module 1 &middot; Session 1</span>

# Framing the Engagement

### <span class="muted">A working session, not a lecture.</span> <span class="brandlite">Today you are the Forward Deployed Engineer on the Sunrise Electronics account. A wish list just landed. You will drive it, all the way to a committed, defensible decision to build.</span>

<p class="muted" style="font-size: 22px; max-width: 54ch; margin-top: 14px;">We work the real moves first. At the end, we name what you learned.</p>

---

## The brief just landed

<div class="note">
<div class="from">from: Vikram Rao, VP Customer Experience, Sunrise Electronics</div>
"The board wants us to use AI on customer experience this year, and everyone here has an opinion. Let me dump it all:
<ul>
<li>My support team is drowning in the same questions all day (order status, returns, warranty), and the hard cases wait behind them.</li>
<li>Sales heard about this and wants the same assistant to upsell and cross-sell while it talks to customers.</li>
<li>Marketing (and the CEO, who saw a demo) want it on brand, and to generate our help content and campaigns too.</li>
<li>Our CSAT slipped last quarter and I am being asked to fix it, so whatever we build has to make customers happier.</li>
<li>IT says we have years of data so this should be easy, and it obviously has to work with our systems and be secure.</li>
<li>Budget is tight and I need something to show the board by end of quarter."</li>
</ul>
</div>

<div class="proof"><b>One direction, six agendas</b> This is not six projects. It is one initiative ("AI for customer experience") with every team bolting on its own priority, and nobody has done the value analysis. Vikram is senior, board-facing, and impatient. Untangling this is your job.</div>

---

## Your homework starts now

<span class="pill field">the FDE's real first job</span>

<p class="muted">This is not homework you assign the customer, and not a task anyone hands you. The moment a wish list like this lands, an FDE has homework to do, before a line of code.</p>

<div class="columns">
<div class="card amber"><h3>What just landed on you</h3><p>One vague direction with six teams' priorities bolted on, no owner, no value analysis, and a deadline. Take it at face value and you will try to build all of it, and land none of it.</p></div>
<div class="card neon"><h3>The homework, before building</h3><p>Read past the asks to the needs, separate the stakeholders and their agendas, weigh each on value, and reduce the noise to one problem you can defend. That homework is <strong>triage, frame, discover, qualify</strong>, and it is this whole session.</p></div>
</div>

<div class="proof"><b>Nobody will ask you to do this</b> The customer will not request it and it will not appear on a ticket. Doing it anyway, before you build, is exactly what separates an FDE from an order-taker.</div>

---

## Where we are going: the Frame framework

<p class="muted">Your homework is one framework, run in four moves. Each move is a small body of knowledge with its own inputs, process, tools, and outputs. We open each move with that map, then run it live. The output of one move is the input to the next.</p>

<div class="flow">
<span class="step hot">Wish list</span><span class="arrow">&rarr;</span>
<span class="step">Triage</span><span class="arrow">&rarr;</span>
<span class="step">Frame</span><span class="arrow">&rarr;</span>
<span class="step">Discover</span><span class="arrow">&rarr;</span>
<span class="step">Qualify</span><span class="arrow">&rarr;</span>
<span class="step hot">Committed GO</span>
</div>

<div class="columns">
<div class="card"><h3>What each move gives you</h3><p>A named <strong>input</strong>, a <strong>process</strong> to run, the <strong>tools</strong> that fit, and a concrete <strong>output</strong> you can hand on. That is the body-of-knowledge shape, the one PMBOK uses.</p></div>
<div class="card neon"><h3>How we teach each one</h3><p>Open with the map (what this move is, and its inputs, process, tools, outputs), run it live on Sunrise, then read the result back through the same four boxes.</p></div>
</div>

<div class="proof"><b>The rule for today</b> We do not start with pure theory. You name the shape of a move, then run it live, make the calls an FDE makes, and produce the real artifacts. Starting with Triage.</div>

---

## Move 1 &middot; Triage: what it is

<p class="muted">Triage is the systematic process of prioritizing incoming items by urgency, severity, and the resources you have. It began in military medicine in World War I: treat the high-impact cases now, and defer, delegate, or drop the rest.</p>

<span class="pill">the three-bucket model</span>

<div class="columns3">
<div class="card amber"><h3>Critical / urgent</h3><p>Immediate action. Needs resources now.</p></div>
<div class="card"><h3>Non-critical</h3><p>Deferred or queued. Low risk in waiting.</p></div>
<div class="card"><h3>Unserviceable</h3><p>Rejected or dropped. Not worth the resources.</p></div>
</div>

<div class="proof"><b>Route, do not resolve</b> Triage sorts every incoming demand into one of these three. It decides what gets attention, not how to fix it.</div>

---

## The same move, in every field

<p class="muted">You already know triage. It runs the emergency room, the incident bridge, and the product backlog.</p>

| Domain | What is triaged | Objective | Example |
| --- | --- | --- | --- |
| **Emergency medicine** | patients arriving at the ED | stabilize the critical first | trauma treated now; a minor fracture waits |
| **Incident response (SRE)** | alerts, outages, bugs | contain blast radius, cut downtime | fix a DB pool crash before a UI alignment bug |
| **Product and support** | tickets, bugs, requests | throughput and stability | P0 auth down; P2 missing export icon |
| **Project management** | tasks, emails, backlog | protect focus, hit deadlines | Eisenhower: urgent vs important |

<div class="proof"><b>Different stakes, one discipline</b> The domain changes; the move does not. As an FDE you are running the product-and-support row, on an AI wish list.</div>

---

## Principles of effective triage

<div class="columns3">
<div class="card"><h3>Speed and decisiveness</h3><p>Assess quickly and route. The goal is to place the problem, not to solve it on the spot.</p></div>
<div class="card neon"><h3>Dynamic re-evaluation</h3><p>Priorities shift. A low-urgency item turns critical when context changes, so you revisit.</p></div>
<div class="card amber"><h3>Resource awareness</h3><p>Priority depends on constraints: the engineers, doctors, or compute and budget you actually have.</p></div>
</div>

<div class="proof"><b>Why it fits the FDE</b> A vague, over-wished brief on a tight budget is exactly a triage problem: many demands, real constraints, one quarter.</div>

---

## Triage as a body of knowledge (ITTO)

<p class="muted">Now the shape of the move, in the abstract. Every stage today has these four boxes, the ones PMBOK uses: inputs, a process, the tools you apply, and the outputs it produces.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| Incoming demands (requests, tickets, asks) with their urgency and severity signals, plus the resources and constraints you have | Assess each item fast; score it; sort into critical, non-critical, unserviceable; re-evaluate as context shifts | Pareto (80/20), weighted scoring (RICE or ICE), MoSCoW, the Eisenhower matrix | A ranked, scored priority list: the critical few to act on now, and an explicit deferred or dropped set |

<div class="proof"><b>Read it left to right</b> Inputs come in, the process acts on them with the tools, and the outputs come out. First, meet the tools in that box.</div>

---

## Tool 1 &middot; Pareto: the vital few

<p class="muted">The Pareto principle, the 80/20 rule: roughly 80 percent of the effect comes from 20 percent of the causes. In prioritization, a small share of items carries most of the impact.</p>

<div class="columns">
<div class="card"><h3>The idea</h3><p>Rank items by volume or impact. A short head accounts for most of the total; a long tail accounts for little. Spend your resources on the head.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Cutting through a long list fast. It answers one question: where is the concentration, and so where should attention go first.</p></div>
</div>

<div class="proof"><b>Everyday Pareto</b> A fifth of customers drive most of the revenue; a fifth of bugs cause most of the crashes. Find that fifth before you do anything else.</div>

---

## Pareto on Sunrise's tickets

<p class="muted">Break the 4,000 weekly tickets down by question type, highest volume first.</p>

| Question type | Share of tickets | In the vital few? |
| --- | --- | --- |
| Where is my order | about 30 percent | yes |
| How do I return this | about 18 percent | yes |
| Is it under warranty (simple) | about 12 percent | yes |
| Everything else (long tail) | about 40 percent | no, many rare types |

<div class="drive"><b>What Pareto solves here</b> Three question types are about 60 percent of all tickets. Deflect those and you move most of the volume. It also tells you not to chase the long tail of rare questions, where the effort is high and the payoff small.</div>

---

## Tool 2 &middot; RICE and ICE: score, do not argue

<p class="muted">A weighted scoring model that turns opinions into comparable numbers, so the ranking is defensible in a room of competing priorities.</p>

<div class="columns">
<div class="card"><h3>RICE</h3><p>Score = (<strong>Reach</strong> times <strong>Impact</strong> times <strong>Confidence</strong>) divided by <strong>Effort</strong>. Reach: how many are affected. Impact: how much. Confidence: how sure you are. Effort: what it costs to build.</p></div>
<div class="card neon"><h3>ICE</h3><p>The lighter version: <strong>Impact</strong> times <strong>Confidence</strong> times <strong>Ease</strong>. Faster to run when you have less data, and good enough for a first cut.</p></div>
</div>

<div class="proof"><b>Why score</b> A number you can show beats "I feel this is important." It makes the ranking survive the stakeholders who each brought a different priority.</div>

---

## RICE on Sunrise's asks

<p class="muted">Score the candidate asks on a 1 to 5 scale. Higher is better, except Effort, which divides.</p>

| Ask | Reach | Impact | Confidence | Effort | Score |
| --- | --- | --- | --- | --- | --- |
| **Support deflection** | 5 | 4 | 4 | 2 | **40** |
| Upsell bot | 4 | 3 | 2 | 4 | 6 |
| Marketing content | 3 | 2 | 2 | 3 | 4 |

<div class="drive"><b>What RICE solves here</b> Support deflection scores an order of magnitude higher: wide reach, real impact, high confidence (the answers already exist), and low effort. The numbers separate the one worth building from the wishes, on evidence Vikram can read.</div>

---

## Tool 3 &middot; MoSCoW: draw the line on scope

<p class="muted">Sort every item into four buckets, agreed with the stakeholders, so scope is explicit and expectations are set.</p>

<div class="columns">
<div class="card amber"><h3>Must and Should</h3><p><strong>Must have:</strong> the release fails without it. <strong>Should have:</strong> important, but the release survives a short delay.</p></div>
<div class="card"><h3>Could and Won't</h3><p><strong>Could have:</strong> nice if time allows. <strong>Won't have this time:</strong> explicitly out of scope, and named, so it does not creep back in.</p></div>
</div>

<div class="proof"><b>The power is in the Won't</b> Saying out loud what you will not do this quarter is how you protect the scope from six stakeholders each pushing their own item.</div>

---

## MoSCoW on Sunrise's scope

<div class="columns">
<div class="card neon"><h3>Must have</h3><p>Deflect order, return, and simple-warranty questions with grounded answers.</p></div>
<div class="card"><h3>Should have</h3><p>Clean escalation to a human for anything out of scope or uncertain.</p></div>
</div>

<div class="columns">
<div class="card"><h3>Could have</h3><p>Track CSAT on deflected chats; add more question types later.</p></div>
<div class="card amber"><h3>Won't have this quarter</h3><p>Upsell in the bot, and generated help content or campaigns.</p></div>
</div>

<div class="drive"><b>What MoSCoW solves here</b> It turns the six competing asks into an agreed scope. Sales, Marketing, and the CEO see their items in Could or Won't, with a reason, not a flat rejection, and Vikram gets a shippable quarter.</div>

---

## The call: one problem, defended

<p class="muted">You did not run the tools to please every team. You ran them to make one pick you can defend, and all three converge on the same answer.</p>

<div class="columns">
<div class="card neon"><h3>The pick</h3><p>Support deflection: order, return, and simple-warranty questions. Pareto put the volume here, RICE scored it far above the rest, and MoSCoW made it the Must.</p></div>
<div class="card amber"><h3>Deferred, with reasons</h3><p>Upsell and generated marketing content go to Could or Won't this quarter, and CSAT becomes a metric, not a project. Nothing is rejected; it is sequenced, so each stakeholder sees why.</p></div>
</div>

<div class="drive"><b>Then the feasibility gate</b> Is it even an AI problem, is the data there, and what is the risk? Yes: the answers live in documents, the help center and past tickets exist, and a wrong "where is my order" is low harm. It passes.</div>

---

## Triage on Sunrise, walked through ITTO

<p class="muted">The same four boxes, now filled with the real engagement. This is what you just produced, read back through the framework.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| Vikram's six competing asks; about 4,000 tickets a week, roughly 60 percent repetitive; a tight budget and a quarter-end deadline | Scored the asks with Pareto, RICE, and MoSCoW; sorted into pick, defer, drop; ran the feasibility gate on the survivor | Pareto (the repetitive 60 percent are the vital few), RICE scoring, MoSCoW across the six asks | A scored list with one clear winner: support deflection is the problem worth the quarter; the rest deferred or dropped, with reasons |

<div class="drive"><b>Output becomes the next input</b> Triage's output, one chosen problem, is the input to Frame. That is how the four moves chain into one framework.</div>

---

## Why we triage

<p class="muted">Because you cannot build six stakeholders' priorities at once, and building the wrong thing well is still a failure.</p>

<div class="columns">
<div class="card neon"><h3>What triage buys you</h3><p>One problem worth solving, chosen on evidence, separated from the politics piled onto it, that you can defend to a VP asking hard questions.</p></div>
<div class="card amber"><h3>Skip it, and</h3><p>You try to satisfy every team at once, spread thin, burn the quarter and the budget, and the customer's real problem is still there.</p></div>
</div>

<div class="proof"><b>The point</b> Focus is the FDE's first act of value. Choosing well, early, is worth more than building fast.</div>

---

## Vikram pushes: "Great, so build the support bot"

<p class="muted">You have a chosen problem. You do not yet have a solution shape. "A support bot" is a tool, picked before anyone decided what it should do. Nodding here is the classic mistake.</p>

<div class="columns">
<div class="card amber"><h3>Jump to the tool</h3><p>Build a chatbot because that is the word everyone used. It fits the tool, not the customer, and it will demo but not land.</p></div>
<div class="card neon"><h3>Hold, and frame</h3><p>Push back gently: "before we build, let me make sure we solve the right thing." Then frame the problem and put real options on the table.</p></div>
</div>

<div class="drive"><b>Move 2 &middot; Frame</b> Before you accept a tool, you frame the problem: understand it, find the root, write it tool-free, and put real options on the table. Here is what framing is, and the tools that do it.</div>

---

## Move 2 &middot; Frame: what it is

<p class="muted">Framing turns a vague ask into a sharp, tool-free problem statement and a set of genuinely different options. It is the define-and-ideate heart of design thinking: understand the user, state the problem, generate options.</p>

<div class="columns">
<div class="card"><h3>Problem, not solution</h3><p>A frame names the outcome to reach and the person it is for. It never names a tool. "Build a chatbot" is a solution wearing a problem's clothes.</p></div>
<div class="card neon"><h3>Options, not one idea</h3><p>Good framing ends with two or three distinct ways to solve the problem, so the later choice is real, not a rubber stamp on the first idea.</p></div>
</div>

<div class="proof"><b>The move in one line</b> Understand, define the problem, then diverge into options. You leave with a statement and a short menu, not a build order.</div>

---

## The same trap, in every field

<p class="muted">Jumping to a solution before framing the problem is universal. Naming the trap is why framing exists.</p>

| Field | The solution-first trap | The framed question |
| --- | --- | --- |
| **Medicine** | treat the symptom that presents | what is the underlying condition |
| **Engineering** | build the feature that was requested | what job is the user trying to do |
| **Consulting** | answer the question as asked | what decision does the client actually face |
| **AI projects** | build the bot everyone named | what problem must it solve, and how else could we |

<div class="proof"><b>Why FDEs get trapped</b> AI makes it trivial to build the named thing fast. Speed to the wrong build is the modern version of the oldest mistake.</div>

---

## Principles of effective framing

<div class="columns3">
<div class="card"><h3>Problem from solution</h3><p>State the outcome and the user. If a tool name appears, you are solutioning, not framing.</p></div>
<div class="card neon"><h3>Ground it in observation</h3><p>Frame from what you saw, not what was reported. Watch the work before you word the problem.</p></div>
<div class="card amber"><h3>Diverge, then converge</h3><p>Generate distinct options first. Narrowing too early hides the option that would have won.</p></div>
</div>

<div class="proof"><b>The test of a good frame</b> The stakeholder reads it and says "yes, exactly," and it contains no tool. If it names a tool, reframe.</div>

---

## Frame as a body of knowledge (ITTO)

<p class="muted">The same four boxes as before, now for framing.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The one problem from triage; observation of the real work; the customer's words and stated ask | Understand the user and the job; find the root cause; write one sharp, tool-free problem statement; diverge into options | Jobs-to-be-Done, How Might We, 5 Whys | A problem statement the stakeholder agrees with, and two or three genuinely different options |

<div class="proof"><b>Read it left to right</b> The chosen problem comes in; understanding, root cause, and divergence act on it; a framed statement with real options comes out. First, the tools.</div>

---

## Tool 1 &middot; Jobs-to-be-Done

<p class="muted">People do not want a product; they hire it to get a job done. Frame the job, not the feature, and the real problem appears.</p>

<div class="columns">
<div class="card"><h3>The shape</h3><p>"When <em>[situation]</em>, I want to <em>[motivation]</em>, so I can <em>[outcome]</em>." The job stays stable even when the tools change.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Stripping a request down to the outcome the user is really after, so you do not build features nobody hired.</p></div>
</div>

<div class="proof"><b>Classic line</b> People do not want a quarter-inch drill; they want a quarter-inch hole. Find the hole.</div>

---

## Jobs-to-be-Done on Sunrise

<p class="muted">Write the jobs behind the support ask, for both the customer and the agent.</p>

<div class="columns">
<div class="card neon"><h3>The customer's job</h3><p>"When I have a question about my order, return, or warranty, I want a correct answer immediately, so I can stop worrying and not wait in a queue."</p></div>
<div class="card"><h3>The agent's job</h3><p>"When routine questions flood in, I want them handled without me, so I can spend my time on the cases that actually need a person."</p></div>
</div>

<div class="drive"><b>What JTBD solves here</b> Neither job is "a chatbot." Both are "an instant, correct answer to a common question." That reframes "build a support bot" into a problem about self-serve answers, which opens real options.</div>

---

## Tool 2 &middot; How Might We

<p class="muted">Turn the problem into an open question that invites solutions, pitched at the right altitude: not so broad it is useless, not so narrow it hides a single answer.</p>

<div class="columns">
<div class="card"><h3>The shape</h3><p>"How might we <em>[achieve the outcome]</em> for <em>[the user]</em>?" Optimistic, open, and free of any named tool.</p></div>
<div class="card neon"><h3>Altitude matters</h3><p>Too broad ("how might we fix support") gives nothing. Too narrow ("how might we add a chatbot") smuggles in the answer. Aim in between.</p></div>
</div>

<div class="proof"><b>Why it works</b> A good "how might we" makes people generate options instead of defending one. It is the doorway from problem to ideas.</div>

---

## How Might We on Sunrise

<p class="muted">Phrase the framed job as an invitation, then watch the options fall out.</p>

<div class="note">
<div class="from">the framed question</div>
"How might we give Sunrise's customers an instant, correct answer to their most common questions, without tying up an agent?"
</div>

<div class="drive"><b>What How Might We solves here</b> That one question invites three distinct answers: <strong>deflect</strong> (self-serve answers), <strong>route</strong> (send the ticket to the right queue), and <strong>assist</strong> (draft a reply the agent sends). The problem now has a real menu, not a foregone bot.</div>

---

## Tool 3 &middot; 5 Whys

<p class="muted">Ask "why" repeatedly, each answer feeding the next question, until you pass the symptom and reach a cause you can actually act on.</p>

<div class="columns">
<div class="card"><h3>The shape</h3><p>Start from the stated problem and ask why about five times. The number is a guide, not a rule; stop when you hit a root you can change.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Making sure you frame the cause, not the symptom, so the solution addresses what actually generates the pain.</p></div>
</div>

<div class="proof"><b>Watch for the wall</b> When "why" stops giving a changeable answer and starts giving "that is just how it is," you have found the root worth framing.</div>

---

## 5 Whys on Sunrise

<p class="muted">Start from Vikram's words and dig.</p>

<div class="card"><ul>
<li><strong>Support is drowning.</strong> Why? Agents answer the same questions all day.</li>
<li>Why do those reach an agent? There is no way for a customer to self-serve the answer.</li>
<li>Why can they not self-serve? The answers exist, but only inside help pages and past tickets no one searches well.</li>
<li>Why is that not enough? The content is not written as answers to real questions, and it is not instant.</li>
<li><strong>Root:</strong> customers cannot get an instant, correct answer to a common question from content Sunrise already owns.</li>
</ul></div>

<div class="drive"><b>What 5 Whys solves here</b> The problem is not "too few agents" or "no chatbot." It is unreachable answers, and that root is exactly what a deflection option addresses. It confirms the frame.</div>

---

## The call: a sharp problem and three options

<p class="muted">The tools converge on one statement and a real menu. This is what you hand forward.</p>

<div class="note">
<div class="from">the problem statement</div>
"Support agents spend most of their day answering the same order, return, and warranty questions, which delays the complex cases that need a person. How might we give customers instant, correct answers to those questions from Sunrise's own content?"
</div>

<div class="columns3">
<div class="card neon"><h3>Deflect</h3><p>Self-serve answerer: grounded answers, no ticket opened.<br><em>high value, data looks ready</em></p></div>
<div class="card"><h3>Route</h3><p>Classifier: tickets sorted to the right queue.<br><em>medium value, tickets to learn from</em></p></div>
<div class="card amber"><h3>Assist</h3><p>Agent copilot: drafts a reply a human approves.<br><em>medium value, needs adoption</em></p></div>
</div>

<div class="drive"><b>These reads are still guesses</b> The value and readiness notes are first impressions, not facts. You cannot commit on guesses, which is exactly why Discover comes next.</div>

---

## Frame on Sunrise, walked through ITTO

<p class="muted">The four boxes, filled with what you just produced.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The chosen problem (support deflection); an hour watching agents; Vikram's "build a support bot" | Wrote the customer and agent jobs; asked why to the root; phrased a how-might-we; diverged into options | Jobs-to-be-Done, How Might We, 5 Whys | A tool-free problem statement Vikram agrees with, and three distinct options: deflect, route, assist |

<div class="drive"><b>Output becomes the next input</b> The framed problem and its options are the input to Discover, where you replace the guesses with facts.</div>

---

## Why we frame

<p class="muted">Because "build a chatbot" is a tool, and if you accept the customer's tool you solve their guess, not their problem.</p>

<div class="columns">
<div class="card neon"><h3>What framing buys you</h3><p>A sharp problem and several real options, so the solution is a choice you can reason about, not the first word someone said.</p></div>
<div class="card amber"><h3>Skip it, and</h3><p>You build the first idea, it demos well, and it does not land, because it fit the tool instead of the customer.</p></div>
</div>

<div class="proof"><b>The point</b> The tool must serve the problem. Framing is how you keep it that way, especially when AI makes it easy to build the wrong thing quickly.</div>

---

## Move 3 &middot; Discover: what it is

<p class="muted">Discovery grounds the framed options in what is actually true, before you commit. You separate the stated ask from the real need, and map the stakeholders, data, systems, and constraints the solution will live inside.</p>

<div class="columns">
<div class="card"><h3>Ask is not need</h3><p>The customer's words are a starting point, not the truth. You go and look: real tickets, real systems, real people, real limits.</p></div>
<div class="card neon"><h3>Surface what would ambush you</h3><p>The veto you did not know about, the data messier than promised, the constraint nobody mentioned. Find them now, while you can still act.</p></div>
</div>

<div class="proof"><b>The move in one line</b> Replace the assumptions inside your options with facts, so the decision that follows rests on the ground, not on hope.</div>

---

## The same move, in every field

<p class="muted">Before a good decision, someone does the unglamorous work of finding out what is real.</p>

| Field | The discovery work | What it prevents |
| --- | --- | --- |
| **Medicine** | history, examination, tests | treating the wrong condition |
| **Journalism** | sourcing and verification | printing a false story |
| **Audit** | tracing records to evidence | signing off on a fiction |
| **Software** | requirements and user research | building the wrong system |

<div class="proof"><b>The FDE version</b> A week of listening before a quarter of building. The cost of discovery is always smaller than the cost of the wrong build.</div>

---

## Principles of effective discovery

<div class="columns3">
<div class="card"><h3>Go and see</h3><p>Observe the real work and the real data. Reported reality and actual reality are never quite the same.</p></div>
<div class="card neon"><h3>Follow the constraints</h3><p>Legal, residency, budget, and timeline shape what is buildable. A constraint found late is a project killed late.</p></div>
<div class="card amber"><h3>Find every veto</h3><p>Anyone who can say no is a stakeholder. Meet them before you commit, not after.</p></div>
</div>

<div class="proof"><b>The discipline</b> Discovery is listening with a purpose: not "tell me everything," but "what would make this fail, and who could stop it."</div>

---

## Discover as a body of knowledge (ITTO)

<p class="muted">The four boxes, now for discovery.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The framed problem and its options; access to people, tickets, systems, and documents | Separate ask from need; interview stakeholders; trace where data and answers live; map the journey; list constraints and vetoes | Power-Interest grid, RACI, customer-journey map | A discovery brief: the real need, the data and its state, the systems, the constraints, the stakeholders, and a narrowed scope |

<div class="proof"><b>Read it left to right</b> Framed options come in; observation and mapping act on them; a grounded brief comes out. First, the tools.</div>

---

## Tool 1 &middot; Power-Interest grid

<p class="muted">Also called Mendelow's matrix. Plot every stakeholder on two axes: how much power they have over the project, and how much interest they have in it.</p>

<div class="columns">
<div class="card"><h3>The four quadrants</h3><p><strong>High power, high interest:</strong> manage closely. <strong>High power, low interest:</strong> keep satisfied. <strong>Low power, high interest:</strong> keep informed. <strong>Low power, low interest:</strong> monitor.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Spending your attention where it changes the outcome, and never being surprised by who can block you.</p></div>
</div>

<div class="proof"><b>Why power and interest</b> A quiet stakeholder with a veto will sink you faster than a loud one with none. The grid tells them apart.</div>

---

## Power-Interest on Sunrise

<p class="muted">Place the people the deflection project touches.</p>

| Stakeholder | Power | Interest | How to handle |
| --- | --- | --- | --- |
| **Vikram (VP CX)** | high | high | manage closely: your sponsor and your skeptic |
| **Legal** | high (can veto warranty answers) | medium | keep satisfied: get scope signed early |
| **IT** | high (owns data and systems) | medium | keep satisfied: agree access and integration |
| **Support agents** | low (formal) | high (adoption) | keep informed and involve: they make or break it |

<div class="drive"><b>What the grid solves here</b> It surfaces Legal as a high-power, easy-to-miss veto on warranty answers, and flags that agents, with no formal power, decide adoption. Both change the scope and the plan.</div>

---

## Tool 2 &middot; RACI

<p class="muted">A simple grid that assigns four roles to each task or decision: who is Responsible (does the work), Accountable (owns the outcome, exactly one), Consulted (gives input), and Informed (kept in the loop).</p>

<div class="columns">
<div class="card"><h3>The rule</h3><p>Every task has exactly one <strong>Accountable</strong>. More than one, and no one owns it; none, and it falls through the cracks.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Killing the "I thought you had it" failures before they happen, and making handoffs explicit across teams.</p></div>
</div>

<div class="proof"><b>Why it matters for an FDE</b> You work across the customer's org. RACI is how you make sure a decision has an owner, not an audience.</div>

---

## RACI on Sunrise

<p class="muted">Assign roles for the deflection PoC, so nothing waits on "someone."</p>

| Task | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Approve warranty answer scope | Legal | Vikram | Support ops | CEO |
| Provide help content and tickets | IT | Vikram | Support ops | you |
| Build the deflection PoC | you (FDE) | Vikram | IT, agents | Legal |
| Sign off on go-live | Vikram | Vikram | Legal, IT | board |

<div class="drive"><b>What RACI solves here</b> It names Vikram as the single accountable owner, gets Legal consulted (not surprised) on scope, and turns the content handoff from IT into an explicit task with a date, not a hope.</div>

---

## Tool 3 &middot; Customer-journey map

<p class="muted">Lay out the steps a customer actually takes, end to end, with what they do, what they feel, and where it breaks. It shows exactly where a solution should sit.</p>

<div class="columns">
<div class="card"><h3>The shape</h3><p>Stages across the top; for each, the customer's action, their goal, and the pain point. The worst pains are your opportunities.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Placing the fix where the pain is, and seeing the moments a wrong answer would do real harm.</p></div>
</div>

<div class="proof"><b>Why map the journey</b> A solution that ignores the surrounding steps solves a slide, not a customer. The map keeps you honest about context.</div>

---

## Journey map on Sunrise

<p class="muted">Trace a customer with a "where is my order" question.</p>

| Stage | What the customer does | Pain today |
| --- | --- | --- |
| **Question arises** | checks email, then the website | no obvious self-serve answer |
| **Looks for help** | scans help pages, gives up | content is not written as answers |
| **Contacts support** | opens a ticket or waits on chat | queue behind the same common questions |
| **Waits** | checks back for a reply | slow, and the answer was simple |

<div class="drive"><b>What the map solves here</b> The break is at "looks for help": the answer exists but is unreachable. That is exactly where deflection sits, and it confirms the frame from the customer's side.</div>

---

## The call: the discovery brief

<p class="muted">The tools converge into one artifact: what is real, what is scoped, and what would still block you.</p>

<div class="note">
<div class="from">discovery brief &middot; Sunrise support deflection</div>
<strong>Real need:</strong> customers cannot get an instant, correct answer to common questions from content Sunrise already owns.<br>
<strong>Data:</strong> help center and resolved tickets are usable; tribal knowledge in agents' heads is a gap.<br>
<strong>Stakeholders:</strong> Vikram (sponsor), Legal (warranty veto), IT (data and systems), agents (adoption).<br>
<strong>Constraints:</strong> customer data stays in Bharat; Legal limits warranty answers to simple cases; quarter-end demo.<br>
<strong>Scope:</strong> order, return, and simple-warranty questions, grounded in Sunrise content, with escalation to a human.
</div>

<div class="drive"><b>The guesses are now facts</b> The option reads from Frame are grounded, and the scope is narrowed to what is real and permitted.</div>

---

## Discover on Sunrise, walked through ITTO

<p class="muted">The four boxes, filled with what you just produced.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The framed problem and three options; access to tickets, content, systems, and people | Separated ask from need; placed stakeholders; assigned roles; mapped the journey; listed constraints | Power-Interest grid, RACI, customer-journey map | A discovery brief: real need, data state, stakeholders and vetoes, constraints, and a narrowed scope |

<div class="drive"><b>Output becomes the next input</b> The discovery brief is the input to Qualify, where you turn a grounded picture into a defensible go or no-go.</div>

---

## Why we discover

<p class="muted">Because the ask is not the need, and the assumptions hiding in your options are exactly where projects die in month two.</p>

<div class="columns">
<div class="card neon"><h3>What discovery buys you</h3><p>Facts instead of guesses, and the constraints and stakeholders that would otherwise ambush you late, surfaced while you can still act on them.</p></div>
<div class="card amber"><h3>Skip it, and</h3><p>You commit on assumptions, then get vetoed by a stakeholder you never met, or blocked by a constraint you never checked.</p></div>
</div>

<div class="proof"><b>The point</b> An FDE builds trust by knowing the customer's reality better than the customer wrote it down. Discovery is where that happens.</div>

---

## Move 4 &middot; Qualify: what it is

<p class="muted">Qualification turns a grounded picture into a decision you can defend. You score the candidate honestly, place it against the alternatives, and write a go or no-go with the exact conditions that would flip it. You try to kill your own idea before the customer's reality does.</p>

<div class="columns">
<div class="card"><h3>Decide, do not drift</h3><p>An enthusiastic "let us start" is not a decision. A qualified go names the evidence, the assumptions, and the risks out loud.</p></div>
<div class="card neon"><h3>Be willing to say no</h3><p>The point of qualifying is that some things fail the test. A no you can defend is worth as much as a yes.</p></div>
</div>

<div class="proof"><b>The move in one line</b> Convert a grounded brief into a defensible go or no-go, in the language a board funds in.</div>

---

## The same move, in every field

<p class="muted">Every field has a gate before the big commitment, where a case is made and a decision is owned.</p>

| Field | The qualification | The decision |
| --- | --- | --- |
| **Investing** | due diligence | fund or pass |
| **Medicine** | risk and benefit assessment | operate or not |
| **Lending** | credit underwriting | approve or decline |
| **AI projects** | feasibility, value, and risk | go or no-go |

<div class="proof"><b>The FDE version</b> You are the underwriter of your own project. The memo you write is what a skeptical board reads instead of trusting your enthusiasm.</div>

---

## Principles of effective qualification

<div class="columns3">
<div class="card"><h3>Try to kill it</h3><p>Argue the no case as hard as the yes. A go that survives your own attack is one that survives the board.</p></div>
<div class="card neon"><h3>Numbers, not adjectives</h3><p>"High value" is an opinion. A payback in months is a fact. Qualify in the units the business runs on.</p></div>
<div class="card amber"><h3>Name the no-conditions</h3><p>State exactly what would flip you to no. Naming them is what makes the yes credible.</p></div>
</div>

<div class="proof"><b>The discipline</b> Qualification is honesty under pressure: the pressure to just start building is highest right when you most need to check.</div>

---

## Qualify as a body of knowledge (ITTO)

<p class="muted">The four boxes, now for the decision.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The discovery brief; the three options; the constraints and the deadline | Test desirability, viability, feasibility; build the business case; trace the value; place it against alternatives; name the no-conditions | DVF, business case (ROI, payback, TCO), value-driver tree, feasibility-by-value grid | A qualification memo: a go or no-go, with evidence, assumptions, and the conditions that would flip it |

<div class="proof"><b>Read it left to right</b> A grounded brief comes in; the decision tools act on it; a defensible memo comes out. First, the tools.</div>

---

## Tool 1 &middot; DVF: desirability, viability, feasibility

<p class="muted">A decision passes only if it clears three lenses at once. Miss any one and it is not a go.</p>

<div class="columns3">
<div class="card"><h3>Desirability</h3><p>Do the users actually want it, and will they adopt it? The field hat.</p></div>
<div class="card neon"><h3>Viability</h3><p>Does it make business sense: enough value, acceptable cost? The product hat.</p></div>
<div class="card amber"><h3>Feasibility</h3><p>Can we build it, with the data and risk we have, in the time we have? The engineering hat.</p></div>
</div>

<div class="proof"><b>DVF is your three hats</b> The FDE mindset from the start of the session, written as a decision lens. All three green, or it is not a go.</div>

---

## DVF on Sunrise

<p class="muted">Run support deflection through all three lenses.</p>

<div class="columns3">
<div class="card"><h3>Desirability</h3><p>Customers want instant answers; agents want the routine load gone. Both jobs are real. <strong>Green.</strong></p></div>
<div class="card neon"><h3>Viability</h3><p>Half of 4,000 weekly tickets are deflectable; the saving is real against a modest build. <strong>Green.</strong></p></div>
<div class="card amber"><h3>Feasibility</h3><p>Standard grounding shape, content exists, low harm with escalation; tribal knowledge is a gap. <strong>Green, with one amber.</strong></p></div>
</div>

<div class="drive"><b>What DVF solves here</b> It forces you to check adoption and business sense, not just "can we build it." Deflection clears all three, which upsell (weak desirability and viability) never did.</div>

---

## Tool 2 &middot; The business case: ROI, payback, TCO

<p class="muted">The language a board funds in. Turn the value into money and time, not adjectives.</p>

<div class="columns">
<div class="card"><h3>The four numbers</h3><p><strong>ROI:</strong> return over cost. <strong>Payback:</strong> how long until it pays for itself. <strong>TCO:</strong> total cost to build and run. <strong>NPV:</strong> value over time, discounted.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Converting "this feels valuable" into a number a CFO can check, so the yes survives budget scrutiny.</p></div>
</div>

<div class="proof"><b>Why a case, not a claim</b> Enthusiasm does not get funded twice. A defensible payback does.</div>

---

## The business case on Sunrise

<p class="muted">Rough numbers, honestly labelled, are enough to defend a first PoC.</p>

| Line | Estimate |
| --- | --- |
| Repetitive tickets a week | about 2,400 (60 percent of 4,000) |
| Conservatively deflected | about 1,200 a week |
| Cost per contact saved | roughly Rs 120 |
| **Run-rate saving** | **about Rs 75 lakh a year** |
| Build and first-year run (TCO) | roughly Rs 25 lakh |
| **Payback** | **under four months** |

<div class="drive"><b>What the business case solves here</b> It replaces "support is expensive" with a payback under four months on a conservative deflection rate. That is a number Vikram can take to the board without flinching.</div>

---

## Tool 3 &middot; Value-driver tree

<p class="muted">A tree that connects what you build to the number the business cares about, one link at a time, so the value is traceable.</p>

<div class="columns">
<div class="card"><h3>The shape</h3><p>The financial outcome at the root; the operational metrics that drive it as branches; your solution at a leaf. Each link is a claim you can check.</p></div>
<div class="card neon"><h3>What it is good for</h3><p>Proving the line from "a deflection bot" to "money saved," so no one can wave away the value or inflate it.</p></div>
</div>

<div class="proof"><b>Why a tree</b> It makes the value auditable. If a link is weak, you see exactly where the case breaks.</div>

---

## Value-driver tree on Sunrise

<p class="muted">Trace the line from the bot to the board's number.</p>

<div class="flow">
<span class="step hot">Deflection bot</span><span class="arrow">&rarr;</span>
<span class="step">Tickets deflected</span><span class="arrow">&rarr;</span>
<span class="step">Agent hours freed</span><span class="arrow">&rarr;</span>
<span class="step">Cost to serve down</span><span class="arrow">&rarr;</span>
<span class="step hot">Support margin up</span>
</div>

<div class="columns">
<div class="card"><h3>The driving metric</h3><p>Deflection rate is the lever. Every point of deflection is fewer tickets, freed hours, and lower cost to serve.</p></div>
<div class="card neon"><h3>The check</h3><p>Each arrow is measurable: deflection rate from the bot, hours from staffing, cost from finance. The value is auditable end to end.</p></div>
</div>

<div class="drive"><b>What the tree solves here</b> It ties "grounded answers to common questions" all the way to "support margin up," so the value survives a CFO who asks how, exactly.</div>

---

## Place it on the grid, then decide

<p class="muted">Score the candidate on the gates, then place it against the alternatives. The go is relative, and it has to hold up.</p>

<div class="columns">
<div class="card"><h3>The gates, with numbers</h3><ul><li><strong>Feasibility:</strong> standard grounding shape, buildable by quarter-end. Green.</li><li><strong>Data readiness:</strong> content and tickets usable; tribal knowledge a gap. Amber.</li><li><strong>ROI:</strong> half of 4,000 weekly tickets deflectable. Green.</li><li><strong>Risk:</strong> bounded, low-harm, with escalation. Green with guardrails.</li></ul></div>
<div class="card neon"><h3>Against the alternatives</h3><img src="assets/qualify-grid.svg" alt="Feasibility-by-value grid: support deflection sits top-right, upsell bot top-left, content generation bottom-left" style="width:100%; margin-top:4px;" /></div>
</div>

---

## The decision you hand to the board

<span class="pill">the artifact</span>

<div class="note">
<div class="from">qualification memo &middot; Sunrise support deflection</div>
<strong>Decision: GO</strong>, scoped to order, return, and simple-warranty questions, answered from Sunrise's own help content, with escalation to a human.<br><br>
<strong>Evidence:</strong> 60 percent of 4,000 weekly tickets are in scope; content exists; payback under four months; DVF green.<br>
<strong>Assumptions:</strong> the help content is usable; Legal permits simple-warranty answers.<br>
<strong>We would say NO if:</strong> the content proved unusable, or Legal forbade warranty answers.
</div>

<div class="drive"><b>Why the no-conditions matter</b> Naming exactly what would flip you to no is what makes the yes credible to a skeptical VP.</div>

---

## Qualify on Sunrise, walked through ITTO

<p class="muted">The four boxes, filled with what you just produced.</p>

| Inputs | Process | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| The discovery brief; the three options; the constraints and the deadline | Ran DVF on the candidate; built the business case; drew the value-driver tree; placed it on the grid; named the no-conditions | DVF, business case (ROI, payback, TCO), value-driver tree, feasibility-by-value grid | A qualification memo: GO on support deflection, with evidence, assumptions, and the exact conditions that would flip it |

<div class="drive"><b>Output becomes the next input</b> The GO memo is the input to the Prototype stage, where you choose the model, make it reliable, and ground it in Sunrise's data.</div>

---

## Why we qualify

<p class="muted">Because a "yes" you cannot defend is a liability, and enthusiasm is not a decision.</p>

<div class="columns">
<div class="card neon"><h3>What qualification buys you</h3><p>A go or no-go backed by evidence and named no-conditions, that survives a skeptical board and protects you when the pressure to just start building is highest.</p></div>
<div class="card amber"><h3>Skip it, and</h3><p>You start building on hope, and find the killer risk (unusable data, a legal block) only after you have spent the budget.</p></div>
</div>

<div class="proof"><b>The point</b> The cheapest solution is the one you correctly decided not to build. Qualification is where an FDE is willing to say no.</div>

---

## Brownfield check

<span class="pill brown">if this were not greenfield</span>

<p class="muted">Sunrise is greenfield, so you chose freely. Most real engagements are not. At each move, brownfield changes the answer.</p>

<div class="columns">
<div class="card brownfield"><h3>Where it bites</h3><ul><li><strong>Triage:</strong> integration effort becomes part of a wish's cost</li><li><strong>Frame:</strong> an existing chatbot may force "assist" over "deflect"</li><li><strong>Discover:</strong> half the brief becomes the systems you must live with</li><li><strong>Qualify:</strong> a green build can flip to no-go on integration risk alone</li></ul></div>
<div class="card neon"><h3>The rule</h3><p>On brownfield, "how it fits what already exists" is not a footnote; it is an input to every decision. We build Sunrise clean, and ask this question at every stage so the habit is there when the real account is not clean.</p></div>
</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">The reveal</span>

## Now, what did you just learn?

<p class="muted">You drove a real engagement from a wish list to a defended go. You were not taught four topics; you used them. Here they are, named.</p>

---

## The four disciplines you just used

<div class="columns">
<div class="card"><h3>The FDE mindset</h3><p>You owned the outcome, not the wish list, wearing three hats at once: product (value), field (the real pain), engineering (feasibility). <span class="muted">Topic 1.</span></p></div>
<div class="card neon"><h3>Design thinking</h3><p>You framed before building: empathize, define, ideate. A sharp problem statement and three distinct options, not a tool chosen too early. <span class="muted">Topic 2.</span></p></div>
<div class="card amber"><h3>Discovery</h3><p>Functional analysis: separating the ask from the need, jobs-to-be-done, and stakeholder and value mapping, to ground the options in reality. <span class="muted">Topic 3.</span></p></div>
<div class="card"><h3>Qualification</h3><p>The four gates, the feasibility-by-value grid, and a defensible go or no-go with named no-conditions. <span class="muted">Topic 4.</span></p></div>
</div>

<div class="proof"><b>One lens ran through all four</b> Value = pain times frequency times cost. You met it in triage, and it reappeared in every read and every gate.</div>

---

## Concept: the FDE mindset

<p class="muted">The stance you held all session: own the outcome, not the artifact.</p>

<div class="columns">
<div class="card"><h3>The three hats</h3><p>An FDE is <strong>product</strong> (what is worth building), <strong>field</strong> (what the customer actually needs), and <strong>engineering</strong> (what will hold up), all in one person. You do not hand the framing to someone else.</p></div>
<div class="card neon"><h3>Ownership and value</h3><p>Forward-deployed ownership runs from the messy problem to the running, handed-over solution. <strong>Value = pain times frequency times cost</strong> decides what is worth solving, and <strong>adoption</strong>, not delivery, is the finish line.</p></div>
</div>

<div class="proof"><b>Where you used it</b> You owned the outcome and cut a wish list down to one problem worth solving, wearing all three hats at once.</div>

---

## Concept: design thinking for AI

<p class="muted">The method that turns a messy situation into a framed problem with real options. A loop, not a line.</p>

<div style="text-align:center; margin: 6px 0 2px;">
<img src="assets/dt-loop.svg" alt="The design thinking loop: empathize, define, ideate, prototype, test, and back" style="width:100%; max-width:840px;" />
</div>

<div class="columns">
<div class="card"><h3>Frame, do not solution</h3><p>Understand the user, then write one sharp problem statement, phrased as <strong>how might we</strong>, so it invites solutions without naming a tool.</p></div>
<div class="card neon"><h3>Generate distinct options</h3><p>Ideate several genuinely different ways to solve it, so the later choice is real, not three shades of one idea.</p></div>
</div>

<div class="proof"><b>Where you used it</b> You sat with the team, wrote the problem statement, and put three distinct options (deflect, route, assist) on the table, before anyone built a bot.</div>

---

## Concept: discovery (functional analysis)

<p class="muted">Grounding the framed options in what is actually true, before you commit.</p>

<div class="columns">
<div class="card"><h3>Separate the ask from the need</h3><p>The stated ask is rarely the real one. Find the <strong>job to be done</strong>, and check it against real data, not "we have tons of data."</p></div>
<div class="card neon"><h3>Map who and what</h3><p><strong>Stakeholders</strong> and their vetoes, the <strong>data sources</strong> and their true state, the <strong>systems</strong> it touches, and the <strong>constraints</strong> (legal, residency, budget, timeline).</p></div>
</div>

<div class="proof"><b>Where you used it</b> You pulled real tickets, mapped support ops, IT, legal, and the agents, surfaced residency and legal limits, and narrowed the scope to what is groundable.</div>

---

## Concept: qualifying AI use-cases

<p class="muted">Turning a grounded picture into a decision you can defend to a skeptical board.</p>

<div class="columns">
<div class="card"><h3>The four gates</h3><p>Score the problem on <strong>feasibility</strong>, <strong>data readiness</strong>, <strong>ROI</strong>, and <strong>risk</strong>, with real numbers, and first ask whether it is even an AI problem at all.</p></div>
<div class="card neon"><h3>Decide, and defend</h3><p>Place it on the <strong>feasibility-by-value grid</strong> against the alternatives, and write a <strong>go or no-go</strong> with the exact <strong>no-conditions</strong> that would flip it.</p></div>
</div>

<div class="proof"><b>Where you used it</b> You scored the gates, placed support deflection top-right, and wrote a GO naming exactly what would make you say no.</div>

---

## Business value, in the numbers a board trusts

<p class="muted">A board does not buy "AI for support." It buys a number it can defend. An FDE translates the problem into the metrics the business already runs on.</p>

<div class="columns3">
<div class="card"><h3>Operational</h3><p>Deflection and containment rate, average handle time (AHT), first-contact resolution (FCR), and cost per contact.</p></div>
<div class="card neon"><h3>Experience</h3><p>CSAT, NPS, and Customer Effort Score (CES): is the customer happier, or only deflected?</p></div>
<div class="card amber"><h3>Financial</h3><p>ROI, payback period, total cost of ownership (TCO), and net present value (NPV) over the build.</p></div>
</div>

<div class="flow">
<span class="step hot">Tickets deflected</span><span class="arrow">&times;</span>
<span class="step">Cost per contact</span><span class="arrow">=</span>
<span class="step">Run-rate saving</span><span class="arrow">&rarr;</span>
<span class="step hot">Payback vs TCO</span>
</div>

<div class="proof"><b>The one calculation that lands</b> At Sunrise, roughly 60 percent of 4,000 weekly tickets are in scope. Even a conservative deflection rate times cost per contact gives a run-rate saving, and that saving sets the payback against build and run cost. That number, not the demo, is what turns a skeptical yes into a funded one.</div>

---

## And you started a delivery framework

<p class="muted">The four artifacts you produced are not one-offs. They are the first templates of the <strong>FDE delivery framework</strong>, the playbook you reuse on every account.</p>

<div class="stats">
  <div class="stat"><b>1</b><span>Problem-selection note</span></div>
  <div class="stat"><b>2</b><span>Problem statement + options</span></div>
  <div class="stat"><b>3</b><span>Discovery brief</span></div>
  <div class="stat"><b>4</b><span>Qualification memo (GO)</span></div>
</div>

<div class="proof"><b>The Frame stage, complete</b> Together these four are the "Frame" stage of an FDE engagement. Every session adds a stage and a template, until you hold a full delivery playbook you can carry into the real role.</div>

---

## Now you drive it

<span class="pill field">your engagement</span>

<div class="columns">
<div class="card neon"><h3>Your brief</h3><p>You picked a vertical and received a wish list of the same messy shape. Run the same four moves: triage, frame, discover, qualify.</p></div>
<div class="card"><h3>Your four artifacts</h3><p>A problem-selection note, a problem statement with three options, a discovery brief, and a qualification memo with a defensible go. This is the Frame stage of your Capstone L1.</p></div>
</div>

<div class="proof"><b>Same rubric, any domain</b> Banking, healthcare, retail, or your own client context, all in Bharat. The wish list changes; the way you drive it does not.</div>

---

<!-- _class: lead -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Session 1 &middot; Complete</span>

# <span class="grad">From a wish list to a committed go.</span>

<p class="muted" style="font-size: 22px; max-width: 52ch; margin-top: 12px;">You framed the right problem and can defend the choice. That is the Frame stage of an FDE engagement, and the first four templates of your delivery playbook.</p>

### <span class="brandlite">Next: the Prototype stage. Choose the model by comparing, make it reliable, ground it in Sunrise's data, and ship a clickable PoC.</span>
