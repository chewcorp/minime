#!/usr/bin/env python3
"""Sweep contract UNIT evidence only: fake runners, disposable static cases.

Run: python3 .kilo/workshop/ablations/test_sweeps.py -v
No model/provider calls and no real evaluator or seed-oracle proof.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parent


class SweepContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sweep unit evidence ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("ablations", "admission/cases/one", "hillclimb"):
            (self.root / name).mkdir(parents=True)
        for name in ("ablate.sh", "retire.sh"):
            shutil.copy2(SCRIPTS / name, self.root / "ablations" / name)
        self.panel = self.root / "ablations/panel.txt"
        self.panel.write_text("model:provider\n")
        self.log = self.root / "hillclimb/LOG.md"
        self.log.write_text("# Unit log\nProse [pending-human] does not block.\n")
        self.rows = self.root / "admission/results.jsonl"
        self.rows.write_text('{"historical":"preserve bytes"}\n')
        self.calls = self.root / "dispatches"
        self.checks = self.root / "admission/cases/one/checks.json"
        self.checks.write_text('{"skill":"converge"}\n')
        self.runner = self.root / "admission/run.sh"
        self.runner.write_text('''#!/usr/bin/env bash
# UNIT FAKE ONLY: records dispatch; never executes a model or evaluator.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
while [ "$1" != --component ]; do shift; done
component=$2
printf '%s\\n' "$component" >> "$root/dispatches"
if [ "$component" = full ]; then rc=${FULL_RC:-0}; else rc=${WITHOUT_RC:-0}; fi
if [ "$rc" -lt 3 ]; then
  printf '%s\\n' '{"unit_fake":true}' >> "$root/admission/results.jsonl"
fi
exit "$rc"
''')
        self.runner.chmod(0o755)
        self.glob = str(self.root / "admission/cases/*")

    def run_sweep(self, script, args, expected, calls=(), rows=0, env=None):
        before_log = self.log.read_bytes() if self.log.exists() else None
        before_rows = self.rows.read_bytes()
        self.calls.unlink(missing_ok=True)
        clean_env = os.environ.copy()
        for key in ("RETIRE_ARM_REAL", "FULL_RC", "WITHOUT_RC", "BASH_ENV", "ENV"):
            clean_env.pop(key, None)
        clean_env.update(env or {})
        result = subprocess.run(
            ["bash", str(self.root / "ablations" / script), *args],
            cwd=self.root, env=clean_env, capture_output=True, text=True,
            timeout=10,
        )
        detail = f"{script} {args!r}\nstdout={result.stdout}\nstderr={result.stderr}"
        self.assertEqual(result.returncode, expected, detail)
        actual_calls = self.calls.read_text().splitlines() if self.calls.exists() else []
        self.assertEqual(actual_calls, list(calls), detail)
        self.assertEqual(self.rows.read_bytes(), before_rows + b'{"unit_fake":true}\n' * rows, detail)
        self.assertEqual(self.log.read_bytes() if self.log.exists() else None, before_log, detail)
        if expected != 0:
            self.assertNotIn("smoke replay complete", result.stdout, detail)
        return result

    def test_usage_is_3_without_side_effects(self):
        for args in ([], [""], ["component", "model:provider"]):
            with self.subTest(script="ablate", args=args):
                self.run_sweep("ablate.sh", args, 3)
        for args in ([], ["rule"], ["", "converge"], ["rule", ""],
                     ["rule", "converge", "glob", "extra"]):
            with self.subTest(script="retire", args=args):
                self.run_sweep("retire.sh", args, 3)

    def test_entire_explicit_panel_validated_before_dispatch(self):
        for bad in ("", ":provider", "model:", "colonless"):
            for panel in ([bad], ["valid:provider", bad]):
                with self.subTest(panel=panel):
                    result = self.run_sweep("ablate.sh", ["component", self.glob, *panel], 3)
                    self.assertIn("panel entry must be model:provider", result.stderr)

    def test_entire_file_panel_validated_before_dispatch(self):
        for content in ("", "# only comments\n \n", ":provider\n", "model:\n",
                        "colonless\n", "valid:provider\n:provider\n",
                        "valid:provider\nmodel:\n", "valid:provider\ncolonless"):
            self.panel.write_text(content)
            for script, args in (("ablate.sh", ["component", self.glob]),
                                 ("retire.sh", ["rule", "converge", self.glob])):
                with self.subTest(script=script, panel=content):
                    result = self.run_sweep(script, args, 3)
                    message = "panel is empty" if content in ("", "# only comments\n \n") else "panel entry must be model:provider"
                    self.assertIn(message, result.stderr)

    def test_missing_panel_is_infrastructure_3(self):
        self.panel.unlink()
        self.run_sweep("ablate.sh", ["component", self.glob], 3)
        self.run_sweep("retire.sh", ["rule", "converge"], 3)

    def test_zero_cases_no_side_effects(self):
        empty = str(self.root / "missing/*")
        self.run_sweep("ablate.sh", ["component", empty], 3)
        self.run_sweep("retire.sh", ["rule", "converge", empty], 3)

    def test_retirement_disabled_for_all_overrides_and_arm_outcomes(self):
        for override in (None, "0", "1"):
            for full, without in ((0, 0), (0, 1), (0, 2), (2, 0), (3, 0), (0, 3)):
                env = {"FULL_RC": str(full), "WITHOUT_RC": str(without)}
                if override is not None:
                    env["RETIRE_ARM_REAL"] = override
                with self.subTest(override=override, full=full, without=without):
                    result = self.run_sweep("retire.sh", ["rule", "converge", self.glob], 3, env=env)
                    self.assertIn("retirement unsupported", result.stderr)

    def test_backlog_and_every_resolution_replace_heading_marker(self):
        heading = "### pending: retire `rule` from `converge` [pending-human]\n"
        self.log.write_text(heading)
        self.run_sweep("retire.sh", ["rule", "converge"], 1, env={"RETIRE_ARM_REAL": "1"})
        for marker in ("confirmed", "rejected", "deferred"):
            with self.subTest(marker=marker):
                self.log.write_text(heading + f"Resolution note [{marker}]\n")
                self.run_sweep("retire.sh", ["rule", "converge"], 1)
                self.log.write_text(heading.replace("[pending-human]", f"[{marker}]"))
                self.run_sweep("retire.sh", ["rule", "converge"], 3)

    def test_log_io_failure_is_3_not_backlog(self):
        self.log.unlink()
        self.run_sweep("retire.sh", ["rule", "converge"], 3)

    def test_grep_error_is_3_not_backlog_or_unsupported_success(self):
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        grep = bin_dir / "grep"
        grep.write_text("#!/bin/sh\n# UNIT infrastructure failure double\nexit 2\n")
        grep.chmod(0o755)
        self.run_sweep("retire.sh", ["rule", "converge"], 3,
                       env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]})

    @unittest.skipUnless(shutil.which("jq"), "jq missing: dispatch-path unit contracts unproven")
    def test_invalid_checks_fail_before_dispatch(self):
        self.checks.write_text("not json\n")
        self.run_sweep("ablate.sh", ["component", self.glob], 3)

    @unittest.skipUnless(shutil.which("jq"), "jq missing: dispatch-path unit contracts unproven")
    def test_arm_verdicts_unproven_and_runner_errors(self):
        for full in (1, 2, 3, 4, 127):
            with self.subTest(arm="full", rc=full):
                self.run_sweep("ablate.sh", ["component", self.glob], full,
                               calls=["full"], rows=int(full < 3), env={"FULL_RC": str(full)})
        for without in (1, 2, 3, 4, 127):
            with self.subTest(arm="without", rc=without):
                self.run_sweep("ablate.sh", ["component", self.glob], without,
                               calls=["full", "component"], rows=1 + int(without < 3),
                               env={"WITHOUT_RC": str(without)})

    def test_missing_or_nonexecutable_runner_is_infrastructure_3(self):
        self.runner.chmod(0o644)
        self.run_sweep("ablate.sh", ["component", self.glob], 3)
        self.runner.unlink()
        self.run_sweep("ablate.sh", ["component", self.glob], 3)

    @unittest.skipUnless(shutil.which("jq"), "jq missing: dispatch-path unit contracts unproven")
    def test_success_is_explicitly_non_admitting_smoke(self):
        # Also exercise a valid final panel line with no newline, comments/spaces,
        # and the existing positional/default-panel grammar.
        self.panel.write_text("# unit panel\n model : provider # comment")
        result = self.run_sweep("ablate.sh", ["component"], 0,
                                calls=["full", "component"], rows=2)
        self.assertIn("NON-ADMITTING SMOKE REPLAY", result.stdout)
        self.assertIn("no model execution or component removal", result.stdout)
        self.assertIn("rows cannot justify comparison, graduation or retirement", result.stdout)


if __name__ == "__main__":
    unittest.main()
