# Wake template

The standard wake of one agent routine as a TLA+ model. `chart-duties` copies this folder per routine and fits it.

The agent may take any enabled step. The environment picks the input kind (explicit request, inferred work, ack-only message, an item another actor holds), whether the loaded charter matches the committed one, and may inject one restart, one context compaction and one stop.

| Config | Meaning |
| --- | --- |
| `gated.cfg` | Host-held guards, outbox with receipts, destination read before any resend. Must hold. |
| `receipts.cfg` | As gated without the destination read. Breaks `NoDuplicateEffect`: a retry after a lost answer sends twice. |
| `prose.cfg` | Every rule held only by the prompt. All eight rules break. |

## The eight rules

| Invariant | Rule | Failure codes |
| --- | --- | --- |
| `NoDuplicateEffect` | An outside action happens at most once | D6 |
| `NoAckOnlyReply` | Never send a message that only acknowledges | A1, B2 |
| `BoundedWake` | Tool calls per wake stay under the cap | A3, A6, A8 |
| `NoStaleCharterAct` | Never act on a charter that is not the committed one | B3, C1 |
| `OneActorPerItem` | Never act on an item another actor holds | D1 |
| `ObserveOnly` | Inferred work in observe mode has no outside effect | C5 |
| `StopWins` | No tool call or outside action after a person says stop, even across a restart | D5 |
| `EndsRecorded` | Every wake ends in a recorded state | A6, A7 |

Codes are in `references/failure-catalogue.md`.

## What it leaves out

One wake, one item, one outside action. The budget counts tool calls, not tokens. `delivered` is the destination's own state, so the gated guard `delivered = 0` is the destination read, and it assumes that read is current. The ack rule is held by routing ack-only inputs to record; an ack-only reply to an explicit agent request is not modelled. No lease race between two agents, no budget across wakes. Gated holds by construction for most rules: the check shows the guards survive restart, compaction and stop orderings, not that a host has them. That is what each routine's `chart.json` records.

## Run

```sh
java -cp "$TLA2TOOLS" tlc2.TLC -workers 1 -config gated.cfg Wake.tla
```

Needs Java and TLC 1.7.4 (`tla2tools.jar`). Each config checks all eight rules and stops at the first break. Results at the template's own settings (Cap = 3), one rule per run: gated holds all eight in 973 states; prose breaks each in 4 to 9 steps. Source and per-rule loop: [workspace-sdlc-skills wake model](https://github.com/chewcorp/workspace-sdlc-skills/tree/main/docs/reports/coordinator-20261107-minime-agents-wake).
