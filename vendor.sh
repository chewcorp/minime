#!/usr/bin/env bash
# vendor.sh <plugin> <tag|tarball> — replace plugins/<plugin> with a released
# payload from chewcorp/minime-<plugin>. A local tarball path (from that repo's
# ./release.sh --build-only) vendors an unreleased build for testing.
# vendor.sh --verify <plugin> — compare the committed payload with its release.
set -euo pipefail
verify=false
if [ "${1:-}" = --verify ]; then
  verify=true
  shift
fi
plugin="${1:?usage: vendor.sh <plugin> <tag|tarball> | vendor.sh --verify <plugin>}"
case "$plugin" in
  ""|*[!a-z0-9-]*) echo "plugin name must be lowercase letters, digits and dashes: $plugin" >&2; exit 64 ;;
esac
root="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if "$verify"; then
  version="$(git -C "$root" show "HEAD:plugins/$plugin/.claude-plugin/plugin.json" | python3 -c '
import json, re, sys
version = json.load(sys.stdin)["version"]
if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
    sys.exit("invalid release version")
print(version)
')"
  ref="v$version"
  pattern="minime-$plugin-$version.tar.gz"
else
  ref="${2:?usage: vendor.sh <plugin> <tag|tarball>}"
  pattern="minime-$plugin-*.tar.gz"
fi

if ! "$verify" && [ -f "$ref" ]; then
  tarball="$ref"
else
  gh release download "$ref" --repo "chewcorp/minime-$plugin" --pattern "$pattern" --dir "$tmp"
  tarballs=("$tmp"/$pattern)
  [ "${#tarballs[@]}" -eq 1 ] && [ -f "${tarballs[0]}" ] || { echo "expected one release tarball for $plugin $ref" >&2; exit 65; }
  tarball="${tarballs[0]}"
fi
tar -xzf "$tarball" -C "$tmp"
[ -f "$tmp/$plugin/.claude-plugin/plugin.json" ] || { echo "no $plugin/.claude-plugin/plugin.json in $tarball" >&2; exit 65; }

if "$verify"; then
  python3 - "$root" "$plugin" "$tmp/$plugin" <<'PY'
import os
from pathlib import Path
import stat
import subprocess
import sys

root, plugin, release = sys.argv[1:]
release = Path(release)
prefix = f"plugins/{plugin}/"

def git(*args):
    return subprocess.check_output(["git", "-C", root, *args])

expected = {}
for file in release.rglob("*"):
    path = prefix + file.relative_to(release).as_posix()
    mode = file.lstat().st_mode
    if stat.S_ISLNK(mode):
        expected[path] = (b"120000", os.readlink(os.fsencode(file)))
    elif stat.S_ISREG(mode):
        expected[path] = (b"100755" if mode & stat.S_IXUSR else b"100644", file.read_bytes())
    elif not stat.S_ISDIR(mode):
        sys.exit(f"unsupported file type in release: {path!r}")

for entry in git("ls-tree", "-rz", "HEAD", "--", prefix).split(b"\0")[:-1]:
    meta, name = entry.split(b"\t", 1)
    mode, kind, oid = meta.split()
    path = os.fsdecode(name)
    if kind != b"blob" or expected.pop(path, None) != (mode, git("cat-file", "blob", oid)):
        sys.exit(f"vendored file differs from release: {path!r}")
if expected:
    sys.exit(f"vendored file missing from HEAD: {next(iter(expected))!r}")
PY
  echo "verified $plugin $version against its release tarball"
  exit 0
fi

rm -rf "$root/plugins/$plugin"
mv "$tmp/$plugin" "$root/plugins/$plugin"
# -f: payload files can be self-ignored (a plugin may ship a .gitignore listing itself).
git -C "$root" add -f "plugins/$plugin"
echo "vendored $plugin $(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$root/plugins/$plugin/.claude-plugin/plugin.json") from $ref"
