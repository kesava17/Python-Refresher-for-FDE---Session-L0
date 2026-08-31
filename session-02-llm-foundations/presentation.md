---
marp: true
size: 16:9
paginate: true
title: LLM Foundations for Solution Builders
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
code { font-family: 'JetBrains Mono', monospace; font-size: 0.86em; background: var(--panel-cool); border: 1px solid var(--border); border-radius: 5px; padding: 1px 6px; color: var(--primary-600); }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">AI for FDE &middot; Module 1 &middot; Session 2</span>

# LLM Foundations for Solution Builders

### <span class="muted">You have a GO. Now you build.</span> <span class="brandlite">Before you wire a language model into the Sunrise assistant, you need a real picture of what the model is, where it came from, what it costs, and how to choose one. And you need to know the tool you will build with.</span>

<p class="muted" style="font-size: 22px; max-width: 56ch; margin-top: 14px;">No prior AI knowledge assumed. We start from the chat box you already know.</p>

---

## Where you are starting

<p class="muted">Be honest about the starting line, because it is a good one.</p>

<div class="columns">
<div class="card"><h3>What you are</h3><p>A strong software engineer. You ship code, read systems, and debug hard problems. That skill transfers directly.</p></div>
<div class="card neon"><h3>What you are not (yet)</h3><p>An AI specialist. You have used ChatGPT or Claude in a <strong>chat box</strong>. You have probably never called a model from code, and that is exactly what this module changes.</p></div>
</div>

<div class="proof"><b>The promise</b> By the end of Level 1 you will have built a working AI feature and be able to explain every part of it in an interview. Today is the on-ramp.</div>

---

## From a chat box to a system

<p class="muted">The chat window is one way to use a model. Building is another. Knowing the difference is the whole shift.</p>

<div class="columns">
<div class="card"><h3>In the chat box</h3><ul><li>You are the user, typing to a model</li><li>One conversation, one window</li><li>The model answers from what it was trained on</li><li>No control over cost, format, or data</li></ul></div>
<div class="card neon"><h3>When you build</h3><ul><li>Your <strong>code</strong> calls the model through an API</li><li>You send it your data, your rules, your format</li><li>You wrap it with retrieval, guardrails, and checks</li><li>The model is one <strong>component</strong>, not the whole app</li></ul></div>
</div>

<div class="proof"><b>The mental model</b> A language model is a function you call: text in, text out. Everything interesting is what you put around it.</div>

---

## Today

<div class="flow">
<span class="step hot">Where AI came from</span><span class="arrow">&rarr;</span>
<span class="step">What a model is</span><span class="arrow">&rarr;</span>
<span class="step">Choose one on evidence</span><span class="arrow">&rarr;</span>
<span class="step">Meet your coding agent</span><span class="arrow">&rarr;</span>
<span class="step hot">Build the model layer</span>
</div>

<div class="columns">
<div class="card"><h3>Foundations</h3><p>Transformers and how we got here, what a model is, tokens, context, temperature, embeddings, model families, cost, and where it runs. Enough to build, and enough to answer for it in an interview.</p></div>
<div class="card neon"><h3>Hands-on</h3><p>Runnable demos you can explore, then the first layer of the Sunrise assistant: a pluggable model interface and a harness that picks a model on evidence.</p></div>
</div>

---

<!-- _class: divider -->

<span class="kicker">Part 1</span>

## How we got here, and what a model is

<p class="muted">We start with the family tree, because the modern model is one branch of it, and interviewers ask.</p>

---

## First, the family: neural networks

<p class="muted">A language model is a kind of neural network. Neural networks have been evolving for decades; the model you call today is the latest branch.</p>

<div class="columns">
<div class="card"><h3>What a neural network is</h3><p>Layers of simple units ("neurons") with numbers ("weights") between them. You show it examples, it adjusts the weights, and it learns to map inputs to outputs. That is all "training" means.</p></div>
<div class="card neon"><h3>Why it matters here</h3><p>Everything that follows, tokens, attention, transformers, is a way to make this idea work well on <strong>language</strong>. Knowing the lineage makes the jargon stop being magic.</p></div>
</div>

<div class="proof"><b>Interview</b> "What is a neural network?" Layers of weighted connections trained on examples to map inputs to outputs. A large language model is a very large one, specialised for text.</div>

---

## The evolution, in four steps

