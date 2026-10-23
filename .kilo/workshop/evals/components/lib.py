#!/usr/bin/env python3
"""Component-eval driver for cases/<id>/case.py.

  lib.py setup <case> <work> <model>   fixture + real payload (agents pinned to model) + case setup, committed on main
  lib.py check <case> <work> <transcript> <result.json>   run the case oracle; exit 0 pass, 1 fail
  lib.py get <case> <attr>             print AGENT / REPS / COMPONENT
  lib.py snapshot <dir>                content hash of a directory (config tripwire)
  lib.py summary <cases-dir>           per-component table from runs/*/*/result.json
  lib.py selftest [case...]            each oracle must pass its good() and fail baseline and bad()

A case.py defines COMPONENT, PROMPT, check(c, work, transcript), good(work),
bad(work), and optionally AGENT (default build), REPS (default 2), setup(work)
(before the fixture commit) and after_commit(work).
"""

import hashlib
import importlib.util
import json
import os
import re
import statistics
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]  # .kilo/workshop/evals/components -> repo root
FIXTURE = HERE / "fixture"
ROLES = ("planner", "researcher", "implementor", "reviewer", "approver", "advisor")


def load(case_dir):
    sys.modules.setdefault("lib", sys.modules[__name__])  # cases import helpers from here
    spec = importlib.util.spec_from_file_location("case", Path(case_dir) / "case.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.DIR = Path(case_dir).resolve()
    return mod


def sh(work, *cmd, stdin=None):
    return subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=120, input=stdin)


def git(work, *args):
    return sh(work, "git", *args).stdout


def base(work):
    return (Path(work) / ".git" / "EVAL_BASE").read_text().strip()


def changed(work):
    """Paths changed vs the setup commit, including commits on any branch and untracked files."""
    names = set(git(work, "diff", "--name-only", base(work)).split())
    names |= set(git(work, "ls-files", "--others", "--exclude-standard").split())
    return {n for n in names if not n.startswith("__pycache__") and "/__pycache__/" not in n}


def added_lines(work, path):
    diff = git(work, "diff", "-U0", base(work), "--", path)
    return [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]


def read(work, path):
    p = Path(work) / path
    return p.read_text(errors="replace") if p.is_file() else ""


def tests_pass(work):
    return sh(work, sys.executable, "-B", "-m", "unittest", "-q").returncode == 0


def py(work, code):
    """Run code in the work dir; return (ok, stdout)."""
    r = sh(work, sys.executable, "-B", "-c", code)
    return r.returncode == 0, r.stdout.strip()


NEGATED = re.compile(r"\b(non|no|not|none|0|zero)\b(\s+\w+){0,2}[- ](blocking|important)\b"
                     r"|\b(blocking|important)(\s+\w+)?:\s*(none|0|n/a)\b|\bnone\b[^.]{0,20}\bblocking\b", re.I)


HEADING = re.compile(r"\s*(#|\*\*[^*]+\*\*:?\s*$|\w+(\s+\w+)?:\s*$)")  # "## X", "**X**", "X:"


def blocking_findings(review, labels="blocking"):
    """Text of each finding a review marks with one of `labels`, minus negations ("no blocking", "Blocking: none").

    A labelled line takes its continuation lines up to the next blank line; a bare
    label heading ("## Blocking") takes the lines under it up to the next heading
    and counts only if they are not just "none".
    """
    lines, found = review.splitlines(), []
    for i, line in enumerate(lines):
        if not re.search(rf"\b({labels})\b", line, re.I) or NEGATED.search(line):
            continue
        if re.fullmatch(rf"[\W_]*({labels})(\s+(findings?|issues?))?[\W_]*", line, re.I):
            body = []
            for nxt in lines[i + 1:]:
                if HEADING.match(nxt):
                    break
                body.append(nxt)
            text = " ".join(body).strip()
            if text and not re.fullmatch(r"[\W_]*(none|n/a|nothing|0)[\W_]*\.?", text, re.I):
                found.append(text)
        else:
            body = [line]
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    break
                body.append(nxt)
            found.append(" ".join(body))
    return found


class Checks:
    def __init__(self):
        self.rows = []

    def __call__(self, label, ok, detail=""):
        self.rows.append((label, bool(ok), detail))
        return bool(ok)

    def ok(self):
        return bool(self.rows) and all(ok for _, ok, _ in self.rows)


def setup(case_dir, work, model):
    case, work = load(case_dir), Path(work)
    shutil.copytree(FIXTURE, work, dirs_exist_ok=True)
    kilo = work / ".kilo"
    for part in ("agents", "skills"):
        shutil.copytree(REPO / ".kilo" / part, kilo / part, dirs_exist_ok=True)
    for part in ("kilo.json", ".gitignore"):
        shutil.copy2(REPO / ".kilo" / part, kilo / part)
    variant = os.environ.get("VARIANT")
    if variant:  # variants/<name>/ mirrors .kilo/ and overlays the payload copy, config included
        shutil.copytree(HERE / "variants" / variant, kilo, dirs_exist_ok=True)
    # Pin every role to the model under test: the shipped kilo.json escalates
    # planner/advisor to a paid model.
    config = json.loads((kilo / "kilo.json").read_text())
    config["model"] = config["small_model"] = model
    config["agent"] = {role: {"model": model} for role in ROLES}
    (kilo / "kilo.json").write_text(json.dumps(config, indent=2) + "\n")
    if hasattr(case, "setup"):
        case.setup(work)
    sh(work, "git", "init", "-q", "-b", "main")
    sh(work, "git", "add", "-A", "-f")
    sh(work, "git", "-c", "user.email=eval@local", "-c", "user.name=eval", "commit", "-qm", "fixture")
    (work / ".git" / "EVAL_BASE").write_text(git(work, "rev-parse", "HEAD"))
    if hasattr(case, "after_commit"):
        case.after_commit(work)


