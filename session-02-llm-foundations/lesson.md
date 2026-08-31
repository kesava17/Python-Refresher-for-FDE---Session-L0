# LLM Foundations for Solution Builders

> You have a GO on the Sunrise Electronics assistant. Now you build it. Before you wire a language
> model into anything, you need a real picture of what a model is, where it came from, what it costs,
> and how to choose one on evidence. And you need to know the tool you will build with.
>
> **This chapter builds the mental model and the model layer.** It assumes no prior AI knowledge. It
> starts from the chat box you already know, walks the whole path from a single neuron to the modern
> transformer, and lands on a running, pluggable model layer for the Sunrise bot. Every major concept
> comes with a plain one-sentence version you can say in an interview.

This is the master chapter for Session 2, and you can read it on its own. Session 1 framed the
problem: Sunrise Electronics wants a service bot to take load off its call center, where about 60
percent of calls are three query types (order status, return and refund, and warranty), warranty is
legally sensitive so it must route to a human, and every answer is logged for audit. You qualified
that problem and got a GO. This session builds the first layer of the bot: the **model layer**, the
part that actually calls a language model. Everything later in the phase (prompting, grounding,
assembly) plugs into what you build here.

You are starting from a good place. You are a strong software engineer: you ship code, read systems,
and debug hard problems. That skill transfers directly. What you are not yet is an AI specialist. You
have used ChatGPT or Claude in a chat window, and you have probably never called a model from code.
That single gap is exactly what this chapter closes.

## Objective

After this chapter you can:

- Explain the shift from using a model in a chat box to calling it as a component from your own code.
- Trace how we got here: neural networks, the path from the perceptron to the transformer, and what
  the 2017 "Attention Is All You Need" paper introduced.
- Say in one plain sentence what a language model is (next-token prediction), and why fluent is not
  the same as correct.
- Reason about the working parts a builder controls: tokens and cost, the context window,
  temperature and determinism, and the difference between generation and embeddings.
- Name the main model families, know where a model can run, and apply Bharat data residency to the
  Sunrise case.
- Choose a model on evidence with a comparison matrix, a golden set, and an eval-driven pick.
- Explain what a coding agent is, pick one on evidence, and give it a **memory** file so it builds to
  spec.

Every major concept below closes with an **Interview** line: the one-sentence version an interviewer
wants to hear. Learn those and you can hold your own in an AI-engineering screen.

## Coverage

The chapter moves in a straight line, from meaning to build:

1. **From a chat box to a system.** The model is a function you call.
2. **How we got here.** Neural networks, the perceptron-to-transformer path, self-attention.
3. **What a model is.** Next-token prediction, tokens and cost, the context window, temperature,
   generation versus embeddings.
4. **The map of models.** Model families, where a model runs, and Bharat residency.
5. **Choosing a model on evidence.** The comparison matrix, the golden set, eval-driven selection.
6. **Coding agents.** What they are, how to pick one, and the first agent skill of the phase: memory.
7. **The model layer.** What today's live lab builds, and how the demos back it.

At the end there is a recap, a pointer to the live lab, and two assignments. Alongside this chapter is
a `demos/` folder of short runnable scripts. Wherever you reach a **Try it** note, run the named
script. The demos are their own small Poetry project: from the `demos/` folder run `poetry install`
once, then `poetry run python <name>.py`. They need no API key and no network, so nothing blocks you.
Follow `demos/cookbook.md` for the guided walkthrough. Watch for the **enterprise lens** (why an idea
matters in production) and the **common trap** (a mistake that is easy to miss).

---

## From a chat box to a system

The chat window is one way to use a model. Building software with a model is another, and knowing the
difference is the whole shift this course asks of you.

In the **chat box**, you are the user. You type into one window, the model answers from what it was
trained on, and the conversation lives and dies in that window. You have no control over cost, output
format, or what data the model sees. This is fine for asking questions. It is not a system.

When you **build**, your *code* calls the model through an **API** (an application programming
interface, the same kind of function-over-the-network call you already make to any other service).
You send the model your data, your rules, and the exact format you want back. You wrap it with
retrieval, guardrails, and checks. The model becomes one **component** inside your application, not
the whole application. For Sunrise, the model is the part that drafts an answer; your code is what
decides whether that answer is allowed to go to the customer or must route to a human.

