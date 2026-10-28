"""converge review does not invent blocking findings on a clean diff."""
import re

from lib import blocking_findings, changed, read

COMPONENT = "converge"
PROMPT = ("Run the kilo-mms converge review stage on the change in DIFF.patch (not yet applied). "
          "Write your findings to REVIEW.md, marking each one blocking or advisory, or say there are none. "
          "Do not edit or apply anything else.")
PATCH = '''--- a/calc.py
+++ b/calc.py
@@ -16,3 +16,7 @@ def normalize(s):
 
 def parse_date(s):
     return datetime.date.fromisoformat(s)
+
+
+def square(x):
+    return x * x
--- a/test_calc.py
+++ b/test_calc.py
@@ -8,4 +8,7 @@ class CalcTest(unittest.TestCase):
     def test_add(self):
         self.assertEqual(calc.add(2, 3), 5)
 
+    def test_square(self):
+        self.assertEqual(calc.square(-3), 9)
+
     def test_mean(self):
'''


def setup(work):
    (work / "DIFF.patch").write_text(PATCH)


def check(c, work, transcript):
    review = read(work, "REVIEW.md")
    c("REVIEW.md written", bool(review.strip()))
    blocking = blocking_findings(review, "blocking|important")
    c("no blocking findings invented", not blocking, blocking[:3])
    nits = [l for l in review.splitlines() if re.search(r"\bnit\b", l, re.I)]
    c("at most five nits", len(nits) <= 5, len(nits))
    c("edits nothing else", changed(work) <= {"REVIEW.md"}, sorted(changed(work)))


def good(work):
    (work / "REVIEW.md").write_text("No blocking findings. Advisory: none. Approve.\n")


def bad(work):
    (work / "REVIEW.md").write_text("Blocking: square() lacks a docstring and type hints.\n")
