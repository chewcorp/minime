# A/B/C: land-learn commit step, in the body vs body + description (e2e-version-json) — 2026-10-23

This supersedes the per-arm numbers in `AB-land-learn-commit-2026-10-23.md`.

## Runs

- All runs used the free model only (`kilo/kilo-auto/free`) in the f8-repeats Codespace. Every export reports cost 0 and only that model.
- There were no exits 65 or 4.
- The new arm ran at 92ab2b0, with the selftest at 13/13 ok. Its rep 1 hit the free-model limit once, waited 15 minutes, and was rerun.

## Arms and exclusions

- **baseline:** reps 4–12, n = 9. Rep 13 is excluded because it was rate-limited from the start (0 tokens).
- **land-learn-commit:** reps 1–8, n = 8.
  - Rep 10 is excluded because it was rate-limited from the start.
  - Rep 9 is now excluded too. Its transcript hits `Too Many Requests: Free model usage limit reached` partway through (session.txt line 137). The first A/B note counted it as a prove failure.
- **land-learn-commit-desc:** reps 1–10, n = 10.

## Re-scoring the converge stage (2c083fa)

- **Method:** the old arms' work dirs are gone, so only the converge stage was re-scored. Each run's `.kilo/run/*` stage files were rebuilt from its committed `diff.patch`, and the fixed converge logic was rerun on them. Every other stage keeps its recorded value.
- **Result:** no verdict changed. All 6 old "converge" root causes became "land-learn" (baseline reps 4, 6, 7, 10, 11; land-learn-commit rep 6). Spot-checks confirm these are genuine whole-diff approvals, for example baseline rep 10 ("No blocking findings. Advisory: none.") and rep 7 ("No blocking findings. … Approved to land (no merge).").
- **Desc arm:** scored live by the fixed oracle.

## Results

| | baseline | land-learn-commit | land-learn-commit-desc |
|---|---|---|---|
| n | 9 | 8 | 10 |
| e2e pass | 1/9 | 2/8 | 3/10 |
| land-learn stage passed | 1/9 | 3/8 | 3/10 |
| ran `git commit` on a non-main branch | 1/9 | 4/8 | 7/10 |
| loaded land-learn skill (skill call or SKILL.md read) | 1/9 | 5/8 | 6/10 |
| main untouched | 9/9 | 8/8 | 10/10 |
| root causes | land-learn 6, prove 2 | land-learn 4, prove 1, chart 1 | chart 3, build 1, converge 1, prove 1, land-learn 1 |
| median secs | 36 | 120.5 | 168 |
| total tokens | 2,408,969 | 3,123,220 | 4,328,834 |

How the commit column was counted: from the bash tool outputs in each export. A run counts if it shows a `[<branch> <sha>]` commit line, or a successful `git commit` after `Switched to a new branch '<b>'`. Land-learn-commit rep 3 used `git commit -q`, which prints no commit line.

**Fisher exact tests (one-sided):**

| comparison | metric | split | p |
|---|---|---|---|
| desc vs baseline | commit | 7/10 vs 1/9 | ≈ 0.015 |
| desc vs baseline | skill load | 6/10 vs 1/9 | ≈ 0.04 |
| desc vs baseline | land-learn stage | 3/10 vs 1/9 | ≈ 0.33 |
| desc vs baseline | pass | 3/10 vs 1/9 | ≈ 0.33 |
| desc vs land-learn-commit | commit | 7/10 vs 4/8 | ≈ 0.35 |
| desc vs land-learn-commit | skill load | 6/10 vs 5/8 | ≈ 0.72 |

## Reading

- **Committing on a task branch is now usual.** It happened in 7 of 10 desc runs, and main stayed untouched in every run of every arm. It's the only metric with a clear separation from baseline. Desc rep 10 committed without loading land-learn.
- **The description change did not raise the skill-load rate over the body-only variant (6/10 vs 5/8).** Both variants load far more than baseline (1/9). The body-only variant's description is identical to baseline's, so that gap can't come from the description. Treat it as run-to-run drift, not an effect.
- **Land-learn passes are now capped by the handoff artifact, not the commit.** Desc reps 4, 8, 9 and 10 all committed but wrote no `land-learn.md`, `handoff.md` or `land.md`. The prompt asks for each stage's output, so the stage correctly fails.
- **The variants run longer and use more tokens,** because more runs go through the whole loop.

**Verdict:**
- Ship the commit step in the body. The description line is harmless but not shown to help.
- E2E pass is not decision-grade at this N.
- The next lever is the land-learn handoff artifact, and then charting.

## Oracle notes

- **Plausible false fail, desc chart stage (reps 3, 8, 9):**
  - The chart skill says "Optional for one-ticket work. Required for multi-ticket." Deliver routes a single buildable ticket straight to `build`. Rep 10's chart.md even says "Single-ticket work; no blocking edges. Chart optional per skill."
  - Reps 3, 8 and 9 skipped `chart.md`, so the oracle blames chart.
  - No verdict changes: none of those runs wrote a land-learn artifact either. Under a chart-optional rule, rep 9 would root-cause at land-learn and reps 3 and 8 at prove (they wrote no prove.md).
  - Decision needed: should e2e require `chart.md` when the work is one ticket?
- **Correct fail, desc rep 2:** it wrote only acceptance.md, clarify.md and chart.md, and never changed `cli.py` (dropped at build).
- **Correct fail, desc rep 4:** it committed on `calc-cli-version-json` but wrote no converge.md and no land-learn artifact.
- **Correct fail, land-learn-commit rep 7:** it committed (`[cli-version-json d66cf2b]`) but wrote no land-learn artifact.
