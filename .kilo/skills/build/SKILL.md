---
name: build
description: Smallest complete diff. One concern per change with proof plan up front.
---

# build

Ladder, first rung that fully works: skip it → reuse codebase → stdlib/platform → installed dep (never add one for a few lines) → one-liner → minimum code.

One concern per change. Split a function only when it does several unrelated jobs, never by line count. Between options of equal size, take the one correct on edge cases.

State proof plan up front: test, check, or calculation a reviewer can rerun. For behaviour changes the plan is acceptance examples: per criterion, exact calls through the real entry point (CLI, API, UI), written literally as a user types them, with expected output and exit status.

Examples include the edge forms the criterion's words imply and inputs where user input first meets a reused parser or library (argument parsing, string or number parsing); each reused parser gets one example in its own syntax with no padding (for argparse, a value starting with `-`).

Write them as tests first and keep them verbatim: never add `--`, quoting or spacing to make one pass; fix the code. If no code change can satisfy an example, stop and return it with its output. Examples of new behaviour must fail before the change; ones that already pass stay as regression tests.

Mark known limits as `shortcut: <limit>, <when to upgrade>`.

Friction reducers: tidy (strip unneeded docs/comments on touch, keep only non-obvious why); quiet (decide two-way doors alone, batch questions); replan (two-way door → adjust tickets inline, one-line delta, no re-clarify).

Done when tests/lint green (no linter configured → if the language's standard one is installed, e.g. `ruff check`, run it on changed files and fix what the change introduced; never install one), small test for non-trivial logic, proof artifact kept re-runnable. Never add unasked option/config/abstraction. Never cut trust-boundary validation, data-loss handling, security, a11y, or anything asked.
