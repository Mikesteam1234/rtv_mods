# Simple Design & SOLID

*From chapters 18 ("Simple Design") and 19 ("The SOLID Principles").*

## YAGNI — "You Aren't Gonna Need It"

Every time you're tempted to add a hook "in case we need it later", ask: **What if I'm not gonna need it?**

- Cost of leaving the hook out and adding it later (given tests + refactoring skill): usually small.
- Cost of carrying the hook year after year (design weight, extra code to understand, extra test surface): steady, compounding.
- Odds of actually needing it: usually low.

Good design is *discerning* about future flexibility. Not every guess should become a configuration point.

## Kent Beck's Four Rules of Simple Design (in priority order)

1. **Passes all the tests** (covered by tests).
2. **Reveals intent** (maximum expression).
3. **No duplication.**
4. **Fewest elements** (minimum size).

Work them top to bottom.

### 1. Covered by tests

- **100% coverage is the only reasonable goal** — asymptotically. You may not reach it; that's no excuse for not trying on every check-in.
- **Testable code is decoupled code.** Writing an isolated test *forces* a decoupled design. Tests are a design activity, not just a verification activity.
- Without tests, the other three rules are impractical, because they rely on fearless refactoring — which requires a safety net.

### 2. Reveals intent

- Names matter. Abstraction levels matter (see [`functions.md`](functions.md) on the stepdown rule).
- Expressive code separates **policy** (high-level rules, "pay each employee on their payday") from **mechanism** (the switch on employee type). Mixing them obscures the essential truth of the program.
- Kent Beck's original phrasing was "the system (code *and* tests) must communicate everything you want to communicate." Tests document how code is used; code documents what it does. They're paired.

### 3. Minimize duplication

- Duplication → fragility. A change has to be made in N places; you'll miss one.
- **But:** not all similar code is duplication. **Accidental duplication** is code that happens to look identical today but changes for different reasons tomorrow — leave it alone; it will dissolve.
  - Real duplication has *convergent* intent.
  - Accidental duplication has *divergent* intent.
- Hard cases: similar traversal code across the system. Extract with strategies / lambdas / template method so the traversal lives once.

### 4. Fewest elements (after the above)

After you've got tests, expressiveness, and no-duplication, reduce the number of classes, functions, and lines. But only *after* — compressing prematurely destroys expressiveness.

---

## SOLID

Five principles for mid-level structure (how classes and their relationships should be shaped so the system tolerates change). The word "class" is used loosely — these apply to any coupled grouping of functions and data.

### SRP — Single Responsibility Principle

> "Each software module should have one, and only one, reason to change."

**Commonly misunderstood.** It does *not* say "a module does one thing" — that's a different, function-level rule (see [`functions.md`](functions.md)).

SRP is about **stakeholders / actors**. If the accounting department and the operations department both need changes to the same class, for different reasons, SRP is violated — those responsibilities should live in different classes.

Symptoms of violation:
- Two unrelated stakeholders both request changes to the same file.
- The class has methods that use disjoint subsets of fields (cohesion red flag).
- You find yourself bracing for conflict when merging changes from different features.

### OCP — Open-Closed Principle

> "Software entities should be open for extension, but closed for modification."

Design so that **new behavior is added by writing new code**, not by editing existing code. Practically: depend on abstractions; let new concrete implementations extend the abstraction without touching it.

Classic shape: plugin architecture. High-level policy depends on an interface; low-level plugins implement it. Adding a new plugin requires zero changes to the high-level code.

### LSP — Liskov Substitution Principle

> "Subtypes must be substitutable for their base types."

If `Duck` is a subtype of `Bird` and a function accepts a `Bird`, it must work just as well when given a `Duck`. Classic counter-example: `Square` extending `Rectangle` — setting width on a `Square` must also change its height, which breaks code written against `Rectangle`.

Practically: subclass overrides must preserve the contract (preconditions no stronger, postconditions no weaker, invariants preserved). A subclass that throws on methods the base supports is an LSP violation.

### ISP — Interface Segregation Principle

> "Clients should not be forced to depend on methods they do not use."

A fat interface with 20 methods, where most clients only care about 3, forces every client to rebuild whenever any of the other 17 changes. Split the interface by role — each client depends only on the role it uses.

### DIP — Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."
> "Abstractions should not depend on details. Details should depend on abstractions."

Invert the natural direction of source-code dependency so it runs **opposite** the direction of control flow at runtime. High-level policy declares an interface; low-level detail implements it. The policy does not import the detail; the detail imports the policy.

Result: you can swap implementations of the low level without touching the high level.

---

## GDScript / RTV notes

- **Tests-first rule** softens in this repo — there is no test suite. The equivalent discipline is: *can you load the mod in-game and verify the change in under 60 seconds?* If deploy-and-play cycle time is too slow, invest in making it faster (`Scripts/deploy_mod.py`).
- **SRP in GDScript** often means: one script per node type, one script per responsibility per autoload. If an autoload has "both input handling *and* save game formatting", split it.
- **OCP in GDScript** is hard because `take_over_path()` replaces a target script wholesale; there is no "extend without modify" of baked scripts. The OCP-friendly shape is: your override's script delegates to small, swappable internal objects / resources. Adding a new behavior means adding a new `Resource` subclass, not editing the override.
- **LSP + GDScript inheritance:** `super._ready()`, `super._input(e)`, etc., are the contract. Not calling `super` breaks the base's postconditions and is an LSP violation, besides being an RTV-specific gotcha.
- **ISP + signals:** signals segregate interfaces naturally. A node emits `damage_taken` and `healed`; receivers connect only to the signals they care about. Don't build one fat "notify" signal carrying a payload type discriminator.
- **DIP + autoloads:** autoloads *are* the lowest-level detail in a Godot codebase, yet they tend to be imported everywhere (high-level policy ends up depending on `GameData`). To salvage DIP: inject an abstraction at the top (`game_state: IGameState`) and default to `GameData` only at the root node. Often in practice this ceremony is not worth it in small mods — note the trade-off and proceed.
- **Duplication across mods** (e.g., similar override boilerplate in `QuickExit`, `VariableCrouch`, etc.) is often *accidental* duplication — each mod changes for different reasons. Don't extract a "mod helper" library just because the shapes look similar.
