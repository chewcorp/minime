---
name: build
description: Use when implementing one delivery-loop ticket. Produces the smallest complete diff, one concern per change, with acceptance examples written as failing tests first.
---

# build

One ticket at a time, on the `<task>` branch. Load the `prove` skill before step 2.
For review repairs, first obtain admission through converge's shared gate; build
is not an alternative path around that admission. Resolve ordering/feasibility risks
with the [bounded investigation contract](../deliver/references/investigation.md)
before dependent production implementation; never promote disposable code.

1. **Pick the smallest rung that fully works:** skip it → reuse the codebase → stdlib or platform → an installed dependency (never add one for a few lines) → a one-liner → the minimum code. Between options of equal size, take the one correct on edge cases. Add an option, config or abstraction only when asked. Keep trust-boundary validation, data-loss handling, security, accessibility and everything asked.
2. **Write the proof first** (`prove` step 1). For a behaviour change the proof is acceptance examples: for each criterion, exact invocations or interaction steps through the real entry point (CLI, API, UI), with preconditions, expected output or observable state, and exit status where applicable.
   - Derive boundary cases from the accepted contract and its consumers. When changing a boundary, consult [contract examples](references/contracts.md) for relevant failure patterns.
   - Write them as tests, preserving contractual inputs, actions and expected results verbatim, not incidental test implementation. When one fails, fix the code, never reshape the contract to suit the implementation. If no code change can satisfy an example, stop and return it with its observed result.
   - Examples of new behaviour must fail before the change; ones that already pass stay as regression tests.
3. **Implement.** One concern per change; split a function only when it does several unrelated jobs, never by line count. On lines you change, drop comments that restate the code and keep only the non-obvious why. Mark a known limit `shortcut: <limit>, <when to upgrade>`.

   Trace changed contracts through their actual producers and consumers; preserve supported behaviour and reuse established implementations.

   For a fix, search for the same cause across affected paths. Repair the cause within scope, record unresolved occurrences, and verify both the defect and behaviour the repair must preserve.
4. **Decide reversible implementation choices yourself.** Record non-scope decisions in `.minime/<task>/implementation.md`; do not edit accepted tickets inline. If a decision changes accepted outcomes or tickets, stop for a human ruling and review, then adopt the revised scope through the gate before continuing.
5. **Commit on `<task>`, never the default branch.** Stage only the task's paths by name. Keep small ordered commits that read as an argument: failing test, then fix. Do not rewrite published history without the human's instruction.

Done when the work is committed on `<task>` (reviewers read commits, not your working tree), the acceptance tests went red then green, the repo's tests and linter pass (no linter configured: run the language's standard one if installed, such as `ruff check`, on changed files and fix what the change introduced; never install one), non-trivial logic has a small test, and every claim has its `prove` row in `.minime/<task>/proof.md`.

Mark the finished ticket with `python3 "$GATE" <task> done T1` (use its actual
ID; single-ticket work is T1), then run `next`. During an admitted repair, call
`done` only after the entire repair is committed; it requires a clean tree and
returns routing to build, where `next` resumes converge when all tickets are
complete. Do not enter final converge while another accepted ticket is
unfinished. See the [gate contract](../deliver/references/gates.md).
