# Framing the Engagement: Live Lab

## What we are driving

You are the Forward Deployed Engineer on the Sunrise Electronics account. A vague wish list has landed.
In this lab you drive it end to end, through the four moves of the Frame stage (Triage, Frame,
Discover, Qualify), until you hold a decision you can defend to a board. You do the analysis on real
datasets, produce the four artifacts, and at each step check your work against a finished sample.

This is a working session, not a reading. Open the data, run the scripts, write the artifact, then
compare. The materials are one logical Live Lab bundle (`liveLab/`), split by type: the datasets
(`liveLab/data/`) and runnable scripts (`liveLab/analysis/`) live in the code repo, and the finished
sample artifacts (`liveLab/artifacts/`) live here in the vault, alongside this guide.

Ground rules: the analysis scripts are plain Python 3.10+, no dependencies. Run them from the
`liveLab/analysis` folder.

## The brief (your vague inputs)

An email from Vikram Rao, VP of Customer Experience, forwarded after a single kickoff call.

> Subject: AI for customer experience, need to move fast
>
> The board wants us to use AI on customer experience this year, and everyone here has an opinion. Let
> me dump it all:
>
> - My support team is drowning in the same questions all day (order status, returns, warranty), and
>   the hard cases wait behind them. I want AI to take that load off.
> - Sales wants the same assistant to upsell and cross-sell while it is talking to customers.
> - Marketing, and the CEO who saw a demo, want it on brand and to generate our help content and
>   campaigns.
> - Our CSAT slipped last quarter and I am being asked to fix it.
> - IT says we have years of data so this should be easy, and it must integrate and be secure.
> - Budget is tight and I need something to show the board by end of quarter.

One direction, six agendas, no owner, no value analysis. Your job is to untangle it.

---

## Step 0: Set up and look at the data

Get the Live Lab bundle and run the Pareto analysis once, so you have seen the raw shape of the load
before you reason about it.

```bash
cd liveLab/analysis
python pareto.py
```

You should see three question types (order_status, return, warranty_simple) crossing 60 percent of
the 4,000 tickets. Now drive.

---

## Stage 1: Triage (choose the one problem)

**Goal:** cut six competing asks down to one problem worth building, on evidence.

1. **Pareto.** You ran `pareto.py`. Read where the volume concentrates and what the long tail is worth.
   Write it up.
   - Checkpoint: `liveLab/artifacts/01-triage/pareto-analysis.md`
2. **RICE.** Open `liveLab/data/asks.csv`. Only three of the six asks are buildable problems (A4 is an outcome,
   A5 an assumption, A6 a constraint). Score the three on Reach, Impact, Confidence, Effort.
   - Checkpoint: `liveLab/artifacts/01-triage/rice-scoring.md`
3. **MoSCoW.** Sort the scope into Must, Should, Could, and Won't-this-quarter. Name the Won'ts out loud.
   - Checkpoint: `liveLab/artifacts/01-triage/moscow-scope.md`
4. **Produce the artifact:** a problem-selection note that states the chosen problem, the evidence, and
   where every other ask went.
   - Checkpoint: `liveLab/artifacts/01-triage/problem-selection-note.md`

**Output of Triage:** one chosen problem (support deflection). It is the input to Frame.

---

## Stage 2: Frame (define the problem, generate options)

**Goal:** turn the chosen problem into a sharp, tool-free statement and real options. Resist "so build
the support bot."

1. **Jobs-to-be-Done.** Write the customer's job and the agent's job. Keep tools out of all three
   clauses.
   - Checkpoint: `liveLab/artifacts/02-frame/jtbd.md`
2. **How Might We.** Phrase the job as one open question at the right altitude (not "fix support," not
   "add a chatbot").
   - Checkpoint: `liveLab/artifacts/02-frame/how-might-we.md`
3. **The 5 Whys.** Ladder from "support is drowning" to the root. Do not stop at "understaffed" or "no
   chatbot."
   - Checkpoint: `liveLab/artifacts/02-frame/five-whys.md`
4. **Produce the artifact:** the problem statement and three distinct options (Deflect, Route, Assist),
   with the health warning that the value reads are still guesses.
   - Checkpoint: `liveLab/artifacts/02-frame/problem-statement-and-options.md`

**Output of Frame:** a problem statement and three options. The input to Discover.

---

## Stage 3: Discover (ground it in what is true)

**Goal:** replace the guesses with facts. Use `liveLab/data/stakeholders.csv` and
`liveLab/data/help_content_inventory.csv`.

1. **Power-Interest grid.** Plot the stakeholders on power and interest. Watch for the quiet high-power
   veto.
   - Checkpoint: `liveLab/artifacts/03-discover/power-interest-grid.md`
2. **RACI.** Assign one Accountable per task across the PoC.
   - Checkpoint: `liveLab/artifacts/03-discover/raci-matrix.md`
3. **Customer-journey map.** Trace a "where is my order" question and find the break.
   - Checkpoint: `liveLab/artifacts/03-discover/journey-map.md`
4. **Produce the artifact:** a discovery brief (real need, data state, stakeholders and vetoes,
   constraints, narrowed scope). Note what changed: warranty splits, residency appears, scope shrinks.
   - Checkpoint: `liveLab/artifacts/03-discover/discovery-brief.md`

**Output of Discover:** a discovery brief. The input to Qualify.

---

## Stage 4: Qualify (decide, and defend it)

**Goal:** turn the grounded picture into a defensible go or no-go. Use `liveLab/data/cost_assumptions.csv`.

1. **DVF.** Run support deflection through desirability, viability, feasibility. Contrast with upsell.
   - Checkpoint: `liveLab/artifacts/04-qualify/dvf-assessment.md`
2. **Business case.** Compute the saving, the TCO, and the payback.
   ```bash
   python business_case.py
   ```
   - Checkpoint: `liveLab/artifacts/04-qualify/business-case.md`
3. **Value-driver tree.** Trace the chain from the bot to support margin, and check every link has an
   owner and a number.
   - Checkpoint: `liveLab/artifacts/04-qualify/value-driver-tree.md`
4. **Produce the artifact:** the qualification memo (the gates, the grid placement, the GO decision,
   the evidence, the assumptions, the no-conditions).
   - Checkpoint: `liveLab/artifacts/04-qualify/qualification-memo.md`

**Output of Qualify:** a qualification memo carrying a defended GO. The input to the Prototype stage.

---

## Wrap: what you built

Four artifacts, each the output of one move and the input to the next:

1. Problem-selection note (Triage)
2. Problem statement with options (Frame)
3. Discovery brief (Discover)
4. Qualification memo (Qualify)

Together they are the Frame stage of the engagement. You drove a real account from a messy wish list to
a decision a board can trust, on evidence at every step.

## Drive your own account

Now do it without the answer key. Pick a vertical (banking, healthcare, retail, manufacturing,
logistics, insurance, the public sector, or your own client context, set in Bharat), take a wish list
of the same messy shape, and produce your own four artifacts. The Sunrise bundle is your reference for
what "good" looks like. This is the Frame stage of your Capstone L1.
