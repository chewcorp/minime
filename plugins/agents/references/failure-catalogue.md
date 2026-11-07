# Failure catalogue

Drawn from the network's records, minime-coder's incidents and this workspace's findings. Each row names a failure we have seen, the evidence, the wake-chart state where it is caught, and the control. Stage skills cite these codes. Codes are stable: add new ones, never renumber. Sources: rgh-botnet `blackboard/` (board envelopes and network reports), workspace-agent-ops `updates/2026/` (dr eggbot's weekly antipattern notes of 19 Oct, 26 Oct and 2 Nov) and `wiki/`, minime-coder `.kilo/plans/`, and the workspace-sdlc-skills wiki.

## A. Inside one wake

| Code | Failure | Evidence | Caught at | Control |
| --- | --- | --- | --- | --- |
| A1 | **Receipt ping-pong.** Two agents answer each other's acknowledgements | hobot3, 12–18 Oct: 26 of 52 seat chat posts opened "Received/Noted/…"; hobot3/main had 107 sessions started by another seat's message. OpenClaw's reply-back loop runs up to 5 turns (eggbot 19 Oct §1) | Classify | An ack-only input ends the wake silently; host caps agent-to-agent turns at 1 |
| A2 | **Missing-skill loop.** The prompt names a skill that is not installed; the agent retries loading it | Closer, 16 Oct: about 800 `skill_view` calls in a day, 92.2M prompt tokens on its key (ABP token-burn briefing, 17 Oct); then five seats in one week (eggbot 26 Oct §2) | Orient | Host-surface check in `routines`; at wake, a missing named tool or skill is a recorded stop, not a retry |
| A3 | **Runaway run after a model change.** | SM-CCP, 22 Oct, after the glm-5.3 → gpt-6-luna rollout: 28,903 tool calls with 1,337 errors in 6 runs; prompt per request 76k → 145k (claude-code envelope 20261022-201500) | Budget region | Tool-call and token caps held by the host; a model change is a control change and re-runs the probes |
| A4 | **One knob for cost and skill retention.** Compression prunes a loaded skill, the agent reloads it, the threshold is tuned up and down per seat | 48k → 128k → 64k on Closer, Operator, PO within two days; `hermes-closer` 6M → 116M tokens (eggbot 26 Oct §2) | Orient | Skill bodies kept out of the compressible window; compression set for cost alone |
| A5 | **Re-reads the world every wake.** | SM and PO re-paginated all of Linear each wake, about 41–48M tokens a day on SM's key (ABP briefing #2) | Orient | Input is a delta since a stored cursor |
| A6 | **Big silent run.** Hundreds of calls, nothing returned | Crabmaster heartbeats at 490–1,364 tool calls returning nothing, 29–31 Oct (eggbot 2 Nov, dropped list) | Record | Every wake ends in a recorded terminal state; the budget region ends it if the agent does not |
| A7 | **Stops before writing its record**, so the next wake redoes the work | scout's turn cap stopped 256k prompts but still let a run end before its record (workspace-agent-ops `wiki/AgentPractice/loop-statecharts.md`) | Record | The host writes the terminal record when a turn ends; cursor advances only after the record |
| A8 | **Prose-held cap lost on compaction.** | Superpowers run that lost its five-round cap and ran 18 rounds ([superpowers](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/superpowers.md)); the compaction break in [prose state machine](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/prose-state-machine.md) | Budget region | Counters live outside the context (script or host) |

## B. Messages and attention

| Code | Failure | Evidence | Caught at | Control |
| --- | --- | --- | --- | --- |
| B1 | **Fan-out ceremony.** One message to many seats is copied to each and each copy wakes a reply | Board envelopes 38–70 a day, then 174 on 17 Oct; one ruling copied 19 times; Chief's inbox 477 files, 1 in `done/` (eggbot 19 Oct §3) | Act | A message to three or more readers is written once and woken by pointer |
| B2 | **All-seat notice comes back as acks.** | Slack-started sessions spike on ruling days: 9 for one repo-move ruling, "Every seat acknowledged it and changed no remotes" (eggbot 26 Oct §4) | Classify | A notice that names no action gets no reply and no check of replies |
| B3 | **Self-report as closure.** A rule change closes when the seat says it is operating under it | 83 of 557 same-day envelopes were confirmations while BRD-65 found 0 of 18 seats loaded the canonical charter (eggbot 19 Oct §2) | Orient | The host checks the loaded charter's hash against the committed one; the seat's statement is not evidence |

