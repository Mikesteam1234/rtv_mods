# Architecture & Components

*From chapter 20 ("Component Principles") and chapters 23–27 ("The Two Values of Software", "Independence", "Architectural Boundaries", "Clean Boundaries", "The Clean Architecture").*

## The two values of software

A piece of software has two values:

1. **Behavior.** What the system does for the user today.
2. **Structure.** The shape of the system — how easy it is to change.

**Structure is the more important of the two**, because it's structure that makes software *soft*. A system that works today but is impossible to change is a system that has lost the primary reason software was invented.

**Urgent feature requests feel more important** than "refactor to keep changes cheap," but they are not. Managers prioritize behavior; professionals protect structure.

## What architecture is for

> "A good architecture maximizes the number of decisions *not* made."

The purpose of architecture is not to make the system work — terrible architectures work fine. The purpose is to **support the lifecycle**: development, deployment, operation, maintenance. Concretely: minimize the lifetime cost of change.

The strategy: **leave as many options open as possible, for as long as possible.**

Things you should be able to defer:
- Database choice (relational vs. document vs. flat files).
- Web / UI framework.
- Network protocol (REST, GraphQL, gRPC).
- DI container and other plumbing.

Achieve this by separating **policy** (business rules, what the system *is*) from **detail** (database, UI, framework, protocol — things that don't affect business rules).

## Four things a good architecture supports

1. **Use cases** of the system. A shopping-cart application should *look like* a shopping-cart application — cart, checkout, and inventory should be first-class top-level elements, not buried inside a pile of framework code.
2. **Operation.** Throughput and latency demands. Architecture leaves open the choice of monolith / threads / processes / microservices.
3. **Development.** Conway's Law + SRP: partition the system into independently-developable components so teams don't step on each other.
4. **Deployment.** Immediate deployment — no manual scripting, no "copy this file to that server, then run these three commands". The build produces an artifact that runs.

## Component cohesion — which classes go into which component?

Three principles, in tension:

### REP — Reuse/Release Equivalence Principle

> "The granule of reuse is the granule of release."

A component must be versioned, tracked, and released as a unit. Classes within it share a theme — a reusable release makes sense as a thing.

### CCP — Common Closure Principle

> "Gather into components those classes that change for the same reasons and at the same times. Separate into different components those that change for different reasons."

**This is SRP at the component level.** If two classes always change together, they belong together.

### CRP — Common Reuse Principle

> "Don't force users of a component to depend on things they don't need."

If component A uses component B, A depends on *all* of B — even the parts of B it doesn't use, because any change to B forces a rebuild/retest of A. So don't put unrelated classes into B together.

**This is ISP at the component level.** "Don't depend on things you don't need."

### Tension

- REP and CCP are **inclusive** — push components larger.
- CRP is **exclusive** — pushes components smaller.
- Find a position that suits the project's current phase. Early projects favor CCP (developability); mature, externally-consumed libraries favor REP (reusability) and CRP.

Expect the partitioning to **evolve over time**. Component structure is not a one-time up-front decision.

## Component coupling

### ADP — Acyclic Dependencies Principle

**No cycles in the component dependency graph.** Cycles cause the "morning-after syndrome" — someone changed something last night that your code depends on, and now nothing builds.

Fix: partition into releasable components, each a DAG node. When a cycle appears, break it — commonly via DIP: introduce an abstraction in one of the components that the other implements.

### SDP — Stable Dependencies Principle

Components should depend in the direction of greater stability. Don't let a stable (hard-to-change) component depend on a volatile one — change ripples up through the whole system.

### SAP — Stable Abstractions Principle

A stable component should be abstract (interfaces / abstract classes), so that its stability doesn't freeze the system. A volatile component can afford to be concrete. Graphed: stability and abstractness should rise together.

## The Clean Architecture

A synthesis of Hexagonal Architecture, DCI, BCE, and Ports-and-Adapters. Concentric layers:

1. **Entities** (innermost) — enterprise-wide business rules. Least likely to change. Don't know anything about the outside world.
2. **Use Cases** — application-specific business rules. Orchestrate entities. Don't know about UI, DB, or frameworks.
3. **Interface Adapters** — MVC, presenters, views, controllers; SQL-mapping; adapters to external services. Convert between use-case-friendly and outside-world-friendly formats.
4. **Frameworks & Drivers** (outermost) — the web, the database, the UI toolkit. Glue code only.

### The Dependency Rule

**Source code dependencies must only point inward**, toward higher-level policies.

- An inner circle must never mention the name of anything in an outer circle — no functions, no classes, no types, not even data formats.
- To allow **flow of control** to cross outward (use case → presenter) while **source dependencies** point inward, invert with DIP: the inner circle defines an interface (e.g. `UseCaseOutputPort`); the outer circle implements it.
- Data crossing a boundary should be plain data structures (DTOs, dicts, function args). Never pass an ORM row inward — that would leak the outer-circle data format.

### Result: the system is

- **Independent of frameworks.**
- **Testable** (business rules testable without UI / DB / network).
- **Independent of UI.**
- **Independent of the database.**
- **Independent of any external agency.**

The number of circles isn't sacred; four is typical. More are fine. The Dependency Rule applies regardless.

## Clean Boundaries

When you cross a boundary (process, network, or even just architectural layer), introduce a **boundary object** you own:

- Wrap third-party APIs behind your own interface.
- Keep your code talking to your interface; only the thin adapter talks to the third party.
- When the third party changes (breaking API, license change, you swap vendors), only the adapter changes.

## GDScript / RTV notes

- **This repo is not a business application** — Clean Architecture's four-circle model doesn't map cleanly. But the underlying rule (**keep policy independent of detail**) still applies.
- **Game engine as the outer circle.** Godot *is* the framework / driver layer. Write mod logic so that the "essence" (e.g., "a crouch state is variable-height", "a quick-exit shortcut should return to main menu") is expressed in a way independent of which Godot node emitted the event.
  - In practice: small helper classes / `Resource`s carry the policy; thin scripts subscribed to Godot signals call the helpers.
- **Mod boundaries.** Each mod folder (`QuickExit/`, `VariableCrouch/`, etc.) is a component. They should not depend on each other. If two mods share logic, extract a *library mod* (cohesion), but don't couple gameplay-level mods together.
- **Override boundary.** A `take_over_path` override is a boundary with the base-game script. Keep the override thin — delegate to your own (non-override) helpers as soon as the flow lets you. That way, when the decompiled target script changes in a game update, only the override needs attention.
- **DTOs in Godot** are `Resource` subclasses — `ItemData`, `LootTable`, `WeaponData`. They cross boundaries cleanly. Don't attach behavior to them; the behavior lives on nodes that consume the resource.
- **Component cohesion in this repo's mods:** a mod is in the "CCP position" — all files in it change at the same time for the same reason. That's why each mod is a separate folder, each separately released.
- **ADP / cycles** are rare here because mods don't import each other. If you find yourself wanting one mod to depend on another, you're probably wrong — extract shared code into a library mod instead.
