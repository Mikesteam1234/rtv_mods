# Compatibility Guide

> Guides | [Publishing](publishing.md) | [Troubleshooting](troubleshooting.md)

This guide helps mod developers write mods that work well together and remain functional through game updates.

## The Conflict Report

The mod loader generates analysis at:
```
%AppData%\Road to Vostok Demo\modloader_conflicts.txt
```

**Key messages:**

| Message | Meaning |
|---------|---------|
| **CONFLICT** | Two mods share the same `res://` path; last-loaded wins |
| **CONFLICT: take_over_path** *(critical)* | Multiple mods call `take_over_path()` on identical scripts |
| **CHAIN OK** | Multiple script overrides with proper `super()` calls working correctly |
| **CHAIN BROKEN** | A mod skipped `super()` in lifecycle methods, breaking the override chain |
| **DATABASE OVERRIDE** *(critical)* | Mod replaced `Database.gd`, potentially breaking scene overrides |
| **OVERHAUL** | Mod overrides 5+ core scripts (expected for major content mods) |
| **TOOLTIP** | Mod overrides `UpdateTooltip()`, which affects only inventory tooltips |
| **NO SUPER** | Lifecycle method override without `super()` — breaks subsequent mods |
| **BAD ZIP** *(critical)* | Archive uses Windows backslash paths; repack with 7-Zip |

## Writing Compatible Mods

### Call `super()`. Always.

This is foundational. Override any method and invoke `super()`:

```gdscript
func _ready():
    super()
    # your code

func _process(delta):
    super(delta)
    # your code

func SomeGameMethod():
    super()
    # your additions
```

Without it, earlier chain mods lose functionality.

### Namespace Your Files

Place everything under `mods/YourModName/`:
```
Good:  mods/MyMod/Helpers.gd
Bad:   Scripts/Helpers.gd
```

### Use `get_node_or_null()` Everywhere

The game world doesn't exist everywhere, and other mods change the node structure:

```gdscript
var ui = get_node_or_null("/root/Map/Core/UI")
if ui == null:
    return
```

### Be Careful with Database.gd

This file preloads everything. Replacing it risks breaking other mods' overrides. Consider runtime item injection instead.

### Think About What You're Overriding

Popular targets increase conflict likelihood:

| Instead of | Try |
|------------|-----|
| `Character.gd` | Hook methods from autoload |
| `HUD.gd` | Add CanvasLayer overlay |
| `Database.gd` | Runtime item injection |
| `Weapon.gd` | Override specific weapon scripts |

### Set a Reasonable Priority

- **0 (default)**: Base mods others build upon
- **1–10**: Small mods layering atop overhauls
- **Higher values**: Only when needing final position

Higher priority loads later, winning conflicts and sitting at the override chain's top.

## Surviving EA Updates

Common issues and solutions:

| Change | Impact | Solution |
|--------|--------|----------|
| Script renamed/moved | Hard crash | Check decompiled code |
| Method signature changed | Hard crash | Verify super() calls |
| Method renamed | Silent failure | Ensure method exists |
| New method added | None | Inherited automatically |
| Node tree changed | Path breaks | Use null checks |
| Database changes | Missing items | Runtime injection |

### Defensive Coding

```gdscript
# Check before accessing
if "someProperty" in target:
    var value = target.someProperty

# Check before calling
if obj.has_method("NewMethod"):
    obj.NewMethod()

# Always null-check node paths
func get_ui():
    return get_node_or_null("/root/Map/Core/UI")
```

Fewer script overrides mean better resilience. Document tested game versions in ModWorkshop descriptions.

### When It Breaks

1. Check `modloader_conflicts.txt` for errors
2. Decompile updated game files
3. Diff your overridden scripts against new versions
4. Fix overrides, bump version, publish update

## Real-World Compatibility Example

Three mods interact as follows:

| | ImmersiveXP | ToDOnClock | ItemSpawner |
|---|---|---|---|
| **ImmersiveXP** | — | Chain works | No overlap |
| **ToDOnClock** | Chain works | — | No overlap |
| **ItemSpawner** | No overlap | No overlap | — |

ImmersiveXP (priority 0) and ToDOnClock (priority 1) both override `HUD.gd`. Both call `super()`, creating an unbroken chain. ItemSpawner uses an autoload without game script overrides, ensuring universal compatibility.

## What Next?

- [Walkthrough: ToDOnClock](../walkthroughs/todon-clock.md) — override chaining in practice
- [Troubleshooting](troubleshooting.md) — resolving issues
