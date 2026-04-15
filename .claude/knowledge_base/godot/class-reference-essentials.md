# Class Reference: Essential Classes

> Godot 4.6 | [Node](class-reference-node.md) | [Scene Tree](scene-tree-and-nodes.md)

## SceneTree

The main loop that manages all nodes. Access via `get_tree()` from any node.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `root` | `Window` | Root viewport of the tree |
| `current_scene` | `Node` | The currently loaded main scene |
| `paused` | `bool` | Whether the tree is paused |
| `debug_collisions_hint` | `bool` | Show collision shapes |

### Key Methods

| Method | Description |
|--------|-------------|
| `change_scene_to_file(path)` | Load and switch to a scene file |
| `change_scene_to_packed(scene)` | Switch to a PackedScene |
| `reload_current_scene()` | Reload the current scene |
| `create_timer(time_sec, process_always?, process_in_physics?, ignore_time_scale?)` | Returns `SceneTreeTimer` with `timeout` signal |
| `get_nodes_in_group(group)` | Returns `Array[Node]` of all nodes in group |
| `call_group(group, method, ...)` | Call method on all nodes in group |
| `call_group_flags(flags, group, method, ...)` | Call with flags (deferred, reverse, etc.) |
| `notify_group(group, notification)` | Send notification to group |
| `set_group(group, property, value)` | Set property on all nodes in group |
| `quit(exit_code?)` | Quit the application |
| `get_node_count()` | Total nodes in tree |

### Signals

| Signal | When |
|--------|------|
| `tree_changed` | Tree hierarchy changed |
| `node_added(node)` | Any node added to tree |
| `node_removed(node)` | Any node removed from tree |
| `process_frame` | After each idle frame |
| `physics_frame` | After each physics frame |

### Inline Timer

```gdscript
await get_tree().create_timer(2.0).timeout
print("2 seconds later")
```

---

## Resource

Base class for all data containers. Resources are reference-counted and cached by path.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `resource_path` | `String` | Path in the filesystem (`res://...` or `user://...`) |
| `resource_name` | `String` | Optional human-readable name |

### Key Methods

| Method | Description |
|--------|-------------|
| `duplicate(deep?)` | Copy this resource. `deep=true` also duplicates sub-resources. |
| `take_over_path(path)` | Replace the cached resource at `path` with this one. All future `load(path)` calls return this resource. |
| `emit_changed()` | Manually emit the `changed` signal |

### Signals

| Signal | When |
|--------|------|
| `changed` | Resource data was modified |

### take_over_path — Critical for Modding

```gdscript
var original_path: String = "res://Scripts/Weapon.gd"
var override: GDScript = load("res://mods/MyMod/weapon.gd")
override.take_over_path(original_path)
# Now load("res://Scripts/Weapon.gd") returns the override
```

The original resource is ejected from the cache. This persists for the process lifetime. It does **not** affect scripts referenced by `uid://` in `.tscn` files.

---

## PackedScene

A serialized scene (node tree) that can be instanced at runtime.

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `instantiate(edit_state?)` | `Node` | Create a new node tree from this scene |
| `can_instantiate()` | `bool` | Whether the scene can be instanced |
| `pack(path)` | `Error` | Serialize a node tree into this PackedScene |

### Usage Pattern

```gdscript
# Preload at compile time
const EnemyScene: PackedScene = preload("res://scenes/enemy.tscn")

# Or load at runtime
var scene: PackedScene = load(scene_path) as PackedScene

# Create instance and add to tree
var enemy: Node3D = EnemyScene.instantiate() as Node3D
enemy.position = spawn_point
add_child(enemy)  # triggers _enter_tree → _ready
```

---

## Tween

Animates properties, calls methods, and chains animations programmatically. Created from nodes or the scene tree.

### Creation

```gdscript
# From a node (auto-killed when node is freed)
var tween: Tween = create_tween()

# From the tree (survives scene changes)
var tween: Tween = get_tree().create_tween()
```

### Tweener Methods

