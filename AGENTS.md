# kilo-mms

Local development workflows for this repo, in the shape of rgh-mms (planner, researcher, implementor, reviewer) without the harness machinery.

## Kilo agents

`.kilo/agents/` holds thin shims: `planner`, `researcher` (read-only), `implementor`, `reviewer` (read-only), `approver` (read-only, AC table), `advisor` (read-only, escalation brief).

`.kilo/skills/` holds the delivery loop, routed by `deliver`: `clarify` → `chart` → `build` → `prove` → `converge` → `land-learn`. `.kilo/workshop/` is plugin-dev only, never installed downstream.

Role models are configured in `.kilo/kilo.json` using Kilo's native `agent.<role>.model` settings, including direct agent invocations outside `deliver`. Planner and advisor default to paid `kilo-auto/frontier` for deeper reasoning and require Kilo Gateway access and credits. Other roles have no model override. To use a different provider or tier, edit those settings (for example, `kilo-auto/efficient`); to restore normal subagent inheritance, remove the role's `model` key rather than setting it to `auto` or `inherit-parent`.

## Dev-loop conventions

- Sync to `origin/main` then cut a fresh branch or worktree for every task. Work stays isolated until merge; no direct commits to `main`.
- Small diffs. One concern per change.
- Run the relevant tests before handing off.
- Planner and researcher never write code or mutate state.
- Reviewer findings are either blocking or advisory; say which.
- Act in the same turn you announce work. Never end a turn on a promise to do something; do it, then report.
- Best-effort protection by elimination, not enumeration: deny dangerous capability at the tool boundary; never glob-filter dangerous flags.
