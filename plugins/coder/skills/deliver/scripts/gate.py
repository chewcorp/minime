#!/usr/bin/env python3
"""Portable delivery bookkeeping gates, not a security boundary for the agent."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


RESULTS = {"pass", "fail", "unproven"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.PIPE).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scope_token(value):
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def scope(work):
    acceptance = work / "acceptance.md"
    text = acceptance.read_text(encoding="utf-8")
    require("[TK]" not in text, "acceptance still has [TK] values")
    outcomes = re.findall(r"^\|\s*(O[1-9][0-9]*)\s*\|", text, re.MULTILINE)
    require(outcomes and len(outcomes) == len(set(outcomes)), "acceptance needs unique outcome table IDs")
    tickets = work / "tickets.md"
    if tickets.exists():
        headings = [line for line in tickets.read_text(encoding="utf-8").splitlines()
                    if line.lstrip().startswith("#")]
        require(headings, "tickets.md needs a ticket heading like '## T1'")
        require(all(re.fullmatch(r"## T[1-9][0-9]*", heading) for heading in headings),
                "tickets.md headings must be standalone '## T1' lines")
        ids = [heading[3:] for heading in headings]
        require(len(ids) == len(set(ids)), "tickets.md needs unique ticket headings")
        ids.sort()
    else:
        ids = ["T1"]
    return {"acceptance": digest(acceptance), "tickets": digest(tickets) if tickets.exists() else None}, outcomes, ids


def initial(work, rounds=0):
    fingerprints, outcomes, tickets = scope(work)
    return {"version": 1, "scope": fingerprints, "outcomes": outcomes,
            "tickets": dict.fromkeys(tickets, False), "rounds": rounds,
            "phase": "build", "tree": None, "evidence": {}}


def load(path):
    state = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(state, dict) and state.get("version") == 1, "invalid gate state version")
    require(type(state.get("rounds")) is int and state["rounds"] >= 0, "invalid round counter")
    require(state.get("phase") in {"build", "review", "repair"}, "invalid phase")
    require(isinstance(state.get("scope"), dict), "invalid scope")
    require(isinstance(state.get("outcomes"), list) and state["outcomes"], "invalid outcomes")
    require(isinstance(state.get("tickets"), dict) and state["tickets"]
            and all(type(v) is bool for v in state["tickets"].values()), "invalid tickets")
    require(isinstance(state.get("evidence"), dict), "invalid evidence")
    require(state.get("tree") is None or re.fullmatch(r"[0-9a-f]{40,64}", state["tree"]), "invalid tree")
    if "requester" in state:
        require(state["requester"] in {"bot", "human"}, "invalid requester")
    return state


@contextmanager
def locked(work):
    lock = work / "gate.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("gate lock exists; wait for its owner, or confirm it stopped before removing the lock") from None
    try:
        yield
    finally:
        lock.rmdir()


def save(path, state):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        name = stream.name
        json.dump(state, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def clean_tree():
    require(not git("status", "--porcelain", "--untracked-files=normal"), "a clean committed worktree is required")
    return git("rev-parse", "HEAD^{tree}")


def current(state, tree):
    require(state["phase"] == "review" and state["tree"] == tree,
            "missing current review; use the admitted repair path for content changes")


def required(state, approvals=True):
    keys = ["review:all"] + [f"independent:{o}" for o in state["outcomes"]]
    if approvals:
        keys += [f"approval:{o}" for o in state["outcomes"]]
    return keys


def evidence_passes(state, work, approvals=True):
    for key in required(state, approvals):
        row = state["evidence"].get(key)
        require(isinstance(row, dict), f"missing evidence: {key}")
        require(row.get("tree") == state["tree"] and row.get("result") == "pass", f"non-passing evidence: {key}")
        require(row.get("scope") == scope_token(state["scope"]), f"non-current scope evidence: {key}")
        report = (work / row["report"]).resolve()
        require(report.is_relative_to(work.resolve()) and report.is_file(), f"missing report: {key}")
        require(digest(report) == row["digest"], f"changed report: {key}; rerun and record its results")


def report_path(work, name):
    report = Path(name).resolve()
    require(report.is_relative_to(work.resolve()) and report.is_file() and report.stat().st_size > 0,
            "report must be a nonempty file inside the task folder")
    require(report.name != "gate.json", "gate state is not an evidence report")
    return report


def run(args, work):
    path = work / "gate.json"
    if args.command == "init":
        require(not path.exists(), "gate state already exists; never reset it to retry")
        legacy = work / "review-round"
        rounds = int(legacy.read_text().strip()) if legacy.exists() else 0
        require(rounds >= 0, "invalid legacy review-round; resolve with the human")
        state = initial(work, rounds)
        output = "initialized"
    else:
        state = load(path)
        if args.command == "scope":
            report_path(work, args.ruling)
            require(scope(work)[0] != state["scope"], "scope is unchanged")
            state = initial(work, state["rounds"])
            output = "scope accepted; repair counter preserved"
        else:
            fingerprints, outcomes, tickets = scope(work)
            require(fingerprints == state["scope"] and outcomes == state["outcomes"]
                    and set(tickets) == set(state["tickets"]), "accepted scope changed; stop for a human ruling")
            output = advance(args, work, state)
    if args.command not in {"next", "ready"}:
        save(path, state)
    return output


def repair_label(state):
    if state.get("requester") == "human":
        return "human repair"
    return f"repair round {state['rounds']}"


def advance(args, work, state):
    command = args.command
    if command == "done":
        require(args.ticket in state["tickets"], "unknown ticket")
        if state["phase"] == "repair":
            clean_tree()
            state["phase"] = "build"
        state["tickets"][args.ticket] = True
        return f"done {args.ticket}"
    if command == "next" and (not all(state["tickets"].values()) or state["phase"] in {"build", "repair"}):
        return "build" if not all(state["tickets"].values()) or state["phase"] == "repair" else "converge"
    if command == "fix":
        require(args.reason.strip(), "a verified blocker reason is required")
        if state["phase"] == "repair":
            return repair_label(state)
        tree = clean_tree()
        require(state["phase"] == "review", "review must start before repair admission")
        require(state["tree"] == tree, "content changed before repair admission; stop for human triage")
        if args.by == "human":
            state.update(phase="repair", evidence={}, requester="human")
        else:
            cap = os.environ.get("MINIME_BOT_REPAIR_CAP", "3")
            require(re.fullmatch(r"[0-9]+", cap), "MINIME_BOT_REPAIR_CAP must be a non-negative integer")
            require(state["rounds"] < int(cap), f"repair cap reached ({cap}); hand unresolved blocker to human")
            state.update(phase="repair", rounds=state["rounds"] + 1, evidence={}, requester="bot")
        state["reason"] = args.reason
        return repair_label(state)
    tree = clean_tree()
    if command == "review":
        require(all(state["tickets"].values()), "unfinished tickets; continue build")
        if state["phase"] == "review":
            require(state["tree"] == tree, "content changed without repair admission; stop and triage")
        else:
            state.update(phase="review", tree=tree, evidence={})
        return f"review {scope_token(state['scope'])} {tree}"
    if command == "next":
        try:
            current(state, tree)
            evidence_passes(state, work)
        except (ValueError, OSError, KeyError, TypeError):
            return "converge"
        return "land-learn"
    current(state, tree)
    if command == "record":
        require(args.scope == scope_token(state["scope"]), "evidence scope differs from the captured review; rerun the check")
        require(args.tree == tree, "evidence tree differs from current tree; rerun the check")
        require(args.outcome == "all" if args.kind == "review" else args.outcome in state["outcomes"], "unknown evidence outcome")
        if args.kind == "approval" and args.result == "pass":
            evidence_passes(state, work, approvals=False)
        report = report_path(work, args.report)
        if args.kind != "approval":
            for key in required(state):
                if key.startswith("approval:"):
                    state["evidence"].pop(key, None)
        state["evidence"][f"{args.kind}:{args.outcome}"] = {
            "scope": args.scope, "tree": tree, "result": args.result,
            "report": str(report.relative_to(work.resolve())), "digest": digest(report)}
        return f"recorded {args.kind}:{args.outcome} {args.result}"
    evidence_passes(state, work)
    return "merge-ready"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", help="current task branch, in kebab-case")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "review", "ready", "next"):
        commands.add_parser(name)
    commands.add_parser("done").add_argument("ticket")
    fix = commands.add_parser("fix")
    fix.add_argument("reason")
    fix.add_argument("--by", choices=("bot", "human"), default="bot")
    commands.add_parser("scope").add_argument("--ruling", required=True)
    record = commands.add_parser("record")
    record.add_argument("kind", choices=("review", "independent", "approval"))
    record.add_argument("outcome")
    record.add_argument("result", choices=sorted(RESULTS))
    record.add_argument("--tree", required=True, help="tree captured BEFORE running the check")
    record.add_argument("--scope", required=True, help="scope token captured BEFORE running the check")
    record.add_argument("--report", required=True, help="completed immutable report in the task folder")
    args = parser.parse_args()
    try:
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.task), "task must be kebab-case")
        root = Path(git("rev-parse", "--show-toplevel"))
        os.chdir(root)
        require(git("branch", "--show-current") == args.task and args.task not in {"main", "master"}, "switch to the task branch first")
        default = subprocess.run(["git", "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], text=True, capture_output=True)
        require(default.stdout.strip() != f"refs/remotes/origin/{args.task}", "the default branch cannot be a task branch")
        work = root / ".minime" / args.task
        require(work.resolve().is_relative_to(root.resolve()) and work.is_dir(), "task folder must exist inside the repository")
        with locked(work):
            print(run(args, work))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"gate: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
