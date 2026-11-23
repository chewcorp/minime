# Statecharts and disposable prototypes

Use only when an unanswered question could change the accepted result or the
implementation. A simple edit with no such question skips both.

## Statechart: ordering is the risk

Trigger: changed stateful behaviour, retry/repair routing, evidence freshness,
or another ordering rule spanning stages. Before dependent implementation:

1. Write one question, the user's invariants, and a finite time/state budget in
   `.minime/<task>/statechart.md`; record start time. Include failure, retry,
   interruption and human-stop paths, not only the happy path.
2. Model the states, transitions and guards needed to express those invariants
   in the smallest statechart. Reuse the project's
   statechart/model checker when available; otherwise label it a design chart,
   not a checked model. Do not install formal tooling just to draw a diagram.
3. Trace violating paths into acceptance examples through the actual entry
   point. A modeled counterexample is a hypothesis until replayed. Record the
   checker command/output, bounds and unchecked rules if a checker was used.
4. Stop at the bound: record end time and the answered question, or escalate an
   unresolved question and block dependent implementation. Preserve the chart,
   invariants and replay tests; never weaken a rule to get a green check.

## Prototype: a runnable answer is missing

Trigger: a specific feasibility or interaction question cannot be answered from
existing code/docs. Write one question, a finite time/attempt limit and an
observable answer in `.minime/<task>/prototype.md` before running anything.

Use a disposable temp directory or isolated scratch repository with fake data,
no production credentials, and no writes to user/global configuration. Name
the directory you own. Run the smallest experiment, record command, actual
output, limits, start/end time and decision. At the bound, stop: answer or
escalate; do not quietly extend the spike or build on an unresolved result.

Delete **only the scratch implementation you created**, after preserving the
observations. Do not promote it by renaming/copying/cherry-picking into product
code. Build the production implementation separately from accepted examples;
retain independently designed regression checks, not prototype shortcuts.
If the answer changes accepted outcomes, return to clarify for a human ruling.

These are investigation contracts, not extra universal gates. Claims that a
skill improves live agent behaviour still require behavioural evidence.
