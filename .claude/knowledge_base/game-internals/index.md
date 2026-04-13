# Game Internals — Reference

Maps Road to Vostok's decompiled GDScript, scene graphs, and resource layouts. Source of truth is `/mnt/c/Dev/RTV/Decomp/` (regenerate with `Scripts/decomp.py`). Treat everything here as **read-only reference** for authoring script overrides.

Companion to the modding wiki mirror under `knowledge_base/` — that explains *how to mod*; this explains *what to mod against*.

---

## Top-level facts

- **Engine:** Godot 4.6 (Forward+), Windows D3D12 by default.
- **Main scene:** `res://Scenes/Menu.tscn` (resolved from uid in `project.godot`).
- **Autoloads** (singleton, in load order): `Loader`, `Database`, `Simulation`. Every gameplay script accesses these by name.
- **Global shared state:** `res://Resources/GameData.tres` — a single `GameData` resource preloaded by ~every script. Flags like `gameData.isAiming`, `gameData.freeze`, `gameData.shelter` drive most behavior.
- **Global groups** declared in `project.godot`: `Furniture`, `Interactable`, `Item`, `AI`, `AI_CP/PP/HP/SP/WP/GP/BTR/VP`, `Player`, `Transition`, `Switch`, `Display`, `Blocker`, `Trader`, `Radio`, `Well`, `Cat`.
- **Physics:** 120 ticks/sec. **Navigation cell:** 0.12.
- **Scene naming:** `.tscn` = text (human-readable), `.scn` = packed binary (heavy outdoor levels).

## Doc map

| File | Covers |
|------|--------|
| [autoloads-and-boot.md](autoloads-and-boot.md) | `Loader`, `Database`, `Simulation`, `GameData`, boot flow, scene-change pipeline |
| [player-system.md](player-system.md) | `Controller`, `Character`, `Camera`, `Inputs`, head rig, movement, vitals |
| [weapons-and-combat.md](weapons-and-combat.md) | `WeaponRig`, `Handling`, grenade/knife/fishing rigs, `Hit`, `Damage`, `Hitbox`, `RigManager` |
| [ai-system.md](ai-system.md) | `AI`, `AIPoint`, `AISpawner`, state machine, `BTR`, `Police`, `Helicopter`, ragdoll |
| [items-and-loot.md](items-and-loot.md) | `Item`, `ItemData` + subclasses, `Slot`, `Grid`, `LootContainer`, `LootTable` |
| [world-and-levels.md](world-and-levels.md) | `World`, time of day, weather, `Spawner`, `Transition`, `Border`, `Optimizer`, shelters |
| [ui-system.md](ui-system.md) | `HUD`, `Interface`, `Menu`, `Settings`, `Loading`, `NVG`, `UIManager` |
| [audio-system.md](audio-system.md) | `Audio`, `AudioLibrary`, `AudioEvent`, 2D/3D instances, buses, music, casette/radio |
| [save-system.md](save-system.md) | `*Save` resources, `Preferences`, `Validator`, persistence paths in `user://` |
| [events-and-tasks.md](events-and-tasks.md) | `EventSystem`, `EventData`, `Event`, trader `TaskData`, `Detector`, `Condition` |
| [crafting-and-traders.md](crafting-and-traders.md) | `Recipe`/`RecipeData`/`Recipes`, `Trader`/`TraderData`, crafting UI flow |
| [shelter-and-interactables.md](shelter-and-interactables.md) | `Furniture`, `Placer`, `DecorMode`, beds, doors, fire/fuel, cables, switches, cat/fish |
| [scenes-reference.md](scenes-reference.md) | Key scene graphs: `Menu`, `Core`, level wrappers, autoload scenes |
| [resources-reference.md](resources-reference.md) | Layout of `Items/`, `Loot/`, `AI/`, `Events/`, `Traders/`, `Crafting/`, `Resources/` |

## Quick orientation

Whenever the game is in-world, the scene tree under `/root/Map` looks like:

```
/root/Map (Node3D, script: World.gd — script is on the Map node for shelters; on Content for outdoor levels)
├── Content (NavigationRegion3D) — actual level geometry, instanced per map
├── World (Node3D, World.gd) — time of day, weather, skybox, ambient audio
├── Core (Node3D) — instance of res://Scenes/Core.tscn, carries player + UI + camera
│   ├── UI (Control) — Effects, NVG, HUD, Settings, Interface
│   ├── Camera (Camera3D) — Manager (rigs), Placer, Interactor, Flashlight, Flash, LOS
│   ├── Controller (CharacterBody3D) — Character, colliders, pelvis→head chain
│   ├── Audio (Node3D) — Music/Breathing/Heartbeat/Suffering/Suffocating streams
│   └── Tools (Node) — Compiler, Decor
└── Killbox (Area3D) — catches the player if they fall out of world
```

The three autoloads live at `/root/Loader`, `/root/Database`, `/root/Simulation`. The main menu has a different (simpler) tree — no `Map`, no `Core`.

Node paths like `"/root/Map/Core/UI/Interface"` are hardcoded throughout the codebase — `Loader.gd` alone uses them ~10 times. If you override a script you must preserve these expectations.
