---
name: deliver
description: Route delivery-loop work only when the user explicitly names the loop, a stage, or asks to route work. Never auto-load on ordinary requests resembling delivery work.
---

# deliver

Entry to the kilo-mms loop: clarify → chart → build → prove → converge → land-learn.

Delegate without per-task model overrides unless the user explicitly requests one. Kilo resolves role defaults from `agent.<role>.model` in `.kilo/kilo.json`; roles without an override use Kilo's normal subagent model inheritance.

Copy the steps for the matched stage verbatim into todos.

- New idea or vague ask → `clarify`
- Multi-ticket work needing a map → `chart`
- Single buildable ticket → `build` with `prove` inside
- Build stopped on an unsatisfiable example → human, with the example and its output
- Diff ready → `converge`
- Merged-ready → `land-learn`

Note: Kilo skills have no user-only flag; this router loads only on explicit user request per its description.
