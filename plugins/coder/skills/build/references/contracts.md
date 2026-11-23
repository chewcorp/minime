# Contract examples

Use these as prompts when the changed contract makes them relevant, not as a
mandatory checklist for every task. Derive the actual cases from supported
behaviour and the consumer's expectations.

| Changed boundary | Cases worth considering |
| --- | --- |
| Input representation | Missing, null, wrong-type, malformed and supported empty values remain distinct before coercion. |
| Parser/library integration | Exercise input in the reused parser's syntax without reshaping it to avoid a collision. For argparse, consider a value starting with `-` that is not a plain number. |
| Temporal semantics | Distinguish absolute instants from local wall time; check required time-zone semantics. |
| Text representation | Check character encoding and context-specific escaping rules. |
| External reader | Follow pagination, correlate responses and decode results as the established consumer expects. Prefer its existing reader when possible. |
| Shared state | Check persistence acknowledgements and required atomicity; exercise relevant concurrency interleavings, retry semantics and idempotency. |
| Resource ownership | Verify cleanup on both success and failure, including resources introduced by a repair. |

A boundary fix should preserve a valid alternative case. Stricter validation,
for example, must still accept supported empty responses. Search sibling readers
and representations when the same cause may recur, but keep the repair within
the agreed task scope.
