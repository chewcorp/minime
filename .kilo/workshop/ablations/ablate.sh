#!/usr/bin/env bash
# Component-ablation tracer bullet.
#
#   ablate.sh <component> [cases-glob]
#
# Component ablation per the plan (component-level, hold 3/4 at seed, vary 1):
# runs every matched case against two arms — the skill under test ("full") and
# "<skill>-no-<component>" — and writes both result lines so the delta is
# comparable. A real ablation replaces one behaviour; here the toggled arm is a
# named placeholder until components can actually be varied.
#
# Exit-code contract with run.sh: 0 pass, 1 failed check, 2 unproven, 3+ runner
# error. A sweep must fail loudly on verdict fail (1) and runner error (3+);
# unproven (2) is legitimate for an arm whose checks gate to another skill.
# The full arm may not be unproven — if it is, the sweep ran nothing real.
# A sweep over zero matched directories is an error, not a success.
#
# shortcut: the ablated arm runs identical mechanics (--gate-skill keeps check
# selection on the full skill) with a different recorded label; upgrade when a
# component can be mechanically removed (e.g. skip the advisor brief, drop the
# approve table) and the runner grows a flag for it.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
component=${1:?"usage: ablate.sh <component> [cases-glob]"}
cases_glob=${2:-"$root/admission/cases/*"}
runner="$root/admission/run.sh"
processed=0

# Expand the glob without splitting checkout or case paths at whitespace.
IFS=
for case_dir in $cases_glob; do
  [ -d "$case_dir" ] || continue
  if ! skill=$(jq -r '.skill // "generic"' "$case_dir/checks.json" 2>/dev/null); then
    echo "cannot read skill from $case_dir/checks.json" >&2
    exit 3
  fi
  echo "-- $case_dir ($skill, ablating: $component)"
  processed=$((processed + 1))

  # Full arm: only a clean pass (0) keeps the sweep going. A fail (1) is a
  # real verdict against the un-ablated skill and must surface; unproven (2)
  # means the case gated every check away from its own skill — malformed setup.
  rc=0; "$runner" "$case_dir" "$skill" || rc=$?
  [ "$rc" -eq 0 ] || { echo "full arm failed (rc=$rc) for $case_dir" >&2; exit "$rc"; }

  # Ablated arm: pass (0) or unproven (2) both carry information; fail (1) is
  # the regression signal the sweep exists to detect; 3+ is runner error.
  rc=0; "$runner" "$case_dir" "$skill-no-$component" --gate-skill "$skill" || rc=$?
  case "$rc" in
    0|2) ;;
    *) echo "ablated arm failed (rc=$rc) for $case_dir" >&2; exit "$rc" ;;
  esac
done

if [ "$processed" -eq 0 ]; then
  echo "no case directories matched: $cases_glob" >&2
  exit 3
fi

echo "compare: jq -c 'select(.skill | test(\"-no-\"))' $root/admission/results.jsonl"
exit 0
