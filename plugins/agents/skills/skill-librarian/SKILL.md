---
name: skill-librarian
description: Use before writing or extending a skill. Judges the proposal as skill, script, hook or nothing and writes that verdict with the reason. Writes no skill, script or hook.
---

# skill-librarian

Use it before writing or extending a skill. A control earns its place by a probe and an eval, or it is cut; this skill asks that of a proposal. It is itself unevaluated, so `recruit` does not require it. It writes a verdict and stops.

## Verdict

```
verdict: skill | script | hook | nothing
reason: <which checks passed or failed, with the evidence>
scope: <one sentence, or the split sentences>
retire: <event that would delete the skill, script or hook; none when the verdict is nothing>
```

`verdict` is one of those four words. A proposal whose only judgement is "run this and paste the output" is `script`.

## Decide

| Form | When |
| --- | --- |
| skill | The model must judge, and at least two repos or seats want that same judgement |
| script | The steps have one right answer from their inputs. Counters, caps and cursors live here (A8) |
| hook | It must run even when the model never loads a skill: a guard on a tool call, a stop, or a record the host writes |
| nothing | One seat and nothing deterministic to extract, an installed skill already does it, or the form would be a skill but no event would delete it |

A single-seat deterministic job is a `script` in that repo. Copies of one skill into several host folders of the same repo count as one seat.

## Checks

Judge all five. The form comes from the table.

1. **Repeat.** Name two repos or seats that would use it. One seat is not a shared skill.
2. **Scope.** One sentence. If that sentence needs "and", split it into two proposals and judge each.
3. **Pipeline.** A step with one right answer goes in a script, not prose. Prose that holds a counter, a cap or a cursor is lost on compaction (A8). A skill may name the script and when to run it. It does not restate the steps.
4. **Already there.** Search installed plugins and marketplace skills for this job. A match is `nothing`; name that skill. When nothing matches, name where you looked. Do not start an index file.
5. **Retire.** A skill names the event that would delete it: the host grows the feature, the second seat drops it, or an eval shows it does not fire. A skill with no such event is `nothing`. A script or hook keeps that form and names the event that would delete that file. A missing skill-retirement trigger does not turn a script or hook into `nothing`.

## Steps

1. Restate the proposal as one sentence of scope. Split on "and" before the checks.
2. Run the five checks. Put the evidence in `reason`: repo or seat names, the existing skill's name, the script or hook path.
3. Pick the form from the table. Write the verdict.
4. Stop. The author writes the artifact after the verdict, in a later pass.

Done when the verdict is written and no skill, script or hook was added or extended.
