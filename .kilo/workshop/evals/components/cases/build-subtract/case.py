"""build makes the smallest complete diff: a function plus its test, nothing else."""
import re

from lib import added_lines, changed, py, read, tests_pass

COMPONENT = "build"
PROMPT = "Add a subtract(a, b) function to calc.py, with a test."


def check(c, work, transcript):
    ok, out = py(work, "import calc; print(calc.subtract(5, 3))")
    c("subtract works", ok and out in ("2", "2.0"), out)
    c("tests pass", tests_pass(work))
    c("a test asserts on subtract", re.search(r"assert\w*\(.*subtract\(", read(work, "test_calc.py")))
    c("touches only calc.py and test_calc.py", changed(work) <= {"calc.py", "test_calc.py"}, sorted(changed(work)))
    code = [l for l in added_lines(work, "calc.py") if l.strip()]
    c("calc.py grows by at most 6 non-blank lines", len(code) <= 6, len(code))


def good(work):
    (work / "calc.py").write_text(read(work, "calc.py") + "\n\ndef subtract(a, b):\n    return a - b\n")
    t = read(work, "test_calc.py").replace(
        "    def test_add(self):",
        "    def test_subtract(self):\n        self.assertEqual(calc.subtract(5, 3), 2)\n\n    def test_add(self):")
    (work / "test_calc.py").write_text(t)


def bad(work):
    good(work)
    (work / "config.json").write_text('{"subtract_mode": "strict"}\n')  # unasked option
