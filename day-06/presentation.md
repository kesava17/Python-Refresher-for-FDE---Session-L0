---
marp: true
size: 16:9
paginate: true
title: Secure by Design and Execution
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

<span class="kicker">Python for AI and Data Engineering &middot; Secure</span>

# Secure by Design and Execution

### <span class="muted">The last of the seven qualities.</span> <span class="brandlite">A defensible design that the code makes real, defended at every layer.</span>

<p class="muted" style="font-size: 22px; max-width: 54ch; margin-top: 14px;">Security bridges two disciplines that fail apart: architectural design (threat modeling, boundaries, standards) and engineering execution (secure coding, hard guardrails). This chapter is both, together.</p>

---

## What we will learn today

<div class="chips">
<span class="tag">the seven qualities</span>
<span class="chip">Performant</span>
<span class="chip">Scalable</span>
<span class="chip">Maintainable</span>
<span class="chip">Reliable</span>
<span class="chip">Interoperable</span>
<span class="chip">Trustworthy</span>
<span class="chip hot">Secure</span>
</div>

<p class="muted"><span class="tag">today</span> security as a shared responsibility, layer by layer.</p>

<div class="learn">
<div class="lrow"><div class="topic">Mindset and maps<small>shared ownership</small></div><div class="body">Security as a quality attribute, the architect and engineer contract, the principles, and the OWASP and STRIDE frameworks you audit against.</div></div>
<div class="lrow"><div class="topic">The layers<small>blueprint and realization</small></div><div class="body">Identity, data and crypto, the API surface, threat modeling, the supply chain and runtime, and detection and response.</div></div>
<div class="lrow"><div class="topic">Prove it<small>build and workshops</small></div><div class="body">reviews-insight hardened layer by layer, the STRIDE-and-code pair, and the break-the-build lab.</div></div>
</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">The reality</span>

## Built by app developers, with no security specialist

<p class="muted">A capable team ships a real system: a React single-page app talking to Java (Spring Boot) microservices, developed and tested in a dev environment, then handed to DevOps to deploy. They are good at building features. There is no security specialist in the room.</p>

<div class="flow">
<span class="step">React SPA</span><span class="arrow">&rarr;</span>
<span class="step">Java microservices</span><span class="arrow">&rarr;</span>
<span class="step">Handed to DevOps</span>
</div>

<div class="proof"><b>How they build</b> By the standard libraries and the design they learned in their degree course. They know each library at an outline level, a package name and a quickstart, not what it actually does underneath.</div>

---

## The system they build

<p class="muted">A normal, reasonable architecture, every box straight from a tutorial.</p>

<div class="columns">
<div class="card"><h3>The moving parts</h3><ul><li>A <strong>React SPA</strong> in the browser</li><li>An <strong>API gateway</strong> to a handful of <strong>Spring Boot microservices</strong> (auth, users, orders, reviews)</li><li>A <strong>Postgres</strong> and a <strong>Mongo</strong>, a <strong>Redis</strong> cache, a <strong>Kafka</strong> queue, a few <strong>third-party APIs</strong></li></ul></div>
<div class="card neon"><h3>How it holds together</h3><ul><li>Login mints a <strong>JWT</strong> in the auth service; the browser sends it on every call</li><li>Services call each other on the internal network</li><li>All configuration lives in <strong>.env</strong> files and container environment variables</li></ul></div>
</div>

<div class="proof"><b>Nothing looks wrong</b> Every choice here is a standard one. The security gaps are inside the boxes and on the arrows between them.</div>

---

## What they build, and what they do not know

<p class="muted">Three everyday choices, each a single function call or a one-line command, each hiding what it actually does.</p>

<div class="columns3">
<div class="card amber"><h3>"Create a JWT"</h3><p>Call the library, get a token. They do not know it is only <strong>base64</strong> (anyone can read the claims), that they put the user's email and role in it in the clear, that they set <strong>no expiry or audience</strong>, that the signing secret is a short string in <code>.env</code>, and that some libraries accept <code>alg:none</code>.</p></div>
<div class="card amber"><h3>"Put it in .env"</h3><p>Every value in one file: the DB password, the third-party keys, the JWT secret, a feature flag, the log level. They do not know which are <strong>secrets</strong> and which are config, that <code>.env</code> gets committed or baked into the image, or that nothing is rotated.</p></div>
<div class="card amber"><h3>"npm install / mvn add"</h3><p>Pull in a package a blog recommended. They do not know its <strong>transitive dependencies</strong>, its known CVEs, its license, or whether the name is a <strong>typosquat</strong>. No lockfile discipline, no scan, nobody to vet it.</p></div>
</div>

<div class="proof"><b>Not laziness</b> This is the honest result of outline-level knowledge of each tool, and no one on the team to check the parts they cannot see.</div>

---

## What it should have been

<p class="muted">The same three choices, made with the security lens this chapter builds.</p>

<div class="columns3">
<div class="card neon"><h3>The JWT</h3><p>A <strong>short-lived</strong> access token with <code>exp</code>, <code>aud</code>, and <code>iss</code> set; <strong>no PII</strong> in the claims (carry a user id, look the rest up); the signing key from a <strong>secrets manager</strong>; a pinned algorithm that rejects <code>alg:none</code>; and full validation on every request.</p></div>
<div class="card neon"><h3>The .env</h3><p>Only <strong>non-secret config</strong> in <code>.env</code>, never committed. Secrets injected at runtime from a <strong>secrets manager</strong>, different per environment, classified and rotated, with a <strong>secret scan</strong> in CI.</p></div>
<div class="card neon"><h3>The dependency</h3><p><strong>Pin and lock</strong> exact versions, <strong>scan</strong> them in CI (npm audit, OWASP dependency-check, Trivy), verify the source and the name, review a new one, and keep an <strong>SBOM</strong>.</p></div>
</div>

<div class="proof"><b>Same effort, once you know</b> None of this is harder to write. It is only harder to know, which is what the rest of the chapter fixes.</div>

---

## More standard choices, more hidden gaps

<p class="muted">The same shape again: a one-line fix that makes the feature work, and a gap nobody sees.</p>

<div class="columns3">
<div class="card amber"><h3>"Enable CORS"</h3><p>Set <code>Access-Control-Allow-Origin: *</code> so the browser stops erroring. They do not know this lets <strong>any website</strong> call the API, and allowing credentials with it hands the user's session to any origin.</p></div>
<div class="card amber"><h3>"Hash the password"</h3><p>Reach for MD5 or a bare SHA-256, because that is "hashing." They do not know it is <strong>unsalted and cracked in seconds</strong>, and that passwords need a slow, salted function (bcrypt, argon2).</p></div>
<div class="card amber"><h3>"Return the error"</h3><p>Send the exception and stack trace back to the client while debugging, and leave it on. They do not know it <strong>leaks the framework, versions, queries, and file paths</strong> that map the system for an attacker.</p></div>
</div>

<div class="proof"><b>Each looks correct</b> The code works, the demo passes, and the gap ships to production unseen.</div>

---

## What it should have been

<p class="muted">The corrected version of the same three moves.</p>

