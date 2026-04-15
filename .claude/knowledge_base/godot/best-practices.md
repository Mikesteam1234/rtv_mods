# Best Practices

> Godot 4.6 | [Scene Tree](scene-tree-and-nodes.md) | [Style Guide](gdscript-style-guide.md)

## Node Communication Patterns

The single most important pattern in Godot: **call down, signal up**.

### Call Down

Parents call methods on children directly. The parent knows its children exist because it created or composed them.

```gdscript
# Parent knows about its children
func start_combat() -> void:
    $Player.enter_combat_mode()
    $EnemySpawner.start_spawning()
    $HUD.show_combat_ui()
```

### Signal Up

Children emit signals when something happens. They don't know or care who's listening.

```gdscript
# In player.gd
signal health_changed(new_health: int)
signal died

func take_damage(amount: int) -> void:
    health -= amount
    health_changed.emit(health)
    if health <= 0:
        died.emit()

# In parent scene
func _ready() -> void:
    $Player.health_changed.connect($HUD.update_health_bar)
    $Player.died.connect(_on_player_died)
```

### Sideways Communication

For siblings or unrelated nodes, use:
- **Groups:** `get_tree().call_group("enemies", "retreat")`
- **Event bus autoload:** `Events.player_died.emit()`
- **Owner:** `owner.get_node("Sibling")`

### Why This Matters

- Nodes stay reusable — a `Player` scene works in any parent
- Dependencies flow one direction (parent → child)
- Signals decouple without sacrificing type safety
- Testing is easier — instantiate a scene without its usual parent

## Data Preferences

### Custom Resources Over Raw Data

Instead of parsing JSON/CSV, use custom `Resource` subclasses:

```gdscript
class_name ItemData
extends Resource

@export var id: String
@export var display_name: String
@export var icon: Texture2D
@export var weight: float
@export var value: int
```

**Advantages:**
- Auto-serialization (`.tres` files, version-control friendly)
- Inspector editing with validation
- Type safety and autocompletion
- Can have methods, getters/setters, signals
- Nested sub-resources

### When to Use Each

| Data Type | Best For |
|-----------|----------|
| Custom `Resource` | Game data (items, weapons, stats), anything that benefits from inspector editing |
| `Dictionary` | Dynamic data, JSON interop, unknown keys at compile time |
| `ConfigFile` | User settings, simple key-value persistence |
| Nodes | Data that needs tree presence (timers, signals from tree events) |

## Logic Preferences

### Composition Over Inheritance

Attach behaviors through child nodes instead of deep class hierarchies:

```
# Instead of:   Player → Character → MovingEntity → DamageableEntity → Node3D
# Do:
Player (CharacterBody3D)
├── HealthComponent      # handles damage, death
├── InventoryComponent   # manages items
├── MovementComponent    # handles physics movement
└── InteractionComponent # raycasts for interactables
```

Each component is a separate script on a child node. Components can be reused across different entities (enemies can also have `HealthComponent`).

### When Inheritance Works

Use inheritance when you have the **same type with variations**:

```gdscript
# Base weapon with shared logic
class_name Weapon
extends Node3D

func fire() -> void: pass
func reload() -> void: pass

# Specific weapons override behavior
class_name Rifle
extends Weapon

func fire() -> void:
    # rifle-specific firing
```

### Keep Scripts Focused

One script = one responsibility. If a script handles movement AND inventory AND combat AND UI, split it.

## Scenes vs Scripts

### Use a Scene When

- You need a visual layout (positioned nodes)
- Multiple nodes compose a behavior
- You want to preview in the editor
- Non-programmers need to edit it

### Use a Script Alone When

- Pure logic or data (utility functions, custom resources)
- No visual representation needed
- The "thing" is conceptually one node, not a tree

### Scenes as Prefabs

Design reusable scenes like components:

```gdscript
# health_bar.tscn — self-contained, works anywhere
# In any parent:
var health_bar: PackedScene = preload("res://ui/health_bar.tscn")
var bar: Control = health_bar.instantiate()
$UI.add_child(bar)
```

## Interfaces in GDScript

GDScript has no formal `interface` keyword. Use duck typing patterns:

### has_method()

```gdscript
func interact_with(target: Node) -> void:
    if target.has_method("interact"):
        target.interact(self)
```

### Groups as Tags

```gdscript
func take_damage(amount: int) -> void:
    if is_in_group("invulnerable"):
        return
    health -= amount
```

### The `is` Operator

```gdscript
func collect(item: Node) -> void:
    if item is Consumable:
        item.consume(self)
    elif item is Equipment:
        item.equip(self)
```

### Convention-Based Interfaces

Document expected methods and rely on the static type system:

```gdscript
# Any node with this method is "damageable"
func take_damage(amount: int, source: Node) -> void:
    pass
```

## Common Anti-Patterns

| Anti-Pattern | Better Approach |
|-------------|-----------------|
| Deep inheritance chains (5+ levels) | Composition with child nodes |
| Overusing autoloads for everything | Regular nodes; promote to autoload only when needed |
| Polling in `_process` when a signal exists | Connect to the signal instead |
| Hardcoded `$Long/Path/To/Node` | `%UniqueNode` or `get_node_or_null()` |
| God scripts (1000+ lines, multiple responsibilities) | Split into focused components |
| Storing game state in scene nodes | Custom Resources or dedicated autoload |

## RTV Modding Notes

- "Call down, signal up" applies to mod overrides too: your override script signals to your mod's autoload; the autoload calls down to other nodes
- Duck typing (`has_method`) is essential for mod compatibility — check before calling methods that other mods might add or remove
- RTV's `Database` autoload is the central data store. Access game data through it rather than walking the scene tree. See [autoloads and boot](../game-internals/autoloads-and-boot.md)
- Composition is preferred for mod features: add child nodes to existing game nodes rather than trying to cram everything into one override script
