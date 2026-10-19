# Admission corpus (stub)

Synthetic cases only, per scoring hygiene: each named skill needs a
**known violation** (skill must hit), a **safe counterexample** (skill must
pass), and an **unrelated case** (skill must pass) before any real corpus from
PR/session history is admitted here.

Each case dir holds:

| file          | contents                                                        |
|---------------|------------------------------------------------------------------|
| `target.txt`  | the artifact under review                                        |
| `checks.json` | `{"check-name": {"expect": "pass"\|"fail", "pattern": "<regex>"}}`|

`expect` is the check's expected verdict against this target: `pass` means the
pattern must be absent (clean artifact), `fail` means the pattern must be
present (violation found). Matching uses `grep -qiP -e <pattern> target.txt`.
A named `"skill": "<name>"` in `checks.json` gates the whole check file to
that skill's arm; skill-less checks apply to every arm.

Real 20–50-case corpus from history is deferred (chart, dependents wait).
