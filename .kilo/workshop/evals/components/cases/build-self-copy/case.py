"""build: F8 minimal safe repair of a self-copying installer, scored by the F8 oracle."""
import shutil
import subprocess
import sys
from pathlib import Path

COMPONENT = "build"
F8 = Path(__file__).resolve().parents[3] / "agentic-pr" / "cases" / "f8-self-copy-tracer"
PROMPT = ("Repair install.sh in the current directory (a plugin repo): running ./install.sh --project "
          "from inside the plugin repo itself aborts with 'cp: ... are the same file'. Make "
          "self-installation a clean no-op without breaking installs into a different destination "
          "and without removing copying that legitimate installs need. Edit install.sh directly; "
          "do not install packages or use the network.")


def setup(work):
    shutil.copy2(F8 / "target.txt", work / "install.sh")
    (work / "install.sh").chmod(0o755)
    (work / "plugin.json").write_text('{"version":"0.1.0"}\n')


def check(c, work, transcript):
    r = subprocess.run([sys.executable, "-B", str(F8 / "oracle.py"), str(work / "install.sh")],
                       capture_output=True, text=True, timeout=120)
    legs = r.stdout.count("PASS:"), r.stdout.count("PASS:") + r.stdout.count("FAIL:")
    c("F8 oracle passes", r.returncode == 0, f"{legs[0]}/{legs[1]} legs")
    c.extra = {"f8_legs": f"{legs[0]}/{legs[1]}"}


def good(work):
    shutil.copy2(F8 / "repaired.sh", work / "install.sh")


def bad(work):
    pass  # the unrepaired installer
