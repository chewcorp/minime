# Workshop results schema

Every runner under `.kilo/workshop/` emits one JSON object per line (JSONL) so
results stay appendable and `jq`-queryable. Budget-matched comparison needs
tokens and wall time recorded next to verdicts — never verdicts alone.

Current `admission/run.sh` and `ablations/ablate.sh` emit **non-admitting static
smoke replay** rows. Their model/provider/component fields are declared labels,
not verified runtime identities or actual instruction changes. Existing JSONL,
including legacy unstamped rows, is preserved as history and excluded from live
comparisons. Matching labels or checker outcomes do not prove equivalence.

## Required fields per line

| field         | type   | meaning                                                     |
|---------------|--------|-------------------------------------------------------------|
| `task`        | string | case directory name, e.g. `admission/cases/violation-1`     |
| `skill`       | string | skill under test; literal `"baseline"` for the no-skill arm |
| `model`       | string | declared model label; current smoke runner executes no model; required, no default |
| `provider`    | string | declared provider label; current smoke runner calls no provider |
| `component`   | string | declared component label; current smoke runner removes nothing; default `"full"` |
| `tokens`      | int    | tokens used; `-1` when unknown                              |
| `wall_ms`     | int    | wall-clock milliseconds of the run                          |
| `verdict`     | string | one of `pass`, `fail`, `unproven`                           |
| `verdicts`    | object | per-check map, e.g. `{"known-hit":"pass","safe-neg":"pass"}`|
| `evidence`    | string | path to the re-runnable proof artifact for this run         |
| `ts`          | string | UTC timestamp, RFC 3339                                     |

`verdict` derives from `verdicts`: all pass → `pass`; any fail → `fail`;
otherwise `unproven`. A claim that was never checked is not a pass.

## Model panel and retirement rule

Every run names its model; comparisons are per-model, never pooled. A rule,
skill line, or component is a removal candidate only when skill-on ≈ skill-off
**on every model in the active panel** at matched budget. A win or loss
observed on one model alone is logged as such and never graduates or retires
anything. The panel always includes the weakest model we still support; that
weakest model's skill-on≈skill-off result is the retirement floor, and only a
human may confirm a retirement (see `hillclimb/LOG.md` for the pending-human
gate).

This is a future admission policy, not a capability of the current runners.
`retire.sh` is hard-disabled without dispatch or proposal/result writes, with no
environment bypass. Its sole exit-1 path is an existing unresolved backlog;
all other invocations return 3+ (including usage/infrastructure errors).

## Runner exit codes

| code | meaning                                   |
|------|-------------------------------------------|
| 0    | verdict pass                              |
| 1    | verdict fail (a real check failed)        |
| 2    | unproven (no checks applied to this arm)  |
| 3+   | runner error (missing files, malformed check, Python regex/jq error) |

Verdicts and infrastructure errors never share a code, so callers can tell
"the artifact failed" from "the run was invalid". `evidence` paths are unique
per run; result lines are append-only and never overwrite each other's proof.

## Static check matching

Checks use **Python 3 `re` syntax**, not PCRE compatibility. Matching is
case-insensitive. Omitted `scope` means `line`: search each line separately,
without its newline (anchors remain line-local). `scope: "document"` searches
the whole UTF-8 target; use `(?m)` for multiline anchors and `[\s\S]` or `(?s)`
to span newlines. `expect: "fail"` requires a match; `expect: "pass"` forbids
one (these describe the matched artifact condition, not the row verdict).
All applicable scopes and regexes are validated before verdict/evidence writes;
checks gated out by top-level `skill` are not interpreted. No applicable checks
still append an `unproven` row and exit 2. Only static data is inspected.

shortcut: `tokens: -1` until a token metering source is wired; upgrade when the
runner gains access to a real token count from the agent runtime.
