# Autoloads & Singletons

> Godot 4.6 | [Scene Tree](scene-tree-and-nodes.md) | [Resources](resources-and-loading.md)

## What Are Autoloads

Autoloads are scripts or scenes that Godot loads **before the main scene** and keeps alive for the entire application lifetime. They persist across scene changes, making them ideal for global state and cross-scene systems.

Autoloads are added as direct children of the root viewport:

```
root (Window)
├── AudioManager    ← autoload
├── GameState       ← autoload
├── EventBus        ← autoload
└── MainScene       ← current_scene (changes on scene switch)
```

## Setting Up Autoloads

In the editor: **Project > Project Settings > Globals > Autoload**

Add a script or scene, give it a name, and optionally check "Enable" as a singleton.

Via code (rarely needed):

```gdscript
# Autoloads are registered in project.godot under [autoload]
# They cannot be added/removed at runtime through the standard API
```

## Accessing Autoloads

When registered as singletons, autoloads are accessible by name from any script:

```gdscript
# Direct name access (if singleton is enabled)
GameState.score += 100
AudioManager.play_sfx("explosion")

# Or via the tree (always works)
var game_state: Node = get_node("/root/GameState")
```

## Autoload Initialization Order

1. Autoloads are instanced and added to the tree **in the order listed** in Project Settings
2. Each autoload receives `_enter_tree()` and `_ready()` before the next is added
3. After all autoloads are ready, the main scene is loaded

This means earlier autoloads **cannot** reference later ones in `_ready()`. If you need cross-autoload references, use `call_deferred` or wait for `SceneTree.process_frame`.

## Scene Switcher Pattern

Autoloads commonly manage scene transitions since they persist:

```gdscript
# scene_manager.gd (autoload)
extends Node

var current_level: String = ""

func change_level(path: String) -> void:
    current_level = path
    get_tree().change_scene_to_file(path)

func reload_level() -> void:
    get_tree().reload_current_scene()

func quit_to_menu() -> void:
    get_tree().change_scene_to_file("res://scenes/menu.tscn")
```

## Event Bus Pattern

A common autoload pattern for decoupled communication:

```gdscript
# events.gd (autoload)
extends Node

signal player_died
signal score_changed(new_score: int)
signal item_collected(item_id: String)
signal level_completed
```

Any node can emit or connect:

```gdscript
# In player.gd
func die() -> void:
    Events.player_died.emit()

# In hud.gd
func _ready() -> void:
    Events.score_changed.connect(_on_score_changed)
```

## When to Use Autoloads vs Regular Nodes

### Use Autoloads For

- **Global state** that survives scene changes (score, settings, save data)
- **Cross-scene systems** (audio, scene transitions, event bus)
- **Singletons** (one instance needed application-wide)

### Use Regular Nodes For

- **Scene-specific logic** (level mechanics, UI for one screen)
- **Testable components** (can instantiate independently)
- **Optional features** (not every scene needs them)

> **Guideline:** If you're unsure, start with a regular node. Promote to autoload only when you confirm it needs to persist across scene changes. Overusing autoloads creates hidden global state that's hard to test and reason about.

## Common Autoload Examples

| Name | Purpose |
|------|---------|
| `GameState` | Player progress, current level, settings |
| `AudioManager` | Music/SFX playback, crossfading |
| `SceneManager` | Scene transitions, loading screens |
| `Events` / `SignalBus` | Global signals for decoupled communication |
| `SaveManager` | Serialize/deserialize save data |
| `InputRemapper` | Custom key bindings |

## RTV Modding Notes

- RTV has three core autoloads: `Loader`, `Database`, `Simulation`. `GameData` is a static class, not an autoload. See [autoloads and boot](../game-internals/autoloads-and-boot.md)
- Mod autoloads are registered in `mod.txt` under `[autoload]` and load after game autoloads. See [mod structure](../reference/mod-structure.md)
- Mod autoloads `extends Node` — do NOT call `super._ready()` since `Node._ready()` doesn't exist (parse error). See [compatibility guide](../guides/compatibility.md)
- The mod autoload pattern: load overrides → `take_over_path()` → reload scene → `queue_free()`. See [first mod](../getting-started/first-mod.md)