<div class="columns3">
<div class="card neon"><h3>CORS</h3><p>Allow only the <strong>specific known origins</strong>, never <code>*</code>, and never combine a wildcard with credentials. Keep the policy as tight as the front end actually needs.</p></div>
<div class="card neon"><h3>Passwords</h3><p>A slow, <strong>salted</strong> function built for it (bcrypt or argon2) with a sensible cost. Never MD5 or a bare SHA for passwords, never plaintext, and add multi-factor for sensitive actions.</p></div>
<div class="card neon"><h3>Errors</h3><p>Log the full detail <strong>internally</strong> with a correlation id, and return a <strong>generic</strong> message to the client. No stack traces, no internal detail, and debug mode off in production.</p></div>
</div>

<div class="proof"><b>Fail safe, reveal nothing</b> The user sees "something went wrong"; you see exactly what, in a place the attacker cannot reach.</div>

---

## The same pattern, again

<p class="muted">Three more everyday moves, from the container to the tokens.</p>

<div class="columns3">
<div class="card amber"><h3>"Copy the Dockerfile"</h3><p><code>FROM node:latest</code>, runs as <strong>root</strong>, a secret passed as a build <code>ARG</code>. They do not know the tag is unpinned, root magnifies any exploit, and the secret stays in the <strong>image layer history</strong>.</p></div>
<div class="card amber"><h3>"Serialize the object"</h3><p>Java native serialization, or Jackson polymorphic typing (in Python, <code>pickle</code>), to save and load objects. They do not know that untrusted input on that path is <strong>remote code execution</strong>.</p></div>
<div class="card amber"><h3>"Generate the token"</h3><p>Use <code>Math.random()</code> or <code>java.util.Random</code> for a password-reset link or a session id. They do not know it is <strong>predictable</strong>, so the token can be guessed.</p></div>
</div>

<div class="proof"><b>All from a tutorial</b> Exposed admin endpoints (Spring Boot Actuator), a superuser database account, front-end-only validation: the list goes on, and every item is somebody's normal Tuesday.</div>

---

## What it should have been

<p class="muted">The last three, done with intent.</p>

<div class="columns3">
<div class="card neon"><h3>The Dockerfile</h3><p>Pin the base image <strong>by digest</strong>, run as a <strong>non-root</strong> user, apply a read-only root filesystem and dropped capabilities at run time, keep <strong>secrets out of build args</strong> (inject at run time), and scan the image.</p></div>
<div class="card neon"><h3>Serialization</h3><p>Use a <strong>data-only format</strong> (JSON) and validate the shape against a schema. Never deserialize untrusted input into objects: disable polymorphic typing, and avoid native serialization and <code>pickle</code>.</p></div>
<div class="card neon"><h3>Tokens</h3><p>Use a <strong>cryptographically secure</strong> source (<code>secrets</code> in Python, <code>SecureRandom</code> in Java) for ids, reset links, and OTPs. Make them long, single-use, and expiring.</p></div>
</div>

<div class="proof"><b>The through-line</b> Every fix is one of the eight principles applied: least privilege, secure by default, validate at the boundary, never roll your own crypto.</div>

---

## How credentials and information actually flow

<p class="muted">Trace one login through the system they built, and follow where the token and the personal data go.</p>

<div class="columns">
<div class="card"><h3>The token's journey</h3><ul><li>The browser gets the JWT and stores it in <strong>localStorage</strong>, readable by any script on the page</li><li>It is sent to every service; some trust it without fully checking signature, expiry, and audience</li><li>The token and the user's email land in the <strong>logs</strong>, in plaintext, shipped to a central store</li></ul></div>
<div class="card"><h3>The secrets' journey</h3><ul><li>A service opens the database with an <strong>admin</strong> connection string from <code>.env</code></li><li>A third-party API key sits in the front-end bundle or a shared config map</li><li>The same <code>.env</code> is copied across dev, test, and prod</li></ul></div>
</div>

<div class="proof"><b>Every copy is a target</b> The same credentials and personal data pass, readable, through the browser, the network, the config, and the logs. Each is a copy an attacker can take.</div>

---

## The hard reality of enterprise development

<p class="muted">This team is competent and shipping on time. And the system has a readable, long-lived token, secrets spread through <code>.env</code>, unvetted dependencies, and personal data in the logs, all at once.</p>

<div class="columns">
<div class="card amber"><h3>Why it happens</h3><p>Security is not in the graduation syllabus. The libraries hide the details behind one function call. And there is no specialist to ask. A reasonable-looking default at every step adds up to an insecure system, with no one moment where anyone did something obviously wrong.</p></div>
<div class="card neon"><h3>What this chapter does</h3><p>Give the whole team the security lens: what a JWT actually packages, what belongs in <code>.env</code> and what does not, how to vet a dependency, and where each standard choice leaves a gap, so they can see it and close it themselves.</p></div>
</div>

<div class="proof"><b>The point</b> You do not need a security specialist on every line. You need the whole team to understand what their standard tools actually do.</div>

---

## Security is a quality attribute

<div class="columns">
<div class="card amber"><h3>Not a feature you add</h3><p>You cannot bolt it on at the end, any more than reliability. Vulnerabilities are created continuously, in a library choice, a query, an error handler.</p></div>
<div class="card"><h3>Continuous and shared</h3><p>Applied in every commit, reviewed in every design. One pasted SQL string undoes a perfect architecture; one "trust the network" undoes perfect code.</p></div>
</div>

<div class="proof"><b>The mature team</b> Security lives in the Definition of Done (validated, authorized, no secret, masked, tested), a security champion per squad, and a shift-left pipeline that makes the checks fast and automatic.</div>

---

## Two disciplines, one job

<div class="columns3">
<div class="card"><h3>Architect designs</h3><p>Threat modeling, boundary definition, standards, and the guardrails a feature is built inside. Decides <strong>what secure means here</strong>.</p></div>
<div class="card neon"><h3>Engineer builds</h3><p>Secure coding, defensive implementation, and hard guardrails in every line. Decides <strong>whether the code is secure or is not</strong>.</p></div>
<div class="card amber"><h3>Owned jointly</h3><p>A <strong>security champion</strong> in each squad, a shared <strong>Definition of Done</strong>, and checks <strong>shifted left</strong> into the pipeline so they are fast and automatic.</p></div>
</div>

<div class="proof"><b>The seam</b> A defensible design implemented carelessly is not secure; careful code inside an indefensible design is not secure. The layer is the contract, and it fails where one role assumes the other has it.</div>

---

## The principles every control is an instance of

<div class="columns">
<div class="card"><ul><li><strong>Least privilege</strong>: the minimum access, so a breach is contained</li><li><strong>Zero trust</strong>: never trust by location; prove it every time</li><li><strong>Defense in depth</strong>: layer controls so one failure is caught</li><li><strong>Fail secure</strong>: on error, deny, never fall through to allow</li></ul></div>
<div class="card neon"><ul><li><strong>Complete mediation</strong>: check authority on every access</li><li><strong>Secure by default</strong>: the safe config is the default config</li><li><strong>Separation of duties</strong>: no one actor completes a sensitive action alone</li><li><strong>Never roll your own crypto</strong>: use vetted libraries</li></ul></div>
</div>

