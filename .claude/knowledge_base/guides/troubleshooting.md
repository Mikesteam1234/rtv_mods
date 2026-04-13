# Troubleshooting & FAQ

> [Compatibility Guide](compatibility.md) | [Publishing](publishing.md) | Guides

## Common Problems

### Mod doesn't show up in the launcher

Extract your `.vmz`/`.zip` file. Check if `mod.txt` is at the root level or nested in a folder. The file structure should be:

```
Right:  mod.txt, mods/, ...
Wrong:  MyMod/mod.txt, MyMod/mods/, ...
```

### Game crashes on startup with mods

Review the log at `%AppData%\Road to Vostok Demo\logs\godot.log`. Common culprits:

- Backslash paths in the ZIP file (repack with 7-Zip)
- Script `extends` pointing to a non-existent path after game updates
- Replaced `Database.gd` with unresolved `preload()` paths
- Multiple mods overriding the same `class_name` script

### Script override does nothing

1. Verify `mod.txt` contains an `[autoload]` section
2. Confirm `take_over_path()` is being called by adding debug output
3. Check that `extends` uses the full `res://` path, not just the class name
4. Review `modloader_conflicts.txt` to see if another mod is taking priority

### Override works but other mods broke

Ensure all overridden methods include `super()` calls:

```gdscript
func _ready():
    super()
    # your code

func _process(delta):
    super(delta)
    # your code
```

### Tooltip works in inventory but not when looking at items

Road to Vostok uses two tooltip systems: `Pickup.UpdateTooltip()` for inventory and `HUD._physics_process()` for world items. Override both to ensure consistent behavior. See the [ToDOnClock walkthrough](../walkthroughs/todon-clock.md) for the pattern.

### Game updated and mod broke

1. Check `modloader_conflicts.txt` for new errors
2. Decompile the updated game files
3. Compare your overridden scripts against new versions
4. Update `extends` paths if files moved or method signatures changed
5. Bump version and release an update

### Works alone but crashes with other mods

Examine `modloader_conflicts.txt` for:

- `CONFLICT: take_over_path` — two mods claiming the same script (hard incompatibility)
- `CHAIN BROKEN` — a mod isn't calling `super()`
- `DATABASE OVERRIDE` — preload timing issue

## FAQ

### Do I need to replace the game's PCK or package my mod as a PCK?

No. Your mod is a `.zip` (or `.vmz`) containing only new or modified files. The loader mounts it at runtime, layering your content over the base game without touching the original PCK.

### Can I use class_name in my scripts?

Yes, in your own scripts. However, `class_name` scripts can only be overridden once due to a Godot 4 limitation. If you use `class_name`, other mods cannot override those scripts.

### Can I add new scenes or resources?

Yes. Place them in `mods/YourMod/` and access them at `res://mods/YourMod/whatever.tscn`. Include the `.godot/exported/` directory for scenes with custom nodes.

### Can I unload a mod at runtime?

No. Once mounted, the resource pack remains loaded until restart. Enable or disable mods through the launcher before launching the game.

### Is there a sandbox?

No. Mods run with the same privileges as the game. GDScript can read and write files via `FileAccess`. Only install mods from trusted sources.

### Linux / Steam Deck?

The mod loader targets Windows. While Godot's core techniques (PCK mounting, script overrides) are cross-platform, the launcher UI and file paths would require adaptation.

### Where are mod settings saved?

Settings are stored in `%AppData%\Road to Vostok Demo\mod_config.cfg`, tracking enabled mods and their load order.

### Can I use C#?

No. Road to Vostok uses the standard (non-.NET) Godot 4 build, which supports GDScript only.

## Debug Tricks

**Print debugging:** Use `print()` statements; output appears in `%AppData%\Road to Vostok Demo\logs\godot.log`

**Dump the scene tree:**
```gdscript
func _ready():
    print_tree_pretty()
```

**Check if an override is active:**
```gdscript
var weapon = load("res://Scripts/Weapon.gd")
print(weapon.source_code.substr(0, 100))
```

**The conflict report** (`modloader_conflicts.txt`) is your most valuable debugging resource, showing load order, file conflicts, and chain analysis.

## What Next?

- [Tools & Resources](../reference/tools-and-resources.md) — downloads and links
- [Decompiling the Game](../getting-started/decompiling.md) — explore game code
