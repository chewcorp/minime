# F8 Self-Copy Tracer — Oracle Proof

Offline behavioral oracle verdicts. No model/provider calls, no instruction-arm
freeze, no live evaluation. Commands run inside this worktree on 2026-10-21;
transcripts refreshed after the oracle gained the `--prefix` self-alias and
`--force-config` self-install legs (PR #7 review).

## Known-bad target (expect reject)

```text
$ cd .kilo/workshop/evals/agentic-pr/cases/f8-self-copy-tracer
$ python3 oracle.py target.txt
  FAIL: self-install --project exits 0
        exit=1 stderr=note: .../self/.kilo exists; payload paths (agents/, skills/, kilo.json, .gitignore) will be overwritten, unrelated files untouched
cp: '.../self/.kilo/agents/.' and '.../self/.kilo/agents/.' are the same file
  PASS: self-install --project leaves payload byte-for-byte unchanged
  FAIL: self-install --prefix self/. exits 0
        exit=1 stderr=note: ...same file...
  PASS: self-install --prefix self/. leaves payload byte-for-byte unchanged
  FAIL: self-install --project --force-config exits 0
        exit=1 stderr=note: ...same file...
  PASS: self-install --project --force-config leaves payload byte-for-byte unchanged
  PASS: distinct-destination install exits 0
  PASS: distinct-destination copies agents/a.md
  PASS: distinct-destination copies agents/nested/deep.md
  PASS: distinct-destination copies skills/b.md
  PASS: distinct-destination copies kilo.json
  PASS: distinct-destination copies .gitignore
$ echo $?
1
```

The broken installer fails all five self-install spellings with the
historical `cp: ... are the same file` error; distinct-destination copying
still works, which matches the real failure mode (self-copy only). Leg
spellings: `--project`, `--prefix` identical-string, trailing-slash
`<repo>/.kilo/.`, symlinked-cwd `--project`, `--project --force-config`.
(Temp-dir prefixes in stderr elided above; full paths appear in the live
transcript.)

## Reference repaired variant (expect accept)

`repaired.sh` is byte-identical to `git show main:install.sh` (SHA256
`ab8c8f89e150b23b2b800db4a7d47bc03dcab30c3f0462c0766b05d87e16f1de`).

```text
$ python3 oracle.py repaired.sh
  PASS: self-install --project exits 0
  PASS: self-install --project leaves payload byte-for-byte unchanged
  PASS: self-install --prefix self/. exits 0
  PASS: self-install --prefix self/. leaves payload byte-for-byte unchanged
  PASS: self-install --project --force-config exits 0
  PASS: self-install --project --force-config leaves payload byte-for-byte unchanged
  PASS: distinct-destination install exits 0
  PASS: distinct-destination copies agents/a.md
  PASS: distinct-destination copies agents/nested/deep.md
  PASS: distinct-destination copies skills/b.md
  PASS: distinct-destination copies kilo.json
  PASS: distinct-destination copies .gitignore
$ echo $?
0
```

The `--force-config` leg is what the round-3 fix (`a529d44`) closed: the
payload guard alone still ran `install_config`, whose `cp kilo.json` self-copy
would abort under `--force-config`. The leg exists so a partial repair that
misses the config path fails here.

## F8 mutation guard: repair that disables copying (expect reject)

The corpus-map failure mode for F8 is "self-copy repair disables valid
installs or removes necessary copying". A minimal `exit 0` script satisfies
the self-install legs but is rejected because it copies nothing:

```text
$ printf '#!/usr/bin/env bash\nset -euo pipefail\nexit 0\n' > /tmp/f8-disable-repair.sh
$ python3 oracle.py /tmp/f8-disable-repair.sh
  PASS: self-install --project exits 0
  PASS: self-install --project leaves payload byte-for-byte unchanged
  PASS: self-install --prefix self/. exits 0
  PASS: self-install --prefix self/. leaves payload byte-for-byte unchanged
  PASS: self-install --project --force-config exits 0
  PASS: self-install --project --force-config leaves payload byte-for-byte unchanged
  PASS: distinct-destination install exits 0
  FAIL: distinct-destination copies agents/a.md
  FAIL: distinct-destination copies agents/nested/deep.md
  FAIL: distinct-destination copies skills/b.md
  FAIL: distinct-destination copies kilo.json
  FAIL: distinct-destination copies .gitignore
$ echo $?
1
```

## Static predicate layer (removed)

This case previously carried a `checks.json` regex smoke layer through the
admission runner. It was deleted on PR #7 review: the document-scope regexes
were subtler than the behavior they approximated (a reviewer traced an
anchor-order path where the guard pattern's pass depended on regex
backtracking rather than on the script's structure), and regex-on-source
cannot see any of the failure modes this family exists to catch. The
executable oracle above is the sole adjudicator; static checks for this case
were smoke we no longer claim.

## Re-score on hardened oracle (2026-10-21, PR #7 external review, amended)

Oracle legs by the end of the final review pass: five self-install spellings
(--project, --prefix identical-string, trailing-slash `<repo>/.kilo/.`,
symlinked-cwd --project, --project --force-config), one distinct-destination
install exit leg, and five distinct-destination content legs — 16 legs total.
Final re-run against all four installers on file:

| candidate | legs | verdict |
| --- | --- | --- |
| target.txt (known-bad) | 11 pass / 5 fail — all five self-install spellings fail with the historical cp same-file error | exit 1 (reject) |
| repaired.sh (= main:install.sh) | 15 pass / 1 fail — passes everything except the trailing-slash `--prefix <self>/.kilo/.` spelling, which evades its string-compare guard (the historical cp error recurs) | exit 1 (reject on that leg) |
| .tracer/current/install-current.sh (readlink-canonicalized) | 16/0 | exit 0 |
| .tracer/absent/install-absent.sh (string compare with readlink fallback on both sides) | 16/0 | exit 0 |

Note on history: an earlier version of this table (16-leg era minus the
trailing-slash leg, 14 legs) claimed repaired.sh passed 14/0. Adding the
trailing-slash leg — suggested in the final bot review pass — caught a real
defect in main's own install.sh, exactly the kind of finding this oracle
exists to surface. The earlier table claimed the same for both produced
installers; that claim stands and strengthened (they pass the leg that
repaired.sh fails).

Caveat, recorded in provenance.md: a fully symlink-spelled invocation
($0 logical *and* dest logical, e.g. ./install.sh from a symlinked dir)
also defeats the plain string compare in main's install.sh — independently
reproduced. Both that form and the trailing-slash `--prefix` form are
product-hardening scope for install.sh, deliberately not folded into this
case's bar.

Oracle-leg exit details for the final rows are reproducible by running
`python3 oracle.py <candidate>` in this directory; the intermediate
transcripts live in this file's git history.