<div class="proof"><b>Learn them once</b> Every specific defense in the modules ahead is one of these principles, applied to one surface.</div>

---

## Principle 1 &middot; Least privilege

<p class="muted">Give every user, service, and process the minimum access it needs to do its job, and nothing more.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Minimum access</span><span class="chip">Grant explicitly, deny by default</span><span class="chip">Contain the blast radius</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>Something will be compromised eventually. Least privilege decides how far the damage spreads: a stolen credential that can only read one table is a very different day from one that can drop the database.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>The read path uses a database account that cannot write; the enrichment worker cannot delete; a token carries only the scopes its caller needs. Nothing holds power it never uses.</p></div>
</div>

<div class="proof"><b>Remember</b> Assume breach. The question is not whether a component is compromised, but how far the attacker gets when it is.</div>

---

## Principle 2 &middot; Zero trust

<p class="muted">Never grant trust based on location. "Inside the network" or "another one of our services" is not a reason to skip authentication.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Never trust by location</span><span class="chip">Verify every request</span><span class="chip">No trusted interior</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>The old model of a hard perimeter and a soft, trusted interior fails the moment an attacker gets one foothold inside, because everything internal then trusts them. A flat trusted network turns a small breach into a total one.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>Service-to-service calls authenticate with mutual TLS; every request proves who it is and what it may do, every time, whether it came from the internet or the next pod over.</p></div>
</div>

<div class="proof"><b>Remember</b> Never trust, always verify. Trust is earned per request, not granted by address.</div>

---

## Principle 3 &middot; Defense in depth

<p class="muted">Assume any single control can fail or be bypassed, and layer independent controls so a failure in one is caught by the next.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Layer independent controls</span><span class="chip">Assume one fails</span><span class="chip">No single point of defense</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>No control is perfect: a validator has a gap, a library has a bug, a config drifts. Independent layers mean one, or even two, can fail and the system is still safe.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>SQL injection is stopped three ways at once: input validation at the edge, a parameterized query at the database, and a least-privilege database account. Two can fail and you are still protected.</p></div>
</div>

<div class="proof"><b>Remember</b> No single control is enough. Stack independent ones, so a gap is never a breach.</div>

---

## Principle 4 &middot; Fail secure

<p class="muted">When something goes wrong, deny by default. Also called "fail closed."</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Deny on error</span><span class="chip">Fail closed, not open</span><span class="chip">An outage locks, not unlocks</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>The insecure opposite, "fail open," is a classic breach source: an outage in the auth service that lets requests through removes the doors instead of locking them. An error must never become an accidental "allow."</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>An authorization check that throws an exception results in a rejection, never a pass-through. If the token store is unreachable, the request is denied, not waved in.</p></div>
</div>

<div class="proof"><b>Remember</b> On error, deny. A failure should lock the doors, not remove them.</div>

---

## Principle 5 &middot; Complete mediation

<p class="muted">Check authority on every access, not once at login and then cache "allowed" forever.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Check every access</span><span class="chip">No cached "allowed"</span><span class="chip">Revocation is immediate</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>Permissions change. A user removed from a team, or a token revoked after a leak, must lose access on the very next request, not whenever a cached decision happens to expire.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>Object-level authorization runs on every request, tokens are short-lived, and a revocation list is checked, so a permission taken away a minute ago is gone now.</p></div>
</div>

<div class="proof"><b>Remember</b> Every access, every time. Authority is a question you ask on each request, not once.</div>

---

## Principle 6 &middot; Secure by default

<p class="muted">The configuration you get without doing anything special is the safe one.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Safe out of the box</span><span class="chip">Opt out of safety, never into it</span><span class="chip">Do not rely on remembering</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>Security that depends on someone remembering to turn it on will eventually be off. The safe path has to be the path of least resistance, or delivery pressure will route around it.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>Encryption is on, ports are closed, verbose errors are off, and the storage bucket is private in the infrastructure code by default, so a new environment is born locked down, not open.</p></div>
</div>

<div class="proof"><b>Remember</b> The default is the safe one. Make the secure choice the one you get for free.</div>

---

## Principle 7 &middot; Separation of duties

<p class="muted">No single person or component can complete a sensitive action alone.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Two hands, not one</span><span class="chip">Split the power</span><span class="chip">A second approver</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>It limits both honest mistakes and deliberate abuse: one compromised account, or one bad actor, cannot cause the worst outcome without a second, independent approval.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>A deploy to production or a bulk data export needs a second approver; the person who writes a change is not the only one who can ship it.</p></div>
</div>

<div class="proof"><b>Remember</b> Two keys for the vault. The most sensitive actions take more than one hand.</div>

---

## Principle 8 &middot; Never roll your own crypto

<p class="muted">Use vetted, standard libraries, and let them make the hard choices.</p>

<div class="chips"><span class="tag">key aspects</span><span class="chip">Use vetted libraries</span><span class="chip">Standard algorithms only</span><span class="chip">Mistakes are invisible and fatal</span></div>

<div class="columns">
<div class="card"><h3>Why it matters</h3><p>Cryptography is a specialist field where subtle mistakes are invisible in testing and fatal in production. A home-made cipher, token, or hash scheme looks fine and is broken.</p></div>
<div class="card neon"><h3>On reviews-insight</h3><p>Field encryption uses the <code>cryptography</code> package (or libsodium), passwords use bcrypt or argon2, and tokens use a standard JWT library. Nothing hand-built stands between data and an attacker.</p></div>
</div>

<div class="proof"><b>Remember</b> Home-made crypto is a vulnerability, not an achievement. Stand on libraries the world has reviewed.</div>

---

## The attack surface: top vulnerabilities, outside in

<p class="muted">Defense in depth means a tier of security at every layer, from the UI the user touches down through the application to the data and the OS. Here are the top vulnerabilities at each layer, and the tier of control that answers them.</p>

| Layer (outside in) | Top vulnerabilities | Security tier (the control) |
| --- | --- | --- |
| Client / UI | XSS, CSRF, clickjacking, secrets in the browser | output encoding, CSP, SameSite cookies |
| Network / transport | weak or missing TLS, man-in-the-middle, DDoS | TLS 1.3, HSTS, rate limiting |
| Gateway / edge | no WAF, SSRF, unthrottled abuse | API gateway, WAF, egress control |
| Identity / session | broken authentication, session hijacking, no MFA | OAuth/OIDC, MFA, secure cookies |
| Access control | broken access control, BOLA, privilege escalation | object-level authz, least privilege |
| Application / API | injection, insecure deserialization, mass assignment | validation, parameterization, allowlist binding |
| Data / storage | data exposure, weak crypto, PII leakage | encryption at rest, a KMS, masking |
| OS / host / container | misconfiguration, unpatched components, root, escape | hardening (CIS), patching, non-root |

<div class="proof"><b>Cutting across every layer</b> Secrets in code, vulnerable dependencies, security misconfiguration, and logging and monitoring failures are not one layer's problem; they appear at all of them.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">The top vulnerabilities, one by one</span>

## From the UI, down to the data and the OS

<p class="muted">One vulnerability per slide: what it is, how the attack works, and the tier of control that stops it. We travel the same outside-in path, from the browser to the operating system.</p>

---

## Cross-Site Scripting (XSS)

