# kilo-mms

Local development workflows for this repo, in the shape of rgh-mms (planner, researcher, implementor, reviewer) without the harness machinery.

## Kilo agents

`.kilo/agents/` holds thin shims: `planner`, `researcher` (read-only), `implementor`, `reviewer` (read-only), `approver` (read-only, AC table), `advisor` (read-only, escalation brief).

`.kilo/skills/` holds the delivery loop, routed by `deliver`: `clarify` → `chart` → `build` → `prove` → `converge` → `land-learn`. `.kilo/workshop/` is plugin-dev only, never installed downstream.

## Dev-loop conventions

- Small diffs. One concern per change.
- Run the relevant tests before handing off.
- Planner and researcher never write code or mutate state.
- Reviewer findings are either blocking or advisory; say which.
- Act in the same turn you announce work. Never end a turn on a promise to do something; do it, then report.
- Best-effort protection by elimination, not enumeration: deny dangerous capability at the tool boundary; never glob-filter dangerous flags.
