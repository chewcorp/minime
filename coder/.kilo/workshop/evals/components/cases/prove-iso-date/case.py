"""prove: the proof exercises the actual input from the ask, not a nearby proxy."""
import re

from lib import py, read, tests_pass

COMPONENT = "prove"
INPUT = "2026-01-02T03:04:05Z"
PROMPT = (f"parse_date('{INPUT}') in calc.py must return the date 2026-01-02, and plain dates like "
          "'2026-01-02' must keep working. Implement it and put the proof in PROOF.md.")


def check(c, work, transcript):
    ok, out = py(work, f"import calc, datetime; d = datetime.date(2026, 1, 2); "
                       f"print(calc.parse_date('{INPUT}') == d == calc.parse_date('2026-01-02'))")
    c("Z timestamp and plain date both parse to the date object", ok and out == "True", out)
    c("tests pass", tests_pass(work))
    proof = read(work, "PROOF.md")
    c("proof uses the exact input from the ask", INPUT in proof)
    outputs = [l for l in proof.splitlines() if "parse_date" not in l and INPUT not in l
               and re.search(r"2026-01-02|date\(2026, 1, 2\)", l)]
    c("proof shows a command and its output", re.search(r"python3?\b", proof) and outputs)


def good(work):
    calc = work / "calc.py"
    calc.write_text(calc.read_text().replace(
        "    return datetime.date.fromisoformat(s)",
        "    return datetime.date.fromisoformat(s[:10])"))
    (work / "PROOF.md").write_text(
        f"$ python3 -c \"import calc; print(calc.parse_date('{INPUT}'), calc.parse_date('2026-01-02'))\"\n"
        "2026-01-02 2026-01-02\n")


def bad(work):
    good(work)
    (work / "PROOF.md").write_text("Implemented; tests passed.\n")
