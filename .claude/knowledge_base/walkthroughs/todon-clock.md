# Walkthrough: The ToDOnClock Mod

> [Item Spawner](item-spawner.md) | Walkthroughs

## What It Does

This mod displays the in-game time when viewing an alarm clock. The tooltip shows "Alarm Clock (14:35)" both in inventory and when looking at a clock on the ground.

## The Dual-Tooltip Problem

Road to Vostok has two separate tooltip systems:

| Context | Code path | When it fires |
|---------|-----------|---------------|
| Inventory | `Pickup.UpdateTooltip()` sets `gameData.tooltip` | Hovering an item in inventory |
| World | `HUD._physics_process()` reads data and sets `label.text` | Looking at an item on the ground |

Overriding only one path leaves the time missing from either inventory or world view. The mod loader flags incomplete overrides as `TOOLTIP WARNING`. ToDOnClock overrides both systems.

## Structure

```
ToDOnClock.zip
├── mod.txt
└── ToDOnClock/
    ├── Main.gd          ← registers overrides, then self-destructs
    ├── HUD.gd           ← world tooltip override
    └── AlarmClock.gd    ← inventory tooltip override
```

> Note: Files are under `ToDOnClock/` rather than `mods/ToDOnClock/`, though both work. The recommended approach is `mods/YourModName/` to avoid accidental path collisions.

## mod.txt

```ini
[mod]
name="Show ToD When Looking At Alarm Clock"
id="show-tod-on-clock"
version="0.0.2"
priority=1

[autoload]
ToDOnClock="res://ToDOnClock/Main.gd"

[updates]
modworkshop=54878
```

The `priority=1` setting is critical. ImmersiveXP defaults to priority 0. By setting priority to 1, ToDOnClock loads after ImmersiveXP, ensuring its `take_over_path()` runs on top of the chain: **ToDOnClock → ImmersiveXP → Vanilla**.

## Main.gd

```gdscript
extends Node

func _ready():
    overrideScript("res://ToDOnClock/HUD.gd")
    overrideScript("res://ToDOnClock/AlarmClock.gd")
    queue_free()

func overrideScript(overrideScriptPath: String):
    var script: Script = load(overrideScriptPath)
    script.reload()
    var parentScript = script.get_base_script()
    script.take_over_path(parentScript.resource_path)
    return script
```

Standard registration pattern: register both overrides and then self-destruct since no persistent node is needed.

## AlarmClock.gd: Inventory Tooltip

```gdscript
extends "res://Scripts/Pickup.gd"

func GetToD() -> String:
    var hours   = int(Simulation.time) / 100
    var minutes = int(Simulation.time) % 100
    minutes = int(floor(minutes * 0.6 / 5.0) * 5)
    if minutes >= 60:
        minutes = 0
        hours  += 1
    hours = hours % 24
    return "%02d:%02d" % [hours, minutes]

func UpdateTooltip():
    super()  # let vanilla (or ImmersiveXP) set the tooltip first
    if slotData and slotData.itemData.name == "Alarm Clock":
        gameData.tooltip += " (" + GetToD() + ")"
```

Extends the base `Pickup` script by file path. Calls `super()` first to allow the base tooltip to be set, then appends the time — but only for alarm clocks. `Simulation.time` provides the game's internal time value.

## HUD.gd: World Tooltip (The Tricky One)

```gdscript
extends "res://Scripts/HUD.gd"

var _alarm_time_shown := ""

func GetTime() -> String:
    var hours   = int(Simulation.time) / 100
    var minutes = int(Simulation.time) % 100
    minutes     = int(floor(minutes * 0.6 / 5.0) * 5)
    if minutes >= 60:
        minutes = 0
        hours  += 1
    hours = hours % 24
    return "%02d:%02d" % [hours, minutes]

func _physics_process(delta):
    super(delta)  # let the full chain run first

    if tooltip.visible and "Alarm Clock" in label.text:
        var t = GetTime()
        if t != _alarm_time_shown or "(" not in label.text:
            _alarm_time_shown = t
            var idx  = label.text.rfind(" (")
            var base = label.text.substr(0, idx) if idx != -1 else label.text
            label.text = base.replace("Alarm Clock", "Alarm Clock (" + t + ")")
    else:
        _alarm_time_shown = ""
```

This is more complex because vanilla rewrites `label.text` every frame. The override:
1. Calls `super(delta)` to run the entire chain first
2. Checks if "Alarm Clock" appears in the text
3. Surgically inserts the time
4. Caches `_alarm_time_shown` to prevent unnecessary label rewrites every frame

## The Chain in Action

With ImmersiveXP installed:

```
1. Vanilla HUD._physics_process()
   → Sets label.text = "Alarm Clock"

2. ImmersiveXP's HUD._physics_process()
   → Calls super(delta)  ← runs vanilla
   → Adds its own HUD enhancements

3. ToDOnClock's HUD._physics_process()
   → Calls super(delta)  ← runs ImmersiveXP (which runs vanilla)
   → Sees "Alarm Clock" in label.text
   → Appends " (14:35)"
   → Final: "Alarm Clock (14:35)"
```

The loader reports `CHAIN OK`. Without ImmersiveXP, the chain is simply ToDOnClock → Vanilla, and it works identically.

## Takeaways

- **Priority controls load order.** Set `priority=1` to load after target mods.
- **Call `super()` first** in lifecycle methods to let the chain execute before modifications.
- **Read the game's code.** The dual-tooltip system demonstrates why single overrides fail.
- **Self-destructing autoloads** are clean. Remove nodes that don't persist.
- **Override chaining works transparently** when everyone follows the pattern — small mods sit cleanly atop massive overhauls.

## What Next?

- [Compatibility Guide](../guides/compatibility.md) — understand compatible mod interactions
- [Publishing](../guides/publishing.md) — submit to ModWorkshop
