#!/usr/bin/env bash
# Retirement is unsupported: static replay cannot remove rule text or execute
# models. No environment override, arm dispatch, result append or proposal sink.
#
#   retire.sh <rule-id> <skill> [cases-glob]
#
# Exit 1 only for an existing pending-human backlog; otherwise exit 3 (usage,
# infrastructure or unsupported capability). No successful retirement verdict.
set -euo pipefail

BACKLOG_OK=
trap 'rc=$?; if [ -z "$BACKLOG_OK" ] && [ "$rc" -lt 3 ]; then exit 3; else exit "$rc"; fi' EXIT
usage() { echo "usage: retire.sh <rule-id> <skill> [cases-glob]" >&2; exit 3; }
[ $# -ge 2 ] && [ $# -le 3 ] && [ -n "$1" ] && [ -n "$2" ] || usage
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
log="$root/hillclimb/LOG.md"

# Validate the whole panel even though dispatch is disabled.
panel=()
panel_file="$(dirname "${BASH_SOURCE[0]}")/panel.txt"
[ -f "$panel_file" ] || { echo "panel file missing: $panel_file" >&2; exit 3; }
while IFS= read -r line || [ -n "$line" ]; do
  line=${line%%#*}; line=${line//[[:space:]]/}
  [ -n "$line" ] && panel+=("$line")
done < "$panel_file"
[ "${#panel[@]}" -ge 1 ] || { echo "panel is empty" >&2; exit 3; }
for entry in "${panel[@]}"; do
  model=${entry%%:*}; provider=${entry#*:}
  [ "$model" != "$entry" ] && [ -n "$model" ] && [ -n "$provider" ] \
    || { echo "panel entry must be model:provider: $entry" >&2; exit 3; }
done

[ -f "$log" ] || { echo "LOG not found: $log" >&2; exit 3; }
# Only unresolved headings block, not prose mentions of the status token.
rc=0
grep -qE '^### pending:.*\[pending-human\]' "$log" || rc=$?
case "$rc" in
  0)
    echo "pending-human retirement backlog present — replace the heading marker on resolution" >&2
    grep -nE '^### pending:.*\[pending-human\]' "$log" >&2
    BACKLOG_OK=1
    exit 1 ;;
  1) ;;
  *) echo "cannot read retirement backlog (grep rc=$rc)" >&2; exit 3 ;;
esac

echo "retirement unsupported: no real rule-removal arm or model execution; no work dispatched or evidence appended" >&2
exit 3
