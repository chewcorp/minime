---
name: converge
description: Review that ends and approval that means it. Fresh contexts, outside caps.
---

# converge

Review (fresh context, reads conventions/structure/tests/docs, never AC): one structural finding per root cause; same class back means fix the root once or narrow the rule; verify finding against source, declined needs a written reason; Important only when it breaks behaviour, leaks data, or breaches policy, naming which; a regression of behaviour the repo already supported is Important whether or not the ticket names it, new unsupported inputs (pathological sizes, fuzzing) are nits; nits capped at five, rest counted; never report what CI enforces; each finding states which core claim it undermines.

Task key is the branch slug, set by the parent before dispatch. Approve (fresh context): parent passes resolved acceptance path plus fallback issue text; derive criteria from `.kilo/run/<task>/acceptance.md` when it matches the active task, else the passed text. Report per-criterion pass/fail/unproven with evidence. Never edits or merges.

Rounds: counter at `.kilo/run/<task>/review-round`, reset when a new review starts. Increment each fix round; 2 standard rounds max. Round 3 routes to advisor for one step-back brief; implementor acts once on it or escalates to human. Same cause 3+ times → human.

Done when approve table all pass with evidence plus reviewer verdict approve. Branch protection and human merge gate decide.
