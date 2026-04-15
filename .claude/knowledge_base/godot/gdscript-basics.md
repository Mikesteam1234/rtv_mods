# GDScript Basics

> Godot 4.6 | [Typing & Exports](gdscript-typing-and-exports.md) | [Style Guide](gdscript-style-guide.md)

GDScript is a high-level, object-oriented, gradually typed language built for Godot. It uses indentation-based syntax similar to Python but is entirely independent from it.

## Keywords

`if` `elif` `else` `for` `while` `match` `when` `break` `continue` `pass` `return` `class` `class_name` `extends` `is` `in` `as` `self` `super` `signal` `func` `static` `const` `enum` `var` `breakpoint` `preload` `await` `assert` `void`

Constants: `PI`, `TAU`, `INF`, `NAN`

## Operators (by precedence, highest first)

| Operator | Description |
|----------|-------------|
| `()` `x[i]` `x.attr` `foo()` | Grouping, subscription, attribute, call |
| `await x` | Await signal/coroutine |
| `x is Node` / `x is not Node` | Type checking |
| `x ** y` | Power (left-associative) |
| `~x` `+x` `-x` | Bitwise NOT, identity, negation |
| `* / %` | Multiply, divide, remainder (**int-only** for `%`) |
| `+ -` | Add/concatenate, subtract |
| `<< >>` | Bit shift |
| `&` `^` `\|` | Bitwise AND, XOR, OR |
| `== != < > <= >=` | Comparison |
| `in` `not in` | Inclusion |
| `not` / `!` | Boolean NOT |
| `and` / `&&` | Boolean AND |
| `or` / `\|\|` | Boolean OR |
| `val if cond else val` | Ternary (right-associative) |
| `x as Type` | Type cast |
| `= += -= *= /= **= %= &= \|= ^= <<= >>=` | Assignment |

> **Note:** `5 / 2 == 2` (integer division). Use `5.0 / 2` or `float(5) / 2` for float result. The `%` operator is int-only; use `fmod()` for floats.

## Literals

| Syntax | Type |
|--------|------|
| `null` | Null (Object-derived types only) |
| `true` `false` | bool |
| `45` `0x8f51` `0b101010` `12_345` | int (64-bit) |
| `3.14` `58.1e-10` | float (64-bit) |
| `"Hello"` `'Hi'` `"""multi"""` `r"raw"` | String |
| `&"name"` | StringName |
| `^"Node/Label"` | NodePath |
| `$NodePath` | Shorthand for `get_node("NodePath")` |
| `%UniqueNode` | Shorthand for `get_node("%UniqueNode")` |

Integers and floats support `_` separators: `1_000_000`, `0xff_00_ff`.

## Built-in Types

**Primitives:** `null`, `bool`, `int`, `float`, `String`, `StringName`, `NodePath`

**Vectors:** `Vector2`, `Vector2i`, `Vector3`, `Vector3i`, `Vector4`, `Vector4i`, `Rect2`, `Rect2i`, `Transform2D`, `Transform3D`, `Basis`, `Quaternion`, `AABB`, `Plane`, `Projection`

**Engine:** `Color`, `RID`, `Object`, `Signal`, `Callable`

**Containers:** `Array`, `Dictionary`, packed arrays (see below)

Built-in types are stack-allocated and passed by value, except `Object`, `Array`, `Dictionary`, and packed arrays (passed by reference).

## Arrays

```gdscript
var arr: Array = [1, 2, 3]
var b: int = arr[1]         # 2
var c: int = arr[-1]        # 3 (negative indexing)
arr.append(4)

# Typed arrays
var ints: Array[int] = [1, 2, 3]
var nodes: Array[Node] = []
# Nested typed arrays (Array[Array[int]]) NOT supported
```

**Packed arrays** (more memory-efficient, faster iteration):
`PackedByteArray`, `PackedInt32Array`, `PackedInt64Array`, `PackedFloat32Array`, `PackedFloat64Array`, `PackedStringArray`, `PackedVector2Array`, `PackedVector3Array`, `PackedVector4Array`, `PackedColorArray`

## Dictionaries

```gdscript
var d: Dictionary = {"key": "value", 2: [1, 2, 3]}
d["new_key"] = 42

# Lua-style syntax (string keys only, no quotes needed)
var d2 := {name = "Sword", damage = 10}

# Typed dictionaries (Godot 4.4+)
var scores: Dictionary[String, int] = {"Alice": 100, "Bob": 85}
```

## Variables

