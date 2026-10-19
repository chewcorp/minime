# Workshop results schema

Every runner under `.kilo/workshop/` emits one JSON object per line (JSONL) so
results stay appendable and `jq`-queryable. Budget-matched comparison needs
tokens and wall time recorded next to verdicts — never verdicts alone.

## Required fields per line

| field         | type   | meaning                                                     |
|---------------|--------|-------------------------------------------------------------|
| `task`        | string | case directory name, e.g. `admission/cases/violation-1`     |
| `skill`       | string | skill under test; literal `"baseline"` for the no-skill arm |
| `tokens`      | int    | tokens used; `-1` when unknown                              |
| `wall_ms`     | int    | wall-clock milliseconds of the run                          |
| `verdict`     | string | one of `pass`, `fail`, `unproven`                           |
| `verdicts`    | object | per-check map, e.g. `{"known-hit":"pass","safe-neg":"pass"}`|
| `evidence`    | string | path to the re-runnable proof artifact for this run         |
| `ts`          | string | UTC timestamp, RFC 3339                                     |

`verdict` derives from `verdicts`: all pass → `pass`; any fail → `fail`;
otherwise `unproven`. A claim that was never checked is not a pass.

## Runner exit codes

| code | meaning                                   |
|------|-------------------------------------------|
| 0    | verdict pass                              |
| 1    | verdict fail (a real check failed)        |
| 2    | unproven (no checks applied to this arm)  |
| 3+   | runner error (missing files, malformed check, grep/jq error) |

Verdicts and infrastructure errors never share a code, so callers can tell
"the artifact failed" from "the run was invalid". `evidence` paths are unique
per run; result lines are append-only and never overwrite each other's proof.

shortcut: `tokens: -1` until a token metering source is wired; upgrade when the
runner gains access to a real token count from the agent runtime.