<span class="tag2">client / ui</span>

<p class="muted">Untrusted input rendered into a page as executable script, so an attacker's code runs in the victim's browser.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A review body containing a <code>&lt;script&gt;</code> tag is stored, then later rendered raw into the page. Every viewer runs the attacker's code, which can read their session or act as them.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Encode output for the HTML context, set a Content Security Policy, and keep tokens in <code>HttpOnly</code> cookies so script cannot read them.</p></div>
</div>

<div class="proof"><b>OWASP injection family</b> Stored XSS is the worst kind: it hits every viewer, not just the attacker.</div>

---

## Cross-Site Request Forgery (CSRF)

<span class="tag2">client / ui</span>

<p class="muted">A malicious site makes the victim's browser send a state-changing request to your app, riding their logged-in session.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A hidden form on another site posts to your "delete review" endpoint. The browser attaches the victim's cookie automatically, so the request looks genuine.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Require an anti-CSRF token on state-changing requests, and set <code>SameSite</code> cookies so the session is not sent on cross-site requests.</p></div>
</div>

<div class="proof"><b>Impact</b> Actions taken as the victim, without their knowledge or intent.</div>

---

## Clickjacking

<span class="tag2">client / ui</span>

<p class="muted">Your page is loaded invisibly in a frame on an attacker's site, and the victim is tricked into clicking a real control they cannot see.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A transparent iframe of your "confirm" button is layered over a decoy the victim wants to click. Their click lands on your control instead.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Send <code>X-Frame-Options</code> or a CSP <code>frame-ancestors</code> directive so other origins cannot frame the page.</p></div>
</div>

<div class="proof"><b>No code flaw needed</b> A UI-layer attack that succeeds purely on missing response headers.</div>

---

## Sensitive data in the client

<span class="tag2">client / ui</span>

<p class="muted">Secrets or personal data placed where the browser or a mobile app can read it: local storage, a hidden field, an API key in the JavaScript.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>An API key shipped inside the frontend bundle is extracted by anyone who opens the developer tools, and now every caller has it.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Keep secrets on the server, store tokens in <code>HttpOnly</code> cookies, and send the client only the data it actually needs.</p></div>
</div>

<div class="proof"><b>The rule</b> The client is fully visible to the user. Treat everything in it as public.</div>

---

## Man-in-the-middle (weak TLS)

<span class="tag2">network / transport</span>

<p class="muted">An attacker on the network path reads or alters traffic that is not properly encrypted.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A call over plain HTTP, or with certificate verification turned off, is intercepted on the wire and its contents read or changed in flight.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>TLS 1.3 everywhere, including between internal services, plus HSTS. Never disable certificate verification to "make it work."</p></div>
</div>

<div class="proof"><b>OWASP Cryptographic Failures</b> <code>verify=False</code> is a one-line breach.</div>

---

## Denial of service (DoS and DDoS)

<span class="tag2">network / edge</span>

<p class="muted">Overwhelming the service with traffic or expensive requests so real users cannot be served.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A flood of requests, or a few very expensive ones (a huge payload, a deeply nested query), exhausts the workers or the database.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Rate limiting and throttling at the gateway, payload size limits, and load shedding, with upstream DDoS protection for volume.</p></div>
</div>

<div class="proof"><b>Availability is security too</b> The attacker's lever is cost asymmetry: cheap to send, expensive to serve.</div>

---

## Server-Side Request Forgery (SSRF)

<span class="tag2">gateway / services</span>

<p class="muted">Tricking your server into making a request to an address the attacker chooses, usually an internal one.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A "fetch image from URL" feature is handed <code>http://169.254.169.254/...</code> to read cloud metadata and steal the instance's credentials.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Validate the outbound destination against an allowlist, block private and loopback addresses, and check the resolved IP to defeat DNS rebinding.</p></div>
</div>

<div class="proof"><b>OWASP A10</b> The server becomes the attacker's proxy into your own network.</div>

---

## Broken authentication

<span class="tag2">identity / session</span>

<p class="muted">Weak proof of who the caller is: guessable passwords, no lockout, no multi-factor, tokens that never expire.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>Credential stuffing with leaked password lists, or brute force against a login with no rate limit and no second factor, walks straight in.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Salted password hashing (bcrypt or argon2), multi-factor for sensitive actions, lockout and rate limiting, and standard protocols (OAuth, OIDC).</p></div>
</div>

<div class="proof"><b>OWASP A07</b> The front door, and the most attacked surface you have.</div>

---

## Session hijacking

<span class="tag2">identity / session</span>

<p class="muted">Stealing or forging a session token to act as another user, skipping authentication entirely.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A token read from insecure storage or an unencrypted connection is replayed, or a session id fixed by the attacker before login is reused after.</p></div>
<div class="card neon"><h3>How you stop it</h3><p><code>HttpOnly</code>, <code>Secure</code>, <code>SameSite</code> cookies, short-lived tokens with rotation, a new session id on login, and clean revocation.</p></div>
</div>

<div class="proof"><b>Impact</b> A stolen session is the user, with no password needed.</div>

---

## Broken access control

<span class="tag2">access control</span>

<p class="muted">A user can act outside their intended permissions: reach an admin page, edit another user's data, or call a function they should not.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A normal user changes a URL from <code>/user</code> to <code>/admin</code>, or replays a privileged API call, and the server does not re-check authority.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Enforce authorization on every request at a policy enforcement point, deny by default, and cover it with tests.</p></div>
</div>

<div class="proof"><b>OWASP A01</b> The number one risk on the web list.</div>

---

## Broken Object Level Authorization (BOLA)

<span class="tag2">access control</span>

<p class="muted">Also called insecure direct object reference: an endpoint returns an object to anyone who names its id, without checking they own it.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p><code>GET /v1/reviews/42</code> returns review 42 to any logged-in caller, so an attacker enumerates every other user's data by changing the id.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Authorize the specific object (does this caller own it), and return <code>404</code> not <code>403</code> so ids cannot be enumerated.</p></div>
</div>

<div class="proof"><b>OWASP API number one</b> "Logged in" is not "allowed."</div>

---

## Privilege escalation

<span class="tag2">access control</span>

<p class="muted">Gaining rights beyond those granted: moving from user to admin, or from one tenant into another's data.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A mass-assignment body sets <code>is_admin: true</code>, or a missing tenant check lets one tenant read another's records.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Least privilege, server-controlled roles (never from the request body), and object- and function-level authorization checks.</p></div>
</div>

<div class="proof"><b>Impact</b> The step that turns a small foothold into a full compromise.</div>

---

## Injection

<span class="tag2">application / api</span>

<p class="muted">Untrusted input treated as code or a command: SQL, shell, LDAP, or a file path.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A crafted <code>product_id</code> of <code>x' OR '1'='1</code> rewrites a string-built query to return every row; a filename with <code>; rm -rf</code> runs a second command.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Keep data as data: parameterized queries, argument lists (no shell), validated inputs, and safe path handling.</p></div>
</div>

<div class="proof"><b>OWASP A03</b> Decades old, and still found everywhere.</div>

---

## Insecure deserialization

<span class="tag2">application / api</span>

