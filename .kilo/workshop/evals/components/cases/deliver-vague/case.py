"""deliver routes a vague ask to clarify."""
from lib import changed, read

COMPONENT = "deliver"
PROMPT = ("Use the kilo-mms delivery loop (the deliver skill) to route this request, then stop: "
          "'make the calculator nicer to use'. Write only the name of the stage you route it to, "
          "one lowercase word, into ROUTE.txt. Change no other file.")


def check(c, work, transcript):
    c("routes to clarify", read(work, "ROUTE.txt").strip().lower() == "clarify", read(work, "ROUTE.txt").strip())
    c("changes nothing else", changed(work) <= {"ROUTE.txt"}, sorted(changed(work)))


def good(work):
    (work / "ROUTE.txt").write_text("clarify\n")


def bad(work):
    (work / "ROUTE.txt").write_text("build\n")
