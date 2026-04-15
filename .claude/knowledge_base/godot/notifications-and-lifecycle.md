# Notifications & Lifecycle

> Godot 4.6 | [Input System](input-system.md) | [Scene Tree](scene-tree-and-nodes.md)

## The Notification System

Every Godot object has a `_notification(what)` method that receives integer constants for lifecycle events. The virtual methods like `_ready()` are convenience wrappers around specific notifications.

```gdscript
func _notification(what: int) -> void:
    match what:
        NOTIFICATION_READY:
            pass  # same as _ready()
        NOTIFICATION_PROCESS:
            pass  # same as _process()
        NOTIFICATION_WM_CLOSE_REQUEST:
            save_game()
```

You rarely override `_notification()` directly — the virtual methods are cleaner. It's useful when you need to handle notifications that don't have dedicated methods.

## Complete Node Lifecycle

### Construction

| Step | Notification / Method | Notes |
|------|----------------------|-------|
| 1 | `_init()` | Object constructed in memory. No tree access. |

### Entering the Tree

| Step | Notification / Method | Notes |
|------|----------------------|-------|
| 2 | `NOTIFICATION_ENTER_TREE` / `_enter_tree()` | Pre-order (parent first). Node is in tree but children may not be ready. Can fire multiple times. |
| 3 | `NOTIFICATION_POST_ENTER_TREE` | After all descendants have entered. No dedicated method. |
| 4 | `NOTIFICATION_READY` / `_ready()` | **Post-order** (children first). Fires once per lifetime. Safe to access children. |

### Running

| Step | Notification / Method | Notes |
|------|----------------------|-------|
| 5 | `NOTIFICATION_PROCESS` / `_process(delta)` | Every rendered frame. Variable timestep. |
| 6 | `NOTIFICATION_PHYSICS_PROCESS` / `_physics_process(delta)` | Every physics tick. Fixed timestep. |
| 7 | Input callbacks | `_input`, `_unhandled_input`, etc. |

### Leaving the Tree

| Step | Notification / Method | Notes |
|------|----------------------|-------|
| 8 | `NOTIFICATION_EXIT_TREE` / `_exit_tree()` | Node leaving the tree. Reverse order. |
| 9 | `NOTIFICATION_PREDELETE` | Object about to be freed from memory. |

### Key Initialization Order for Member Variables

1. Type defaults (`0`, `false`, `null`, etc.)
2. Declared values assigned top-to-bottom
3. `_init()` called
4. Exported values assigned (from inspector/scene file)
5. `@onready` variables initialized
6. `_ready()` called

## Idle vs Physics Processing

### _process(delta) — Idle/Render Frame

Called every rendered frame. `delta` varies based on framerate. Use for:
- Visual updates (animations, particles, UI)
- Non-physics logic
- Input response that doesn't affect physics

```gdscript
func _process(delta: float) -> void:
    # Rotate a visual element smoothly
    $Sprite2D.rotation += spin_speed * delta

    # Update UI
    $HealthBar.value = health
```

### _physics_process(delta) — Physics Frame

Called at a fixed interval (default 60 times/second, configurable in Project Settings). `delta` is constant (`1.0 / physics_ticks_per_second`). Use for:
- Movement and physics
- Raycasts
- Collision-dependent logic

```gdscript
func _physics_process(delta: float) -> void:
    velocity.y += gravity * delta
    velocity.x = input_direction * speed
    move_and_slide()
```

### Enabling/Disabling Processing

```gdscript
set_process(false)          # stops _process
set_physics_process(false)  # stops _physics_process
set_process_input(false)    # stops _input
set_process_unhandled_input(false)  # stops _unhandled_input
```

## Pausing

### Setting Pause State

```gdscript
get_tree().paused = true   # pause the game
get_tree().paused = false  # unpause
```

### Process Mode

Each node's `process_mode` property controls behavior when the tree is paused:

| Value | Behavior |
|-------|----------|
| `PROCESS_MODE_INHERIT` | Same as parent (default) |
| `PROCESS_MODE_PAUSABLE` | Stops when paused |
| `PROCESS_MODE_WHEN_PAUSED` | **Only** runs when paused |
| `PROCESS_MODE_ALWAYS` | Always runs regardless of pause |
| `PROCESS_MODE_DISABLED` | Never runs |

```gdscript
# Pause menu should work while paused
func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS

# Or set in _ready for a pause overlay
$PauseMenu.process_mode = Node.PROCESS_MODE_WHEN_PAUSED
```

### What Pausing Affects

When `get_tree().paused = true`:
- `_process()` and `_physics_process()` stop for PAUSABLE nodes
- `_input()` and `_unhandled_input()` stop for PAUSABLE nodes
- `Timer` nodes with default process mode stop
- `AnimationPlayer` nodes pause
- Physics simulation pauses

Signals still fire. Manual function calls still work. Only the automatic callbacks are affected.

## Common Notification Constants

| Constant | When |
|----------|------|
| `NOTIFICATION_ENTER_TREE` | Node entered tree |
| `NOTIFICATION_EXIT_TREE` | Node leaving tree |
| `NOTIFICATION_READY` | Node is ready |
| `NOTIFICATION_PROCESS` | Idle frame |
| `NOTIFICATION_PHYSICS_PROCESS` | Physics frame |
| `NOTIFICATION_PAUSED` | Tree just paused |
| `NOTIFICATION_UNPAUSED` | Tree just unpaused |
| `NOTIFICATION_PARENTED` | Got a parent |
| `NOTIFICATION_UNPARENTED` | Lost parent |
| `NOTIFICATION_WM_CLOSE_REQUEST` | Window close requested |
| `NOTIFICATION_CRASH` | About to crash |
| `NOTIFICATION_OS_MEMORY_WARNING` | Low memory |

## RTV Modding Notes

- RTV uses 120 physics ticks/second (not the default 60). `_physics_process` delta is ~0.0083s
- `GameData.freeze` is RTV's game-specific pause mechanism, separate from `get_tree().paused`. Mods that need to respect the game's pause state should check both
- Mod autoloads run `_ready()` during boot, before the main scene loads. Guard scene-dependent code with `if get_tree().current_scene != null`. See [core concepts](../reference/core-concepts.md)
