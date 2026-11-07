---
name: role
description: Use when an agent has an accepted brief but no role, or the recruit script prints role. Writes role.md - what the agent owns, reads and must never do, its identity, and its split with any actor already in the same role - then goldfish-reviews it.
---

# role

The job description: what this colleague owns, what they read, who they work alongside, and whose name they sign with. Read `.minime/<agent>/brief.md` and the roster of existing actors (for the network, `rgh-botnet` `blackboard/charters/` and `bots/`). Write `.minime/<agent>/role.md`:

1. **Owns**: each kind of state it writes (a label, a file, a card field, a mailbox). Each has one writer. If another actor already writes it, either it stays theirs and this agent reads it, or the human rules on a handover (D4).
2. **Reads**: each input, with its named consumer. An input queue nobody reads in full is a starved mailbox (D2).
3. **Never**: actions outside its authority, copied from the brief's limits, plus any one-way door it may only propose.
4. **Overlap**: every existing actor in the same role or touching the same items, and the written split (who acts, who only prepares evidence). A second actor with no split does not go live (D1).
5. **Identity**: its own account or app user on each service it writes to. No borrowed human identity (C3). List every path it uses on each service (read, write, mentions, scheduled pulls) for `trial` (C4).
6. **Reports to**: the one voice that speaks for it to people, if it is not that voice.

Load `goldfish-review` with artifact `role.md`, intent `brief.md`, question "which state has two writers, which input has no full reader, which actor overlaps without a split?", blocking rule "two writers to one state, an overlap with no split, or a borrowed identity", output `role-review.md`. Run `python3 "$NEXT" <agent> --pin role` before loading it, then `--clear role` once every verified blocker is fixed or declined (see `recruit`).

Done when every owned state has one writer, every overlap has a split, the identity is the agent's own, and `role-review.json` is clear for the current `role.md`.
