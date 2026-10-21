#!/usr/bin/env python3
"""Behavioral oracle for F8 self-copy tracer.

Executes a candidate install.sh into synthetic plugin/destination fixtures and
asserts: (a) self-install is a guarded no-op across --project, the --prefix
self-alias, a repo reached through a symlinked path (macOS-style /tmp), and
--force-config (round-3 hole), (b) distinct-destination install
copies all payload members, (c) recursive payload content survives. Exit 0 if
all assertions hold, 1 otherwise.

shortcut: the symlink leg invokes the installer by its physical path from a
symlinked cwd; a guard is also defeated when $0 itself is symlink-spelled
(e.g. invoked as ./install.sh through a symlinked dir, where `pwd` without -P
keeps the logical spelling). Current repo install.sh fails that form too —
out-of-scope hardening for this case, recorded in provenance.md.
"""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def write_fixture(root: Path):
    """Create a minimal plugin repo fixture at *root*."""
    (root / ".kilo" / "agents").mkdir(parents=True)
    (root / ".kilo" / "skills").mkdir(parents=True)
    (root / ".kilo" / "agents" / "a.md").write_text("agent-a\n")
    (root / ".kilo" / "agents" / "nested").mkdir()
    (root / ".kilo" / "agents" / "nested" / "deep.md").write_text("deep\n")
    (root / ".kilo" / "skills" / "b.md").write_text("skill-b\n")
    (root / ".kilo" / "kilo.json").write_text('{"pinned":true}\n')
    (root / ".kilo" / ".gitignore").write_text(".kilo/run/\n")
    (root / "plugin.json").write_text('{"version":"0.1.0"}\n')
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "fixture"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def snapshot(root: Path):
    """Map relative posix paths to file bytes for every file under *root*."""
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def run_installer(script: Path, cwd: Path, *extra_args: str):
    """Run *script* with bash from *cwd*; return the CompletedProcess."""
    env = os.environ.copy()
    env.pop("BASH_ENV", None)
    env.pop("ENV", None)
    return subprocess.run(
        ["bash", str(script), *extra_args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  {status}: {label}")
    if detail and not condition:
        print(f"        {detail}")
    return condition


def main(script_path: Path):
    if not script_path.is_file():
        print(f"error: candidate not found: {script_path}", file=sys.stderr)
        return 3

    ok = True
    with tempfile.TemporaryDirectory(prefix="f8-oracle-") as temp:
        temp_root = Path(temp)

        # --- (a) self-install is a guarded no-op, including via --prefix
        # pointing back at the source root, via --force-config (the round-3
        # hole: install_config's own cp self-copy), and via a repo reached
        # through a symlinked path (the macOS default: /tmp is a symlink, so
        # src_root and dest spell the same directory differently and a plain
        # string-compare guard misses it).
        self_repo = temp_root / "self"
        write_fixture(self_repo)
        target_script = self_repo / "install.sh"
        shutil.copy2(script_path, target_script)
        sym_link = temp_root / "self-symlink"
        os.symlink(self_repo, sym_link)
        for label, cwd, args in (
            ("--project", self_repo, ["--project"]),
            ("--prefix self/.", self_repo, ["--prefix", str(self_repo / ".kilo")]),
            ("--prefix self/. with trailing-slash dir spelling", self_repo, ["--prefix", str(self_repo) + "/.kilo/."]),
            ("--project via symlinked repo path", sym_link, ["--project"]),
            ("--project --force-config", self_repo, ["--project", "--force-config"]),
        ):
            before = snapshot(self_repo / ".kilo")
            result = run_installer(self_repo / "install.sh", cwd, *args)
            after = snapshot(self_repo / ".kilo")
            ok &= check(
                f"self-install {label} exits 0",
                result.returncode == 0,
                f"exit={result.returncode} stderr={result.stderr.strip()}",
            )
            ok &= check(
                f"self-install {label} leaves payload byte-for-byte unchanged",
                before == after,
                f"changed={[k for k in before if before.get(k) != after.get(k)]}",
            )

        # --- (b)+(c) distinct-destination install copies and works ---
        # The installer locates its payload relative to $0, so the candidate
        # must run from inside a source plugin fixture, targeting a separate
        # destination repo.
        src_repo = temp_root / "src"
        write_fixture(src_repo)
        src_script = src_repo / "install.sh"
        shutil.copy2(script_path, src_script)
        dest_repo = temp_root / "dest"
        dest_repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=dest_repo, check=True, capture_output=True)
        result = run_installer(src_script, dest_repo, "--project")
        ok &= check(
            "distinct-destination install exits 0",
            result.returncode == 0,
            f"exit={result.returncode} stderr={result.stderr.strip()}",
        )
        dest_kilo = dest_repo / ".kilo"
        expected = {
            "agents/a.md": "agent-a\n",
            "agents/nested/deep.md": "deep\n",
            "skills/b.md": "skill-b\n",
            "kilo.json": '{"pinned":true}\n',
            ".gitignore": ".kilo/run/\n",
        }
        for rel, content in expected.items():
            path = dest_kilo / rel
            ok &= check(
                f"distinct-destination copies {rel}",
                path.is_file() and path.read_text() == content,
                f"path={path} exists={path.is_file()} content={path.read_text() if path.is_file() else '<missing>'}",
            )

    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <candidate-install.sh>", file=sys.stderr)
        sys.exit(3)
    sys.exit(main(Path(sys.argv[1]).resolve()))
