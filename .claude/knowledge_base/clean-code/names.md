# Meaningful Names

*From chapter 4 ("Meaningful Names").*

Names are the primary way code explains itself. Choosing good names takes time but saves more than it takes. Change them when you find better ones.

## Use intention-revealing names

A name should answer: **why** does this exist, **what** does it do, **how** is it used?

- If a name needs a comment to explain it, the name failed.
- `int d; // elapsed time in days` → `elapsed_days`, `days_since_creation`, `file_age_in_days`.
- Longer names aren't better — *clearer* names are better. Clarity wins over brevity.

## Build a system of names

Renaming incrementally teaches a reader the domain:

- `the_list` → `game_board`
- `x[0]` → `cell[STATUS_VALUE]`
- `x[0] == 4` → `cell.is_flagged()`

After these renames, even a first-time reader knows: this is a game with a board of cells that have statuses. Good names communicate a great deal about the application as a whole.

## Avoid disinformation

- Don't call a collection an `account_list` unless it's a `List`. Use `accounts`, `account_group`, or `bunch_of_accounts`.
- Avoid names that differ in small ways: `XYZControllerForEfficientHandlingOfStrings` vs `XYZControllerForEfficientStorageOfStrings`.
- Avoid optical-illusion characters: lowercase `l`, uppercase `O`, with numbers `1`/`0`.
- Don't encode type in the name (Hungarian notation is noise today).

## Make meaningful distinctions

- **Number series** (`a1`, `a2`) and **noise words** (`Info`, `Data`, `Object`, `variable`, `table`) add characters without meaning.
  - Bad: `Product`, `ProductData`, `ProductInfo` — what is each for?
  - Bad: `get_active_account()`, `get_active_accounts()`, `get_active_account_info()` — indistinguishable.
- If you can't explain the difference between two names, collapse or re-differentiate them.

## Use pronounceable names

Programming is a social activity. If you can't say it, you can't discuss it.

- `gen_ymdhms` → `generation_timestamp`
- `dta_rcrd102` → `Customer`

## Use searchable names

- Single letters and numeric literals are hard to grep.
- `7` buried in code → `const MAX_CLASSES_PER_STUDENT = 7`.
- Short names are acceptable only in very short scopes (loop indices, caught exceptions).

## Name length by scope

| Kind | Rule | Why |
|------|------|-----|
| **Variables** | Length **proportional** to scope | Tiny scopes can use `i`, `n`. Instance/global vars need descriptive names. |
| **Functions** | Length **inversely proportional** to scope | Global `open()` is fine. Private helper `parse_trailing_configuration_block_for_legacy_users()` needs many words. |
| **Classes** | Same as functions — bigger scope, shorter name | Global `Player`. Nested private helper `PlayerInventoryDirtyFlagObserver`. |
| **Tests** | Longest of all | Test names are documentation; scope is effectively zero. |

## Other rules

- **Don't be cute.** `holy_hand_grenade()` is clever today, baffling tomorrow. Say what it does: `delete_items()`.
- **Pick one word per concept.** Don't have `fetch`, `retrieve`, `get` doing the same thing across classes. Pick one.
- **Don't pun.** If you use `add` to mean concatenation in one place, don't also use it to mean "insert into a map" elsewhere. Use `insert` or `append`.
- **Use solution-domain names** (CS terms: `Queue`, `Visitor`, `AccountVisitor`) when readers are programmers; use **problem-domain names** when a concept has no computer-science analog.
- **Add meaningful context** only when needed. `state` is ambiguous alone; `address_state` is clear. But inside an `Address` class, `state` is perfectly fine — prefer structure over prefix-stuffing.
- **Don't add gratuitous context.** Don't prefix every class in a payroll module with `GSD` because the project is "Gas Station Deluxe". IDEs are better than prefixes.

## GDScript / RTV conventions

The authoritative repo style guide is [`../godot/gdscript-style-guide.md`](../godot/gdscript-style-guide.md). Summary of how Clean Code rules land in GDScript:

- **Functions/variables:** `snake_case` (Godot convention), not `camelCase`.
- **Classes (`class_name`) and nodes in `.tscn`:** `PascalCase`.
- **Constants:** `SCREAMING_SNAKE_CASE`.
- **Signals:** past-tense verbs — `damage_taken`, `door_opened`. Signal handlers: `_on_<emitter>_<signal>`.
- **Private members:** `_leading_underscore`. Respect it; don't reach across it.
- **Booleans:** read as predicates — `is_crouched`, `has_key`, `can_move`. Not `crouch` or `crouched_flag`.
- **Override scripts:** name them for what they override. `ControllerOverride.gd` > `MyScript.gd`.
- **Autoload singletons** (`GameData`, `Simulation`, `Loader`) are short because their scope is the entire process — consistent with the "inversely proportional" rule.
- **Test names:** in this repo there is no test suite, but if you add one, use the long-descriptive-test-name convention.