<div class="flow">
<span class="step">Perceptron</span><span class="arrow">&rarr;</span>
<span class="step">Deep nets (MLP)</span><span class="arrow">&rarr;</span>
<span class="step">RNN / LSTM</span><span class="arrow">&rarr;</span>
<span class="step hot">Transformer</span>
</div>

<div class="columns">
<div class="card"><h3>The first three</h3><ul><li><strong>Perceptron (1958):</strong> a single neuron. Learns simple splits.</li><li><strong>Deep nets:</strong> many layers. Learn rich patterns, but treat inputs as an unordered bag.</li><li><strong>RNN / LSTM:</strong> read a sequence word by word, and carry a memory. Good for language, but slow, and they <em>forget</em> over long text.</li></ul></div>
<div class="card neon"><h3>The breakthrough</h3><p>The <strong>Transformer (2017)</strong> dropped the word-by-word reading. It looks at the whole sequence at once and learns what to pay attention to. Faster to train, and it remembers across long text.</p></div>
</div>

<div class="proof"><b>Interview</b> "Why did transformers replace RNNs?" RNNs read sequentially and lose long-range context; transformers process the whole sequence in parallel and capture long-range relationships with attention.</div>

---

## "Attention Is All You Need" (2017)

<p class="muted">One paper, from Vaswani and colleagues, is the root of every modern LLM. The idea it introduced is <strong>self-attention</strong>.</p>

<div style="text-align:center; margin: 4px 0;">
<img src="assets/transformer-block.svg" alt="A transformer block: input tokens, embeddings and position, self-attention, feed-forward, repeated N times, producing next-token probabilities; with the self-attention idea explained" style="width:100%; max-width:820px;" />
</div>

<div class="proof"><b>Interview</b> "What is self-attention?" A mechanism that lets each token weigh how much every other token matters, so the model captures context (which word "it" refers to) across the whole input at once.</div>

---

## Encoder, decoder, and the transformer

<p class="muted">The original 2017 transformer had two halves. Which half a model keeps decides what it is good at, and it is why a chat LLM is what it is.</p>

<div class="columns3">
<div class="card"><h3>Encoder</h3><p>Reads the whole input and builds a rich understanding of it. Good for classification, search, and <strong>embeddings</strong>. It does not generate text. <em>BERT.</em></p></div>
<div class="card neon"><h3>Decoder</h3><p>Generates text one token at a time, using what it has produced so far. This is the <strong>chat LLM</strong>. <em>GPT, Llama, Claude, Gemini.</em></p></div>
<div class="card amber"><h3>Encoder plus decoder</h3><p>Reads with an encoder, then writes with a decoder. Good for translation and summarization. <em>T5.</em></p></div>
</div>

<div class="proof"><b>Interview</b> "Encoder-only, decoder-only, or encoder-decoder?" The 2017 transformer had both halves. A language model like GPT is <strong>decoder-only</strong>: it just predicts the next token. BERT is encoder-only (understands, does not generate). T5 keeps both.</div>

---

## What a language model actually is

<p class="muted">Strip away the magic and this is the whole engine: it predicts the next token, over and over.</p>

<div style="text-align:center; margin: 4px 0;">
<img src="assets/llm-next-token.svg" alt="Model representation: input text becomes tokens, the transformer produces next-token probabilities, the most likely token is appended, and the process repeats" style="width:100%; max-width:900px;" />
</div>

<div class="proof"><b>Interview</b> "How does an LLM work, in one sentence?" It turns text into tokens and repeatedly predicts the most likely next token. Fluency is not truth, which is why grounding (Session 4) matters.</div>

---

## Tokens

<p class="muted">The model does not read words or characters. It reads tokens.</p>

<div class="columns">
<div class="card"><h3>What a token is</h3><p>A chunk of text, often a word or part of a word. A rough rule: one token is about four characters, or three quarters of a word.</p></div>
<div class="card neon"><h3>Why you care</h3><p>Everything is counted and priced in tokens: the text you send (input) and the text it generates (output). Longer prompts and answers cost more and take longer.</p></div>
</div>

<div class="proof"><b>Interview</b> "What is a token?" The unit a model reads and bills in, roughly three quarters of a word. Cost and speed scale with token count, input plus output.</div>

---

## The context window

<p class="muted">The model has no memory between calls. Its only memory is what you send in this call.</p>

