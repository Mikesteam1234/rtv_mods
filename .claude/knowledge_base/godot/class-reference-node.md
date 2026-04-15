# Class Reference: Node

> Godot 4.6 | [Essential Classes](class-reference-essentials.md) | [Scene Tree](scene-tree-and-nodes.md)

`Node` is the base class for all scene tree objects. Every node has a name, can have children, and receives callbacks for processing, input, and lifecycle events.

## Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `StringName` | Node identifier within parent's children |
| `owner` | `Node` | Node that "owns" this one (set when using `add_child` with default args) |
| `process_mode` | `ProcessMode` | Controls processing when tree is paused |
| `unique_name_in_owner` | `bool` | Enables `%Name` access syntax |
| `scene_file_path` | `String` | Path of the scene this node was instanced from |
| `multiplayer` | `MultiplayerAPI` | Multiplayer API for this node |

### ProcessMode Enum

| Value | Behavior |
|-------|----------|
| `PROCESS_MODE_INHERIT` | Same as parent (default) |
| `PROCESS_MODE_PAUSABLE` | Pauses when tree is paused |
| `PROCESS_MODE_WHEN_PAUSED` | Only processes when paused |
| `PROCESS_MODE_ALWAYS` | Always processes |
| `PROCESS_MODE_DISABLED` | Never processes |

## Tree Navigation

| Method | Returns | Description |
|--------|---------|-------------|
| `get_node(path)` | `Node` | Get node at path. Crashes if not found. |
| `get_node_or_null(path)` | `Node?` | Get node at path. Returns null if not found. |
| `get_parent()` | `Node` | Immediate parent |
| `get_children()` | `Array[Node]` | All immediate children |
| `get_child_count()` | `int` | Number of children |
| `get_child(idx)` | `Node` | Child by index |
| `find_child(pattern, recursive?, owned?)` | `Node` | First child matching pattern |
| `find_children(pattern, type?, recursive?, owned?)` | `Array[Node]` | All matching children |
| `find_parent(pattern)` | `Node` | Search ancestors for match |
| `get_tree()` | `SceneTree` | The active scene tree |
| `get_viewport()` | `Viewport` | This node's viewport |
| `get_window()` | `Window` | This node's window |
| `is_inside_tree()` | `bool` | Whether node is in the tree |
| `is_node_ready()` | `bool` | Whether `_ready()` has been called |
| `get_path()` | `NodePath` | Absolute path in tree |
| `get_path_to(node)` | `NodePath` | Relative path to another node |

```gdscript
# Pattern matching with find_child
var button: Button = find_child("Submit*", true, false) as Button

# find_children with type filter
var labels: Array[Node] = find_children("*", "Label", true)
```

## Child Management

| Method | Description |
|--------|-------------|
| `add_child(node)` | Add node as child. Triggers `_enter_tree` → `_ready`. |
| `add_sibling(node)` | Add node as sibling (same parent). |
| `remove_child(node)` | Remove from children. Does NOT free the node. |
| `reparent(new_parent, keep_global_transform?)` | Move to different parent. |
| `replace_by(node, keep_groups?)` | Replace this node with another in the tree. |
| `move_child(child, to_index)` | Reorder child within children list. |
| `queue_free()` | Mark for deletion at end of frame. Frees all children too. |
| `duplicate(flags?)` | Create a copy of this node (and optionally children, signals, etc.) |

```gdscript
# Spawn and add
var enemy: Node3D = enemy_scene.instantiate()
add_child(enemy)

# Remove and free
enemy.queue_free()

# Remove without freeing (reuse later)
remove_child(enemy)
# ... later:
add_child(enemy)
```

## Processing Control

| Method | Description |
|--------|-------------|
| `set_process(enable)` | Toggle `_process()` callback |
| `set_physics_process(enable)` | Toggle `_physics_process()` callback |
| `set_process_input(enable)` | Toggle `_input()` callback |
| `set_process_unhandled_input(enable)` | Toggle `_unhandled_input()` callback |
| `set_process_shortcut_input(enable)` | Toggle `_shortcut_input()` callback |
| `is_processing()` | Check if `_process` is active |
| `is_physics_processing()` | Check if `_physics_process` is active |

## Groups

| Method | Description |
|--------|-------------|
| `add_to_group(group, persistent?)` | Add to named group |
| `remove_from_group(group)` | Remove from group |
| `is_in_group(group)` | Check membership |
| `get_groups()` | All groups this node belongs to (`Array[StringName]`) |

## Key Signals

| Signal | When |
|--------|------|
| `ready` | Node and children are ready |
| `renamed` | Node name changed |
| `tree_entered` | Node entered the scene tree |
| `tree_exiting` | Node about to leave tree (still in tree) |
| `tree_exited` | Node left the tree |
| `child_entered_tree(node)` | A child was added |
| `child_exiting_tree(node)` | A child is about to be removed |
| `child_order_changed` | Children were reordered |

## Virtual Methods (Override These)

### Lifecycle

```gdscript
func _enter_tree() -> void:    # every time node enters tree (pre-order)
func _ready() -> void:         # once, after children ready (post-order)
func _exit_tree() -> void:     # when leaving tree
```

### Per-Frame Processing

```gdscript
func _process(delta: float) -> void:          # every render frame
func _physics_process(delta: float) -> void:  # every physics tick
```

### Input (in dispatch order)

```gdscript
func _input(event: InputEvent) -> void:              # first, before GUI
func _shortcut_input(event: InputEvent) -> void:      # keyboard/joypad shortcuts
func _unhandled_key_input(event: InputEvent) -> void:  # keyboard after GUI
func _unhandled_input(event: InputEvent) -> void:      # everything after GUI
```

## Shorthand Syntax

```gdscript
# $ is shorthand for get_node()
var sprite: Sprite2D = $Player/Sprite2D
# equivalent to:
var sprite: Sprite2D = get_node("Player/Sprite2D")

# % accesses unique-named nodes (set in editor)
var hud: Control = %HUD
# equivalent to:
var hud: Control = get_node("%HUD")
```

## Debugging Helpers

```gdscript
print_tree_pretty()        # print node hierarchy to console
print_orphan_nodes()       # find nodes not in tree (memory leaks)
get_tree().get_node_count() # total nodes in tree
```

## RTV Modding Notes

- Always use `get_node_or_null()` instead of `get_node()` / `$` — the game world doesn't exist on the main menu, so direct access crashes. See [troubleshooting](../guides/troubleshooting.md)
- `queue_free()` on the mod autoload node is standard after `take_over_path()` completes — the autoload has done its job. See [first mod](../getting-started/first-mod.md)
- `find_child()` is useful for locating game nodes when the exact path varies between scenes. Use with type checking for safety
- `print_tree_pretty()` is invaluable for exploring the live game scene tree from a mod. See [troubleshooting](../guides/troubleshooting.md)
