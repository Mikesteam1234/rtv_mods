# First Principles

*From chapters 1–3 ("Clean Code", "Clean That Code!", "First Principles").*

## What clean code is

Multiple definitions from the book, all consistent:

- **Bjarne Stroustrup:** "Clean code does one thing well."
- **Grady Booch:** "Clean code reads like well-written prose."
- **Michael Feathers:** "Clean code always looks like it was written by someone who cares."
- **Ward Cunningham:** "You know you are working on clean code when each routine you read turns out to be pretty much what you expected."
- **Mark Seeman:** "Clean code fits in your head. A function fits on a single screen, involves no more than a handful of moving parts, and has good names. It's understandable by peers years after it was written. It minimizes surprises, composes well, and is easy to delete."

The unifying word is **care**.

## Core laws

- **LeBlanc's Law:** "Later equals never." If you leave a mess for later, it stays.
- **Kent Beck's rule:** "First, make it work. Then, make it right." Cleanliness and functionality are competing concerns; separate the passes.
- **The only way to go fast is to go well.** Messes always slow a team down. A messy module slows everyone who touches it, every time they touch it. Cleaning is one-time; mess cost compounds.
- **We read code ~10× more than we write it.** Therefore, optimize for readability, not typing speed. You cannot write new code without reading the surrounding code, so easy-to-read code is also easier to *write*.

## The Boy Scout Rule

**Leave the campground cleaner than you found it.**

- Check in code a little cleaner than you checked it out.
- Every commit: one small kindness — rename a variable, split one too-large function, remove one duplication, clean one composite `if`.
- No heroics required; continuous, small improvements beat big rewrites.

## "First Principles" (Ch 3) — four pillars

Every piece of code should be:

1. **Small.** Functions small, classes small, modules small. Size is the number-one predictor of comprehensibility.
2. **Well named.** Names are the primary documentation. See [`names.md`](names.md).
3. **Organized.** Related things near each other; unrelated things far apart. Public API near the top, private helpers below (stepdown rule — see [`functions.md`](functions.md)).
4. **Ordered.** Code should read top-down, each function calling ones declared just below it, in decreasing levels of abstraction.

If a reviewer cannot say yes to all four of these about a change, the change is not clean yet.

## Livability, not perfection

Clean code is not Golden Perfection. It's a **lived-in clean house**, not a show house. You can maintain, expand, and evolve it without degrading its livability. A drop of milk on the counter is fine; an accumulation of crumbs is not. Don't chase perfection; refuse to let the mess build.

## The Primal Conundrum

Developers know messes slow them down, yet feel pressure to make messes to hit deadlines. That pressure is a trap:

- You will not make the deadline by making the mess.
- The mess slows you, your teammates, and every future reader.
- Defend the code with the same passion managers defend the schedule — that is your professional responsibility.

## GDScript / RTV notes

- **Small** in GDScript usually means: functions ≤ ~20 lines, scripts ≤ ~200 lines, scenes with few node-type responsibilities. Big scripts in this repo (`Controller.gd`, `Handling.gd`) are game-code we inherit — don't try to clean those; just write small overrides.
- **Well named** defers to [`../godot/gdscript-style-guide.md`](../godot/gdscript-style-guide.md): `snake_case` for funcs/vars, `PascalCase` for classes, `_leading_underscore` for private.
- **Ordered** fits the Godot convention of: `class_name`, `extends`, `@export`, signals, constants, vars, `_ready` / `_process` / lifecycle, public methods, private methods.
- **Boy Scout Rule** in practice: if a PR touches a function with a confusing name, rename it as part of the PR — don't open a separate "cleanup" PR unless the rename is wide.
