# Stage 5 Rechart — post-F8 (2026-10-21)

Supersedes the ticket graph of `.kilo/plans/2026-10-21-workshop-stage5-remediation.md`
without rewriting it. That chart's history stays as the record of *why* the
proportionate bar exists; this file is the working map from `main` = `133f661`.
Predecessor addendum: same plan, "Addendum 2026-10-21 (second)"; failure record:
`.kilo/plans/2026-10-21-overgating-incident.md`.

## What changed

1. **PR #7 merged.** S01a-S01c repaired PR #5's foundation (merged earlier as
   PR #6). The F8 self-copy case and a tracer run at the **reversible-edit
   evidence tier** landed: real provenance, behavioral oracle (16 legs), tracer
   driver, and an audit whose honest outcome is "no behavioral gap on the
   hardened oracle; possible robustness gap, N=1, not decision-grade".
2. **Tiers are the axis.** Evidence effort is gated on cost of being wrong, not
   topic. Two tiers now exist by decision, not drift:
   - **Tier-R (reversible)**: runnable session per arm, visible arm difference,
     durable audit artifact (committed note + reproducible driver). Small N,
     free panel default, human merge. F8 tracer is the reference.
   - **Tier-I (irreversible / publication-grade)**: the original S08-S11
     apparatus (sealed holdouts, precommitted budgets/thresholds, panel coverage,
     human retirement gate) unchanged and reserved for decisions expensive to
     walk back.
3. **The runtime question is answered for Tier-R** and remains open only where
   Tier-I genuinely needs it (attributable identity, exact byte capture). That
   part stays a future spike if and when a Tier-I decision is scheduled.

## What the chart got wrong

S05-S11 assumed the corpus build-out would be one monolithic pre-registered
suite before any instruction conclusion was allowed. Under tiering that is
exactly backwards: Tier-R conclusions flow per-family as incidents justify;
Tier-I gates only the specific decisions that need them. The 36-case frozen
suite is still the Tier-I destination, but it is built incrementally by
admitting cases that have already earned their oracle at Tier-R.

## Requirements layer

The predecessor chart stacked a fixed requirements layer (R1-R7) between plan
and tickets. This rechart collapses that to outcomes → tickets deliberately:
tiering replaced fidelity to a fixed requirements list as the evidence
discipline, and the predecessor's R table remains the record in
`.kilo/plans/2026-10-21-workshop-stage5-remediation.md`. The collapse is a
decision, not a drop — each requirement's obligations now live in:

| Requirement | New home |
| --- | --- |
| R1 Honest foundation | Merged foundation — PR #6, repaired by PR #7; the record, not a live ticket. |
| R2 Real execution boundary | The Tier-R tracer loop (T3, F8 as reference); its Tier-I remainder (attributable identity) waits in T5. |
| R3 Discriminating corpus | T2/T3/T4 corpus growth — per-family admission replaces the single 36-case build-out. |
| R4 Valid measurement | T5 — precommitted budgets/thresholds and matched arms, priced only when a Tier-I decision is scheduled. |
| R5 Controlled instruction experiment | T5 — one-hypothesis discipline, priced only when a Tier-I decision is scheduled. |
| R6 Human decision and retention | T5 — per-model equivalence/retention plus the human gate, priced only when a Tier-I decision is scheduled. |
| R7 Ordered, bounded delivery | Standing human-merge/delivery gates, unchanged per AGENTS.md — outside this chart by design. |

## Ticket map from here

Tracer-bullet first; each ticket sized to one implementor context; spikes
timeboxed. `depends on` edges are hard; parallel-capable tickets say so.

| Ticket | Outcome | Depends on | Tier | Size / proof |
| --- | --- | --- | --- | --- |
| T1 Canonicalize install.sh paths | O4 product defect closed | none | product | S: `cd + pwd -P` both sides in install.sh with non-GNU fallback; acceptance = the case oracle (already on main) now passes `repaired.sh` on all 16 legs incl. trailing-slash + symlink spellings; because install.sh changes here, acceptance also includes refreshing the case's `repaired.sh` — PROOF.md locks it byte-identical to the branch's install.sh (the post-merge main:install.sh) — and re-running PROOF's re-score table on the refreshed copy; keep the two `install_config` guards. |
| T2 F10 evidence-proportionality case | O1 grows by one family | none (incident doc already on main) | Tier-R | S: the violation/safe-negative/unrelated triplet already exists in the incident doc ("Proposed candidate seed (family F10)"); this ticket converts that seed into case materials mirroring the f8-self-copy-tracer layout minus fixture — provenance, a behavioral oracle that scores the *gate choice* for a described decision, constructed prompts as inputs — with the oracle's rubric informed by the three logged failures (over-gating, gold-plating, premature human hand-off). |
| T3 Per-family Tier-R tracers (F1-F3, F7, F9 next) | O1 steady state | T2 conventions preferred style | Tier-R | M per family, parallelizable: each family admits only after its oracle discriminates known-bad vs valid + one mutation probe, and its tracer runs current+absent once on the free panel with an audit note in the F8 format. No 36-case suite freeze required to learn at this tier. |
| T4 Case-admission rule update | O1, O4 hygiene | T2, T3 first admissions inform it | process | S: amend `.kilo/workshop/evals/agentic-pr/README.md` and `.kilo/workshop/SCHEMA.md` (the SCHEMA lives at the workshop root, not under `evals/agentic-pr/`) so a case is admitted when its behavioral oracle discriminates, static regex layers optional and explicitly smoke-tier; records the F8 lesson (static layer deleted) so future families don't re-add it by habit. |
| T5 Tier-I suite assembly | O2, O3 scheduled only when a hard-retirement/publication claim is next on the table | T3 corpus mass (≥ several families with clean Tier-R runs), scheduled by human | Tier-I | **Question: what is the smallest Tier-I gate set that covers the next hard decision on the table?** Spike, 60 min, human-scheduled: price the actual decision (what exactly would we adopt/retire, blast radius, rollback cost) and only then size S08-S11-analogue gates; do not build the apparatus ahead of the decision. |

Blocking graph:

```text
T1 (product, independent)

T2 (independent)
  |
  v
T3 (parallel per family) --> T4 (T2 conventions + T3 first admissions)
  |
  +-- (corpus mass) --> T5 (spike, human-scheduled; needs T3, not T4)
```

S05-S07 as originally written dissolve into T3's per-family admissions; S08-S11
survive only inside T5's sized-when-needed gate. S02's unresolved Tier-I runtime
questions live in T5's spike, not on the critical path. F4 (weakest-model
decision), F5 (incomplete evidence), and F6 (source-grounded triage) also
queue behind T3's initial batch — their oracles need the decision-scoring
harness material T2's F10 work will produce — and attach there as later
per-family admissions.

## Traceability

| Outcome | Tickets |
| --- | --- |
| O1 Trusted experiment | T2, T3, T4 |
| O2 Current-instruction diagnosis | T3 (Tier-R per family), T5 (Tier-I) |
| O3 Successful first ablation pass | T5 (only when a Tier-I decision is scheduled) |
| O4 Safe delivery and subtraction | T1 (product defect), T4, and the standing human-merge gate |

Every ticket has a home outcome and a proof; no ticket waits on another
ticket's future output except as graphed. Zero orphans.
