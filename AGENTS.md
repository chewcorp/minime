# kilo-mms

Local development workflows for this repo, in the shape of rgh-mms (planner, researcher, implementor, reviewer) without the harness machinery.

## Kilo agents

`.kilo/agents/` holds thin shims: `planner`, `researcher` (read-only), `implementor`, `reviewer` (read-only), `approver` (read-only, AC table), `advisor` (read-only, escalation brief).

`.kilo/skills/` holds the delivery loop, routed by `deliver`: `clarify` → `chart` → `build` → `prove` → `converge` → `land-learn`. `.kilo/workshop/` is plugin-dev only, never installed downstream.

Role models are configured in `.kilo/kilo.json` using Kilo's native `agent.<role>.model` settings, including direct agent invocations outside `deliver`. Planner and advisor default to paid `kilo-auto/frontier` for deeper reasoning and require Kilo Gateway access and credits. Other roles have no model override. To use a different provider or tier, edit those settings (for example, `kilo-auto/efficient`); to restore normal subagent inheritance, remove the role's `model` key rather than setting it to `auto` or `inherit-parent`.

## Install and release

The consumer payload is defined by `plugin.json`: `.kilo/agents/`, `.kilo/skills/`, `.kilo/kilo.json`, `.kilo/.gitignore`. Workshop, plans, and `.kilo/run/` are development-only or runtime state and are never installed.

- Install to your account (all repos): `./install.sh` or `./install.sh --global` → `~/.config/kilo/`.
- Install to one repo: from the target repo's root, run `<path-to-this-repo-or-tarball>/install.sh --project` — it reads the payload from where the script lives and installs into the repo containing your CWD (adds a `.kilo/run/` rule to the repo-root `.gitignore`, idempotently).
- Install anywhere else: `./install.sh --prefix DIR` (advanced; DIR gets the kilo config-dir layout).
- An existing `kilo.json` at the target is preserved byte-for-byte unless `--force-config` is passed. The bundled config pins planner/advisor to paid `kilo-auto/frontier` (Kilo Gateway credits required — remove the `model` keys to inherit instead).

Versioning: semver lives in `plugin.json`; releases are git tags `v<version>` plus GitHub release tarballs. Cut one from a clean, synced `main` with `./release.sh patch|minor|major` (or an explicit `./release.sh X.Y.Z`, which must be greater than the current version) — it validates the payload, bumps `plugin.json`, commits, creates annotated tag `v<version>`, builds `dist/kilo-mms-<version>.tar.gz` (payload + installer only, tracked files only), pushes the commit and tag, then creates the GitHub release via `gh` (push before release because `gh release create` requires an annotated tag to exist on the remote; if the `gh` call fails after the push, the tag is published without a release — rerun the single `gh release create` command the error message prints). Build the tarball without cutting a release via `./release.sh --build-only`. Note: `.kilo/.gitignore` is payload but self-ignored by its own contents — if it was never committed, run `git add -f .kilo/.gitignore` once so release tarballs built from clean clones include it (the release precheck fails loudly if any payload path is untracked).

## Dev-loop conventions

- Sync to `origin/main` then cut a fresh branch or worktree for every task. Work stays isolated until merge; no direct commits to `main`.
- Small diffs. One concern per change.
- Run the relevant tests before handing off.
- Planner and researcher never write code or mutate state.
- Reviewer findings are either blocking or advisory; say which.
- Act in the same turn you announce work. Never end a turn on a promise to do something; do it, then report.
- Best-effort protection by elimination, not enumeration: deny dangerous capability at the tool boundary; never glob-filter dangerous flags.
