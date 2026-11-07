---
name: recruit
description: Use when the user asks to build, rebuild or govern an agent (a bot, seat or scheduled routine) with the minime agents loop, or names one of its stages (brief, role, routines, chart, trial). Sets up the work folder, then loads the stage the routing script names. For a one-line prompt edit the user did not route here, just make the edit.
---

# recruit

Bring on a new agent the way you would a new colleague: agree what the job is for, what they own, when they work, how their day runs, and watch them handle a trial before they start for real. The loop: `brief` → `role` → `routines` → `chart` → `trial` → land. Code the agent needs goes through minime-coder's `deliver`; this loop owns the agent's brief, responsibilities, wakes and controls.

## 1. Set up

1. Pick `<agent>`: the agent's kebab-case name. Create a branch named for it from the default branch.
2. Create `.minime/<agent>/`. If `.minime/.gitignore` is missing, write it with the single line `*`.

Done when the branch is checked out and `.minime/<agent>/` exists.

## 2. Route

Resolve `NEXT` to this skill's `scripts/next.py` (Python 3.9+, Git). On every start and resume, run `python3 "$NEXT" <agent>` from the repo root and load the stage it prints. Do not route from your own reading of the folder.

| Prints | Load |
|---|---|
| `brief` | `brief` |
| `role` | `role` |
| `routines` | `routines` |
| `chart R1 …` | `chart`, for each routine listed |
| `trial` | `trial` |
| `land` | ready to start: hand the human the package, `proof.json` and the list of host-missing controls from the charts |

The script reads only JSON records, and each record names the hash of what it vouches for, so editing an artifact after its record voids the record:

- A reviewed stage is done when `<stage>.md` has no `[TK]` and `<stage>-review.json` is `{"artifact": "<hash of <stage>.md>", "findings": "<hash of <stage>-review.md>", "status": "clear"}`, each hash from `python3 "$NEXT" <agent> --hash <file>`. Write it only after every verified blocker in `<stage>-review.md` is fixed or declined with a reason, and never when that file says `review: incomplete`. Never write it to move on.
- A chart is done when `charts/R<n>/chart.json` matches the current model and `gated.out`, the check found no error, and every guard is placed (see `chart`).
- Proof is done when `proof.json` passes every row and covers every guard both ways at the current digest (see `trial`).

Malformed, stale or missing records count as not done.

## 3. Rules for every stage

- The human owns the agent's brief, authority limits, the rules in its charts, and the switch from observe to act. Ask; do not decide them.
- Size evidence to the cost of being wrong: classify each decision as a one-way or two-way door before choosing how much proof it needs (`references/failure-catalogue.md` F1).
- Review stops after two rounds; then it goes to the human.
- Failure codes (A1, D6, …) refer to `references/failure-catalogue.md`.
