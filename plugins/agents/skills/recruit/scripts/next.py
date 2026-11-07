#!/usr/bin/env python3
"""Print the next recruit stage for .minime/<agent>/. Bookkeeping, not a security boundary.

`next.py <agent>` prints the stage.
`next.py <agent> --digest` prints the value proof.json records as "digest".
`next.py <agent> --hash <path>` prints a hash for a review or chart record: the
sha256 of a file, or for a chart folder the hash of its .tla and .cfg files.

State the router reads is JSON. Anything malformed, stale or missing counts as
not done, and git errors fail closed.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REVIEWED = ("brief", "role", "routines")
PLACES = {"host", "script", "prompt"}
GUARD_ID = re.compile(r"G[1-9][0-9]*")


def text(path):
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def load(path):
    """A JSON object, or None if the file is missing or malformed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def model_hash(folder):
    h = hashlib.sha256()
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix in (".tla", ".cfg"))
    if not files:
        return None
    for path in files:
        h.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def clear(work, stage):
    """Done when the artifact has no [TK] and its review record is clear for this exact artifact and findings file."""
    doc, findings = work / f"{stage}.md", work / f"{stage}-review.md"
    review = load(work / f"{stage}-review.json")
    if not text(doc) or "[TK]" in text(doc) or review is None:
        return False
    if not text(findings) or text(findings).startswith("review: incomplete"):
        return False
    return (review.get("status") == "clear" and review.get("artifact") == sha(doc)
            and review.get("findings") == sha(findings))


def routines(work):
    return re.findall(r"^## (R[1-9][0-9]*)\s*$", text(work / "routines.md"), re.M)


def guards(work, routine):
    """Guard IDs from charts/<routine>/chart.json, or None unless every guard is placed, uniquely named and the check is current."""
    folder = work / "charts" / routine
    chart = load(folder / "chart.json")
    if chart is None or "No error has been found" not in text(folder / "gated.out"):
        return None
    model = model_hash(folder)
    if model is None or chart.get("model") != model or chart.get("gated") != sha(folder / "gated.out"):
        return None
    rows = chart.get("guards")
    if not isinstance(rows, list) or not rows or not all(isinstance(g, dict) for g in rows):
        return None
    ids = [g.get("id") for g in rows]
    if not all(isinstance(i, str) and GUARD_ID.fullmatch(i) for i in ids) or len(set(ids)) != len(ids):
        return None
    if not all(isinstance(g.get("place"), str) and g["place"] in PLACES for g in rows):
        return None
    return ids


def git(*args):
    """Git output, or None on any failure (fail closed)."""
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def digest(work):
    """Committed tree plus every recruit artifact except proof.json; None if the worktree is dirty or git fails."""
    status, tree = git("status", "--porcelain"), git("rev-parse", "HEAD^{tree}")
    if status is None or status.strip() or not tree:
        return None
    h = hashlib.sha256(tree.strip().encode())
    for path in sorted(p for p in work.rglob("*") if p.is_file() and p.name != "proof.json"):
        h.update(str(path.relative_to(work)).encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def proved(work, names):
    """Every row passes, row IDs are unique, and every guard has a fire and a clean row, at the current digest."""
    proof, current = load(work / "proof.json"), digest(work)
    if proof is None or not current or proof.get("digest") != current:
        return False
    rows = proof.get("rows")
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        return False
    ids = [r.get("id") for r in rows]
    if not all(isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
        return False
    if not all(r.get("result") == "pass" for r in rows):  # fail, unproven or anything else blocks
        return False
    needed = {f"{r} {g} {k}" for r in names for g in guards(work, r) for k in ("fire", "clean")}
    return needed <= set(ids)


def next_stage(work):
    for stage in REVIEWED:
        if not clear(work, stage):
            return stage
    names = routines(work)
    if not names:
        return "routines"
    missing = [r for r in names if guards(work, r) is None]
    if missing:
        return "chart " + " ".join(missing)
    return "land" if proved(work, names) else "trial"


def main():
    args = sys.argv[1:]
    if not (len(args) == 1 or args[1:] == ["--digest"] or (len(args) == 3 and args[1] == "--hash")):
        sys.exit("usage: next.py <agent> [--digest | --hash <path>]")
    work = Path(".minime") / args[0]
    if not work.is_dir():
        sys.exit(f"missing {work}/; run recruit section 1 first")
    if args[1:] == ["--digest"]:
        print(digest(work) or sys.exit("worktree is dirty or git failed; commit or stash before proving"))
    elif args[1:2] == ["--hash"]:
        target = work / args[2]
        print((model_hash(target) if target.is_dir() else sha(target)) or sys.exit(f"nothing to hash at {target}"))
    else:
        print(next_stage(work))


if __name__ == "__main__":
    main()
