# Mod Structure & mod.txt

> [Core Concepts](core-concepts.md) | Reference | [Tools & Resources](tools-and-resources.md)

A mod is fundamentally a zip file containing a configuration file and scripts. This guide explains the proper file organization for the mod loader to locate all components.

## File Layout

A mod archive (`.vmz` or `.zip`) requires `mod.txt` at its root. Mod files should be placed in a namespaced subfolder:

```
MyMod.vmz (or .zip)
├── mod.txt                          ← at archive root
├── mods/
│   └── MyMod/
│       ├── Main.gd                  ← autoload entry point
│       ├── SomeOverride.gd          ← script overrides
│       └── textures/
│           └── custom_icon.png      ← custom assets
└── .godot/
    └── exported/                    ← only needed for custom scenes
        └── .../
```

### Why namespace under `mods/YourModName/`?

When the archive mounts, all files become part of `res://`. Without namespacing, two mods sharing the same filename would conflict. The `mods/YourModName/` structure prevents collisions with the game and other mods.

**Exception:** Intentional game file replacements should use the original game path (e.g. `Textures/UI/crosshair.png`).

## mod.txt

Uses Godot's ConfigFile format (INI-style). Three sections are available:

### [mod]: Required

```ini
[mod]
name="My Cool Mod"
id="my-cool-mod"
version="1.0.0"
priority=0
```

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Display name in launcher |
| `id` | Yes | Unique identifier (a-z, -, _) |
| `version` | For updates | Semver format (1.2.3) |
| `priority` | No | Load order weight; higher loads later |

### [autoload]: Optional

```ini
[autoload]
MyModMain="res://mods/MyMod/Main.gd"
MyModConfig="res://mods/MyMod/Config.gd"
```

Creates nodes running specified scripts or scenes. Scripts must extend `Node` or a subclass. Can also reference `.tscn` PackedScene files.

### [updates]: Optional

```ini
[updates]
modworkshop=55672
```

Specify the numeric ModWorkshop ID to enable update checking and downloads via the launcher's Updates tab.

## Packaging

### The Critical Rule

`mod.txt` must be at the root of the archive, not inside a subfolder.

```
✅  Archive root → mod.txt, mods/, ...
❌  Archive root → MyMod/ → mod.txt, mods/, ...
```

This is the most common reason mods fail to appear in the launcher.

### Archive Formats

| Format | Notes |
|--------|-------|
| `.zip` | Standard format; use forward-slash paths |
| `.vmz` | Zip with different extension (community convention) |
| `.pck` | Godot binary format; limited features, uncompressed |

### The Backslash Bug

Windows tools sometimes write backslash paths in ZIPs (`mods\MyMod\Main.gd`). Godot requires forward slashes (`mods/MyMod/Main.gd`) and silently fails otherwise.

- **7-Zip** consistently uses forward slashes — use this
- PowerShell/.NET users should verify path formats

### Custom Scenes

Mods with `.tscn` files need the exported/imported versions. Include `.godot/exported/` in the archive. Use Project > Export > Export PCK/Zip in Godot.

## Mods Without mod.txt

Archives lacking `mod.txt` mount as resource packs, entering `res://` and replacing game assets. However, they lack autoloads, UI naming, update checking, and priority control. Suitable for simple texture swaps only.

## Dev Workflow

Re-zipping constantly becomes tedious. Keep source files in a working directory during development. Zip only for integration testing.

Full testing: zip → place in `mods/` → launch → check `modloader_conflicts.txt` and `logs/godot.log`.

7-Zip CLI speeds the process:
```
7z a -tzip MyMod.zip mod.txt mods/
```

## What Next?

- [Modding Techniques](../techniques/modding-techniques.md) — the four core approaches for building mods
- [Compatibility Guide](../guides/compatibility.md) — ensuring compatibility with other mods
