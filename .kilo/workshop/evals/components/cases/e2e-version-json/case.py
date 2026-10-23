"""End-to-end tracer: two requirements through the whole loop, with root-cause attribution.

Each requirement is traced through every stage's artifact in loop order. Its root
cause is the first stage where it drops out, so a failure that surfaces at prove
but was never charted is blamed on chart, not prove.
"""
import json
import re

import sys

from lib import NEGATED, blocking_findings, git, read, sh, tests_pass

COMPONENT = "e2e"
REPS = 3
PROMPT = ("Use the kilo-mms delivery loop (the deliver skill) end to end for this request. Do not wait "
          "for me: where a stage needs a human answer, assume the most reasonable one and note it. Save "
          "each stage's output to .kilo/run/<task>/<stage>.md (clarify also writes acceptance.md). "
          "Stop before any merge to main.\n\nRequest: (1) `python3 cli.py --version` prints the contents "
          "of VERSION; (2) `python3 cli.py add 2 3 --json` prints {\"result\": 5.0}.")
STAGES = ("clarify", "chart", "build", "prove", "converge", "land-learn")
REQS = {
    "R1 --version": (r"version", r"--version", ("--version",), lambda out: out == "0.3.1", r"0\.3\.1"),
    "R2 add --json": (r"json", r"--json", ("add", "2", "3", "--json"),
                      lambda out: _json(out) == {"result": 5.0}, r'"result":\s*5\.0'),
}


def _json(out):
    try:
        return json.loads(out)
    except ValueError:
        return None


def _ids(acceptance, key):
    """Acceptance ids ("O1", "AC2") on the lines naming this requirement, so a review can cite them instead."""
    return {i for line in acceptance.splitlines() if re.search(key, line, re.I)
            for i in re.findall(r"\b[A-Z]{1,3}\d+\b", line)}


def _stage_text(work, stage):
    names = ("acceptance.md",) if stage == "clarify" else (f"{stage}.md",)
    if stage == "land-learn":
        names += ("handoff.md", "land.md")
    return "\n".join(p.read_text(errors="replace") for n in names for p in (work / ".kilo" / "run").glob(f"*/{n}"))


def _branch_diff(work):
    branches = [b.strip("* ").strip() for b in git(work, "branch", "--list").splitlines()]
    return "\n".join(git(work, "diff", "main", b) for b in branches if b and b != "main")


def check(c, work, transcript):
    main_untouched = git(work, "rev-parse", "main").strip() == (work / ".git" / "EVAL_BASE").read_text().strip()
    c("main untouched (merge stays human)", main_untouched)
    branch_diff = _branch_diff(work)
    tests = read(work, "test_calc.py") + "".join(p.read_text() for p in work.glob("test_*.py") if p.name != "test_calc.py")
    green = tests_pass(work)
    traces, root_causes = {}, []
    for req, (key, flag, argv, works, shown) in REQS.items():
        run = sh(work, sys.executable, "-B", "cli.py", *argv)  # the entry point, as the request asks
        ok, out = run.returncode == 0, run.stdout.strip()
        texts = {s: _stage_text(work, s) for s in ("clarify", "chart", "prove", "converge", "land-learn")}
        # a review that approves the whole diff ("approve", "merge-ready", "no blocking findings") covers every requirement in it
        approved = bool(re.search(r"\b(approve[ds]?|merge[- ]ready|lgtm)\b", texts["converge"], re.I)
                        or NEGATED.search(texts["converge"])) and not blocking_findings(texts["converge"])
        stage_ok = {
            "clarify": bool(re.search(key, texts["clarify"], re.I)),
            "chart": bool(re.search(key, texts["chart"], re.I)),
            "build": ok and works(out),
            # prove.md must cover the requirement; the evidence is a new test or the command run with its output
            "prove": green and bool(re.search(key, texts["prove"], re.I))
                     and (flag in tests or (flag in texts["prove"] and bool(re.search(shown, texts["prove"])))),
            "converge": approved or bool(re.search(key, texts["converge"], re.I))
                        or any(re.search(rf"\b{i}\b", texts["converge"]) for i in _ids(texts["clarify"], key)),
            "land-learn": flag in branch_diff and bool(texts["land-learn"].strip()),
        }
        traces[req] = stage_ok
        dropped = next((s for s in STAGES if not stage_ok[s]), None)
        c(f"{req}: traced through every stage", dropped is None, f"drops out at {dropped}")
        if dropped:
            root_causes.append(dropped)
    root = min(root_causes, key=STAGES.index) if root_causes else None
    c.extra = {"root_cause": root, "trace": traces,
               "stage_artifacts": {s: bool(_stage_text(work, s).strip()) for s in STAGES if s not in ("build", "prove")}}


GOOD_CLI = '''import argparse
import json
from pathlib import Path

import calc


def main(argv=None):
    parser = argparse.ArgumentParser(prog="calc")
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="cmd")
    add = sub.add_parser("add")
    add.add_argument("a", type=float)
    add.add_argument("b", type=float)
    add.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        print((Path(__file__).parent / "VERSION").read_text().strip())
    elif args.cmd == "add":
        result = calc.add(args.a, args.b)
        print(json.dumps({"result": result}) if args.json else result)


if __name__ == "__main__":
    main()
'''
GOOD_TEST = '''import contextlib
import io
import json
import unittest

import cli


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        cli.main(argv)
    return out.getvalue().strip()


class CliTest(unittest.TestCase):
    def test_version(self):
        self.assertEqual(run(["--version"]), "0.3.1")

    def test_add_json(self):
        self.assertEqual(json.loads(run(["add", "2", "3", "--json"])), {"result": 5.0})
'''


def _write_stages(work, chart="T1 --version flag; T2 add --json output, blocked by none"):
    run = work / ".kilo" / "run" / "cli-flags"
    run.mkdir(parents=True, exist_ok=True)
    (run / "acceptance.md").write_text("O1 --version prints VERSION\nO2 add --json prints result JSON\n")
    (run / "chart.md").write_text(chart + "\n")
    (run / "prove.md").write_text("$ python3 cli.py --version\n0.3.1\n$ python3 cli.py add 2 3 --json\n"
                                  '{"result": 5.0}\n$ python3 -m unittest -q\nOK\n')
    (run / "converge.md").write_text("O1 version: pass\nO2 json: pass\nReviewer: approve\n")
    (run / "land-learn.md").write_text("Handoff: branch feat/cli-flags ready for human merge.\n")


def good(work):
    from lib import commit
    _write_stages(work)
    (work / "cli.py").write_text(GOOD_CLI)
    (work / "test_cli.py").write_text(GOOD_TEST)
    commit(work, "cli: --version and add --json", branch="feat/cli-flags")
    # leave the branch checked out, as the loop would
    git(work, "checkout", "-q", "feat/cli-flags")


def bad(work):
    """Chart drops R2: --json never gets built, and the failure must be blamed on chart."""
    from lib import commit
    _write_stages(work, chart="T1 --version flag")
    (work / "cli.py").write_text(GOOD_CLI.replace('    add.add_argument("--json", action="store_true")\n', "")
                                 .replace('print(json.dumps({"result": result}) if args.json else result)', "print(result)"))
    (work / "test_cli.py").write_text(GOOD_TEST.split("    def test_add_json")[0])
    commit(work, "cli: --version", branch="feat/cli-flags")
    git(work, "checkout", "-q", "feat/cli-flags")
