# Decompiling the Game

> [Installing Mods](installing-mods.md) | [First Mod](first-mod.md) | Getting Started

To create script modifications, you must extract and decompile the game's `.pck` file to access readable GDScript source code. While texture and sound replacements don't require this step, any code-based mods depend on decompilation.

## Tools

### GDRE Tools (gdsdecomp)

The most widely-used decompilation utility, offering a graphical interface for extraction and decompilation simultaneously.

- **Source:** https://github.com/GDRETools/gdsdecomp
- Compatible with Godot versions 2.x through 4.x
- Two operational modes: Extract-only (quick file extraction) or Full Recovery (complete decompilation into a functional Godot project)

### GodotPckTool

A command-line alternative for those preferring terminal-based workflows or script automation.

- **Source:** https://github.com/hhyyrylainen/GodotPckTool
- Command syntax: `godotpcktool "path\to\Road to Vostok Demo.pck" --action extract --output "output\path"`
- Extracts files but produces `.gdc` bytecode files requiring GDRE Tools for decompilation conversion

## Full Recovery Walkthrough

1. Download and launch GDRE Tools
2. Navigate to **RE Tools > Recover project...**
3. Direct the tool to the game's `.pck` file:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\Road to Vostok Demo\Road to Vostok Demo.pck
   ```
4. Select **Full Recovery** mode
5. Specify output directory and execute

### Using the Godot Editor

1. Obtain the matching Godot version (currently 4.6.1 as of early 2026)
2. Open Godot, select Import, locate your decompiled folder, and open `project.godot`
3. Initial import requires time for texture and mip-map re-processing

The decompiled project functions primarily as a research tool, allowing script inspection and scene tree exploration. Games utilizing GDExtension dependencies may encounter errors or crashes when run from the editor.

## Essential Files Reference

| File | Purpose |
|------|---------|
| `Scripts/Database.gd` | Item definitions, scene paths, preloads — start here for item modifications |
| `Scripts/Character.gd` | Player movement mechanics, stamina, health systems |
| `Scripts/Weapon.gd` | Firing mechanics, reload cycles, recoil behavior |
| `Scripts/HUD.gd` | Tooltip rendering, UI state management; frequently modified |
| `Scripts/Pickup.gd` | Item interaction logic, inventory tooltips |
| `Scripts/Interface.gd` | Inventory interface, item instantiation, context menus |
| `Scripts/AI.gd` | Enemy behavior patterns |
| `Scripts/Transition.gd` | Level transitions, weather systems, time progression |

## Version Update Procedures

When game updates affect mod functionality:

1. Rename previous decompiled folder with build date identifier
2. Decompile new version into separate folder
3. Compare modified scripts against your overridden files

Focus on identifying:
- Changed method signatures that affect `super()` calls
- Relocated or renamed files impacting `extends` statements
- New properties offering opportunities
- Restructured node trees affecting `get_node()` references

## Practical Tips

- Maintain the decompiled project for continuous reference without direct editing
- Leverage search-in-files functionality for tracing implementation details
- Always consult `Database.gd` when working with item-related modifications

## Next Steps

- [Core Concepts](../reference/core-concepts.md) — understand how decompiled code relates to modding workflows
- [Modding Techniques](../techniques/modding-techniques.md) — practical application
