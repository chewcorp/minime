#!/usr/bin/env bash
# vendor.sh <plugin> <tag|tarball> — replace plugins/<plugin> with a released
# payload from chewcorp/minime-<plugin>. A local tarball path (from that repo's
# ./release.sh --build-only) vendors an unreleased build for testing.
set -euo pipefail
plugin="${1:?usage: vendor.sh <plugin> <tag|tarball>}"
ref="${2:?usage: vendor.sh <plugin> <tag|tarball>}"
root="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if [ -f "$ref" ]; then
  tarball="$ref"
else
  gh release download "$ref" --repo "chewcorp/minime-$plugin" --pattern "minime-$plugin-*.tar.gz" --dir "$tmp"
  tarball="$(ls "$tmp"/minime-"$plugin"-*.tar.gz)"
fi
tar -xzf "$tarball" -C "$tmp"
[ -f "$tmp/$plugin/.claude-plugin/plugin.json" ] || { echo "no $plugin/.claude-plugin/plugin.json in $tarball" >&2; exit 65; }

rm -rf "$root/plugins/$plugin"
mv "$tmp/$plugin" "$root/plugins/$plugin"
echo "vendored $plugin $(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$root/plugins/$plugin/.claude-plugin/plugin.json") from $ref"
