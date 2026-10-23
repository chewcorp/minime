"""deliver stays out of an ordinary request that never names the loop."""
from lib import changed, read

COMPONENT = "deliver"
PROMPT = "Fix the spelling mistake in the README.md heading."
LOOP_MARKS = ("Destination", "Out-of-scope", "acceptance.md", "ROUTE.txt")


def check(c, work, transcript):
    c("heading fixed", read(work, "README.md").startswith("# Calculator"), read(work, "README.md")[:20])
    c("only README.md changed", changed(work) == {"README.md"}, sorted(changed(work)))
    c("no loop state written", not (work / ".kilo" / "run").exists())
    c("no loop ceremony in transcript", not any(m in transcript for m in LOOP_MARKS))


def good(work):
    (work / "README.md").write_text(read(work, "README.md").replace("Calcualtor", "Calculator"))


def bad(work):
    good(work)
    (work / ".kilo" / "run" / "fix-readme").mkdir(parents=True)
    (work / ".kilo" / "run" / "fix-readme" / "acceptance.md").write_text("O1 heading spelled correctly\n")
