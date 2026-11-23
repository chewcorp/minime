# Plugin-local gates

Requires Git and Python 3.9+. Resolve `GATE` to this skill's installed
`scripts/gate.py` (not a consumer-repo copy). Run from the target repository.
Commands exit 0 when admitted, 1 when blocked, 2 for invalid CLI usage.
On nonzero, stop the requested transition; never treat it as a warning.

The coordinator owns the ledger; reviewers return reports, never edit it.
This is deterministic bookkeeping, **not** tamper-proof enforcement: an agent
can skip the command, edit state, or misrepresent evidence. No host hook, CI
service, model runner, or new package dependency is installed.

## Start and route

After acceptance review (and ticket review when chart was needed), use the
base ref from `deliver` as `BASE`:

```sh
python3 "$GATE" <task> init
python3 "$GATE" <task> next --base "$BASE"
```

`init` reads outcome IDs from the acceptance table (`| O1 | ... |`) and ticket
IDs from standalone `## T1`, `## T2`, ... lines in `tickets.md`. Goals and
metadata belong in the body. Every line whose left-stripped text starts with
`#` must be exactly a ticket declaration; titles, subheadings, punctuation,
and goal text in headings invalidate the entire plan. Declarations must be
nonempty and unique. Without `tickets.md`, the single ticket is `T1`. Check
those IDs match the accepted work. It fingerprints both documents; finish
planning first, and do not put changing progress notes in them.

For example:

```markdown
## T1
Implement the first vertical slice.
serves: O1

## T2
Add the follow-up behavior.
serves: O2
blocked-by: T1
```

Mark each implemented ticket with `python3 "$GATE" <task> done T1`.
The ledger records this judgement, not proof that implementation is correct.
`next` returns `build`, `repair`, `converge`, or `land-learn`. An admitted
repair resumes at converge's Fix rounds, even with every ticket complete; it
doesn't require a clean tree to resume. Before acceptance exists, use clarify.

## Review, evidence, readiness

Commit the complete diff. `review` refuses dirty/untracked work and unfinished tickets. Capture its
output `review <SCOPE> <TREE> <BASE_TREE>` **before** dispatching the checks.
`BASE_TREE` is the merge-base tree of `BASE` and the task head:

```sh
python3 "$GATE" <task> review --base "$BASE"
# Copy SCOPE, TREE and BASE_TREE from the output; give all three to every checker.
python3 "$GATE" <task> record review all pass --base "$BASE" --scope "$SCOPE" --base-tree "$BASE_TREE" --tree "$TREE" --report .minime/<task>/review.md
python3 "$GATE" <task> record independent O1 pass --base "$BASE" --scope "$SCOPE" --base-tree "$BASE_TREE" --tree "$TREE" --report .minime/<task>/proof.md
# Repeat independent for every outcome; finish all proof rows BEFORE recording.
python3 "$GATE" <task> record approval O1 pass --base "$BASE" --scope "$SCOPE" --base-tree "$BASE_TREE" --tree "$TREE" --report .minime/<task>/approval.md
# Repeat approval for every outcome, after a fresh approver reads the finished reports.
python3 "$GATE" <task> ready --base "$BASE"
```

The `--scope` token binds the accepted documents and the merge-base tree. Carry
the captured token and both trees through every report row and record command;
never recompute them from the ledger when recording a completed check. Review
the pinned diff with `git diff "$BASE_TREE" "$TREE"`.

The v0.2.3 commands still work without `--base`, using the local tracking ref
for origin's default branch when available, then the local branch with the
same name. If a named default cannot be resolved, pass `--base` explicitly.
If no default is advertised, the gate tries local `main` or `master`. Without
`--base`, `review` prints exactly `review <SCOPE> <TREE>`. If `record`
omits `--base-tree`, the gate uses the current captured base tree only
after validating the supplied review token. If the default branch cannot be
found, or the task uses a different review base, pass `--base` explicitly.

Record the actual `pass`, `fail`, or `unproven` result, never infer it from a
file's existence. `review:all` means complete goldfish review with no verified
blocker. Independent and approval results each cover the whole named outcome,
including all its required checks. Keep individual failures in the report;
do not replace an aggregate failure with one passing subcheck.

Reports must be nonempty files in the task folder. The gate saves their digests
and rejects subsequently edited/missing reports. Finish a report before recording
all its outcomes. Any new review/independent record invalidates approvals.
Records replace only the same role/outcome for the admitted scope and diff;
repair admission clears current evidence, while historical reports may be
retained. Earlier failures and passes cannot apply to a new scope or diff.
A new review at an unchanged task tree but different base tree clears stale
evidence without spending a repair round, including pre-upgrade evidence that
didn't capture a base tree. Metadata-only rewrites retain evidence if both
trees and accepted scope are unchanged.

`ready` means **local evidence ready**, printed as `merge-ready`; forge checks,
review threads and conflicts still have to pass land-learn. It does not merge.

## One repair path

Dismiss unsupported findings with evidence first. A structural change or a
repeated cause stops for a human ruling before any repair is admitted. Dispatch
the advisor when that escalation needs a refactor direction. Neither stop spends
a repair round. A structural ruling revises scope or re-cuts the pull request.
For a repeated cause, a ruling may instead approve one more bounded repair.
The ruling does not update the ledger. For every verified bounded repair,
including that approved repeat, **before editing**, run:

```sh
python3 "$GATE" <task> fix --base "$BASE" 'verified blocker and bounded remedy'
python3 "$GATE" <task> fix --base "$BASE" --by human 'a human reviewer asked, and the bounded remedy'
```

The first command is the bot path, including CI, other bot findings during
landing, and a human-approved retry of a bot finding. It increments `rounds`
in `gate.json` up to the cap, which defaults to 3. Set `MINIME_BOT_REPAIR_CAP`
in the environment that runs the gate to override it, for example
`export MINIME_BOT_REPAIR_CAP=5`. Use a non-negative decimal integer.
Zero blocks all new bot repairs. An invalid value rejects new bot repairs
with an error. At or above the cap, hand unresolved bot findings to the human.

The second command admits a repair a human reviewer requested even at the cap.
It leaves `rounds` unchanged and records `requester` as `human`.
`--by` defaults to `bot`. The script records the coordinator's mark; it cannot
check who commented. A retry while that repair is active is idempotent,
whichever `--by` the retry uses.
Do not call `done` midway through the admitted repair. After all repair work is
committed, `done <ticket>` marks the repair complete; it requires a clean tree
and returns to build routing. Run `next` to resume converge when all tickets
are complete. A clean `review` remains a supported direct path from repair;
review and rerun all required evidence before recording results or readiness.
A changed tree without admission stops for human triage.

At init and when loading an existing ledger, keep the highest count among
`gate.json` and any `review-round` files in `.minime/<task>/` or the older
`.kilo/run/<task>/`. Reconciliation persists only a higher count and leaves
all other ledger fields intact, even when the requested command is blocked.
Lowering the cap affects only new bot repair admissions. Existing counts,
active repairs and readiness checks remain valid.
Do not delete/reinitialize it. A scope change blocks until the human rules; after
revised clarify/chart reviews, `scope --ruling .minime/<task>/ruling.md` adopts the
new accepted documents, resets completion/evidence, and **preserves** `rounds`.
The ruling is a recorded human decision, not permission the script can authenticate.

Writes are serialized by `gate.lock` and atomic replacement. A crash may leave
the lock: confirm no gate process is running before removing only that lock.
Malformed/missing state is a blocker, never an invitation to reset the counter.