| Method | Description |
|--------|-------------|
| `tween_property(object, property, final_val, duration)` | Animate a property |
| `tween_callback(callable)` | Call a function at this point in the sequence |
| `tween_method(callable, from, to, duration)` | Call method with interpolated value |
| `tween_interval(time)` | Wait before next tweener |

### Chaining & Configuration

| Method | Description |
|--------|-------------|
| `set_trans(type)` | Transition type (LINEAR, SINE, QUAD, CUBIC, EXPO, BOUNCE, etc.) |
| `set_ease(ease)` | Ease type (IN, OUT, IN_OUT, OUT_IN) |
| `set_parallel()` | Run next tweeners in parallel |
| `chain()` | Return to sequential after `set_parallel()` |
| `set_loops(count?)` | Repeat (0 = infinite) |
| `set_speed_scale(scale)` | Speed multiplier |
| `stop()` / `pause()` / `play()` | Control playback |
| `kill()` | Stop and free the tween |
| `is_running()` | Check if active |

### Signals

| Signal | When |
|--------|------|
| `finished` | All tweeners completed |
| `step_finished(idx)` | One tweener completed |
| `loop_finished(loop_count)` | One loop iteration done |

### Examples

```gdscript
# Fade out and free
var tween: Tween = create_tween()
tween.tween_property(self, "modulate:a", 0.0, 0.5)
tween.tween_callback(queue_free)

# Bounce animation
var tween: Tween = create_tween()
tween.set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
tween.tween_property($Sprite, "position:y", 0.0, 0.8)

# Parallel tweens
var tween: Tween = create_tween().set_parallel()
tween.tween_property(self, "position", target_pos, 1.0)
tween.tween_property(self, "rotation", target_rot, 1.0)

# Sequence with delays
var tween: Tween = create_tween()
tween.tween_property($Label, "modulate:a", 1.0, 0.3)
tween.tween_interval(2.0)
tween.tween_property($Label, "modulate:a", 0.0, 0.3)
```

> **Note:** Each `create_tween()` call creates a new tween and kills the previous one from the same node. Tweens auto-free when finished.

---

## Timer

A countdown node that emits `timeout` after `wait_time` seconds.

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `wait_time` | `float` | `1.0` | Seconds to wait |
| `one_shot` | `bool` | `false` | Stop after first timeout (vs repeat) |
| `autostart` | `bool` | `false` | Start automatically when entering tree |
| `time_left` | `float` | — | Remaining time (read-only) |

### Methods

| Method | Description |
|--------|-------------|
| `start(time_sec?)` | Start (optionally override wait_time) |
| `stop()` | Stop the timer |
| `is_stopped()` | Whether the timer is not running |

### Signals

| Signal | When |
|--------|------|
| `timeout` | Timer reached zero |

### Examples

```gdscript
# One-shot timer (fire once)
@onready var cooldown: Timer = $CooldownTimer

func _ready() -> void:
    cooldown.one_shot = true
    cooldown.timeout.connect(_on_cooldown_done)

func shoot() -> void:
    if cooldown.is_stopped():
        fire_bullet()
        cooldown.start(0.5)

# Inline one-shot (no Timer node needed)
await get_tree().create_timer(1.0).timeout
print("1 second passed")

# Repeating timer
@onready var spawn_timer: Timer = $SpawnTimer

func _ready() -> void:
    spawn_timer.wait_time = 3.0
    spawn_timer.timeout.connect(spawn_enemy)
    spawn_timer.start()
```

## RTV Modding Notes

- `take_over_path()` on `Resource` is the core modding mechanism. See [core concepts](../reference/core-concepts.md) for the full pattern
- `reload_current_scene()` is used after `take_over_path()` to force nodes to re-instantiate with the overridden scripts. Guard with `if get_tree().current_scene != null`
- `create_tween()` is useful in mods for animated UI overlays and visual feedback without requiring AnimationPlayer nodes
- RTV uses Timer nodes extensively in its AI and event systems. See [AI system](../game-internals/ai-system.md) and [events](../game-internals/events-and-tasks.md)
