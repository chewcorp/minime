---
name: prove
description: Use before claiming any delivery-loop result is done, fixed, faster or working. Verifies each claim against the real artifact on its real surface, records a rerunnable check, and reports pass, fail or unproven. Loaded by build, converge and land-learn.
---

# prove

A claim is done only when a check you ran on the real artifact shows it. Compiling, "tests passed", a summary, or a subagent's report is a lead, not a proof.

1. **Name the oracle before the work.** For each claim, write the observable state that makes it true and the surface it lives on: the CLI command, API call, UI action, or stored value a user would see. For a bug fix the oracle must tell the fixed state from the original defect: reproduce the defect first and keep that check.
2. **Check the real artifact on that surface.** If the repo has a verification skill (such as `verify-<app>`) or a documented run command, launch and drive the app through it the way a user would. Run it, read the actual value, inspect the actual diff. A check on another surface (a unit test for a CLI claim, a mock for an API claim) or an inconclusive result is unproven, not a pass. When a check disagrees with expectation, suspect the observation first (wrong path, stale build, cached output, wrong environment), then the system. For final evidence, start from a clean committed tree and capture `git rev-parse HEAD^{tree}` before the run; if content changes during the check, rerun rather than relabeling old output. Build-time dirty-tree checks remain provisional until rerun on that tree.
3. **Make the check able to fail.** For a new or changed test, show it red: run it before the change, or revert the change and run it. Its result must depend on the claimed property, with expectations derived independently of the implementation's assumptions. Confirm the documented runner executes it. When designing or assessing a check, consult [evidence pitfalls](references/evidence.md). When a test run reports skipped, xfail or deselected tests (`OK (skipped=1)`, `1 skipped`), find each one: unskip it if it covers the claim, otherwise name it and say why in the report. Echoing the summary line is not calling it out.
4. **Record it.** For shell checks, give one copy-pastable command (`python3 bench.py`, `python3 -c '…'`, `python3 -m timeit …`); a sequence you ran twice becomes a script file. For interactive UI checks, record preconditions, exact actions and observed rendered state, with screenshots or recordings where needed to substantiate the claim. Use `N/A` for exit status when no process exit applies. Append one row per claim to `.minime/<task>/proof.md`:
   `outcome/claim | captured scope | base tree (required for independent or base-dependent checks) | task tree | role (author/independent) | command or interaction steps | observed output/state (trimmed; evidence reference) | exit status or N/A | pass/fail/unproven`
   For author checks before converge captures a review token, write `provisional (pre-review)` in the captured scope field. Keep these rows as leads; never backfill the token. Use the captured review token for fresh evidence run in converge.
   Base-dependent checks must also capture the merge-base tree before running. Performance claims also record the bottleneck (CPU, I/O, lock contention, network), sample count, median, range as min–max, and a verdict: faster, slower, no-diff or inconclusive.
   Retain historical rows, but assess only the current diff and accepted scope.
   Aggregate every required check per outcome; one passing subcheck cannot erase
   another current failure. After the report is complete, register independent
   results with the [gate](../deliver/references/gates.md); it also binds reports
   to their contents and invalidates approval when underlying evidence changes.
5. **Report the result.** Per claim: pass, fail or unproven, each with its row. Say what was not checked and why. Show the command and actual output, or interaction steps and observed state with supporting evidence. Your own checks are leads until a fresh agent reproduces them (`converge` sections 1 and 2).

Done when every claim in your report has a `proof.md` row with a check a reviewer can reproduce, and each row's result is the one you observed.
