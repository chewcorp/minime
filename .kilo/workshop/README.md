# Workshop (plugin developers only — never installed into consumer repos)

Admission eval, budget-matched comparison, hill-climb log, component/tool/ACI ablations, maintenance eval wiring. Nothing here becomes consumer-mandatory; wins graduate only as small skills/gates with their own checks.

Layout: `SCHEMA.md` (JSONL results contract), `admission/` (`run.sh` tracer + `cases/` stub corpus), `hillclimb/LOG.md` (decision log), `ablations/` (`ablate.sh` scaffold), `evals/` (maintenance suite, deferred).

Result lines are append-only JSONL in `admission/results.jsonl`; per-run proof artifacts (re-runnable) live under `/tmp/kilo-workshop-proof/`.