<p class="muted">Rebuilding an object from untrusted bytes in a way that can execute code during the load itself.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p><code>pickle.loads</code> on a cache entry or queue message the attacker controls runs their code before you ever look at the result.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Use a data-only format (JSON) and validate the shape against a schema. Never unpickle bytes from outside your program.</p></div>
</div>

<div class="proof"><b>OWASP Software and Data Integrity Failures</b> A quiet path to remote code execution.</div>

---

## Mass assignment

<span class="tag2">application / api</span>

<p class="muted">Binding a whole request body onto a model, so the caller can set fields they were never meant to control.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A create request adds <code>"is_approved": true</code> or <code>"owner_id": victim</code>, and the server accepts them because it binds every field in the body.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Bind only the fields the caller may set. The server assigns owner, roles, and status from trusted sources, never from the body.</p></div>
</div>

<div class="proof"><b>OWASP API</b> The body is untrusted, field by field.</div>

---

## Sensitive data exposure

<span class="tag2">data / storage</span>

<p class="muted">Personal, financial, or secret data readable because it is unencrypted, weakly encrypted, or leaked into logs.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A stolen disk or backup yields plaintext PII; or an exception logs a full record with a card number in it, and the log is shipped onward.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Encrypt at rest and in transit with a KMS and strong algorithms, classify the data, and mask it before every log and prompt.</p></div>
</div>

<div class="proof"><b>OWASP Cryptographic Failures</b> The data is the prize; protect it in every state.</div>

---

## Security misconfiguration

<span class="tag2">cross-cutting / infra</span>

<p class="muted">Insecure defaults left in place: debug mode on, verbose errors, open ports, default credentials, over-permissive cloud settings.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A public storage bucket, an exposed admin console, or a stack trace that reveals internals hands the attacker a free map of the system.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Secure by default, hardening baselines (CIS), least-exposure configuration, and infrastructure-as-code that ships safe settings.</p></div>
</div>

<div class="proof"><b>OWASP A05</b> The most common finding, and among the easiest to avoid.</div>

---

## Vulnerable and outdated components

<span class="tag2">cross-cutting / supply chain</span>

<p class="muted">A dependency, base image, or library with a known vulnerability, or one that has been tampered with.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>An unpatched library with a public exploit, or a typosquatted or compromised package pulled into the build, ships the flaw straight to production.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Pin and lock, scan dependencies in CI, verify sources, keep an SBOM, and patch on a schedule.</p></div>
</div>

<div class="proof"><b>OWASP A06</b> Most of your application is code you did not write.</div>

---

## Insecure runtime (root and container escape)

<span class="tag2">os / host / container</span>

<p class="muted">A workload that runs with more privilege than it needs, so an exploit at runtime can own the host.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A container running as root with extra Linux capabilities is broken out of, reaching the node and the other workloads on it.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Non-root user, read-only root filesystem, dropped capabilities, network policies, and a patched, minimal base image.</p></div>
</div>

<div class="proof"><b>Least privilege at runtime</b> Contain the blast radius of any exploit to a powerless account.</div>

---

## Secrets in code

<span class="tag2">cross-cutting / config</span>

<p class="muted">An API key, password, or token committed to source, or written into a log.</p>

<div class="columns">
<div class="card"><h3>How the attack works</h3><p>A key hard-coded in a config file lives in the git history forever, or is copied into a log that is later shipped to a third party.</p></div>
<div class="card neon"><h3>How you stop it</h3><p>Load secrets from the environment or a secrets manager, scan for them in CI and pre-commit, and rotate on any leak.</p></div>
</div>

<div class="proof"><b>Once exposed, assume compromised</b> A secret in history or a log must be rotated.</div>

---

## The maps you audit against

<div class="columns3">
<div class="card"><h3>OWASP Top 10</h3><p>The critical web risks: Broken Access Control, Injection, Cryptographic Failures, Misconfiguration, SSRF, and more.</p></div>
<div class="card neon"><h3>API and LLM Top 10</h3><p>API risks led by <strong>BOLA</strong> (broken object-level authorization); the LLM list led by <strong>prompt injection</strong>.</p></div>
<div class="card amber"><h3>ASVS and STRIDE</h3><p><strong>ASVS</strong>: verification requirements to test against. <strong>STRIDE</strong>: a method to threat-model a design.</p></div>
</div>

<div class="proof"><b>Not academic</b> These are the checklists a professional runs over their own code and a tool's. Each layer below points at the part of the map it defends.</div>

---

## Framework &middot; OWASP Top 10

<p class="muted">The ten most critical web application risks, maintained by the Open Worldwide Application Security Project and updated periodically. The baseline every web engineer is expected to know.</p>

<div class="columns">
<div class="card">

<span class="tag2">the list</span>
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
</div>
<div class="card neon">

<span class="tag2">continued</span>
6. Vulnerable and Outdated Components
7. Identification and Authentication Failures
8. Software and Data Integrity Failures
9. Security Logging and Monitoring Failures
10. Server-Side Request Forgery (SSRF)
</div>
</div>

<div class="proof"><b>How you use it</b> A checklist for design and code review. If a change touches one of these areas, the review asks the matching question.</div>

---

## Framework &middot; OWASP API Security Top 10

<p class="muted">The API-specific list, because most enterprise services are APIs and their failures differ from classic web apps.</p>

<div class="columns">
<div class="card"><h3>What leads it</h3><p><strong>Broken Object Level Authorization (BOLA)</strong> is number one: an endpoint that returns object 42 to anyone who asks, without checking they may see it. Then broken authentication, and broken object-property-level authorization (mass assignment and excessive data exposure).</p></div>
<div class="card neon"><h3>How you use it</h3><p>Audit each endpoint, not just the app as a whole: does it authorize the specific object, limit which fields go in and out, and cap resource consumption per caller?</p></div>
</div>

<div class="proof"><b>Why separate from the web Top 10</b> APIs have no browser to lean on and expose objects directly, so authorization at the object level is where they break.</div>

---

## Framework &middot; OWASP Top 10 for LLM Applications

<p class="muted">The risk map for applications that call or embed large language models, the newest and fastest-moving surface.</p>

<div class="columns">
<div class="card"><h3>What leads it</h3><p><strong>Prompt Injection</strong> is number one: untrusted content becoming instructions to the model. Then insecure output handling, sensitive information disclosure, excessive agency, and model supply chain.</p></div>
<div class="card neon"><h3>How you use it</h3><p>Treat the model as an untrusted boundary: frame external content as data, validate the output against a schema, keep secrets and raw PII out of prompts, and limit what the model may reach.</p></div>
</div>

<div class="proof"><b>The theme</b> The classic injection and least-privilege lessons, moved to the model boundary. Same principles, new surface.</div>

---

## Framework &middot; OWASP ASVS

<p class="muted">The Application Security Verification Standard. Not a list of risks but a list of <strong>requirements</strong> to build and test against.</p>

<div class="columns">
<div class="card"><h3>What it is</h3><p>Hundreds of concrete, testable requirements across authentication, session management, access control, cryptography, and more, organized into three levels by how sensitive the application is.</p></div>
<div class="card neon"><h3>How you use it</h3><p>Pick the level that matches your risk profile, turn its requirements into a checklist and a set of tests, and verify against them. It answers "what does secure actually require here."</p></div>
</div>

