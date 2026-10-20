# Staged delivery loop — kilo-mms house style (v2)

Goal: intent → plan → build → prove → converge → land, with validation correcting every stage, ending in a small reviewed change. Uniquely ours: rewritten to Russell's maxims (INTENT.md), not vendored copies. Sources are inspiration with links, never pasted.

House rules (from `workspace-sdlc-skills`):
- No evidence, no skill. Reputation is not proof (`INTENT.md` §How a change gets in).
- Budget always-on load; additions compete for cap (`[[machinery-ratchet]]`).
- Model proposes, deterministic gate disposes (`[[propose-and-gate]]`, `[[pipeline-with-agent-steps]]`).
- Graph for process, agent for step; stops/rounds capped outside model (`[[review-convergence]]`, Stripe 2-round cap).
- Fresh context per stage, thin supervisor holds IDs/refs never diffs; hand off via files (`[[fresh-context-dispatch]]`, `[[isolate-execution-share-knowledge]]`).
- One writer, readers in parallel (`[[one-writer-many-readers]]`).
- Skills are thin wrappers; mechanics in scripts, judgement in markdown; shrink as models improve (`[[skill-structure]]`, `[[skills-as-process]]`).
- Router hints, never fires; shared refs live outside skill system (`[[user-invoked-vs-model-invoked]]`).
- Write for reader: pointers, hierarchy, completion criteria, existing leading words, prune by no-op test (`[[writing-for-agents]]`).
- Removable overlay: deletes cleanly, repo conventions win (`[[removable-overlay]]`).

## Proposed loop (5 stage skills + 1 router, model-invoked except router)

### 1. `clarify` (user-invoked entry) — intent that survives contact
Inspired by: grilling rounds/frontier + grill-with-docs GLossary/ADR habit; SME `essence-of-business-work` (ask why until tech-free need), `requirement-vs-design-decision` (what+how-well, never how), `fit-criterion` (one numeric solution-free measure or unfinished), `precommitted-evaluation-criteria` (≥3/10 not "some"), `opportunity-solution-tree` (≥2 mechanisms or comparison skipped), `pyramid/SCQ/R1-R2` shape.
Does: short rounds; facts via researcher, decisions via human; emits Destination, Decisions, Fog (not-yet-specified), Out-of-scope, outcome AC with fit criteria + rationale per req (gold-plating detector: rationale restating req = flag).
Completion: frontier empty OR user says proceed with Fog explicitly accepted; zero `[TK]` before handoff (`verification-markup-conventions`).
Gate (deterministic): AC table has IDs O1… with one numeric fit each; solution words flagged.
Does NOT: write spec, tickets, or code.

### 2. `chart` — map small enough to build
Inspired by: wayfinder decision-tickets + blocking edges + frontier; to-spec/to-tickets tracer-bullet; SME `story-splitting-patterns` (workflow steps, rule variations, entry method, defer qualities), `INVEST` (unestimable → split or spike), `spike-story` (question+timebox, dependents in later iteration), `reversible-doors` (depth scales with door type), `good-enough-requirements` (spend where wrong costs most).
Does: emits ordered tickets, one context-window each; marks blocking; tracer-bullet first.
Completion: every ticket INVEST-passed or marked spike; traceability O→R→S with orphan list empty.
Gate: schema check fields present + orphan/dangling count = 0.
Does NOT: implement.

### 3. `build` — smallest complete diff
Inspired by: ponytail ladder (skip → reuse codebase → stdlib → installed dep → one-liner → minimum), pstack laziness/subtract/minimize-reader-load, SME `speculative-generality-smell` + YAGNI, `collapse/inline/strip` cures, Karpathy surgical changes.
Does: one concern per change; states proof plan up front (test/check/calc reviewer can rerun); marks `shortcut: <limit>, <when to upgrade>`.
Friction reducers (rewritten, not pasted): `tidy` — strip unneeded docs/comments on touch (only non-obvious why stays, one line; delete speculative prose not added this change); `quiet` — don't-bother-the-human: decide two-way doors alone, batch questions, never stop for reversible choices; `replan` — dynamic replan where door is two-way: adjust tickets inline, note delta in one line, no re-clarify round.
Completion: `ci.local_command` green + small test for non-trivial logic + proof artifact kept re-runnable.
Gate: tests/lint/type gate in CI/hook, not prose promise.
Does NOT: add option/config/abstraction unasked; never cut trust-boundary validation, data-loss handling, security, a11y, anything asked.

### 4. `prove` (continuous, called inside every stage) — real artifact or rumour
Inspired by: `[[prove-it-works]]` (real artifact not proxy, suspect observation before system, deterministic script over eyeball), `working-software-as-status-evidence`, MAST +15.6% for verification step / 17% missing-verification failures, SME `defining-checkable-claims` + `negation-test` + `claim-scope-calibration`.
Does: names proof before work; shows proof not summary; perf claims carry limiter + median/range + verdict faster/slower/no-diff/inconclusive.
Completion: each unit ends in a check (`sequence-verifiable-units`).
Gate: holdout scenarios outside repo where it matters; "tests passed/agent said so" is not done.
Does NOT: infer from compile or self-report.

