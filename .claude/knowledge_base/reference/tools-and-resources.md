# Tools and Resources

> [Core Concepts](core-concepts.md) | [Mod Structure](mod-structure.md) | Reference

Everything needed to decompile, build, test, and publish Vostok mods.

## Tools

### Mod Loader
- **Metro Mod Loader** on ModWorkshop — the community mod loader this wiki covers

### Community Mods for Mod Developers
- **Mod Configuration Menu (MCM)** by DoinkOink — gives your mod an in-game settings UI with sliders, toggles, keybinds, dropdowns, and color pickers. MCM Wiki contains integration guidance.

### Decompiling
- **GDRE Tools / gdsdecomp** — GUI tool to decompile Godot games, supporting versions 2.x through 4.x
- **GodotPckTool** — CLI tool for extracting and inspecting PCK files

### Assets
- **ModZipExporter** — Godot plugin to export mod archives with properly imported assets
- **Godot PCK Explorer** — browse and extract PCK contents without the editor

### Development
- **Godot Engine** — match the game's version (currently 4.6.1 as of early 2026)
- **VS Code with GDScript extension** — syntax highlighting and autocomplete
- **7-Zip** — creates ZIPs with forward-slash paths, avoiding the backslash bug

### Publishing
- **ModWorkshop** — where Vostok mods are published

## Godot Docs Worth Bookmarking

- GDScript Reference — language basics
- GDScript Style Guide — naming conventions
- Exporting Packs, Patches, and Mods — official modding documentation
- Runtime File Loading — loading resources at runtime
- ResourceLoader API — the mechanics behind `load()` and `preload()`
- Using Signals — Godot's event system

## Other Modding References

- Godot Mod Loader Wiki — different loader with translatable GDScript techniques
- VostokMods Wiki — documentation for the original Vostok mod loader by Ryhon0

## Known Godot Bugs

- **#83542** — `take_over_path` + `class_name`: scripts with `class_name` can only be overridden once; second override causes a fatal crash

## File Paths

### Game Install

```
C:\Program Files (x86)\Steam\steamapps\common\Road to Vostok Demo\
├── Road to Vostok Demo.pck    ← decompile this
├── Road to Vostok Demo.exe
├── override.cfg               ← mod loader config
└── mods/                      ← mod archives go here
```

### User Data

```
%AppData%\Road to Vostok Demo\
├── modloader.gd               ← mod loader script
├── mod_config.cfg             ← which mods are enabled (auto-generated)
├── modloader_conflicts.txt    ← compatibility report (auto-generated)
└── logs/
    └── godot.log              ← print() output and errors
```

## Quick Reference

### mod.txt Template

```ini
[mod]
name="My Mod Name"
id="my-mod-id"
version="1.0.0"
priority=0

[autoload]
MyModMain="res://mods/MyMod/Main.gd"

[updates]
modworkshop=12345
```

### Standard Override Pattern

```gdscript
# Main.gd (autoload — self-destructs after registering)
extends Node

func _ready():
    overrideScript("res://mods/MyMod/Override.gd")
    queue_free()

func overrideScript(path: String):
    var script: Script = load(path)
    script.reload()
    var parent = script.get_base_script()
    script.take_over_path(parent.resource_path)
```

```gdscript
# Override.gd
extends "res://Scripts/OriginalScript.gd"

func _ready():
    super()
    # your stuff

func some_game_method():
    super()
    # your modifications
```

### Defensive Node Access

```gdscript
# Always use get_node_or_null — game world doesn't exist on main menu
var ui = get_node_or_null("/root/Map/Core/UI")
if ui == null:
    return
```

### Safe Method Call Pattern

```gdscript
func _safe_call(obj, method_name: String, args: Array = []) -> Variant:
    if obj == null or !obj.has_method(method_name):
        return null
    return obj.callv(method_name, args)
```
