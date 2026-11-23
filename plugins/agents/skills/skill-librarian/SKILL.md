---
name: skill-librarian
description: Use before writing or extending a skill. Judges the proposal as skill, script, hook or nothing and writes that verdict with the reason. Writes no skill, script or hook.
---

# skill-librarian

Use it before writing or extending a skill. A control earns its place by a probe and an eval, or it is cut; this skill asks that of a proposal. It is itself unevaluated, so `recruit` does not require it. It writes a verdict and stops.

## Verdict

```
verdict: skill | script | hook | nothing
scope: <one sentence>
reason: <which checks passed or failed, with the evidence>
verify: <the known input that fires it, the clean input that must stay quiet, and the with/without eval; none when the verdict is nothing>
retire: <event that would delete the skill, script or hook; none when the verdict is nothing>
```

Write one block per scope: a proposal split under Scope gets one complete block for each sentence. `verdict` is one of those four words. A proposal whose only judgement is "run this and paste the output" is `script`.

## Decide

| Form | When |
| --- | --- |
| skill | The model must judge, and at least two repos or seats want that same judgement |
| script | The steps have one right answer from their inputs. Counters, caps and cursors live here (A8) |
| hook | It must run even when the model never loads a skill: a guard on a tool call, a stop, or a record the host writes |
| nothing | One seat and nothing deterministic to extract, an installed skill already does it, the form would be a skill but no event would delete it, or Verify found no probe and eval plan |

When the hook row matches, the form is `hook` even if the script row also does; the hook may call a script for the deterministic part. A single-seat deterministic job that need not run on the host is a `script` in that repo. Copies of one skill into several host folders of the same repo count as one seat.

## Checks

Judge all six. The form comes from the table.

1. **Repeat.** Name two repos or seats that would use it. One seat is not a shared skill.
2. **Scope.** One sentence. If that sentence needs "and", split it into two proposals and judge each.
3. **Pipeline.** A step with one right answer goes in a script, not prose. Prose that holds a counter, a cap or a cursor is lost on compaction (A8). A skill may name the script and when to run it. It does not restate the steps.
4. **Already there.** Search installed plugins and marketplace skills for this job. A match is `nothing`; name that skill. When nothing matches, name where you looked. Do not start an index file.
5. **Retire.** A skill names the event that would delete it: the host grows the feature, the second seat drops it, or an eval shows it does not fire. A skill with no such event is `nothing`. A script or hook keeps that form and names the event that would delete that file. A missing skill-retirement trigger does not turn a script or hook into `nothing`.
6. **Verify.** Unless the verdict is `nothing`, name the known input that fires the control and the clean input that leaves it quiet (E5), and the with/without eval that would keep or cut it. Record the plan in `verify`; do not build or run it. A control with no plan is `nothing`.

## Steps

1. Restate the proposal as one sentence of scope. Split on "and" before the checks; each sentence is judged and written on its own.
2. Run the six checks. Put the evidence in `reason`: repo or seat names, the existing skill's name, the script or hook path. Put the probe and eval plan in `verify`.
3. Pick the form from the table. Write one verdict block per scope.
4. Stop. The author writes the artifact after the verdict, in a later pass.

Done when every scope has a verdict block and no skill, script or hook was added or extended.
