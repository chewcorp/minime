---
name: role
description: Use when an agent has an accepted brief but no role, or the recruit script prints role. Writes role.md - what the agent owns, reads and must never do, its identity, and its split with any actor already in the same role - then goldfish-reviews it.
---

# role

Writes `.minime/<agent>/role.md`: owned state, inputs, prohibitions, overlap split, identity. Read `brief.md` and the roster of existing actors (for the network, `rgh-botnet` `blackboard/charters/` and `bots/`).

1. **Owns**: each kind of state it writes (a label, a file, a card field, a mailbox). One writer per state. If another actor already writes it, it stays theirs and this agent reads it, or the human rules on a handover (D4).
2. **Reads**: each input, with its named consumer. An input queue nobody reads in full is a starved mailbox (D2).
3. **Never**: actions outside its authority, copied from the brief's limits, plus each one-way door it may only propose.
4. **Overlap**: every existing actor in the same role or on the same items, and the written split (who acts, who only prepares evidence). A second actor with no split does not go live (D1).
5. **Identity**: its own account or app user on each service it writes to; no borrowed human identity (C3). Cite the evidence it exists (account or app id), or the cutover precondition that creates it. List every path it uses per service (read, write, mentions, scheduled pulls) for `trial` (C4).
6. **Reports to**: the one voice that speaks for it to people, if it is not that voice.

Reviewed stage (see `recruit`): artifact `role.md`; intent `brief.md`; question "which state has two writers, which input has no full reader, which actor overlaps without a split?"; blocking rule "two writers to one state, an overlap with no split, or a borrowed identity"; output `role-review.md`.

Done when every owned state has one writer, every overlap has a split, the identity is the agent's own, and `role-review.json` is clear for the current `role.md`.