Hold on to one mental model for the rest of the course:

> A language model is a function you call. Text goes in, text comes out. Everything interesting is
> what you put around it.

That framing is why an FDE with strong engineering skills can build AI features quickly. You already
know how to design the code around a function. The function is new; the engineering around it is your
home ground.

**Enterprise lens.** In the chat box, the data is whatever the user pastes, and it leaves your
control. In a built system, *you* decide what data the model sees and where the call goes. For a
customer like Sunrise, that control is the whole reason a built system is allowed and a public chat
box is not.

**Interview.** "What changes when you go from using an LLM in a chat box to building with one?" You
call it from code through an API, you control the input, output format, and cost, and the model
becomes one component wrapped in retrieval, guardrails, and checks rather than the whole application.

---

## How we got here, and what a model is

We start with the family tree, because the modern model is one branch of it, and interviewers ask you
to place it. None of this is trivia. Knowing the lineage is what makes the jargon stop feeling like
magic.

### First, the family: neural networks

A language model is a kind of **neural network**. Neural networks are not new; they have been evolving
for decades, and the model you call today is the latest branch.

A neural network is layers of simple units (loosely called "neurons") with numbers called **weights**
on the connections between them. You show the network many examples. It makes a guess, sees how wrong
it was, and nudges its weights to be a little less wrong next time. Repeat that across a huge number
of examples and the weights settle into values that map inputs to outputs well. That process of
adjusting weights from examples is all that **training** means. There is no rule-writing and no
database of facts inside; there are just weights that were tuned until the outputs were good.

Everything that follows (tokens, attention, transformers) is a way to make this one idea work well on
**language** specifically.

**Interview.** "What is a neural network?" Layers of weighted connections trained on examples to map
inputs to outputs. A large language model is a very large one, specialized for text.

### The evolution, in four steps

The path from the first neural network to the transformer runs through four milestones. You do not
need the mathematics; you need the story of what each step fixed.

- **Perceptron (1958).** A single neuron. It takes some inputs, weighs them, and outputs one
  decision. It can learn simple splits (is this above or below a line) and nothing more complex. It
  is the seed of the whole field.
- **Deep networks (the multi-layer perceptron, or MLP).** Stack many layers of neurons and the
  network can learn rich, non-obvious patterns. This is "deep learning." The limit for language: an
  MLP treats its inputs as an unordered bag, so it has no real sense of word order or sequence.
- **RNN and LSTM (recurrent networks).** These read a sequence one item at a time, left to right, and
  carry a running **memory** of what they have seen. That made them genuinely good at language for the
  first time. Two problems held them back: they must process word by word, so they are slow and hard
  to parallelize, and their memory fades over long passages, so they **forget** things said far back.
  (LSTM, "long short-term memory," was a smarter memory cell that helped, but did not fully solve
  this.)
- **Transformer (2017).** The breakthrough. It dropped the word-by-word reading entirely. Instead it
  looks at the whole sequence at once and learns, for each word, which other words matter. That makes
  it fast to train (the work parallelizes) and good at long-range context (nothing has to survive a
  long walk through a fading memory).

**Interview.** "Why did transformers replace RNNs?" RNNs read sequentially, which is slow and loses
long-range context as their memory fades; transformers process the whole sequence in parallel and
capture long-range relationships directly with attention.

### "Attention Is All You Need" (2017)

One paper, from Vaswani and colleagues at Google, is the root of every modern large language model.
Its title is a claim: you do not need the recurrent, word-by-word machinery at all. The one mechanism
you need is **attention**, and specifically **self-attention**.

Self-attention lets each word (each token, really) look at every other token in the input and decide
how much each one matters for understanding it. Take the sentence "The customer returned the phone
because it was faulty." To handle the word "it," the model needs to know whether "it" refers to the
customer or the phone. Self-attention is the mechanism that lets "it" weigh every other token and put
most of its attention on "phone." It does this for every token, across the whole input, at once. That
is where the model's grip on context comes from.

A transformer stacks this mechanism into blocks: the input text becomes tokens, each token gets an
**embedding** (a numeric representation) plus a signal of its position, then self-attention and a
small feed-forward network refine those representations, and this block repeats many times. At the
end, the model produces a probability for what the next token should be. That is the machine under
every chat model you have used.

