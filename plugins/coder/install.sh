#!/usr/bin/env bash
# install.sh — install the coder delivery loop into Kilo (or opencode via --prefix).
# Clients with a plugin system install from the minime marketplace instead.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./install.sh              # install globally to ~/.config/kilo (default)
  ./install.sh --global     # same as above, explicit
  ./install.sh --project    # install into the current repo's .kilo/
  ./install.sh --prefix DIR # install into DIR (advanced; expects the kilo
                            # config dir layout: agents/ skills/ kilo.json)
  --force-config            # overwrite an existing target kilo.json

Run from the plugin root (the directory containing .claude-plugin/) or an
unpacked release tarball root. Existing payload files are overwritten;
unrelated files in the target are left untouched. Workshop, plans, and
runtime state are never installed.
EOF
}

mode="global"
prefix=""
force_config=""

while [ $# -gt 0 ]; do
  case "$1" in
    --global)  mode="global" ;;
    --project)  mode="project" ;;
    --prefix)  mode="prefix"; prefix="${2:?--prefix requires a directory}"; shift ;;
    --force-config) force_config="1" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown flag: $1" >&2; usage >&2; exit 64 ;;
  esac
  shift
done

# E1: expand a quoted leading tilde in --prefix (the shell won't, once quoted).
case "$prefix" in
  '~')   prefix="$HOME" ;;
  '~/'*) prefix="$HOME/${prefix#'~/'}" ;;
esac

src="$(cd "$(dirname "$0")" && pwd)"
manifest="$src/.claude-plugin/plugin.json"
[ -f "$manifest" ] || { echo "run from the plugin root (no .claude-plugin/plugin.json at $src)" >&2; exit 66; }

src_root="$src/.kilo"
[ -d "$src_root" ] || { echo "no payload dir .kilo at $src" >&2; exit 66; }

# T1/F8: canonicalize the source side of the self-install equality guards
# below — a $0 reached through a symlinked directory (macOS-style /tmp)
# spells src_root differently from dest and the string compare misses it.
# `cd ... && pwd -P` is the POSIX-portable canonicalization (no GNU
# readlink -f on macOS).
src_root="$(CDPATH= cd "$src_root" && pwd -P)"

# shortcut: sed-based JSON version read, upgrade to jq if plugin.json grows
# free-form string fields containing colons adjacent to "version".
version="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$manifest")"
[ -n "$version" ] || { echo "no version in $manifest" >&2; exit 65; }

case "$mode" in
  global)
    dest="${XDG_CONFIG_HOME:-$HOME/.config}/kilo"
    ;;
  project)
    git -C . rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
      echo "--project must run inside a git repo" >&2; exit 65; }
    dest="$(git rev-parse --show-toplevel)/.kilo"
    ;;
  prefix)
    dest="$prefix"
    ;;
esac

# T1/F8: canonicalize dest the same way, so alias spellings of the same
# directory (trailing-slash/dot like .kilo/., symlinked paths) hit the
# self-install equality guards in install_config and the copy block instead
# of evading them and aborting on cp "are the same file".
if [ -d "$dest" ]; then
  # CDPATH= : a relative --prefix must not be retargeted through the
  # user's CDPATH (cd prefers a CDPATH match for bare relative names).
  dest="$(CDPATH= cd "$dest" && pwd -P)"
elif [ -d "$(dirname "$dest")" ]; then
  # Dest not there yet: resolve the spelled parent, keep the final component
  # (a dir ending in /. or / /.. would be -d exactly when its parent is, so
  # the final component here is always a plain missing name).
  dest="$(CDPATH= cd "$(dirname "$dest")" && pwd -P)/$(basename "$dest")"
fi

# agents/ and skills/ live at the plugin root, so installing into it would
# truncate each agent through the sed redirect below.
if [ "$dest" = "$(CDPATH= cd "$src" && pwd -P)" ]; then
  echo "refusing to install into the plugin source itself ($dest)" >&2; exit 64
fi

# Config conflict policy (D5): preserve an existing target kilo.json unless
# --force-config is passed. When source and destination are the same file
# (self-install, E3), there is nothing to write even under --force-config:
# cp would fail with "are the same file" and set -e would abort the install.
install_config() {
  if [ "$dest" = "$src_root" ]; then
    return
  fi
  if [ -f "$dest/kilo.json" ] && [ -z "$force_config" ]; then
    echo "note: $dest/kilo.json exists; skipping (use --force-config to overwrite)" >&2
    return
  fi
  if [ "$force_config" = "1" ] && [ -f "$dest/kilo.json" ]; then
    # Force overwrite discards the target's config policy file (a real user
    # choice), so keep one recoverable copy next to it — a mis-aimed
    # --force-config (e.g. a test run against $HOME) must never be silent
    # data loss. Refresh the backup only when the current config is NOT the
    # one this installer would write anyway: otherwise a repeated force-run
    # would clobber the user's original backup with our own output.
    if ! cmp -s "$dest/kilo.json" "$src_root/kilo.json"; then
      cp "$dest/kilo.json" "$dest/kilo.json.bak"
      echo "note: previous config kept as $dest/kilo.json.bak" >&2
    fi
  fi
  cp "$src_root/kilo.json" "$dest/kilo.json"
  echo "wrote $dest/kilo.json (default model + planner/advisor pins; see the file)"
}

# A4: one stderr notice when an existing target is about to be overwritten.
if [ -d "$dest" ] && [ "$dest" != "$src_root" ]; then
  echo "note: $dest exists; payload paths (agents/, skills/, .gitignore) will be overwritten, unrelated files untouched (kilo.json only with --force-config; then kept as kilo.json.bak)" >&2
fi

mkdir -p "$dest/agents" "$dest/skills"
# Kilo/opencode pass unknown agent frontmatter keys to the model provider as
# request options, so drop the keys only other clients read.
for f in "$src"/agents/*.md; do
  sed '/^disallowedTools:/d; /^readonly:/d' "$f" > "$dest/agents/$(basename "$f")"
done
cp -R "$src/skills/." "$dest/skills/"
install_config

# B1: .kilo/.gitignore is payload — copy it so --global/--prefix/--project
# install the same set. E3: skip when source is destination (--project from
# this repo's root), where cp would fail "are the same file".
if [ "$dest" != "$src_root" ]; then
  cp "$src_root/.gitignore" "$dest/.gitignore"
fi

# Project installs additionally keep .kilo/run/ (transient loop state) out of
# git via the TARGET repo's root .gitignore: a pattern ".kilo/run/" in
# .kilo/.gitignore cannot match that path relative to the repo root.
# A5: tolerate a root .gitignore missing its trailing newline.
if [ "$mode" = "project" ]; then
  root_gitignore="$(git rev-parse --show-toplevel)/.gitignore"
  if ! grep -qxF '.kilo/run/' "$root_gitignore" 2>/dev/null; then
    if [ -s "$root_gitignore" ] && [ -n "$(tail -c1 "$root_gitignore")" ]; then
      printf '\n' >> "$root_gitignore"
    fi
    printf '.kilo/run/\n' >> "$root_gitignore"
  fi
fi

echo "installed coder $version -> $dest"
echo "verify: restart kilo, then /status should list agents (planner, researcher, ...) and the deliver skill"
