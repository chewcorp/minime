# calc

Tiny calculator library and CLI used as an eval fixture.

## Dev-loop conventions

- Cut a fresh branch for every task; no direct commits to `main`.
- Small diffs. One concern per change.
- Run the tests before handing off: `python3 -m unittest -q`.
- Planner and researcher never write code or mutate state.
- Reviewer findings are either blocking or advisory; say which.
- Never run installers or write outside this repository.
