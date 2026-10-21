# Workshop Stage 5 Remediation Chart

Status: S01a-S01c implemented and locally approved; S02 investigated but
unproven; dependent implementation blocked. Updated: 2026-10-21.
Scope: checkpoint PR #5, complete the prerequisites for a real first ablation
pass, then make an evidence-backed instruction decision. Human merges only.

## Execution Checkpoint

- Recovery/publication branch: `workshop/stage5-foundation`, repaired from
  frozen PR #5 HEAD `17b52eae21d74f57b8c34b1ffa0f62e17e076d25`.
  Foundation repairs committed as `d0a43d4e` after the local approval below;
  publication and babysitting are now explicitly authorized. Final published-head
  verification and human merge remain required. The original checkpoint facts
  below describe chart creation, not current publication status.
- S01a complete: source-grounded review dispositions, including stale findings
  and intentionally bad fixtures, in
  `.kilo/run/workshop-stage5-foundation/triage.md`.
- S01b/S01c complete locally: independent proof reran 13 sweep contracts and
  11 native-runner/oracle tests, zero failures or skips. All 14 reviewed files
  match patch SHA256
  `15ddf94ea4fe6a8497700893ba8885296b26682cb7c5105ee11332d3ad22d567`.
  Six frozen targets and all 75 historical rows remain unchanged.
- Two scoped source reviews approve; fresh acceptance approval passes all 14
  criteria. Evidence: `.kilo/run/workshop-stage5-foundation/{review.md,approval.md,prove-recovered/proof.md}`.
  Nonblocking advisory: sweep tests do not yet cover full dispatch arguments
  across multiple cases/panel entries. No live model-evaluation evidence exists.
- S02 investigation ended within its timebox, acceptance **unproven**, adapter
  choice **none**. Report:
  `.kilo/run/workshop-stage5-foundation/s02-runtime.md`.
  CLI selection/events are interface evidence, not proven confinement, complete
  resolved-arm capture or aggregate usage/limit enforcement. PR #14 supplies
  corpus/rubric material but no real task-execution runner.
- S03-S11 remain blocked by the original graph. The follow-up below is a
  proposed later iteration, not permission to bypass S02 or build a framework.
  At recovery approval no commits, pushes or PR changes had been performed;
  subsequent publication is separately authorized. No merges, installs or live
  eval calls are authorized by that publication request.

## Checkpoint

- PR: https://github.com/xchewtoyx/kilo-mms/pull/5
- Branch: `workshop/model-panel-and-retirement`.
- Frozen review head: `17b52eae21d74f57b8c34b1ffa0f62e17e076d25`.
- Main at chart creation: `1f4ebdd55de79e02d55a1519e9240e70d6e33588`.
- PR #5 is nine commits ahead and one behind that main; its code is unchanged
  by this chart. The existing untracked `.conda/` is unrelated and untouched.
- This chart is on `plan/workshop-stage5-remediation`, based on main. No
  checkpoint commit, tag, push, PR mutation, or evaluation is performed here.
  The existing remote PR head is the code checkpoint; this file is the local
  durable record, pending a separately requested commit.
- Scope is the original plan's **build-order step 5**, not consumer stage
  `converge`: first ablation pass, delete losers, tighten AGENTS to
  build/test/gotchas. Step 3 supplies the harness; step 4's PR #4 pilot and
  PR #5's failures supply incidents. Step 6 maintenance wiring and step 7
  babysit skill admission remain later work.

Observed at the checkpoint: review checks report success/neutral, but the latest
Kilo review still recommends changes. There are 25 inline threads, 18 unresolved
(five of those outdated), plus outside-diff findings. These counts are a
snapshot, not an instruction to make 18 code changes.

## Evidence And Limits

- Existing results: 75 JSONL rows, 57 stamped and 18 legacy unstamped. These
  demonstrate deterministic fixture replay, not 57 executions of the named model.
- `--model`, `--provider`, and component labels do not execute a model or remove
  an instruction. Full/without and panel inputs are currently identical.
- Default retirement refuses placeholder evidence; `RETIRE_ARM_REAL=1` bypasses
  that refusal without implementing a real arm. Invalid/empty evidence guards
  have already been improved and should be preserved.
- Confirmed eval defects: contradictory release-order predicates, rejection of
  correct comma-space prose, and rejection of identity-guarded recursive copying.
