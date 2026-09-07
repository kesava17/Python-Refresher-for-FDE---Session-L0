---
marp: true
size: 16:9
paginate: true
title: Artificial Neural Networks - An Introduction
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
.card h3 { margin-top: 0; }
.card p { margin: 5px 0 0; }
.card ul { margin: 4px 0 0; }

.pill { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--primary-600); background: var(--panel-cool); border: 1px solid var(--border); border-radius: 999px; padding: 3px 12px; margin-bottom: 8px; }

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

.era { display: grid; grid-template-columns: 92px 1fr; gap: 14px; align-items: center; background: var(--panel); border: 1px solid var(--border); border-left: 4px solid var(--primary); border-radius: 8px; padding: 8px 14px; margin: 6px 0; }
.era .yr { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 20px; color: var(--primary-600); }
.era:nth-child(3n+2) { border-left-color: var(--neon); }
.era:nth-child(3n+2) .yr { color: var(--neon-600); }
.era:nth-child(3n) { border-left-color: var(--accent); }
.era:nth-child(3n) .yr { color: #B45309; }
.era .what { font-size: 15px; color: var(--ink-soft); }

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
code { font-family: 'JetBrains Mono', monospace; font-size: 0.86em; background: var(--panel-cool); border: 1px solid var(--border); border-radius: 5px; padding: 1px 6px; color: var(--primary-600); }

.prompt { font-family: 'JetBrains Mono', monospace; font-size: 14px; line-height: 1.5; white-space: pre-wrap; background: #0B1020; color: #E6EAF5; border: 1px solid var(--border); border-radius: 8px; padding: 12px 15px; margin: 10px 0; overflow-x: auto; }
.prompt .lbl { color: #A5B4FC; font-weight: 700; }
.prompt .hot { color: #6EE7B7; }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Artificial Neural Networks &middot; Module 1 &middot; An Introduction</span>

# Artificial Neural Networks

### <span class="muted">One long idea, eighty years in the making.</span> <span class="brandlite">From a single mathematical neuron in 1943 to the generative models of today, this is the story of teaching machines to learn: the research, the setbacks, the breakthroughs, and where it goes next.</span>

<p class="muted" style="font-size: 22px; max-width: 60ch; margin-top: 14px;">We meet each idea at the moment it was invented, and follow it to the tools you use now.</p>

---

## How we will tell this story

<p class="muted">Not a list of equations. A story, told the way the field actually unfolded, so each idea arrives with a reason.</p>

<div class="columns">
<div class="card"><h3>Three threads, woven together</h3><ul>
<li><strong>Research and innovation</strong>: the idea, and who found it</li>
<li><strong>Drivers</strong>: what made it possible, and what held it back</li>
<li><strong>Applications</strong>: what it let us build</li>
</ul></div>
<div class="card neon"><h3>Where it leads</h3><p>Each concept is introduced as it was researched and put to use. The thread runs through two long winters and two revivals, into today's <strong>generative AI</strong>, and on to what the next couple of years make possible.</p></div>
</div>

<div class="proof"><b>Who this is for</b> Anyone starting the neural networks course. No mathematics is assumed today. The goal is a clear mental map of the field: the ideas, the order they came in, and why each one mattered.</div>

---

## The one idea behind all of it

<p class="muted">Strip away the decades and the jargon, and every neural network is the same idea.</p>

<div class="note" style="font-size:20px;">
<div class="from">the through-line</div>
Learn from examples by <strong>adjusting the strength of connections</strong>. Show the network many examples, let it guess, measure how wrong it was, and nudge its connection weights to be a little less wrong next time. Repeat, millions of times.
</div>

<div class="drive"><b>The recurring driver</b> Progress came whenever one of three levers caught up: more <strong>data</strong> to learn from, more <strong>compute</strong> to learn with, and better <strong>algorithms</strong> to learn by. Every winter was a missing lever; every spring was a lever arriving. Watch for these three all the way through.</div>

---

## Eighty years, at a glance

<div class="chips">
<span class="tag">the arc</span>
<span class="chip hot">1943 the neuron</span>
<span class="chip">1958 the perceptron</span>
<span class="chip">1969 first winter</span>
<span class="chip hot">1986 backpropagation</span>
<span class="chip">1998 vision</span>
<span class="chip">2012 deep learning</span>
<span class="chip hot">2017 the transformer</span>
<span class="chip">2022 generative AI</span>
<span class="chip">next agents</span>
</div>

<div class="columns">
<div class="card"><h3>A field of comebacks</h3><p>Neural networks were declared dead twice, in 1969 and again in the 1990s. Both times a small group kept working, and both times a new driver brought them roaring back. This is a story of patience as much as genius.</p></div>
<div class="card neon"><h3>Where we are now</h3><p>The last decade turned a research curiosity into the most important technology of the moment. We will see exactly which ideas made that happen, and in what order.</p></div>
</div>

---

<!-- _class: divider -->

<span class="kicker">Part 1 &middot; 1943 to 1958</span>

## The idea is born

<p class="muted">A neuron becomes mathematics, and a machine learns for the first time.</p>

---

## 1943: a neuron, written as math

<p class="muted">Two researchers, Warren McCulloch and Walter Pitts, asked a bold question: could the brain's neurons be described as logic?</p>

<div class="columns">
<div class="card"><h3>The model</h3><p>A neuron takes several inputs, weighs each one, adds them up, and fires if the total passes a <strong>threshold</strong>. That is it. A tiny decision unit, written in arithmetic.</p></div>
<div class="card neon"><h3>Why it mattered</h3><p>It was the first claim that <strong>thought could be computed</strong>. If a neuron is just weighted inputs and a threshold, then a network of them could, in principle, compute anything logic can.</p></div>
</div>

<div class="proof"><b>The concept</b> The artificial neuron: inputs, weights, a sum, and an activation. Every network in this deck, up to the largest model today, is built from this one unit repeated.</div>

---

## What a neuron computes

<p class="muted">One picture to carry through the whole course. Inputs come in, each is scaled by a weight, they are summed, and an activation decides the output.</p>

<div class="flow">
<span class="step">inputs</span><span class="arrow">&rarr;</span>
<span class="step">multiply by weights</span><span class="arrow">&rarr;</span>
<span class="step">add them up</span><span class="arrow">&rarr;</span>
<span class="step hot">activation</span><span class="arrow">&rarr;</span>
<span class="step">output</span>
</div>

<div class="prompt"><span class="lbl">one neuron, in words</span>
output = activation( w1*x1 + w2*x2 + ... + wn*xn + bias )

<span class="lbl">learning</span>
the x values are the input you are given.
the w values (weights) are what the network <span class="hot">learns</span>.</div>

<div class="drive"><b>The whole game</b> Training a network means finding the weights. The inputs are fixed by the problem; the weights are the knowledge. Everything that follows is a better way to find good weights.</div>

---

## 1949: how connections could learn

<p class="muted">The neuron could compute, but how would it learn? Donald Hebb gave the first answer, from biology.</p>

<div class="columns">
<div class="card"><h3>Hebb's rule</h3><p>Neurons that <strong>fire together, wire together</strong>. When two connected neurons are active at the same time, strengthen the connection between them. Learning is a change in connection strength.</p></div>
<div class="card neon"><h3>Why it mattered</h3><p>It turned learning into something mechanical: not a mystery, but a rule for adjusting weights from experience. The idea that <strong>weights change with use</strong> is still the heart of training today.</p></div>
</div>

<div class="proof"><b>The concept</b> Learning as weight change. A network does not store facts in cells; it stores them in the strengths of its connections.</div>

---

## 1958: the Perceptron, a machine that learns

<p class="muted">Frank Rosenblatt built the first neural network that could be trained from examples, and the world took notice.</p>

<div class="columns">
<div class="card"><h3>The innovation</h3><p>The <strong>Perceptron</strong>: a neuron with a learning rule. Show it an example, compare its guess to the right answer, and adjust each weight up or down to close the gap. Do this over many examples and it learns to classify.</p></div>
<div class="card amber"><h3>The moment</h3><p>Built as real hardware (the Mark I Perceptron) to recognize simple shapes. The press announced a machine that would soon walk, talk, and be conscious. The <strong>hype</strong> ran far ahead of the science.</p></div>
</div>

<div class="drive"><b>Driver and application</b> The driver was the dream of machine intelligence in the cybernetics era. The application was <strong>pattern recognition</strong>: telling one simple image from another, the ancestor of every classifier since.</div>

---

<!-- _class: dark -->

<span class="kicker">The problem of the day &middot; circa 1958</span>

## Can a machine learn to see?

<p class="muted">Picture a lab at Cornell Aeronautical Laboratory. A room-sized machine, the Mark I Perceptron, stares at cards through a grid of four hundred light sensors and slowly learns to tell one shape from another. The US Navy is paying, hoping for machines that can read photographs and spot patterns no human has time to check.</p>

<div class="columns3">
<div class="card"><h3>The hard problem</h3><p>Recognizing a shape, a letter, a face, is effortless for people and was impossible for computers. Every rule someone wrote by hand broke on the next example.</p></div>
<div class="card neon"><h3>How the network helped</h3><p>The Perceptron did not need the rules. Shown enough labelled examples, it <strong>adjusted its own weights</strong> until it could classify them. The machine learned the pattern instead of being told it.</p></div>
<div class="card amber"><h3>The new challenge</h3><p>It could only separate classes a straight line could divide. Anything more tangled, it could not learn, a limit that was about to stop the field cold.</p></div>
</div>

<div class="drive"><b>The thread</b> This is the shape of the whole story: a hard human problem, a network that learns instead of being programmed, and a fresh limit that becomes the next chapter's quest.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 2 &middot; 1969</span>

## The first winter

<p class="muted">A simple problem the Perceptron could not solve, and a book that froze the field.</p>

---

## 1969: the problem the Perceptron could not solve

<p class="muted">Marvin Minsky and Seymour Papert proved a hard limit, and the funding vanished.</p>

<div class="columns">
<div class="card amber"><h3>The XOR problem</h3><p>A single-layer perceptron can only separate classes with a straight line. Some problems, like <strong>exclusive-or</strong>, cannot be split by any straight line. The Perceptron simply could not learn them.</p></div>
<div class="card"><h3>The consequence</h3><p>Their book <em>Perceptrons</em> made the limit famous. Confidence collapsed, funding dried up, and neural networks entered their <strong>first winter</strong>, roughly a decade of neglect.</p></div>
</div>

<div class="proof"><b>The concept</b> Linear separability. A single layer draws one straight boundary. Real problems are not straight, so one layer is not enough.</div>

---

## The fix everyone could see, and no one could train

<p class="muted">The escape was known in principle: stack the neurons in layers. The trouble was training them.</p>

<div class="flow">
<span class="step">inputs</span><span class="arrow">&rarr;</span>
<span class="step hot">hidden layer</span><span class="arrow">&rarr;</span>
<span class="step hot">hidden layer</span><span class="arrow">&rarr;</span>
<span class="step">output</span>
</div>

<div class="columns">
<div class="card"><h3>Hidden layers</h3><p>Add layers between input and output. Each layer bends the boundary a little more, so a stack of them can carve any shape, including XOR. The power was never in doubt.</p></div>
<div class="card amber"><h3>The missing piece</h3><p>Nobody had a reliable way to decide how to adjust the weights of the <strong>hidden</strong> layers, the ones not directly connected to the answer. Without that, deep networks were a dead end.</p></div>
</div>

---

<!-- _class: divider -->

<span class="kicker">Part 3 &middot; 1980s</span>

## Backpropagation and the revival

<p class="muted">An old idea, made practical, teaches deep networks to learn, and vision follows.</p>

---

## 1986: backpropagation, teaching the hidden layers

<p class="muted">David Rumelhart, Geoffrey Hinton, and Ronald Williams popularized the algorithm that broke the logjam.</p>

<div class="columns">
<div class="card"><h3>The idea</h3><p>Make a guess, measure the error at the output, then <strong>propagate that error backward</strong> through the layers, using calculus to work out how much each weight contributed. Nudge every weight to reduce the error. Repeat.</p></div>
<div class="card neon"><h3>Why it changed everything</h3><p>Now the hidden layers could be trained. Networks could be made <strong>deep</strong>, and a deep enough network can approximate almost any relationship between input and output.</p></div>
</div>

<div class="proof"><b>The concepts</b> Gradient descent (roll downhill on the error), the chain rule (share the blame across layers), and non-linear activations, which let stacked layers do more than a single layer ever could.</div>

---

## Gradient descent, and making it practical

<p class="muted">Backpropagation tells each weight which way to move. Gradient descent is the rule for actually moving them, and much of the craft of training a network lives here.</p>

<div class="columns">
<div class="card"><h3>The core idea</h3><p>Think of the error as a landscape and the weights as your position on it. The gradient points uphill, so <strong>step downhill</strong> a little, again and again, and you settle into a low-error valley. How big each step is, is the <strong>learning rate</strong>.</p></div>
<div class="card neon"><h3>Making it fast and stable</h3><ul>
<li><strong>Stochastic gradient descent</strong>: update from small batches instead of the whole dataset, so training is faster and scales</li>
<li><strong>Momentum</strong>: keep rolling in a consistent direction to push through flat spots</li>
<li>Later, adaptive optimizers like <strong>Adam</strong> tune the step size for each weight</li>
</ul></div>
</div>

<div class="proof"><b>The concept</b> Optimization. A network learns by descending an error surface, and the choices of batch size, learning rate, and momentum decide whether it learns quickly, slowly, or not at all. You will tune these in every model you train.</div>

---

## Why depth is powerful

<p class="muted">Backpropagation made depth trainable. Depth is what lets a network build understanding in stages.</p>

<div class="columns">
<div class="card"><h3>Features, layer by layer</h3><p>Early layers learn simple patterns; later layers combine them into complex ones. For an image: edges, then shapes, then objects. The network <strong>discovers</strong> the useful features itself, instead of being told them.</p></div>
<div class="card neon"><h3>Representation learning</h3><p>This is the shift that defines the field. You stop hand-designing features and let the network learn its own, from raw data. Give it enough examples and depth, and it finds structure a human might miss.</p></div>
</div>

<div class="drive"><b>Driver and application</b> The driver was cognitive science, which saw the brain as a network of simple units learning together. Early applications included a system that learned to pronounce written English, and the first real handwritten digit recognition.</div>

---

## 1989 to 1998: networks that see

<p class="muted">Yann LeCun built a network shaped for images, and put it to work reading the mail.</p>

<div class="columns">
<div class="card"><h3>The convolutional network</h3><p>Instead of connecting every pixel to every neuron, slide a small <strong>filter</strong> across the image to detect a feature wherever it appears. Share the same weights across the whole image, so the network learns "an edge is an edge" once, not everywhere separately.</p></div>
<div class="card neon"><h3>The application</h3><p>LeNet read <strong>handwritten digits</strong> on cheques and postal codes, at scale, in production. The famous MNIST dataset comes from this work. It was one of the first neural networks to earn its keep in the real world.</p></div>
</div>

<div class="proof"><b>The concepts</b> Convolution (a filter that finds a feature anywhere), weight sharing (learn a pattern once), and translation invariance (recognize it wherever it sits). Convolutional networks still power much of computer vision.</div>

---

<!-- _class: dark -->

<span class="kicker">The problem of the day &middot; circa 1990</span>

## Reading a nation's mail

<p class="muted">Every day, post offices and banks drown in handwriting: millions of envelopes to sort by postal code, millions of cheques to read by hand. No two people write a seven the same way. At Bell Labs, Yann LeCun points a convolutional network at the problem.</p>

<div class="columns3">
<div class="card"><h3>The hard problem</h3><p>Read handwritten digits reliably, at industrial scale, when every sample is a little different and a wrong read costs money.</p></div>
<div class="card neon"><h3>How the network helped</h3><p>The convolutional network learned the <strong>features of a digit</strong>, a stroke, a loop, a corner, wherever they appeared, and read digits well enough to deploy. For years it read cheques by the millions across the banking system.</p></div>
<div class="card amber"><h3>The new challenge</h3><p>It worked on clean, cropped digits. Photographs of the real world, cluttered and varied, were still far out of reach, and training on them needed more data and compute than existed.</p></div>
</div>

<div class="drive"><b>The thread</b> A neural network left the lab and did real work for the first time. The win was narrow, and the gap to natural images defined the next twenty years.</div>

---

## 1997: networks that remember

<p class="muted">Images are still pictures. Language, speech, and time are sequences, and sequences need memory.</p>

<div class="columns">
<div class="card"><h3>The recurrent family</h3><p>A <strong>recurrent network</strong> (an RNN) feeds its own output back as input, so it carries a memory of what came before. Plain RNNs forgot too fast, so Sepp Hochreiter and Jurgen Schmidhuber added <strong>gates</strong>: the <strong>LSTM</strong>, and later the simpler <strong>GRU</strong>, decide what to keep and what to forget.</p></div>
<div class="card amber"><h3>The vanishing gradient</h3><p>In deep or long networks, the backward error signal can shrink to almost nothing, so early layers barely learn. The LSTM's gates were an early, clever fix; the problem itself returns in the next act.</p></div>
</div>

<div class="drive"><b>Application</b> Sequence models learned speech recognition, handwriting, and translation. For years, LSTM was the workhorse of anything that arrived one step at a time.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 4 &middot; 1990s to 2000s</span>

## The quiet years

<p class="muted">Other methods pull ahead, neural networks fall from fashion, and a few keep the faith.</p>

---

## The second lull

<p class="muted">Backpropagation worked, but training deep networks was slow, finicky, and starved of data and compute. Simpler methods often won.</p>

<div class="columns">
<div class="card amber"><h3>Why nets fell behind</h3><ul>
<li>Too little <strong>data</strong> to feed a hungry deep network</li>
<li>Too little <strong>compute</strong>: training took days for modest results</li>
<li>The vanishing-gradient problem made depth hard to train</li>
<li>Rival methods (support vector machines) were faster and often more accurate</li>
</ul></div>
<div class="card neon"><h3>The keepers of the flame</h3><p>A small group, including Geoffrey Hinton, Yann LeCun, and Yoshua Bengio, kept improving the ideas through the lean years. The field went quiet, but it did not stop.</p></div>
</div>

<div class="proof"><b>The pattern, again</b> Two of the three levers, data and compute, were missing. The algorithms were ahead of the hardware and the datasets. That gap was about to close.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 5 &middot; 2006 to 2012</span>

## Deep learning breaks through

<p class="muted">The three levers line up at last, and one contest changes the field overnight.</p>

---

## The three drivers converge

<p class="muted">Around 2010, the missing pieces arrived together. This is the moment the modern era begins.</p>

<div class="columns3">
<div class="card"><h3>Data</h3><p>The internet produced huge labelled datasets. <strong>ImageNet</strong> gathered millions of labelled images, a proper test of learning at scale.</p></div>
<div class="card neon"><h3>Compute</h3><p><strong>GPUs</strong>, built for video games, turned out to be ideal for the parallel maths of neural networks, cutting training from weeks to days.</p></div>
<div class="card amber"><h3>Algorithms</h3><p>Better activations (<strong>ReLU</strong>), regularization (<strong>dropout</strong>), and smarter initialization finally made deep networks train reliably.</p></div>
</div>

<div class="drive"><b>The turning point</b> None of these alone was enough. Together, data, compute, and algorithms crossed a threshold, and deep networks went from also-ran to unbeatable.</div>

---

## 2012: AlexNet, the moment deep learning won

<p class="muted">A single result ended the argument. In the ImageNet contest, a deep network did not just win, it demolished the field.</p>

<div class="columns">
<div class="card"><h3>What happened</h3><p>Alex Krizhevsky, Ilya Sutskever, and Geoffrey Hinton entered a deep convolutional network trained on GPUs. It cut the image recognition error rate almost in half, far beyond every hand-engineered rival.</p></div>
<div class="card neon"><h3>Why it was a shock</h3><p>Overnight, the message was clear: with enough data and compute, <strong>learned features beat hand-designed ones</strong>, decisively. Within a year, the whole field of computer vision switched to deep learning.</p></div>
</div>

<div class="proof"><b>Application explosion</b> Object detection, face recognition, medical imaging, and the perception systems in self-driving cars all followed from this one door opening. The deep learning decade had begun.</div>

---

## The toolkit that made depth train

<p class="muted">AlexNet, and the wave of work right after it, was not one trick but a bundle. These methods, most now standard, are what finally made deep networks train reliably.</p>

<div class="columns">
<div class="card"><h3>Better signals through the layers</h3><ul>
<li><strong>ReLU</strong> activation: a simple non-linearity that keeps the gradient alive, curing much of the vanishing-gradient problem</li>
<li><strong>Batch normalization</strong>: steady the numbers flowing through each layer, so training is faster and more stable</li>
<li>Careful <strong>weight initialization</strong></li>
</ul></div>
<div class="card neon"><h3>Learning that generalizes</h3><ul>
<li><strong>Dropout</strong>: randomly switch off neurons while training so the network cannot lean on any one, which reduces overfitting</li>
<li><strong>Adam</strong> and similar optimizers that adapt the step size per weight</li>
<li>Plenty of <strong>labelled data</strong> and <strong>GPUs</strong> to use it</li>
</ul></div>
</div>

<div class="proof"><b>The concept</b> Regularization and optimization methods. Depth was always powerful; these are the practical methods that made it trainable. You will reach for ReLU, dropout, batch normalization, and Adam in almost every network you build.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 6 &middot; 2013 to 2017</span>

## Language, attention, and the Transformer

<p class="muted">Vision was solved enough to trust. Language was next, and it needed a new idea.</p>

---

<!-- _class: dark -->

<span class="kicker">The problem of the day &middot; 1954 to 2016</span>

## The translation dream

<p class="muted">In 1954, a computer translated a set of Russian sentences into English and made headlines: the language barrier would fall within years. It did not. For half a century, translation defeated hand-written rules and word-by-word statistics, because meaning lives in whole sentences, not single words.</p>

<div class="columns3">
<div class="card"><h3>The hard problem</h3><p>Translate faithfully, when a word's meaning depends on words far away and the word order differs from one language to the next.</p></div>
<div class="card neon"><h3>How the network helped</h3><p><strong>Attention</strong> let a model look across the whole sentence and focus on the words that matter for each output word. Quality jumped, and by 2016 the large translation services had switched to neural models.</p></div>
<div class="card amber"><h3>The new challenge</h3><p>Attention was powerful but bolted onto slow, step-by-step recurrence. Could a network be built from attention alone, and trained in parallel at scale?</p></div>
</div>

<div class="drive"><b>The thread</b> A sixty-year-old problem cracked, and the crack opened straight onto the Transformer and everything after it.</div>

---

## 2013: meaning as numbers

<p class="muted">To work with language, a network first needs to turn words into something it can compute with.</p>

<div class="columns">
<div class="card"><h3>Word embeddings</h3><p>Represent each word as a list of numbers, a <strong>vector</strong>, learned so that words with similar meaning sit near each other. "King" and "queen" land close; "king" minus "man" plus "woman" lands near "queen".</p></div>
<div class="card neon"><h3>Why it mattered</h3><p>Meaning became <strong>geometry</strong>. Once words are points in a space, a network can reason about similarity and relationship with arithmetic. This is the same idea behind modern search and retrieval.</p></div>
</div>

<div class="proof"><b>The concept</b> Embeddings: text (and later images, audio, anything) turned into vectors, so that similarity becomes distance. A foundational idea you will meet again and again.</div>

---

## 2014: attention, focusing on what matters

<p class="muted">Sequence models read one step at a time and struggled to hold a long input in memory. Attention gave them a way to look back.</p>

<div class="columns">
<div class="card"><h3>The idea</h3><p>Instead of squeezing a whole sentence into one memory, let the network <strong>attend</strong> to the most relevant input words for each output word. Translating "bank", it can look back at "river" or "money" and choose.</p></div>
<div class="card neon"><h3>Why it mattered</h3><p>Attention let models handle long inputs without forgetting, and it made their choices more interpretable. It quickly became the most important tool in sequence modelling.</p></div>
</div>

<div class="drive"><b>Application</b> Machine translation leapt forward, and attention spread to captioning, summarization, and speech. It set the stage for the idea that would reshape the field.</div>

---

## 2017: Attention Is All You Need

<p class="muted">A single paper proposed dropping recurrence entirely and building a network from attention alone. It is the architecture behind nearly everything modern.</p>

<div class="columns">
<div class="card"><h3>The Transformer</h3><p><strong>Self-attention</strong>: every word looks at every other word in the input at once, and decides what to pay attention to. No step-by-step recurrence, so the whole sequence is processed in <strong>parallel</strong>.</p></div>
<div class="card neon"><h3>Why it took over</h3><p>Parallel training made it fast on modern hardware, and it kept getting better as it grew. The Transformer <strong>scales</strong>, and scaling is what the next chapter is all about.</p></div>
</div>

<div class="proof"><b>The concept</b> Self-attention and the Transformer. Every large language model, image generator, and multimodal system today is, at its core, a Transformer. If you remember one architecture from this course, remember this one.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 7 &middot; 2014 to now</span>

## The generative era

<p class="muted">Networks stop only recognizing the world and start creating it.</p>

---

## Two ways to use a network

<p class="muted">Before the generative wave, one distinction makes the rest of the story clear.</p>

<div class="columns">
<div class="card"><h3>Discriminative: tell things apart</h3><p>Given an input, predict a label. Is this a cat or a dog? Is this email spam? Everything up to now, from the Perceptron to AlexNet, was mostly this.</p></div>
<div class="card neon"><h3>Generative: create new things</h3><p>Learn the pattern of the data well enough to <strong>produce new examples</strong> of it. Write a sentence, paint an image, compose audio. This is the shift that defines the current moment.</p></div>
</div>

<div class="proof"><b>The concept</b> Generative versus discriminative. A generative model does not just recognize a cat, it can draw one it has never seen. That capability is what the public now calls "AI".</div>

---

## 2014 to 2022: learning to generate images

<p class="muted">Two families of ideas taught networks to create pictures, ending in the tools everyone now knows.</p>

<div class="columns">
<div class="card"><h3>GANs, 2014</h3><p>Ian Goodfellow's idea: pit two networks against each other. One <strong>generates</strong> fakes, the other tries to <strong>spot</strong> them. They improve together until the fakes are convincing. The first striking machine-made faces came from this.</p></div>
<div class="card neon"><h3>Diffusion, 2020 to 2022</h3><p>Start from pure noise and <strong>remove it step by step</strong> until an image appears, guided by a text prompt. This powers DALL-E, Stable Diffusion, and Midjourney, the tools that put image generation in everyone's hands.</p></div>
</div>

<div class="drive"><b>Application</b> Text-to-image generation, image editing, and now video. In under a decade, machine-made images went from blurry curiosities to indistinguishable from photographs.</div>

---

## Foundation models and the scaling insight

<p class="muted">The Transformer set off a simple, powerful realization: do not build a model per task. Build one big model, then adapt it.</p>

<div class="columns">
<div class="card"><h3>Pretrain, then adapt</h3><p>Train one large model on a vast amount of general data (a <strong>foundation model</strong>), then adapt it to specific jobs with a little extra training or just a good prompt. One model, many uses.</p></div>
<div class="card neon"><h3>Scaling laws</h3><p>Researchers found that more data, more compute, and larger models keep producing better results, predictably. "Just make it bigger" turned out to work far longer than anyone expected.</p></div>
</div>

<div class="proof"><b>The concept</b> Transfer learning and scale. The knowledge learned once, from everything, transfers to almost any task. This is why a single model can write code, summarize a report, and answer questions.</div>

---

<!-- _class: dark -->

<span class="kicker">The problem of the day &middot; 1950 to 2022</span>

## A machine you can just talk to

<p class="muted">In 1950, Alan Turing asked whether a machine could hold a conversation well enough to pass for human. In 1966, a simple program called ELIZA echoed people's words back as questions, and some were convinced it understood them. It did not. General, open-ended language stayed out of reach for another fifty years.</p>

<div class="columns3">
<div class="card"><h3>The hard problem</h3><p>Not a scripted chatbot, but a system that genuinely handles open language: questions, instructions, and reasoning, on any topic.</p></div>
<div class="card neon"><h3>How the network helped</h3><p>A Transformer trained to predict the next word, at enormous scale, absorbed grammar, facts, and reasoning patterns from a vast slice of text. Tuned to follow instructions, it became a general assistant.</p></div>
<div class="card amber"><h3>The new challenge</h3><p>It is fluent, and it can be confidently wrong. Making it reliable, honest, and safe is the open problem of the moment.</p></div>
</div>

<div class="drive"><b>The thread</b> Turing's question took seventy years, and three of the ideas in this deck, embeddings, the Transformer, and scale, to answer in practice.</div>

---

## 2022: the generative AI moment

<p class="muted">Large language models had been growing quietly for years. Then one product put them in front of everyone at once.</p>

<div class="columns">
<div class="card"><h3>Large language models</h3><p>A Transformer trained to predict the next word, on a large slice of the internet, learns grammar, facts, reasoning patterns, and style. Tuned to follow instructions and human feedback, it becomes a general assistant.</p></div>
<div class="card neon"><h3>Emergent abilities</h3><p>Past a certain scale, these models began to do things they were never directly taught: translate, write code, explain a joke, solve a word problem. Capability <strong>emerged</strong> from scale.</p></div>
</div>

<div class="drive"><b>Application</b> ChatGPT reached a hundred million users in weeks. Writing, coding, customer support, tutoring, and search were all touched within a year. The technology left the lab and entered daily life.</div>

---

## Beyond text: one method, many worlds

<p class="muted">The same core ideas, embeddings and Transformers and scale, reached far past chat.</p>

<div class="columns3">
<div class="card"><h3>Science</h3><p><strong>AlphaFold</strong> predicted the 3D shape of proteins, a decades-old grand challenge, accelerating biology and medicine.</p></div>
<div class="card neon"><h3>Games and control</h3><p><strong>AlphaGo</strong> beat the world's best Go player in 2016, learning strategies no human had taught it.</p></div>
<div class="card amber"><h3>Multimodal</h3><p>Single models now handle <strong>text, images, audio, and video</strong> together, describing a picture or answering a spoken question.</p></div>
</div>

<div class="proof"><b>The vindication</b> In 2024 the field's founders were honoured with Nobel Prizes: John Hopfield and Geoffrey Hinton in physics for neural networks, and the AlphaFold team in chemistry. An idea dismissed twice was now reshaping science itself.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 8 &middot; The near future</span>

## Where the story goes next

<p class="muted">We are in the middle of the chapter, not the end. Here is what is taking shape, and the honest limits.</p>

---

## The frontier right now

<p class="muted">Four directions are moving fast, and together they define the next couple of years.</p>

<div class="columns">
<div class="card"><h3>Agents that act</h3><p>Models are moving from answering questions to <strong>taking actions</strong>: using tools, browsing, writing and running code, and completing multi-step tasks on your behalf.</p></div>
<div class="card neon"><h3>Reasoning</h3><p>New models are trained to <strong>think before they answer</strong>, working through a problem step by step, which sharply improves maths, coding, and planning.</p></div>
</div>
<div class="columns" style="margin-top:14px;">
<div class="card amber"><h3>Multimodal and embodied</h3><p>One assistant that sees, hears, and speaks, and increasingly systems that act in the <strong>physical world</strong> through robotics.</p></div>
<div class="card"><h3>Smaller and cheaper</h3><p>Efficient models that run on a laptop or a phone, bringing capable AI on-device, private and low-cost.</p></div>
</div>

---

## The honest limits

<p class="muted">A clear-eyed view matters as much as the excitement. These are the real open problems.</p>

<div class="columns">
<div class="card amber"><h3>What is hard today</h3><ul>
<li><strong>Reliability</strong>: models can state falsehoods confidently</li>
<li><strong>Cost and energy</strong>: training and running large models is expensive</li>
<li><strong>Data</strong>: the supply of fresh, high-quality training data is finite</li>
</ul></div>
<div class="card"><h3>What we owe it</h3><ul>
<li><strong>Alignment and safety</strong>: making systems do what we intend</li>
<li><strong>Fairness and privacy</strong>: what the data carries, the model inherits</li>
<li><strong>Judgement</strong>: a human stays responsible for the outcome</li>
</ul></div>
</div>

<div class="proof"><b>The engineer's stance</b> These are not reasons to look away; they are the work. The people who understand both the power and the limits are the ones who will build the useful, trustworthy systems.</div>

---

## The next couple of years, plausibly

<p class="muted">Not predictions, but the near-term directions the current trends point to.</p>

<div class="columns3">
<div class="card"><h3>Assistants everywhere</h3><p>Capable, multimodal assistants built into the tools of every profession, as ordinary as spell-check is today.</p></div>
<div class="card neon"><h3>Agents that finish work</h3><p>Systems that carry out real multi-step tasks end to end, with a person reviewing and approving.</p></div>
<div class="card amber"><h3>AI for discovery</h3><p>More breakthroughs in science and medicine, from drug design to materials, with models proposing and testing ideas.</p></div>
</div>

<div class="drive"><b>The honest close</b> The story is not finished, and no one can see the end of it. What is certain is that the one idea from 1943, learning by adjusting connections, is nowhere near the limit of what it can do.</div>

---

## The family of neural architectures

<p class="muted">The story produced a toolbox of network types, each shaped for a kind of data or a kind of job. This is the map of what you will learn to build.</p>

<table>
<tr><th>Architecture</th><th>Best for</th><th>Key idea</th></tr>
<tr><td>Multilayer perceptron</td><td>tabular data, the basics</td><td>fully connected layers</td></tr>
<tr><td>Convolutional network (CNN)</td><td>images and grids</td><td>shared filters, local features</td></tr>
<tr><td>Recurrent network (RNN, LSTM, GRU)</td><td>sequences and time series</td><td>a memory of the past</td></tr>
<tr><td>Transformer</td><td>language, and now almost everything</td><td>self-attention, parallel, scalable</td></tr>
<tr><td>Autoencoder and VAE</td><td>compression and generation</td><td>encode to a small code, decode back</td></tr>
<tr><td>GAN</td><td>generating images</td><td>a generator and a critic compete</td></tr>
<tr><td>Diffusion model</td><td>high-quality image and video</td><td>generate by removing noise step by step</td></tr>
</table>

<div class="proof"><b>The foundation</b> Every one of these is the same neuron and the same learn-by-adjusting-weights idea, arranged differently for a different job. Learn the core, and each architecture is a variation on a theme you already understand.</div>

---

## The through-line, in one table

<p class="muted">Every concept in this deck, and the moment it entered the story.</p>

<table>
<tr><th>Year</th><th>Idea</th><th>Concept it introduced</th></tr>
<tr><td>1943</td><td>the artificial neuron</td><td>weighted inputs, a sum, an activation</td></tr>
<tr><td>1958</td><td>the Perceptron</td><td>learning weights from examples</td></tr>
<tr><td>1969</td><td>the XOR limit</td><td>linear separability, the need for depth</td></tr>
<tr><td>1986</td><td>backpropagation</td><td>gradient descent, training hidden layers</td></tr>
<tr><td>1989 to 1998</td><td>convolutional networks</td><td>filters, weight sharing, learned features</td></tr>
<tr><td>1997</td><td>LSTM</td><td>memory for sequences</td></tr>
<tr><td>2012</td><td>AlexNet</td><td>depth plus data plus GPUs</td></tr>
<tr><td>2013</td><td>word embeddings</td><td>meaning as vectors</td></tr>
<tr><td>2017</td><td>the Transformer</td><td>self-attention, scaling</td></tr>
<tr><td>2014 to 2022</td><td>GANs and diffusion</td><td>generating images</td></tr>
<tr><td>2022</td><td>large language models</td><td>foundation models, emergent ability</td></tr>
</table>

---

## What you can now do

<p class="muted">You do not have the maths yet. You do have the map, which is what makes the maths make sense.</p>

<div class="columns">
<div class="card"><h3>You can explain</h3><ul>
<li>The one idea: learning by adjusting connection weights</li>
<li>Why the field had two winters, and what ended each</li>
<li>The three drivers: data, compute, algorithms</li>
<li>How we got from a 1943 neuron to generative AI</li>
</ul></div>
<div class="card neon"><h3>You are ready for</h3><ul>
<li>The neuron and the perceptron, in detail and in code</li>
<li>Backpropagation and how networks actually train</li>
<li>Convolutional, recurrent, and Transformer architectures</li>
<li>Building and using models yourself, in the topics ahead</li>
</ul></div>
</div>

<div class="proof"><b>The point of this module</b> Every idea in the rest of the course has a place on the timeline you just walked. When a concept arrives, you will know why it was invented and what it replaced.</div>

---

<!-- _class: lead -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Artificial Neural Networks &middot; Introduction &middot; Complete</span>

# <span class="grad">One idea, eighty years, and still accelerating.</span>

<p class="muted" style="font-size: 22px; max-width: 58ch; margin-top: 12px;">From a neuron written in arithmetic to models that write, see, and reason, the story of neural networks is a story of patience, drivers arriving, and one simple idea proving far deeper than anyone guessed.</p>

### <span class="brandlite">Next: we open up that first neuron and the perceptron, and train one ourselves. The maths starts here, and now you know why it matters.</span>
