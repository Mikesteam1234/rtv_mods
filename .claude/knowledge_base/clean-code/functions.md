# Functions

*From chapters 7–11 ("Clean Functions", "Function Heuristics", "The Clean Method", "One Thing", "Be Polite").*

Functions are the first line of organization in any program. Writing them well is the single most effective thing you can do for a codebase.

## Small

- **Functions should be small.** Smaller than that. The author (after 60 years of writing code) targets ~a dozen lines or less.
- **Rule of thumb:** fits on a screen. Indent level rarely exceeds 1–2.
- **Blocks inside `if` / `else` / `while`** should be one or two lines — typically a single call to a well-named helper.
- A small function with an expressive name often reads like prose:
  ```gdscript
  if employee.should_be_paid_today():
      employee.pay()
  ```

Some functions read better un-decomposed; those are exceptions. In general, smaller is better.

## Do One Thing

> "Functions should do one thing. They should do it well. They should do it only."

How do you know? Test: can you extract another function from it whose name is not merely a restatement of the implementation? If yes, the function was doing more than one thing.

"One thing" is operationalized as **one level of abstraction**. A function that mixes high-level policy (`loop over rentals`), mid-level logic (`switch on movie type`), and low-level detail (`increment a counter`) is doing more than one thing.

## One Level of Abstraction per Function

Every statement in the function body should be at the same conceptual level. If some lines are "policy" and others are "mechanism", extract the mechanism into its own function.

## The Stepdown Rule

Code should read like a top-down narrative. Each function is followed — vertically below it in the file — by functions at the *next lower* level of abstraction. The reader reads top-to-bottom, descending one level at a time:

```
make_statement()
  clear_totals()
  make_header()
  make_details()
    make_detail()
      format_detail()
  make_footer()
```

This is the same "newspaper metaphor" from [`formatting.md`](formatting.md), applied to functions.

## Switch / match statements

- Switches are inherently N-thing-doing. Hard to keep small, hard to make SRP-compliant.
- Each switch will tend to breed sibling switches (`determine_amount` spawns `determine_points`, `apply_coupon`, `get_age_restriction`) — all with the same branching structure.
- **Solution:** bury switches in a factory and dispatch via polymorphism. The switch appears once, in one low-level module, never repeated.
- Acceptable exception: a single switch at a boundary that maps enum values to domain objects.

## Function arguments

- **Ideal arity: 0 (niladic). Next best: 1 (monadic). Then 2 (dyadic).** 3 (triadic) should be avoided; 4+ requires serious justification.
- Arguments are hard: they force the reader to look up types, meanings, and orderings.
- **Flag arguments are ugly.** `render(true)` is a tell that the function does two things. Split into `render_for_screen()` and `render_for_printer()`.
- **Common monadic forms:**
  - Ask a question about the argument: `file_exists("foo")`.
  - Operate on the argument and return a transformed version: `fopen("foo")`.
  - Event: the argument is the event being dispatched; no return value.
- **Output arguments** (mutable parameters used to return data) are confusing — readers expect data to come in via args and out via returns. Prefer multi-return (tuple / object) or mutate the receiver.
- **Argument objects.** When you have 3+ related arguments, wrap them: `make_circle(center: Vector2, radius: float)` > `make_circle(x: float, y: float, radius: float)`.

## Have No Side Effects

A function named `check_password(user, pw)` that *also* initializes the session is lying about what it does. Side effects violate the principle of least surprise. Either rename the function to disclose the effect (`check_password_and_initialize_session`) or separate them.

## Command-Query Separation (CQS)

A function should either **do** something (command, returns void/`Result`) or **answer** something (query, returns a value and has no side effects). Not both.

Bad:
```gdscript
if set_attribute("username", "mike"):   # did it exist, or did it succeed?
    ...
```

Better:
```gdscript
if attribute_exists("username"):
    set_attribute("username", "mike")
```

Violations of CQS are sometimes practical (`stack.pop()` returns top and removes it), but adopt them deliberately, not by accident.

## Prefer Exceptions to Error Codes

Error codes push deeply nested `if` pyramids onto every caller and entangle commands with queries:

```
if (delete_page(page) == E_OK) {
    if (registry.delete_reference(page.name) == E_OK) {
        if (config_keys.delete_key(...) == E_OK) {
            ...
        }
    }
}
```

With exceptions (where available), the happy path stays straight and error handling is localized.

- Extract `try` / `catch` blocks into their own function. Error handling *is* one thing; don't mix it with business logic.
- Don't return `null` for "no result" — return empty collections, `Option`/`Maybe`, or throw. Callers should not need ubiquitous null checks.
- Don't accept `null` as a valid argument. Either reject explicitly or split the function.

## Structured Programming

- **Single entry, single exit** is too strict for modern small functions. A function 3 lines long doesn't need it.
- Multiple `return`s are fine in small functions; they often *improve* readability.
- `break` and `continue` are similarly fine in short loops.
- `goto` is still (generally) wrong.

## Be Polite (Ch 11)

Writing order and reading order differ. We *write* depth-first, discovering helpers as we go. But readers want to start at the *top* and descend. The final layout should be the reader-friendly one, not the author's order of discovery.

- After a function works, re-order it top-down so a new reader can skim the top and drill down only as needed.
- This is "politeness" — doing extra work so readers don't have to.

## GDScript / RTV notes

- **Size targets:** function ≤ ~20 lines; script ≤ ~200 lines. Inherited game scripts in `Decomp/` are exempt — we don't own them.
- **Exceptions:** GDScript has no `try`/`catch`. Use one of:
  - `assert(condition, "msg")` for programmer errors.
  - `push_error("msg")` + early return for recoverable errors.
  - Tagged-union return values (`{"ok": true, "value": ...}` or a small class) where a typed `Result` helps.
- **CQS exception — signals.** Emitting a signal is a command; a method that both mutates state and emits the corresponding signal is idiomatic Godot, not a CQS violation. Keep it. Don't try to force "return new state then emit" ordering.
- **Override functions** (`_input`, `_process`, `_ready`) MUST call `super._<fn>(...)`. That is not dead code. Leave it. Clean Code's "do one thing" rule is softened by this inheritance contract.
- **`_on_<emitter>_<signal>` handlers** tend to accrete; keep each tiny and delegate to well-named helpers so the handler itself has one line of substance.
- **Avoid polled input branching in `_physics_process`.** If a function is reading half a dozen `Input.is_action_*` calls, that is 6 things. Split per action or push into a smaller state machine.
- **`get_node_or_null()` > `get_node()`** — don't pass `null` around when you can return early at the boundary.
