#!/usr/bin/env bash
set -euo pipefail
source_dir="$(cd "$(dirname "$0")/.." && pwd)"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
cd "$scratch"
git init -q
cp "$source_dir/vendor.sh" .
mkdir -p plugins/fixture/.claude-plugin
printf '{"version":"1.2.3"}\n' > plugins/fixture/.claude-plugin/plugin.json
printf 'released\n' > plugins/fixture/example
ln -s example plugins/fixture/link
tar -czf minime-fixture-1.2.3.tar.gz -C plugins fixture

gh() {
  [[ "$*" == "release download v1.2.3 --repo chewcorp/minime-fixture --pattern minime-fixture-1.2.3.tar.gz --dir "* ]]
  cp minime-fixture-1.2.3.tar.gz "${@: -1}"
}
export -f gh

commit_payload() {
  git add -f plugins/fixture
  git -c user.name=Test -c user.email=test@example.com commit -qm fixture
}

commit_payload
baseline="$(git rev-parse HEAD)"
./vendor.sh --verify fixture

assert_rejected() {
  local expected="$1" output
  shift
  if output="$(./vendor.sh --verify fixture "$@" 2>&1)"; then
    echo "tampered plugin passed verification" >&2
    exit 1
  fi
  [[ "$output" == "$expected" ]]
  echo "$output"
}

expect_rejection() {
  commit_payload
  assert_rejected "$1"
  git switch -q --detach "$baseline"
}

printf 'tampered\n' > plugins/fixture/example
commit_payload
tampered="$(git rev-parse HEAD)"
assert_rejected "vendored file differs from release: 'plugins/fixture/example'"
./vendor.sh --verify fixture "$baseline"
git switch -q --detach "$baseline"
assert_rejected "vendored file differs from release: 'plugins/fixture/example'" "$tampered"
echo "Explicit verification uses the selected commit, not HEAD"

printf 'extra\n' > plugins/fixture/extra
expect_rejection "vendored file differs from release: 'plugins/fixture/extra'"
rm plugins/fixture/example
expect_rejection "vendored file missing from commit: 'plugins/fixture/example'"
chmod +x plugins/fixture/example
expect_rejection "vendored file differs from release: 'plugins/fixture/example'"
ln -snf .claude-plugin/plugin.json plugins/fixture/link
expect_rejection "vendored file differs from release: 'plugins/fixture/link'"