<div class="proof"><b>Top 10 vs ASVS</b> The Top 10 tells you what commonly goes wrong; ASVS tells you what to require and prove so it does not.</div>

---

## ASVS: ten requirements to verify

<p class="muted">ASVS groups its requirements into chapters (V1 to V14) and three levels of rigor. Ten of the most important, phrased as things you verify:</p>

<div class="columns">
<div class="card">

1. A **threat model** and secure design exist (V1)
2. **Authentication** is strong: salted-hashed credentials, MFA (V2)
3. **Sessions** are server-managed, rotated, and revocable (V3)
4. **Access control** is enforced server-side and denies by default (V4)
5. **Input** is validated and **output** encoded for its context (V5)
</div>
<div class="card neon">

6. **Stored crypto** is strong and standard, with managed keys (V6)
7. **Errors** fail safely and **security events** are logged, no data leaked (V7)
8. **Data** is classified, minimized, and protected in transit and at rest (V8, V9)
9. Known attacks are defended: **injection, deserialization, SSRF** (V5, V10)
10. **Configuration** is secure and dependencies are vetted and patched (V14)
</div>
</div>

<div class="proof"><b>How you use it</b> Pick the level that matches your risk, turn these into a checklist and tests, and verify each on every release.</div>

---

## Framework &middot; STRIDE

<p class="muted">A threat-modeling method that finds threats in a design before any code is written, by asking six questions of each part of the system.</p>

<div class="columns">
<div class="card">

| Letter | Threat | Violates |
| --- | --- | --- |
| S | Spoofing | authenticity |
| T | Tampering | integrity |
| R | Repudiation | non-repudiation |
| I | Info disclosure | confidentiality |
| D | Denial of service | availability |
| E | Elevation | authorization |
</div>
<div class="card neon"><h3>How you use it</h3><p>Draw the data flow and its trust boundaries, then walk each element and each crossing asking the six questions. Every threat you find becomes a control and, later, a test.</p></div>
</div>

<div class="proof"><b>Where it fits</b> This is the tool for "Insecure Design," a flaw you cannot patch later because it is in the shape of the system.</div>

---

## Framework &middot; PASTA

<p class="muted">Process for Attack Simulation and Threat Analysis: a heavier, risk-centric threat-modeling process that ties technical threats to business impact.</p>

<div class="columns">
<div class="card"><h3>What it is</h3><p>Seven stages, from defining business objectives, through decomposing the application and analyzing threats and vulnerabilities, to simulating attacks and scoring the residual business risk.</p></div>
<div class="card neon"><h3>When to reach for it</h3><p>On high-stakes systems where you must prioritize by business risk and justify security spend, not just enumerate threats. STRIDE is faster for everyday design review; PASTA is deeper for the crown jewels.</p></div>
</div>

<div class="proof"><b>The difference</b> STRIDE asks "what can go wrong here." PASTA asks "what is worth an attacker's effort, and what would it cost us."</div>

---

## Guidance &middot; NIST and CIS

<p class="muted">Where the OWASP lists cover application risks, these cover the systems and infrastructure underneath: how a server, container, or cloud account should be configured.</p>

<div class="columns">
<div class="card"><h3>NIST</h3><p>US standards body. Widely used references include the Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover) and the SP 800-53 control catalog, the vocabulary many compliance programs are built on.</p></div>
<div class="card neon"><h3>CIS Benchmarks</h3><p>Concrete, step-by-step secure-configuration guides for operating systems, containers, and cloud services. Directly actionable: "set this flag, close this port," and the baseline for runtime hardening.</p></div>
</div>

<div class="proof"><b>How you use them</b> NIST for the framework and controls language; CIS for the hands-on hardening checklist your infrastructure is measured against.</div>

---

## Guidance &middot; ISO/IEC 27001 and 27002

<p class="muted">The international standards for managing information security as a governed system, and the origin of the older name ISO 17799.</p>

<div class="columns">
<div class="card"><h3>ISO/IEC 27001</h3><p>The certifiable standard for an Information Security Management System (ISMS): the risk assessment, roles, policies, and continual improvement an organization runs. The certificate is what many enterprise customers and regulators require.</p></div>
<div class="card neon"><h3>ISO/IEC 27002 <span class="muted">(formerly ISO 17799)</span></h3><p>The companion code of practice: a catalog of security controls with implementation guidance. <strong>ISO 17799</strong> was its original number, renumbered into the 27000 family, so a reference to 17799 means these controls.</p></div>
</div>

<div class="proof"><b>How you use it</b> 27001 is the management frame (are we running security as a governed process); 27002 is the controls you implement and audit against. Where NIST and CIS are common in the US, ISO 27001 is the global certification most enterprises are asked to hold.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">The layers &middot; blueprint and realization</span>

## Seven modules, from the user to the data

<p class="muted">Module 1 is the mindset the opening established. Modules 2 to 7 are the layers, each co-owned: the architect designs the frame (the blueprint), the engineer builds the implementation (the realization). We read both halves together.</p>

---

## Module 1 &middot; Foundational mindset and shared ownership

<div class="split">
<div class="own arch"><span class="tag2">architect designs</span><h3>Blueprint</h3><ul><li>The security <strong>risk profile</strong>: compliance targets, data sensitivity tiers, exposure surface</li><li>Non-negotiable <strong>guardrails</strong> and architectural constraints</li></ul></div>
<div class="own eng"><span class="tag2">engineer builds</span><h3>Realization</h3><ul><li>Security in the <strong>Definition of Done</strong></li><li><strong>Defensive programming</strong> and continuous secure-code analysis</li></ul></div>
</div>

<div class="proof"><b>Owned jointly</b> A security champion per squad, shifted left. This is the mindset from the opening; it is Module 1, and Modules 2 to 7 apply it layer by layer.</div>

---

## Module 2 &middot; Identity and access

<div class="split">
<div class="own arch"><span class="tag2">architect designs</span><h3>Blueprint</h3><ul><li>Protocols: OAuth 2.1, OIDC, SAML</li><li>Tokens: JWT vs opaque vs short-lived + refresh</li><li>Model: RBAC, ABAC, or ReBAC</li><li>Zero trust: segmentation, mTLS</li></ul></div>
<div class="own eng"><span class="tag2">engineer builds</span><h3>Realization</h3><ul><li>Validate signature, exp, aud, iss (fail closed)</li><li>Cache JWKS; reject <code>alg:none</code></li><li>Object-level authz at a policy enforcement point</li><li>HttpOnly/Secure/SameSite cookies; revocation; MFA</li></ul></div>
</div>

<div class="proof"><b>The number one risk</b> Broken access control. "Logged in" is not "allowed"; authorize the specific object, every request.</div>

---

## Demo &middot; the BOLA fix

<span class="pill">broken object-level authorization</span>

```python
# Broken: any logged-in caller gets any review.
def get_review(review_id, user):
    return store.get(review_id)

# Fixed: authorize THIS object, and fail secure.
def get_review(review_id, user):
    review = store.get(review_id)
    if review is None or review.owner_id != user.id:
        raise HTTPException(status_code=404)   # do not even reveal it exists
    return review
```

