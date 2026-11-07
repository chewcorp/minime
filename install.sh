#!/usr/bin/env bash
# install.sh — install minime plugins into opencode, which has no plugin
# marketplace. Other clients install from the marketplace (see README).
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--project | --prefix DIR] [plugin ...]
  (default)     install into ~/.config/opencode
  --project     install into the current git repo's .opencode/
  --prefix DIR  install into DIR (agents/ and skills/ are created under it)
  plugin ...    plugins to install (default: every plugin under plugins/)
Existing files with the same names are overwritten; others are left alone.
USAGE
}

dest="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
plugins=()
while [ $# -gt 0 ]; do
  case "$1" in
    --project) dest="$(git rev-parse --show-toplevel)/.opencode" ;;
    --prefix)  dest="${2:?--prefix requires a directory}"; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "unknown flag: $1" >&2; usage >&2; exit 64 ;;
    *) plugins+=("$1") ;;
  esac
  shift
done

root="$(cd "$(dirname "$0")" && pwd)"
[ ${#plugins[@]} -gt 0 ] || plugins=($(ls "$root/plugins"))

mkdir -p "$dest/agents" "$dest/skills"
for p in "${plugins[@]}"; do
  src="$root/plugins/$p"
  [ -f "$src/.claude-plugin/plugin.json" ] || { echo "no plugin: $p" >&2; exit 66; }
  cp -R "$src/skills/." "$dest/skills/"
  # Skills resolve support dirs (templates/, references/) from the plugin
  # root, which is skills/.. once installed.
  for d in "$src"/*/; do
    case "$(basename "$d")" in agents|skills) ;; *) cp -R "$d" "$dest/" ;; esac
  done
  # opencode forwards unknown agent frontmatter keys to the model provider,
  # so drop the keys only other clients read.
  for f in "$src"/agents/*.md; do
    [ -e "$f" ] || continue
    sed '/^disallowedTools:/d; /^readonly:/d' "$f" > "$dest/agents/$(basename "$f")"
  done
  echo "installed $p -> $dest"
done
echo "verify: restart opencode; its agent list should include the plugins' agents"