**Interview.** "What is self-attention?" A mechanism that lets each token weigh how much every other
token matters, so the model captures context (like which word "it" refers to) across the whole input
at once, in parallel.

### What a language model actually is

Strip the magic away and the whole engine is this: a language model predicts the **next token**, over
and over. It reads the text so far, produces a probability for every possible next token, picks one,
appends it, and then does the whole thing again with the slightly longer text. Fluent paragraphs are
just this loop run hundreds of times.

This has one consequence you must internalize now, because it shapes every design decision later:

> A language model is not a database. It does not look facts up. It generates the most likely
> continuation of your text based on patterns in its training.

That is why a model can produce a confident, fluent answer that is simply wrong. It is optimizing for
*plausible-sounding*, not for *true*. The industry word for a confident wrong answer is a
**hallucination**. This is not a bug you can prompt away; it is what the machine does. The fix is to
give the model the right facts to work from at call time (retrieval, which you build in Session 4) and
to check its output (guardrails, Session 3). For Sunrise, this is exactly why warranty answers cannot
be trusted to the model alone: a fluent, wrong warranty answer is a legal problem, so those route to a
human.

**Try it.** Run `predict.py` from the `demos/` project (`poetry run python predict.py "where is my"`).
Watch the candidate next tokens with their probabilities, one being picked, and the sentence building
itself token by token. Change the input, predict what comes next, then check. Follow `demos/cookbook.md`.

**Interview.** "How does an LLM work, in one sentence?" It turns text into tokens and repeatedly
predicts the most likely next token; it generates plausible continuations, not looked-up facts, which
is why grounding matters.

### Tokens, and why they are the unit of cost

The model does not read words or characters. It reads **tokens**. A token is a chunk of text, often a
whole common word, sometimes a piece of a longer or rarer word, sometimes just a punctuation mark. A
rough rule of thumb: one token is about four characters of English, or roughly three quarters of a
word. The word "warranty" might be one token; an order id like "SE-1024" might split into several.

Tokens matter to a builder for one blunt reason: **everything is counted and priced in tokens.** The
text you send in (the **input**, sometimes called the prompt) is counted, and the text the model
generates (the **output**) is counted, and you pay for both. Longer prompts and longer answers cost
more money and take more time. At Sunrise volumes (thousands of tickets a week), a prompt that is
needlessly long on every single call adds up to real Rs.

**Try it.** Run `tokens.py` (`poetry run python tokens.py "Where is my order SE-1024?"`). Watch the
sentence split into tokens, the token count, and a cost estimate. Then paste a long paragraph and
watch the count and cost jump. That jump is exactly why we later retrieve only the passages we need
instead of sending the whole handbook.

**Interview.** "What is a token?" The unit a model reads and bills in, roughly three quarters of a
word. Cost and speed scale with the total token count, input plus output.

### The context window, and why it forces retrieval

Here is a fact that surprises every engineer coming from the chat box: the model has **no memory
between calls.** Each API call is fresh. The only thing the model knows is what you send it in that
one call. The chat window creates an illusion of memory by quietly resending the earlier conversation
every time; when you build, *you* are responsible for that.

The **context window** is the maximum number of tokens the model can consider in a single call. It
must hold everything at once: your instructions, any data you provide, the conversation so far, and
the answer the model is writing. All of it competes for the same finite budget. Modern windows are
large (tens or hundreds of thousands of tokens), but they are still finite, and filling them is slow
and expensive.

This single limit is the reason a whole technique exists. You cannot paste the entire Sunrise product
handbook into every call. It would not fit, and if it did it would be slow and costly. Instead you
**retrieve** only the few passages relevant to the customer's question and send just those. That is
**Retrieval-Augmented Generation (RAG)**, and it is the whole subject of Session 4. For now, just hold
the cause: the context window is finite, so you feed the model only what it needs, not everything you
have.

**Enterprise lens.** Treat the context window as a budget you spend deliberately, not a bucket you
fill. Every token of boilerplate instruction you repeat on every call is money spent and latency added
at Sunrise's real volume. Sending less, chosen well, is both cheaper and often more accurate, because
the model is not distracted by irrelevant text.

**Interview.** "What is the context window?" The model's working memory for one call, measured in
tokens. It is finite and holds instructions, data, history, and the answer together, so you feed the
model only what it needs, which is why retrieval exists.

