# Kilo commit attribution

Kilo must follow this rule for all Git commit messages it prepares or submits.

## Scope

This rule applies exclusively to Git commit messages.

- Add the trailer only for commits where Kilo contributed content changes.
- Kilo "contributed content" means Kilo performed the file edits, creations, or deletions whose diff is included in the commit.
- Reviewing a change, writing a commit message, staging files, or invoking `git commit` for changes made by a human or another agent does not qualify.
- If it is unclear whether Kilo authored the underlying changes, or if Kilo only provided advice or a message template, do not add the trailer.

## Trailer

When eligible, append exactly one instance of:

Co-authored-by: kiloconnect[bot] <240665456+kiloconnect[bot]@users.noreply.github.com>

## Format and placement

- The trailer appears in the final trailer block.
- Precede the trailer block with a single blank line.
- Do not insert blank lines between trailer lines.
- Example of a complete trailers section:

  <body>

  <blank line>
  Co-authored-by: human@example.com
  Co-authored-by: kiloconnect[bot] <240665456+kiloconnect[bot]@users.noreply.github.com>

- Preserve every pre-existing trailer (Co-authored-by, Signed-off-by, etc.).
- When amending, squashing, or rebasing, keep all existing trailers. Add Kilo's only if the net content changes include Kilo-authored work and the trailer is not already present.

## Never use this trailer for

- Ordinary chat output, session summaries, plans, todo lists, or reasoning.
- Source code, documentation, configuration files, or any non-commit-message text.
- PR descriptions, review comments, issue bodies, or release notes.
- Commits that Kilo did not materially change (e.g., pure reverts, renames without content, or human-authored diffs).

## Additive and truthful attribution only

- Never replace or remove another contributor's trailer.
- Never change git author or committer identity solely to attach co-authorship.
- Other agents and humans keep their own attribution; Kilo never impersonates them or lets them impersonate Kilo.

This rule is loaded only via Kilo's non-payload project configuration (root `kilo.jsonc` `instructions` array) so it does not ship in the consumer payload and cannot affect other tools.
