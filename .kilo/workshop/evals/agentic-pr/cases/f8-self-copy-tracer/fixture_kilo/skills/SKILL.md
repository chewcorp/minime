---
name: build
description: Smallest complete diff. One concern per change with proof plan up front.
---

# build

Ladder, first rung that fully works: skip it → reuse codebase → stdlib/platform → installed dep (never add one for a few lines) → one-liner → minimum code.

One concern per change. State proof plan up front: test, check, or calculation a reviewer can rerun. Mark known limits as `shortcut: <limit>, <when to upgrade>`.

Friction reducers: tidy (strip unneeded docs/comments on touch, keep only non-obvious why); quiet (decide two-way doors alone, batch questions); replan (two-way door → adjust tickets inline, one-line delta, no re-clarify).

Done when tests/lint green, small test for non-trivial logic, proof artifact kept re-runnable. Never add unasked option/config/abstraction. Never cut trust-boundary validation, data-loss handling, security, a11y, or anything asked.
