# Evidence pitfalls

Consult the examples relevant to the claim. They illustrate how proof can share
an implementation's blind spot; they are not required cases for every change.

| Weak evidence | Stronger observation |
| --- | --- |
| A fixture already forces the answer for an unrelated reason | Minimise the fixture so breaking the claimed property changes the result. |
| An export and its expected count reuse the same filter | Derive the expected population independently, including rows the repair must preserve. |
| Direct rendering described as a transition test | Drive the transition, or narrow the coverage claim. |
| Green runner summary without execution of the new case | Confirm the documented runner discovers and executes that case. |
| Stub falls through to a real service or depends on local images | Isolate the stub and exercise its failure path. |
| Temporary resources survive a failing test | Scope ownership so cleanup runs on both success and failure. |
| Test freezes prose, task names or implementation spelling | Observe executable values and consumer behaviour. Exact external identifiers can be legitimate contracts. |
| Prompt wording exists but a supported workflow dead-ends | Trace the affected actors and state transitions, including ordinary and exception paths. |

Choose normal, supported alternative and failure cases when they distinguish the
claimed behaviour. If an environment or dependency prevents checking the actual
surface, record the claim as unproven rather than substituting a weaker check.

Background: [Proof Against Requirements](https://github.com/chewcorp/workspace-sdlc-skills/blob/f3f2c1b758171e0eaf757463648acb297e0ae2c8/wiki/concepts/proof-against-requirements.md)
explains repair pairs and independent expectations. The local guidance above
does not require access to that private wiki.