### 5. `converge` — review that ends + approve that means it
Review half (fresh context reader): checks conventions/structure/tests/docs, NOT AC. Inspired by `[[review-convergence]]`: recurrence ≠ convergence (same class back → fix root once or narrow rule), one structural finding per root cause, fix fact not sentence (verify vs source, declined needs reason), move mechanical to CI, reviewer-side volume cap (Important only break/leak/breach; nits ≤5 rest counted; never report CI-enforced), pertinence test (must say which core claim it undermines).
Approve half (fresh context): mechanically re-derives AC per-criterion pass/fail/unproven with evidence; never edits/merges.
Rounds: 2 standard fix rounds (outside cap, in pipeline/hook). Round 3 is MMS escalation shape, not a third fix attempt: fresh advisor-model context does step-back analysis — structural issues, root cause, recommended refactor direction — and returns one advisory brief. Implementor then acts once on the brief or escalates to human. 3+ same cause → human. Cap never lives in fixer prompt.
Completion: approve table all pass with evidence + reviewer verdict approve.
Gate: branch protection/human merge gate; findings propose, gate disposes.

### 6. `land-learn` + router `deliver`
Ship: rebase small ordered commits → babysit (conflicts/threads/CI one batched push, stop at merge-ready) → fresh-agent verify per PR, land contiguous verified bottom-up. Default-branch merge always human.
Learn: compact handoff to `$TMPDIR` (reference don't duplicate, suggested-skills, redact secrets) + retro on environment not product (Navigation/Checks/Standards/AGENTS/Tool-economy/No-ops/Info-access; mechanical→linter/hook/CI, judgement→CODING_STANDARDS).
Router `deliver` (user-invoked, `disable-model-invocation: true`): names the five above so human remembers one name; copies steps verbatim into todos; never calls another user-invoked skill.

#### 6a. `babysit` (gap added 2026-10-20 after PR #4 pilot exposed it)

Inspired by cursor pstack `playbooks/babysit.md` + `autopilot-full.md` (github.com/cursor/plugins) and cursor's built-in `/autopilot` (monitors a PR, addresses feedback, conflicts, failing checks). Rewritten in our words per house rules; sources are inspiration with links, never pasted. The single babysit sentence in §6 was the whole spec — the PR #4 pilot ran babysitting ad hoc and external-review triage had no home at all. Gap: no named stage owns diff-ready → merge-ready.

Does:
- **Declare the mode in the first line** (pstack): `drive` = run to merge-ready; `check` = one status pass + report (small/docs-only PRs); `threads-only` = answer review comments, touch nothing else. Undeclared → `check`, NOT drive — pstack default-drive stalled parent agents; we invert it.
- **Merge frontier only**: the lowest unmerged PR is the only one that matters until it merges; nothing upstack while the frontier is red. One watcher per stack; fixes land on the owning branch only.
- **Order: conflicts → review threads → CI**, batched into ONE push wave (each restarts checks; earlier CI work is thrown away otherwise). Fix-forward; one writer per branch.
- **Compass check at every tick**: re-read the task's destination (acceptance.md / armed goal) before acting on findings; loop-vs-goal drift is a blocker, not a nit.
- **Conflict resolution rules**: trunk merges/rebases INTO the branch, never force-push of shared branches; `--force-with-lease` pinned to last-pushed SHA when force is genuinely needed (own branch only). Ambiguous conflict (both sides changed logic) → report, don't guess. A defect trunk shows without the PR is trunk's; a defect the PR introduces or newly reaches is the PR's.
- **External review triage** (bugbot/Kilo Code Review/human): every finding classified fix / decline-with-reason / escalate; decline requires the `converge` pertinence test (name the core claim it would undermine). External findings use the shared `.kilo/run/<task>/review-round` counter: never reset it, increment it per fix round, and route to the round-3 advisor shape when the two-round cap is reached.
- **Stop conditions**: green checks + threads triaged + conflict-free + fresh-agent approval re-derived at the final head after every base update (trunk move, rebase, conflict resolution) = merge-ready → human merge gate; patch-id may detect an unchanged diff to skip duplicate *review*, but never substitutes for re-approval at the head that will actually merge; babysit never merges. 3 fix-push-check cycles without resolution → report what still fails. Fix needing a design decision → human. A push on the branch you did not make → stop and report.

Does NOT: merge (human gate, §6); restart CI on speculative fixes; touch upstack PRs; own defects trunk already has.

Completion: merge-ready report — final head SHA + checks green + per-finding triage + approve table valid at that SHA.

## Two tracks: plugin workshop (us) vs consumer loop (them)

Workshop-only (develop the plugin; never shipped as consumer requirements):
- Admission eval, budget-matched comparison, hill-climb log, component/tool/ACI ablations, maintenance eval wiring, Brier tracking, scoring hygiene. These are our lab for deciding what earns a place.
- Rule: nothing becomes consumer-mandatory because we used it in the workshop. A workshop win graduates to consumer only as a small skill/gate with its own completion check.

Consumer loop (what a user runs): `clarify → chart → build → prove → converge → land-learn` via router `deliver`. Light by default:
- `clarify` skippable: proceed with Fog explicitly accepted; no forced rounds.
- `chart` optional for one-ticket work; tracer-bullet only when it helps.
- `build` + `prove`: only consumer-mandatory gates are tests/lint green + re-runnable proof artifact + small test for non-trivial logic.
- `converge`: reviewer caps + approve table + human merge gate; no eval/ablation language leaks into consumer prompts.
- Overlay stays removable: deletes cleanly, repo conventions win, no required telemetry/config in consumer repos.

## Evidence & tuning (workshop only; informs but never burdens consumer)

- Admission eval per candidate: 20–50 real failed tasks from PR/session history; with vs without skill on same task; precommitted pass threshold; scored separately coverage/restraint/retention/actionability/convergence (review-guidance method: known violation + safe counterexample + unrelated case).
- Budget-matched (`[[budget-matched-comparison]]`): record tokens + wall time beside pass rate; single agent given same budget as control. Gain vanishing at matched budget = cost not skill.
- Intermediate artifacts scored separately (plan/outline coverage before final output; Shao et al) so discovery vs drafting failures don't hide.
- Hill-climb (pstack `hillclimb`): frozen harness, one hypothesis at a time, decision log, one commit per win. Start minimal, add only winners.
- Ablations (agentic-engineering-wiki): component-level (hold 3/4 at seed, keep 1 evolved — prompt-only expected regression per Lin et al; watch non-additive redundant re-checks), tool-selection (remove tool → measure drop; if none drop it; replace chronically misused; Huyen ch6), ACI pieces (guardrailed edit+lint, summarized multi-hit search, ~100-line viewer, collapsed history; SWE-agent §4–5).
- Maintenance eval (light, in kilo-mms): reruns on any `AGENTS.md`/skill/hook change + every incident adds a permanent case; saturated non-discriminating cases are removal candidates except incident regressions (kept).
- Measures for a decision only (`[[measure-for-a-decision]]`): forge/tracker DORA-style (bot findings unanswered at merge, time-to-merge). No new loop telemetry — rgh-mms telemetry never retuned a setting.
- Grades travel: every claim carries high/medium/low (`[[evidence-grades]]`); ungraded = rumour. Calibrate LLM judge vs deterministic checks + human verdicts; track Brier vs naive baseline.
- Scoring hygiene (SME): binary gates + per-dimension findings/counts, never weighted-sum ordinals; trait-by-trait blind then overall last; simple checklist over holistic 8/10; LLM flags broken-leg overrides only.

## Build order (implementor tasks)
1. Consumer MVP: router `deliver` + `clarify` (skippable) + `build` + `prove` + `converge` skeleton. Thin wrappers, shared refs in plain files. No eval/ablation strings in consumer prompts.
2. `chart` (optional path; required only for multi-ticket work) + `land-learn` (ship gates + handoff/retro templates).
3. Workshop harness (separate dir, e.g. `.kilo/workshop/`): admission suite (20–50 cases, with/without runner, budget-matched logging, precommitted thresholds) + hill-climb log + ablation scripts. Never installed into consumer repos.
4. Pilot: 1 consumer end-to-end (proof artifacts + approve table + human merge gate) + 1 workshop admission run.
5. First ablation pass; delete losers; tighten `AGENTS.md` to build/test/gotchas only.
6. Maintenance eval wired to config-change trigger (workshop side).
7. `babysit` skill (§6a) as its own stage, once PR #4's external-review triage lands as evidence: shape the skill from what the ad hoc run actually needed; keep the caps and one-push-wave discipline; decide then whether babysit stays inside `land-learn` or splits out (split likely — it has its own completion check and its own stop conditions).

## Risks
- Workshop stricture leaks into consumer UX → mitigate: separate dirs/prompts; grep CI for eval/ablation terms in consumer skills.
- 6 skills still load-bearing → router + short descriptions + progressive disclosure; no-op test every line.
- pstack model-tiering doesn't map to Kilo → provider-neutral, single-agent default, parallel readers only.
- Pocock do-not-vendor 1.3.1 + ponytail 5.3.2 + pstack 0.15.26 move upstream → link, rewrite own words, re-count only when decision needs it.
- Prompt-level gates erode (`[[propose-and-gate]]`) → prefer hook/CI enforcement; persona prompts only as eval baseline.

## Open
- MVP-first (clarify/prove/build/converge) vs full six upfront? Recommendation: MVP-first per lean-MVP maxim + hill-climb method. (2026-10-20: resolved, MVP-first.)
- Where does workshop live (`.kilo/workshop/` vs separate repo)? Recommendation: `.kilo/workshop/` for now, excluded from consumer install. (2026-10-20: resolved by pilot payload definition.)
- Maintenance eval trigger location (`.kilo/evals/` vs CI job)?
- Babysit placement (§6a): inside `land-learn` vs standalone skill — decide at step 7 from PR #4 evidence.

Validation: consumer pilot shows proof artifacts + approve table + human merge gate with zero workshop terminology visible; workshop admission numbers decide each graduation; anything without measured with>without gain is removed.
