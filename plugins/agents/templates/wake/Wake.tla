---- MODULE Wake ----
\* One wake of one agent routine, as the standard minime-agents skeleton.
\* Mode "prose": the rules live in the prompt; the agent may take any step.
\* Mode "receipts": host guards plus an outbox with receipts, but no check of
\*   the destination before resending after a restart.
\* Mode "gated": host guards, outbox, and a destination check before resend.
EXTENDS Naturals
CONSTANTS Mode, Cap

Kinds == {"explicit", "inferred", "ack", "others"}
Hosted == Mode # "prose"

VARIABLES phase, kind, fresh, woke, calls, seen, outbox, delivered, acks,
          staleAct, othersAct, inferredAct, stopped, afterStop, unrecorded,
          crashes, compactions
vars == <<phase, kind, fresh, woke, calls, seen, outbox, delivered, acks,
          staleAct, othersAct, inferredAct, stopped, afterStop, unrecorded,
          crashes, compactions>>

Init ==
  /\ phase = "asleep" /\ kind = "none" /\ fresh = TRUE /\ woke = FALSE
  /\ calls = 0 /\ seen = 0 /\ outbox = "empty" /\ delivered = 0 /\ acks = 0
  /\ staleAct = FALSE /\ othersAct = FALSE /\ inferredAct = FALSE
  /\ stopped = FALSE /\ afterStop = FALSE /\ unrecorded = FALSE
  /\ crashes = 0 /\ compactions = 0

Effects == <<calls, seen, delivered, acks, staleAct, othersAct, inferredAct,
             afterStop, unrecorded, crashes, compactions>>

\* Environment: a trigger arrives with some kind of input, and the loaded
\* charter may or may not match the committed one.
Wake ==
  /\ phase = "asleep" /\ ~woke
  /\ phase' = "orient" /\ woke' = TRUE
  /\ kind' \in Kinds /\ fresh' \in BOOLEAN
  /\ UNCHANGED <<outbox, stopped>> /\ UNCHANGED Effects

\* Orient: hosted modes refuse to act on a charter that is not the committed one.
Orient ==
  /\ phase = "orient"
  /\ phase' \in (IF Hosted /\ ~fresh THEN {"record"} ELSE {"classify", "record"})
  /\ UNCHANGED <<kind, fresh, woke, outbox, stopped>> /\ UNCHANGED Effects

\* Classify: only an explicit, unowned request goes to act. Hosted modes
\* route ack-only, inferred (observe mode) and someone else's item to record.
Classify ==
  /\ phase = "classify"
  /\ phase' \in (IF Hosted /\ kind # "explicit" THEN {"record"} ELSE {"act", "record"})
  /\ UNCHANGED <<kind, fresh, woke, outbox, stopped>> /\ UNCHANGED Effects

\* Prose agents answer an ack with an ack (receipt ping-pong).
ReplyAck ==
  /\ ~Hosted /\ phase = "classify" /\ kind = "ack"
  /\ acks' = acks + 1 /\ phase' = "record"
  /\ UNCHANGED <<kind, fresh, woke, calls, seen, outbox, delivered, staleAct,
                 othersAct, inferredAct, stopped, afterStop, unrecorded,
                 crashes, compactions>>

\* A tool call. Prose checks its own count (in context); hosted modes count outside.
ToolCall ==
  /\ phase = "act"
  /\ IF Hosted THEN calls < Cap ELSE seen < Cap
  /\ calls' = calls + 1 /\ seen' = seen + 1
  /\ afterStop' = (afterStop \/ stopped)
  /\ UNCHANGED <<phase, kind, fresh, woke, outbox, delivered, acks, staleAct,
                 othersAct, inferredAct, stopped, unrecorded,
                 crashes, compactions>>

Queue ==
  /\ Hosted /\ phase = "act" /\ outbox = "empty" /\ ~stopped
  /\ outbox' = "pending"
  /\ UNCHANGED <<phase, kind, fresh, woke, stopped>> /\ UNCHANGED Effects

\* The outside action (post, push, open a PR, message a person).
CanDo ==
  CASE Mode = "prose"    -> phase = "act"
    [] Mode = "receipts" -> phase = "act" /\ outbox = "pending" /\ ~stopped
    [] Mode = "gated"    -> phase = "act" /\ outbox = "pending" /\ ~stopped
                            /\ delivered = 0
