# Testing

*From chapters 14–16 ("Testing Disciplines", "Clean Tests", "Acceptance Testing").*

Tests are as important as production code — arguably more, because they preserve the flexibility to change the production code safely. **If you let tests rot, the code rots too.**

## Testing disciplines (pick one)

### 1. TDD — Test-Driven Development

Three laws, yielding a seconds-long cycle:

1. Write no production code until you have a failing test that requires it.
2. Write no more of a test than is sufficient to fail (or fail to compile).
3. Write no more production code than is sufficient to pass the currently failing test.

Result: everything worked a few minutes ago. Debugging collapses; the reflex becomes "revert to last green and try again."

### 2. TCR — Test && Commit || Revert

Kent Beck, 2018. Hook into save/build: if tests pass, auto-commit. If they fail, auto-revert. Doesn't mandate test-first; mandates tiny steps (because you lose your work otherwise).

### 3. Small Bundles

Ousterhout-style. Order is free; interval is longer (minutes, not seconds). A bundle of production code + tests lands together with high coverage. Requires honest discipline to keep the bundle actually small.

All three are compatible with clean code. Whichever you choose, honor the bundle size and test coverage.

## Keep tests clean

- Tests are code too. Refactor, rename, extract, deduplicate.
- Dirty tests → tests get abandoned → production code stops being safe to change.
- Tests preserve the **-ilities**: flexibility, maintainability, reusability.

## F.I.R.S.T.

Test characteristics:

- **Fast.** If tests are slow you won't run them; if you don't run them you won't find bugs early. Design tests for speed.
- **Independent (Isolated).** No test sets up another. Order-independent. One failure should not cascade.
- **Repeatable.** Any environment — dev laptop offline on a train, CI, staging. Non-repeatable tests grow excuses.
- **Self-validating.** Boolean pass/fail. No log inspection, no visual diff.
- **Timely.** Write the test with (or just before) the production code. Code written first often turns out to be untestable.

## One assertion per test (heuristic)

Not a strict rule — a single logical assertion. Sometimes that's one `assert_equal`, sometimes it's several lines asserting one concept. The heuristic exists because a test with a dozen assertions becomes a diagnostic nightmare on failure.

Stronger phrasing: **one concept per test.** Each test tests exactly one thing; name it so.

## Test Design

Tests must be **decoupled from production-code structure** as much as the production code is decoupled from itself. Bad test design symptom: a one-line production change breaks hundreds of tests.

- Build a **Domain-Specific Testing Language (DSL)** — a small helper layer that reads like the domain. Tests written in the DSL are resilient to implementation change.
- Keep test setup out of the tests. Common builders / fixtures live in a separate module; tests just say "`a_valid_order()`" not "`Order.new(id=..., customer=..., lines=[...])`".

## Acceptance Testing

- The *true* requirements of a system are the tests that sign off on it. A requirements document that contradicts the acceptance tests is wrong by definition.
- Acceptance tests should be **written by BA/QA**, feature by feature, before implementation.
- Programmers *automate* them (programmers will not manually re-test endlessly).
- The automation language must be one BA/QA can read and ideally author in (Cucumber, SpecFlow, FitNesse, etc.).

## GDScript / RTV notes

- **RTV has no test suite.** The repo's `CLAUDE.md` says so explicitly: "There is no test suite or linter — mods are plain GDScript loaded at runtime by the game."
- For this repo, "testing" in practice means:
  - **Deploy-and-play.** `Scripts/deploy_mod.py` pushes a mod to the game; the author launches the game and verifies behavior.
  - **`Scripts/validate_mod.py`** — static sanity checks on mod structure.
  - **Decompiled-source grep** — confirm the override path matches a real `res://Scripts/...` file before trusting `take_over_path()`.
- **If you *do* add automated tests** to the Python tooling (`Scripts/*.py`), use `pytest` and apply F.I.R.S.T. literally.
- **GUT (Godot Unit Testing)** is available for Godot 4 if you choose to add GDScript tests — test resources and pure-logic classes. Don't try to test node-tree behavior without a headless harness; it's more pain than value for a mod codebase.
- **Manual acceptance test for RTV mods:** keep a short checklist per mod (`deploy → open main menu → start new game → exercise the mod's feature → return to menu → no errors in `%AppData%\Road to Vostok Demo\logs\godot.log`). That's the repeatable battery — write it down for each mod.