<div class="columns">
<div class="card"><h3>The idea</h3><p>The <strong>context window</strong> is the maximum number of tokens the model can consider at once: your instructions, your data, the conversation so far, and the answer it is writing. All of it must fit.</p></div>
<div class="card neon"><h3>Why it shapes design</h3><p>You cannot paste an entire company handbook into every call. You retrieve only the relevant pieces and send those. That is the whole reason RAG exists (Session 4).</p></div>
</div>

<div class="proof"><b>Interview</b> "What is the context window?" The model's working memory for one call, in tokens. It is finite, so you feed the model only what it needs, not everything.</div>

---

## Temperature and determinism

<p class="muted">The same prompt can give different answers. There is a knob for that.</p>

<div class="columns3">
<div class="card"><h3>Temperature</h3><p>A setting from 0 upward that controls randomness in the output.</p></div>
<div class="card neon"><h3>Low (near 0)</h3><p>Focused, consistent, repeatable. What you want for grounded, factual answers.</p></div>
<div class="card amber"><h3>Higher</h3><p>More varied and creative, less predictable. Good for brainstorming, risky for support answers.</p></div>
</div>

<div class="proof"><b>Interview</b> "Why might a model give two different answers to the same prompt?" Sampling, controlled by temperature. Set it low when you need reliable, testable output.</div>

---

## Generation versus embeddings

<p class="muted">Models do two different jobs, and the Sunrise assistant needs both.</p>

<div class="columns">
<div class="card"><h3>Generation</h3><p>Text in, new text out. This is what writes the answer to a customer's question.</p></div>
<div class="card neon"><h3>Embeddings</h3><p>Text in, a list of numbers (a <strong>vector</strong>) out. Similar meanings give similar vectors, so you can search by meaning. This is how we find the right help article (Session 4).</p></div>
</div>

<div class="proof"><b>Interview</b> "What is an embedding?" A numeric vector that captures a text's meaning, so similar texts sit close together. It powers semantic search and retrieval, not text generation.</div>

---

## Cost intuition and model tiers

<p class="muted">You are spending real money per call. A builder keeps a rough meter running.</p>

<div class="columns">
<div class="card"><h3>How it is priced</h3><p>Per token, usually a small amount per thousand tokens, and often output costs more than input. Context is not free: a long prompt on every call adds up fast at 4,000 tickets a week.</p></div>
<div class="card neon"><h3>Tiers</h3><p>Providers offer small, medium, and large models. Bigger is more capable, more expensive, and slower. Much of the craft is using the <strong>smallest model that is good enough</strong>.</p></div>
</div>

<div class="proof"><b>Interview</b> "How do you control LLM cost?" Fewer tokens (shorter prompts, retrieve only what is needed), a smaller model where it suffices, and caching repeated work.</div>

---

## Model families you will hear about

<p class="muted">Not all models are the same shape. This is a map, not a deep dive; we treat the ones that matter in later sessions.</p>

| Family / type | The idea, in one line | Frontier (closed) | Open weights |
| --- | --- | --- | --- |
| **Decoder-only transformer** | The classic chat LLM: reads text, generates the next tokens | GPT, Claude, Gemini | Llama, Mistral, Qwen |
| **Mixture of Experts (MoE)** | Many expert sub-networks; only a few fire per token, so it is big but efficient | several frontier models | Mixtral, DeepSeek |
| **Encoder-only** | Reads and understands text (does not generate); good for embeddings | mostly open | BERT, RoBERTa |
| **Encoder-decoder** | Reads, then writes: translation, summarization | mostly open | T5, FLAN-T5 |
| **Multimodal** | Text plus images and audio | GPT-4o, Gemini, Claude | Llama Vision, Qwen-VL |
| **Reasoning models** | Trained to think step by step before answering | o-series, Gemini, Claude | DeepSeek-R1, QwQ |
| **Small / efficient** | Tiny and fast, for on-device or low cost | Gemini Flash, Claude Haiku | Phi, Gemma |

<div class="proof"><b>Interview</b> "What is a Mixture of Experts model?" A model split into many expert sub-networks where a router activates only a few per token, giving the capacity of a huge model at a fraction of the compute per call.</div>

---

## Open weights vs closed weights

<p class="muted">A model's weights are the trained numbers inside it. Whether you can have them decides what you can do.</p>

