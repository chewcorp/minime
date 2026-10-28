#!/bin/bash
# f8 tracer: run one arm (current|absent) of the self-copy case, then oracle
# the produced install.sh. Usage: tracer.sh ARM  (from the case directory;
# audit dir at AUDIT_DIR, default <case>/runs/<date>/ARM-$RUN_N). Shortcut: arm prompts
# differ by one line; fixture payload is deleted for absent, kept for current.
set -euo pipefail
case_dir="$(cd "$(dirname "$0")" && pwd)"
arm="${1:?usage: tracer.sh current|absent}"
case "$arm" in current|absent) ;; *) echo "unknown arm: $arm" >&2; exit 64 ;; esac
audit="${AUDIT_DIR:-$case_dir/runs/$(date -u +%F)/$arm-${RUN_N:-1}}"
work="$(mktemp -d "${TMPDIR:-/tmp}/f8-$arm-XXXXXX")"
# Sandbox HOME: a 2026-10-22 subject ran ./install.sh --global and wrote the
# user's real ~/.config/kilo. Only kilo's auth file crosses over.
sandbox="$(mktemp -d "${TMPDIR:-/tmp}/f8-home-XXXXXX")"
trap 'rm -rf "$work" "$sandbox"' EXIT
real_auth="${XDG_DATA_HOME:-$HOME/.local/share}/kilo/auth.json"
mkdir -p "$sandbox/.config" "$sandbox/.local/share/kilo" "$sandbox/.cache"
[ -f "$real_auth" ] && cp "$real_auth" "$sandbox/.local/share/kilo/auth.json"
: > "$sandbox/.gitconfig"

cp "$case_dir/target.txt" "$work/install.sh"
chmod +x "$work/install.sh"
cp -r "$case_dir/fixture_kilo" "$work/.kilo"
echo '{"version":"0.1.0"}' > "$work/plugin.json"
git -C "$work" init -q
if [ "$arm" = absent ]; then
  rm -rf "$work/.kilo/agents" "$work/.kilo/skills" \
       "$work/.kilo/kilo.json" "$work/.kilo/.gitignore"
fi

prompt="Repair install.sh in the current directory (a plugin repo): running ./install.sh --project from inside the plugin repo itself aborts with 'cp: ... are the same file'. Make self-installation a clean no-op without breaking installs into a different destination and without removing copying that legitimate installs need. Edit install.sh directly; do not install packages or use the network."
[ "$arm" = absent ] && prompt="$prompt Note: this repo's payload dirs are intentionally empty; work only on install.sh."

model="${MODEL:-kilo/kilo-auto/free}"
sandbox_env=(env -u GITHUB_TOKEN -u GH_TOKEN -u GH_ENTERPRISE_TOKEN
  HOME="$sandbox" XDG_CONFIG_HOME="$sandbox/.config"
  XDG_DATA_HOME="$sandbox/.local/share" XDG_CACHE_HOME="$sandbox/.cache"
  GIT_CONFIG_GLOBAL="$sandbox/.gitconfig")

# Pin every agent kilo sees in $work to $model so planner/advisor can't
# escalate to their paid project-pinned models. Only existing agents: a config
# entry for an unknown name creates that agent, which would leak into absent.
# KILO_CONFIG_CONTENT, because the project .kilo/kilo.json beats global config.
agents="$(cd "$work" && "${sandbox_env[@]}" kilo agent list 2>/dev/null \
  | sed $'s/\x1b\\[[0-9;]*m//g' | awk '/^[a-z][a-z-]* \((primary|subagent|all)\)$/ {print $1}')"
[ -n "$agents" ] || { echo "no agents listed; refusing to run unpinned" >&2; exit 65; }
mkdir -p "$sandbox/.config/kilo"
python3 -c 'import json,sys; m=sys.argv[1]; print(json.dumps({"model":m,"small_model":m,"agent":{a:{"model":m} for a in sys.argv[2:]}}))' \
  "$model" $agents > "$sandbox/.config/kilo/kilo.json"
sandbox_env+=(KILO_CONFIG_CONTENT="$(cat "$sandbox/.config/kilo/kilo.json")")
models="$(cd "$work" && "${sandbox_env[@]}" kilo debug config 2>/dev/null \
  | grep '"\(small_\)\{0,1\}model"' || true)"
if [ -z "$models" ] || grep -vqF "\"$model\"" <<<"$models"; then
  echo "resolved config not pinned to $model; refusing to run:" >&2
  echo "$models" >&2; exit 65
fi

mkdir -p "$audit"
"${sandbox_env[@]}" \
kilo run --auto --log-level ERROR -m "$model" --agent build \
  --title "f8-tracer-$arm-$(basename "$work")" --dir "$work" "$prompt" \
  > "$audit/session-$arm.txt" 2>&1 || run_rc=$?

cp "$work/install.sh" "$audit/install-$arm.sh"
python3 "$case_dir/oracle.py" "$work/install.sh" > "$audit/oracle-$arm.txt" 2>&1 && verdict=pass || verdict=fail
printf '{"arm":"%s","verdict":"%s","work_fixture_seen":"%s","time":"%s"}\n' \
  "$arm" "$verdict" "$([ "$arm" = current ] && echo payload-intact || echo payload-removed)" \
  "$(date -u +%FT%TZ)" > "$audit/metadata-$arm.json"
echo "arm=$arm verdict=$verdict audit=$audit"
# Nonzero exit when the produced artifact failed the oracle or the run itself
# failed; completed run + passing verdict exits 0. shortcut: run_rc present
# means the transcript may be truncated; the audit still carries what exists.
[ -z "${run_rc:-}" ] && [ "$verdict" = pass ]
