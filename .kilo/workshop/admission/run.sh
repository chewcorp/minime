#!/usr/bin/env bash
# Admission runner.
#
#   run.sh [--results <file>] [--gate-skill <s>] --model <m> --provider <p> [--component <c>] <case-dir> <skill>
#
# Runs each check in <case-dir>/checks.json against <case_dir>/target.txt
# and appends one JSONL record per SCHEMA.md. Verdicts are deterministic
# (Python regex), never model judgement.
#
# --gate-skill decouples check selection from the recorded skill label so
# ablation arms ("converge-no-x") can still run converge's checks.
#
# --model/--provider/--component stamp the identity SCHEMA.md requires.
# --component defaults to "full". Missing --model or --provider is a runner
# error: pooled rows break per-model comparisons silently.
#
# Exit codes: 0 pass, 1 fail, 2 unproven (no applicable checks), 3+ runner
# error. 0/1/2 are reachable only from the guarded final exit; anything
# else is remapped to 3 by the EXIT trap.
set -euo pipefail

# Structural contract guard: any exit path that did not pass through the
# final verdict case (which sets VERDICT_OK first) leaves with 3, never 0/1/2.
VERDICT_OK=
trap 'rc=$?; if [ -z "$VERDICT_OK" ] && { [ "$rc" -eq 0 ] || [ "$rc" -eq 1 ] || [ "$rc" -eq 2 ]; }; then exit 3; else exit "$rc"; fi' EXIT

usage() { echo "usage: run.sh [--results <file>] [--gate-skill <s>] --model <m> --provider <p> [--component <c>] <case-dir> <skill>" >&2; exit 3; }

results_file="$(dirname "${BASH_SOURCE[0]}")/results.jsonl"
gate_skill=
model=
provider=
component=full
pos=()
while [ $# -gt 0 ]; do
  case "$1" in
    --results)    results_file=${2:?"--results needs a value"}; shift 2 ;;
    --gate-skill) gate_skill=${2:?"--gate-skill needs a value"}; shift 2 ;;
    --model)      model=${2:?"--model needs a value"}; shift 2 ;;
    --provider)   provider=${2:?"--provider needs a value"}; shift 2 ;;
    --component)  component=${2:?"--component needs a value"}; shift 2 ;;
    -*)           echo "unknown flag: $1" >&2; usage ;;
    *)            pos+=("$1"); shift ;;
  esac
done
[ "${#pos[@]}" -eq 2 ] || usage
[ -n "$model" ] && [ -n "$provider" ] || { echo "--model and --provider are required (SCHEMA: no pooled rows)" >&2; usage; }
case_dir=${pos[0]}
skill=${pos[1]}
gate_skill=${gate_skill:-$skill}

# Normalize to an absolute path at the input boundary so every derived identity
# (task_key, evidence name) is stable across caller cwds and path spellings.
case_dir=$(cd "$case_dir" 2>/dev/null && pwd) \
  || { echo "case dir not found: ${pos[0]}" >&2; exit 3; }

target="$case_dir/target.txt"
checks="$case_dir/checks.json"
[ -f "$target" ] && [ -f "$checks" ] || { echo "missing target/checks in $case_dir" >&2; exit 3; }

start_ms=$(python3 -c 'import time; print(time.monotonic_ns() // 1_000_000)')