<div class="columns">
<div class="card"><h3>Closed (proprietary)</h3><p>The weights stay with the provider; you call the model over an API. <em>GPT, Claude, Gemini.</em></p><ul><li>Often the most capable, and the fastest to start</li><li>No infrastructure to run</li><li>Your data leaves your walls; you cannot host it yourself</li></ul></div>
<div class="card neon"><h3>Open weights</h3><p>The weights are published; you download and run them yourself. <em>Llama, Mistral, Qwen, Gemma, DeepSeek.</em></p><ul><li>Run on-prem and keep data in region</li><li>Control, privacy, no per-token vendor fee</li><li>You run and maintain the infrastructure</li></ul></div>
</div>

<div class="proof"><b>Interview and Sunrise</b> "Open or closed?" Closed is often more capable and simpler to start; open weights let you run on-prem and keep data in Bharat, which is what Sunrise's residency rule pushes you toward. Note: "open weights" is not the same as "open source", the license and training data may still be restricted.</div>

---

## Where the model runs

<p class="muted">Same model idea, three very different places to run it, and it matters for Sunrise.</p>

<div class="columns3">
<div class="card"><h3>Hosted API</h3><p>Call a provider's model over the internet. Fastest to start, no infrastructure, but your data leaves your walls.</p></div>
<div class="card neon"><h3>Open-weights, self-hosted</h3><p>Run an open model on your own servers. More control and privacy, more work to operate.</p></div>
<div class="card amber"><h3>On-prem</h3><p>Self-hosted inside the customer's own environment. The answer when data cannot leave.</p></div>
</div>

<div class="proof"><b>Interview and Sunrise</b> Sunrise customer data must stay in <strong>Bharat</strong>. That residency rule can rule out a foreign hosted API and push you to an open model hosted in region. Always ask "where does the data go?"</div>

---

## Part 1 recap: your interview checklist

<div class="columns">
<div class="card"><h3>You can now explain</h3><ul><li>Neural networks, and the path to transformers</li><li>Self-attention and why it replaced RNNs</li><li>Next-token prediction, and why fluent is not correct</li><li>Tokens, and how cost and speed scale with them</li></ul></div>
<div class="card neon"><h3>and</h3><ul><li>The context window, and why it forces retrieval</li><li>Temperature and determinism</li><li>Generation versus embeddings</li><li>Model families (including MoE), open versus closed weights, tiers, and where a model runs</li></ul></div>
</div>

<div class="proof"><b>The bar</b> If you can say each of these in one plain sentence, you can hold your own in an AI-engineering screen. That is the minimum this session guarantees.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 2</span>

## Choose a model on evidence, not hype

---

## Do not pick by vibes

<p class="muted">"Everyone uses model X" is not a reason. Models differ, and the job decides.</p>

<div class="chips">
<span class="chip hot">capability</span>
<span class="chip">cost per token</span>
<span class="chip">latency</span>
<span class="chip">context size</span>
<span class="chip">hosting and residency</span>
<span class="chip">safety</span>
</div>

<div class="proof"><b>The point</b> A cheaper, smaller, in-region model that answers Sunrise's support questions well beats a famous model that is expensive, slow, or not allowed to hold the data.</div>

---

## The model-comparison matrix

<p class="muted">The instrument: score the candidates on what the job needs, in one table.</p>

| Factor | What to check |
| --- | --- |
| **Capability** | Does it answer the golden questions correctly and grounded? |
| **Cost** | Price per 1,000 tokens, at the real volume (thousands of tickets a week) |
| **Latency** | Time to answer; will a customer wait for it? |
| **Context** | Big enough to hold the retrieved passages plus instructions? |
| **Hosting / residency** | Can it run where the data must stay (Bharat)? |
| **Safety** | Does it refuse and escalate cleanly when it should? |

<div class="drive"><b>Evidence, not opinion</b> Fill this from a real run, not from a blog post.</div>

---

## Model benchmarks: where to look

<p class="muted">For the capability row, do not trust marketing. Public benchmarks give a first read, and a few sites make the comparison easy.</p>