### Temperature and determinism

Ask a model the same question twice and you can get two different answers. That is not a fault; it is
a setting, and you control it.

When the model has computed the probabilities for the next token, it has to actually pick one. If it
always took the single most likely token, the output would be fixed. Instead it **samples**: it draws
from the probability distribution, so a slightly-less-likely token sometimes wins. **Temperature** is
the knob that controls how much randomness is in that draw.

- **Temperature near 0** makes the model almost always take the most likely token. The output is
  focused, consistent, and close to repeatable. This is what you want for grounded, factual,
  testable answers.
- **Higher temperature** flattens the odds so less-likely tokens get picked more often. The output is
  more varied and creative, and less predictable. Good for brainstorming; risky for a support answer
  a customer relies on.

For the Sunrise bot you will run at a low temperature, because you want reliable answers you can test
and audit. A support bot that gives a different warranty-adjacent answer every time is not auditable.

A note on the word **deterministic**: low temperature makes output much more *stable*, but production
APIs do not guarantee bit-for-bit identical output even at temperature 0 (there are other sources of
variation on the provider side). The practical takeaway holds: low temperature when you need reliable,
repeatable behavior; higher only when you deliberately want variety.

**Try it.** Run `temperature.py` (`poetry run python temperature.py`). At temperature 0.0 the pick is
identical every run; higher up it varies run to run. Ask yourself which setting you would ship for a
support bot, and why.

**Interview.** "Why might a model give two different answers to the same prompt?" It samples the next
token from a probability distribution, and temperature controls that randomness. Set it low when you
need reliable, testable output.

### Generation versus embeddings

Models do two different jobs, and the Sunrise assistant needs both. Keeping them straight is a common
interview check.

- **Generation.** Text in, new text out. This is the job you have been picturing all along: the model
  writes the answer to the customer's question.
- **Embeddings.** Text in, a list of numbers out. That list is called a **vector**. The useful
  property is that texts with similar *meaning* produce similar vectors, so you can measure how close
  two pieces of text are in meaning by comparing their vectors. "How do I return this?" and "What is
  your return policy?" land close together; "Where is my order?" lands farther away, even though it
  shares few words.

Embeddings are how you **search by meaning** instead of by keyword. When the bot needs to find the
right help article for a question, it embeds the question, compares it against embedded help
articles, and pulls the closest ones. That is the retrieval half of RAG, and it is why the model layer
you build today exposes both jobs. Generation writes the answer; embeddings find the facts to write it
from.

**Try it.** Run `embed_vs_generate.py` (`poetry run python embed_vs_generate.py "how do I return an
item?"`). Watch the generated sentence, the embedding vector, and that two same-topic questions score a
higher similarity than two different-topic ones. The demo's embeddings are a crude stand-in; real ones
arrive in Session 4, but the idea is exactly this.

**Interview.** "What is an embedding?" A numeric vector that captures a text's meaning, so texts with
similar meaning sit close together. It powers semantic search and retrieval, and it is a different job
from text generation.

### Cost intuition and model tiers

You are spending real money on every call now, so a builder keeps a rough meter running in their head.
Pricing is **per token**, usually quoted as a small amount per thousand tokens, and output tokens
often cost more than input tokens. Context is not free: a long prompt sent on every call is billed on
every call, which is why the context-window discipline above is also a cost discipline.

Providers offer models in **tiers**: small, medium, and large. Bigger models are more capable, but
they are also more expensive and slower. A large amount of the craft of building with models is using
the **smallest model that is good enough** for the job, and reserving the big one for the hard cases.
For Sunrise, answering "where is my order" from a provided order record does not need a frontier
model; a small, cheap, fast one may pass every test.

**Interview.** "How do you control LLM cost?" Send fewer tokens (shorter prompts, retrieve only what
is needed), use the smallest model that still passes your tests, and cache repeated work.

---

## The map of models

Not all models are the same shape, and the words for the shapes come up constantly. This is a map, not
a deep dive; you meet the ones that matter again in later sessions.

### Model families you will hear about

