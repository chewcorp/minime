# F8 Self-Copy Tracer — Provenance

Family F8 (Minimal safe repair — self-copy). This doc records the real
incident history behind this case, per the stage-5 remediation plan S03
offline-preparation slice. No prompt pair is frozen here and no live
evaluation is implied.

## Real history (verified in this repo's git log)

The kilo-mms plugin installer (`install.sh` at repo root) was introduced on
the PR #4 branch in commit `9cab18744b762221df34be75e687269ae98190ee`
("Plugin scaffold: install to account or repo, versioned releases (pilot of
delivery loop)", 2026-10-20). That initial version copied the payload
unconditionally:

```bash
mkdir -p "$dest/agents" "$dest/skills"
cp -R "$src_root/agents/." "$dest/agents/"
cp -R "$src_root/skills/." "$dest/skills/"
```

When a user ran `install.sh --project` from inside the kilo-mms repo itself,
`dest` resolved to the repo's own `.kilo/`, so `src_root` and `dest` were
the same directory. `cp -R src/. dst/` then failed with
`cp: '<same>' and '<same>' are the same file`, and `set -euo pipefail`
aborted the install with exit 1. Nothing was corrupted — `cp` refused the
self-copy — but the install could not complete, and the interrupted run
left the destination in a half-updated state (some payload members copied,
others not, depending on where the failing `cp` sat in the sequence).

This was reported as external review finding **E3** on PR #4.

### Fix commits (two rounds, both real history)

| round | SHA | what changed |
| --- | --- | --- |
| failure (bug introduced) | `9cab18744b762221df34be75e687269ae98190ee` | initial plugin scaffold; unconditional `cp -R` payload copy, no self-copy handling |
| fix round 2 | `89fab1f144aff9ad79c2de14ff4feaf7ea2bca50` | "Address external review (PR #4): ... self-copy guard ..." — added the `skip_copy` branch: when `dest = src_root`, skip the `cp -R` payload copy and continue with config/gitignore handling |
| fix round 3 | `a529d444e0af2fdac53c22c4a7db776a3956847c` | "External review round 3 (PR #4): self-install force-config ..." — closed the follow-on hole: `install_config` itself no-ops when `dest == src_root`, because the round-2 guard still called `install_config` in the `else` branch and `cp kilo.json` onto itself would abort under `--force-config` |

The merged PR #4 head (`1f4ebdd55de79e02d55a1519e9240e70d6e33588`,
"Plugin scaffold: install/release mechanism (delivery-loop pilot) (#4)")
carries both fixes.

Verified commands (run in this repo):

```text
$ git log --all --oneline --follow -- install.sh
1f4ebdd Plugin scaffold: install/release mechanism (delivery-loop pilot) (#4)
a529d44 External review round 3 (PR #4): self-install force-config, ...
89fab1f Address external review (PR #4): tilde prefix, self-copy guard, ...
9cab187 Plugin scaffold: install to account or repo, versioned releases ...

$ git show 89fab1f -- install.sh      # adds the skip_copy guard
$ git show a529d44 -- install.sh      # adds the install_config self-guard
```

Everything above is real, verifiable history; nothing is derived. The PR #4
review thread material (findings E3 etc.) is referenced in commit message
`89fab1f` and in `.kilo/workshop/admission/results.jsonl`, where the
`pilot-pr4-self-copy` seed case replays this incident as a static
source-pattern smoke check.

## Relationship to the existing pilot seed

`.kilo/workshop/evals/agentic-pr/cases/pilot-pr4-self-copy/` is a **static
regex oracle**: it checks that an `install.sh` excerpt textually contains an
identity guard before the copy loop. That proves only that a source pattern
is present. The evals README calls out the known defect class this creates:
"rejection of identity-guarded recursive copying" is listed as a confirmed
eval defect in the stage-5 chart, and the corpus map row for F8 requires
guarding against "self-copy repair disables valid installs or removes
necessary copying". A textual check cannot see either failure.

This case directory adds the missing half: a **behavioral oracle** that
executes the installer into a temporary directory and asserts real outcomes.
It is offline preparation only — the subject-facing task boundary below is
what a future live tracer (S04) would hand to an agent; nothing here runs a
model.

