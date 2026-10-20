#!/usr/bin/env bash
# release.sh — cut a versioned kilo-mms release.
#
# Usage:
#   ./release.sh --build-only            # build dist/kilo-mms-<version>.tar.gz only
#   ./release.sh patch|minor|major|X.Y.Z # bump, commit, tag, push, gh release
#
# P2 preconditions: clean worktree, on main, HEAD == origin/main, gh on PATH,
# tag v<next> does not exist. The tarball contains exactly the consumer
# payload (install.sh, plugin.json, .kilo/{agents,skills,kilo.json,.gitignore})
# under a kilo-mms/ prefix. Workshop, plans, and .kilo/run/ are never shipped.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
cd "$root"

[ -f plugin.json ] || { echo "no plugin.json in $root" >&2; exit 66; }

# shortcut: sed-based JSON version read/write, upgrade to jq if plugin.json
# grows free-form string fields containing colons adjacent to "version".
current="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' plugin.json)"
printf '%s' "$current" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$' || {
  echo "no semver version in plugin.json" >&2; exit 65; }

# R-N1: payload membership, one place. Every path must exist AND be tracked
# (staging below copies tracked files only); fail loudly listing all missing
# or untracked paths before any mutation. This is what enforces the AGENTS.md
# "git add -f .kilo/.gitignore" remedy: an untracked payload file fails here
# instead of being silently omitted from the tarball.
payload_paths="install.sh plugin.json .kilo/agents .kilo/skills .kilo/kilo.json .kilo/.gitignore"
precheck_payload() {
  local missing="" untracked="" p
  for p in $payload_paths; do
    [ -e "$p" ] || missing="$missing $p"
  done
  for p in $payload_paths; do
    [ -e "$p" ] || continue
    if [ -f "$p" ]; then
      git ls-files --error-unmatch "$p" >/dev/null 2>&1 || untracked="$untracked $p"
    elif [ -d "$p" ]; then
      [ -z "$(git ls-files -- "$p")" ] && untracked="$untracked $p"
    fi
  done
  if [ -n "$missing$untracked" ]; then
    [ -n "$missing" ] && echo "payload paths missing:$missing" >&2
    [ -n "$untracked" ] && echo "payload paths untracked (run: git add -f <path>):$untracked" >&2
    exit 66
  fi
}

# B2 portability: no GNU-only flags. Stage tracked payload files under
# kilo-mms/ in a tmp dir (exact membership by construction), tar with -C.
# bsdtar-safe. E4: trap removes the stage dir on any exit (set -e included).
build_tarball() {
  local version="$1" tarball stage f
  mkdir -p dist
  tarball="dist/kilo-mms-$version.tar.gz"
  rm -f "$tarball"
  stage="$(mktemp -d)" || exit 1
  trap 'rm -rf "$stage" plugin.json.tmp' EXIT
  git ls-files -- $payload_paths | while IFS= read -r f; do
    mkdir -p "$stage/kilo-mms/$(dirname "$f")"
    cp "$f" "$stage/kilo-mms/$f"
  done
  tar -czf "$tarball" -C "$stage" kilo-mms
  rm -rf "$stage"
  trap - EXIT
  echo "built $tarball"
}

if [ "${1:-}" = "--build-only" ]; then
  # --build-only also enforces the tracked-payload precheck: a tarball built
  # from a dirty clone that silently omitted .kilo/.gitignore wasted a pilot
  # cycle once already (d1).
  precheck_payload
  build_tarball "$current"
  exit 0
fi

# --- P2 precondition: gh -----------------------------------------------------
# E5: gh presence is not gh auth. Check before any release state exists so a
# failed release never leaves a pushed tag without its GitHub release.
command -v gh >/dev/null || { echo "gh CLI required for release upload" >&2; exit 69; }
gh auth status >/dev/null 2>&1 || {
  echo "gh not authenticated (run: gh auth login)" >&2; exit 69; }

bump="${1:?usage: release.sh --build-only | patch|minor|major|<version>}"

# --- P2 preconditions: git state ----------------------------------------------
[ -z "$(git status --porcelain)" ] || { echo "worktree not clean" >&2; exit 65; }
branch="$(git branch --show-current)"
[ "$branch" = "main" ] || { echo "must be on main (currently $branch)" >&2; exit 65; }
# n1: fetch tags too, so the tag-exists check sees remote tags.
git fetch origin main --tags --quiet
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || {
  echo "main not in sync with origin/main" >&2; exit 65; }

IFS=. read -r major minor patch <<< "$current"
case "$bump" in
  patch) next="$major.$minor.$((patch + 1))" ;;
  minor) next="$major.$((minor + 1)).0" ;;
  major) next="$((major + 1)).0.0" ;;
  *)
    # n4: explicit if, not an && || chain.
    if printf '%s' "$bump" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
      next="$bump"
      # E6: explicit versions must strictly increase; equal/lower would make
      # the sed bump a no-op (commit then fails "nothing to commit") or
      # publish an out-of-order release.
      IFS=. read -r nmajor nminor npatch <<< "$next"
      if [ "$nmajor" -lt "$major" ] || \
         { [ "$nmajor" -eq "$major" ] && [ "$nminor" -lt "$minor" ]; } || \
         { [ "$nmajor" -eq "$major" ] && [ "$nminor" -eq "$minor" ] && [ "$npatch" -le "$patch" ]; }; then
        echo "explicit version $next must be greater than current $current (or use patch|minor|major)" >&2
        exit 64
      fi
    else
      echo "bad version: $bump" >&2; exit 64
    fi
    ;;
esac

if git rev-parse -q --verify "refs/tags/v$next" >/dev/null; then
  echo "tag v$next already exists" >&2; exit 65
fi

echo "releasing $current -> $next"

# --- preflight, then bump + build --------------------------------------------
# E4: validate the payload before plugin.json is touched, so a missing or
# untracked payload path fails before any mutation exists to clean up.
precheck_payload

# B2 portability: BSD sed has no bare -i; write-then-move instead.
sed "s/\"version\":[[:space:]]*\"$current\"/\"version\": \"$next\"/" plugin.json > plugin.json.tmp
mv plugin.json.tmp plugin.json
build_tarball "$next"

# --- commit, tag, push, release ----------------------------------------------
# gh release create with an ANNOTATED tag requires the tag on the remote
# first (gh docs: "first create one locally with git, push the tag to GitHub,
# then run this command"). Failure modes are safe at every step: commit/tag
# local until push; if gh fails after push, the tag exists and the operator
# reruns the one gh command printed below.
tarball="dist/kilo-mms-$next.tar.gz"
git add plugin.json
git commit -m "Release kilo-mms $next"
git tag -a "v$next" -m "kilo-mms $next"
git push origin main --follow-tags

if ! gh release create "v$next" "$tarball" \
  --title "kilo-mms $next" \
  --notes "Install: download and unpack this tarball, then run ./install.sh (--global installs to ~/.config/kilo; --project installs into the current repo's .kilo/). See AGENTS.md for details."; then
  echo "gh release create failed after tag v$next was pushed. Recover with:" >&2
  echo "  gh release create v$next $tarball --title 'kilo-mms $next'" >&2
  exit 1
fi

echo "released v$next with $tarball"
