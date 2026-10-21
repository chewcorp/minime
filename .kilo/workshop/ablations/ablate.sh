#!/usr/bin/env bash
# Non-admitting component-label smoke replay; no model is executed.
#
#   ablate.sh <component> [cases-glob] [model:provider...]
#
# Replays identical static targets/checks twice per panel entry, stamped as
# the skill and "<skill>-no-<component>". No component is actually removed.
# --gate-skill keeps check selection identical; labels are not causal evidence.
#
# Panel entries come from explicit args or from ablations/panel.txt.
# Explicit panel args require the preceding cases-glob positional argument.
#
# Exit codes match run.sh (0 pass, 1 verdict fail, 2 unproven, 3+ runner
# error). Either unproven arm stops with 2, never sweep success. Zero matched
# cases is a runner error. Status 0 means smoke replay only, not admission.
#
# shortcut: static replay only; upgrade after real isolated model execution,
# component removal and budget/provenance capture are implemented and proven.
set -euo pipefail

# Only an explicit arm verdict or completed smoke replay may return 0/1/2.
VERDICT_OK=
trap 'rc=$?; if [ -z "$VERDICT_OK" ] && [ "$rc" -lt 3 ]; then exit 3; else exit "$rc"; fi' EXIT
usage() { echo "usage: ablate.sh <component> [cases-glob] [model:provider...]" >&2; exit 3; }
[ $# -ge 1 ] && [ -n "$1" ] || usage
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
component=$1
cases_glob=${2:-"$root/admission/cases/*"}
# Catch a panel entry accidentally supplied in the glob position.
case "$cases_glob" in *:* ) echo "cases-glob must precede panel args" >&2; usage ;; esac
if [ $# -ge 2 ]; then shift 2; else shift; fi
runner="$root/admission/run.sh"
processed=0

# Panel: explicit args win; else read model:provider lines from panel.txt.
panel=()
if [ $# -gt 0 ]; then
  panel=("$@")
else
  panel_file="$(dirname "${BASH_SOURCE[0]}")/panel.txt"
  [ -f "$panel_file" ] || { echo "no panel args and $panel_file missing" >&2; exit 3; }
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%%#*}; line=${line//[[:space:]]/}
    [ -n "$line" ] && panel+=("$line")
  done < "$panel_file"
fi
[ "${#panel[@]}" -ge 1 ] || { echo "panel is empty" >&2; exit 3; }

# Validate the entire panel before any dispatch or evidence append.
for entry in "${panel[@]}"; do
  model=${entry%%:*}
  provider=${entry#*:}
  [ "$model" != "$entry" ] && [ -n "$model" ] && [ -n "$provider" ] \
    || { echo "panel entry must be model:provider: $entry" >&2; exit 3; }
done

[ -f "$runner" ] && [ -x "$runner" ] \
  || { echo "runner missing or not executable: $runner" >&2; exit 3; }
echo "NON-ADMITTING SMOKE REPLAY: static targets; no model execution or component removal"
for entry in "${panel[@]}"; do
  model=${entry%%:*}
  provider=${entry#*:}
  # Expand the glob without splitting checkout or case paths at whitespace.
  IFS=
  for case_dir in $cases_glob; do
    [ -d "$case_dir" ] || continue
    if ! skill=$(jq -r '.skill // "generic"' "$case_dir/checks.json" 2>/dev/null); then
      echo "cannot read skill from $case_dir/checks.json" >&2
      exit 3
    fi
    echo "-- $case_dir ($skill, ablating: $component, model: $model)"
    processed=$((processed + 1))

    rc=0
    "$runner" --model "$model" --provider "$provider" --component full \
      "$case_dir" "$skill" || rc=$?
    [ "$rc" -eq 0 ] || { echo "full smoke arm stopped (rc=$rc) for $case_dir ($model)" >&2; VERDICT_OK=1; exit "$rc"; }

    rc=0
    "$runner" --model "$model" --provider "$provider" --component "$component" \
      --gate-skill "$skill" "$case_dir" "$skill-no-$component" || rc=$?
    case "$rc" in
      0) ;;
      *) echo "without smoke arm stopped (rc=$rc) for $case_dir ($model)" >&2; VERDICT_OK=1; exit "$rc" ;;
    esac
  done
done

if [ "$processed" -eq 0 ]; then
  echo "no case directories matched: $cases_glob" >&2
  exit 3
fi

echo "non-admitting smoke replay complete; rows cannot justify comparison, graduation or retirement"
VERDICT_OK=1
exit 0
