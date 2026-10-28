---
name: deliver
description: Route delivery-loop work only when the user explicitly names the loop, a stage, or asks to route work. Never auto-load on ordinary requests resembling delivery work.
---

# deliver

Entry to the coder loop: clarify → chart → build → prove → converge → land-learn.

Delegate without per-task model overrides unless the user explicitly requests one. Role defaults come from the client's agent config (Kilo: `agent.<role>.model` in `.kilo/kilo.json`); roles without an override inherit the client's normal subagent model.

Copy the steps for the matched stage verbatim into todos.

- New idea or vague ask → `clarify`
- Multi-ticket work needing a map → `chart`
- Single buildable ticket → `build` with `prove` inside
- Build stopped on an unsatisfiable example → human, with the example and its output
- Diff ready → `converge`
- Merged-ready → `land-learn`

Note: this router stays model-invocable so a request that names the loop in plain text reaches it; it loads only on explicit user request per its description.