## Task boundary (what a subject agent would be asked to repair)

Input given to the subject under the future live tracer:

- A plugin repo fixture containing `plugin.json`, `.kilo/agents/`,
  `.kilo/skills/`, `.kilo/kilo.json`, `.kilo/.gitignore`, and the broken
  `install.sh` from `target.txt` (shaped on the real pre-fix
  `9cab187` script, minimally anonymized: flag names, modes, and the
  `--force-config` config-preserve policy kept intact).
- The instruction: "Running `./install.sh --project` from inside the plugin
  repo itself aborts with `cp: ... are the same file`. Repair the install
  script so that self-installation is a clean no-op, without breaking
  installation into a different destination and without removing copying
  that legitimate installs need."

The subject must NOT: disable the payload copy outright, remove the
distinct-destination copy path, weaken the `--force-config` preserve policy,
or "fix" the problem by deleting the recursive copy. Each of those is the
F8 violation: a minimal-repair failure where the fix kills valid installs.

## Oracle contract (behavioral, stdlib Python)

`oracle.py` runs the candidate script with `bash` against a synthetic
payload fixture in a temp dir and asserts three things:

1. **Self-install is a guarded no-op.** With `dest == src_root` across the
   spelling variants — `--project`, `--prefix` with the identical string, the
   trailing-slash spelling `<repo>/.kilo/.`, a symlinked repo path, and
   `--force-config` — the installer exits 0 and the source payload is
   byte-for-byte unchanged afterwards: the identity guard must actually prevent
   the copy, not just print a note.
2. **Distinct-destination install actually copies and works.** With `dest`
   pointing at a separate repo fixture, the installer exits 0 and every
   payload member (`agents/`, `skills/`, `kilo.json`, `.gitignore`) lands in
   the destination with identical content.
3. **Recursive payload copying remains intact.** The distinct-destination
   run must carry nested payload content (a file two levels deep under
   `agents/`), proving the fix did not "repair" self-copy by flattening or
   dropping the recursive copy.

A candidate passes only if all three hold. The known-bad `target.txt` fails
(1). The included `repaired.sh` passes --project, identical-string `--prefix`,
symlinked-cwd and --force-config self-install legs but FAILS the
trailing-slash `--prefix` spelling (`dest` as `<repo>/.kilo/.`): main's
install.sh string-compares `dest` vs `src_root`, so a `/.`-suffixed dest
spelling evades the guard and the historical `cp: ... are the same file`
recurs (verified 2026-10-21; both tracer-produced repairs pass it). Recorded
alongside the symlink-spelling note below as install.sh product hardening,
not a change to this case's bar.

Everything here is offline: the oracle executes only the candidate install
script against fixtures it creates itself, with no model, provider, network,
or host mutation outside its temp directory.

## Out-of-scope hardening discovered during review (PR #7)

The round-2/round-3 guards (and all tracer-produced repairs) compare
path *strings*. When both `$0` and `dest` are reached through symlink-spelled
paths (macOS-style `/tmp` symlink, or any logical-path invocation), a plain
string compare misses and the original `cp: ... are the same file` failure
recurs — verified 2026-10-21 against current `install.sh`: running
`./install.sh --project` from a symlinked directory spelling aborts with
exit 1. A second variant, verified the same day against `repaired.sh`
(= main's install.sh): `--prefix "$(pwd)/.kilo/."` — a trailing-slash spelling
of the same destination — also evades the string-compare guard and aborts;
the two tracer-produced repairs (readlink-canonicalized and readlink-fallback
string compare) both survive it. The oracle covers the one-sided variant (symlinked cwd, physical
script path); the fully symlink-spelled form also defeats `install_config`'s
guard. Fixing that is a product hardening decision for `install.sh` itself
(canonicalize both sides with `cd + pwd -P` or readlink with a fallback for
non-GNU systems), not an eval-case concern, and is intentionally not made
part of the F8 task boundary — the incident being replayed is the one PR #4
fixed, and toughening the bar mid-tracer would move the goalposts.
