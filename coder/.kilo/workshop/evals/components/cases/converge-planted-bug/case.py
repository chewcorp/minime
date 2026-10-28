"""converge review finds a planted bug and marks it blocking."""
import re

from lib import blocking_findings, changed, read

COMPONENT = "converge"
PROMPT = ("Run the kilo-mms converge review stage on the change in DIFF.patch (not yet applied). "
          "Write your findings to REVIEW.md, marking each one blocking or advisory. "
          "Do not edit or apply anything else.")
PATCH = '''--- a/calc.py
+++ b/calc.py
@@ -16,3 +16,7 @@ def normalize(s):
 
 def parse_date(s):
     return datetime.date.fromisoformat(s)
+
+
+def clamp(x, lo, hi):
+    return max(lo, min(x, lo))
'''


def setup(work):
    (work / "DIFF.patch").write_text(PATCH)


def check(c, work, transcript):
    review = read(work, "REVIEW.md")
    c("REVIEW.md written", bool(review.strip()))
    c("names the clamp bug (min against lo, not hi)", "clamp" in review and re.search(r"\bhi\b", review), review[:120])
    blocking = blocking_findings(review)
    c("marks the clamp bug blocking", any(re.search(r"\bhi\b", f) for f in blocking), blocking[:3])
    nits = [l for l in review.splitlines() if re.search(r"\bnit\b", l, re.I)]
    c("at most five nits", len(nits) <= 5, len(nits))
    c("edits nothing else", changed(work) <= {"REVIEW.md"}, sorted(changed(work)))


def good(work):
    (work / "REVIEW.md").write_text(
        "1. **Blocking**: clamp() returns max(lo, min(x, lo)), so it never exceeds lo; "
        "it should be min(x, hi). No test covers clamp.\n")


def bad(work):
    (work / "REVIEW.md").write_text("LGTM. Advisory: consider a docstring for clamp.\n")
