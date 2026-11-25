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
./vendor.sh --verify fixture
printf 'tampered\n' > plugins/fixture/example
commit_payload
if output="$(./vendor.sh --verify fixture 2>&1)"; then
  echo "tampered plugin passed verification" >&2
  exit 1
fi
[[ "$output" == "vendored file differs from release: 'plugins/fixture/example'" ]]
echo "$output"
