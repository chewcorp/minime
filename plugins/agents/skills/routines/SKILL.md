---
name: routines
description: Use when an agent has an accepted role but its wakes are not written down, or the recruit script prints routines. Writes routines.md - one section per trigger with input as a delta, done-when, budgets, silence rule and approval gate - then goldfish-reviews it.
---

# routines

Their working pattern: what wakes them, what they look at, when they speak up, and when they stop. Read `brief.md` and `role.md`. Write `.minime/<agent>/routines.md` with one section per trigger. Each heading line is exactly `## R1`, `## R2`, …; the recruit script reads only those lines. Under each:

- **Trigger**: schedule, event or message, and who may send it.
- **Input**: what it reads, as a delta since a stored cursor, never the whole world (A5). Where the cursor lives and who advances it (after the record, A7).
- **Decisions**: each judgement the wake makes. Mark the mechanical ones (one right answer) for a script, not prose.
- **Tools and skills**: every one it names. Each must exist on the target host; a missing one is a recorded stop, not a retry (A2).
- **Outside actions**: each post, push, PR or message, its idempotency key, and how to read the destination before a resend (D6).
- **Budgets**: tool calls and tokens per wake, held by the host (A3, A8). Say what happens at the cap: record a partial result and stop.
- **Done-when**: the observable result that ends the wake well.
- **Silence**: what a wake with nothing to do records, and that it sends nothing (A6).
- **Approval gate**: who approves each outside action in an unattended run, chosen now (C6).

Load `goldfish-review` with artifact `routines.md`, intent `brief.md` and `role.md`, question "which wake can repeat an outside action, run unbounded, re-read everything, or end without a record?", blocking rule "an outside action with no key, a budget held only in the prompt, or a wake with no done-when", output `routines-review.md`. Then write `routines-review.json` as `{"artifact": "<python3 \"$NEXT\" <agent> --hash routines.md>", "findings": "<… --hash routines-review.md>", "status": "clear"}` once every verified blocker is fixed or declined (see `recruit`).

Done when every routine has every field above and `routines-review.json` is clear for the current `routines.md`.
