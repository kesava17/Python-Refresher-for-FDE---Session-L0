---
marp: true
size: 16:9
paginate: true
title: Microservices Architecture
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
li { margin: 3px 0; }
li::marker { color: var(--neon-600); }
em { color: var(--muted); font-style: italic; }

table { border-collapse: collapse; width: 100%; font-size: 14px; margin-top: 4px; }
th { background: var(--ink); color: #EEF2FF; text-align: left; padding: 6px 10px; font-weight: 600; }
td { border-bottom: 1px solid var(--border); padding: 6px 10px; vertical-align: top; }
tr:nth-child(even) td { background: var(--panel-cool); }

blockquote {
  border: none; border-left: 5px solid var(--neon); background: var(--panel-cool);
  padding: 12px 17px; color: var(--ink-soft); font-size: 19px; border-radius: 6px; margin: 10px 0;
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
.card h3 { margin-top: 0; }
.card p { margin: 5px 0 0; }
.card ul { margin: 4px 0 0; }

.tag2 { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }

.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 16px; }
.stat { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 15px 10px; text-align: center; }
.stat b {
  display: block; font-family: 'Space Grotesk', sans-serif; font-size: 30px; line-height: 1; margin-bottom: 5px;
  background: linear-gradient(120deg, var(--neon), var(--primary)); -webkit-background-clip: text; background-clip: text; color: transparent;
}
.stat span { color: var(--muted); font-size: 14px; }

.pill { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--primary-600); background: var(--panel-cool); border: 1px solid var(--border); border-radius: 999px; padding: 3px 12px; margin-bottom: 8px; }

.flow { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin: 12px 0; }
.flow .step { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 7px 13px; font-weight: 600; font-size: 15px; color: var(--ink); }
.flow .step.hot { border-color: var(--neon); color: var(--neon-600); }
.flow .arrow { color: var(--primary); font-weight: 800; font-size: 18px; }

.chips { display: flex; flex-wrap: wrap; gap: 7px; margin: 10px 0; align-items: center; }
.chip {
  background: var(--panel-cool); border: 1px solid var(--border); color: var(--ink-soft);
  border-radius: 999px; padding: 6px 12px; font-weight: 600; font-size: 15px;
}
.chip.hot { background: linear-gradient(100deg, rgba(79,70,229,.12), rgba(16,185,129,.12)); border-color: rgba(79,70,229,.35); color: var(--primary-600); }
.tag { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-right: 2px; }