| Family / type | The idea, in one line | Familiar examples |
| --- | --- | --- |
| **Decoder-only transformer** | The classic chat LLM: reads text, generates the next tokens | GPT, Llama, Mistral, Claude, Gemini |
| **Mixture of Experts (MoE)** | Many expert sub-networks; a router fires only a few per token, so it is big but efficient | Mixtral, DeepSeek |
| **Encoder-only** | Reads and understands text but does not generate; strong for embeddings and classification | BERT family |
| **Encoder-decoder** | Reads a whole input, then writes an output: translation, summarization | T5, FLAN-T5 |
| **Multimodal** | Handles text plus images (and sometimes audio) | GPT-4o, Gemini, Claude |
| **Reasoning models** | Trained to work step by step before answering, for harder problems | o-series, DeepSeek-R1 |
| **Small / efficient** | Tiny and fast, for on-device or low-cost use | Phi, Gemma |

A few of these deserve a sentence more. **Decoder-only** is the default shape of the chat models you
know; when someone says "an LLM" they usually mean one of these. **Mixture of Experts** is the trick
behind several of the largest models: instead of running the whole enormous network for every token, a
small router picks a few relevant "expert" sub-networks to run, so you get the capability of a huge
model at a fraction of the compute per call. **Reasoning models** trade speed and cost for the ability
to think through multi-step problems; they are overkill for "where is my order" and worth it for
genuinely hard reasoning.

**Interview.** "What is a Mixture of Experts model?" A model split into many expert sub-networks where
a router activates only a few per token, giving the capacity of a very large model at a fraction of
the compute per call.

### Where the model runs

The same model idea can run in three very different places, and the choice matters for Sunrise as much
as any capability question.

- **Hosted API.** You call a provider's model over the internet. Fastest to start, no infrastructure
  to run, but your data leaves your walls and travels to the provider.
- **Open-weights, self-hosted.** You take an open model (one whose weights you can download) and run it
  on your own servers. More control and privacy, and more work to operate and scale.
- **On-prem.** A self-hosted model running inside the customer's own environment. This is the answer
  when data is not permitted to leave that environment at all.

The deciding question is almost always: **where does the data go?** Sunrise handles customer data, and
that data must stay in **Bharat**. A residency rule like that can rule out a foreign hosted API outright,
regardless of how good the model is, and push you toward an open model hosted in region or fully
on-prem. This is not a detail to discover late. It is a constraint that shapes the whole architecture,
and an FDE asks about it on day one.

**Enterprise lens.** Data residency and privacy frequently decide the model before capability does.
The strongest hosted model in the world is the wrong choice if the contract or the law says the data
cannot leave the country. Design the model layer so the running model is a pluggable choice, and this
constraint becomes a configuration decision, not a rewrite. That pluggability is exactly what today's
live lab builds.

**Interview and Sunrise.** "How does data residency affect model choice?" It can override capability:
if customer data must stay in Bharat, a foreign hosted API may be disallowed, pushing you to an
in-region open model or on-prem, so you always ask where the data goes before you pick a model.

---

## Choosing a model on evidence, not hype

"Everyone uses model X" is not a reason. Models differ across many axes, and the *job* decides which
one wins. A cheaper, smaller, in-region model that answers Sunrise's support questions well beats a
famous model that is expensive, slow, or not allowed to hold the data. The way you land on the right
choice is to measure, not to guess.

### The model-comparison matrix

The instrument is one table. Score each candidate model on what this job actually needs, and the
choice stops being an opinion.

| Factor | What to check |
| --- | --- |
| **Capability** | Does it answer the golden questions correctly and grounded? |
| **Cost** | Price per 1,000 tokens, at the real volume (thousands of tickets a week) |
| **Latency** | Time to answer; will a waiting customer accept it? |
| **Context** | Big enough to hold the retrieved passages plus the instructions? |
| **Hosting / residency** | Can it run where the data must stay (Bharat)? |
| **Safety** | Does it refuse and escalate cleanly when it should? |

The rule for this table: fill every cell from a **real run**, not from a blog post or a leaderboard.
Marketing numbers are measured on someone else's task, not yours.

### The golden set and eval-driven selection

The honest way to choose is to let a small test decide. That test is built on a **golden set**.

