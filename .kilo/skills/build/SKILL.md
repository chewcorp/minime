---
name: build
description: Smallest complete diff. One concern per change with proof plan up front.
---

# build

Ladder, first rung that fully works: skip it → reuse codebase → stdlib/platform → installed dep (never add one for a few lines) → one-liner → minimum code.

One concern per change. State proof plan up front: test, check, or calculation a reviewer can rerun. For behaviour changes the plan is acceptance examples: per criterion, exact calls through the real entry point (CLI, API, UI) with expected output and exit status, including the edge forms the criterion's words imply and inputs where user input first meets a reused parser or library (argument parsing, string or number parsing). Write them as tests first; examples of new behaviour must fail before the change, ones that already pass stay as regression tests. Mark known limits as `shortcut: <limit>, <when to upgrade>`.

Friction reducers: tidy (strip unneeded docs/comments on touch, keep only non-obvious why); quiet (decide two-way doors alone, batch questions); replan (two-way door → adjust tickets inline, one-line delta, no re-clarify).

Done when tests/lint green, small test for non-trivial logic, proof artifact kept re-runnable. Never add unasked option/config/abstraction. Never cut trust-boundary validation, data-loss handling, security, a11y, or anything asked.
