# Hill-climb log

Frozen harness, one hypothesis at a time, decision log, one commit per win.
Start minimal; add only winners (plan §78).

Harness seed (frozen until first climb): `.kilo/workshop/admission/run.sh` +
stub corpus (violation-1, safe-neg-1, unrelated-1), verdicts `grep`-based,
tokens `-1` placeholder.

Current and historical JSONL rows are deterministic, non-admitting smoke replay,
not executions of the stamped models. The policy below requires future real,
budget-matched instruction-changing arms and attributable runtime provenance.

## Decision policy

- **Win condition.** A hypothesis wins only if it beats the seed on the
  *weakest model in the active panel* (`ablations/panel.txt`) at matched
  budget. A win on the strongest model alone is logged
  `win (strongest-only, non-graduating)` and earns no commit.
- **Retirement.** A rule, skill line, or component is a removal candidate only
  when real skill-on ≈ skill-off evidence exists on **every** panel entry.
  `ablations/retire.sh` is currently hard-disabled: no arm dispatch, results or
  proposal append, and no environment override. It exits 3 unless an existing
  unresolved heading blocks with 1. Future proposals require per-model evidence
  and human review; smoke equality or missing measured gain is not enough.
- **Resolution.** A human resolves one pending entry per commit. For **every**
  outcome below, replace `[pending-human]` in the heading with the chosen marker
  (do not merely append a resolution note or keep both markers):
  - [confirmed] — rule text removed in the same commit;
  - [rejected] — entry annotated with the reason (e.g. margin within noise,
    panel gap), rule stays;
  - [deferred] — allowed only with a named re-run date and the additional case
    that would settle it.
- **Panel rotation.** Dropping a model from `ablations/panel.txt` is itself a
  [pending-human] LOG entry; adding one is routine (panel grows before it
  shrinks).

Status tokens are literal `[pending-human]`/`[confirmed]`/`[rejected]`/`[deferred]`
markers inside an entry heading, greppable so `retire.sh` can detect an
unresolved backlog before running.

## Entries

| date       | hypothesis | arm vs seed | outcome | status | commit |
|------------|------------|-------------|---------|--------|--------|
| 2026-10-19 | seed: tracer-bullet harness lands | n/a | 3 cases x (full, baseline, no-advisor-brief, no-approve-table) = 18 canonical lines in `admission/results.jsonl`; vacuous-pass guard holds (unproven, exit 2) | n/a | c8fdb66 |

Append measured decisions only. Unknown/unobserved gain is not evidence to
remove an incumbent. Keep historical entries unchanged; no current smoke row
supports a win, retirement proposal or instruction deletion.