## C. Configuration and authority

| Code | Failure | Evidence | Caught at | Control |
| --- | --- | --- | --- | --- |
| C1 | **Charter drift.** Merged rules reach seats only by hand-apply | Claim contract rewritten four times in about 9 hours, SM's SOUL still on the old one (ABP charter-live-drift grade, 18 Oct); workspace-agent-ops `wiki/agent-network/rulings-reach-live-prompt.md` | Orient | Load from canonical main at wake, cite the hash; on fetch failure run read-only on the last-known hash (record, no outside action), never on an empty charter |
| C2 | **Overruled advice returns through plans.** | "Pause any cron silent 10 runs" reappeared in Chief's plan two days after Russell ruled silent crons are never paused; SM charter said 3 cards against a ruling of 2 (eggbot 19 Oct §4) | Decide | Plan and charter steps are checked against the ruling ledger before publishing |
| C3 | **Borrowed identity.** | Board commits "made on Russell's identity by grok-ops" through November; Cursor refuses a Linear delegate that is not a linked human (workspace-agent-ops `wiki/AgentPractice/automation-identity.md`) | Role | Each agent has its own identity, named in `role.md`, before it goes live |
| C4 | **Credential cutover proved on one path.** | CPB-85 closed 25 Oct on one write per seat; that week Linear 401, GitHub 403 on Actions, a board pull that disabled itself after 10 failures (eggbot 26 Oct §3) | Trial | Probe every path each routine uses; a cutover stays open until 24h of scheduled runs show no auth error |
| C5 | **Authority read from the message.** | Design rule from dsh-superagent ([observe before act](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/observe-before-act.md)); untrusted triggers can also poison memory (workspace-agent-ops `wiki/AgentPractice/memory-poisoning.md`) | Classify | Permissions and mandate come from the host; memory off for triggers anyone can write to |
| C6 | **Headless run approves everything.** | Cursor's SDK approves tool calls by default in local headless runs (workspace-agent-ops `wiki/AgentPractice/headless-approval-gate.md`); a Kilo tracer under `--auto` wrote the real `~/.config/kilo` (kilo-mms PR #9) | Trial | The approval gate is chosen in `routines.md`; tests run with a throwaway HOME |

## D. Coordination between actors

| Code | Failure | Evidence | Caught at | Control |
| --- | --- | --- | --- | --- |
| D1 | **Two actors on the same work.** | Two Closure Validators judged the same cards in the same minute (29 Oct); Devin ran twice on CCP-783, 791 and 920, duplicate homecode PRs #312/#313 (eggbot 2 Nov §3); claim race on CCP-920 (closer, 30 Oct) | Classify | Act only while holding the item's lease; a second runtime for a role goes live only with a written split |
| D2 | **Mailbox starvation.** | Operator's pre-run read the newest 20 unread and never marked answered ones; a per-profile mailbox had no reader (workspace-agent-ops `wiki/agent-network/board-inbox-consumers.md`) | Orient | Every input queue has a named consumer that reads all of it and marks what it handled |
| D3 | **Silent sync failure.** | `blackboard-sync.sh` hides git errors behind "offline?" and retries forever (workspace-agent-ops `wiki/agent-network/board-sync-silent-failure.md`) | Orient | Errors are surfaced in the wake record; a probe proves sync still moves |
| D4 | **Two writers to one state.** | hermes-home's heartbeat overwrote a retired hub back to `up` (rgh-botnet 5eb9da60) | Role | One writer per kind of state ([one writer, many readers](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/one-writer-many-readers.md)) |
| D5 | **Cancel does not reach work in flight.** | Cycle-planning model: a story placed in a cycle before Russell cuts its feature stays Ready and can be built (workspace-agent-ops `wiki/agent-network/cycle-planning-statechart.md`) | Outer state | Cancel and stop are arrows on the outer state, so they win over any inner step ([statechart step semantics](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/statechart-step-semantics.md)) |
| D6 | **Duplicate outside action after a restart or timeout.** | Design rules from dsh-superagent ([restart-safe side effects](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/restart-safe-side-effects.md)); the wake model in `templates/wake/` shows receipts alone still double-send | Act | Store, then do, then read the destination before any resend |

