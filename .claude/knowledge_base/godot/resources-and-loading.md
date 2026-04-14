# Resources & Loading

> Godot 4.6 | [Scene Tree](scene-tree-and-nodes.md) | [Autoloads](autoloads-and-singletons.md)

## Resource vs Node

- **Nodes** provide functionality — they process, render, handle input
- **Resources** are data containers — textures, scripts, meshes, audio, animations, fonts, custom data

Resources are loaded once into memory; subsequent `load()` calls for the same path return the same cached instance.

## Common Resource Types

| Type | Contains |
|------|----------|
| `Texture2D` | Image data |
| `PackedScene` | Scene (node tree) serialized to disk |
| `Script` / `GDScript` | Code |
| `AudioStream` | Audio data |
| `Mesh` | 3D geometry |
| `Material` | Rendering properties |
| `Animation` | Keyframe data |
| `Font` | Typography |

## The res:// Filesystem

`res://` is Godot's virtual filesystem. In exported games, it maps to the `.pck` file. All game assets live under `res://`.

When mod archives (PCK or ZIP) are loaded, their files are injected into the same `res://` namespace. A mod file at `res://Scripts/Weapon.gd` replaces the game's version.

```gdscript
# These all reference the virtual filesystem
load("res://scenes/player.tscn")
preload("res://scripts/utils.gd")
```

## The user:// Data Path

`user://` is per-user persistent storage. On Windows: `%AppData%/Godot/app_userdata/<project>/` or the custom path set in project settings.

```gdscript
# Save a config file
var config := ConfigFile.new()
config.set_value("player", "name", "Alice")
config.save("user://settings.cfg")
```

## load() vs preload()

### preload()

- Loads at **compile time** (when the script is parsed)
- Requires a **constant string** path
- Returns the specific resource type
- Best for resources you always need

```gdscript
const BulletScene: PackedScene = preload("res://scenes/bullet.tscn")
const ICON: Texture2D = preload("res://ui/icon.png")
```

### load()

- Loads at **runtime** (when the line executes)
- Accepts **variable** paths
- Returns `Resource` (needs casting for specific type)
- Use when the path isn't known at compile time

```gdscript
var scene: PackedScene = load("res://scenes/" + level_name + ".tscn") as PackedScene
var script: GDScript = load(script_path) as GDScript
```

Both return the **cached instance** — Godot doesn't re-read from disk if already loaded.

## ResourceLoader (Threaded Loading)

For large resources, load in a background thread to avoid frame hitches:

```gdscript
func load_level_async(path: String) -> void:
    ResourceLoader.load_threaded_request(path)

func _process(_delta: float) -> void:
    var status: ResourceLoader.ThreadLoadStatus = ResourceLoader.load_threaded_get_status(path)
    match status:
        ResourceLoader.THREAD_LOAD_IN_PROGRESS:
            var progress: Array = []
            ResourceLoader.load_threaded_get_status(path, progress)
            loading_bar.value = progress[0] * 100
        ResourceLoader.THREAD_LOAD_LOADED:
            var scene: PackedScene = ResourceLoader.load_threaded_get(path)
            get_tree().change_scene_to_packed(scene)
        ResourceLoader.THREAD_LOAD_FAILED:
            print("Failed to load: ", path)
```

## Loading Scenes

Scenes are `PackedScene` resources. Create node instances with `instantiate()`:

```gdscript
var scene: PackedScene = preload("res://scenes/bullet.tscn")

func shoot() -> void:
    var bullet: Node3D = scene.instantiate() as Node3D
    bullet.global_position = muzzle.global_position
    bullet.rotation = muzzle.global_rotation
    get_tree().current_scene.add_child(bullet)
```

## Custom Resources

Extend `Resource` for custom data types with automatic serialization:

```gdscript
class_name WeaponData
extends Resource

@export var name: String
@export var damage: int
@export var fire_rate: float
@export var icon: Texture2D

func dps() -> float:
    return damage * fire_rate
```

Use in other scripts:

```gdscript
@export var weapon_data: WeaponData

func _ready() -> void:
    print(weapon_data.name, " DPS: ", weapon_data.dps())
```

Custom resources serialize automatically to `.tres` (text) or `.res` (binary) files. They support nested sub-resources, getters/setters, and signals.

## Resource Sharing

By default, resources are **shared** — multiple nodes referencing the same resource share one instance. Modifying it affects all users.

```gdscript
# Creates an independent copy
var unique_material: Material = shared_material.duplicate()

# Deep copy (also duplicates sub-resources)
var deep_copy: Resource = original.duplicate(true)
```

## take_over_path()

Patches the resource cache so all future `load()` calls for that path return this resource instead of the original. The original resource at that path is effectively replaced for the lifetime of the process.

```gdscript
var override_script: GDScript = load("res://mods/MyMod/weapon_override.gd")
var original: GDScript = load("res://Scripts/Weapon.gd")
override_script.take_over_path(original.resource_path)
```

This is the core mechanism for script overrides in Godot modding.

## Saving Resources

```gdscript
var data := WeaponData.new()
data.name = "Sword"
data.damage = 25
ResourceSaver.save(data, "user://weapons/sword.tres")
```

## RTV Modding Notes

- `take_over_path()` is the core override mechanism for RTV mods. See [core concepts](../reference/core-concepts.md) and [modding techniques](../techniques/modding-techniques.md) for the full pattern
- `preload()` in mod autoloads runs before the scene tree exists — use `load()` instead for anything that depends on game state. See [core concepts — preload timing problem](../reference/core-concepts.md)
- `take_over_path()` does NOT work for scripts referenced by `uid://` in `.tscn` files. Use scene inheritance to strip UIDs. See [advanced techniques](../techniques/advanced-techniques.md)
- RTV's resource layout (Items/, Loot/, AI/, etc.) is documented in [resources reference](../game-internals/resources-reference.md)
```
