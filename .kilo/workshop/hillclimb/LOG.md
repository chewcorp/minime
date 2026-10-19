# Hill-climb log

Frozen harness, one hypothesis at a time, decision log, one commit per win.
Start minimal; add only winners (plan §78).

Harness seed (frozen until first climb): `.kilo/workshop/admission/run.sh` +
stub corpus (violation-1, safe-neg-1, unrelated-1), verdicts `grep`-based,
tokens `-1` placeholder.

## Entries

| date       | hypothesis | arm vs seed | outcome | commit |
|------------|------------|-------------|---------|--------|
| 2026-10-19 | seed: tracer-bullet harness lands | n/a | 3 cases x (full, baseline, no-advisor-brief, no-approve-table) = 18 canonical lines in `admission/results.jsonl`; vacuous-pass guard holds (unproven, exit 2) | this commit |

Append winners only. Losers are removed; an entry without measured
with>without gain is a removal candidate.
