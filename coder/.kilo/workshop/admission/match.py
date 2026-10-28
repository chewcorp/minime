#!/usr/bin/env python3
"""Read applicable checks on stdin; emit case-insensitive Python regex matches."""

import json
from pathlib import Path
import re
import sys


def main():
    checks = json.load(sys.stdin)
    compiled = {}
    for name, check in checks.items():
        scope = check.get("scope", "line")
        if scope not in ("line", "document"):
            raise ValueError(f"invalid scope for {name!r}: {scope!r}")
        try:
            compiled[name] = (re.compile(check["pattern"], re.IGNORECASE), scope)
        except re.error as error:
            raise ValueError(f"invalid regex for {name!r}: {error}") from error
    text = Path(sys.argv[1]).read_bytes().decode("utf-8")
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    print(json.dumps({
        name: any(regex.search(part) is not None for part in
                  ([text] if scope == "document" else lines))
        for name, (regex, scope) in compiled.items()
    }))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"regex matcher: {error}", file=sys.stderr)
        sys.exit(3)
