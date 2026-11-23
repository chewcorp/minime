---
name: clarify
description: Use when a coding request is too vague to test as written ("make it nicer", "improve X", "clean this up"), or a delivery-loop task has no accepted criteria. Asks, or records assumptions, before touching code. Turns it into testable outcome criteria with IDs and numeric fit criteria, plus Decisions, Fog and Out-of-scope. Goldfish-reviews the criteria before any code. Writes no spec, tickets or code.
---

# clarify

Before any code change, ask your questions or, when told not to wait, write down your assumptions. Work in `.minime/<task>/`; if `deliver` has not set it up, run `deliver` section 1 first. Short rounds: dispatch the `researcher` agent for facts; ask the human for decisions, batched in one message per round.

1. Elicit the underlying need. Separate outcome requirements (what and how well) from implementation choices; preserve mandated platform, protocol and compatibility constraints in Decisions.
2. Write `.minime/<task>/acceptance.md`, replacing any earlier copy for this `<task>`, with these sections:
   - **Destination**: one sentence.
   - **Outcomes**: a table `ID | requirement | fit | rationale`, IDs `O1`, `O2`, …. A fit criterion is one numeric, solution-free acceptance measure (for example "p95 under 200 ms", "0 lost rows"). A rationale that restates the requirement flags gold-plating.
   - **Decisions**: what the human decided.
   - **Fog**: what is not yet specified. Mark each still-missing value `[TK]` (to come). When the human accepts an uncertainty by name, record the ruling and its explicit assumption in Decisions or exclusion in Out-of-scope, then remove that resolved marker. Unresolved required values remain blocking.
   - **Out-of-scope**.
3. Open questions are the frontier: questions whose answer would change an outcome or its fit criterion. Run another round while any remain. If an answer needs an experiment, use the bounded [statechart/prototype detour](../deliver/references/investigation.md); unresolved or scope-changing results return here, never silently become production work.
4. Load the `goldfish-review` skill on the draft:
   - artifact: `.minime/<task>/acceptance.md`
   - intent: the user's request, quoted verbatim
   - question: which assumption is unstated, which requirement is ambiguous, which fit criterion cannot be measured, what belongs in Out-of-scope?
   - blocking rule: an outcome that cannot be tested as written, or two parts that contradict each other
   - output: `.minime/<task>/acceptance-review.md`

   Fold the verified findings into `acceptance.md`; their questions join the frontier. Rerun the review when an outcome, fit criterion or mandated constraint changed.

Done when the frontier is resolved (including any explicitly accepted assumptions or exclusions), every outcome has a numeric fit criterion, `acceptance.md` contains no `[TK]`, and `acceptance-review.md` is complete (not `review: incomplete`) with no open blocking finding.
