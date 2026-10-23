# Component evals

Lightweight cases per kilo-mms component (skills and agents) plus an end-to-end
tracer, for mapping weak points before optimising one. Every case runs the real payload
from this repo; `VARIANT=<name>` overlays `variants/<name>/` (laid out like `.kilo/`)
on top of it, so an A/B is the same case run with and without `VARIANT`.

- `run_case.sh <case-dir> [rep]`: one run on `$MODEL` (default `kilo/kilo-auto/free`)
  in a throwaway HOME, with every agent and `small_model` pinned to `$MODEL`; refuses
  to run unpinned; exits 4 if the real `~/.config/kilo` changed. Outputs land in
  `<case>/runs/<date>/<model>-<rep>/`; only `result.json` and `oracle.txt` are
  committed. `../runs.sh pack <run-dir>...` uploads the raw transcript, export and
  patch to the `eval-runs` release and records the asset and sha256 in `result.json`;
  `../runs.sh fetch` brings them back for rescoring. Ship variant code and its
  results as separate PRs.
- `run_map.sh [case...]`: every case `REPS` times, then the summary table.
- `python3 lib.py summary cases`: pass/checks/median time per case, plus e2e root causes.
- `python3 lib.py selftest`: every oracle must pass its known-good result and fail
  both the untouched baseline and a known-bad one. Run it after editing a case.

A case is `cases/<id>/case.py` (see `lib.py` for the contract). The e2e tracer traces
each requirement through every stage artifact and blames the first stage where it
drops out, so a failure seen at prove that was never charted is charted's.

A component counts as weak only when it fails on two or more of its cases; a
single-case failure means check the case first.
