---
name: brief
description: Use when an agent to be built or rebuilt has no accepted brief, or the recruit script prints brief. Interviews the human and writes brief.md (problem, outcomes with numeric fits, non-goals, authority limits, attention budget, open decisions), then goldfish-reviews it for comprehension. Writes no charter, prompt or code.
---

# brief

The job brief: why we are hiring, what good looks like, and what the new colleague must never do. Work in `.minime/<agent>/`. Ask the human one question at a time, with a recommended answer; look up facts yourself rather than asking for them.

1. Write `brief.md`, replacing any earlier copy, with these sections:
   - **Problem**: what goes wrong today without this agent, and why now.
   - **Serves**: the people or agents it acts for, and who may address it explicitly.
   - **Outcomes**: table `ID | outcome | fit | gauge`, IDs `O1`, `O2`, …. A fit is numeric and solution-free. The gauge says where the number is read and when it cannot judge (E1). Name the binding constraint (quota, attention, tokens) and gauge it (E2).
   - **Non-goals and authority limits**: what it may not touch or decide. Mark each one-way door (data loss, messages outside the project, production, spend).
   - **Attention budget**: when it may speak to a person, and the one acknowledgement it may send on new explicit work. Nothing else is a message (A1, B2).
   - **Initiative**: which inferred work it may take up, each rule starting in observe mode.
   - **Decides**: who owns each open choice. Mark unresolved values `[TK]`.
2. Check the outcomes against each other: a lever counted against its own target is a contradiction (E3).
3. Load `goldfish-review`:
   - artifact: `.minime/<agent>/brief.md`
   - intent: the human's request, quoted verbatim
   - question: paraphrase what this agent is for and what it may never do; which outcome cannot be measured as written; which two parts contradict?
   - blocking rule: a reviewer cannot paraphrase a section, an outcome has no numeric fit, or two outcomes contradict
   - output: `.minime/<agent>/brief-review.md`

   A comprehension gap cannot be contested: fix the text. Fold verified findings; rerun when an outcome or limit changed. Then write `brief-review.json` as `{"artifact": "<python3 \"$NEXT\" <agent> --hash brief.md>", "findings": "<… --hash brief-review.md>", "status": "clear"}` once every verified blocker is fixed or declined (see `recruit`).

Done when `brief.md` has no `[TK]`, every outcome has a numeric fit and a gauge, and `brief-review.json` is clear for the current `brief.md`.
