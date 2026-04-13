# Modding Techniques

> Techniques | [Advanced Techniques](advanced-techniques.md)

Four techniques cover just about everything you'd want to do. Most mods combine a couple of them.

## Technique 1: Replacing Assets

The simplest kind of mod. Put a file at the same `res://` path as the original, and the game loads yours instead. Works for textures, audio, models, any resource file. No code needed.

To replace the game's crosshair at `res://Textures/UI/crosshair.png`:

```
YourMod.zip
├── mod.txt
└── Textures/UI/crosshair.png    ← same path as original
```

That's literally it.

### The .remap / .import Thing

Most game assets get processed by Godot's import system. The original `.png` becomes a `.png.import` plus an engine-optimized binary. Dropping in a raw `.png` might not work if the game references the imported version. Use ModZipExporter to export replacements in the right format, or decompile the game to understand the import structure.

## Technique 2: Autoload Scripts

Autoloads are singleton nodes that live alongside the game. Use them to add new stuff without touching existing code: UI overlays, background systems, keybinds, or as the entry point for script overrides.

### Basic Example

**mod.txt:**

```ini
[mod]
name="My Timer Mod"
id="my-timer"
version="1.0.0"

[autoload]
MyTimer="res://mods/MyTimer/Main.gd"
```

**mods/MyTimer/Main.gd:**

```gdscript
extends Node

var elapsed := 0.0

func _ready():
    print("[MyTimer] Started!")

func _process(delta):
    elapsed += delta
```

This node hangs around for the whole game session.

### Scene-based Autoloads

You can also use a `.tscn` scene as the autoload, which lets you design UI in the Godot editor instead of building it all in code:

```ini
[autoload]
ItemSpawner="res://mods/ItemSpawner/ItemSpawner.tscn"
```

### Accessing Game Nodes

The game world lives under `/root/Map/`. Some useful paths:

```gdscript
var ui = get_node_or_null("/root/Map/Core/UI")
var interface = get_node_or_null("/root/Map/Core/UI/Interface")

func is_interface_open() -> bool:
    var ui = get_node_or_null("/root/Map/Core/UI")
    if ui == null or ui.gameData == null:
        return false
    return bool(ui.gameData.interface)
```

Always use `get_node_or_null()` instead of `get_node()`. The game world doesn't exist on the main menu, and a hard `get_node()` call will crash.

### Self-destructing Autoloads

If your autoload just needs to register some script overrides and then it's done, free it:

```gdscript
extends Node

func _ready():
    setup_overrides()
    queue_free()
```

### Player-configurable Settings

If your mod has values that players should be able to tweak (keybinds, toggle features, difficulty sliders), check out the Mod Configuration Menu (MCM). It's a community mod that adds an in-game settings UI.

## Technique 3: Script Overrides (take_over_path)

This is where it gets powerful. Override any game script to change behavior, add features, or intercept function calls.

### The Pattern

Every script override follows the same steps:

**1. Write the override script** (extends the original by file path):

```gdscript
# mods/MyMod/WeaponOverride.gd
extends "res://Scripts/Weapon.gd"

func PlayFireAudio():
    super()  # call the original
    print("Bang!")
```

**2. Write the loader** (autoload that registers the override):

```gdscript
# mods/MyMod/Main.gd
extends Node

func _ready():
    overrideScript("res://mods/MyMod/WeaponOverride.gd")
    queue_free()

func overrideScript(path: String):
    var script: Script = load(path)
    script.reload()
    var parent = script.get_base_script()
    script.take_over_path(parent.resource_path)
```

**3. Register in mod.txt:**

```ini
[autoload]
MyMod="res://mods/MyMod/Main.gd"
```

That `overrideScript()` helper is the standard pattern you'll see in basically every Vostok mod.

### Always Call `super()`

When you override a method, call `super()` to run the original code:

```gdscript
extends "res://Scripts/Character.gd"

func _ready():
    super()  # run the original _ready
    # your additions here

func _process(delta):
    super(delta)  # pass arguments through
    # your additions here
```

If you skip `super()`, you break the override chain. Other mods that also override this script will have their code silently dropped.

### Override Multiple Scripts

Just call `overrideScript()` for each one:

```gdscript
func _ready():
    overrideScript("res://mods/MyMod/WeaponOverride.gd")
    overrideScript("res://mods/MyMod/CharacterOverride.gd")
    overrideScript("res://mods/MyMod/HUDOverride.gd")
    queue_free()
```

### Adding New Stuff

Your override is a full subclass. You can add variables, methods, whatever:

```gdscript
extends "res://Scripts/Weapon.gd"

var shots_fired := 0

func get_accuracy() -> float:
    return 1.0 - (shots_fired * 0.01)

func Fire():
    super()
    shots_fired += 1
```

### Override Chaining

When multiple mods override the same script, they form a chain. The last mod to call `take_over_path()` wins. If everyone calls `super()`, the chain works and each mod's code runs in order.

```
Your Mod's Script
    └── extends → Other Mod's Script
                      └── extends → Original Game Script
```

### What You Can't Do

- Override `class_name` scripts more than once — causes a fatal crash (Godot 4 bug #83542)
- Redefine variables or constants from the parent script
- Override `_init()` without double-execution issues
- Override preloaded scripts — if the game used `preload()`, the old version is already cached

## Technique 4: Loading Custom Files at Runtime

Once the mod loader mounts your zip, every file inside it is accessible through normal `res://` paths. You can ship data files in your mod and read them at runtime from your autoload.

### Reading a Data File

```gdscript
# Your mod ships a JSON file at mods/MyMod/data.json
var file = FileAccess.open("res://mods/MyMod/data.json", FileAccess.READ)
var json_text = file.get_as_text()
file.close()
var data = JSON.parse_string(json_text)
```

### Loading a Godot Resource

```gdscript
# .tres, .theme, etc.
var my_resource = load("res://mods/MyMod/custom_data.tres")
```

### Writing to User Space

Your mod can also save data (configs, state, logs) to the user directory:

```gdscript
# user:// maps to %AppData%/Road to Vostok Demo/
var file = FileAccess.open("user://my_mod_config.json", FileAccess.WRITE)
file.store_string(JSON.stringify(my_settings))
file.close()
```

Once your zip is mounted, the files inside are first-class citizens in Godot's filesystem. You don't need PCK files or special export tools.

## Choosing Your Approach

| I want to... | Use... |
|---|---|
| Swap a texture, sound, or model | Asset replacement |
| Add a new UI panel or HUD overlay | Scene-based autoload |
| Run background logic (timers, trackers) | Script autoload |
| Change how a game system works | Script override |
| Add behavior to a game object | Script override |
| React to game events | Autoload + signals, or script override |
| Ship config files, data tables, JSON | Custom file loading from your autoload |

Most real mods mix these. The [Item Spawner walkthrough](../walkthroughs/item-spawner.md) uses a scene-based autoload. The [ToDOnClock walkthrough](../walkthroughs/todon-clock.md) uses autoload + script overrides with chaining.

## What Next?

- [Advanced Techniques](advanced-techniques.md) — singleton replacement, shader control, coroutines, save/load, and more
- [Compatibility Guide](../guides/compatibility.md) — make your overrides play nice
