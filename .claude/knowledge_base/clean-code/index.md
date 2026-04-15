# Clean Code — Knowledge Base Index

Distilled from Robert C. Martin, *Clean Code: A Handbook of Agile Software Craftsmanship*, 2nd Edition.

These files summarize the book's rules and rationale in a scannable form. They are *not* a port of the book; they extract the durable principles and, where relevant, translate examples into GDScript 4.6 idioms used in this repo. For repo-specific style authority, defer to [`../godot/gdscript-style-guide.md`](../godot/gdscript-style-guide.md) and [`../godot/best-practices.md`](../godot/best-practices.md).

---

## Part I — Code

| File | Covers | Summary |
|------|--------|---------|
| [first-principles.md](first-principles.md) | Ch 1–3 | What "clean" means; reading vs. writing ratio; Boy Scout Rule; "first make it work, then make it right"; small / well-named / organized / ordered |
| [names.md](names.md) | Ch 4 | Intention-revealing, pronounceable, searchable names; avoid disinformation and encodings; naming by role (function, variable, class, boolean) |
| [comments.md](comments.md) | Ch 5 | Comments are a failure to express; good comments (legal, TODO, intent, warning); bad comments (redundant, misleading, commented-out code) |
| [formatting.md](formatting.md) | Ch 6 | Vertical formatting (openness, density, distance, ordering); horizontal formatting; the newspaper metaphor; team rules |
| [functions.md](functions.md) | Ch 7–11 | Small; do one thing; one level of abstraction; stepdown rule; few arguments; command-query separation; prefer exceptions; be polite to the reader |
| [objects-and-classes.md](objects-and-classes.md) | Ch 12–13 | Object vs. data-structure antisymmetry; Law of Demeter; DTOs; SRP at class scope; cohesion; what a class should contain |
| [testing.md](testing.md) | Ch 14–16 | TDD, TCR, small bundles; F.I.R.S.T.; test DSLs; one-assert guideline; acceptance tests as specifications |

## Part II — Design

| File | Covers | Summary |
|------|--------|---------|
| [simple-design-and-solid.md](simple-design-and-solid.md) | Ch 18–19 | Kent Beck's four rules of simple design; YAGNI; SOLID (SRP, OCP, LSP, ISP, DIP) |

## Part III — Architecture

| File | Covers | Summary |
|------|--------|---------|
| [architecture-and-components.md](architecture-and-components.md) | Ch 20, 23–27 | Component cohesion/coupling; the two values of software; independence; architectural boundaries; the Clean Architecture rings |
| [concurrency.md](concurrency.md) | Ch 22 | Why concurrency is hard; defense principles; keep concurrency out of business logic |

## Part IV — Craftsmanship

| File | Covers | Summary |
|------|--------|---------|
| [craftsmanship.md](craftsmanship.md) | Ch 28–37 | Harm; no defect in behavior or structure; repeatable proof; small cycles; relentless improvement; honest estimates; team; learning |

---

## Applying to this repo

- RTV is GDScript 4.6. Where a Clean Code rule conflicts with an RTV/Godot constraint, the constraint wins. The biggest recurring ones:
  - **`super._<lifecycle>()` is mandatory** in overrides. Never flag as dead code.
  - **Autoloads act as global singletons** (`GameData`, `Simulation`, etc.). DIP is often satisfied by accessing them via well-named wrappers rather than constructor injection.
  - **GDScript has no exceptions** in the Java sense. "Prefer exceptions over error codes" becomes "prefer `assert`/`push_error` + explicit `Result`-style returns over silent nulls".
  - **Signals replace many getter/observer patterns.** Don't force traditional observer classes.
- For code reviews, prefer the `code-reviewer` agent in [`../../agents/code-reviewer.md`](../../agents/code-reviewer.md). It synthesizes these files with the Godot/GDScript and RTV-specific knowledge bases.