# Validation phase, complete before any verdict is produced: every applicable
# check must have a string pattern, expect: pass|fail and optional line/document
# scope. A malformed case is a runner error (exit 3), never an
# artifact failure (exit 1) and never silently dropped into a vacuous pass.
invalid=$(jq -r --arg gate "$gate_skill" '
  (if (has("skill")) then
     if .skill == $gate then del(.skill) else {} end
   else . end)
  | to_entries
  | map(select(
      (.value | type) != "object"
       or (.value.pattern | type) != "string"
       or ((.value.expect | IN("pass", "fail")) | not)
       or ((.value | has("scope")) and ((.value.scope | IN("line", "document")) | not))
    ) | .key)
  | join(", ")
' "$checks") || { echo "checks.json unreadable: $checks" >&2; exit 3; }
if [ -n "$invalid" ]; then
  echo "malformed checks (need string pattern, expect: pass|fail, optional scope: line|document): $invalid in $checks" >&2
  exit 3
fi

applicable=$(jq --arg gate "$gate_skill" '
  if (has("skill")) then
    if .skill == $gate then del(.skill) else {} end
  else . end
' "$checks")

# Compile every applicable regex before matching; invalid scopes/patterns never
# produce verdict rows or evidence. The helper only reads data, never runs it.
matches=$(python3 "$(dirname "${BASH_SOURCE[0]}")/match.py" "$target" <<<"$applicable") \
  || { echo "regex validation/matching failed: $checks" >&2; exit 3; }

verdicts='{}'
overall=pass
while IFS= read -r name; do
  expect=$(jq -r --arg n "$name" '.[$n].expect' <<<"$applicable")
  found=$(jq -r --arg n "$name" '.[$n]' <<<"$matches")
  if { [ "$expect" = "fail" ] && $found; } || { [ "$expect" = "pass" ] && ! $found; }; then
    verdict=pass
  else
    verdict=fail
    overall=fail
  fi
  verdicts=$(jq --arg n "$name" --arg v "$verdict" '. + {($n): $v}' <<<"$verdicts")
done < <(jq -r 'keys[]' <<<"$applicable")

# Vacuous pass is forbidden (SCHEMA.md): every check gated out for this arm means
# nothing was verified, so the result is unproven, not pass.
if [ "$verdicts" = '{}' ]; then overall=unproven; fi

wall_ms=$(( $(python3 -c 'import time; print(time.monotonic_ns() // 1_000_000)') - start_ms ))

# Canonical task key: repo-relative path without trailing slash, so arms of the
# same case group correctly no matter where the runner is invoked from.
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
task_key=${case_dir#"$repo_root"/}
task_key=${task_key%/}

# Proof artifacts are unique-per-run and append-only; a failed append
# removes the orphan proof before exit.
run_id=$(python3 -c 'import uuid; print(uuid.uuid4().hex)')
evidence=/tmp/kilo-workshop-proof/$(basename "$case_dir")-$skill-$run_id-proof.txt
mkdir -p "$(dirname "$evidence")"
{
  echo "case:    $task_key"
  echo "skill:   $skill"
  echo "gate-skill: $gate_skill"
  echo "model:   $model ($provider)"
  echo "component: $component"
  echo "verdict: $overall"
  echo "checks:"
  jq -r 'to_entries[] | "  \(.key): \(.value)"' <<<"$verdicts"
  if [ "$gate_skill" = "$skill" ]; then
    echo "rerun:   .kilo/workshop/admission/run.sh --model $model --provider $provider --component $component $task_key $skill"
  else
    echo "rerun:   .kilo/workshop/admission/run.sh --gate-skill $gate_skill --model $model --provider $provider --component $component $task_key $skill"
  fi
} > "$evidence"

if ! jq -n -c \
  --arg task "$task_key" \
  --arg skill "$skill" \
  --arg model "$model" \
  --arg provider "$provider" \
  --arg component "$component" \
  --argjson tokens -1 \
  --argjson wall_ms "$wall_ms" \
  --arg verdict "$overall" \
  --argjson verdicts "$verdicts" \
  --arg evidence "$evidence" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{task:$task, skill:$skill, model:$model, provider:$provider, component:$component, tokens:$tokens, wall_ms:$wall_ms, verdict:$verdict, verdicts:$verdicts, evidence:$evidence, ts:$ts}' \
  >> "$results_file"; then
  rm -f "$evidence"
  echo "could not append results to $results_file" >&2
  exit 3
fi

echo "$overall  $task_key  skill=$skill  model=$model  wall=${wall_ms}ms  evidence=$evidence"
VERDICT_OK=1
case "$overall" in
  pass) exit 0 ;;
  unproven) exit 2 ;;
  *) exit 1 ;;
esac
