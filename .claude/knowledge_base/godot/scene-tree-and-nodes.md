# Scene Tree & Nodes

> Godot 4.6 | [Signals & Groups](signals-and-groups.md) | [Resources](resources-and-loading.md)

## SceneTree Architecture

The `SceneTree` is Godot's main loop. It manages all nodes in a tree hierarchy rooted at a `Window` node (accessible via `get_tree().root`). Your main scene is a child of this root.

```
root (Window)
├── Autoload1
├── Autoload2
└── MainScene (current_scene)
    ├── Player
    │   ├── Sprite2D
    │   └── CollisionShape2D
    └── Level
```

Operations follow **tree order** (top-to-bottom, depth-first), with one exception: `_ready()` uses **post-order** (children first, then parent).

## Node Lifecycle

### _enter_tree()

Called every time the node enters the scene tree (pre-order). Children may not be ready yet. Can fire multiple times if a node is removed and re-added.

```gdscript
func _enter_tree() -> void:
    print("Entered tree")
```

### _ready()

Called **once** per node lifetime, after all children have entered and received their own `_ready()`. Safe to call `get_node()` here. This is where you set up references and initial state.

```gdscript
func _ready() -> void:
    var label: Label = get_node("UI/Label")
    label.text = "Ready"
```

### _process(delta)

Called every **rendered frame**. `delta` is the time since the last frame (variable). Use for visual updates, UI, non-physics logic.

```gdscript
func _process(delta: float) -> void:
    rotation += spin_speed * delta
```

### _physics_process(delta)

Called every **physics tick** (fixed timestep, default 60/s). `delta` is constant. Use for movement, collision detection, physics-related logic.

```gdscript
func _physics_process(delta: float) -> void:
    velocity += gravity * delta
    move_and_slide()
```

### _exit_tree()

Called when the node is about to leave the scene tree. Clean up connections, remove from groups, etc.

```gdscript
func _exit_tree() -> void:
    print("Leaving tree")
```

### Full Order

1. `_enter_tree()` — pre-order (parent first)
2. `NOTIFICATION_POST_ENTER_TREE`
3. `_ready()` — post-order (children first)
4. `_process()` / `_physics_process()` — every frame/tick
5. `_exit_tree()` — when removed (reverse order)
6. `NOTIFICATION_PREDELETE` — when freed

## Scene Instancing

Scenes are `PackedScene` resources. To create nodes from a scene at runtime:

```gdscript
# Compile-time (constant path)
var bullet_scene: PackedScene = preload("res://scenes/bullet.tscn")

# Runtime (variable path)
var scene: PackedScene = load("res://scenes/" + scene_name + ".tscn")

# Create an instance and add to tree
var bullet: Node = bullet_scene.instantiate()
bullet.position = muzzle.global_position
add_child(bullet)
```

The node doesn't enter the tree (and `_ready` doesn't fire) until `add_child()` is called.

## Node References

### $ shorthand

```gdscript
# These are equivalent:
var sprite: Sprite2D = get_node("Character/Sprite2D")
var sprite: Sprite2D = $Character/Sprite2D
```

### % unique names

Mark a node as "unique name in owner" in the editor, then access it from anywhere in the scene:

```gdscript
var hud: Control = %HUD  # same as get_node("%HUD")
```

### get_node_or_null()

Returns `null` instead of crashing if the node doesn't exist:

```gdscript
var player: Node = get_node_or_null("Player")
if player:
    player.heal(10)
```

### @onready

Defers variable initialization until `_ready()`:

```gdscript
@onready var label: Label = $UI/Label
@onready var health_bar: ProgressBar = %HealthBar
```

## Changing Scenes

```gdscript
# By file path
get_tree().change_scene_to_file("res://scenes/game.tscn")

# By preloaded PackedScene
var next: PackedScene = preload("res://scenes/game.tscn")
get_tree().change_scene_to_packed(next)

# Reload current scene
get_tree().reload_current_scene()
```

> **Note:** These methods stall until the new scene is fully loaded. For large scenes, use `ResourceLoader` with threading for background loading.

## Scene Organization Best Practices

### Scenes as Reusable Components

Design scenes as self-contained units. A `Player` scene should work independently — don't assume specific parent structure.

### Composition Over Inheritance

Attach behavior through child nodes rather than deep class hierarchies:

```
Player (CharacterBody3D)
├── HealthComponent
├── InventoryComponent
├── Sprite2D
└── CollisionShape2D
```

### Communication Pattern: Call Down, Signal Up

- **Parents call children directly:** `$Player.take_damage(10)`
- **Children signal parents:** `health_depleted.emit()`
- **Sideways (siblings):** Use the parent as mediator, groups, or an event bus autoload

This keeps nodes decoupled and reusable. A child doesn't need to know who its parent is.

```gdscript
# In parent:
func _ready() -> void:
    $Player.health_depleted.connect(_on_player_died)

func _on_player_died() -> void:
    $UI/GameOver.show()
```

### Node Path Robustness

Prefer `%UniqueNode` over `$Long/Path/To/Node` — unique names survive scene restructuring. Use `get_node_or_null()` when a node may not exist (e.g., checking for game world nodes from a menu).

## RTV Modding Notes

- RTV's scene tree is documented in [scenes reference](../game-internals/scenes-reference.md). Key scenes: `Menu`, `Core` (main game), level wrappers
- `reload_current_scene()` fails during boot because autoloads run before the main scene is set. Guard with `if get_tree().current_scene != null`. See [core concepts](../reference/core-concepts.md)
- Mod autoloads are added via `mod.txt` `[autoload]` section. They enter the tree after game autoloads. See [mod structure](../reference/mod-structure.md)
- Always use `get_node_or_null()` — the game world doesn't exist on the main menu. See [troubleshooting](../guides/troubleshooting.md)
