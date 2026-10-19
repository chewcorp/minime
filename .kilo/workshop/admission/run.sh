#!/usr/bin/env bash
# Admission-runner tracer bullet.
#
#   run.sh [--results <file>] [--gate-skill <s>] <case-dir> <skill>
#
# Runs every check in <case-dir>/checks.json against <case_dir>/target.txt and
# appends one JSONL record per SCHEMA.md. Baseline arm is skill="baseline".
# Deterministic: verdicts are grep results, not model judgement.
#
# --gate-skill decouples check selection from the recorded skill label: checks
# gate on <gate-skill> (default: <skill>), while the JSONL row records <skill>.
# Ablation uses this so "converge-no-x" arms still run converge's checks.
#
# Exit codes: 0 pass, 1 fail, 2 unproven (no applicable checks), 3+ runner
# error (missing files, malformed checks, grep/jq/IO error). Verdicts never
# share a code with infrastructure errors, so callers can tell "the artifact
# failed" from "the run was invalid". The contract is enforced structurally:
# verdict codes are reachable only from the final case statement (guarded by
# VERDICT_OK); every other exit is remapped to 3 by the EXIT trap, so an
# unguarded failure (set -e on mkdir, >>, jq, date, ...) can never leak an
# infrastructure error onto a verdict code.
#
# shortcut: tokens recorded as -1 until a real metering source exists;
# upgrade when the runner gains access to runtime token counts.
# Requires GNU grep with -P (PCRE); Linux workshop only.
set -euo pipefail

# Structural contract guard: any exit path that did not pass through the final
# verdict case (which sets VERDICT_OK first) leaves with 3, never 0/1/2.
VERDICT_OK=
trap 'rc=$?; if [ -z "$VERDICT_OK" ] && { [ "$rc" -eq 0 ] || [ "$rc" -eq 1 ] || [ "$rc" -eq 2 ]; }; then exit 3; else exit "$rc"; fi' EXIT

usage() { echo "usage: run.sh [--results <file>] [--gate-skill <s>] <case-dir> <skill>" >&2; exit 3; }

results_file="$(dirname "${BASH_SOURCE[0]}")/results.jsonl"
gate_skill=
pos=()
while [ $# -gt 0 ]; do
  case "$1" in
    --results)    results_file=${2:?"--results needs a value"}; shift 2 ;;
    --gate-skill) gate_skill=${2:?"--gate-skill needs a value"}; shift 2 ;;
    -*)           echo "unknown flag: $1" >&2; usage ;;
    *)            pos+=("$1"); shift ;;
  esac
done
[ "${#pos[@]}" -eq 2 ] || usage
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

start_ms=$(date +%s%3N)

# Validation phase, complete before any verdict is produced: every applicable
# check must be an object with a string `pattern` and an `expect` of exactly
# "pass" or "fail". A malformed case is a runner error (exit 3), never an
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
    ) | .key)
  | join(", ")
' "$checks") || { echo "checks.json unreadable: $checks" >&2; exit 3; }
if [ -n "$invalid" ]; then
  echo "malformed checks (need object with string pattern and expect: pass|fail): $invalid in $checks" >&2
  exit 3
fi

applicable=$(jq --arg gate "$gate_skill" '
  if (has("skill")) then
    if .skill == $gate then del(.skill) else {} end
  else . end
' "$checks")

verdicts='{}'
overall=pass
while IFS= read -r name; do
  expect=$(jq -r --arg n "$name" '.[$n].expect' <<<"$applicable")
  pattern=$(jq -r --arg n "$name" '.[$n].pattern' <<<"$applicable")
  # grep exit codes: 0 match, 1 no match, 2 error (bad PCRE, unreadable file).
  # An error must propagate as a runner error, never collapse into "not found"
  # (an expect:pass check would otherwise pass on a pattern that never ran).
  if grep -qiP -e "$pattern" "$target"; then
    found=true
  else
    grep_status=$?
    if [ "$grep_status" -ne 1 ]; then
      echo "grep error (status $grep_status) for check '$name' pattern '$pattern'" >&2
      exit 3
    fi
    found=false
  fi
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

wall_ms=$(( $(date +%s%3N) - start_ms ))

# Canonical task key: repo-relative path without trailing slash, so arms of the
# same case group correctly no matter where the runner is invoked from.
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
task_key=${case_dir#"$repo_root"/}
task_key=${task_key%/}

# Unique evidence per run: result lines are append-only, so each must point at
# its own proof file instead of overwriting a shared one. shortcut: proof files
# live under /tmp (ephemeral, workshop-local); move into the repo if durable
# evidence is ever required by an external gate.
# Write order: proof first, results append second. Proof-file failures exit via
# the trap (3+); an append failure removes the orphan proof before exiting.
run_id=$(date +%s%N)-$$
evidence=/tmp/kilo-workshop-proof/$(basename "$case_dir")-$skill-$run_id-proof.txt
mkdir -p "$(dirname "$evidence")"
{
  echo "case:    $task_key"
  echo "skill:   $skill"
  echo "gate-skill: $gate_skill"
  echo "verdict: $overall"
  echo "checks:"
  jq -r 'to_entries[] | "  \(.key): \(.value)"' <<<"$verdicts"
  if [ "$gate_skill" = "$skill" ]; then
    echo "rerun:   .kilo/workshop/admission/run.sh $task_key $skill"
  else
    echo "rerun:   .kilo/workshop/admission/run.sh --gate-skill $gate_skill $task_key $skill"
  fi
} > "$evidence"

if ! jq -n -c \
  --arg task "$task_key" \
  --arg skill "$skill" \
  --argjson tokens -1 \
  --argjson wall_ms "$wall_ms" \
  --arg verdict "$overall" \
  --argjson verdicts "$verdicts" \
  --arg evidence "$evidence" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{task:$task, skill:$skill, tokens:$tokens, wall_ms:$wall_ms, verdict:$verdict, verdicts:$verdicts, evidence:$evidence, ts:$ts}' \
  >> "$results_file"; then
  rm -f "$evidence"
  echo "could not append results to $results_file" >&2
  exit 3
fi

echo "$overall  $task_key  skill=$skill  wall=${wall_ms}ms  evidence=$evidence"
VERDICT_OK=1
case "$overall" in
  pass) exit 0 ;;
  unproven) exit 2 ;;
  *) exit 1 ;;
esac