<div class="columns">
<div class="card"><h3>Leaderboards and comparison sites</h3><ul><li><strong>LMArena</strong> (Chatbot Arena): human-preference ranking across models</li><li><strong>Artificial Analysis</strong>: quality, speed, and price side by side</li><li><strong>Hugging Face Open LLM Leaderboard</strong>: standard benchmarks for open models</li><li><strong>HELM</strong> (Stanford): a holistic, multi-metric evaluation</li></ul></div>
<div class="card neon"><h3>Benchmarks you will see quoted</h3><ul><li><strong>MMLU</strong>: broad knowledge across subjects</li><li><strong>GPQA</strong>: hard, graduate-level reasoning</li><li><strong>HumanEval</strong> and <strong>SWE-bench Verified</strong>: coding</li><li><strong>GSM8K</strong>: grade-school math word problems</li></ul></div>
</div>

<div class="proof"><b>Interview</b> "How do you compare model capability?" Start with a leaderboard (LMArena, Artificial Analysis) and the benchmarks that match your task (MMLU, GPQA, SWE-bench). Then confirm on your own golden set: public benchmarks can be leaked or gamed, and none of them is your support queue.</div>

---

## Eval-driven selection

<p class="muted">The honest way to choose: let a small test decide.</p>

<div class="flow">
<span class="step hot">Golden set</span><span class="arrow">&rarr;</span>
<span class="step">Run one task 3 ways</span><span class="arrow">&rarr;</span>
<span class="step">Score each</span><span class="arrow">&rarr;</span>
<span class="step hot">Recommend, with reasons</span>
</div>

<div class="columns">
<div class="card"><h3>The golden set</h3><p>A handful of real support questions with known good answers. The same set you reuse to test grounding and the whole PoC.</p></div>
<div class="card neon"><h3>The output</h3><p>A recommendation you can defend: "model B, because it matched on the golden set, costs half as much, and runs in region."</p></div>
</div>

---

## Sunrise: what the model has to be

<div class="columns">
<div class="card"><h3>Must</h3><ul><li>Answer order, return, and simple-warranty questions from provided text</li><li>Cheap enough at thousands of tickets a week</li><li>Low latency (a customer is waiting)</li></ul></div>
<div class="card neon"><h3>Constraint</h3><ul><li>Runs where data stays in Bharat</li><li>Escalates cleanly when unsure (warranty is sensitive)</li></ul></div>
</div>

<div class="proof"><b>Where this lands</b> This is exactly the model-comparison harness you build today. It turns "which model?" into a scored answer.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 3</span>

## How you will actually build: coding agents

---

## You will not hand-write all of this

<p class="muted">Modern AI features are built with an AI helper in the loop. This is a skill in itself.</p>

<div class="columns">
<div class="card"><h3>A chat assistant</h3><p>Answers questions in a window. You copy and paste code back and forth. You did this with ChatGPT.</p></div>
<div class="card neon"><h3>A coding agent</h3><p>Works <strong>inside your project</strong>: it reads your files, writes and edits code across them, runs commands and tests, sees the errors, and fixes them. It acts, it does not just chat.</p></div>
</div>

<div class="proof"><b>Why it matters for an FDE</b> You will stand up a working PoC in hours, not weeks. The agent does the typing; you provide the judgment, the review, and the direction.</div>

---

## The landscape

<p class="muted">Coding agents come in three shapes. Knowing the shapes helps you choose.</p>

<div class="columns3">
<div class="card"><h3>Terminal / CLI</h3><p>Live in your command line. Strong at multi-file work and running things. <em>Claude Code, Aider, Gemini CLI, Codex CLI.</em></p></div>
<div class="card neon"><h3>IDE-integrated</h3><p>Live in your editor. Smooth for editing as you go. <em>Cursor, Copilot, Windsurf, Cline, Antigravity.</em></p></div>
<div class="card amber"><h3>Autonomous / cloud</h3><p>Take a task and work on their own, async. <em>Devin, Copilot Workspace, Jules.</em></p></div>
</div>

<div class="proof"><b>Not a ranking</b> These overlap and change monthly. What matters is fit for the job and how much control you keep.</div>

---

## Coding agents, compared