- Confirmed shell defects: missing arguments collide with verdict/block exit 1;
  retirement panel entries are not validated consistently.
- Prior verification: predicate probes, shell syntax, whitespace checks, and
  isolated sweep-contract tests. Native macOS full-run verification was limited
  by pre-existing GNU grep/date assumptions. None is model-effectiveness evidence.
- Historical material: PR #4 review, its frozen code and failure/fix commits,
  PR #5 review comments and this checkpoint's failure/fix-counterexample probes.
  S03 records exact provenance; do not invent missing pilot measurements.

## Destination And Fits

| Outcome | Fit criterion |
| --- | --- |
| O1 Trusted experiment | One real vertical tracer, then 36 adjudicated cases; every case has a known-bad and a valid counterexample for its oracle, and zero subject writes to scoring/evidence storage. |
| O2 Current-instruction diagnosis | Every frozen case x active panel entry x arm x declared repeat has attributable execution evidence or an explicit invalid status; all five scoring dimensions reported separately; zero fixture-only rows counted as model measurements. |
| O3 Successful first ablation pass | At least one pre-registered instruction/component hypothesis is tested with current, absent, and candidate arms at the declared budget; adopt, reject, retain, or pending-human retirement is justified per model. A measured rejection/no-change is a valid outcome. |
| O4 Safe delivery and subtraction | Zero unsupported graduation/retirement decisions, zero automatic merges, zero workshop payload leakage; each adopted change has passing final-head approval and a permanent incident regression case. AGENTS changes preserve operational/trust-boundary requirements. |

Precommitted scoring dimensions: coverage/correctness, restraint, retention,
actionability, convergence. Verification/provenance is a validity gate, not a
sixth weighted score. Unknown/not-observed is never a pass. Score discovery
separately from repair so an accurate diagnosis cannot conceal a broken patch.

## Requirements

| Requirement | Outcomes | Contract |
| --- | --- | --- |
| R1 Honest foundation | O1, O4 | PR #5 is an explicitly non-admitting foundation; no environment override can turn unchanged arms into retirement evidence. Preserve historical rows but exclude them from live comparisons. |
| R2 Real execution boundary | O1, O2 | Reuse a supported Kilo execution surface; fresh isolated task checkout/context per arm, actual model execution, captured model/provider/instruction revision/budget and produced artifacts. |
| R3 Discriminating corpus | O1, O2 | 27 core cases in nine incident-derived triplets plus nine sealed variants; executable, adjudicated oracles and provenance, not text presence alone. |
| R4 Valid measurement | O2, O3 | Frozen harness/corpus/panel and precommitted budgets/thresholds; matched arms; all missing/error/budget-unknown cells invalidate the affected decision. |
| R5 Controlled instruction experiment | O3 | One hypothesis and one instruction/component delta at a time; identical evaluators across arms; no prompt addition unless current instructions demonstrably need it. |
| R6 Human decision and retention | O3, O4 | Weakest supported model cannot be hidden by pooling; retirement requires valid per-model equivalence/no-regression evidence and human resolution; incident regressions stay. |
| R7 Ordered, bounded delivery | O4 | Bottom-up stacked PRs, one writer per branch, no upstack fix waves while the frontier is red, reapproval after base/head changes, no maintenance service or deployment added. |

## Experiment Boundary

A real case supplies a frozen input repo/task, tools and execution constraints,
and a hidden evaluator. The subject agent reviews or changes the task's actual
files; an independent evaluator runs commands against the produced artifact and
checks the structured decision. It must not grade the agent's success claim.

Task fixtures are legitimate experimental inputs. Replaying greps against an
unchanged target is only a checker smoke test. Fake adapters are allowed for
runner unit tests, never for live evaluation rows.

- Keep evaluator/oracle data and holdout answers outside the subject's readable
  checkout and tool scope. Subject agents cannot modify checks, manifests,
  accepted-result rows, or the evidence store. Treat case/review text as data.
- No real releases, pushes, credentials, or destructive host operations by
  default. Use real local Git repos/remotes and real file operations for those
  contracts. Controlled service doubles prove only their explicit scope; real
  external-integration claims need a separately approved disposable integration.
- Actual model budgets and wall time include dispatched work. No unmetered
  retries or hidden reasoning-budget advantage. Cancel/error paths stay visible.
