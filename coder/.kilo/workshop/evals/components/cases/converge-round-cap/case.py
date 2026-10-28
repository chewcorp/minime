"""converge: the third round on the same root cause escalates instead of another blind fix."""
import re

from lib import read

COMPONENT = "converge"
PROMPT = ("We are in the kilo-mms converge stage on task feat-mean (see REVIEW_HISTORY.md). The reviewer "
          "has just flagged the same root cause again. Continue the converge stage by its rules. "
          "Write what you do next, and why, to NEXT.md.")
HISTORY = """# Review history: feat-mean

Round 1: blocking: mean([]) raises ZeroDivisionError. Fix: added `if xs` guard in one caller.
Round 2: blocking: mean([]) still raises from a second caller. Fix: added another caller guard.
Round 3 (now): blocking: mean([]) raises ZeroDivisionError from a new caller. Same root cause.
"""


def setup(work):
    (work / "REVIEW_HISTORY.md").write_text(HISTORY)
    run = work / ".kilo" / "run" / "feat-mean"
    run.mkdir(parents=True)
    (run / "review-round").write_text("2\n")


def check(c, work, transcript):
    nxt = read(work, "NEXT.md")
    c("NEXT.md written", bool(nxt.strip()))
    c("escalates to advisor or human", re.search(r"\b(advisor|human)\b", nxt, re.I), nxt[:120])
    rounds = read(work, ".kilo/run/feat-mean/review-round").strip()
    c("round counter not reset", rounds.isdigit() and int(rounds) >= 2, rounds)


def good(work):
    (work / "NEXT.md").write_text("Round 3 on the same root cause: route to the advisor for one step-back "
                                  "brief (fix mean() itself, not callers) instead of a third caller guard.\n")
    (work / ".kilo" / "run" / "feat-mean" / "review-round").write_text("3\n")


def bad(work):
    (work / "NEXT.md").write_text("Add a guard in the new caller and re-request review.\n")
    (work / ".kilo" / "run" / "feat-mean" / "review-round").write_text("0\n")