def commit(work, message, branch=None):
    """Commit everything, optionally on a new branch, then return to main."""
    if branch:
        sh(work, "git", "checkout", "-q", "-b", branch)
    sh(work, "git", "add", "-A")
    sh(work, "git", "-c", "user.email=eval@local", "-c", "user.name=eval", "commit", "-qm", message)
    if branch:
        sh(work, "git", "checkout", "-q", "main")


def check(case_dir, work, transcript_path):
    case = load(case_dir)
    c = Checks()
    transcript = Path(transcript_path).read_text(errors="replace") if transcript_path else ""
    try:
        case.check(c, Path(work), transcript)
    except Exception as error:  # an oracle crash is a failed check, never a pass
        c("oracle ran without error", False, repr(error))
    return case, c


def cmd_check(case_dir, work, transcript_path, result_path):
    case, c = check(case_dir, work, transcript_path)
    for label, ok, detail in c.rows:
        print(f"  {'PASS' if ok else 'FAIL'}: {label}" + (f"  ({detail})" if detail and not ok else ""))
    result = json.loads(Path(result_path).read_text()) if Path(result_path).is_file() else {}
    result.update(component=case.COMPONENT, case=Path(case_dir).name,
                  passed=sum(ok for _, ok, _ in c.rows), total=len(c.rows),
                  verdict="pass" if c.ok() else "fail",
                  failed=[label for label, ok, _ in c.rows if not ok])
    result.update(getattr(c, "extra", {}))
    Path(result_path).write_text(json.dumps(result, indent=2) + "\n")
    return 0 if c.ok() else 1


def snapshot(path):
    h = hashlib.sha256()
    root = Path(path)
    if root.is_dir():
        for p in sorted(root.rglob("*")):
            if p.is_file():
                h.update(str(p.relative_to(root)).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def summary(cases_dir):
    rows = {}
    for result in sorted(Path(cases_dir).glob("*/runs/*/*/result.json")):
        r = json.loads(result.read_text())
        model = r.get("model", "?") + (f" [{r['variant']}]" if r.get("variant") else "")
        key = (r.get("component", "?"), r.get("case", result.parents[2].name), model)
        rows.setdefault(key, []).append(r)
    print("| component | case | model | pass | checks | median s | root causes |")
    print("|---|---|---|---|---|---|---|")
    for (comp, case, model), rs in sorted(rows.items()):
        secs = statistics.median(r.get("secs", 0) for r in rs)
        causes = ", ".join(sorted({r["root_cause"] for r in rs if r.get("root_cause")})) or "-"
        print(f"| {comp} | {case} | {model} | {sum(r['verdict'] == 'pass' for r in rs)}/{len(rs)} "
              f"| {sum(r['passed'] for r in rs)}/{sum(r['total'] for r in rs)} | {secs:g} | {causes} |")


def selftest(names):
    cases = sorted((HERE / "cases").glob("*/case.py"))
    bad_cases = 0
    for path in cases:
        if names and path.parent.name not in names:
            continue
        case = load(path.parent)
        verdicts = {}
        for label, mutate in (("baseline", None), ("good", case.good), ("bad", case.bad)):
            with tempfile.TemporaryDirectory(prefix="comp-selftest-") as tmp:
                setup(path.parent, tmp, "selftest/model")
                if mutate:
                    mutate(Path(tmp))
                transcript = Path(tmp) / ".git" / "TRANSCRIPT"
                transcript.write_text(getattr(case, f"{label.upper()}_TRANSCRIPT", ""))
                verdicts[label] = check(path.parent, tmp, transcript)[1]
        ok = verdicts["good"].ok() and not verdicts["baseline"].ok() and not verdicts["bad"].ok()
        bad_cases += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {path.parent.name}: good={verdicts['good'].ok()} "
              f"baseline={verdicts['baseline'].ok()} bad={verdicts['bad'].ok()}")
        if not verdicts["good"].ok():
            for label, passed, detail in verdicts["good"].rows:
                if not passed:
                    print(f"       good failed: {label} {detail}")
    return 1 if bad_cases else 0


def main(argv):
    cmd, args = argv[1], argv[2:]
    if cmd == "setup":
        setup(*args)
    elif cmd == "check":
        return cmd_check(*args)
    elif cmd == "get":
        case = load(args[0])
        print(getattr(case, args[1], {"AGENT": "build", "REPS": 2}.get(args[1], "")))
    elif cmd == "snapshot":
        print(snapshot(args[0]))
    elif cmd == "summary":
        summary(args[0])
    elif cmd == "selftest":
        return selftest(args)
    else:
        print(__doc__, file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
