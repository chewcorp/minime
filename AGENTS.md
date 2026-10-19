# kilo-mms

Local development workflows for this repo, in the shape of rgh-mms (planner, researcher, implementor, reviewer) without the harness machinery.

## Kilo agents

`.kilo/agents/` holds thin shims: `planner`, `researcher` (read-only), `implementor`, `reviewer` (read-only).

## Dev-loop conventions

- Small diffs. One concern per change.
- Run the relevant tests before handing off.
- Planner and researcher never write code or mutate state.
- Reviewer findings are either blocking or advisory; say which.
