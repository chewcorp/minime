# Review boundaries

[Converge sections 4–5](../SKILL.md#4-triage-before-fixing) own repair triage and
escalation policy; the [gate contract](../../deliver/references/gates.md#one-repair-path)
owns admission, repair-completion transitions and counter semantics.

## Context references

Local instructions are sufficient when the private wiki is unavailable.

- [Retry vs Re-plan](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/retry-vs-replan.md): design feedback needs a ruling, not another reactive patch.
- [Prose State Machine](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/prose-state-machine.md): remove unnecessary states; use code for deterministic admission and retain human judgement for structural changes.
- [Measured Retune](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/measured-retune.md): compare agent behaviour before claiming improvement. One run per arm is a smoke test; repeated comparable runs and a predeclared bar are needed for stronger conclusions. Risk tiers and additional review dispatches remain evaluation candidates.
