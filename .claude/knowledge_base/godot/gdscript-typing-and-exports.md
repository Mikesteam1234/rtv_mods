# GDScript Static Typing & Exports

> Godot 4.6 | [Basics](gdscript-basics.md) | [Style Guide](gdscript-style-guide.md)

## Static Typing

### Declaring Types

```gdscript
var health: int = 100              # explicit type
var speed := 50.0                  # inferred as float
const MAX_HP: int = 200            # typed constant

func take_damage(amount: int) -> bool:
    health -= amount
    return health <= 0
```

### What Can Be a Type Hint

1. `Variant` — any type (increases readability, not much different from untyped)
2. `void` — return type only, function returns nothing
3. Built-in types (`int`, `float`, `String`, `Vector2`, `Array`, etc.)
4. Native classes (`Object`, `Node`, `Area2D`, `Camera3D`, etc.)
5. Global classes registered with `class_name`
6. Inner classes
7. Enums (stored as `int`, no guarantee value is in the enum set)
8. Constants containing a preloaded class or enum

### Using Custom Classes as Types

```gdscript
# Method 1: preload into a constant
const Rifle = preload("res://weapons/rifle.gd")
var my_rifle: Rifle

# Method 2: class_name (globally registered)
# In rifle.gd:
class_name Rifle
extends Node3D
# Then anywhere:
var my_rifle: Rifle
```

### Return Types

```gdscript
func find_item(ref: Item) -> Item:
    # Must return Item or null
    return inventory.get(ref.id)
```

### Covariance & Contravariance

- **Covariance** (return types): override can return a more specific subtype
- **Contravariance** (parameters): override can accept a less specific supertype

### Safe Lines and Casting

```gdscript
# as keyword — returns null on type mismatch (no error)
var sprite := $Character as Sprite2D

# is keyword — type checking
if entity is Enemy:
    entity.alert()  # compiler knows entity is Enemy here (type narrowing)
```

### Benefits

- Compile-time error detection (catch bugs before running)
- Better autocompletion in the editor
- Optimized opcodes for known types (performance)

---

## Exports

### Basic Usage

```gdscript
@export var health: int = 100
@export var target: Node
@export var texture: Texture2D
```

Exported values are saved with the resource and editable in the inspector.

### Grouping

```gdscript
@export_group("Movement")
@export var speed: float = 300.0
@export var jump_force: float = 500.0

@export_subgroup("Advanced")
@export var air_friction: float = 0.1

@export_category("Combat")
@export var damage: int = 10
```

### String Paths

```gdscript
@export_file var config_path: String
@export_file("*.json") var data_file: String
@export_dir var save_directory: String
@export_multiline var description: String
```

### Numeric Ranges

```gdscript
@export_range(0, 100) var health: int
@export_range(-10, 20, 0.2) var speed: float
@export_range(0, 100, 1, "or_less", "or_greater") var level: int
@export_range(0, 100000, 0.01, "exp") var distance: float
@export_range(0, 1000, 0.01, "hide_slider") var precise: float
@export_range(0, 100, 1, "suffix:m") var altitude: int
@export_range(0, 360, 0.1, "radians_as_degrees") var angle: float
```

### Easing & Colors

```gdscript
@export_exp_easing var transition_speed: float
@export var color: Color
@export_color_no_alpha var solid_color: Color
```

### Nodes

```gdscript
@export var target_node: Node
@export var button: BaseButton          # limits to BaseButton subtypes
@export_node_path("Button", "TouchScreenButton") var btn_path: NodePath
```

### Resources

```gdscript
@export var resource: Resource
@export var animation: AnimationNode    # limits dropdown to this type
```

### Bit Flags

```gdscript
@export_flags("Fire", "Water", "Earth", "Wind") var elements: int = 0
@export_flags("Self:4", "Allies:8", "Foes:16") var targets: int = 0
@export_flags_2d_physics var collision_layers: int
@export_flags_3d_render var render_layers: int
```

### Enums

```gdscript
enum Element {FIRE, WATER, EARTH, WIND}
@export var element: Element

@export_enum("Warrior", "Magician", "Thief") var class_id: int
@export_enum("Slow:30", "Average:60", "Fast:200") var speed: int
@export_enum("Alice", "Bob", "Charlie") var name: String = "Alice"
```

### Arrays

```gdscript
@export var items: Array[PackedScene] = []
@export var ints: Array[int] = [1, 2, 3]
@export var vectors := PackedVector3Array()

# Combined with other annotations
@export_range(-360, 360, 0.001, "degrees") var angles: Array[float] = []
@export_file("*.json") var data_files: Array[String] = []
```

### Storage Without Inspector

```gdscript
var a                  # not stored, not in editor
@export_storage var b  # stored in file, NOT in editor
@export var c: int     # stored in file AND in editor
```

### Custom & Tool Button

```gdscript
@export_custom(PROPERTY_HINT_NONE, "suffix:m") var altitude: float

# Clickable button in inspector (@tool scripts only)
@tool
extends Node
@export_tool_button("Print Hello", "Callable") var btn = do_hello
func do_hello() -> void:
    print("Hello!")
```

### Export Timing

Exported values are assigned **after** `_init()` but **before** `_ready()`. Reading an exported var in `_init()` returns the script default, not the inspector value. Read in `_ready()` or in a setter instead:

```gdscript
@export var max_hp: int = 100:
    set(value):
        max_hp = value
        # This runs when the inspector value is applied

func _init() -> void:
    print(max_hp)  # 100 (default, not inspector value)

func _ready() -> void:
    print(max_hp)  # inspector value
```

## RTV Modding Notes

- Mod scripts can't use `@export` effectively since there's no editor — use constants or runtime configuration instead
- Type hints are especially valuable in mod scripts for catching errors without a test suite
- When extending game scripts, the parent's exported values are already assigned. Your override's `_ready()` sees the inspector-configured values from the `.tscn`. See [core concepts](../reference/core-concepts.md)