## E. Measurement and evals

| Code | Failure | Evidence | Caught at | Control |
| --- | --- | --- | --- | --- |
| E1 | **Gauge goes blind.** | `unclear` card kinds rose to 53% of the 7-day table while the worth-it verdict kept running (eggbot 26 Oct §1) | Brief | Each outcome's gauge says when it cannot judge; no verdict above a stated unclassified share |
| E2 | **Gauge reads zero while the real budget runs out.** | Effective spend fell to $0.96 a week while Cursor quota neared its limit, because subscriptions were priced at 0 (eggbot 2 Nov §1) | Brief | The brief names the binding constraint and the gauge reads it |
| E3 | **Lever counted against its own target.** | Delegation rose from 10 to 52 points while seat-built work fell from 22% to 8%, by definition (eggbot 2 Nov §2) | Brief | Outcomes and their gauges are goldfish-reviewed together for contradictions |
| E4 | **Scripted evals.** Code decides the answers | CCP-822 redo: Russell's 20 Oct rule "Tests run INSIDE A MODEL… Forbidden: code that decides answers" (workspace-agent-ops `INTENT.md`) | Trial | Answers come from a fresh model run, stored before scoring, recorded in `proof.json` |
| E5 | **A quiet control may be dead.** | [Known-input probe](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/known-input-probe.md), [control reliability engineering](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/control-reliability-engineering.md) | Trial | Every control has a scheduled probe |

## F. The building process itself

| Code | Failure | Evidence | Caught at | Control |
| --- | --- | --- | --- | --- |
| F1 | **Over-gating a reversible change.** | minime-coder stage-5 incident: sealed holdouts demanded for a one-sentence edit, blocking S03–S11 (`.kilo/plans/2026-10-21-overgating-incident.md`) | Brief | Classify each decision as one-way or two-way door first; evidence sized to the cost of being wrong |
| F2 | **Gold-plating the fix.** | Same incident: a 90-line runner where a 35-line driver did the job. chewcorp-roster#12: Adjutant's review rounds folded all but 2 of about 40 advisories and landed a 1.6k-line trial harness | Build, review fold | Smallest rung that works ([ponytail ladder](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/ponytail-ladder.md)); advisories stay recorded unless one-line or failure-coded |
| F3 | **Ungated second fix loop, stale proof.** | minime-coder statechart run ([one fix path](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/one-fix-path.md), [head-scoped evidence](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/head-scoped-evidence.md)) | Converge | Reused from coder: one capped fix path, evidence keyed to the tree hash |
| F4 | **Review that never converges.** | [Review convergence](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/wiki/concepts/review-convergence.md); Russell's 2-round cap (20 Oct) | Converge | Two rounds, then the human |
| F5 | **Stale review counted clear after its upstream changed.** | Devin review of chewcorp/minime#3: a role reviewed against an old brief reached land; `tests/route/` model breaks unpinned, holds pinned | Recruit router | Review and chart records pin upstream hashes when reviewers start |
| F6 | **Proposal lands as the live record.** A rebuilt agent's package is read as the agent that runs | chewcorp-roster#12 placed the Adjutant rebuild inside the live profile, and #13 added a parallel `agents/scout/` beside the live `agents/hermes-home-gui/scout`; Devin Review raised four findings on the two PRs from one cause: the roster layout describes only live records. #13 landed at the trial stage with prose that read as proved | Land | The package declares `metadata.status`, `metadata.live_record` and the router `x-minime.stage`; the destination's layout is read before push and amended or ruled on |
| F7 | **Standard wake rule weakened without a ruling.** A chart passes after redefining or dropping one of the eight template invariants | chewcorp-roster#13: Scout's charts rewrote `ObserveOnly` and the classify guard, with no recorded ruling; reviewers caught it by reading the model | Chart-duties | `next.py` compares each chart's eight definitions and `gated.cfg` invariants with `templates/wake/`; each difference needs a `chart.json` ruling |

Source: [foundation report](https://github.com/chewcorp/workspace-sdlc-skills/blob/main/docs/reports/coordinator-20261107-minime-agents-foundation.md), 2026-11-07.
