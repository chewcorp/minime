# Workshop (plugin developers only — never installed into consumer repos)

Non-admitting foundation for future admission evals and budget-matched comparisons. Current runners replay static fixtures: model/provider/component values are labels, not executed models or removed instructions. Nothing here becomes consumer-mandatory; smoke results justify neither graduation nor retirement.

Layout: `SCHEMA.md` (JSONL contract and evidence limits), `admission/` (`run.sh` static checker + `cases/` stub corpus), `hillclimb/LOG.md` (decision policy and pending-human backlog), `ablations/` (`ablate.sh` non-admitting smoke replay, `retire.sh` disabled retirement capability, `panel.txt` labels), `evals/` (seed audition cases, `agentic-pr/` first).

Result lines are append-only JSONL in `admission/results.jsonl`; per-run proof artifacts (re-runnable) live under `/tmp/kilo-workshop-proof/`.

Existing JSONL is historical smoke data, including legacy unstamped rows. Preserve it; do not include it in live model or effectiveness comparisons. Real execution, isolated instruction-changing arms, metering and attributable provenance are still required.

## Smoke replay CLI

From the repo root (requires Bash, jq and Python 3; no GNU grep/date extensions):

```bash
bash .kilo/workshop/ablations/ablate.sh advisor-brief '.kilo/workshop/admission/cases/*' kimi-k3:ollama-cloud
```

The positional cases glob must precede explicit `model:provider` entries; to use the default panel, omit the panel arguments. With no glob or panel arguments, the default admission cases and `panel.txt` apply. Status 0 means only a completed smoke replay; 1 is a failed check, 2 is an unproven arm, and 3+ is usage/infrastructure failure. An unproven arm stops the sweep, never becomes success.

`retire.sh <rule-id> <skill> [cases-glob]` retains its positional grammar but never dispatches arms or appends results/proposals. It exits 3 for unsupported capability (including empty/no-match case sets); no environment variable enables it. A pre-existing unresolved backlog exits 1 instead. Resolving that backlog does not enable retirement.

Focused contract proof: `python3 .kilo/workshop/ablations/test_sweeps.py -v`. Fake runners in disposable copies are unit evidence only, not model execution or real evaluator proof.

Actual static-runner/oracle regression proof: `python3 .kilo/workshop/admission/test_oracles.py -v`. This includes controlled release-order doubles (not GitHub integration) and real disposable self/distinct copies; no case text is executed.
