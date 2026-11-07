---
name: goldfish-review
description: Use when a recruit artifact (brief, role, routines, a wake chart or an agent package) needs review before the next stage. Parallel goldfish reviewers read only the artifact and its sources, never the conversation; you merge and verify their findings. Called by brief, role, routines and chart.
---

# goldfish-review

A **goldfish** is a fresh `reviewer` agent with no conversation history: it sees only the artifact, the sources it references, and the brief. A review in your own context is not a goldfish review.

The caller supplies: the artifact path(s), the intent (what the artifact must serve, one level up), a question, the blocking rule, and an output path.

1. **Dispatch.** Start 3 fresh `reviewer` agents in parallel, in one message, using different model families where the client allows. Give each the brief below and nothing else: no summary of the conversation, no earlier rounds, no author reasoning. If the client cannot start a fresh agent, stop and tell the user why.

   > Review `<artifact>` cold. Read it, `AGENTS.md`, and the files it references or changes; reproduce its recorded checks. Intent: `<intent>`. Judge the artifact against it; do not review the intent itself. Question: `<question>`. Report each finding on one line: `- blocking|advisory — <file:line> — <problem> — <effect> — <remedy>`. Blocking means: `<blocking rule>`. Everything else is advisory. Skip duplicate formatting/lint findings enforced by CI; still assess correctness, assertions and coverage. End with one line: `verdict: approve` or `verdict: changes`.

2. **Collect.** A reviewer that fails, times out or returns no report did not review: retry it once with a new fresh agent, then mark it `not run`. Never count `not run` as approve. With fewer than 2 verdicts, the review is incomplete: write `review: incomplete` at the top of the output, and the caller treats it as blocking.
3. **Merge.**
   1. Group findings by root cause: one finding per cause, with how many reviewers raised it. Agreement is a triage signal, not independent corroboration; reviewers can share correlated errors.
   2. Verify every blocker against the current source and accepted intent; retain it only with reproduction or source evidence, otherwise decline with a reason. When assessing disputed findings or response diffs, load [finding triage](references/triage.md). Record the finding's disposition separately from the proposed remedy's suitability.
   3. Keep at most five advisory findings and count the rest.
   4. Put any trade-off that needs a human decision in one batched question.
4. **Write the output file**, keeping the one-line finding format: blocking, advisory, declined with reasons, questions for the human, and each reviewer's verdict or `not run`.

Done when at least 2 reviewers returned a verdict (otherwise the output says `review: incomplete`), every other reviewer is marked `not run`, every blocking finding is verified or declined with a reason, and the output file is written.