| Tool | Type | Free tier | Strengths | Watch-outs |
| --- | --- | --- | --- | --- |
| **Claude Code** | Terminal + IDE | Paid plans | Strong multi-file reasoning, runs and tests, top on coding benchmarks | Usage cost; review diffs |
| **Cursor** | IDE (fork) | Yes, limited | Smooth inline + agent, multi-model | Pro subscription |
| **GitHub Copilot** | IDE plugin | Yes | Everywhere, cheap, familiar | Agent mode younger |
| **Windsurf** | IDE | Yes, generous | Agentic flows | Younger ecosystem |
| **Google Antigravity** | Agentic IDE | Yes, free preview | Agent-first across editor, terminal, browser; Gemini 3 | Very new |
| **Cline** | VS Code ext (open) | Free, bring your model | Transparent, model-agnostic | You pay model API |
| **Aider** | Terminal (open) | Free, bring your model | Git-aware, scriptable | Terminal only |
| **Gemini CLI** | Terminal | Yes, generous | Free agentic CLI | Newer |
| **Devin / Jules** | Autonomous | Limited / paid | Hands-off scoped tasks | Less control, cost |

---

## Cost and benchmarks, for the course

<p class="muted">Two practical questions: what does it cost a trainee, and how do you compare their strength honestly?</p>

<div class="columns">
<div class="card neon"><h3>Free tier, for training</h3><p>You can complete this course at no tool cost. <strong>Gemini CLI</strong>, <strong>Antigravity</strong> (free preview), <strong>Windsurf</strong>, and <strong>Copilot</strong> have real free tiers; <strong>Cline</strong> and <strong>Aider</strong> are free tools where you pay only for a cheap model's API. Paid agents (Claude Code, Devin) bill by usage or subscription.</p></div>
<div class="card"><h3>How to compare strength</h3><p>Do not trust marketing. The standard benchmark is <strong>SWE-bench Verified</strong> (can the agent fix real GitHub issues); <strong>Terminal-Bench</strong> tests terminal tasks. Check the current leaderboard when you choose; the order shifts monthly.</p></div>
</div>

<div class="proof"><b>Rule of thumb</b> Frontier agents (Claude-based and Gemini-3-based) lead the coding benchmarks today. For learning, a strong free tier that you can review beats the last few benchmark points.</div>

---

## How to pick

<div class="columns">
<div class="card"><h3>Weigh these</h3><ul><li><strong>Task fit:</strong> multi-file build vs quick edits</li><li><strong>Model quality:</strong> the brain behind the agent (check SWE-bench)</li><li><strong>Control:</strong> can you see and approve every change?</li></ul></div>
<div class="card neon"><h3>and these</h3><ul><li><strong>Cost and free tier:</strong> what will you actually pay?</li><li><strong>Privacy:</strong> can it run against a private or on-prem setup?</li><li><strong>Your comfort:</strong> terminal or editor</li></ul></div>
</div>

<div class="proof"><b>The rule</b> Pick one you can <strong>review and steer</strong>. An agent you cannot check is a liability, not a speed-up.</div>

---

## Our recommendation for this course

<div class="columns">
<div class="card neon"><h3>Use in the walkthroughs</h3><p>We use <strong>Claude Code</strong>: it handles multi-file Python builds, runs the eval harness, keeps repo-wide context, and leads the coding benchmarks. If you want a free path, <strong>Gemini CLI</strong> or <strong>Antigravity</strong> (free preview) will build this PoC too.</p></div>
<div class="card"><h3>Also strong</h3><p><strong>Cursor</strong> for an editor-first experience; <strong>Aider</strong> or <strong>Cline</strong> for a fully open, model-agnostic setup where you control cost.</p></div>
</div>

<div class="proof"><b>Pick one, learn it deeply</b> Any of these will build the PoC. The win is fluency with one tool, not owning ten.</div>

---

## Working with an agent well

<p class="muted">The agent is fast and confident. Your job is to keep it honest.</p>

<div class="columns">
<div class="card"><h3>Do</h3><ul><li>Give it context: the goal, the files, the constraints</li><li>Work in small steps you can check</li><li>Read every diff before you accept it</li><li>Keep tests; let them catch the agent</li></ul></div>
<div class="card amber"><h3>Do not</h3><ul><li>Accept large changes you have not read</li><li>Let it invent APIs or secrets</li><li>Skip running the code because "it looks right"</li></ul></div>
</div>

<div class="proof"><b>Coming up</b> Across the phase you will learn to drive the agent well: give it <strong>memory</strong> (today), then efficient context, reusable <strong>skills</strong>, an eval <strong>harness</strong>, and a build-run-check <strong>loop</strong>.</div>

---

<!-- _class: divider -->

<span class="kicker">Part 4</span>

## What we build today: the model layer