- Evidence persists beyond `/tmp`: retain a small manifest, hashes, commands,
  source and instruction revisions, runtime identity, usage, and redacted
  artifact/transcript locations. Do not duplicate bulky raw runs into JSONL git
  history or claim a declared model label proves runtime identity.
- The absence arm removes only the targeted instruction/component from agent
  input, never an evaluator check. Keep task, tools, limits, and evaluator fixed.
- Require separate decision/diagnosis and repair artifacts where relevant.
  Convergence is `not_observed` until fresh reviewer/fixer rounds are exercised.

## Corpus Map

Each family has violation, safe-negative, and unrelated task variants. The nine
extra held-out variants rotate across those polarities (three of each overall)
and alter wording/layout/identifiers. They are sealed before instruction tuning;
their individual results are not exposed during candidate selection.

| Family | Violation | Safe-negative | Unrelated | Candidate owner |
| --- | --- | --- | --- | --- |
| F1 Evidence scope | Stubbed release run claimed as live integration. | Stub is accurately scoped to argument/order testing; integration unproven. | Pure local calculation needs no remote service. | prove |
| F2 Check the checker | Bad-only fixture replay hides an unsatisfiable oracle. | Bad fails and repaired passes through the real oracle. | Valid oracle exposes a product bug and must not be weakened. | prove/converge |
| F3 Comparison authenticity | Relabelled identical arms/model inputs claimed as causal evidence. | Attributable real executions with unchanged outputs reported as no observed gain. | Metadata round-trip is correctly labelled a smoke test. | prove |
| F4 Weakest-model decision | Strong model masks weaker-model regression in a retirement recommendation. | Complete valid panel evidence supports only a human retirement proposal. | Schema change calls for no retirement decision. | prove/converge plus gate |
| F5 Incomplete evidence | Empty/error/unproven/unmetered comparisons justify retirement. | Valid complete comparisons support a bounded decision. | Unknown tokens are acceptable in a declared non-admitting smoke test. | prove plus gate |
| F6 Source-grounded triage | Review warning causes intentional bad fixture to be repaired away. | Same defect in production code is verified and repaired. | A source-verified stale finding is declined without needless edits. | converge; future babysit evidence |
| F7 Repair retention | Release reorder leaves contradictory current docs/rerun instructions. | Behavior and relevant prose agree, including normal punctuation. | Historical release notes correctly retain past behavior. | build/prove |
| F8 Minimal safe repair | Self-copy repair disables valid installs or removes necessary copying. | Identity guard and distinct-destination install both work. | Legitimate recursive copying is left intact. | build |
| F9 Comment restraint | Production headers accumulate fix history and abandoned approaches. | A concise non-obvious why/current limit remains. | Changelog/decision history is left intact. | converge |

F4/F5 may provide precomputed comparison evidence to a decision-making subject;
they are real reasoning/action tasks, not a claim that the embedded records are
new model executions. Keep that task data distinct from outer-run provenance.

Mechanically test the evaluator itself with counterexample/mutation probes:
correct/broken operation order despite misleading marker comments; guarded and
unguarded installs; equivalent prose; contradictions; missing artifacts; altered
oracles. A lintable/mechanical failure belongs in code/CI, not extra prompt prose.

## Stack And Blocking Edges

These are proposed PR boundaries, not created PRs. The first new implementation
is a vertical tracer, not a large fixture/schema framework. S01a-S01c bound the
repair of already-open PR #5; S02 is the only unestimated runtime investigation.

| PR | Branch suggestion | Base while stacked | Tickets | Deployable result |
| --- | --- | --- | --- | --- |
| A: existing #5 | workshop/model-panel-and-retirement | main | S01a, S01b, S01c | Honest, tested, non-admitting foundation. |
| B: live tracer | workshop/live-eval-tracer | A | S02, S03, S04 | One real incident task end to end with validated oracle/provenance. |
| C: case suite | workshop/incident-eval-suite | B | S05, S06, S07 | Frozen 36-case suite with adjudicated expectations and sealed variants. |
| D: baseline | workshop/instruction-baseline | C | S08, S09 | Budgeted current-vs-absent runs and a gap report; no consumer changes. |
| E: first ablation | workshop/first-instruction-ablation | D | S10 | One preregistered candidate/component experiment with blind scoring. |
| F: stage-5 decision | workshop/stage5-decision | E | S11 | Measured instruction decision, incident regressions and justified cleanup. |

Blocking graph:

