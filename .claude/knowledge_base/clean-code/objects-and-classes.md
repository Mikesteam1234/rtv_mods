# Objects and Classes

*From chapters 12–13 ("Objects and Data Structures", "Clean Classes").*

## Data Abstraction

Hiding implementation is not merely putting a getter/setter on every field. That's not abstraction — it's exposure with extra ceremony. True abstraction means exposing an interface that lets a user manipulate the *essence* of the data without knowing its representation.

- **Concrete:** `getX(): double; getY(): double; setCartesian(x, y); setPolar(r, θ)` — every internal form leaks.
- **Abstract:** `makePolar(); makeCartesian(); getR(); getTheta(); getX(); getY()` — the caller doesn't know which form is stored.

Design the interface so callers don't know (and don't care) how the data is physically organized.

## Object / Data-Structure Antisymmetry

Two complementary definitions, and they are virtual opposites:

- **Objects** hide data behind abstractions and expose functions that operate on that data.
- **Data structures** expose their data and have no meaningful functions.

Consequences:

| | Add a new function | Add a new type |
|---|---|---|
| **Procedural code** (data structures + free functions) | Easy — no existing data changes | Hard — every function must change |
| **OO code** (polymorphic objects) | Hard — every class must change | Easy — add a new class, no existing code changes |

**The things that are hard for OO are easy for procedures, and vice versa.** Mature programmers reject "everything is an object" — sometimes you genuinely want a dumb data structure with free functions operating on it.

### Hybrids are the worst of both worlds

A class with both significant behavior *and* public fields (or equivalent getters/setters) is a hybrid. It's hard to add new functions *and* hard to add new types. Decide: is this an object, or a data structure? Don't split the difference.

## The Law of Demeter

**A method `f` of class `C` should only call methods of:**

- `C` itself
- Objects created by `f`
- Objects passed as arguments to `f`
- Objects held in instance variables of `C`

**The method should not invoke methods on objects returned by the above.** In short: *be shy. Talk to friends, not strangers.*

Short form: **"OO in one sentence: keep it DRY, Shy, and Tell the Other Guy."** — Dave Thomas & Andy Hunt.

### Train wrecks

```
outputDir = ctxt.getOptions().getScratchDir().getAbsolutePath()
```

This is a train wreck. It's a violation when `ctxt`, `Options`, `ScratchDir` are **objects** (abstractions hiding data). It's fine when they're **data structures** (public fields). This is why hybrids are terrible: you can't tell.

### Tell, don't ask

Don't fetch data from `ctxt` to operate on it in the caller. Tell `ctxt` to do the thing:

```
# Before (Demeter violation):
out_path = ctxt.get_options().get_scratch_dir().get_absolute_path()
stream = FileStream.new(out_path + "/" + class_name)

# After:
stream = ctxt.create_scratch_file_stream(class_name)
```

## Data Transfer Objects (DTOs)

A class with public fields and no functions — useful at boundaries (DB rows, network payloads, config files). Don't add getters/setters just to feel OO-pure; that's noise.

A reasonable progression: raw DTO at the boundary → domain object deeper inside the system.

### Active Record

A DTO that also has navigation/persistence methods (`save`, `find`). Treat as a data structure, *not* an object. Putting business logic on an Active Record creates hybrid pain. Keep business logic in separate domain objects that use the Active Record as a data source.

## Classes

### Classes Should Be Small

Like functions. But "small" for a class isn't line count — it's **responsibilities**.

- **The Single Responsibility Principle (SRP):** a class should have one, and only one, reason to change.
- A class name should describe what it does succinctly. If you need "and", "or", "also" to describe it, it's doing too much.
- A class with the word `Processor`, `Manager`, or `Super` often indicates unfortunate aggregation of responsibilities. These words are vague catch-alls.

### Organization / Standard form

A class's source code should be organized top-down:

1. List of variables (public static constants → private static → private instance).
2. Public functions.
3. Private utilities (placed just below the public method that calls them — stepdown rule).

### Encapsulation

- Tests need to get at internals sometimes. Relax from `private` to package-level for the sake of testability — but this is a last resort. Losing encapsulation is a cost.
- Don't expose fields publicly if the class has behavior; expose intent-revealing methods.

### Cohesion

A class is cohesive when its methods and fields are tightly related. A rule of thumb: most methods should manipulate most of the instance variables. When a subset of methods manipulates a subset of fields, that's a hint to **split the class**.

Low cohesion → extract the cohesive subset into its own class. This tends to create many small classes; that is not a bug.

### Organizing for Change

A system ideally needs *only structural growth*, not *structural modification*, to add features — the Open-Closed Principle (see [`simple-design-and-solid.md`](simple-design-and-solid.md)).

- Depend on abstractions (interfaces, abstract base classes), not concrete classes.
- Isolate volatile external dependencies (databases, external APIs) behind an interface you own. Your domain code talks to your abstraction; a thin adapter talks to the volatile thing.

## GDScript / RTV notes

- GDScript is OO but loose. You can always add a new method to an object at runtime (with `set_meta` / scripting tricks) — resist; it breaks static analysis.
- **`class_name`** makes a script globally-named and gives it a type usable in `@export` and static typing. Use it for domain objects, not for internal helpers.
- **Inner classes** (`class Foo extends Node: ...` inside a script) are fine for small tightly-coupled helpers; prefer them to scattering many tiny files.
- **Resources (`Resource` subclasses)** are GDScript's natural **DTO**. `ItemData`, `WeaponData`, `LootTable` in RTV are DTOs. Don't put business logic on them — put it on nodes that *consume* them.
- **Nodes are objects**, with real behavior. Keep business logic on nodes; hold state on resources.
- **Law of Demeter in Godot:** `get_node("..//UI/Panel/Label").text = ...` is a train wreck across the scene tree. Prefer:
  - Expose a method on a parent node (`parent.set_label_text("hi")`).
  - Or use a signal (`bubble_up: label_requested.emit("hi")`).
  - **Exception:** `@onready var label: Label = $UI/Panel/Label` pulls the node once, then uses `label.text = ...` — that's *not* a Demeter violation; the node is now an instance variable.
- **RTV autoloads** (`GameData`, `Simulation`) are effectively global singletons. Accessing them from anywhere *is* a kind of Demeter violation, but it's the platform convention and unavoidable. Scope the access — touch them at high-level nodes, pass values down; don't let every leaf reach into them.
- **Signals as "Tell, Don't Ask":** emitting `damage_taken.emit(hp)` is idiomatic "tell the other guy". Resist adding a separate query API that callers `await`.