A golden set is a handful of real support questions paired with known good answers: the kind of
questions Sunrise customers actually ask ("Where is my order SE-1024?", "How do I return a defective
charger?", "Is my six-month-old phone still under warranty?") with the answer you would accept as
correct. You build this set once and reuse it everywhere: to choose the model now, to test grounding
in Session 4, and to check the whole PoC later. It is the single most valuable artifact in an AI
build, because it turns "does this work?" into a question you can actually answer.

**Eval-driven selection** is then simple to describe and rigorous in practice:

1. Take the golden set.
2. Run the same task through each candidate model.
3. Score each model's answers against the known good answers, and record cost, latency, and residency.
4. Recommend a model, with reasons you can defend.

The output is a sentence you can stand behind in a review: "Model B, because it matched the golden set
as well as the others, costs half as much at our volume, answers in under a second, and runs in
region." That is a defensible engineering decision, not a preference.

**Common trap.** Choosing a model on a public leaderboard or a demo transcript instead of your own
golden set. A model that tops a general benchmark can still fail *your* questions, be too slow at
*your* latency target, or be disallowed by *your* residency rule. The only evidence that counts is a
run on your task.

For Sunrise, the model must answer order, return, and simple-warranty questions from provided text; be
cheap enough at thousands of tickets a week; answer fast enough that a customer waits; run where the
data stays in Bharat; and escalate cleanly when it is unsure, because warranty is sensitive. That set
of requirements is exactly what the **model-comparison harness** in today's live lab checks. It turns
"which model?" into a scored, defended answer.

**Interview.** "How do you choose a model for a task?" Build a golden set of real questions with known
good answers, run each candidate through it, score capability alongside cost, latency, context, and
residency in a comparison matrix, and recommend the one the evidence supports.

---

## How you will actually build: coding agents

Modern AI features are built with an AI helper in the loop, and using that helper well is a skill in
itself. This course teaches it as a running thread, one idea per session. Today's job is to understand
what a coding agent is, pick one, and give it its first piece of context.

### Chat assistant versus coding agent

You already know a **chat assistant**: it answers questions in a window, and you copy and paste code
back and forth. You did this with ChatGPT. It is helpful, but it does not touch your project.

A **coding agent** works *inside your project*. It reads your files, writes and edits code across many
of them, runs commands and tests, sees the errors those produce, and fixes them. It **acts**; it does
not only chat. That is the difference that lets an FDE stand up a working PoC in hours instead of
weeks. The agent does the typing; you provide the judgment, the review, and the direction.

**Interview.** "What is the difference between a chat assistant and a coding agent?" A chat assistant
answers in a window and you move code by hand; a coding agent works inside your repository, reading,
editing, running, and fixing across files, so it takes actions rather than only giving text.

### The landscape

Coding agents come in three broad shapes. Knowing the shapes helps you choose, and helps you read a
market that changes every month.

- **Terminal / CLI agents** live in your command line and are strong at multi-file work and running
  things. Examples: Claude Code, Aider, Gemini CLI, Codex CLI.
- **IDE-integrated agents** live in your editor and are smooth for editing as you go. Examples: Cursor,
  GitHub Copilot, Windsurf, Cline, Google Antigravity.
- **Autonomous / cloud agents** take a scoped task and work on it asynchronously, largely on their
  own. Examples: Devin, Copilot Workspace, Jules.

These categories overlap and shift constantly, so treat this as a map of the terrain, not a ranking.

### Picking one on evidence

Two practical questions decide a pick: what does it cost, and how strong is it, honestly measured.

On **cost**, you can complete this entire course at no tool cost. Several agents have real free tiers:
**Gemini CLI**, Google **Antigravity** (free preview), **Windsurf**, and **GitHub Copilot**. **Cline**
and **Aider** are free, open tools where you bring your own model and pay only for a cheap model's API.
Paid agents like **Claude Code** and **Devin** bill by usage or subscription.

On **strength**, do not trust marketing. The industry-standard benchmark for coding agents is
**SWE-bench Verified**: a curated set of real GitHub issues, where the score is the fraction the agent
can actually fix, with its solution checked against the project's own tests. (A related benchmark,
Terminal-Bench, measures terminal tasks specifically.) Check the current SWE-bench Verified
leaderboard when you choose, because the order shifts month to month. As a rule of thumb today,
frontier agents (Claude-based and Gemini-based) lead. For *learning*, a strong free tier you can watch
and review beats the last few benchmark points.

