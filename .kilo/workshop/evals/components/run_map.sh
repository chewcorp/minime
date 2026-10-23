#!/bin/bash
# Run every case (or the named ones) REPS times on $MODEL; stop on any runner error or the config tripwire.
# Usage: run_map.sh [case-name...]   Then: python3 lib.py summary cases > MAP-<date>.md
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
names=("$@")
[ ${#names[@]} -gt 0 ] || names=($(ls "$here/cases"))
for name in "${names[@]}"; do
  reps="$(python3 "$here/lib.py" get "$here/cases/$name" REPS)"
  for rep in $(seq 1 "$reps"); do
    "$here/run_case.sh" "$here/cases/$name" "$rep"
    rc=$?
    [ $rc -le 1 ] || exit $rc  # 1 is an oracle fail; anything else (65 unpinned, 4 tripwire) stops the map
  done
done
python3 "$here/lib.py" summary "$here/cases"
