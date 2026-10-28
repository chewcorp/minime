# agentic-pr audition suite

Audition harness for new instructions (skill edits, rule candidates, process
gates) before they enter rgh-mms consumer skills. Same contract as
`../../admission/`: append-only JSONL, with declared model/provider labels.
Current execution is static, non-admitting checker smoke replay, not a
budget-matched skill-on vs skill-off experiment. Future graduation requires
real attributable instruction-changing runs that beat skill-off on the weakest
panel model without regressing restraint on safe-neg/unrelated.

## Layout

`cases/<case-id>/` — flat, one directory per case; case ids name the rule
family and variant (e.g. `pilot-pr4-stub-gh-critical`, `r7-test-tamper-violation-1`).
Grouping by rule subdirectory deferred until a rule family has ≥3 cases —
the flat layout is greppable and keeps `run.sh` calls un-nested. Each case
directory holds:
- `target.txt` — the artifact a check inspects (PR body, diff hunk, reply
  body, commit message — whatever the rule claims to govern);
- `checks.json` — per-check `{pattern, expect: pass|fail, scope?: line|document}` objects, plus an
  optional top-level `skill` key when checks gate to a named skill;
- `provenance.md` (optional but expected for public-replay cases) — upstream
  PR/issue link, freeze SHA, what the originating failure looked like.

Patterns use Python 3 `re`, case-insensitive, line-local by default; see
`../../SCHEMA.md` for scope and polarity. The three pilot seeds are bounded
source-pattern smoke oracles, not general shell/prose semantic verification:
release excerpts support standalone `git push origin main --follow-tags` and
standalone or `if ! gh release create` lines, once each, with comments ignored
for order. Docs recognize the displayed release-before-push and push-then-create
phrases with ordinary spacing/wrapping. Self-copy supports the displayed
`if [ "$src_root" -ef "$dest" ]; then` / `exit 0` / `fi` guard immediately before
the agents/skills copy loop; destination must exist before the guard. The guard
must precede copying and the distinct-destination loop must remain. Other shell
forms, unreachable/deceptive code, aliases and general language equivalence are
not adjudicated. Upgrade to isolated behavioral evaluation in S02-S04, not more
claims about regex semantics. Original known-bad targets remain unchanged.

Each rule family should contain at minimum one of each: `violation-*` (rule
should fire), `safe-neg-*` (rule must not fire), `unrelated-*` (spillover
check). pilot-pr4 seeds are real cases harvested from PR #4 review rounds.

## Scoring

Per case × arm × model: correctness (violation found), restraint (no fire
on safe-neg + unrelated), verification (claims in output cite a run),
retention (fix holds across the diff), convergence (rounds ≤ 2; needs a
reviewer in the loop, else `not_observed`).

## Gaps before results count as admission evidence

- Public-replay cases must record their freeze SHA in `provenance.md` on
  first replay; none do yet.
- Real model execution, isolated instruction-changing arms, metering and runtime
  provenance are absent; existing stamped smoke rows cannot fill these gaps.
- Public cases are training-data discounted; own-repo cases count high.
- Reviewer-in-the-loop is required for convergence; solo runs emit
  `convergence: not_observed`.
