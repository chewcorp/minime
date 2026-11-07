---
name: trial
description: Use when every routine has a checked chart and the recruit script prints trial. Proves each control fires on a known input and stays quiet on a clean one, runs behavioural cases inside a real model in a throwaway HOME, and writes proof.json keyed to the tree hash.
---

# trial

A trial shift before they start: show each safeguard catches the thing it is for and stays out of the way on ordinary work. A control nobody has seen fire may be dead (E5). Read each `charts/R<n>/chart.json` and `role.md`.

1. **Probes.** For each guard, write one known input that must trip it (an ack-only message, a missing named skill, a stale charter, an item another actor holds, a resend after a lost answer, a stop mid-wake) and one clean input that must not. Keep probes harmless and labelled so they never reach real work.
2. **Paths.** Exercise every service path `role.md` lists for the agent's identity, not just one write (C4).
3. **Behaviour.** Run the agent's routine on each case with a real model. The answer comes from a fresh run that never sees the checks; store raw output before scoring. No code decides an answer (E4). Use a throwaway HOME and no production credentials (C6).
4. **Record.** Commit the package first. Write `.minime/<agent>/proof.json` as `{"digest": "<python3 \"$NEXT\" <agent> --digest>", "rows": [{"id": "R1 G1 fire", "how": "...", "result": "pass"}, …]}`. The digest covers the committed tree and every recruit artifact except `proof.json`. Rows: `R<n> G<m> fire` and `R<n> G<m> clean` for every guard of every routine, plus one row per path and case with its own unique ID; `result` is `pass`, `fail` or `unproven`. Any change to the package or a recruit artifact, a dirty worktree or a git error voids the proof; rerun.

Never weaken a probe to make it pass. A probe that cannot run is `unproven`, not skipped.

Done when every guard in every `chart.json` has a passing `fire` and `clean` row, every row is `pass`, and the digest matches.
