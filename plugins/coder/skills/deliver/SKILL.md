---
name: deliver
description: Use when the user names the coder delivery loop or one of its stages (clarify, chart, build, prove, converge, land-learn), or asks to route work through it. Sets up the task branch and work folder, then loads the matching stage. For an ordinary edit the user did not route here, just do the edit.
---

# deliver

Entry to the coder loop: `clarify` → `chart` → `build` (with `prove`) → `converge` → `land-learn`.

## 1. Set up the task

1. Pick the task key `<task>`: a short kebab-case slug of the goal. It is the branch name and the work-folder name for every stage.
2. Set `<base>`: `origin/<default-branch>` after `git fetch origin` when an `origin` remote exists, otherwise the local default branch. If no `<task>` branch exists, `git switch -c <task> <base>`; if it exists, switch to it. Every stage diffs against `<base>`.
3. Create the work folder `.minime/<task>/`. If `.minime/.gitignore` is missing, write it with the single line `*` so loop state never reaches git in any client.

Done when `git branch --show-current` prints `<task>` and `.minime/.gitignore` exists.

## 2. Route

Before accepted criteria exist, load clarify. On upgrade, use any
`.kilo/run/<task>/acceptance.md` as input, not as reviewed acceptance.
After acceptance review (and chart
review for multi-ticket work), initialize the [plugin-local gate](references/gates.md).
Resolve `GATE` to this installed skill's `scripts/gate.py`; it requires Git and
Python 3.9+. Run `python3 "$GATE" <task> next --base <base>` on every resume. A nonzero gate exit
blocks progression; do not fall back to guessing from file existence.

Load the stage skill named below (one load per skill). Track task-specific deliverables and blockers in todos, not copies of the stage procedure.

| State | Load |
|---|---|
| New idea or vague ask, or no `.minime/<task>/acceptance.md` | `clarify` |
| Accepted criteria, more than one ticket | `chart` |
| Gate says `build`: one buildable ticket or the next unblocked unfinished ticket | `build` |
| Gate says `repair`: resume the admitted repair from `gate.json`, not an unfinished ticket | `converge`, directly at [Fix rounds](../converge/SKILL.md#5-fix-rounds) |
| `build` stopped on an unsatisfiable example | stop; give the human the example and its output |
| Gate says `converge`: every ticket built; review/evidence still required | `converge` |
| Gate says `land-learn`: current-diff review, independent proof and approval pass | `land-learn` |

For ordering risks or unresolved feasibility questions, use the conditional
[statechart/prototype investigation](references/investigation.md) before the
dependent implementation. Neither is required for a straightforward edit.

Dispatch roles as the stage says (`researcher`, `implementor`, `reviewer`, `approver`, `advisor`). Use each role's configured model; set a per-task model only when the user asks for one.

Done when the stage skill is loaded and the next task-specific action is identified.
