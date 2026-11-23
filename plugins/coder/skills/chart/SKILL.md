---
name: chart
description: Use when accepted delivery-loop criteria need more than one ticket. Maps the work into ordered tickets with blocking edges, each small enough for one context window. Skip it for one-ticket work and go to build.
---

# chart

Read `.minime/<task>/acceptance.md`. Write `.minime/<task>/tickets.md`.

1. Order tickets tracer-bullet first: the first ticket runs end to end through the real entry point, however thin.
2. Split by workflow step, rule variation, entry method, or deferred quality, until each ticket fits one context window.
3. Give each ticket a standalone `## T1` heading. Put its goal and `serves: O1, O3` or `blocked-by: T…` metadata in the body; every heading line must be exactly `## T[1-9][0-9]*`. References in prose do not declare tickets. See the [gate contract](../deliver/references/gates.md) for the copyable format.
4. A ticket you cannot estimate becomes a spike: one question plus a timebox. Use the [disposable prototype contract](../deliver/references/investigation.md) when the answer needs a run. Tickets blocked by a spike wait for its answer; at the bound, an unanswered question goes to the human.
5. Spend scrutiny where a mistake is hard to undo (one-way doors); decide two-way doors quickly. For changed contracts, identify producers, consumers, supported paths to preserve and an independent observable result. For ordering risks, use the [statechart contract](../deliver/references/investigation.md) and turn violating paths into acceptance examples. Keep verification proportional to the outcome.
6. Load the `coder-goldfish-review` skill:
   - artifact: `.minime/<task>/tickets.md`
   - intent: `.minime/<task>/acceptance.md`
   - question: what work is missing, out of order, or too big for one context window, and which `blocked-by` edge is wrong?
   - blocking rule: an outcome no ticket delivers, a dependency cycle, or a ticket that cannot be built in the stated order
   - output: `.minime/<task>/tickets-review.md`

   Fold the verified findings into `tickets.md`.

Done when every ticket passes INVEST or is a marked spike, every outcome ID in `acceptance.md` is served by at least one ticket, every ticket serves at least one outcome ID, and `tickets-review.md` is complete (not `review: incomplete`) with no open blocking finding.

Then initialize the [delivery gate](../deliver/references/gates.md). Keep ticket
progress in the ledger, not edits to the accepted plan; changed scope requires
a human ruling and renewed planning review, without resetting the repair counter.