---

## The PoC, and today's layer

<p class="muted">Recall the target from the GO memo: the Sunrise Support Deflection Assistant. We build it one layer per session.</p>

<div class="flow">
<span class="step hot">Model layer</span><span class="arrow">&rarr;</span>
<span class="step">Prompt + output</span><span class="arrow">&rarr;</span>
<span class="step">Grounding (RAG)</span><span class="arrow">&rarr;</span>
<span class="step">Assemble + demo</span>
</div>

<div class="proof"><b>Today</b> The model layer: a clean, pluggable way to call a model, and a harness to choose one. Everything later plugs into this.</div>

---

## The model interface

<p class="muted">One small contract, so the rest of the PoC never cares which model is behind it.</p>

<div class="columns">
<div class="card"><h3>Two jobs</h3><p><code>generate(prompt)</code> returns text. <code>embed(texts)</code> returns vectors. That is all the rest of the code needs to know.</p></div>
<div class="card neon"><h3>Pluggable</h3><p>A <strong>deterministic mock</strong> runs offline with no keys, so everything is testable. A real or on-prem adapter plugs in behind the same interface, chosen by an environment variable. Secrets never live in the code.</p></div>
</div>

<div class="proof"><b>Why offline first</b> Every build in this course runs with no API key, so you are never blocked. Add a real model when you want, without changing a line of the caller.</div>

---

## Explore the concepts: the demos

<p class="muted">Five short, offline demos back the foundations. Each is documented in <code>demos/cookbook.md</code> with what to run and what to watch for.</p>

<div class="columns">
<div class="card"><h3>The demos</h3><ul><li><code>predict.py</code> the model guessing the next token</li><li><code>tokens.py</code> tokens and cost</li><li><code>temperature.py</code> randomness and determinism</li><li><code>embed_vs_generate.py</code> the two model jobs</li><li><code>mock_model.py</code> the offline model behind the interface</li></ul></div>
<div class="card neon"><h3>How to use them</h3><p>Follow <code>demos/cookbook.md</code>. Do not just read the output: change the input, predict what will happen, run it, and see if you were right. That is how the concept sticks.</p></div>
</div>

<div class="drive"><b>Where they live</b> Runnable in the <code>demos/</code> project, no API key needed. The cookbook is the detailed try-it guide.</div>

---

## The live lab today

<div class="columns">
<div class="card"><h3>You will build (with your coding agent)</h3><ul><li>The help corpus and golden question set (used all phase)</li><li>The model interface, with the offline mock</li><li>A real/on-prem adapter behind the same interface</li><li>The model-comparison harness with a recommendation</li></ul></div>
<div class="card neon"><h3>Agent skill today: memory</h3><p>You will give your coding agent a <strong>memory</strong> file: the repo conventions, the PoC contract, and the goal, so it builds to spec instead of guessing. This is the first coding-agent skill of the phase.</p></div>
</div>

<div class="drive"><b>The deliverable</b> A model-comparison harness: one task, three ways, one defended pick.</div>

---

## Recap, and what you can now do

<div class="columns">
<div class="card"><h3>You learned</h3><ul><li>How AI got here: neural nets to transformers to self-attention</li><li>What a model is, and its foundations, at interview depth</li><li>Model families, and how to choose one on evidence</li><li>What a coding agent is, how to pick one, and how to give it memory</li></ul></div>
<div class="card neon"><h3>You built</h3><ul><li>The corpus and golden set</li><li>A pluggable model layer</li><li>A comparison harness with a recommendation</li></ul></div>
</div>

<div class="proof"><b>Next</b> Session 3, Prompt Engineering and Structured Outputs: make the model return reliable, structured, guardrailed answers you can trust in code.</div>

---

<!-- _class: lead -->

<img class="deck-logo" src="logos/guildtrek-logo.png" alt="GuildTrek" />

<span class="kicker">Session 2 &middot; Complete</span>

# <span class="grad">You understand the tool, and you have the first layer.</span>

<p class="muted" style="font-size: 22px; max-width: 54ch; margin-top: 12px;">From neural networks to transformers to a running model layer. You can choose a model on evidence, build with a coding agent, and you have laid the first layer of the Sunrise assistant.</p>

### <span class="brandlite">Next: Session 3, make it reliable. Structured, valid, guardrailed output the rest of the PoC can trust.</span>