Do ==
  /\ CanDo
  /\ delivered < 2   \* model bound: a second delivery already breaks the rule
  /\ delivered' = delivered + 1
  /\ staleAct' = (staleAct \/ ~fresh)
  /\ othersAct' = (othersAct \/ kind = "others")
  /\ inferredAct' = (inferredAct \/ kind = "inferred")
  /\ afterStop' = (afterStop \/ stopped)
  /\ outbox' = outbox
  /\ UNCHANGED <<phase, kind, fresh, woke, calls, seen, acks, stopped,
                 unrecorded, crashes, compactions>>

\* Mark the receipt. `delivered` is the destination's own state, so the
\* gated guard `delivered = 0` in CanDo is the destination read before a send,
\* and MarkSent from pending is the reconcile when the read finds it landed.
MarkSent ==
  /\ Hosted /\ outbox = "pending" /\ delivered > 0
  /\ outbox' = "sent"
  /\ UNCHANGED <<phase, kind, fresh, woke, stopped>> /\ UNCHANGED Effects

Verify ==
  /\ phase = "act"
  /\ IF Hosted THEN outbox = "sent" ELSE delivered > 0
  /\ phase' = "record"
  /\ UNCHANGED <<kind, fresh, woke, outbox, stopped>> /\ UNCHANGED Effects

\* Hosted: at the cap the host ends the wake and records a partial result.
BudgetHit ==
  /\ Hosted /\ phase = "act" /\ calls = Cap
  /\ phase' = "record"
  /\ UNCHANGED <<kind, fresh, woke, outbox, stopped>> /\ UNCHANGED Effects

Record ==
  /\ phase = "record"
  /\ phase' = IF Hosted /\ stopped THEN "halted" ELSE "asleep"
  /\ UNCHANGED <<kind, fresh, woke, outbox, stopped>> /\ UNCHANGED Effects

\* The turn ends mid-wake. Prose: nothing is recorded (next wake redoes it).
\* Hosted: the host wrapper writes the terminal record.
EndTurn ==
  /\ phase \in {"classify", "act"}
  /\ IF Hosted
       THEN phase' = "record" /\ UNCHANGED unrecorded
       ELSE phase' = "asleep" /\ unrecorded' = TRUE
  /\ UNCHANGED <<kind, fresh, woke, calls, seen, outbox, delivered, acks,
                 staleAct, othersAct, inferredAct, stopped, afterStop,
                 crashes, compactions>>

\* Environment faults: one restart and one context compaction per wake.
\* Hosted: the stop is latched outside the run, so a restart after a stop
\* resumes at record, not orient.
Crash ==
  /\ crashes < 1 /\ phase \in {"orient", "classify", "act", "record"}
  /\ crashes' = crashes + 1 /\ seen' = 0
  /\ phase' = IF Hosted /\ stopped THEN "record" ELSE "orient"
  /\ UNCHANGED <<kind, fresh, woke, calls, outbox, delivered, acks, staleAct,
                 othersAct, inferredAct, stopped, afterStop, unrecorded,
                 compactions>>

Compact ==
  /\ compactions < 1 /\ phase = "act"
  /\ compactions' = compactions + 1 /\ seen' = 0
  /\ UNCHANGED <<phase, kind, fresh, woke, calls, outbox, delivered, acks,
                 staleAct, othersAct, inferredAct, stopped, afterStop,
                 unrecorded, crashes>>

\* A person says stop. Hosted: the outer arrow wins; the host writes the
\* terminal record, then the wake halts.
Stop ==
  /\ ~stopped /\ woke
  /\ stopped' = TRUE
  /\ phase' = IF Hosted /\ phase # "asleep" THEN "record" ELSE phase
  /\ UNCHANGED <<kind, fresh, woke, outbox>> /\ UNCHANGED Effects

Done == phase \in {"asleep", "halted"} /\ woke /\ UNCHANGED vars

Next == Wake \/ Orient \/ Classify \/ ReplyAck \/ ToolCall \/ Queue \/ Do
        \/ MarkSent \/ Verify \/ BudgetHit \/ Record \/ EndTurn \/ Crash
        \/ Compact \/ Stop \/ Done

Spec == Init /\ [][Next]_vars

\* The rules, in the reader's words.
NoDuplicateEffect == delivered <= 1     \* an outside action happens at most once
NoAckOnlyReply    == acks = 0           \* an ack-only input gets no reply
BoundedWake       == calls <= Cap       \* tool calls per wake stay under the cap (tokens not modelled)
NoStaleCharterAct == ~staleAct          \* never act on a charter that is not the committed one
OneActorPerItem   == ~othersAct         \* never act on an item another actor holds
ObserveOnly       == ~inferredAct       \* inferred work in observe mode has no outside effect
StopWins          == ~afterStop         \* no tool call or outside action after a person says stop
EndsRecorded      == ~unrecorded        \* every wake ends in a recorded state
====
