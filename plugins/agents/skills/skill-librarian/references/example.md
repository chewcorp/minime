# Worked example: `/progress` in rgh-sme

Proposal: keep [`.agents/skills/progress/SKILL.md`](https://github.com/chewcorp/rgh-sme/blob/545b4b86802260341fc91ff377542798727d7bfa/.agents/skills/progress/SKILL.md) as a skill (`.claude/` and `.cursor/` copies are symlinks to it). It runs [`scripts/curation-progress.sh`](https://github.com/chewcorp/rgh-sme/blob/545b4b86802260341fc91ff377542798727d7bfa/scripts/curation-progress.sh), which execs [`scripts/curation-progress.py`](https://github.com/chewcorp/rgh-sme/blob/545b4b86802260341fc91ff377542798727d7bfa/scripts/curation-progress.py), shows the table unchanged, then restates its columns and a fixed list of follow-up commands.

```
verdict: script
scope: Show per-domain curation progress (pending fleeting notes).
reason: Repeat fails for a shared skill: the three host copies live in chewcorp/rgh-sme, one seat. Scope is one sentence. Pipeline: the table (PENDING, NEW_SINCE, RELEVANT_PENDING, MAX_P, P>0.7, sort order, * marker) has one right answer and already lives in scripts/curation-progress.py; the skill restating it is A8. Already there: searched minime-agents and minime-coder skills and the rgh-sme skills; none prints this ledger. Hook row does not match: nothing must run when the model never loads a skill. Retire keeps the script form.
verify: known input: a fixture repo whose fleeting note is absent from curation/<slug>.txt marks that domain's row with *; clean input: every note ledgered gives no * row and --pending-only prints "No domains with pending work." (tests/test_curation_progress.py, test_pending_only_footer_when_every_raw_pending_is_zero). Eval: /progress answered with the script vs a model counting ledgers itself, each scored against the fixture's known pending counts.
retire: delete scripts/curation-progress.py when rgh-sme no longer keeps per-domain curation ledgers
```
