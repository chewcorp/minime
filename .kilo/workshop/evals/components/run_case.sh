#!/bin/bash
# Run one component case once on $MODEL in a sandboxed HOME, then score it.
# Usage: run_case.sh <case-dir> [rep]   Output: <case-dir>/runs/<date>/<model>-<rep>/
# Stops with exit 4 if the real ~/.config/kilo changed during the run.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
case_dir="$(cd "${1:?usage: run_case.sh <case-dir> [rep]}" && pwd)"
rep="${2:-1}"
model="${MODEL:-kilo/kilo-auto/free}"
out="$case_dir/runs/$(date -u +%F)/${model//\//_}-$rep"
work="$(mktemp -d "${TMPDIR:-/tmp}/comp-work-XXXXXX")"
sandbox="$(mktemp -d "${TMPDIR:-/tmp}/comp-home-XXXXXX")"
trap 'rm -rf "$work" "$sandbox"' EXIT

# Sandbox HOME (see the F8 tracer): only kilo's auth file crosses over.
real_auth="${XDG_DATA_HOME:-$HOME/.local/share}/kilo/auth.json"
mkdir -p "$sandbox/.config" "$sandbox/.local/share/kilo" "$sandbox/.cache"
[ -f "$real_auth" ] && cp "$real_auth" "$sandbox/.local/share/kilo/auth.json"
: > "$sandbox/.gitconfig"
before="$(python3 "$here/lib.py" snapshot "$HOME/.config/kilo")"

python3 "$here/lib.py" setup "$case_dir" "$work" "$model"
agent="$(python3 "$here/lib.py" get "$case_dir" AGENT)"
prompt="$(python3 "$here/lib.py" get "$case_dir" PROMPT)"
mkdir -p "$out"
tmo="$(command -v timeout || command -v gtimeout || true)"
sandboxed() {
  env -u GITHUB_TOKEN -u GH_TOKEN -u GH_ENTERPRISE_TOKEN \
    HOME="$sandbox" XDG_CONFIG_HOME="$sandbox/.config" \
    XDG_DATA_HOME="$sandbox/.local/share" XDG_CACHE_HOME="$sandbox/.cache" \
    GIT_CONFIG_GLOBAL="$sandbox/.gitconfig" GIT_AUTHOR_NAME=eval GIT_AUTHOR_EMAIL=eval@local \
    GIT_COMMITTER_NAME=eval GIT_COMMITTER_EMAIL=eval@local "$@"
}
# Pin every listed agent (and small_model) to $model through KILO_CONFIG_CONTENT,
# which beats project config, then refuse to run if anything resolves elsewhere
# (same guard as the F8 tracer).
agents="$(cd "$work" && sandboxed kilo agent list 2>/dev/null \
  | sed $'s/\x1b\\[[0-9;]*m//g' | awk '/^[a-z][a-z-]* \((primary|subagent|all)\)$/ {print $1}')"
[ -n "$agents" ] || { echo "no agents listed; refusing to run unpinned" >&2; exit 65; }
export KILO_CONFIG_CONTENT="$(python3 -c 'import json,sys; m=sys.argv[1]; print(json.dumps({"model":m,"small_model":m,"agent":{a:{"model":m} for a in sys.argv[2:]}}))' "$model" $agents)"
models="$(cd "$work" && sandboxed kilo debug config 2>/dev/null | grep '"\(small_\)\{0,1\}model"' || true)"
if [ -z "$models" ] || grep -vqF "\"$model\"" <<<"$models"; then
  echo "resolved config not pinned to $model; refusing to run:" >&2; echo "$models" >&2; exit 65
fi

start=$(date +%s); run_rc=0
sandboxed ${tmo:+$tmo 900} kilo run --auto --log-level ERROR -m "$model" --agent "$agent" \
  --title "comp-$(basename "$case_dir")-$rep" --dir "$work" "$prompt" \
  > "$out/session.txt" 2>&1 || run_rc=$?
secs=$(( $(date +%s) - start ))
# Bare `kilo export` opens an interactive session picker and hangs (kilo
# 7.8.15), so export the newest session by id; messages carry tokens and cost.
sid="$(cd "$work" && sandboxed kilo session list --format json -n 1 </dev/null 2>/dev/null \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["id"])' 2>/dev/null || true)"
(cd "$work" && sandboxed ${tmo:+$tmo 60} kilo export "$sid" </dev/null) > "$out/export.json" 2>/dev/null || true

git -C "$work" add -A >/dev/null 2>&1 || true
git -C "$work" diff --cached "$(cat "$work/.git/EVAL_BASE")" > "$out/diff.patch" || true
printf '{"model":"%s","rep":%s,"secs":%s,"run_rc":%s,"time":"%s"}\n' \
  "$model" "$rep" "$secs" "$run_rc" "$(date -u +%FT%TZ)" > "$out/result.json"
verdict=0  # oracles run model-edited code: same HOME/token sandbox as the run
sandboxed python3 "$here/lib.py" check "$case_dir" "$work" "$out/session.txt" "$out/result.json" \
  > "$out/oracle.txt" 2>&1 || verdict=$?
echo "$(basename "$case_dir") rep=$rep verdict=$([ $verdict = 0 ] && echo pass || echo fail) secs=$secs out=$out"

if [ "$before" != "$(python3 "$here/lib.py" snapshot "$HOME/.config/kilo")" ]; then
  echo "TRIPWIRE: real ~/.config/kilo changed during this run; restore it and stop" >&2
  exit 4
fi
exit "$verdict"