```text
S01a -> S01b, S01c
S01b + S01c -> S02 -> S03 -> S04
S04 -> S05, S06, S07
S05 + S06 + S07 -> S08 -> S09 -> S10 -> S11
```

S05-S07 have independent case scopes; one author writes their shared branch, or
use isolated child branches and integrate serially. Nothing requires concurrent
writers. Only the lowest unmerged PR is actively babysat. Merge bottom-up after
human approval; retarget descendants and verify at the actual final head. These
are local workshop capability rollouts, not production releases or live deploys.

## Tickets

All tickets except the marked spike are intended to fit one implementor context.
Split again if actual exploration exceeds the stated boundary. Sizes are
relative (S/M), not commitments to elapsed time or model spend.

| Ticket | Requirements | Depends on | Size / proof |
| --- | --- | --- | --- |
| S01a Triage checkpoint findings | R1, R7 | checkpoint | S: Source-grounded fix/decline/escalate disposition of existing inline and outside-diff findings; distinguish deliberate bad fixtures and fixed/stale findings. Confirm S01b/S01c scopes and sizes before either starts; split newly discovered larger work rather than silently expanding them. No implementation in this ticket. |
| S01b Repair PR #5 boundary | R1, R7 | S01a | M: Fix exit-code collision, panel validation and resolution wording; hard-disable unsupported retirement; qualify PR/README/result claims. Contract tests cover missing args, malformed panels, no cases, invalid arms, and disabled proposals. Preserve historical data without admitting it as live evidence. No LLM framework or consumer instructions. |
| S01c Repair seed oracles | R1, R3 | S01a | M: Repair the three existing seed-case predicates with independently checked broken/repaired counterexamples; show correct operation order, natural prose and identity-guarded copying discriminate. Permit one small stdlib Python matcher with optional line/document scope and stdlib replacement of GNU-dependent timing/unique IDs in the existing admission entry point, so actual-run proof works on native tools without installs. Document Python regex syntax; preserve CLI, row schema, polarity and intentional bad targets. No arbitrary evaluator commands, shell parser, framework, or live execution adapter. This ticket repairs bounded source-pattern smoke validity, not model measurement. |
| S02 Runtime reuse spike | R2, R4 | S01b, S01c | SPIKE, 60 minutes: identify the smallest existing Kilo surface that can run an isolated task with chosen supported model, resolved instructions, bounded usage, tool restrictions, and durable artifacts. Inspect the referenced workspace-sdlc-skills PR #14 suite/runner for reusable compatible evidence before duplication. No paid calls without explicit budget authorization. Output capability table, one adapter choice, gaps and updated S03/S04 estimate; no general framework. If unresolved, stop and rechart dependents for a later iteration. |
| S03 Freeze tracer contract | R2, R3 | S02 accepted | S: Select F8 self-copy incident from PR #4, record exact failure/fix SHAs and task boundary; prepare a real temporary install task plus independent self-install/distinct-destination assertions; demonstrate oracle rejection of broken output and acceptance of valid repairs. Freeze one absent/current prompt pair and evaluation interface. |
| S04 Execute vertical tracer | R2, R4 | S03 | M: Before any model call, demonstrate tool-boundary denial of oracle/holdout reads and scoring/manifest/evidence writes, bounded execution, and a clean isolated task; obtain explicit tracer spend approval. Then the smallest reused adapter executes one actual case with current and absent instruction contexts on one approved panel entry, captures runtime/usage/artifacts, and evaluates the produced files. Repeat to prove fresh-run isolation. Runner unit tests may use fakes but live proof cannot. Show a useful real artifact and actual costs; identical model outcomes are valid, no skill-win claim required. |
| S05 Evidence families | R3 | S04 | M: Implement F1-F3 triplets (nine core tasks) and three sealed variants, each with incident/provenance, expected decision/action and adjudicated oracle counterexamples. No model-tuned keyword or magic-marker scoring. |
| S06 Decision families | R3 | S04 | M: Implement F4-F6 triplets and three sealed variants. Test weaker-model regression, incomplete comparison evidence, and true/stale/misapplied findings with explicit expected action; do not grade reviewer obedience. |
| S07 Repair/restraint families | R3 | S04 | M: Complete F7-F9 triplets and three sealed variants, reusing the F8 tracer instead of duplicating it. Verify functional installs, behavioral/doc retention, and helpful-vs-historical comments. Distinguish judgment from mechanical lint. |
| S08 Freeze run protocol | R3, R4 | S05, S06, S07 | S: Validate 36-case manifest and all oracles; rerun S04's access-denial preflight on the full suite; freeze harness/corpus/holdout hashes. Human approves active panel, weakest supported entry, runtime variants, repeat count, numerical budgets, decision thresholds and equivalence margins before paid runs. Preflight estimated total calls/cost and stop conditions. No paid defaults inferred from role config. |
| S09 Run current baseline | R2, R4 | S08 accepted | M: Execute all cases x panel x current/absent x declared repeats; report core-case validity and the five dimensions per model/family, with discovery/repair separated. Use core results alone to classify gaps as absent instruction, existing instruction not followed, missing context/tool, mechanical gate, oracle problem, or no gap. Seal all holdout scores, including aggregates, from candidate selection/tuning until S11; precomputed controls may remain sealed. Invalid cells require bounded rerun or unproven conclusion, never silent exclusion. |
| S10 One real ablation | R4, R5 | S09 valid core results | M: Select one high-value core-case gap, pre-register one minimal candidate and exact removed component; compare current/absent/candidate on the 27 core cases under frozen evaluators and matched budgets, then lock the candidate revision before any holdout feedback. Record full tool/subagent costs. A harness/oracle defect discovered here invalidates affected results: version the fix, then rerun impacted controls, not just the candidate. No expansion into multiple prompt changes. |
| S11 Decide and close stage 5 | R5, R6, R7 | S10 candidate locked | S: Execute the locked candidate on nine sealed variants and blind-score against attributable matched controls (rerun controls if the reuse policy does not apply); only now unseal holdout results. Adopt only under the precommitted per-model gains/restraint/retention rules, otherwise reject candidate and retain current text. No tuning on those holdouts; a new attempt needs fresh held-out cases and budget. Retirement needs its own valid equivalence evidence plus human gate. Keep incident regressions even when saturated. Tighten AGENTS only where justified, preserving required safety/operational rules. Publish final decision, instruction diff or explicit no-change, final-head proof and fresh approval; no automatic merge. |

