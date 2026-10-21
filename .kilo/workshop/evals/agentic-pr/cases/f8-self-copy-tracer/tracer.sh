#!/bin/bash
# f8 tracer: run one arm (current|absent) of the self-copy case, then oracle
# the produced install.sh. Usage: tracer.sh ARM  (from the case directory;
# audit dir at AUDIT_DIR, default <case>/.tracer/ARM). Shortcut: arm prompts
# differ by one line; fixture payload is deleted for absent, kept for current.
set -euo pipefail
case_dir="$(cd "$(dirname "$0")" && pwd)"
arm="${1:?usage: tracer.sh current|absent}"
case "$arm" in current|absent) ;; *) echo "unknown arm: $arm" >&2; exit 64 ;; esac
audit="${AUDIT_DIR:-$case_dir/.tracer/$arm}"
work="$(mktemp -d "${TMPDIR:-/tmp}/f8-$arm-XXXXXX")"
trap 'rm -rf "$work"' EXIT

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

mkdir -p "$audit"
kilo run --auto --log-level ERROR -m "${MODEL:-kilo/kilo-auto/free}" --agent build \
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
