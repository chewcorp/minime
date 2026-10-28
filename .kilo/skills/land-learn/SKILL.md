---
name: land-learn
description: Commit the work on a task branch (never main), ship small ordered commits, then harvest handoff and retro.
---

# land-learn

Ship: commit the work on a task branch first (`git switch -c <task>`, then `git add` and `git commit`); a task is not landed until it is committed, whatever the default about leaving changes uncommitted. Then rebase into small ordered commits, babysit conflicts/threads/CI in one batched push stopping at merge-ready, fresh-agent verify per PR, land contiguous verified bottom-up. Default-branch merge is always human. The final report opens with the one thing the reader must do next and who does it; if nothing is needed, say so first.

Learn: compact handoff to `$TMPDIR` (reference, don't duplicate; suggested-skills section; redact secrets) plus retro on the environment not the product (Navigation, Checks, Standards, AGENTS, Tool-economy, No-ops, Info-access; mechanical → linter/hook/CI, judgement → CODING_STANDARDS).