## Protocol Decisions Before Live Runs

Recovery execution gate (2026-10-21): S02 could not verify a supported isolated
composition from the installed Kilo 7.8.15 CLI and accessible local source/types.
Do not infer capability from fresh checkouts, permission prose or event output.
Do not substitute a newer/different runtime or implement a sandbox/broker without
an accepted design. Preserve the existing dependency graph until that gate closes.

Proposed next iteration, requiring an accepted rechart before implementation:

| Slice | Size | Gate / result |
| --- | --- | --- |
| S02 follow-up | Timeboxed spike | Select and verify one minimal execution boundary, exact resolved instruction capture, complete usage accounting and enforced limits using attributable runtime evidence. Source acquisition or isolation changes outside current scope need authorization. Reject unsupported composition rather than build around assumptions. |
| S03 offline preparation | S | Separately release only F8 provenance and independent behavioral oracle work from the S02 dependency; not original S03 completion. No instruction-arm freeze or model execution. |
| S03 runtime contract | S if feasible | After S02 accepted, freeze exact current/absent inputs and evaluator/output interface. Re-spike rather than silently expand if runtime support is missing. |
| S04 preflight | M | Approved boundary implementation and real-tool denial/allowed-edit, cancellation, cleanup and budget-contract proof before any live subject call. Fakes prove only mechanics. |
| S04 transport and execution | Unestimated until S02 accepted | Thin supported transport, then separately approved live tracer budget/model/variant/repeats/stop policy; capture attributable identity, usage and durable artifacts. |

These are proposed subdivisions of existing tickets, not newly admitted tickets.
No downstream ticket is marked passed by the foundation's static proof. An
isolation/runtime decision and later explicit spend approval are human/design
gates, not time-based waits. The loop stops here rather than polling or running
an unapproved subject model.

Execution rechart (2026-10-21, isolated planner `ses_ea2499817fferH7yvd9fQjufN8`):
S01c's real-run proof was impossible with line-only matching and missing native
GNU grep/date behavior. Its explicitly expanded boundary above permits only the
small existing-runner matcher/timing adaptation. Keep source-pattern expectations
bounded to supported excerpt forms, independently exercise controlled order/copy
counterexamples, and prove existing case/error/gating contracts. General runtime
or behavioral-evaluator design remains S02-S04. No model/provider calls or installs
are authorized by this rechart.

