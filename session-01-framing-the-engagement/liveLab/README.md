# Framing the Engagement: Live Lab bundle

A complete, end-to-end working session on one account (Sunrise Electronics). You get the vague brief,
real datasets to analyze, two runnable analysis scripts, and a finished sample artifact for every
tool and every stage, so the whole thing reads like a real engagement from wish list to a defended GO.

The bundle is one logical `liveLab/` tree, split across two repos by content type:

- **Docs (this repo, the vault):** this README, and the finished sample artifacts under `artifacts/`.
- **Code and data (the code repo):** the runnable scripts under `analysis/` and the datasets under
  `data/`, at the mirror path `.../code/.../session-01-framing-the-engagement/liveLab/`.

## Layout

```
liveLab/
  data/                         (code repo)  raw inputs you analyze
    support_tickets.csv         one week, 4,000 tickets (for the Pareto)
    asks.csv                    the six asks from the brief (for RICE and MoSCoW)
    stakeholders.csv            for the Power-Interest grid
    help_content_inventory.csv  for the data-readiness read
    cost_assumptions.csv        for the business case
  analysis/                     (code repo)  runnable, no third-party libraries
    generate_tickets.py         regenerates support_tickets.csv (seeded)
    pareto.py                   Pareto analysis of the tickets
    business_case.py            saving, TCO, and payback from the assumptions
  artifacts/                    (vault)  the finished sample deliverables (the answer key)
    01-triage/   pareto-analysis, rice-scoring, moscow-scope, problem-selection-note
    02-frame/    jtbd, how-might-we, five-whys, problem-statement-and-options
    03-discover/ power-interest-grid, raci-matrix, journey-map, discovery-brief
    04-qualify/  dvf-assessment, business-case, value-driver-tree, qualification-memo
```

## Run it

From the code repo's `liveLab/analysis` folder:

```bash
python pareto.py          # rediscover the vital few (60.7% in three types)
python business_case.py   # run-rate saving, TCO, payback
```

Python 3.10+ only, no dependencies. To regenerate the tickets from scratch: `python
generate_tickets.py` (seeded, so the numbers are stable).

## How to use it

Two ways, depending on where you are:

1. **Follow the walkthrough** in the session's `live-lab.md` guide. It hands you the brief, then walks
   the four moves in order. At each step you analyze the data yourself, then open the matching file in
   `artifacts/` to check your work against a finished sample.
2. **Drive your own account.** Take the same shape (a vague brief, the same datasets swapped for your
   vertical) and produce your own four artifacts. The Sunrise artifacts here are your reference for
   what "good" looks like.

The output of each move is the input to the next: problem-selection note to problem statement to
discovery brief to qualification memo. That final GO memo is the input to the Prototype stage.