.proof { border: none; border-left: 5px solid var(--accent); background: #FFFBEB; padding: 9px 15px; border-radius: 6px; font-size: 16px; color: var(--ink-soft); margin-top: 10px; }
.proof b { color: #B45309; font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; display: inline-block; margin-right: 6px; }

.learn { display: flex; flex-direction: column; gap: 5px; margin-top: 6px; }
.lrow { display: grid; grid-template-columns: 190px 1fr; gap: 12px; align-items: center; background: var(--panel); border: 1px solid var(--border); border-left: 4px solid var(--primary); border-radius: 8px; padding: 6px 12px; }
.lrow:nth-child(3n+2) { border-left-color: var(--neon); }
.lrow:nth-child(3n) { border-left-color: var(--accent); }
.lrow .topic { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px; line-height: 1.15; }
.lrow .topic small { display: block; font-family: 'JetBrains Mono', monospace; font-size: 9.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-top: 1px; }
.lrow .body { font-size: 14px; color: var(--ink-soft); }

.split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 8px; }
.own { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 11px 15px; }
.own.arch { border-top: 4px solid var(--primary); }
.own.eng { border-top: 4px solid var(--neon); }
.own h3 { margin: 0 0 6px; }
.own .tag2 { display: block; margin-bottom: 4px; }

section.lead, section.divider, section.dark {
  background:
    radial-gradient(120% 120% at 85% 12%, rgba(79,70,229,0.30), transparent 46%),
    radial-gradient(120% 120% at 8% 92%, rgba(16,185,129,0.22), transparent 50%),
    linear-gradient(135deg, #0B1020 0%, #131A31 55%, #0A0E1A 100%);
  color: #E6EAF5;
}
section.lead h1, section.divider h1, section.dark h1,
section.lead h2, section.divider h2, section.dark h2 { color: #fff; border: none; padding: 0; }
section.divider h2, section.dark h2 {
  border-bottom: 3px solid transparent;
  border-image: linear-gradient(90deg, var(--primary), var(--neon)) 1;
  padding-bottom: 8px; display: inline-block;
}
section.lead strong, section.divider strong, section.dark strong { color: #fff; }
section.lead .muted, section.divider .muted, section.dark .muted { color: #AEB6CC; }
section.lead::after, section.divider::after, section.dark::after { color: #6B7488; }
section.divider .pill, section.dark .pill { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.18); color: #C7D2FE; }
section.dark .card, section.divider .card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); }
section.dark .card h3, section.divider .card h3 { color: #C7D2FE; }
section.dark li { margin: 6px 0; }
section.dark li::marker { color: var(--neon); }
section.dark .stat, section.divider .stat { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.14); }

.deck-logo { height: 50px; display: block; margin-bottom: 18px; }
.brandmark { position: absolute; top: 32px; right: 54px; height: 27px; opacity: .9; }
.brandlite { color: #A5B4FC; font-weight: 700; }
section.lead h3, section.divider h3, section.dark h3 { color: #C7D2FE; }

section.dark blockquote, section.divider blockquote, section.lead blockquote { color: var(--ink-soft); }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Python for AI and Data Engineering &middot; Microservices Architecture</span>

# Microservices Architecture

### <span class="muted">A 101 on the shape of a system.</span> <span class="brandlite">When one deployable is no longer enough, you split it into services. This session is why you split, the architecture that results, how each piece is built, and how you redesign the app you already have into it.</span>

<p class="muted" style="font-size: 22px; max-width: 56ch; margin-top: 14px;">The hardest judgment is not how to split, it is when not to. We build both.</p>

---

## What we will learn today

<div class="chips">
<span class="tag">the qualities this architecture must deliver</span>
<span class="chip">Performant</span>
<span class="chip">Scalable</span>
<span class="chip">Reliable</span>
<span class="chip">Maintainable</span>
<span class="chip">Interoperable</span>
<span class="chip">Trustworthy</span>
<span class="chip">Secure</span>
</div>

<p class="muted"><span class="tag">today</span> from the drivers, to the model, to the engineering, to the redesign.</p>

<div class="learn">
<div class="lrow"><div class="topic">The drivers<small>why split at all</small></div><div class="body">What pushes a team off a monolith, what a split buys, what it costs, and when a monolith is still the right call.</div></div>
<div class="lrow"><div class="topic">The architecture model<small>the overall shape</small></div><div class="body">What a microservice is, the reference model, synchronous and asynchronous communication, and data per service.</div></div>
<div class="lrow"><div class="topic">Piece by piece<small>design, then FastAPI code</small></div><div class="body">Each part of the system, its design decision and the FastAPI code that builds it: the service, contract, gateway, UI, calls, messaging, data, resilience, observability, deployment, tests.</div></div>
<div class="lrow"><div class="topic">Redesign the app<small>reviews-insight, front to back</small></div><div class="body">Take the running reviews-insight application and design it into a microservice pattern of vertical slices, UI to data, with a safe migration path.</div></div>
</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Why split at all</span>

## The drivers

<p class="muted">Microservices are a trade, not an upgrade. Start with the pressure that makes the trade worth taking.</p>

---

## The monolith you have today

<p class="muted">One codebase, one deployable, one database. For a long time this is exactly right, and you should not apologize for it.</p>

<div class="columns">
<div class="card neon"><h3>What a monolith is</h3><p>All the application's capabilities in <strong>one deployable unit</strong>: one process to run, one pipeline to ship, one database behind it. Our <code>reviews-insight</code> app is a monolith today.</p></div>
<div class="card"><h3>Why it is a good default</h3><p>Simple to build, run, and reason about. One place to deploy, one place to debug, no network between your own functions. Most systems should start here.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> The monolith is not the enemy. A well-structured monolith with clear internal modules will outlast a badly split set of services. Earn the split; do not assume it.</div>

---

## Where the monolith strains

<p class="muted">The trouble is not size on its own. It is when one part of the system holds the rest hostage.</p>

<div class="columns">
<div class="card amber"><h3>Coupling of change</h3><ul>
<li>A one-line fix means redeploying the whole application</li>
<li>One team's release is blocked by another team's unfinished work</li>
<li>The whole system shares one technology choice, forever</li>
</ul></div>
<div class="card amber"><h3>Coupling of failure and scale</h3><ul>
<li>One memory leak or crash can take everything down</li>
<li>One hot path forces you to scale the entire app, not just it</li>
<li>The database becomes a single point of contention</li>
</ul></div>
</div>

<div class="proof"><b>Common trap</b> Reaching for microservices to fix a messy monolith. If the boundaries are unclear in one process, they will be worse across a network. Clean up the modules first, then split along the seams you found.</div>

---

## What a split buys you

<p class="muted">Each benefit is really the same word: independence. The parts stop holding each other back.</p>

<div class="columns3">
<div class="card"><h3>Independent deploy</h3><p>Ship one service without redeploying the rest. Small, frequent, low-risk releases.</p></div>
<div class="card neon"><h3>Independent scale</h3><p>Give more machines to the one busy service, and leave the quiet ones small. You pay for what is hot.</p></div>
<div class="card amber"><h3>Team ownership</h3><p>A team owns a service end to end and moves at its own pace, behind a clear contract.</p></div>
</div>
<div class="columns" style="margin-top:14px;">
<div class="card"><h3>Fault isolation</h3><p>One service failing is a degraded feature, not a dead system, if you designed for it.</p></div>
<div class="card neon"><h3>Technology fit</h3><p>A service can use the language or store that suits its job, as long as it honours its contract.</p></div>
</div>

---

## The costs, and the honest trade

<p class="muted">The network is now in the middle of your application. Everything that was a function call is now a request that can be slow, fail, or arrive twice.</p>

<div class="columns">
<div class="card amber"><h3>What you take on</h3><ul>
<li><strong>Latency and partial failure</strong>: calls cross the wire and can time out</li>
<li><strong>Distributed data</strong>: no single database, so no easy join or transaction</li>
<li><strong>Operational load</strong>: many deployables to run, watch, and secure</li>
<li><strong>Harder debugging</strong>: one request now spans several services</li>
</ul></div>
<div class="card neon"><h3>The rule</h3><p><strong>Monolith first.</strong> Split only when a real pressure appears: a team that must ship independently, a path that must scale alone, a fault that must be contained. Split for a reason you can name.</p></div>
</div>

<div class="proof"><b>The trade</b> Microservices exchange in-process simplicity for independence at the cost of distributed-system complexity. You only come out ahead when the independence is worth more than the complexity it buys.</div>

---

## When to split, and when not

<p class="muted">The unit of a good split is a business capability, not a technical layer. Cut along what the system does, not how it is coded.</p>

<div class="columns">
<div class="card neon"><h3>Split by capability</h3><p>A <strong>bounded context</strong>: a slice of the domain with its own data and rules, such as "ingest reviews" or "serve aggregates". Each service is one capability, whole.</p></div>
<div class="card amber"><h3>The anti-pattern</h3><p>The <strong>distributed monolith</strong>: services that cannot deploy or change without each other. You paid the network cost and kept none of the independence. The worst of both.</p></div>
</div>

<div class="proof"><b>Common trap</b> Splitting by technical layer (a "controller service", a "database service") instead of by capability. It scatters one change across every service and couples them tightly. Split so that a typical change touches one service.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">The architecture model</span>

## The overall shape

<p class="muted">Before the pieces, the picture: what a service is, how the parts connect, and how the data is divided.</p>

---

## What a microservice is

<p class="muted">Four properties, together. Drop any one and it is something else.</p>

<div class="columns">
<div class="card"><h3>Small and single-purpose</h3><p>It owns <strong>one capability</strong> and does it well. You can hold its job in your head.</p></div>
<div class="card neon"><h3>Independently deployable</h3><p>It ships on its own, without a coordinated release of the whole system.</p></div>
</div>
<div class="columns" style="margin-top:14px;">
<div class="card amber"><h3>Owns its data</h3><p>It has <strong>its own store</strong>. No other service reaches into its database.</p></div>
<div class="card"><h3>Talks over a contract</h3><p>It is reached only through a defined interface, never by sharing internals.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> "Independently deployable" and "owns its data" are the two that teams skip, and skipping them is how a set of services quietly becomes a distributed monolith.</div>

---

## The reference model

<p class="muted">Clients load an app shell that composes the user interface from fragments. Behind one gateway, services each own their capability and their store, talk synchronously when they must and through events when they can, and report to a shared observability plane.</p>

<div class="tag" style="margin-bottom:4px;">the request path</div>
<div class="flow">
<span class="step">Clients</span><span class="arrow">&rarr;</span>
<span class="step">App shell + micro-frontends</span><span class="arrow">&rarr;</span>
<span class="step">API gateway</span><span class="arrow">&rarr;</span>
<span class="step hot">Service A + store</span>
<span class="step hot">Service B + store</span>
</div>

<div class="columns3">
<div class="card"><h3>Data plane</h3><p>Each service owns its <strong>store</strong>. No shared database, no cross-service joins.</p></div>
<div class="card neon"><h3>Async plane</h3><p>Services publish and consume <strong>events</strong> through a broker for work that can decouple.</p></div>
<div class="card amber"><h3>Cross-cutting</h3><p>An <strong>observability</strong> plane (logs, metrics, traces) and configuration from the environment.</p></div>
</div>

---

## Communication: synchronous and asynchronous

<p class="muted">Two ways for services to talk. The choice is about whether the caller needs an answer right now.</p>

<div class="columns">
<div class="card"><h3>Synchronous (request and response)</h3><p>The caller asks and waits for the reply. Simple and immediate, but it <strong>couples</strong> the two in time: if the callee is slow or down, the caller feels it. Use when you need the answer to continue.</p></div>
<div class="card neon"><h3>Asynchronous (events and messages)</h3><p>The caller publishes a message and moves on; a consumer handles it later. <strong>Decouples</strong> the two in time and absorbs load spikes, at the cost of eventual, not immediate, results. Use when the work can happen later.</p></div>
</div>

<div class="proof"><b>Common trap</b> Making everything synchronous because it is easier to reason about, then watching one slow service stall a whole chain of callers. Reach for async when a step does not need to block the response.</div>

---

## Data per service, and consistency

<p class="muted">The rule that makes services independent is also the one that makes them hard: each service owns its data, so there is no single database to hold the truth.</p>

<div class="columns">
<div class="card"><h3>Own the store</h3><p>Each service keeps its own database or schema, and no one else touches it. That is what lets a service change its data model without breaking others.</p></div>
<div class="card amber"><h3>Eventual consistency</h3><p>Without one database you lose the easy transaction across services. State becomes <strong>eventually consistent</strong>: correct in a moment, not in the same instant. A multi-service change is coordinated by a <strong>saga</strong>, a sequence of steps with compensating undo.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> Data ownership is the decision that most shapes a microservice design. Get the boundaries right and most calls stay inside one service; get them wrong and every request becomes a distributed transaction.</div>

---

## The frontend monolith problem

<p class="muted">Here is where most "microservice" migrations stop half done. You split the backend into services, and leave one large frontend sitting in front of them all.</p>

<div class="columns">
<div class="card amber"><h3>The hidden bottleneck</h3><p>Every backend team now waits on <strong>one</strong> frontend: one codebase, one release train, one team. The independence you paid for at the back is lost at the front, because a change to one capability still ships through a shared UI.</p></div>
<div class="card neon"><h3>The completing idea</h3><p>True microservice architecture splits <strong>front to back</strong>. If a capability is a service, its slice of the user interface belongs with it, owned and deployed by the same team.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> A monolithic UI over microservices re-couples them at the edge. The frontend becomes the new single point of contention, and the org quietly splits back into a "frontend team" and a "backend team", the horizontal divide microservices were meant to end.</div>

---

## Micro-frontends and vertical slices

<p class="muted">Decompose the user interface along the same capability boundaries, then compose the fragments into one experience behind an app shell.</p>

<div class="columns">
<div class="card"><h3>How they compose</h3><ul>
<li><strong>Build-time</strong>: fragments as packages (simple, but re-couples releases)</li>
<li><strong>Server-side</strong>: assemble fragments at the edge</li>
<li><strong>Runtime</strong>: module federation, web components, or iframes for independent deploy</li>
</ul><p>An <strong>app shell</strong> hosts the fragments and owns the shared concerns: routing, authentication, and the design system.</p></div>
<div class="card neon"><h3>The vertical slice</h3><p>One team owns a capability <strong>front to back</strong>: the UI fragment, the service, and its data, shipped together. The split is <strong>vertical</strong> (by capability), not <strong>horizontal</strong> (by tier). That is what makes the independence real.</p></div>
</div>

<div class="proof"><b>Common trap</b> Runtime micro-frontends add real cost (shared state, a versioned design system, duplicated dependencies). Like the backend split, do it when a pressure justifies it, and let the app shell absorb the shared concerns.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Piece by piece</span>

## Solution architecture and engineering

<p class="muted">Now walk the system part by part. For each, two decisions: the <strong>architecture</strong> (the design choice) and the <strong>engineering</strong> (how it is built in Python).</p>

---

## Two decisions per piece

<p class="muted">Architecture decides the shape; engineering makes it real. A design without the engineering is a diagram; engineering without the design is an accident. Every piece ahead carries both.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>The design choice</h3><p>What the piece is, why it exists, and the boundary and contract it presents to the rest of the system.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>The realization</h3><p>The concrete Python and tooling that make the choice real: the framework, the client, the store, the container, the test.</p></div>
</div>

<div class="proof"><b>How to read the next slides</b> Left is the decision an architect defends; right is the code an engineer ships. The FDE owns both, and reads AI-written code against both.</div>

---

## The service

<p class="muted">The unit of the whole architecture: one capability, deployable on its own.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>One capability, isolated</h3><p>A bounded context with its own data and lifecycle. It can be built, deployed, and scaled without the others.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>A Python service</h3><p>A web framework (for example FastAPI) over a <code>src</code> layout, config read from the environment, a <code>/health</code> endpoint, and its own Poetry project and image.</p></div>
</div>

<div class="proof"><b>Common trap</b> A service that reads another service's database "just for now". That one shortcut couples their data models permanently. Reach only through the contract.</div>

---

## The contract (the API)

<p class="muted">A service is only ever seen through its interface. That interface is a promise you version and keep.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>A versioned boundary</h3><p>Resource-oriented and stateless (REST), or typed and streaming (gRPC). Validate every input at the boundary; version deliberately so a change does not break callers.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>Typed and validated</h3><p><strong>pydantic</strong> models for the request and response, a versioned path such as <code>/v1/reviews</code>, and an OpenAPI schema generated from the code so the contract is not just prose.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> The contract is the real product boundary. Backwards-compatible changes (add a field) are safe; breaking changes (remove or rename) need a new version and a deprecation window.</div>

---

## The API gateway (the edge)

<p class="muted">One front door for many services, so clients see a single system and cross-cutting concerns live in one place.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>A single entry point</h3><p>Routes each request to the right service, and holds the concerns every service would otherwise repeat: authentication, rate limiting, and TLS termination.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>A gateway or reverse proxy</h3><p>A dedicated gateway or a reverse proxy in front of the services. Auth and rate limits are enforced at the edge; internal services trust only what the gateway forwards.</p></div>
</div>

<div class="proof"><b>Common trap</b> Putting business logic in the gateway. The edge routes and guards; it does not decide. Logic in the gateway recreates the monolith at the front door.</div>

---

## The user interface

<p class="muted">A service is not truly independent until its slice of the UI ships with it. The interface is the front of the vertical slice.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>Decompose and compose</h3><p>Split the UI by capability into <strong>micro-frontends</strong>, composed by an <strong>app shell</strong>. A <strong>backend-for-frontend</strong> (BFF) can shape one service's data for its fragment.</p></div>
<div class="own eng"><span class="tag2">engineering</span><h3>Composition and a shell</h3><p>Runtime composition (module federation or web components) and an app shell for routing, auth, and a shared design system. The frontend stack is JavaScript; the <strong>architecture principle is the same</strong> as the services behind it.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> A backend-for-frontend keeps the fragment simple: it calls one tailored endpoint instead of orchestrating several services in the browser. One BFF per frontend, owned by the same vertical-slice team.</div>

---

## Synchronous calls between services

<p class="muted">When one service must ask another for an answer to continue, the call crosses the network, so it must assume the network fails.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>Assume partial failure</h3><p>Every remote call can be slow or fail. Bound it with a timeout, retry the transient failures, and have a plan for when it stays down.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>A guarded HTTP client</h3><p>An <strong>httpx</strong> client with an explicit <strong>timeout</strong>, <strong>retry with backoff</strong> on transient errors, and a correlation id passed in the headers so the call can be traced.</p></div>
</div>

<div class="proof"><b>Common trap</b> A call with no timeout. One slow dependency then holds a request open, threads pile up, and a single slow service takes down its callers. A timeout is not optional.</div>

---

## Asynchronous messaging

<p class="muted">When the work does not need to block the response, hand it off through a broker and let a consumer do it later.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>Decouple through a broker</h3><p>The producer publishes an event and returns; a consumer processes it on its own time. This absorbs spikes and survives a consumer being briefly down.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>A queue and an idempotent consumer</h3><p>A message queue or broker, <strong>at-least-once</strong> delivery, and a consumer written to be <strong>idempotent</strong> so a redelivered message does not double-count.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> At-least-once delivery means duplicates will happen. Idempotency (a processed-id set, an upsert keyed by event id) is what keeps the result correct when they do.</div>

---

## Message queues and brokers

<p class="muted">The broker is the piece in the middle of the asynchronous path. It holds messages so the producer and the consumer never have to be up, or fast, at the same moment.</p>

<div class="flow">
<span class="step">Producer</span><span class="arrow">&rarr;</span>
<span class="step hot">Broker (the queue)</span><span class="arrow">&rarr;</span>
<span class="step">Consumer</span>
</div>

<div class="split">
<div class="own arch"><span class="tag2">queue: point to point</span><h3>One message, one consumer</h3><p>Each message goes to exactly one worker in a pool, each taking the next item. Use it to <strong>share out</strong> a workload across workers.</p></div>
<div class="own eng"><span class="tag2">topic: publish and subscribe</span><h3>One message, every subscriber</h3><p>Each message goes to every interested service, each reacting on its own. Use it to <strong>fan an event out</strong> to many consumers.</p></div>
</div>

<div class="proof"><b>What the broker buys you</b> It decouples the two sides in time, buffers a spike so a burst does not overwhelm the consumer, and retries delivery when a consumer is briefly down. Common brokers: RabbitMQ, Apache Kafka, Amazon SQS, Redis Streams, and NATS.</div>

---

## Delivery guarantees, ordering, and dead letters

<p class="muted">A queue makes a promise about how a message is delivered. Know the three, and the two failure valves every real queue needs.</p>

<div class="columns3">
<div class="card"><h3>At most once</h3><p>Deliver and forget. A message can be <strong>lost</strong>, but never duplicated. Rarely what you want for work that matters.</p></div>
<div class="card neon"><h3>At least once</h3><p>Retry until acknowledged. A message is <strong>never lost</strong>, but can arrive twice. The common default, paired with an idempotent consumer.</p></div>
<div class="card amber"><h3>Exactly once</h3><p>The ideal, and the hardest. Real systems approximate it with at-least-once plus idempotency instead of paying its full cost.</p></div>
</div>

<div class="columns" style="margin-top:14px;">
<div class="card"><h3>Ordering</h3><p>Global order is expensive. Most brokers guarantee order only within a <strong>partition or key</strong> (for example, per account), which is usually all you need.</p></div>
<div class="card amber"><h3>Dead-letter queue</h3><p>A message that keeps failing is moved aside to a <strong>dead-letter queue</strong> after a few tries, so one poison message does not block the rest.</p></div>
</div>

<div class="proof"><b>In practice</b> The working recipe is at-least-once delivery, an idempotent consumer keyed on the message id, per-key ordering where it matters, and a dead-letter queue for messages that cannot be processed.</div>

---

## Data per service

<p class="muted">The store is part of the service, not a shared resource. This is the boundary that makes independence real.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>Private data</h3><p>Each service owns its schema and no other reaches in. Shared state moves by API call or event, never by a shared table.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>A store per service</h3><p>A separate database or schema per service, its own migrations, and no cross-service joins. Data needed elsewhere is published as an event or fetched through the owner's API.</p></div>
</div>

<div class="proof"><b>Common trap</b> One shared database with every service reading every table. It looks efficient and quietly couples every service to every other one's data model. The shared database is the classic distributed-monolith tell.</div>

---

## Resilience

<p class="muted">In a distributed system, failure is normal, not exceptional. The design decides whether a failure is contained or spreads.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>Contain the blast radius</h3><p>One dependency down should be a degraded feature, not a cascade. Stop calling a failing service, and return a clear, fast fallback.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>Timeout, retry, circuit breaker</h3><p>A <strong>timeout</strong> on every call, <strong>retry with backoff</strong> for transient errors, a <strong>circuit breaker</strong> that stops calling after repeated failures and recovers, and a <strong>graceful degradation</strong> path.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> The circuit breaker protects the caller, not the callee. It stops a healthy service from throwing every request into a dead one and exhausting its own resources waiting.</div>

---

## Observability

<p class="muted">One request now spans several services. If you cannot follow it across them, you cannot debug the system.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>See across the system</h3><p>Every service reports its health, and one request can be followed end to end through all the services it touched.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>Health, logs, metrics, traces</h3><p>A <code>/health</code> endpoint, <strong>structured logs</strong> carrying a <strong>correlation id</strong> threaded across calls, metrics per service, and distributed <strong>tracing</strong> to see the full path of a request.</p></div>
</div>

<div class="proof"><b>Common trap</b> Plain text logs with no correlation id. When a request fails halfway across three services, you cannot stitch the story together. The correlation id is what makes the logs one story.</div>

---

## Deployment and parity

<p class="muted">Independent deployment is a promise the packaging has to keep: each service ships on its own, and runs the same everywhere.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>One deployable per service</h3><p>Each service is packaged, versioned, and released on its own, and behaves the same in development and production.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>Containers and Compose</h3><p>One image per service, a <code>docker-compose.yml</code> to run the whole system locally, config from the environment, and the twelve-factor basics for parity with production.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> Local parity matters more with many services than with one. Compose lets a developer bring the whole system up on a laptop and see them talk, which is where most integration bugs surface early.</div>

---

## Testing services

<p class="muted">With the network in the middle, two things need testing: each service alone, and the contract between them.</p>

<div class="split">
<div class="own arch"><span class="tag2">architecture</span><h3>Test the seam</h3><p>Test a service in isolation, and test that two services still agree on their shared contract, so a change on one side cannot silently break the other.</p></div>
<div class="own eng"><span class="tag2">engineering (Python)</span><h3>Contract and isolation tests</h3><p><strong>pytest</strong> for each service with its dependencies stubbed, plus a <strong>contract test</strong> that checks the request and response shapes both sides rely on.</p></div>
</div>

<div class="proof"><b>Common trap</b> Only end-to-end tests. They are slow, flaky, and vague about which service broke. Test each service alone, guard the contract, and keep a few end-to-end checks for the critical path.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Build it with FastAPI</span>

## From design to code

<p class="muted">Now the engineering, for real. Each backend component of the architecture, built in Python with FastAPI, trimmed to its essence. The frontend fragments are JavaScript; everything behind the gateway is here.</p>

---

## The service, and its health

<p class="muted">A microservice is a small FastAPI app: a few routes, config read from the environment, and a health endpoint the platform can poll.</p>

```python
from fastapi import FastAPI
from .config import settings          # read from the environment

app = FastAPI(title="reviews-ingest", version="1.0")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

<div class="columns">
<div class="card"><h3>Run it</h3><p><code>poetry run uvicorn reviews_ingest.main:app</code>. One service, one process, its own Poetry project and image.</p></div>
<div class="card neon"><h3>Why a health route</h3><p>The gateway and the container platform poll it to route only to healthy instances and to restart a sick one.</p></div>
</div>

---

## The contract: pydantic and a versioned route

<p class="muted">FastAPI turns a pydantic model into input validation, a typed response, and an OpenAPI schema, all from the same code.</p>

```python
from pydantic import BaseModel, Field

class ReviewIn(BaseModel):
    product_id: str
    rating: int = Field(ge=1, le=5)
    text: str

@app.post("/v1/reviews", status_code=201)
def create_review(review: ReviewIn) -> dict:
    review_id = store.save(review)         # already validated here
    return {"id": review_id}
```

<div class="proof"><b>The boundary is enforced</b> A rating of 7 is rejected with a 422 before any code runs. The versioned path <code>/v1</code> lets the contract grow without breaking callers, and <code>/docs</code> is generated for free.</div>

---

## Data per service: a private store

<p class="muted">Each service owns its store and reaches it through a small repository. No other service opens this database.</p>

```python
# reviews_ingest/store.py  (owned by this service alone)
import sqlite3

def save(review: ReviewIn) -> int:
    with sqlite3.connect(settings.db_path) as db:
        cur = db.execute(
            "INSERT INTO reviews(product_id, rating, text) VALUES (?, ?, ?)",
            (review.product_id, review.rating, review.text),
        )
        return cur.lastrowid
```

<div class="columns">
<div class="card"><h3>Owned, not shared</h3><p>Only <code>reviews-ingest</code> opens this database. <code>reviews-query</code> keeps its own read store, updated by an event.</p></div>
<div class="card amber"><h3>Swap the engine</h3><p>sqlite for the lab; the same repository interface fronts Postgres or another store in production.</p></div>
</div>

---

## Calling another service, safely

<p class="muted">When one service must call another, wrap the call: a timeout always, a retry with backoff for transient errors, and the correlation id passed along.</p>

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def get_aggregate(product_id: str, correlation_id: str) -> dict:
    with httpx.Client(timeout=2.0) as client:      # never without a timeout
        r = client.get(
            f"{settings.query_url}/v1/aggregates/{product_id}",
            headers={"X-Correlation-ID": correlation_id},
        )
        r.raise_for_status()
        return r.json()
```

<div class="proof"><b>Common trap</b> A call with no timeout holds a request open when the callee stalls. The <code>timeout=2.0</code> is the line that keeps one slow service from taking its callers down.</div>

---

## Asynchronous work: publish and consume

<p class="muted">When work can happen later, publish an event and return. A separate consumer processes it, idempotently, so a redelivery does not double-count.</p>

```python
# producer: after saving a review, publish and return
def create_review(review: ReviewIn) -> dict:
    review_id = store.save(review)
    broker.publish("review-received", {"id": review_id, "product_id": review.product_id})
    return {"id": review_id}

# consumer in reviews-query: idempotent by event id
def on_review_received(event: dict) -> None:
    if seen.add_if_new(event["id"]):           # skip a duplicate
        read_store.update_aggregate(event["product_id"])
```

<div class="proof"><b>At-least-once means duplicates</b> The consumer must be idempotent. Keying on the event id (the <code>seen</code> set, or an upsert) keeps the aggregate correct when a message is redelivered.</div>

---

## Observability: one id across services

<p class="muted">One request spans several services. A FastAPI middleware stamps a correlation id and puts it on every log line, so the request can be followed end to end.</p>

```python
@app.middleware("http")
async def add_correlation_id(request, call_next):
    cid = request.headers.get("X-Correlation-ID", str(uuid4()))
    with logging_context(correlation_id=cid):      # structured logs
        response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    return response
```

<div class="columns">
<div class="card"><h3>Threaded through</h3><p>The service passes the same id on any downstream call, so the logs of every service share one id for the request.</p></div>
<div class="card neon"><h3>Plus health and metrics</h3><p>A health route for liveness, and a metrics endpoint per service for latency and error rates.</p></div>
</div>

---

## The gateway and the backend-for-frontend

<p class="muted">The edge is often a dedicated proxy, but a thin FastAPI service can route or shape data for one frontend, a backend-for-frontend.</p>

```python
# a BFF endpoint: one tailored call for the dashboard fragment
@app.get("/bff/dashboard/{product_id}")
async def dashboard(product_id: str) -> dict:
    async with httpx.AsyncClient(timeout=2.0) as client:
        agg = await client.get(f"{settings.query_url}/v1/aggregates/{product_id}")
    return {"product_id": product_id, "summary": agg.json()}
```

<div class="proof"><b>Keep the edge thin</b> The BFF shapes and forwards; it holds no business logic. Auth, rate limiting, and TLS usually live in a dedicated gateway in front of it, not in this code.</div>

---

## Testing a service, and the contract

<p class="muted">FastAPI's TestClient runs the service in process, with no network, so each service is tested alone and the contract is guarded.</p>

```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_create_review_validates():
    ok = client.post("/v1/reviews", json={"product_id": "p1", "rating": 5, "text": "great"})
    assert ok.status_code == 201

    bad = client.post("/v1/reviews", json={"product_id": "p1", "rating": 7, "text": "x"})
    assert bad.status_code == 422        # the contract rejects rating 7
```

<div class="proof"><b>Run it through Poetry</b> <code>poetry run pytest</code>. The contract test pins the request and response shapes both sides rely on, so a change on one side cannot silently break the other.</div>

---

## Deployment: one image per service

<p class="muted">Each service ships as its own image with uvicorn as the entry point, and Docker Compose brings the whole system up locally.</p>

```dockerfile
FROM python:3.12-slim
RUN pip install poetry
COPY . .
RUN poetry install --only main
CMD ["poetry", "run", "uvicorn", "reviews_ingest.main:app", "--host", "0.0.0.0"]
```

<div class="columns">
<div class="card"><h3>One image each</h3><p>gateway, reviews-ingest, reviews-query: three images, versioned and deployed on their own.</p></div>
<div class="card neon"><h3>Compose for the system</h3><p><code>docker compose up</code> runs all three together, so a developer sees them talk and catches integration bugs on a laptop.</p></div>
</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">From monolith to microservices</span>

## Redesigning reviews-insight

<p class="muted">Now apply all of it to the application you already have. Not a rewrite: a deliberate, safe redesign of the running app into services.</p>

---

## The reviews-insight monolith today

<p class="muted">One deployable that does three jobs behind one process and one database.</p>

<div class="flow">
<span class="step hot">reviews-insight (one app)</span>
<span class="arrow">&rarr;</span>
<span class="step">ingest reviews</span>
<span class="step">compute aggregates</span>
<span class="step">serve queries</span>
<span class="arrow">&rarr;</span>
<span class="step">one database</span>
</div>

<div class="columns">
<div class="card neon"><h3>What works</h3><p>Simple to run and reason about. For its current size, the monolith is a reasonable place to be, and the redesign is a design exercise, not a rescue.</p></div>
<div class="card amber"><h3>The pressure to model</h3><p>Ingest is write-heavy and spiky; query is read-heavy and latency-sensitive. They want to <strong>scale differently</strong>, and they are a clean capability boundary. That is the seam.</p></div>
</div>

---

## The target: reviews-insight as services

<p class="muted">Split along the capability seam into two services, each owning its store, behind one gateway, with the read model kept fresh by an event.</p>

<div class="tag" style="margin-bottom:4px;">the request path</div>
<div class="flow">
<span class="step">Client</span><span class="arrow">&rarr;</span>
<span class="step">App shell</span><span class="arrow">&rarr;</span>
<span class="step">Gateway</span><span class="arrow">&rarr;</span>
<span class="step hot">reviews-ingest + store</span>
<span class="step hot">reviews-query + store</span>
</div>

<div class="columns">
<div class="card"><h3>reviews-ingest slice</h3><p>A <strong>submit-a-review</strong> UI fragment, the service that validates and writes to <strong>its own store</strong>, and a <code>review-received</code> event it publishes. One team, front to back.</p></div>
<div class="card neon"><h3>reviews-query slice</h3><p>A <strong>dashboard</strong> UI fragment, the service that serves aggregates from a <strong>read store</strong> it owns, updated by consuming the ingest event. Reads never touch the ingest database.</p></div>
</div>

<div class="proof"><b>The shape</b> Two vertical slices, each from UI fragment to service to store, behind one app shell and one gateway. A versioned contract, a synchronous read path, and an asynchronous update path. Each slice scales, deploys, and fails independently.</div>

---

## The migration path: strangler fig

<p class="muted">You do not stop and rewrite. You grow the new services around the monolith and retire it a slice at a time, staying live throughout.</p>

<div class="flow">
<span class="step">Route through a gateway</span><span class="arrow">&rarr;</span>
<span class="step">Extract one capability</span><span class="arrow">&rarr;</span>
<span class="step">Move its data</span><span class="arrow">&rarr;</span>
<span class="step hot">Retire the old path</span>
</div>

<div class="columns">
<div class="card"><h3>One capability at a time</h3><p>Put the gateway in front, carve out <code>reviews-query</code> first (reads are safest), point traffic at it, prove it, then do <code>reviews-ingest</code>. The monolith shrinks until it is gone.</p></div>
<div class="card amber"><h3>Why not big-bang</h3><p>A stop-the-world rewrite is the highest-risk option: no working system until the end, and every problem lands at once. The strangler keeps a working app at every step.</p></div>
</div>

<div class="proof"><b>Enterprise lens</b> The migration is itself an application of the qualities: each extraction is small (maintainable), independently shipped (deployable), and gated by tests and a rollback (reliable).</div>

---

## The redesign decisions, mapped

<p class="muted">Every piece from the middle of this session, applied to reviews-insight. This table is the design.</p>

<table>
<tr><th>Piece</th><th>Decision for reviews-insight</th></tr>
<tr><td>Vertical slices</td><td>two capabilities, each owned front to back: UI fragment, service, and store</td></tr>
<tr><td>Services</td><td><code>reviews-ingest</code> (write) and <code>reviews-query</code> (read), split by capability</td></tr>
<tr><td>User interface</td><td>a submit fragment and a dashboard fragment, composed in one app shell</td></tr>
<tr><td>Contract</td><td>versioned REST, pydantic-validated, <code>/v1/reviews</code> and <code>/v1/aggregates</code></td></tr>
<tr><td>Gateway</td><td>one front door, routing plus auth and rate limiting at the edge</td></tr>
<tr><td>Sync call</td><td>guarded httpx client with timeout and retry where query must ask ingest</td></tr>
<tr><td>Async</td><td><code>review-received</code> event updates the read model; idempotent consumer</td></tr>
<tr><td>Data</td><td>a write store and a read store, each private to its service</td></tr>
<tr><td>Resilience</td><td>timeouts, circuit breaker, and a clear fallback when ingest is down</td></tr>
<tr><td>Observability</td><td>health per service, correlation id across the call, metrics and traces</td></tr>
<tr><td>Deployment</td><td>one image per service, one <code>docker-compose.yml</code> for the system</td></tr>
</table>

---

## Prove it in the live lab

<span class="pill">the build</span>

<p class="muted">The redesign becomes runnable code. You split <code>reviews-insight</code> into the two services and stand the system up locally.</p>

<div class="columns">
<div class="card neon"><h3>What you build</h3><ul>
<li><code>reviews-ingest</code> and <code>reviews-query</code>, each its own service and store</li>
<li>A versioned contract between them, and a gateway in front</li>
<li>Health, a correlation id across the call, a timeout and retry</li>
<li>One <code>docker-compose.yml</code> to run the whole system</li>
</ul></div>
<div class="card"><h3>The proof</h3><ul>
<li><code>docker compose up</code> brings both services healthy</li>
<li>A contract test between them passes</li>
<li>Stop <code>reviews-ingest</code>: <code>reviews-query</code> degrades cleanly, it does not hang</li>
</ul></div>
</div>

<div class="proof"><b>Run it through Poetry</b> Each service is its own Poetry project; you run and test it with <code>poetry run</code>, and bring the system together with Docker Compose. The demos and the step-by-step are in the live lab.</div>

---

## Recap: what you can now do

<div class="columns">
<div class="card"><h3>You understand</h3><ul>
<li>Why teams split, what it buys, and what it costs</li>
<li>Monolith-first, and when a split is justified</li>
<li>What a microservice is, and the reference model</li>
<li>Synchronous versus asynchronous, and data per service</li>
</ul></div>
<div class="card neon"><h3>You can design</h3><ul>
<li>Each piece as an architecture decision and its engineering</li>
<li>The contract, gateway, UI, calls, messaging, data, resilience, observability, deployment, and tests</li>
<li>Micro-frontends and vertical slices, so the split runs front to back</li>
<li>A monolith redesigned into services with a strangler-fig migration</li>
</ul></div>
</div>

<div class="proof"><b>The one-line answer</b> Microservices trade in-process simplicity for independence: split by capability into vertical slices owned front to back, give each service its own data and contract, design for partial failure, and migrate a slice at a time, only when a real pressure makes the trade worth it.</div>

---

<!-- _class: lead -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Microservices Architecture &middot; Complete</span>

# <span class="grad">One app becomes a system of services, on purpose.</span>

<p class="muted" style="font-size: 22px; max-width: 56ch; margin-top: 12px;">You learned the drivers, the architecture model, the engineering of each piece, micro-frontends and vertical slices, and how to redesign the running reviews-insight application into a microservice pattern, front to back, with a safe migration path.</p>

### <span class="brandlite">Next: the live lab, where you split reviews-insight into two services, wire them with a contract and a gateway, and prove the system comes up healthy and fails gracefully.</span>
