# Vostok Modding Wiki — Knowledge Base Index

Source: https://github.com/ametrocavich/vostok-modding-wiki/wiki

---

## Getting Started

| File | Summary |
|------|---------|
| [getting-started/installing-mods.md](getting-started/installing-mods.md) | Install the Metro Mod Loader, create the mods folder, install and manage mods |
| [getting-started/first-mod.md](getting-started/first-mod.md) | Build a working mod from scratch — `mod.txt`, `Main.gd`, zip packaging, testing |
| [getting-started/decompiling.md](getting-started/decompiling.md) | Extract game source with GDRE Tools or GodotPckTool; key script reference table |

## Reference

| File | Summary |
|------|---------|
| [reference/core-concepts.md](reference/core-concepts.md) | `res://` virtual filesystem, `take_over_path()`, autoloads, `preload()` timing problem, full boot flow |
| [reference/mod-structure.md](reference/mod-structure.md) | `mod.txt` format (`[mod]`, `[autoload]`, `[updates]`), packaging rules, backslash bug |
| [reference/tools-and-resources.md](reference/tools-and-resources.md) | Tool links, file path reference, `mod.txt` template, override pattern cheat sheet |

## Techniques

| File | Summary |
|------|---------|
| [techniques/modding-techniques.md](techniques/modding-techniques.md) | 4 core techniques: asset replacement, autoload scripts, `take_over_path()` overrides, custom file loading |
| [techniques/advanced-techniques.md](techniques/advanced-techniques.md) | Singleton replacement, resource extension, coroutines, shaders, save/load, intermod checks, and more |

## Guides

| File | Summary |
|------|---------|
| [guides/compatibility.md](guides/compatibility.md) | Conflict report messages, `super()` rules, priority, update survival strategies |
| [guides/publishing.md](guides/publishing.md) | ModWorkshop upload process, auto-update setup, versioning conventions |
| [guides/troubleshooting.md](guides/troubleshooting.md) | Common failure modes, FAQ, debug tricks (`print_tree_pretty`, conflict report) |

## Walkthroughs

| File | Summary |
|------|---------|
| [walkthroughs/item-spawner.md](walkthroughs/item-spawner.md) | Scene-based autoload, zero script overrides, defensive coding, dual data paths |
| [walkthroughs/todon-clock.md](walkthroughs/todon-clock.md) | Override chaining, priority ordering, dual tooltip system (inventory + world) |

---

## Key Facts at a Glance

- **Mod format:** `.vmz` or `.zip` (identical; `.vmz` is community convention)
- **`mod.txt` must be at archive root** — nested placement breaks the launcher
- **Always call `super()`** in overridden lifecycle methods or you break the chain
- **`take_over_path()` + `class_name` scripts:** only overridable once (Godot 4 bug #83542)
- **Log location:** `%AppData%\Road to Vostok Demo\logs\godot.log`
- **Conflict report:** `%AppData%\Road to Vostok Demo\modloader_conflicts.txt`
- **Game version (early 2026):** Godot 4.6.1
- **Use `get_node_or_null()`** not `get_node()` — game world doesn't exist on main menu
