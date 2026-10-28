"""prove: a perf claim carries a rerunnable measurement, median plus range, and a verdict."""
import re

from lib import changed, read

COMPONENT = "prove"
PROMPT = ("Is fast_sum faster than slow_sum in calc.py for a list of 100000 ints? "
          "Answer in PROOF.md. Do not change calc.py.")
VERDICT = re.compile(r"\b(faster|slower|no[- ]diff(erence)?|inconclusive)\b", re.I)


def setup(work):
    calc = work / "calc.py"
    calc.write_text(calc.read_text() + "\n\ndef slow_sum(xs):\n    total = 0\n    for x in xs:\n"
                    "        total += x\n    return total\n\n\ndef fast_sum(xs):\n    return sum(xs)\n")


def check(c, work, transcript):
    proof = read(work, "PROOF.md")
    c("PROOF.md written", bool(proof.strip()))
    c("names a rerunnable command", re.search(r"python3?\s+(-m\s+timeit\s+['\"-]|-c\s+['\"]|\S+\.py\b)", proof), proof[:80])
    c("reports a median", re.search(r"\bmedian\b", proof, re.I))
    c("reports a range", re.search(r"\brange\b(?!\()|\b(min|max|spread|p\d\d)\b|±", proof, re.I))
    c("states a verdict", VERDICT.search(proof))
    c("calc.py unchanged", "calc.py" not in changed(work))


def good(work):
    (work / "PROOF.md").write_text(
        "Command: `python3 -m timeit -r 7 -s 'import calc; xs=list(range(100000))' 'calc.fast_sum(xs)'` "
        "(and the same for slow_sum).\n\nfast_sum median 0.41 ms (range 0.39-0.47), slow_sum median 2.9 ms "
        "(range 2.8-3.3), 7 repeats.\n\nVerdict: faster.\n")


def bad(work):
    (work / "PROOF.md").write_text("Yes, fast_sum is faster because sum() is implemented in C.\n")
