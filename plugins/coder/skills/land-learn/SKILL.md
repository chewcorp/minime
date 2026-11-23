---
name: land-learn
description: Use when converge is done on a delivery-loop task. Ships the reviewed commits from the task branch (never the default branch), brings each pull request to merge-ready for a human to merge, then writes the handoff and retro.
---

# land-learn

## 1. Ship

1. Verify the clean `<task>` branch contains the commits approved by converge. Do not create new content commits here; repairs use the shared path below. Do not rewrite published history without the human's instruction.
2. Refresh `<base>` with `git fetch origin` if it is a remote-tracking ref. Run `python3 "$GATE" <task> ready --base <base>`. If evidence is missing or stale, restart at converge's opening `review` command before sections 1–3, even if the task branch did not change. Push and open or update the pull request only after `ready` passes. Triage conflicts, review threads and CI findings: dismiss unsupported findings with evidence; every content-changing repair returns to `converge` section 4 **before editing**, using the same repair admission and fresh review/proof/approval afterward. A repair a human reviewer requested uses `fix --by human` and leaves the counter unchanged. Land-learn has no separate fix loop. For stacked pull requests, work only the lowest unmerged one until it is merge-ready.
   Include every declined blocker with its evidence, open human decisions and what was not checked in the PR body. Do not present the author's triage as independent approval; see [handoff and learning](references/handoff-learning.md).
3. After every push or history change, refresh `<base>` and rerun `ready`. Retain evidence only for the same diff and accepted scope. If evidence is missing/stale, restart at converge's opening `review` command before sections 1–3; if a verified defect needs repair, return to section 4. An approver failure never leaves the loop without a next step. Do not label the PR merge-ready while any gate is blocked.

Merge-ready means: checks green, every review thread answered (fixed, or declined with a reason), no conflicts, and the [local gate](../deliver/references/gates.md) passes for the current diff and accepted scope. Local readiness alone does not establish forge readiness. Stop there. Merging into the default branch is always the human's.

## 2. Learn

1. Write `.minime/<task>/handoff.md`: what changed, where proof lives (point to `proof.md`, `review.md`, `approval.md`; do not copy them), open items, and a suggested-skills section. Redact secrets.
2. Add a retro on the environment, not the product. Before persisting guidance, apply the counterfactual bar in [handoff and learning](references/handoff-learning.md): would a future engineer repeat the mistake without it? Update existing guidance before adding; skip lessons already evident from the code and tests. Store useful detail in a relevant reference or solutions document, with only a short pointer in always-loaded instructions.

Done when the pull request is merge-ready, `handoff.md` exists, and the final report opens with the one thing the reader must do next and who does it (or says nothing is needed).
