---
name: brief
description: Use when an agent to be built or rebuilt has no accepted brief, or the recruit script prints brief. Interviews the human and writes brief.md (problem, outcomes with numeric fits, non-goals, authority limits, attention budget, open decisions), then goldfish-reviews it for comprehension. Writes no charter, prompt or code.
---

# brief

Writes `.minime/<agent>/brief.md`: problem, principals, outcomes with numeric fits and gauges, authority limits, attention budget, initiative. Interview the human one question at a time, each with a recommended answer; resolve facts yourself.

1. Write `brief.md`, replacing any earlier copy:
   - **Problem**: the failure today without this agent, and why now.
   - **Serves**: the principals it acts for, and who may address it explicitly.
   - **Outcomes**: table `ID | outcome | fit | gauge`, IDs `O1`, `O2`, …. Fit: numeric, solution-free. Gauge: the source path each term is read from, and when it cannot judge (E1). Name the binding constraint (quota, attention, tokens) and gauge it (E2).
   - **Non-goals and authority limits**: what it may not touch or decide. Mark each one-way door (data loss, messages outside the project, production, spend).
   - **Attention budget**: when it may address a person; at most one receipt per explicit request, keyed to the request id. No other message (A1, B2).
   - **Initiative**: the inferred work it may take up. One mode switch per agent, `observe | act`, starting at `observe`, written only by the human.
   - **Decides**: the owner of each open choice. Mark unresolved values `[TK]`.
2. Contradiction check: a lever counted against its own target is a contradiction (E3).
3. Reviewed stage (see `recruit`):
   - artifact: `brief.md`
   - intent: the human's request, quoted verbatim
   - question: paraphrase what this agent is for and what it may never do; which outcome cannot be measured as written; which two parts contradict?
   - blocking rule: two or more reviewers fail to paraphrase a section, or their readings conflict; an outcome has no numeric fit; two outcomes contradict. One reviewer's failed paraphrase is advisory.
   - output: `brief-review.md`

Done when `brief.md` has no `[TK]`, every outcome has a numeric fit and a gauge, and `brief-review.json` is clear for the current `brief.md`.
