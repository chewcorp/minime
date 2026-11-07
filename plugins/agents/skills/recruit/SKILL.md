---
name: recruit
description: Use when the user asks to build, rebuild or govern an agent (a bot, seat or scheduled routine) with the minime agents loop, or names one of its stages (brief, role, routines, chart-duties, trial). Sets up the work folder, then loads the stage the routing script names. For a one-line prompt edit the user did not route here, just make the edit.
---

# recruit

Router for the agent loop: `brief` → `role` → `routines` → `chart-duties` → `trial` → `land`. Each stage writes its artifact to `.minime/<agent>/`; `scripts/next.py` alone decides the current stage. Code the agent needs goes through minime-coder's `deliver`; this loop owns the brief, role, routines, wake charts and controls.

## 1. Set up

1. Pick `<agent>`: the agent's kebab-case name. Create a branch named for it from the default branch.
2. Create `.minime/<agent>/`. If `.minime/.gitignore` is missing, write it with the single line `*`.

Done when the branch is checked out and `.minime/<agent>/` exists.

## 2. Route

Resolve `NEXT` to this skill's `scripts/next.py` (Python 3.9+, Git). On every start and resume, run `python3 "$NEXT" <agent>` from the repo root and load the stage it prints. Never route from your own reading of the folder.

| Prints | Load |
|---|---|
| `brief` | `brief` |
| `role` | `role` |
| `routines` | `routines` |
| `chart-duties R1 …` | `chart-duties`, for each routine listed |
| `trial` | `trial` |
| `land` | §5 Land |

Every record is JSON naming the hash of what it vouches for; an edit after the record voids it. Malformed, stale or missing records count as not done.

- **Reviewed stage** (`brief`, `role`, `routines`): done when `<stage>.md` has no `[TK]` and `<stage>-review.json` is clear for the current `<stage>.md`, its findings, and the upstream pinned at review start (role: brief; routines: brief and role).
- **Upstream edit reopens downstream** (F5): a brief edit reopens role, routines and every chart, even when their text is unchanged. A routine edit reopens only its own chart.
- **Chart, proof**: done per the Done-when of `chart-duties` and `trial`.

## 3. Reviewed-stage protocol

The stage supplies `goldfish-review`'s parameters: artifact, intent, question, blocking rule, output `<stage>-review.md`.

1. `python3 "$NEXT" <agent> --pin <stage>` immediately before loading `goldfish-review`.
2. Fold each verified blocker into `<stage>.md`, or decline it with a reason in `<stage>-review.md`. Advisories stay recorded in `<stage>-review.md`; fold one only when it is a one-line edit or cites a failure code (F2). Re-review when a fix changes anything the question or blocking rule judges; two rounds, then the human (F4).
3. `python3 "$NEXT" <agent> --clear <stage>` once every verified blocker is fixed or declined. `--clear` refuses without a pin or when the findings say `review: incomplete`. Never clear to advance.

## 4. Rules for every stage

- The human owns the brief, authority limits, chart invariants and the `observe → act` mode switch. Ask; never decide them.
- Size evidence to the cost of being wrong: classify each decision as a one-way or two-way door first (F1).
- Failure codes (A1, D6, …) refer to `references/failure-catalogue.md`.

## 5. Land

Run `python3 "$NEXT" <agent>` first. Land only on `land`, or on the human's request for an unproved landing; either way the package records the printed stage and claims nothing past it.

1. Read the destination repo's `AGENTS.md`. If its layout has no place for a `status: proposed` package, add a one-paragraph layout amendment in the same PR or stop for the human's ruling. Never invent a parallel layout (F6).
2. Write the package in the destination checkout, never as a new commit on the proved tree: any commit there voids the proof digest.

   | Path | Content |
   |---|---|
   | `agent.yaml` | gitagent keys; `metadata.status: proposed\|live`, `metadata.live_record` (path or `null`) |
   | `minime.yaml` | `x-minime`: `stage` (the printed stage), `proof: {commit}`, then outcomes, identity, overlap, approval gates |
   | `SOUL.md` | brief: Problem, Serves, Outcomes |
   | `RULES.md` | brief authority limits, role Never |
   | `DUTIES.md` | role: Owns, Reads, Overlap, Reports to |
   | `schedules/r<n>.yaml` | one per routine: gitagent `id`, `prompt`, and `cron` or the event trigger; budgets, idempotency keys and approval gate under `x-minime` |
   | `charts/R<n>/` | the checked chart folder as-is, template README included |
   | `reviews/<stage>-review.md` | each reviewed stage's findings |
   | `proof.json` | copied from `.minime/<agent>/`, when one exists |

3. Prose (README, PR body) cites `proof.json`; never restate row or probe counts. "Proved" or "ready to land" only with `stage: land`.
4. A correction to the live record is a separate PR.
5. Trial harness code and raw outputs stay in the recruit checkout; the package carries only `proof.json` (F2).
6. Hand the human the package, `proof.json` when one exists, and every guard placed `prompt` or not yet built on the host.
