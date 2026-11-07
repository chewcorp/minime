# Finding triage

Use when a finding is disputed or concerns a response to an earlier review.

Check the premise against the current artifact and accepted intent. A stale
description, unsupported severity or reviewer consensus does not establish a
defect. Keep blocking status only when reproduction or source evidence shows
that the caller's blocking rule applies.

Assess the remedy separately. A valid defect can require a different repair
from the one suggested. Challenge requests that expand the solution or break
supported behaviour; record why and identify a compatible alternative where
possible. Decisions that change accepted intent return to the owning stage.

For later findings, distinguish:

- Introduced regression: before/after commit evidence shows the repair caused it.
- Incomplete remediation: the original cause remains in an affected path.
- Pre-existing discovery: the defect already existed before the repair.
- Origin unknown: available evidence does not establish when it appeared.

Inspect the response diff as well as the original finding. A renamed or moved
check can preserve unwanted behaviour; a broader rule can remove valid paths.
Record the evidence for the classification without treating every later-pass
finding as a newly introduced defect.

Origin and disposition are separate. Compare with the PR base as well as the
previous repair commit. A defect that predates the repair may still have been
introduced by the PR. An unrelated defect already present at the base is advisory
and belongs in the follow-up list; it does not consume a repair round. A base
defect that prevents an accepted outcome or becomes newly reachable through the
change can still block. Unknown origin is not a reason to dismiss demonstrated
impact under the caller's blocking rule.

Keep every declined blocker and its evidence visible in `review.md` and the PR
handoff. If declining depends on unwritten intent or outside knowledge that the
reviewer cannot verify, ask the human rather than silently suppressing it.

## Context references

These pinned wiki sources provide background; the local rules above remain
usable without wiki access.

- [Finding vs Remedy](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/finding-vs-remedy.md): separate defect evidence from repair suitability. Use the qualified disposition rules above rather than automatically downgrading everything pre-existing.
- [Comprehension Test](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/comprehension-test.md): for ambiguous specifications, a fresh paraphrase can expose missing links. Concrete conflicting readings warrant clarification; one reader's confusion alone is not an incontestable verdict.
- [Divergent Readings](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/divergent-readings.md): compare independent interpretations when ambiguity matters. This is an evaluation candidate, not another mandatory dispatch.
- [Attacker-Gain Test](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/attacker-gain-test.md): identify exploit preconditions and added capability. Check the actual trust boundary, affected principals and intended security requirements; existing access alone does not dismiss persistence, integrity or cross-boundary impact.
