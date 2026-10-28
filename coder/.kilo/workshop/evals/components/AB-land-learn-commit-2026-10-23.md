# A/B: land-learn-commit vs baseline (e2e-version-json) — 2026-10-23

**Superseded:** see `AB-land-learn-commit-desc-2026-10-23.md`. That file re-scores the converge stage after 2c083fa, excludes land-learn-commit rep 9 (rate-limited partway through), and adds the commit-desc arm.

Free model only (`kilo/kilo-auto/free`), in the f8-repeats Codespace on d227b1c. Selftest was 13/13 ok. There were 20 runs with the arms interleaved: baseline reps 4–13 alternating with variant reps 1–10. Every export reports cost 0 and only that model. No exit 65 or exit 4. `lib.py summary` table (the e2e baseline row also includes reps 1–3 from the map run, which were scored with the oracles from before #13):

| component | case | model | pass | checks | median s | root causes |
|---|---|---|---|---|---|---|
| build | build-mean-fix | kilo/kilo-auto/free | 2/2 | 8/8 | 13 | - |
| build | build-self-copy | kilo/kilo-auto/free | 2/2 | 2/2 | 184.5 | - |
| build | build-subtract | kilo/kilo-auto/free | 2/2 | 10/10 | 31.5 | - |
| converge | converge-clean-diff | kilo/kilo-auto/free | 2/2 | 8/8 | 102.5 | - |
| converge | converge-planted-bug | kilo/kilo-auto/free | 2/2 | 10/10 | 29.5 | - |
| converge | converge-round-cap | kilo/kilo-auto/free | 1/2 | 4/6 | 94.5 | - |
| deliver | deliver-diff-ready | kilo/kilo-auto/free | 2/2 | 4/4 | 20 | - |
| deliver | deliver-stay-out | kilo/kilo-auto/free | 2/2 | 8/8 | 13 | - |
| deliver | deliver-vague | kilo/kilo-auto/free | 2/2 | 4/4 | 31 | - |
| e2e | e2e-version-json | kilo/kilo-auto/free | 1/13 | 15/39 | 43 | clarify, converge, land-learn, prove |
| e2e | e2e-version-json | kilo/kilo-auto/free [land-learn-commit] | 2/10 | 14/30 | 120.5 | chart, clarify, converge, land-learn, prove |
| prove | prove-iso-date | kilo/kilo-auto/free | 1/2 | 7/8 | 68 | - |
| prove | prove-perf-claim | kilo/kilo-auto/free | 0/2 | 8/12 | 14 | - |
| prove | prove-skipped-test | kilo/kilo-auto/free | 2/2 | 6/6 | 17.5 | - |

## Per arm (baseline reps 4–13 vs variant reps 1–10)

Two runs are excluded as infrastructure failures: baseline rep 13 and variant rep 10. Both transcripts end with `Error: Too Many Requests: Free model usage limit reached.` (0 tokens). That leaves n = 9 per arm.

| | baseline | land-learn-commit |
|---|---|---|
| e2e pass | 1/9 | 2/9 |
| land-learn stage passed (flag committed on a non-main branch plus a land-learn artifact) | 1/9 | 3/9 |
| ran `git commit` (from the export's bash tool calls) | 1/9 | 4/9 |
| loaded the land-learn skill (skill call or read of its SKILL.md) | 1/9 | 5/9 |
| main untouched | 9/9 | 9/9 |
| root causes | converge 5, prove 2, land-learn 1 | land-learn 3, prove 2, chart 1, converge 1 |
| median secs | 36 | 122 |
| total tokens (exports) | 2,408,969 | 3,346,343 |

One-sided Fisher exact tests:
- commit 4/9 vs 1/9: p ≈ 0.15
- land-learn stage 3/9 vs 1/9: p ≈ 0.29
- pass 2/9 vs 1/9: p ≈ 0.50
- skill loaded 5/9 vs 1/9: p ≈ 0.07

## Reading

- **When the skill loads, the commit step works:** 4 of the 5 variant runs that loaded land-learn ran `git commit` on a task branch, and 3 of those passed land-learn. Every run that didn't load land-learn left the work uncommitted, in both arms.
- **The bottleneck is reaching land-learn, not what the skill says.** Most baseline runs end about 35 s in, after deliver, clarify or chart. Their converge.md files never name the requirements, which is why converge is the usual root cause, and they never load land-learn. The variant only changes the SKILL.md body, so its higher load rate (5/9 vs 1/9) is most likely noise. That's also why its runs take longer and use more tokens: more of them run the whole loop.
- **Verdict:** directionally positive for the commit wording, but not decision-grade at n = 9 per arm. The variant doesn't regress anything we measured, and main stayed untouched in every run. The next lever is getting the loop to reach land-learn (deliver's stage hand-off), not more land-learn wording.

## Oracle notes

- **Correct fail, variant rep 7:** it committed on a non-main branch (`[cli-version-json d66cf2b] cli: add --version and add --json output modes`), but it never wrote a land-learn artifact. Its stage files are acceptance, build, chart, converge and prove. The prompt asks for each stage's output, so the oracle is right. Partial credit: the commit step itself worked.
- **Plausible oracle strictness, baseline converge failures:** baseline rep 4's converge.md reads "Review: small diff, one concern. Blocking: none. … Merge-ready (not merged per instruction)". It approves without naming either requirement, so the keyword trace misses it. This doesn't change any verdict: the same runs also never committed (rep 4 land-learn.md: "No commit made.").
