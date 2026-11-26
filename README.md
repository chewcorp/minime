# minime
A me flavoured development workflow

minime is a family of agent plugins, published as one marketplace that works across agent clients. Each plugin is developed and versioned in its own repo (`chewcorp/minime-<plugin>`) and vendored here on release under `plugins/<plugin>/`.

| Plugin | What it does |
|---|---|
| [`coder`](plugins/coder/) | Staged delivery loop: clarify, chart, build, prove, converge, land-learn, routed by `deliver`, with planner, researcher, implementor, reviewer, approver and advisor subagents. Source: [chewcorp/minime-coder](https://github.com/chewcorp/minime-coder). |
| [`agents`](plugins/agents/) | Recruit and onboard an agent like a new colleague: brief, role, routines, a TLC-checked chart for every wake, and a trial that shows each safeguard fires, routed by `recruit`, with a reviewer subagent. Source: [chewcorp/minime-agents](https://github.com/chewcorp/minime-agents). |

## Install

| Client | Install | Gets |
|---|---|---|
| Claude Code | `/plugin marketplace add chewcorp/minime` then `/plugin install coder@minime` | skills, agents |
| Codex | `codex plugin marketplace add chewcorp/minime` then `codex plugin add coder@minime` | skills |
| GitHub Copilot CLI | `copilot plugin marketplace add chewcorp/minime` then `copilot plugin install coder@minime` | skills; agents untested |
| Cursor | Add `chewcorp/minime` as a team marketplace, then install `coder` | skills, agents |
| Factory Droid | `droid plugin marketplace add https://github.com/chewcorp/minime` then `droid plugin install coder@minime` | skills, droids |
| Grok Build | Add `chewcorp/minime` as a marketplace source, then install `coder` from `/marketplace` | skills, agents |
| Devin | `devin plugins install chewcorp/minime#plugins/coder` | skills, agents (CLI and Desktop only) |
| pi | `pi install git:github.com/chewcorp/minime` | skills |
| opencode | `git clone https://github.com/chewcorp/minime && minime/install.sh` (`--project` for one repo; name plugins to install only some) | skills, agents |
| Manual install | Copy the complete [coder skill directories](plugins/coder/skills/), preserving scripts and references. To run `deliver`, register the [coder agent definitions](plugins/coder/agents/) using the client's subagent setup. The client must support named subagents and be able to run Git and Python 3.9+. | skills, agents if configured |

For `agents`, swap `coder` for `agents` in the plugin rows (for example `/plugin install agents@minime`, or `devin plugins install chewcorp/minime#plugins/agents`). pi and `install.sh` install every plugin.

Installs are verified with Claude Code, Codex, Copilot CLI, pi and opencode. The other rows follow each client's documented plugin format and haven't been tried yet.

Start the coder loop by asking for it by name, or run `/deliver` (`/coder:deliver` in Claude Code). Start agents with `/recruit` (`/agents:recruit`).

### Clean up after a coder-only OpenCode upgrade

If you upgraded a coder-only install from v0.2.3 or earlier, the old
`skills/goldfish-review/` may still sit beside `skills/coder-goldfish-review/`.
Check the old directory's `SKILL.md` in your install location. Remove that
directory only if the skill calls `reviewer` (the old coder copy). If it calls
`agent-review`, keep it: that copy belongs to recruitment. If you want both
plugins, you can instead reinstall `agents` and `coder` in the same location
to restore recruitment's copy and install coder under its new name.

## Layout

- `.claude-plugin/marketplace.json` is the catalog read by Claude Code, Codex, Copilot CLI and Factory Droid. `.cursor-plugin/marketplace.json` (Cursor) and `.grok-plugin/marketplace.json` (Grok Build) carry the same entries; keep the three in step when adding a plugin.
- `package.json` lists each plugin's skills for pi.
- `install.sh` copies plugin skills and agents into opencode, which has no marketplace.
- `plugins/<plugin>/` is a vendored release. Don't edit it here; change the plugin repo, release, then vendor.

## Vendoring a release

```bash
./vendor.sh coder v0.2.0                                 # from the minime-coder GitHub release
./vendor.sh coder ../minime-coder/dist/minime-coder-0.2.0.tar.gz   # from a local ./release.sh --build-only
```

Commit the result with the tag in the message and open a PR.

`coder` and `agents` are vendored automatically: their release workflows run `./vendor.sh` and open a marketplace PR. [`REVIEW.md`](REVIEW.md) tells Devin Review to skip vendored files and keep reviewing the marketplace's own files. The `.gitattributes` marker remains for review tools that honor it.

The release workflows publish the exact tarball under the marketplace release tag `<plugin>-v<version>` before opening or updating the PR. **Verify vendored plugins** runs trusted code from `main` and compares the PR's committed payload with that public asset. It fails if the asset is missing or differs, and needs no additional secret. Maintainers can also run `./vendor.sh --verify <plugin>` locally with GitHub CLI authentication.

To remove a plugin, delete its entire directory and remove its entries from the marketplace catalogs and `package.json`.
