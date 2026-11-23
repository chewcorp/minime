---
name: converge
description: Use when a delivery-loop diff is ready for review. Runs a goldfish review, an independent user-path verification and a separate approver against the acceptance criteria, and escalates repeated causes and structural changes. Never edits or merges.
---

# converge

Work in `.minime/<task>/`. Require build's completed commits on `<task>`, so the diff reviewers see is the one `land-learn` ships. Run `python3 "$GATE" <task> review` using the [gate contract](../deliver/references/gates.md); stop on nonzero. It requires every ticket complete and a clean tree. Capture its printed scope token and tree before dispatch, and give both to every reviewer and approver; do not recompute or relabel earlier results. See [review boundaries](references/boundaries.md) for escalation rationale.

## 1. Review

Load the `goldfish-review` skill:

- artifact: the diff `git diff <base>...<task>` and `.minime/<task>/proof.md`
- intent: `.minime/<task>/acceptance.md` and the tickets in `tickets.md` this diff implements (or the issue text)
- question: does this change do what it claims without breaking anything, and does each `proof.md` row reproduce at the head?
- blocking rule: it breaks behaviour, regresses behaviour the repo already supported, leaks data, breaches a rule `AGENTS.md` states, or a `proof.md` row does not reproduce. New unsupported inputs (pathological sizes, fuzzing) are advisory.
- output: `.minime/<task>/review.md`

Record the captured scope token and tree in the finished report and register
`review all` with both values:
pass only for a complete review without a verified blocker; otherwise fail or
unproven. Historical-tree rows need not reproduce at this head; current claims do.

Advisory findings go in the report, not a fix round.

## 2. Verify as a user

Run this alongside section 1. The author's own checks are leads. Dispatch one more fresh `reviewer` with only the outcome IDs, their acceptance examples, captured scope token, captured tree and the repo: it drives each changed feature through the real entry point (using the repo's verification skill, such as `verify-<app>`, when one exists) and returns pass, fail or unproven per outcome using `prove`'s command or interaction evidence format. Append its rows to `proof.md`, marked `independent` with both captured values. Finish the report before registering each outcome's aggregate independent result with the gate.

## 3. Approve

Dispatch one fresh `approver` agent with the captured scope token and tree, `.minime/<task>/acceptance.md` and `.minime/<task>/proof.md`. Save its table as `.minime/<task>/approval.md`: one row per outcome ID, scope token, tree, pass/fail/unproven, and evidence. Run it after sections 1 and 2 finish; register its results with both captured values. Run `python3 "$GATE" <task> ready`. On failure, distinguish missing/stale evidence (rerun sections 1–3 without spending a repair round) from a verified defect (section 4). Never treat an earlier-scope/tree failure as a current blocker or an earlier pass as approval.

## 4. Triage before fixing

**Triage before charging a round.** Dismiss unsupported findings with evidence;
they leave the repair counter unchanged. Missing evidence requires checks, not a fix.

For each verified blocker, record the root cause, affected sibling paths, accepted scope, proposed remedy and supported behaviour that must remain valid. Decline incompatible requests with evidence and a compatible alternative where possible; do not silently change acceptance criteria. An acknowledged unmet guarantee stays open until repaired or explicitly changed by the human. Explanation and deferral are not repair.

If a remedy changes accepted outcomes or the solution's structure, or no longer fits one buildable ticket, stop converge. Write the failing case, preserved behaviour, options and required decision to `review.md` and hand it to the human. A ruling determines whether to revise the design through `clarify`/`chart` or re-cut the PR; there is no automatic mid-round resume.

If the same cause returns after a repair, stop before admitting another repair. Hand the failing evidence to the human, and dispatch the `advisor` for one step-back brief when that escalation needs a refactor direction. There is no automatic resume. A ruling can approve one more bounded repair of that cause, which then uses the `fix` admission below and does not update the ledger by itself, or send the work through `clarify`/`chart` or a re-cut pull request when the remedy is no longer bounded.

Small bounded repairs proceed below, including a repeated cause only after that ruling. The coordinator never implements them itself.

For a verified bounded repair, run `python3 "$GATE" <task> fix 'blocker and remedy'`
**before editing**. When a human reviewer requested the repair, add `--by human`.
Approval to retry a bot finding keeps the bot command. A human admission leaves
the bot counter unchanged. On nonzero, including when the gate's bot repair cap
is reached, stop and hand off. Never reset the ledger. An interrupted active
admission is idempotent. Landing and CI fixes use this same path.

## 5. Fix rounds

1. Use the round admitted in section 4; do not increment again. Apply its triage to the advisor's remedy too. Dispatch a fresh `implementor` with the verified blockers, triage brief and advisor brief when present. It searches the failure family, fixes the cause within scope, and loads `build` and `prove`. Verify both the defect and preserved behaviour; inspect the response diff for new failures and incomplete remediation.
2. Require build's complete committed repair, then resume through the [gate's repair-completion transition](../deliver/references/gates.md#one-repair-path). Rerun sections 1 to 3 with new agents against that head. Earlier-head evidence does not approve a response diff. If blockers survive, return to section 4. A context limit leaves blockers unresolved and the PR not merge-ready; hand off the failing evidence rather than skipping verification.

Done when `ready` passes for the clean current tree and accepted scope: complete
goldfish review, passing independent evidence and approval for every outcome.
Forge checks and human merge remain land-learn's responsibility.