S08 must resolve these to numerical values; they are planning gates, not invented
evidence or permission to spend. S04 needs the corresponding small tracer budget
approved earlier. Call-count estimate is `cases x panel entries x arms x repeats`
plus declared reviewer/fixer calls. Candidate runs may reuse controls only when
all frozen versions and runtime settings match the approved reuse policy.

- Name the active supported panel and weakest entry. A one-entry panel supports
  only a one-model conclusion; do not manufacture broader coverage or silently
  add paid providers. Fix decoding/reasoning/tool limits and record them.
- Set per-arm token/wall/tool limits, total spend ceiling, repeat count and
  retry policy. Missing usage means no budget-matched effectiveness conclusion.
- Precommit graduation gains and allowed regressions separately per dimension.
  Proposed safety floor: zero new safe-negative/unrelated interventions, zero
  trust-boundary violations and zero retained-behavior losses in the final gate.
  Choose minimum correctness gain/repeat consistency before viewing results.
- Set a meaningful per-model equivalence margin and uncertainty standard before
  considering incumbent retirement. No significant gain is not equivalence.
- Score judgments blind to arm/model where feasible; human-adjudicate ambiguous
  expectations before running. Do not add an LLM judge unless deterministic
  checks plus a small explicit human rubric cannot settle the trait.
- Preserve the original review-round contract. A solo task cannot claim measured
  convergence; reviewer-in-the-loop trials declare their additional budget.

## Completion, Stops And Out Of Scope

Stage 5 is complete only with a valid live baseline and at least one bounded
ablation decision, not merely working infrastructure or green smoke checks.
Report per-model paired outcomes, costs, limits and evidence grade. A null result
can complete the experiment; it cannot justify unmeasured deletion of incumbents.
Any inconclusive gate is reported as unproven, with no graduation/retirement.

Stop/rechart for an unresolved runtime spike, missing spend authorization,
oracle leakage/tampering, insufficient metering, exhausted budget, or a design
decision outside the accepted boundary. Do not run loops until something wins.

No instruction pack expansion, automatic retirement, generic benchmarking
platform, production publish, provider installation, maintenance scheduler,
telemetry system, or babysit skill ships through this chart. F6 supplies evidence
for a later babysit decision. Step 6 config-change triggers follow only after
this evaluator has proven useful. Every finding need not become an instruction.

## Traceability And INVEST Check

| Outcome | Requirements | Tickets |
| --- | --- | --- |
| O1 | R1, R2, R3 | S01a-S01c, S02-S07 |
| O2 | R2, R3, R4 | S02-S09 |
| O3 | R4, R5, R6 | S08-S11 |
| O4 | R1, R6, R7 | S01a-S01c, S11; delivery constraints apply to every PR |

Every requirement has an outcome and an implementing ticket; every ticket has
requirements and a proof. Blocking references resolve. S02 alone is unestimated
and explicitly timeboxed; dependent implementation waits for its accepted result.
All other tickets have a bounded independent scope (subject to stated blocking
edges), a demonstrable valuable result, negotiable implementation, S/M size and
testable acceptance. S01a validates the repair-ticket sizing after source triage;
if that boundary cannot fit one context, split and recheck the chart before work.
No ticket requires another ticket's future output to count its own proof as
passed. Traceability orphans: zero.

## Addendum 2026-10-21 (second): proportionate evidence bar adopted

Incident `.kilo/plans/2026-10-21-overgating-incident.md` records that this
chart gated a reversible one-sentence instruction decision behind
beyond-reasonable-doubt apparatus — the failure mode the corpus exists to
catch. Human decision 2026-10-21: evidence effort is gated on cost of being
wrong, not on topic.

Accordingly, for the reversible-edit decision tier only, S02's acceptance is
revised to: one runnable session per arm on a chosen supported model, a
demonstrably visible instruction difference between arms, and durable audit
capture (session export JSON with tokens/cost, runtime permission-deny logs,
oracle verdicts). Attributable-identity proof and exact resolved-instruction
byte capture are demoted to logged best-effort gaps, covered by
arm-discrimination probes, not blocking gates. Sealed holdouts and
precommitted thresholds remain required only for hard-to-reverse instruction
adoption/retirement and publication-grade quantified claims (S10/S11 tier);
their apparatus is unchanged there. The recovery execution gate stands for
claims made under the original standard.
