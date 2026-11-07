---
name: routines
description: Use when an agent has an accepted role but its wakes are not written down, or the recruit script prints routines. Writes routines.md - one section per trigger with input as a delta, done-when, budgets, silence rule and approval gate - then goldfish-reviews it.
---

# routines

Writes `.minime/<agent>/routines.md`: one bounded wake per trigger. Read `brief.md` and `role.md`. Each heading line is exactly `## R1`, `## R2`, …; the recruit script reads only those lines. Under each:

- **Trigger**: schedule, event or message, and who may send it.
- **Input**: a delta since a stored cursor, never a full re-read (A5). Where the cursor lives; it advances only after the record (A7).
- **Decisions**: each judgement the wake makes. Mark the mechanical ones (one right answer) for a script, not the prompt.
- **Tools and skills**: every one it names, each present on the target host. A missing one is a recorded stop, not a retry (A2).
- **Outside actions**: each post, push, PR or message, its idempotency key built from a stable input id (never wake time), and the destination read before any resend (D6).
- **Budgets**: tool calls and tokens per wake, and attempts and spend across wakes for any retry or fan-out, held outside the context by host or script (A3, A8). Cite each numeric limit from `brief.md` by value; state the worst-case cost per mode (`observe`, `act`). At the cap: record a partial result and stop.
- **Done-when**: the observable result that ends the wake.
- **Silence**: what a no-op wake records; it sends nothing (A6).
- **Approval gate**: who approves each outside action in an unattended run, chosen now (C6).

Reviewed stage (see `recruit`): artifact `routines.md`; intent `brief.md` and `role.md`; question "which wake can repeat an outside action, run unbounded, re-read everything, or end without a record?"; blocking rule "an outside action with no key, a budget held only in the prompt, or a wake with no done-when"; output `routines-review.md`.

Done when every routine has every field above and `routines-review.json` is clear for the current `routines.md`.