```gdscript
var a                      # null by default
var b: int = 5             # explicit type
var c := "Hello"           # inferred type (String)
var d: Vector2             # default Vector2(0, 0)

static var count: int = 0  # shared across all instances
```

**Initialization order:** (1) type defaults → (2) specified values top-to-bottom → (3) `_init()` → (4) exported values → (5) `@onready` vars → (6) `_ready()`

## Casting

```gdscript
var sprite := $Character as Sprite2D  # null if wrong type
var n: int = "123" as int             # forced conversion
```

## Constants & Enums

```gdscript
const MAX_SPEED: float = 120.0
const TILE = preload("res://tile.tscn")

# Anonymous enum — constants in current scope
enum {IDLE, RUNNING, JUMPING}  # 0, 1, 2

# Named enum — creates a Dictionary-like type
enum State {MENU = 0, GAME = 1, PAUSE = 2}
# Access: State.GAME, State.keys(), State.values()
```

## Functions

```gdscript
func my_func(a: int, b: String = "default") -> int:
    return a + b.length()

func void_func() -> void:
    print("no return value")

# One-liner
func square(x: float) -> float: return x * x

# Lambda
var double := func(x: int) -> int: return x * 2
double.call(5)  # 10

# Static function (no access to self or instance vars)
static func helper(x: int) -> int:
    return x * 2

# Variadic (Godot 4.5+)
func log_all(...args: Array) -> void:
    for arg in args:
        print(arg)
```

Lambdas capture local variables **by value** at creation time.

Functions are first-class via `Callable`: `var fn: Callable = my_func` then `fn.call(args)`.

## Control Flow

### if / elif / else

```gdscript
if health <= 0:
    die()
elif health < 20:
    warn_low_health()
else:
    pass

# Ternary
var label := "dead" if health <= 0 else "alive"
```

### for

```gdscript
for item: String in inventory:
    print(item)

for i in range(10):          # 0..9
for i in range(2, 8, 2):    # 2, 4, 6
for key in dictionary:       # iterates keys
for c in "Hello":            # iterates characters
```

### while

```gdscript
while queue.size() > 0:
    process(queue.pop_front())
```

### match

```gdscript
match action:
    "jump":
        jump()
    "attack", "special":
        attack()
    _:
        idle()

# Pattern binding and guards
match point:
    [var x, var y] when x == y:
        print("On diagonal")
    [var x, var y]:
        print("At %s, %s" % [x, y])

# Array/dictionary patterns
match data:
    [1, 3, ..]:          # open-ended array
        pass
    {"name": var n, ..}: # open-ended dictionary
        print(n)
```

## Classes

```gdscript
# A file IS a class. Unnamed — referenced by path.
extends Node

# Named class — globally accessible
class_name MyClass
extends Node

# Inheritance
extends "res://path/to/base.gd"

# Constructor
func _init() -> void:
    pass

# Override parent method
func _ready() -> void:
    super()  # call parent's _ready

func attack() -> void:
    super.attack()  # call specific parent method

# Type checking
if entity is Enemy:
    entity.alert()

# Inner class
class InnerThing:
    var value: int = 10

# Abstract (Godot 4.6+)
@abstract
class_name Shape
extends Node

@abstract
func area() -> float:
    pass
```

## Annotations

| Annotation | Purpose |
|------------|---------|
| `@export` | Expose property to editor inspector |
| `@export_range(min, max)` | Numeric range in inspector |
| `@onready` | Defer init until `_ready()` |
| `@tool` | Run script in editor |
| `@icon("path")` | Custom class icon |
| `@abstract` | Mark class/method as abstract |
| `@static_unload` | Allow script unloading with static vars |

See [Typing & Exports](gdscript-typing-and-exports.md) for full `@export` reference.

## Comments & Code Regions

```gdscript
# Regular comment
## Documentation comment (shows in inspector tooltips and docs)

#region Movement Logic
func move() -> void:
    pass
#endregion
```

## RTV Modding Notes

- Override scripts use `extends "res://Scripts/SomeScript.gd"` — the path must match the decompiled game script exactly
- `super()` is critical in overrides: skipping it in `_ready`, `_process`, `_input`, etc. breaks the base game and other mods' override chains. See [compatibility guide](../guides/compatibility.md)
- `class_name` on override scripts causes Godot bug #83542 — the script becomes only overridable once. Avoid `class_name` in mod scripts. See [advanced techniques](../techniques/advanced-techniques.md)
- `match` is useful for handling RTV's enum-heavy systems (item types, AI states). See [game internals](../game-internals/index.md)
