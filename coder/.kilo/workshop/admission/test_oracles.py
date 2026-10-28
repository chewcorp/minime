#!/usr/bin/env python3
"""Actual static admission runner proof; no models, publishing or case execution.

Only the fixed scripts below are executed for independent behavioral adjudication.
Set S01C_PROOF_DIR to retain every invocation, row, evidence and controlled trace.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid


ADMISSION = Path(__file__).resolve().parent
WORKSHOP = ADMISSION.parent
SEEDS = WORKSHOP / "evals/agentic-pr/cases"
RELEASE = "pilot-pr4-stub-gh-critical"
DOCS = "pilot-pr4-reorder-doc-drift"
COPY = "pilot-pr4-self-copy"
PUSH = 'git push origin main --follow-tags\n'
CREATE = 'gh release create "v$next" "$tarball" --title "kilo-mms $next"\n'
WRAPPED_CREATE = ('if ! ' + CREATE.rstrip() + '; then\n'
                  '  echo "release failed" >&2\n  exit 1\nfi\n')
COPY_SETUP = '''#!/usr/bin/env bash
set -euo pipefail
src_root=$(cd "$(dirname "$0")/.kilo" && pwd)
dest="$target_repo/.kilo"
mkdir -p "$dest"
'''
GUARD = '''if [ "$src_root" -ef "$dest" ]; then
  exit 0
fi
'''
COPY_LOOP = '''for d in agents skills; do
  cp -R "$src_root/$d/." "$dest/$d/"
done
'''


class OracleProof(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="s01c actual runner ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.case = self.root / ("case-" + uuid.uuid4().hex)
        self.case.mkdir()
        self.rows = self.root / "results.jsonl"
        self.history = b'{"historical":"unchanged"}\n'
        self.rows.write_bytes(self.history)
        self.env = os.environ.copy()
        for key in ("BASH_ENV", "ENV"):
            self.env.pop(key, None)
        self.archive = None
        if os.environ.get("S01C_PROOF_DIR"):
            self.archive = Path(os.environ["S01C_PROOF_DIR"]) / self.id().split(".")[-1]
            self.archive.mkdir(parents=True, exist_ok=True)
        self.sequence = 0

    def retain(self, name, text):
        if self.archive:
            (self.archive / name).write_text(text, encoding="utf-8")

    def evidence_paths(self):
        return set(Path("/tmp/kilo-workshop-proof").glob(self.case.name + "-*-proof.txt"))

    def run_case(self, checks, target, expected, verdicts=None, extra=(), results=None):
        self.sequence += 1
        label = f"{self.sequence:03d}"
        checks_text = json.dumps(checks) if not isinstance(checks, str) else checks
        (self.case / "checks.json").write_text(checks_text)
        (self.case / "target.txt").write_text(target)
        rows = results or self.rows
        before = self.rows.read_bytes()
        proofs_before = self.evidence_paths()
        command = ["bash", str(ADMISSION / "run.sh"), "--results", str(rows),
                   "--model", "static-proof", "--provider", "local-no-model",
                   *extra, str(self.case), "converge"]
        result = subprocess.run(command, env=self.env, capture_output=True,
                                text=True, timeout=15)
        self.retain(label + "-invocation.json", json.dumps({
            "command": command, "exit": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "checks": checks_text, "target": target,
        }, indent=2))
        detail = f"{command!r}\n{result.stdout}\n{result.stderr}"
        self.assertEqual(result.returncode, expected, detail)
        proofs_after = self.evidence_paths()
        for path in proofs_after - proofs_before:
            self.addCleanup(path.unlink, missing_ok=True)
        if expected >= 3:
            self.assertEqual(self.rows.read_bytes(), before, detail)
            self.assertEqual(proofs_after, proofs_before, detail)
            self.assertNotIn("evidence=", result.stdout, detail)
            return result
        content = self.rows.read_bytes()
        self.assertTrue(content.startswith(before), detail)
        added = content[len(before):].splitlines()
        self.assertEqual(len(added), 1, detail)
        row = json.loads(added[0])
        self.assertEqual(set(row), {"task", "skill", "model", "provider", "component",
                                   "tokens", "wall_ms", "verdict", "verdicts", "evidence", "ts"})
        self.assertEqual(row["verdict"], {0: "pass", 1: "fail", 2: "unproven"}[expected])
        self.assertEqual(row["verdicts"], verdicts, detail)
        self.assertEqual(row["task"], str(self.case))
        self.assertEqual(row["skill"], "converge")
        self.assertEqual(row["model"], "static-proof")
        self.assertEqual(row["provider"], "local-no-model")
        self.assertEqual(row["component"], "full")
        self.assertEqual(row["tokens"], -1)
        self.assertIs(type(row["wall_ms"]), int)
        self.assertGreaterEqual(row["wall_ms"], 0)
        self.assertRegex(row["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        evidence = Path(row["evidence"])
        self.assertEqual(proofs_after - proofs_before, {evidence}, detail)
        proof = evidence.read_text()
        self.assertIn(f'verdict: {row["verdict"]}', proof)
        self.assertIn("rerun:", proof)
        for name, verdict in verdicts.items():
            self.assertIn(f"  {name}: {verdict}", proof)
        self.retain(label + "-row.json", json.dumps(row, indent=2))
        self.retain(label + "-evidence.txt", proof)
        return row

    def seed(self, name):
        return json.loads((SEEDS / name / "checks.json").read_text())

    def release_verdicts(self, order="pass", operations="pass", stub="pass"):
        return {"order-push-before-release": order,
                "release-operations-present": operations, "stub-used-as-proof": stub}

    def test_known_bad_targets(self):
        expected = {
            RELEASE: self.release_verdicts(order="fail", stub="fail"),
            DOCS: {"stale-order-phrase": "fail", "fixed-order-phrase": "fail"},
            COPY: {"identity-guard-before-copy": "fail", "cp-recursive-present": "pass"},
        }
        for name, verdicts in expected.items():
            with self.subTest(seed=name):
                self.run_case(self.seed(name), (SEEDS / name / "target.txt").read_text(), 1, verdicts)

    def release_trace(self, operations):
        # Allowlisted constants ONLY. Never execute the target or any case input.
        allowed = {"push": PUSH, "create": CREATE, "wrapped-create": WRAPPED_CREATE}
        script = '''set -euo pipefail
next=1.2.3
tarball=payload.tar.gz
git() { printf 'git:%s\\n' "$*"; }
gh() { printf 'gh:%s\\n' "$*"; }
''' + "".join(allowed[operation] for operation in operations)
        result = subprocess.run(["bash", "-c", script], env=self.env,
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.retain("trace-" + "-".join(operations) + ".txt", result.stdout)
        return result.stdout.splitlines()

    def test_release_actual_order_despite_lying_or_missing_comments(self):
        for create in ("create", "wrapped-create"):
            create_text = CREATE if create == "create" else WRAPPED_CREATE
            for ordered in (False, True):
                operations = ("push", create) if ordered else (create, "push")
                trace = self.release_trace(operations)
                # Independent expected trace, not generated by the regex matcher.
                wanted = ["git:push origin main --follow-tags",
                          "gh:release create v1.2.3 payload.tar.gz --title kilo-mms 1.2.3"]
                self.assertEqual(trace, wanted if ordered else wanted[::-1])
                body = PUSH + create_text if ordered else create_text + PUSH
                for marker in ("", "# ORDER: tag-push-then-gh-release\n",
                               "# ORDER: gh-release-then-tag-push\n"):
                    with self.subTest(create=create, ordered=ordered, marker=marker):
                        self.run_case(self.seed(RELEASE), marker + body, 0 if ordered else 1,
                                      self.release_verdicts(order="pass" if ordered else "fail"))

    def test_release_missing_operations_and_comment_only_commands(self):
        for target in ("", PUSH, CREATE, "# " + PUSH + "# " + CREATE):
            self.run_case(self.seed(RELEASE), target, 1,
                          self.release_verdicts(order="fail", operations="fail"))
        # Isolate the stub claim check: correctly ordered operations cannot hide it.
        self.run_case(self.seed(RELEASE), PUSH + CREATE + "# stubbed gh\n", 1,
                      self.release_verdicts(stub="fail"))

    def test_docs_natural_equivalents_and_retained_contradictions(self):
        # Independent language expectations fixed here, not inferred from matches.
        for good in ("It pushes, then creates the GitHub release.\n",
                     "It pushes,\nthen creates the GitHub\nrelease.\n",
                     "It pushes then creates the GitHub release.\n",
                     "Push first, then create the GitHub release.\n"):
            self.run_case(self.seed(DOCS), good, 0,
                          {"stale-order-phrase": "pass", "fixed-order-phrase": "pass"})
            for stale in ("release before push", "release\nbefore push",
                          "creates the GitHub release via `gh`, then pushes"):
                self.run_case(self.seed(DOCS), good + stale, 1,
                              {"stale-order-phrase": "fail", "fixed-order-phrase": "pass"})

    def install_behavior(self, guard_position, alias=False):
        # Trusted, hand-authored install variants, not case text or extracted code.
        bodies = {"guarded": GUARD + COPY_LOOP, "unguarded": COPY_LOOP,
                  "late": COPY_LOOP + GUARD, "disabled": "exit 0\n" + COPY_LOOP}
        root = self.root / ("install-" + uuid.uuid4().hex)
        source, destination = root / "source", root / "destination"
        source.mkdir(parents=True)
        destination.mkdir()
        for directory in ("agents", "skills"):
            payload = source / ".kilo" / directory
            payload.mkdir(parents=True)
            (payload / "sentinel.txt").write_text(directory + " payload\n")
        installer = source / "install.sh"
        installer.write_text(COPY_SETUP + bodies[guard_position])
        before = {str(p.relative_to(source)): p.read_bytes()
                  for p in source.rglob("*") if p.is_file()}
        results = []
        for mode, dest in (("self", str(source) + ("/." if alias else "")),
                           ("distinct", str(destination))):
            env = dict(self.env, target_repo=dest)
            result = subprocess.run(["bash", str(installer)], env=env,
                                    capture_output=True, text=True, timeout=5)
            if mode == "self":
                after = {str(p.relative_to(source)): p.read_bytes()
                         for p in source.rglob("*") if p.is_file()}
                self.assertEqual(after, before)
            copied = all((destination / ".kilo" / d / "sentinel.txt").is_file()
                         and (destination / ".kilo" / d / "sentinel.txt").read_text() == d + " payload\n"
                         for d in ("agents", "skills"))
            results.append({"mode": mode, "exit": result.returncode, "copied": copied,
                            "stdout": result.stdout, "stderr": result.stderr})
        self.retain(f"install-{guard_position}-alias-{alias}.json", json.dumps(results, indent=2))
        return results

    def test_selfcopy_real_self_and_distinct_install(self):
        for alias in (False, True):
            results = self.install_behavior("guarded", alias)
            self.assertEqual([r["exit"] for r in results], [0, 0])
            self.assertTrue(results[1]["copied"])
        self.run_case(self.seed(COPY), COPY_SETUP + GUARD + COPY_LOOP, 0,
                      {"identity-guard-before-copy": "pass", "cp-recursive-present": "pass"})
        for position, body in (("unguarded", COPY_LOOP), ("late", COPY_LOOP + GUARD)):
            results = self.install_behavior(position)
            self.assertNotEqual(results[0]["exit"], 0)
            self.assertEqual(results[1]["exit"], 0)
            self.assertTrue(results[1]["copied"])
            self.run_case(self.seed(COPY), COPY_SETUP + body, 1,
                          {"identity-guard-before-copy": "fail", "cp-recursive-present": "pass"})
        disabled = self.install_behavior("disabled")
        self.assertEqual([r["exit"] for r in disabled], [0, 0])
        self.assertFalse(disabled[1]["copied"])
        self.run_case(self.seed(COPY), COPY_SETUP + "exit 0\n" + COPY_LOOP, 1,
                      {"identity-guard-before-copy": "fail", "cp-recursive-present": "pass"})

    def test_selfcopy_missing_copy_and_commented_guard(self):
        self.run_case(self.seed(COPY), COPY_SETUP + GUARD, 1,
                      {"identity-guard-before-copy": "fail", "cp-recursive-present": "fail"})
        self.run_case(self.seed(COPY), COPY_SETUP + "# " + GUARD.replace("\n", "\n# ") + "\n" + COPY_LOOP, 1,
                      {"identity-guard-before-copy": "fail", "cp-recursive-present": "pass"})

    def test_existing_admission_cases_and_gating(self):
        for name in ("violation-1", "safe-neg-1", "unrelated-1"):
            case = ADMISSION / "cases" / name
            checks = json.loads((case / "checks.json").read_text())
            verdicts = {key: "pass" for key in checks if key != "skill"}
            self.run_case(checks, (case / "target.txt").read_text(), 0, verdicts)
            if "skill" in checks:
                self.run_case(checks, (case / "target.txt").read_text(), 2, {},
                              extra=("--gate-skill", "other"))
        checks = {"skill": "build", "required": {"pattern": "yes", "expect": "fail"}}
        self.run_case(checks, "yes", 0, {"required": "pass"}, extra=("--gate-skill", "build"))

    def test_line_default_document_opt_in_and_polarity(self):
        checks = {
            "default-no-cross": {"pattern": "alpha\\s+beta", "expect": "pass"},
            "explicit-line": {"pattern": "^beta$", "expect": "fail", "scope": "line"},
            "document-cross": {"pattern": "alpha\\s+beta", "expect": "fail", "scope": "document"},
            "document-anchors": {"pattern": "^beta$", "expect": "pass", "scope": "document"},
        }
        self.run_case(checks, "ALPHA\nbeta\n", 0, dict.fromkeys(checks, "pass"))
        self.run_case({"a": {"pattern": "^$", "expect": "pass"}}, "", 0, {"a": "pass"})
        self.run_case({"a": {"pattern": "yes", "expect": "pass"}}, "yes", 1, {"a": "fail"})
        self.run_case({"a": {"pattern": "no", "expect": "fail"}}, "yes", 1, {"a": "fail"})

    def test_invalid_applicable_patterns_scopes_and_shapes_no_writes(self):
        valid = {"pattern": "yes", "expect": "fail"}
        for bad in ({"pattern": "[", "expect": "pass"},
                    {"pattern": "(?|PCRE)", "expect": "fail"},
                    {**valid, "scope": "shell"}, {**valid, "scope": None},
                    {**valid, "scope": []}, {**valid, "pattern": 9},
                    {**valid, "expect": "anything"}, "not an object"):
            self.run_case({"a-valid-first": valid, "z-invalid-later": bad}, "yes", 3)
        for malformed in ("{not json", "[]", "null", '{"a": {"pattern":"yes"}}'):
            self.run_case(malformed, "yes", 3)
        # Gated-out malformed checks do not become applicable or get evaluated.
        self.run_case({"skill": "other", "bad": {"pattern": "[", "scope": "shell"}}, "yes", 2, {})
        self.run_case({}, "yes", 2, {})

    def test_io_failures_and_missing_args_no_verdict_or_evidence(self):
        self.run_case({"a": {"pattern": "x", "expect": "fail"}}, "x", 3,
                      results=self.root / "nonexistent-parent" / "results.jsonl")
        # Missing target and missing identity/arguments use the real entry point.
        (self.case / "target.txt").unlink()
        for args in ([], [str(self.case), "converge"],
                     ["--model", "m", "--provider", "p", str(self.case), "converge"],
                     ["--model"]):
            before = self.rows.read_bytes()
            before_proofs = self.evidence_paths()
            result = subprocess.run(["bash", str(ADMISSION / "run.sh"),
                                     "--results", str(self.rows), *args],
                                    env=self.env, capture_output=True, text=True, timeout=5)
            self.assertGreaterEqual(result.returncode, 3, result.stderr)
            self.assertEqual(self.rows.read_bytes(), before)
            self.assertEqual(self.evidence_paths(), before_proofs)
            self.retain("usage-" + str(len(args)) + ".txt", repr(args) + "\n" + result.stderr)

    def test_append_only_unique_evidence_and_untrusted_text_is_data(self):
        marker = self.root / "must-not-execute"
        target = f'$(touch "{marker}")\nexit 99\n'
        checks = {"text": {"pattern": "touch", "expect": "fail"}}
        first = self.run_case(checks, target, 0, {"text": "pass"})
        first_bytes = Path(first["evidence"]).read_bytes()
        second = self.run_case(checks, target, 0, {"text": "pass"})
        self.assertNotEqual(first["evidence"], second["evidence"])
        self.assertEqual(Path(first["evidence"]).read_bytes(), first_bytes)
        self.assertFalse(marker.exists())
        self.assertEqual(len(self.rows.read_bytes().splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
