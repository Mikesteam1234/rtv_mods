# Core Concepts

> Reference | [Mod Structure](mod-structure.md) | [Tools & Resources](tools-and-resources.md)

Five concepts. Once you get these, the rest of modding falls into place.

## The `res://` Virtual Filesystem

Every Godot game packs its assets into a virtual filesystem rooted at `res://`. When the game calls `load("res://Scripts/Weapon.gd")`, Godot looks that up in its internal file table.

Here's the important bit: when you load a mod archive (PCK or ZIP), its files get injected into that same filesystem. If your mod has a file at `res://Scripts/Weapon.gd`, it replaces the game's version. That's the whole foundation of Godot modding right there.

```
Game's res://                     Mod's res://
├── Scripts/                      ├── Scripts/
│   ├── Weapon.gd                 │   └── Weapon.gd  ← REPLACES original
│   ├── Character.gd              └── mods/
│   └── Database.gd                   └── MyMod/
├── Scenes/                               └── Main.gd  ← NEW file
└── ...
```

## Mods Are Layered On Top, Not Baked In

**You do not touch, copy, or replace the game's `.pck` file.** That file is the entire game bundled into one archive. Your mod is a separate archive that sits alongside it.

When the mod loader mounts your mod's zip, your files get layered on top of the game's existing files at runtime. Everything you _didn't_ include still loads from the original game PCK untouched. You only ship the files you changed or added.

### What format should my mod be?

| Format | When to use it |
|--------|----------------|
| `.zip` / `.vmz` | **Use this.** Standard zip, compressed, small. Easy to create (right-click → compress) and easy to inspect. `.vmz` is just a renamed `.zip`. |
| `.pck` | Godot's native binary format. It works with the mod loader, but it's uncompressed (bigger than zip) and you need Godot's export tools to create one. Rarely a reason to use it. |

The mod loader uses `ProjectSettings.load_resource_pack(path)` to mount both formats. They work identically at runtime.

A few things to be aware of:

- Resource packs can't be unloaded at runtime — removing a mod means restarting the game
- `load_resource_pack()` returns `false` on failure without throwing an exception (error details may appear in the engine log)
- Load order matters: if two packs have the same file, the last one loaded wins

## `take_over_path()`: Script Replacement

File-level replacement via resource packs works fine for assets, but scripts need special treatment because Godot may have already loaded and cached them. `take_over_path()` tells the engine: "from now on, when anyone asks for the script at this path, give them mine instead."

```gdscript
var script: Script = load("res://MyMod/WeaponOverride.gd")
script.reload()
var parent = script.get_base_script()
script.take_over_path(parent.resource_path)
```

After that call, every node using `res://Scripts/Weapon.gd` runs your override instead. The pattern works like this:

1. Your override script `extends "res://Scripts/Weapon.gd"` (the original)
2. Your Main.gd autoload loads the override, calls `reload()`, gets the base, and calls `take_over_path()`
3. The game runs your version, which can call `super()` to invoke the original behavior

**One gotcha:** In Godot 4, scripts with `class_name` can only be overridden **once** due to [engine bug #83542](https://github.com/godotengine/godot/issues/83542). If two mods both `take_over_path()` the same `class_name` script, the game will **crash** with a fatal error at startup. This is a hard crash, not a silent failure.

## Autoloads: Your Mod's Entry Point

In standard Godot, autoloads are singleton nodes added to `/root/`. With the Metro Mod Loader, mod autoloads work similarly but are added as **children of the ModLoader node** (not direct children of `/root/`). The effect is the same — your code runs at startup — but the tree path is different.

In `mod.txt`:

```ini
[autoload]
MyMod="res://mods/MyMod/Main.gd"
```

This creates a node that runs your `Main.gd`. From `_ready()`, you can override game scripts with `take_over_path()`, add child nodes like UI overlays, connect to signals, or access game singletons.

Autoload ordering matters. The mod loader processes mods by priority (then alphabetically), and autoloads run in that order. If your mod depends on another mod's overrides being in place first, set your priority so you load after it.

## The `preload()` Timing Problem

`preload()` loads resources at compile time, before any mod packs are mounted. So if the game uses `preload("res://Scripts/Weapon.gd")`, your mod's replacement won't affect code that already preloaded it.

`load()` (runtime) and `take_over_path()` are the modder's tools here. They respect mounted packs because they run later.

`Database.gd` is the big pain point: it preloads every item and scene path in the game. If you replace it, your version needs every single preload path to be valid or the whole script fails to parse. This is why `take_over_path()` exists as a separate mechanism — it patches the engine's script cache after loading, working around preload.

## How It All Fits Together

Here's what happens when you launch the game with mods:

```
1. Godot starts
2. override.cfg tells Godot to autoload modloader.gd
3. Mod loader UI appears (Mods / Compatibility / Updates tabs)
4. You click "Launch Game"
5. For each enabled mod (by priority, then alphabetically):
   a. Mount the archive → files enter res://
   b. Parse mod.txt
   c. Instantiate autoload scripts as children of the ModLoader node
6. Autoload _ready() functions run
   - Script overrides (take_over_path) happen here
   - UI elements get created here
   - Signal connections get made here
7. Current scene is reloaded (reload_current_scene())
   - This forces all nodes to pick up the overridden scripts
8. Game runs with all mod overrides active
```

## What Next?

- [Mod Structure](mod-structure.md) — the `mod.txt` format and how to package your mod
- [Modding Techniques](../techniques/modding-techniques.md) — putting these concepts to work