<div class="proof"><b>What it means</b> The check is per object, not per session, and it returns 404 (not 403) so an attacker cannot enumerate which reviews exist.</div>

---

## Module 3 &middot; Data protection and cryptography

<div class="split">
<div class="own arch"><span class="tag2">architect designs</span><h3>Blueprint</h3><ul><li>Data classification: public, internal, confidential, regulated</li><li>Key management: lifecycle, HSM/KMS, envelope encryption</li><li>Residency, retention, multi-tenant isolation</li></ul></div>
<div class="own eng"><span class="tag2">engineer builds</span><h3>Realization</h3><ul><li>TLS 1.3 in transit; field-level encryption at rest</li><li>AEAD, correct IV/nonce/salt; bcrypt for passwords</li><li>Mask PII before logs and prompts</li></ul></div>
</div>

<div class="proof"><b>Know the difference</b> Hashing (one way, for passwords), encryption (reversible with a key), and encoding (not security at all). Confusing them is a classic finding.</div>

---

## Concept &middot; envelope encryption

<span class="pill">key management</span>

<div class="flow">
<span class="step">Master key (in the KMS)</span><span class="arrow">&rarr;</span>
<span class="step hot">encrypts a data key</span><span class="arrow">&rarr;</span>
<span class="step">data key encrypts the field</span>
</div>

```python
data_key = fetch_data_key_from_kms()        # fetched at runtime, never in code
token = Fernet(data_key).encrypt(value.encode("utf-8"))   # AEAD, safe defaults
```

<div class="proof"><b>Why two keys</b> The data never meets the master key, and rotating the master key re-wraps the data keys without re-encrypting terabytes of data.</div>

---

## Module 4 &middot; API and system surface

<div class="split">
<div class="own arch"><span class="tag2">architect designs</span><h3>Blueprint</h3><ul><li>API gateway, rate-limit tiers, WAF</li><li>Schema-first specs (OpenAPI, GraphQL)</li><li>Signed webhooks, sandboxing, egress control</li></ul></div>
<div class="own eng"><span class="tag2">engineer builds</span><h3>Realization</h3><ul><li>Injection, BOLA, SSRF, mass assignment defenses</li><li>Context-aware encoding; safe deserialization</li><li>Rate-limit middleware, payload limits, breakers</li></ul></div>
</div>

<div class="proof"><b>One shape of defense</b> Keep data as data. Parameterize queries, pass shell args as a list, bind only allowed fields, never unpickle untrusted bytes.</div>

---

## Demo &middot; injection and mass assignment

<span class="pill">keep data as data</span>

```python
# Injection: parameterize; the driver keeps the value as data, never SQL.
cursor.execute("SELECT * FROM reviews WHERE product_id = %s", (product_id,))

# Mass assignment: bind only the fields the caller may set.
review = Review(product_id=body["product_id"], rating=body["rating"])
# tenant_id, author_id, is_approved come from the server, never the body
```

<div class="proof"><b>What it means</b> A crafted <code>product_id</code> cannot rewrite the query, and a crafted body cannot set <code>is_approved: true</code> or another tenant's id.</div>

---

## Module 5 &middot; Threat modeling with STRIDE

<div class="columns">
<div class="card"><h3>Model before you code</h3><p>Draw the trust boundaries and data flow, then ask six questions of each part. "Insecure Design" is a flaw you cannot patch later.</p></div>
<div class="card neon">

| Letter | Threat | Violates |
| --- | --- | --- |
| S | Spoofing | authenticity |
| T | Tampering | integrity |
| R | Repudiation | non-repudiation |
| I | Info disclosure | confidentiality |
| D | Denial of service | availability |
| E | Elevation | authorization |
</div>
</div>

<div class="proof"><b>Patterns</b> Fail-secure defaults, defense in depth, blast-radius reduction, graceful degradation.</div>

---

## Demo &middot; a threat becomes a test

<span class="pill">translate STRIDE to abuse cases</span>

```python
def test_tampered_token_is_rejected(client):
    forged = make_token(alg="none", sub="attacker")   # T: tampering
    r = client.get("/v1/reviews/42", headers=auth(forged))
    assert r.status_code == 401

def test_cross_user_read_is_denied(client, user_b_token):
    r = client.get("/v1/reviews/owned-by-a", headers=auth(user_b_token))
    assert r.status_code == 404          # E: elevation, and no enumeration
```

<div class="proof"><b>What it means</b> Each STRIDE finding becomes a test that fails if the mitigation is ever removed. The design and the code are joined by the suite.</div>

---

## Module 6 &middot; Supply chain and infrastructure

<div class="split">
<div class="own arch"><span class="tag2">architect designs</span><h3>Blueprint</h3><ul><li>Policy-as-code: allowed images and registries</li><li>SBOM; library vetting</li><li>IaC governance: secure-by-default cloud</li></ul></div>
<div class="own eng"><span class="tag2">engineer builds</span><h3>Realization</h3><ul><li>CI scans: SAST, DAST, SCA, secret detection</li><li>Runtime secret injection (Vault, Secrets Manager)</li><li>Non-root, read-only, least-privilege containers</li></ul></div>
</div>

<div class="proof"><b>Most of your app is not yours</b> Your dependencies and their dependencies. Pin, lock, scan, and verify sources, on every build.</div>

---

## Demo &middot; scan the build, harden the runtime

<span class="pill">shift left</span>

```yaml
# CI: fail the build on a known-vulnerable dependency or a leaked secret
- run: pip-audit --strict
- run: trivy fs --scanners secret,vuln,misconfig --exit-code 1 .
```

```dockerfile
# Runtime: run as an unprivileged user, not root
RUN useradd --system appuser
USER appuser
# launched read-only, with all Linux capabilities dropped
```

<div class="proof"><b>What it means</b> A vulnerable pin or a hard-coded secret blocks the merge, and even an exploit at runtime lands in a powerless account.</div>

---

## Module 7 &middot; Observability and incident response

<div class="split">
<div class="own arch"><span class="tag2">architect designs</span><h3>Blueprint</h3><ul><li>Immutable, tamper-evident audit logs; WORM</li><li>Centralized telemetry into a SIEM</li><li>Runbooks; break-glass access</li></ul></div>
<div class="own eng"><span class="tag2">engineer builds</span><h3>Realization</h3><ul><li>Structured security events with a trace id</li><li>No secrets or raw PII in logs</li><li>Kill-switch feature flags; dynamic isolation</li></ul></div>
</div>

<div class="proof"><b>Close the loop</b> An attacker edits the logs first, so make them immutable. Every incident becomes a regression test, exactly like the Dependable chapter.</div>

---

## Demo &middot; security events and a kill switch

<span class="pill">detect and respond</span>

```python
security_log("authz_denied", trace_id=tid,
             user=mask_email(email), resource=review_id)   # no PII, correlated

if not flags.enabled("review_export"):     # flip in seconds, no deploy
    raise HTTPException(status_code=503)    # fail closed
```

<div class="proof"><b>What it means</b> A denial is a searchable, correlated event with nothing sensitive in it, and a compromised path is turned off instantly while the fix is prepared.</div>

---

<!-- _class: divider -->

