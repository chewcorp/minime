"""deliver routes a finished, tested diff to converge."""
from lib import changed, commit, read

COMPONENT = "deliver"
PROMPT = ("Use the kilo-mms delivery loop (the deliver skill) to route this, then stop: the subtract() "
          "change on branch feat/subtract is implemented and its tests pass; it has not been reviewed. "
          "Write only the name of the stage you route it to, one lowercase word, into ROUTE.txt. "
          "Change no other file and do not switch branches.")


def after_commit(work):
    calc = work / "calc.py"
    calc.write_text(calc.read_text() + "\n\ndef subtract(a, b):\n    return a - b\n")
    commit(work, "add subtract", branch="feat/subtract")


def check(c, work, transcript):
    c("routes to converge", read(work, "ROUTE.txt").strip().lower() == "converge", read(work, "ROUTE.txt").strip())
    c("changes nothing else", changed(work) <= {"ROUTE.txt"}, sorted(changed(work)))


def good(work):
    (work / "ROUTE.txt").write_text("converge\n")


def bad(work):
    (work / "ROUTE.txt").write_text("build\n")
