# Advanced Techniques

> [Modding Techniques](modding-techniques.md) | Techniques

The [Modding Techniques](modding-techniques.md) page covers the fundamentals. This page catalogs advanced patterns used by real overhaul mods like **ImmersiveXP** (Oldman's Immersive Overhaul), which overrides 20+ game scripts.

Every technique here comes from working, published mod code.

---

## Replacing Singletons at Runtime with `set_script()`

`take_over_path()` works for unloaded scripts, but already-instantiated singletons like `Database` require runtime replacement:

```gdscript
var script: Script = load("res://MyMod/Database.gd")
script.take_over_path("res://Scripts/Database.gd")
Database.set_script(script)
```

This applies to any instantiated node or resource, including shared `GameData` Resources.

---

## Extending Resources to Add State

Game resources are shared globally. By extending them with `set_script()`, you can add variables accessible across all override scripts:

```gdscript
# MyMod/GameData.gd
extends "res://Scripts/GameData.gd"

var isSuppressed = false
var isInteracting = false
var displayTime = false
```

Once assigned, those variables exist on the resource everywhere in the game.

---

## Shared Settings via Custom Resources

For mods with many configurable settings, create a custom `Resource` subclass serialized as `.tres`:

```gdscript
# MyMod/MySettings.gd
extends Resource
class_name MyModSettings

var featureEnabled = true
var difficulty = 1.0
var maxEnemies = 6
```

Every override script preloads the same resource instance, enabling unified configuration across many scripts.

---

## Conditional `super()` for Feature Toggles

Check settings and call `super()` for vanilla behavior when features are disabled:

```gdscript
func _physics_process(delta):
    if !settings.betterCameraShake:
        super(delta)
        return
    # custom camera shake implementation...
```

This allows individual feature opt-out without separate mod files.

---

## Modifying Resource Properties at Runtime

Load resources and change specific properties without full replacement:

```gdscript
func ModifyUseTime(resFile: String, time: float) -> Resource:
    var resource = ResourceLoader.load(resFile)
    resource.time = time
    return resource
```

**Important:** Keep references to modified resources. Without active references, Godot's garbage collection may discard them and lose changes.

---

## Scene Inheritance for UID Stripping

Godot 4 scenes reference scripts by UID, breaking `take_over_path()`. Create inherited scenes reassigning scripts by **path**:

```
; akm_rig_mod.tscn
[ext_resource type="PackedScene" path="res://Items/Weapons/AKM/AKM_Rig.tscn" id="1"]
[ext_resource type="Script" path="res://Scripts/WeaponRig.gd" id="2"]

[node name="AKM_Rig" instance=ExtResource("1")]
script = ExtResource("2")
```

Update Database.gd to reference the mod scene instead of the original.

---

## Reflection and Meta-Programming

Use `get_script_constant_map()` to iterate over script constants for auto-discovery:

```gdscript
@tool
extends Node

func RebuildItemList() -> void:
    var constants = get_script().get_script_constant_map()
    for name in constants:
        if constants[name] is PackedScene and not "_Rig" in name:
            var itemPath = constants[name].resource_path
            var dataPath = itemPath.replace(".tscn", ".tres")
            if ResourceLoader.exists(dataPath):
                var resource = load(dataPath)
                if resource is ItemData:
                    master.items.append(resource)
```

This auto-builds item lists from preloaded constants, avoiding hardcoded lists.

---

## Dynamic Node Injection

Add child nodes to game objects at runtime:

```gdscript
var LineDrawer = preload("res://MyMod/DrawLine3D.gd").new()

func _ready():
    add_child(LineDrawer)
    super()
```

Works for debug visualizers, audio players, particle effects, collision shapes, and custom audio playback.

---

## Simulating Input

Trigger game actions programmatically:

```gdscript
Input.action_press("reload")
Input.action_release("reload")

# Sprint-to-crouch transition
if Input.is_action_just_pressed("sprint"):
    Input.action_press("crouch")
    Input.action_release("crouch")
```

Use sparingly as it simulates real key presses.

---

## Coroutine-Based Timing

`await` with `create_timer()` enables readable linear timed sequences:

```gdscript
func StagedReload():
    gameData.isReloading = true
    animator["parameters/conditions/Magazine_Attach_Empty"] = true
    await get_tree().create_timer(0.1).timeout
    animator["parameters/conditions/Magazine_Attach_Empty"] = false
    await get_tree().create_timer(reloadDelay).timeout
    interface.InsertMagazine(data, weaponSlot, magazine)
    gameData.isReloading = false
```

Replaces state machines for staged sequences like multi-step reloads.

---

## AnimationTree Parameter Control

Manipulate AnimationTree state machines directly:

```gdscript
animator["parameters/conditions/Reload_Empty"] = true

func GetAnimationLength(stateName: String) -> float:
    var node = animator.tree_root.get_node(stateName) as AnimationNodeAnimation
    var animation = animations.get_animation(node.animation)
    return animation.length
```

---

## Shader Parameter Modification

Change visual effects at runtime:

```gdscript
NVGMaterial.set_shader_parameter("noise", 15.0)

RenderingServer.global_shader_parameter_set("Snow", winterValue)
RenderingServer.global_shader_parameter_set("Wind", windValue)
RenderingServer.global_shader_parameter_set("Rain", rainValue)

ocular.set_shader_parameter("Opacity", ocularOpacity)
activeOptic.reticle.set_shader_parameter("size", reticleSize)
```

`RenderingServer.global_shader_parameter_set()` affects all shaders using that parameter, enabling world-wide effects.

---

## NavigationServer for Procedural Placement

Use navigation meshes to find valid positions for spawned objects:

```gdscript
var nav_map = get_world_3d().get_navigation_map()
var x = origin.x + randf_range(-7.0, 7.0)
var z = origin.z + randf_range(-7.0, 7.0)
var requested = Vector3(x, origin.y, z)
var valid_pos = NavigationServer3D.map_get_closest_point(nav_map, requested)
global_transform.origin = valid_pos
```

Ensures randomly placed objects land on walkable surfaces.

---

## Runtime Groups for Cross-Mod Queries

Add nodes to groups at runtime for system discovery:

```gdscript
func _ready():
    super()
    add_to_group("Door")

var doors = get_tree().get_nodes_in_group("Door")
for door in doors:
    door.Lock()
```

Groups categorize objects without modifying their scripts.

---

## Save/Load with ResourceSaver

Build persistence using Godot's resource serialization:

```gdscript
func SaveMap(mapName: String):
    var save_data = SaveData.new()
    for container in get_tree().get_nodes_in_group("Container"):
        save_data.containers.append({
            "name": container.name,
            "position": container.global_position,
            "items": container.get_items()
        })
    ResourceSaver.save(save_data, "user://" + mapName + ".tres")

func LoadMap(mapName: String):
    var path = "user://" + mapName + ".tres"
    if ResourceLoader.exists(path):
        var save_data = ResourceLoader.load(path)
```

---

## Intermod Compatibility Checks

Detect other mods and defer behavior accordingly:

```gdscript
func Movement(delta):
    if McmHelpers != null and McmHelpers.RegisteredMods.has("FreeLook"):
        super(delta)
    else:
        # custom movement code
```

Enables coexistence with specific other mods.

---

## Context Menu Modification

Add or rename buttons in game context menus:

```gdscript
func ShowContextMenu():
    super()
    if interface.contextItem.slotData.itemData.type == "Weapon":
        if !interface.contextItem.slotData.chamber and \
           interface.contextItem.slotData.amount > 0:
            var useButton = buttons.get_node("Use")
            useButton.text = "Chamber Round"
            useButton.show()
```

---

## What ImmersiveXP Modifies (Scope Reference)

| System | Changes |
|--------|---------|
| **AI** | Visibility calculations, hearing, suppressive fire, door interaction, reload behavior |
| **Weapons** | Jamming, condition degradation, staged reloads, chamber tracking, ADS zoom |
| **Camera** | DOF blur for ADS/NVG, enhanced camera shake, Perlin noise sway |
| **Movement** | Sprint/crouch transitions, weapon lowering, enhanced headbob |
| **HUD/UI** | Interact dot, condition colors, context menu additions, tooltip modifications |
| **Inventory** | Auto-equip, holster during item use, magazine swap, weapon repair |
| **World** | Weather shader parameters, mine randomization, room replacements |
| **Survival** | Temperature system, hypothermia, transition costs |
| **Loot** | Reduced tables, persistent loot across sessions, save/load |
| **Level Design** | 9 replacement room scenes, custom decals, 3D assets |

This represents 30+ GDScript files, 25+ weapon rig scenes, room scenes, textures, and custom resources.

---

## Next Steps

- [Modding Techniques](modding-techniques.md) — foundational patterns
- [Compatibility Guide](../guides/compatibility.md) — critical for large mods
- [Walkthrough: Item Spawner](../walkthroughs/item-spawner.md) — alternative approaches