When you pick, weigh: **task fit** (a multi-file build versus quick inline edits), **model quality**
(the model behind the agent, checked on SWE-bench), **control** (can you see and approve every
change?), **cost and free tier**, **privacy** (can it run against a private or on-prem setup?), and
**your own comfort** (terminal or editor). Above all, pick one you can **review and steer**. An agent
whose changes you cannot check is a liability, not a speed-up.

For this course's walkthroughs we use **Claude Code**, because it handles multi-file Python builds,
runs the eval harness, keeps repo-wide context, and leads the coding benchmarks. If you want a free
path, **Gemini CLI** or **Antigravity** will build this PoC too, and **Cursor** is a strong
editor-first choice. Any of them works. The win is fluency with one tool, not owning ten.

**Common trap.** Accepting large agent changes you have not read because they "look right." The agent
is fast and confident, and it can invent an API that does not exist or a secret that should never be
in code. Work in small steps you can check, read every diff before you accept it, and keep your tests
so they catch the agent. Speed without review is how a confident wrong change reaches production.

**Interview.** "How do you evaluate a coding agent?" Check its strength on SWE-bench Verified (real
GitHub issues fixed against the project's tests), weigh task fit, control, cost and free tier, and
privacy, and pick one you can review and steer rather than the highest benchmark you cannot check.

### The first agent skill: memory

Here is the first coding-agent skill of the phase, and the one today's lab uses: give the agent a
**memory** file.

An agent starts every session knowing nothing about your project beyond what it can read. Left to
guess, it invents conventions, picks libraries you would not, and builds something almost right that
you then have to correct. A memory file (a project-context file the agent reads at the start of its
work, often named something like `CLAUDE.md` or `AGENTS.md` depending on the tool) fixes this. In it
you write down the things the agent must build *to*, not guess at:

- The **goal**: what this project is (the Sunrise model layer) and what it must do.
- The **conventions**: how this repo is laid out, what libraries and patterns to use, how to run and
  test.
- The **contract**: the interfaces and constraints that must not drift (for Sunrise, the model
  interface, the offline-first rule, and the residency constraint).

With that file in place, the agent builds to spec instead of to its best guess, and its output needs
far less correcting. This is the single highest-leverage habit in agent-assisted building, which is
why it comes first. Across the rest of the phase you will add the other agent skills at the session
where the lab first needs each: efficient context and prompting (Session 3), reusable skills and an
eval harness (Session 4), and the build-run-check loop (Session 5).

**Enterprise lens.** A memory file is version-controlled project knowledge that every agent session,
and every teammate's agent, reads the same way. It is how "build it the way we build things here" stops
being tribal knowledge and becomes a file the agent honors on every run. On a real client engagement,
that consistency is worth more than any single clever prompt.

**Interview.** "What is agent memory and why does it matter?" A project-context file the coding agent
reads at the start of its work, holding the goal, conventions, and contract, so it builds to spec
instead of guessing and its output needs far less correcting.

---

## What we build today: the model layer

Recall the target from the Session 1 GO: the Sunrise Support Deflection Assistant, built one layer per
session. Today you build the **model layer**: a clean, pluggable way to call a model, and a harness to
choose one on evidence. Every later layer (prompting in Session 3, grounding in Session 4, assembly in
Session 5) plugs into this.

### The model interface

The centerpiece is one small contract, so the rest of the PoC never has to care which model is behind
it. The interface exposes exactly two jobs, matching the two model jobs from earlier in this chapter:

- `generate(prompt)` returns text. This is generation: it drafts the answer.
- `embed(texts)` returns vectors. This is embeddings: it finds the right facts by meaning (used from
  Session 4).

That is all the rest of the code needs to know. Behind the interface, a **deterministic mock** runs
completely offline with no API key, so every build in this course is testable and nothing ever blocks
you. A real or on-prem adapter plugs in behind the same interface, chosen by an **environment
variable**, and secrets never live in the code. Because the caller only knows the interface, swapping
the mock for a real in-region model is a configuration change, not a rewrite. This is where the
residency constraint from earlier stops being a worry and becomes a setting.

**Try it.** Run `mock_model.py` (`poetry run python mock_model.py`) to see the offline model behind the
single `generate` interface. Notice that it answers order and return questions directly but handles the
warranty question cautiously; that caution is the escalation guardrail you make real in Session 3. Then
open `mocklib.py` and read `generate`: that function is the exact seam a real model slots into in the
live lab.

**Enterprise lens.** Offline-first is not a training convenience; it is how you keep a build testable,
fast, and free of secrets in continuous integration. A deterministic mock means your tests give the
same result every run, with no key, no network, and no cost, and the day you add a real model, not one
line of the caller changes.

### The demos behind the concepts

Five short, offline demos back the foundations in this chapter, each documented in `demos/cookbook.md`
with what to run, what to watch for, and what to explore:

- `predict.py`: the model guessing the next token.
- `tokens.py`: tokens and cost.
- `temperature.py`: randomness and determinism.
- `embed_vs_generate.py`: the two model jobs.
- `mock_model.py`: the offline model behind the interface.

Use them the way that makes a concept stick: do not just read the output. Change the input, predict
what will happen, run it, and check whether you were right.

---

## Recap

Read the chapter back as one line of thought:

- **From chat box to system.** A language model is a function you call from code: text in, text out.
  Everything interesting is the retrieval, guardrails, and checks you put around it, and the model is
  one component, not the whole app.
- **How we got here.** Neural networks are layers of weights trained on examples. The path ran
  perceptron, deep networks, RNN and LSTM, then the transformer (2017), whose self-attention lets every
  token weigh every other token at once, in parallel, fixing the speed and memory limits of RNNs.
- **What a model is.** Next-token prediction, over and over. It generates plausible continuations, not
  looked-up facts, so fluent is not the same as correct, which is why grounding and escalation matter.
- **The parts a builder controls.** Tokens (the unit of cost), the context window (finite, so you
  retrieve rather than send everything), temperature (randomness, low for reliable answers), and the
  split between generation and embeddings.
- **The map of models.** The families (decoder-only, MoE, encoder-only, encoder-decoder, multimodal,
  reasoning, small), the tiers, and where a model runs (hosted, self-hosted, on-prem), with Bharat
  residency often deciding the choice.
- **Choosing on evidence.** A comparison matrix filled from a real run, a reusable golden set, and
  eval-driven selection that produces a defended pick, not a preference.
- **Coding agents.** An agent acts inside your repo; pick one you can review and steer, judged on
  SWE-bench Verified, and give it a memory file so it builds to spec. That memory file is the first
  agent skill of the phase.

The review lens for the whole topic: given a task, ask what the model is being asked to do, whether the
data is allowed to go where that model runs, how many tokens the call really needs, what temperature the
job wants, whether the choice was made on a golden set or a guess, and whether the agent building it has
the context to build to spec. Those questions turn "it worked in the chat box" into "it will hold up as
a system, and I can defend every part of it."

And the through-line: **the model is the easy part; the engineering around it is the job.** A strong
software engineer who understands what the model is, controls its cost and behavior, chooses it on
evidence, and drives a coding agent well is exactly what an FDE building AI features looks like.

**Next:** the [live lab](live-lab.md) builds the model layer for the Sunrise assistant: the shared help
corpus and golden question set (reused all phase), a pluggable **model interface** with an offline
**deterministic mock**, a **real / on-prem adapter** chosen behind the interface by an environment
variable, and a **model-comparison harness** that scores candidates on the golden set and produces a
defended recommendation. You build it with your coding agent, and you start by giving that agent its
**memory** file so it builds to this spec instead of guessing. Then two assignments extend the work.

### Assignments

1. **Compare three model configs and defend a pick.** Using the model-comparison harness and the
   golden question set from the lab, run the same Sunrise support task through three model
   configurations (for example the offline mock plus two adapter settings, or three tiers of one
   provider). Fill the comparison matrix from your own run: capability against the golden set, cost at
   Sunrise volume, latency, context, residency, and escalation behavior. Recommend one config in a
   short written note, with the evidence that supports it. The deliverable is the filled matrix and a
   defensible one-paragraph recommendation.

2. **Add a new model adapter behind the interface.** Implement a new adapter for the model interface
   (a different provider, a different local or on-prem model, or a second mock with different
   behavior) so it plugs in behind the same `generate` and `embed` contract and is selected by the
   environment variable, with no change to the caller. Prove it: run the existing tests and the
   comparison harness against your new adapter unchanged. The deliverable is the working adapter,
   selectable by config, passing the same tests as the mock.
