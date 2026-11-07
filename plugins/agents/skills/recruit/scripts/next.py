#!/usr/bin/env python3
"""Print the next recruit stage for .minime/<agent>/. Bookkeeping, not a security boundary.

`next.py <agent>` prints the stage.
`next.py <agent> --digest` prints the value proof.json records as "digest".
`next.py <agent> --hash <path>` prints a hash for a chart record: the sha256 of
a file, or for a chart folder the hash of its .tla and .cfg files.
`next.py <agent> --upstream <R<n>>` prints the upstream hashes a chart record pins.
`next.py <agent> --pin <stage>` records, before reviewers start, the hashes of
everything upstream of a stage; `--clear <stage>` marks it clear for the stage's
current text and findings.
A record goes stale when anything it pinned changes.

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
ROUTINE = re.compile(r"R[1-9][0-9]*")
TEMPLATE = Path(__file__).resolve().parents[3] / "templates" / "wake"
RULES = ("NoDuplicateEffect", "NoAckOnlyReply", "BoundedWake", "NoStaleCharterAct",
         "OneActorPerItem", "ObserveOnly", "StopWins", "EndsRecorded")
UPSTREAM = {"brief": (), "role": ("brief.md",), "routines": ("brief.md", "role.md")}


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


def section(work, routine):
    """The text of `## <routine>` in routines.md, up to the next `## ` heading."""
    m = re.search(rf"^## {routine}\s*$.*?(?=^## |\Z)", text(work / "routines.md"), re.M | re.S)
    return m.group(0) if m else None


def upstream(work, name):
    """Hashes of what a stage or chart was built against; a chart pins its own routine's section only."""
    if name in UPSTREAM:
        return {f: sha(work / f) for f in UPSTREAM[name]}
    body = section(work, name)
    return {"brief.md": sha(work / "brief.md"), "role.md": sha(work / "role.md"),
            f"routines.md#{name}": hashlib.sha256(body.encode()).hexdigest() if body else None}


def reviewable(work, stage):
    findings = text(work / f"{stage}-review.md")
    return bool(findings) and not findings.startswith("review: incomplete")


def clear(work, stage):
    """Done when the artifact has no [TK] and its clear review record pins this artifact, its upstream and its findings."""
    doc, review = work / f"{stage}.md", load(work / f"{stage}-review.json")
    if not text(doc) or "[TK]" in text(doc) or review is None or not reviewable(work, stage):
        return False
    return (review.get("status") == "clear" and review.get("artifact") == sha(doc)
            and review.get("upstream") == upstream(work, stage)
            and review.get("findings") == sha(work / f"{stage}-review.md"))


def routines(work):
    return re.findall(r"^## (R[1-9][0-9]*)\s*$", text(work / "routines.md"), re.M)


def bare(path):
    """A TLA+ or TLC config file's lines with (* *) and \\* comments removed."""
    return [line.split("\\*")[0] for line in re.sub(r"\(\*.*?\*\)", " ", text(path), flags=re.S).splitlines()]


def definitions(path):
    """Each standard rule's definition in a .tla file, with indented continuation lines, whitespace stripped."""
    found, name = {}, None
    for body in bare(path):
        m = re.match(r"(\w+)\s*==(.*)", body)
        if m:
            name = m.group(1) if m.group(1) in RULES else None
            if name:
                found[name] = "\0" if name in found else ""  # a second definition is drift
            body = m.group(2)
        elif not body.strip():
            continue
        elif not body[:1].isspace():
            name = None
        if name:
            found[name] += "".join(body.split())
    return found


def checked(path):
    """Names a TLC config lists under INVARIANT or INVARIANTS."""
    names, listing = set(), False
    for token in re.findall(r"[A-Za-z_]\w*", "\n".join(bare(path))):
        if token.isupper():
            listing = token in ("INVARIANT", "INVARIANTS")
        elif listing:
            names.add(token)
    return names


def drifted(folder):
    """Standard rules the chart redefines or leaves out of gated.cfg; None if the template is unreadable."""
    want = definitions(TEMPLATE / "Wake.tla")
    if set(want) != set(RULES):
        return None
    have, listed = definitions(folder / "Wake.tla"), checked(folder / "gated.cfg")
    return {r for r in RULES if have.get(r) != want[r] or r not in listed}


def guards(work, routine):
    """Guard IDs from charts/<routine>/chart.json, or None unless every guard is placed, uniquely named, the check is current and every weakened standard rule has a ruling."""
    folder = work / "charts" / routine
    chart = load(folder / "chart.json")
    if chart is None or "No error has been found" not in text(folder / "gated.out"):
        return None
    model = model_hash(folder)
    if model is None or chart.get("model") != model or chart.get("gated") != sha(folder / "gated.out"):
        return None
    if chart.get("upstream") != upstream(work, routine):
        return None
    rulings, drift = chart.get("rulings", {}), drifted(folder)
    if drift is None or not isinstance(rulings, dict) or not all(
            isinstance(rulings.get(r), str) and rulings[r].strip() for r in drift):
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
        return "chart-duties " + " ".join(missing)
    return "land" if proved(work, names) else "trial"


def pin(work, stage):
    doc = work / f"{stage}.md"
    if not text(doc):
        sys.exit(f"nothing to review at {doc}")
    record = {"upstream": upstream(work, stage), "status": "pending"}
    (work / f"{stage}-review.json").write_text(json.dumps(record), encoding="utf-8")


def mark_clear(work, stage):
    path = work / f"{stage}-review.json"
    record = load(path)
    if record is None or record.get("status") != "pending":
        sys.exit(f"no pending pin at {path}; run --pin {stage} before the reviewers start")
    if not reviewable(work, stage):
        sys.exit(f"{stage}-review.md is missing or incomplete")
    # The artifact is hashed now, so fixes folded in from the findings count; upstream stays as pinned.
    record.update(status="clear", artifact=sha(work / f"{stage}.md"), findings=sha(work / f"{stage}-review.md"))
    path.write_text(json.dumps(record), encoding="utf-8")


def main():
    args = sys.argv[1:]
    flags = {"--hash", "--upstream", "--pin", "--clear"}
    if not (len(args) == 1 or args[1:] == ["--digest"] or (len(args) == 3 and args[1] in flags)):
        sys.exit("usage: next.py <agent> [--digest | --hash <path> | --upstream <R<n>> | --pin <stage> | --clear <stage>]")
    work = Path(".minime") / args[0]
    if not work.is_dir():
        sys.exit(f"missing {work}/; run recruit section 1 first")
    if args[1:2] in (["--pin"], ["--clear"]):
        if args[2] not in REVIEWED:
            sys.exit(f"--pin and --clear take one of {', '.join(REVIEWED)}")
        (pin if args[1] == "--pin" else mark_clear)(work, args[2])
    elif args[1:2] == ["--upstream"]:
        if not ROUTINE.fullmatch(args[2]) or section(work, args[2]) is None:
            sys.exit(f"no routine {args[2]} in routines.md")
        print(json.dumps(upstream(work, args[2])))
    elif args[1:] == ["--digest"]:
        print(digest(work) or sys.exit("worktree is dirty or git failed; commit or stash before proving"))
    elif args[1:2] == ["--hash"]:
        target = work / args[2]
        print((model_hash(target) if target.is_dir() else sha(target)) or sys.exit(f"nothing to hash at {target}"))
    else:
        print(next_stage(work))


if __name__ == "__main__":
    main()
