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

## Game Internals

Decompiled-source reference — *what to mod against* (complement to the how-to-mod docs above). See [game-internals/index.md](game-internals/index.md) for the full map.

| File | Summary |
|------|---------|
| [game-internals/index.md](game-internals/index.md) | Top-level facts (engine, autoloads, `GameData`, groups, physics tick), scene-tree orientation, doc map |
| [game-internals/autoloads-and-boot.md](game-internals/autoloads-and-boot.md) | `Loader`, `Database`, `Simulation`, `GameData`, boot flow, scene-change pipeline |
| [game-internals/player-system.md](game-internals/player-system.md) | `Controller`, `Character`, `Camera`, `Inputs`, head rig, movement, vitals |
| [game-internals/weapons-and-combat.md](game-internals/weapons-and-combat.md) | `WeaponRig`, `Handling`, grenade/knife/fishing rigs, `Hit`, `Damage`, `Hitbox`, `RigManager` |
| [game-internals/ai-system.md](game-internals/ai-system.md) | `AI`, `AIPoint`, `AISpawner`, state machine, `BTR`, `Police`, `Helicopter`, ragdoll |
| [game-internals/items-and-loot.md](game-internals/items-and-loot.md) | `Item`, `ItemData` + subclasses, `Slot`, `Grid`, `LootContainer`, `LootTable` |
| [game-internals/world-and-levels.md](game-internals/world-and-levels.md) | `World`, time of day, weather, `Spawner`, `Transition`, `Border`, `Optimizer`, shelters |
| [game-internals/ui-system.md](game-internals/ui-system.md) | `HUD`, `Interface`, `Menu`, `Settings`, `Loading`, `NVG`, `UIManager` |
| [game-internals/audio-system.md](game-internals/audio-system.md) | `Audio`, `AudioLibrary`, `AudioEvent`, 2D/3D instances, buses, music, casette/radio |
| [game-internals/save-system.md](game-internals/save-system.md) | `*Save` resources, `Preferences`, `Validator`, persistence paths in `user://` |
| [game-internals/events-and-tasks.md](game-internals/events-and-tasks.md) | `EventSystem`, `EventData`, `Event`, trader `TaskData`, `Detector`, `Condition` |
| [game-internals/crafting-and-traders.md](game-internals/crafting-and-traders.md) | `Recipe`/`RecipeData`/`Recipes`, `Trader`/`TraderData`, crafting UI flow |
| [game-internals/shelter-and-interactables.md](game-internals/shelter-and-interactables.md) | `Furniture`, `Placer`, `DecorMode`, beds, doors, fire/fuel, cables, switches, cat/fish |
| [game-internals/scenes-reference.md](game-internals/scenes-reference.md) | Key scene graphs: `Menu`, `Core`, level wrappers, autoload scenes |
| [game-internals/resources-reference.md](game-internals/resources-reference.md) | Layout of `Items/`, `Loot/`, `AI/`, `Events/`, `Traders/`, `Crafting/`, `Resources/` |

## Clean Code

Distilled from Robert C. Martin, *Clean Code: A Handbook of Agile Software Craftsmanship* (2nd ed.). See [clean-code/index.md](clean-code/index.md) for the full section index. Used by the [`code-reviewer`](../agents/code-reviewer.md) agent.

| File | Summary |
|------|---------|
| [clean-code/index.md](clean-code/index.md) | Section map; how Clean Code principles translate to GDScript / RTV |
| [clean-code/first-principles.md](clean-code/first-principles.md) | What "clean" means; Boy Scout Rule; 10:1 read/write ratio; small / well-named / organized / ordered |
| [clean-code/names.md](clean-code/names.md) | Intention-revealing, pronounceable, searchable names; length-by-scope rules; no disinformation or noise |
| [clean-code/comments.md](clean-code/comments.md) | Comments as failure; good vs. bad kinds; delete commented-out code; repo prefers no comments |
| [clean-code/formatting.md](clean-code/formatting.md) | Vertical/horizontal formatting; newspaper metaphor; defers to `godot/gdscript-style-guide.md` |
| [clean-code/functions.md](clean-code/functions.md) | Small; one thing; one level of abstraction; stepdown; few args; CQS; prefer exceptions |
| [clean-code/objects-and-classes.md](clean-code/objects-and-classes.md) | Object/data antisymmetry; Law of Demeter; DTOs; SRP at class scope; cohesion |
| [clean-code/testing.md](clean-code/testing.md) | TDD/TCR/Small Bundles; F.I.R.S.T.; test DSLs; RTV's deploy-and-play equivalent |
| [clean-code/simple-design-and-solid.md](clean-code/simple-design-and-solid.md) | Kent Beck's four rules; YAGNI; SOLID (SRP/OCP/LSP/ISP/DIP) |
| [clean-code/architecture-and-components.md](clean-code/architecture-and-components.md) | Two values of software; REP/CCP/CRP; ADP/SDP/SAP; the Clean Architecture rings |
| [clean-code/concurrency.md](clean-code/concurrency.md) | Why concurrency is hard; defense principles; Godot's main-thread rule |
| [clean-code/craftsmanship.md](clean-code/craftsmanship.md) | The Programmer's Oath; harm; small cycles; relentless improvement |

## Godot 4.6.1 Reference

Distilled from the [official Godot 4.6 documentation](https://docs.godotengine.org/en/stable/). See [godot/index.md](godot/index.md) for the full section index.

| File | Summary |
|------|---------|
| [godot/gdscript-basics.md](godot/gdscript-basics.md) | Variables, types, operators, control flow, functions, classes, inheritance, enums, annotations |
| [godot/gdscript-typing-and-exports.md](godot/gdscript-typing-and-exports.md) | Static typing, typed arrays/dicts, `@export` annotations, ranges, hints |
| [godot/gdscript-style-guide.md](godot/gdscript-style-guide.md) | Naming conventions, formatting, file ordering, documentation comments |
| [godot/scene-tree-and-nodes.md](godot/scene-tree-and-nodes.md) | SceneTree lifecycle, `_ready`/`_process`/`_input` order, instancing, node references |
| [godot/signals-and-groups.md](godot/signals-and-groups.md) | Signal declaration/connection/emission, groups, `get_nodes_in_group()` |
| [godot/resources-and-loading.md](godot/resources-and-loading.md) | Resource vs Node, `load()`/`preload()`, `ResourceLoader`, `res://` vs `user://` |
| [godot/autoloads-and-singletons.md](godot/autoloads-and-singletons.md) | Autoload setup, access patterns, when to use autoloads vs node injection |
| [godot/input-system.md](godot/input-system.md) | InputEvent hierarchy, InputMap, `_input` vs `_unhandled_input`, `Input` singleton |
| [godot/notifications-and-lifecycle.md](godot/notifications-and-lifecycle.md) | NOTIFICATION constants, lifecycle order, `delta`, `process_mode`, pausing |
| [godot/class-reference-node.md](godot/class-reference-node.md) | Node class: key properties, methods, signals, virtual methods |
| [godot/class-reference-essentials.md](godot/class-reference-essentials.md) | SceneTree, Resource, PackedScene, Tween, Timer — curated API |
| [godot/best-practices.md](godot/best-practices.md) | Composition vs inheritance, call down / signal up, duck typing, interfaces |

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
