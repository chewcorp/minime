#!/usr/bin/env bash
# vendor.sh <plugin> <tag|tarball> — replace plugins/<plugin> with a released
# payload from chewcorp/minime-<plugin>. A local tarball path (from that repo's
# ./release.sh --build-only) vendors an unreleased build for testing.
# vendor.sh --verify <plugin> [commit [base]] — compare the committed payload with its release.
set -euo pipefail
verify=false
if [ "${1:-}" = --verify ]; then
  verify=true
  shift
fi
plugin="${1:?usage: vendor.sh <plugin> <tag|tarball> | vendor.sh --verify <plugin> [commit [base]]}"
case "$plugin" in
  ""|*[!a-z0-9-]*) echo "plugin name must be lowercase letters, digits and dashes: $plugin" >&2; exit 64 ;;
esac
root="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if "$verify"; then
  commit="$(git -C "$root" rev-parse --verify --end-of-options "${2:-HEAD}^{commit}")"
  entry="$(git -C "$root" ls-tree "$commit" -- "plugins/$plugin")"
  if [ -z "$entry" ]; then
    if [ -z "${3:-}" ]; then
      echo "no vendored plugin $plugin in the selected commit" >&2
      exit 66
    fi
    base="$(git -C "$root" rev-parse --verify --end-of-options "$3^{commit}")"
    if [ "$(git -C "$root" cat-file -t "$base:plugins/$plugin" 2>/dev/null)" != tree ]; then
      echo "no vendored plugin $plugin in the base commit" >&2
      exit 66
    fi
    python3 - "$root" "$plugin" "$commit" <<'PY'
import json
import posixpath
import subprocess
import sys

root, plugin, commit = sys.argv[1:]
catalogs = (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json",
            ".grok-plugin/marketplace.json", "package.json")
prefix = f"plugins/{plugin}"

def git(*args):
    return subprocess.check_output(["git", "-C", root, *args])

def refers_to_plugin(path):
    if not isinstance(path, str):
        return False
    path = posixpath.normpath(path)
    return path == prefix or path.startswith(prefix + "/")

for catalog in git("ls-tree", "--name-only", commit, "--", *catalogs).decode().splitlines():
    data = json.loads(git("show", f"{commit}:{catalog}"))
    if catalog == "package.json":
        listed = any(refers_to_plugin(path) for paths in data.get("pi", {}).values()
                     if isinstance(paths, list) for path in paths)
    else:
        listed = False
        for item in data["plugins"]:
            source = item.get("source")
            if isinstance(source, dict):
                source = source.get("path")
            if item.get("name") == plugin or refers_to_plugin(source):
                listed = True
                break
    if listed:
        sys.exit(f"removed plugin {plugin} is still listed in {catalog}")
PY
    echo "removed $plugin; no vendored files to verify"
    exit 0
  fi
  if [ "${PR_REPO+x}" = x ]; then
    if [ "$PR_REPO" != "$GITHUB_REPOSITORY" ]; then
      echo "::error::Vendored plugins must be updated by a marketplace branch"
      exit 1
    fi
    : "${GH_TOKEN:?MINIME_RELEASE_READ_TOKEN is required to read private plugin releases}"
  fi
  version="$(git -C "$root" show "$commit:plugins/$plugin/.claude-plugin/plugin.json" | python3 -c '
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
  python3 - "$root" "$plugin" "$tmp/$plugin" "$commit" <<'PY'
import os
from pathlib import Path
import stat
import subprocess
import sys

root, plugin, release, commit = sys.argv[1:]
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

for entry in git("ls-tree", "-rz", commit, "--", prefix).split(b"\0")[:-1]:
    meta, name = entry.split(b"\t", 1)
    mode, kind, oid = meta.split()
    path = os.fsdecode(name)
    if kind != b"blob" or expected.pop(path, None) != (mode, git("cat-file", "blob", oid)):
        sys.exit(f"vendored file differs from release: {path!r}")
if expected:
    sys.exit(f"vendored file missing from commit: {next(iter(expected))!r}")
PY
  echo "verified $plugin $version against its release tarball"
  exit 0
fi

rm -rf "$root/plugins/$plugin"
mv "$tmp/$plugin" "$root/plugins/$plugin"
# -f: payload files can be self-ignored (a plugin may ship a .gitignore listing itself).
git -C "$root" add -f "plugins/$plugin"
echo "vendored $plugin $(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$root/plugins/$plugin/.claude-plugin/plugin.json") from $ref"
