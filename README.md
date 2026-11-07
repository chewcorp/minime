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
| Devin | `devin plugins install chewcorp/minime#plugins/coder` | skills, agents |
| pi | `pi install git:github.com/chewcorp/minime` | skills |
| Kilo | `git clone https://github.com/chewcorp/minime && minime/plugins/coder/install.sh` (`--project` for one repo) | skills, agents, role models |
| opencode | `git clone https://github.com/chewcorp/minime && minime/plugins/coder/install.sh --prefix ~/.config/opencode` | skills, agents |
| Perplexity Computer, others | Upload or copy `plugins/coder/skills/*/SKILL.md` into the client's skills | skills |

For `agents`, swap `coder` for `agents` in the plugin rows (for example `/plugin install agents@minime`, or `devin plugins install chewcorp/minime#plugins/agents`). It has no `install.sh`, so for Kilo, opencode and others, copy `plugins/agents/skills/*` into the client's skills folder.

Installs are verified with Claude Code, Codex, Copilot CLI, pi, Kilo and opencode. The other rows follow each client's documented plugin format and haven't been tried yet.

Start the coder loop by asking for it by name, or run `/deliver` (`/coder:deliver` in Claude Code). Start agents with `/recruit` (`/agents:recruit`).

## Layout

- `.claude-plugin/marketplace.json` is the catalog read by Claude Code, Codex, Copilot CLI and Factory Droid. `.cursor-plugin/marketplace.json` (Cursor) and `.grok-plugin/marketplace.json` (Grok Build) carry the same entries; keep the three in step when adding a plugin.
- `package.json` lists each plugin's skills for pi.
- `plugins/<plugin>/` is a vendored release. Don't edit it here; change the plugin repo, release, then vendor.

## Vendoring a release

```bash
./vendor.sh coder v0.2.0                                 # from the minime-coder GitHub release
./vendor.sh coder ../minime-coder/dist/minime-coder-0.2.0.tar.gz   # from a local ./release.sh --build-only
```

Commit the result with the tag in the message and open a PR.

`agents` is vendored automatically: a version bump merged in chewcorp/minime-agents publishes a release, and its release workflow runs `./vendor.sh agents` and pushes the result to `main` here.
