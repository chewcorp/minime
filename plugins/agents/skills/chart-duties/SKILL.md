---
name: chart-duties
description: Use when the recruit script prints chart-duties with routine IDs. Instantiates the standard wake statechart for each routine, adds the agent's own rules as invariants, checks it with TLC, and records which guards the host does not provide. Does not write the charter.
---

# chart-duties

How each shift runs, written so a model checker can try every bad day on it before the colleague has one. Every wake runs one standard chart: orient, classify, act, verify, record, with stop, the budget cap and an early end as outer arrows, and a budget and mandate held by the host. The template in `templates/wake/` (relative to this plugin's root) carries eight rules every agent keeps; see its README for what they mean and what the model leaves out.

For each routine `R<n>` the script listed:

1. Copy `templates/wake/` to `.minime/<agent>/charts/R<n>/`, and save the output of `python3 "$NEXT" <agent> --upstream R<n>` now, before fitting: it pins the brief, role and routine you fit against.
2. Fit it to the routine, smallest change first: input kinds the routine really gets, its cap, its outside actions. Add each extra rule from `brief.md` or `role.md` as an `INVARIANT` the human agrees to. Never remove or weaken one of the eight without the human's ruling.
3. In that folder, check the gated config and keep the output:

   ```sh
   java -cp "$TLA2TOOLS" tlc2.TLC -workers 1 -config gated.cfg Wake.tla > gated.out 2>&1
   ```

   Also run `prose.cfg` once and keep `prose.out`: the paths that break there are the rules the agent's prompt alone would be holding.
4. Write `charts/R<n>/chart.json`:

   ```json
   {"model": "<python3 \"$NEXT\" <agent> --hash charts/R<n>>",
    "gated": "<python3 \"$NEXT\" <agent> --hash charts/R<n>/gated.out>",
    "upstream": <the object saved in step 1>,
    "guards": [{"id": "G1", "rule": "...", "guard": "...", "place": "host"}]}
   ```

   One guard per assumption the gated config makes, IDs `G1`, `G2`, … unique, `place` one of `host`, `script`, `prompt` or `unplaced`. A guard the host cannot provide is either built as a script, accepted by the human as prompt-held (the weakest place), or the routine changes. The recruit script will not pass a chart with no guards, an `unplaced` or unknown place, a repeated ID, or a model, `gated.out`, brief, role or routine section that changed after the record. A record that matches a hand-written `gated.out` still passes: the hash catches staleness, not forgery.
5. A break in `gated.out` means the routine design is wrong. Fix the routine or the chart and rerun; until a replay on the host reproduces a path, call it modeled.

If Java or TLC is unavailable, stop and say so. A chart that was not checked is a drawing, and the recruit script will not pass it.

Done when every listed routine has a current `chart.json`, `gated.out` with no error, and no unplaced guard.
