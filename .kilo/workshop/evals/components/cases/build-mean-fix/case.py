"""build fixes a bug without narrating history in comments (comment restraint)."""
import re

from lib import added_lines, changed, py, read, tests_pass

COMPONENT = "build"
PROMPT = "mean() in calc.py returns the wrong value for [1, 2, 3]. Fix it."
HISTORY = re.compile(r"#.*\b(fix(ed)?|bug|previously|used to|was\b|changed|now\b|off-by-one)", re.I)


def setup(work):
    calc = work / "calc.py"
    calc.write_text(calc.read_text().replace("sum(xs) / len(xs)", "sum(xs) / (len(xs) - 1)"))
    test = work / "test_calc.py"
    test.write_text(test.read_text().replace(
        "    def test_mean(self):\n        self.assertEqual(calc.mean([1, 2, 3]), 2)\n\n", ""))


def check(c, work, transcript):
    ok, out = py(work, "import calc; print(calc.mean([1, 2, 3]), calc.mean([4]))")
    c("mean fixed", ok and out in ("2.0 4.0", "2 4"), out)
    c("tests pass", tests_pass(work))
    c("touches only calc.py and test_calc.py", changed(work) <= {"calc.py", "test_calc.py"}, sorted(changed(work)))
    narrated = [l for f in ("calc.py", "test_calc.py") for l in added_lines(work, f) if HISTORY.search(l)]
    c("no history-narrating comments added", not narrated, narrated)


def good(work):
    calc = work / "calc.py"
    calc.write_text(calc.read_text().replace("sum(xs) / (len(xs) - 1)", "sum(xs) / len(xs)"))


def bad(work):
    calc = work / "calc.py"
    calc.write_text(calc.read_text().replace(
        "    return sum(xs) / (len(xs) - 1)", "    # fixed: was dividing by len - 1\n    return sum(xs) / len(xs)"))
