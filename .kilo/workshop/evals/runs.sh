#!/bin/bash
# Raw eval output (transcripts, exports, patches) lives in release assets, not git.
# Usage: runs.sh pack <run-dir>...    tar each run's raw files, upload to the release,
#                                     record artifacts {uri, sha256} in its result.json
#        runs.sh fetch <run-dir>...   download, check sha256, unpack back into the run dir
# Needs an authenticated gh. Run dirs keep result.json/oracle.txt in git (see .gitignore).
set -euo pipefail
tag="${RUNS_RELEASE:-eval-runs}"
repo="${RUNS_REPO:-xchewtoyx/kilo-mms}"
raw=(export.json 'session*.txt' diff.patch 'install*.sh')
mode="${1:?usage: runs.sh pack|fetch <run-dir>...}"; shift

record() {  # the small json every run keeps in git: result.json, or metadata-<arm>.json for f8
  local f; for f in "$1"/result.json "$1"/metadata*.json; do [ -f "$f" ] && { echo "$f"; return; }; done
  echo "$1/result.json"
}

asset_name() {  # unique per run: <case>-<date>-<run>.tar.gz
  local d; d="$(cd "$1" && pwd)"
  echo "$(basename "$(dirname "$(dirname "$(dirname "$d")")")")-$(basename "$(dirname "$d")")-$(basename "$d").tar.gz"
}

case "$mode" in
pack)
  gh release view "$tag" -R "$repo" >/dev/null 2>&1 ||
    gh release create "$tag" -R "$repo" --prerelease --title "Eval run artifacts" \
      --notes "Raw eval output; each run's result.json names its asset and sha256." >/dev/null
  for run in "$@"; do
    files=(); for p in "${raw[@]}"; do for f in "$run"/$p; do [ -f "$f" ] && files+=("$(basename "$f")"); done; done
    [ ${#files[@]} -gt 0 ] || { echo "skip $run: no raw files" >&2; continue; }
    name="$(asset_name "$run")"; tmp="$(mktemp -d)"
    tar -C "$run" -czf "$tmp/$name" "${files[@]}"
    sum="$(shasum -a 256 "$tmp/$name" | cut -d' ' -f1)"
    gh release upload "$tag" -R "$repo" --clobber "$tmp/$name" >/dev/null
    python3 - "$(record "$run")" "https://github.com/$repo/releases/download/$tag/$name" "$sum" <<'EOF'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
data = json.loads(p.read_text()) if p.exists() else {}
data["artifacts"] = {"uri": sys.argv[2], "sha256": sys.argv[3]}
p.write_text(json.dumps(data, indent=2) + "\n")
EOF
    rm -rf "$tmp"; echo "packed $run -> $name"
  done ;;
fetch)
  for run in "$@"; do
    read -r uri sum < <(python3 -c 'import json,sys; a=json.load(open(sys.argv[1]))["artifacts"]; print(a["uri"], a["sha256"])' "$(record "$run")")
    tmp="$(mktemp -d)"
    gh release download "$tag" -R "$repo" -p "${uri##*/}" -D "$tmp"
    echo "$sum  $tmp/${uri##*/}" | shasum -a 256 -c - >/dev/null
    tar -C "$run" -xzf "$tmp/${uri##*/}"; rm -rf "$tmp"; echo "fetched $run"
  done ;;
*) echo "unknown mode: $mode" >&2; exit 64 ;;
esac