<img class="brandmark" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Security testing and hardening</span>

## Find the weaknesses, then remove them

<p class="muted">Two disciplines that close the loop on everything so far. Testing proves where the defenses still have gaps; hardening shrinks the attack surface so there is less to defend. Both run continuously, and both belong in the pipeline.</p>

<div class="flow">
<span class="step">Test to find the gaps</span><span class="arrow">&rarr;</span>
<span class="step">Fix and add a regression test</span><span class="arrow">&rarr;</span>
<span class="step">Harden to reduce the surface</span>
</div>

<div class="proof"><b>The mindset</b> You do not become secure by hoping; you become secure by attacking your own system on purpose, and by removing everything an attacker could use.</div>

---

## Security testing: the toolbox

<p class="muted">A layered set of tools, each finding what the others miss. The acronyms, plainly:</p>

<div class="columns3">
<div class="card"><h3>Read the code</h3><ul><li><strong>SAST</strong>: static analysis of the source, in CI, before it runs</li><li><strong>SCA</strong>: scan dependencies for known CVEs and licenses</li><li><strong>Secret scanning</strong>: hard-coded keys and tokens</li></ul></div>
<div class="card neon"><h3>Attack the running app</h3><ul><li><strong>DAST</strong>: attack the deployed app from outside, in staging</li><li><strong>IAST</strong>: instrument the app during tests to see inside</li><li><strong>Fuzzing</strong>: flood it with malformed input to find crashes</li></ul></div>
<div class="card amber"><h3>Scan the surroundings</h3><ul><li><strong>Container and image</strong> scanning for CVEs</li><li><strong>IaC scanning</strong> for misconfigured infrastructure</li><li><strong>Abuse-case tests</strong>: your own STRIDE threats, as tests</li></ul></div>
</div>

<div class="proof"><b>Shift left</b> Run the fast ones (SAST, SCA, secret scan) on every commit; the slower ones (DAST, image scan) before release. Speed decides where each one lives.</div>

---

## Beyond the tools: people who attack

<p class="muted">Tools find the known patterns; skilled humans find the creative path through them. You need both.</p>

<div class="columns3">
<div class="card"><h3>Penetration testing</h3><p>A scoped, point-in-time expert attack that finds what scanners cannot. The output is a report of findings ranked by severity (CVSS).</p></div>
<div class="card neon"><h3>Bug bounty</h3><p>Continuous, crowd-sourced testing: you publish a scope and pay for valid findings, so coverage widens over time.</p></div>
<div class="card amber"><h3>Red, blue, purple team</h3><p>Red attacks, blue defends, and purple is the two working together to improve detection and response, not just find one hole.</p></div>
</div>

<div class="proof"><b>The fix loop</b> Every finding becomes a regression test that reproduces the exploit, then the fix, then validation against the original payload, so the same hole cannot reopen.</div>

---

## Hardening: shrink the attack surface

<p class="muted">The other half. Every feature, port, package, and account you do not need is one an attacker can use. Hardening removes them.</p>

<div class="columns">
<div class="card"><h3>Reduce and lock down</h3><ul><li><strong>Remove what is unused</strong>: features, endpoints, ports, packages, default accounts</li><li><strong>Secure baselines</strong>: CIS Benchmarks for OS, containers, and cloud; NIST controls</li><li><strong>Patch on a cadence</strong>: OS, base images, and dependencies kept current</li></ul></div>
<div class="card neon"><h3>Harden the runtime and network</h3><ul><li><strong>Runtime</strong>: non-root, read-only root filesystem, dropped capabilities, minimal base image, resource limits</li><li><strong>Network</strong>: segmentation, private services, least exposure, egress control</li><li><strong>Config</strong>: secure defaults, unused features off, no verbose errors</li></ul></div>
</div>

<div class="proof"><b>What hardening is</b> Least privilege and secure-by-default, applied to the whole stack. What is not there cannot be attacked.</div>

---

## Security in the pipeline

<p class="muted">Testing and hardening are not a phase at the end; they run at every stage, gating what moves forward.</p>

<div class="flow">
<span class="step">Commit</span><span class="arrow">&rarr;</span>
<span class="step hot">CI: SAST, SCA, secret scan</span><span class="arrow">&rarr;</span>
<span class="step hot">Build: image and IaC scan</span><span class="arrow">&rarr;</span>
<span class="step hot">Staging: DAST, pen test</span><span class="arrow">&rarr;</span>
<span class="step">Prod: runtime monitoring</span>
</div>

<div class="proof"><b>The gate</b> A failing scan blocks the merge, a failing image scan blocks the deploy, and a runtime alert triggers the response. The pipeline enforces what the chapter taught.</div>

---

## The build &middot; reviews-insight, hardened module by module

<div class="stats">
  <div class="stat"><b>404</b><span>cross-user read, not the data</span></div>
  <div class="stat"><b>0</b><span>secrets in code</span></div>
  <div class="stat"><b>CI</b><span>dep + secret scan gate</span></div>
  <div class="stat"><b>non-root</b><span>hardened container</span></div>
</div>

<div class="proof"><b>Proof, module by module</b> Object-level authz test, injection and mass-assignment blocked, secret scan clean, masked security logs, a dependency scan that fails a vulnerable pin, and a non-root container. The CI gate keeps it that way.</div>

---

## Hands-on workshops

<div class="columns">
<div class="card"><h3>1. STRIDE and code pair</h3><p><strong>Phase A (architect):</strong> from a diagram, draw trust boundaries and run STRIDE. <strong>Phase B (engineer):</strong> fix the BOLA and injection in a component, and turn two threats into tests.</p></div>
<div class="card neon"><h3>2. Break-the-build lab</h3><p>Try to slip subtle bugs (a hard-coded token, a vulnerable pin, a string-built query, a root container) past a CI pipeline, and see which control catches what, and what slips through.</p></div>
</div>

<div class="proof"><b>The lesson</b> No single tool catches everything; the human review in the Definition of Done catches what the machines cannot.</div>

---

## What we covered

<div class="columns">
<div class="card"><h3>Mindset and maps</h3><ul><li>Security is a quality attribute, co-owned</li><li>Eight principles; the shared-responsibility contract</li><li>OWASP Top 10, API and LLM, ASVS, STRIDE</li></ul></div>
<div class="card neon"><h3>The layers, proven</h3><ul><li>Identity, data and crypto, the API surface</li><li>Threat modeling, supply chain and runtime, detection</li><li>reviews-insight hardened, with a test for each</li></ul></div>
</div>

<div class="proof"><b>The review lens</b> Are boundaries and threats named; the caller authenticated and the object authorized; input validated, secrets out, data masked, the supply chain scanned, the runtime hardened, and security events watched? Blueprint and realization both yes.</div>

---

<!-- _class: lead -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Secure &middot; Complete</span>

# <span class="grad">Secure by design, and by execution.</span>

<p class="muted" style="font-size: 22px; max-width: 52ch; margin-top: 12px;">The architect designs a defensible frame, the engineer builds a bulletproof implementation, and the two are proven together. That is the only kind of secure that lasts.</p>

### <span class="brandlite">That completes the seven qualities. Next: the right libraries for Data Engineering and for AI.</span>
