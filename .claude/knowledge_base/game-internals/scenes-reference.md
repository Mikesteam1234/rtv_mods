# Scenes Reference

High-level scene layout and what lives where. Path-based reference for override authoring: when you need to know `get_node("/root/...")`, start here.

## Top-level scenes (`res://Scenes/`)

| Scene | Type | Purpose |
|---|---|---|
| `Menu.tscn` | `.tscn` | Main menu. Root is `Menu.gd`. No `Core`, no `World`. |
| `Intro.tscn` | `.tscn` | New-game cinematic. World static + intro audio. |
| `Death.tscn` | `.tscn` | Death screen (Load/Menu/Quit). |
| `Tutorial.tscn` | `.tscn` | Tutorial shelter. Same shape as other shelters. |
| `Cabin.tscn` | `.tscn` | Shelter (always unlocked at start). |
| `Attic.tscn` | `.tscn` | Shelter. |
| `Classroom.tscn` | `.tscn` | Shelter. |
| `Tent.tscn` | `.tscn` | Shelter (always unlocked at start). |
| `Bunker.tscn` | `.tscn` | Shelter. |
| `Village.scn` | `.scn` | Outdoor zone. |
| `School.scn` | `.scn` | Outdoor zone (member of `Loader.randomScenes`). |
| `Highway.scn` | `.scn` | Outdoor zone (member of `randomScenes`). |
| `Outpost.scn` | `.scn` | Outdoor zone (member of `randomScenes`). |
| `Minefield.scn` | `.scn` | Outdoor zone. |
| `Apartments.scn` | `.scn` | Outdoor zone. |
| `Terminal.scn` | `.scn` | Outdoor zone. |
| `Template.scn` | `.scn` | Dev/sandbox map — only non-shelter that allows decor mode. |

Shelter names that matter to `Loader`:
```gdscript
const shelters = ["Cabin", "Attic", "Classroom", "Tent", "Bunker"]
```

## Autoloads (loaded at boot, before any scene)

Registered in `project.godot`. Instantiated from `res://Resources/<Name>.tscn`:

| Path | Script | Purpose |
|---|---|---|
| `/root/Database` | `Database.gd` | Central scene lookup by `ItemData.file` string. Populated at boot from `res://Items/` tree. |
| `/root/Loader` | `Loader.gd` | Save/load + scene transitions + fade overlay + messages. |
| `/root/Simulation` | `Simulation.gd` | Global clock (day/time/weather). |

GameData lives at `res://Resources/GameData.tres` — a preloaded resource, not an autoload node. Accessed by `preload("res://Resources/GameData.tres")`.

## Core scene (`res://Scenes/Core.tscn`)

Instantiated as a child of every **non-menu** map's root. Holds player, camera, UI, audio, AI spawner. Canonical paths:

```
/root/Map                       (Map.gd — script on scene root)
├── Core                        (Core.tscn instance)
│   ├── Controller              (Controller.gd — CharacterBody3D)
│   ├── Character               (Character.gd — vitals/medical driver)
│   ├── Detector                (Detector.gd — Area3D → gameData flags)
│   ├── Camera                  (Camera3D)
│   │   ├── Manager             (RigManager.gd — weapon rig slot)
│   │   ├── Flashlight          (Flashlight.gd — SpotLight3D)
│   │   ├── Placer              (Placer.gd — item/furniture placement)
│   │   ├── Interactor          (Interactor.gd — ray hit → Interact() dispatch)
│   │   └── UIPosition nodes    (magazine/chamber ammo-check popups)
│   ├── Audio                   (Audio.gd — per-player audio state)
│   │   ├── Music
│   │   ├── Breathing
│   │   ├── Heartbeat
│   │   ├── Suffering
│   │   └── Suffocating
│   └── UI                      (UIManager.gd)
│       ├── HUD                 (HUD.gd)
│       ├── Interface           (Interface.gd — inventory/crafting/trader)
│       ├── Settings            (Settings.gd)
│       ├── NVG                 (NVG.gd)
│       ├── Effects             (Effects.gd — screen shaders)
│       └── Tooltip             (Tooltip.gd — item hover)
├── World                       (World.gd — sky/TOD/weather)
│   ├── Planet (Sun/Moon)
│   ├── Audio (Dawn/Day/Dusk/Night + weather beds)
│   ├── VFX (Rain/Snow)
│   └── Environment (WorldEnvironment)
├── AISpawner                   (AISpawner.gd — outdoor maps)
│   ├── A_Pool                  (regular agents)
│   ├── B_Pool                  (boss)
│   └── Agents                  (active agents live here when spawned)
├── EventSystem                 (EventSystem.gd — outdoor maps)
│   ├── Paths                   (Police/BTR waypoint chains)
│   └── Crashes                 (Helicopter crash candidates)
├── DynamicAmbient              (DynamicAmbient.gd — outdoor maps)
├── Killbox                     (Killbox.gd — Area3D safety net)
├── Border / BorderPoles        (Border.gd — outdoor maps only)
└── <level geometry>            (Terrains, Optimizer groups, props)
```

Paths that code literally hard-codes (grep-friendly):
- `/root/Map`
- `/root/Map/Core/Controller`
- `/root/Map/Core/Character`
- `/root/Map/Core/Camera`
- `/root/Map/Core/Camera/Manager`
- `/root/Map/Core/Camera/Flashlight`
- `/root/Map/Core/Camera/Interactor`
- `/root/Map/Core/Audio`
- `/root/Map/Core/UI`
- `/root/Map/Core/UI/HUD`
- `/root/Map/Core/UI/Interface`
- `/root/Map/Core/UI/Settings`
- `/root/Map/Core/UI/NVG`
- `/root/Map/Core/UI/Effects`

Any override that moves these nodes breaks every lookup that hard-codes them.

## Menu scene (`res://Scenes/Menu.tscn`)

Root = `Menu.gd`. Different shape — no `Core`, no `Map`:

```
/root/Menu                      (Menu.gd)
├── Main                        (buttons: New / Load / Tutorial / Settings / Roadmap / About / Quit)
├── Modes                       (Difficulty: Standard/Darkness/Ironman × Season: Dynamic/Summer/Winter)
├── Roadmap
├── Settings                    (reuses Settings.gd with menu-scene wiring)
├── About
├── API                         (DirectX/Vulkan indicators)
├── Profiler                    (Profiler.gd — hardware banner)
├── Log / Hardware / Intro / Music (toggle widgets)
└── blocker                     (MOUSE_FILTER_IGNORE during scene change)
```

`/root/Loader` (autoload) is the same node — it overlays fade/label/circle/messages on top of every scene.

## Death scene (`res://Scenes/Death.tscn`)

Minimal:
```
/root/Death                     (Death.gd)
├── Permadeath banner
└── Buttons (Load / Menu / Quit)
```
Load is disabled if `ValidateShelter() == ""`.

## Shelter scenes (`.tscn`)

All shelter roots follow the same pattern. Example: `Cabin.tscn`:
```
/root/Map                       (Map.gd — mapName="Cabin", mapType="Shelter")
├── Core                        (Core.tscn instance — the shared player stack)
├── World                       (shelter=true — World.Static() mode, no weather)
├── <Geometry, Transitions>     (doors out to outdoor maps)
├── <Interactables>             (Bed, Fire, Door, Switch, Radio, Television, CatBox, etc.)
└── <Furniture>                 (Furniture-group nodes placed by player — respawned from ShelterSave)
```

Shelters don't have `AISpawner`, `EventSystem`, `DynamicAmbient`, or `Border`. They're sized to fit in a single room or small building.

## Outdoor scenes (`.scn`)

Binary. Large — include terrain, vegetation Spawners, AI point markers, Police/BTR paths, event crash sites, Border/BorderPoles, Optimizer-merged static meshes.

```
/root/Map                       (Map.gd — mapName=..., mapType="Area 05"/"Border Zone"/"Vostok")
├── Core                        (Core.tscn instance)
├── World                       (full weather/TOD simulation)
├── AISpawner                   (with its spawn-point groups registered)
├── EventSystem
├── DynamicAmbient
├── Killbox
├── Border                      (procedural)
├── Terrains/<Name>/Spawner_*   (vegetation scatter via Spawner.gd)
├── Optimizer                   (merged static collisions)
└── <Level geometry>
```

Because outdoor maps are binary, editing structure requires opening in Godot — you can't patch via text diff.

## Scene transitions

Driven by `Transition.gd` nodes in group `"Transition"`. The Transition node exports `nextMap: String` (matches a const in `Loader.gd`). On `Interact()`:
1. `Loader.LoadScene(nextMap)` — fade out, change `current_scene`, fade in.
2. Simulation clock advances by `time * 100.0`.
3. Character + World + Shelter (if exiting a shelter) saves fire before the scene swap.

Random outdoor picks via `Loader.LoadSceneRandom()` → pulls from `randomScenes = [School, Highway, Outpost]`.

## Boot flow — scene-by-scene

1. Project autoloads `Database`, `Loader`, `Simulation`.
2. `Menu.tscn` loads. `Menu._ready`:
   - `gameData.Reset()` + `gameData.menu = true`.
   - `Loader.ValidateID()` — if invalid → `FormatAll()` + `CreateValidator()`.
   - `Loader.ValidateShelter()` — toggles Load button.
3. **New Game** → `Loader.NewGame(diff, season)` → `LoadScene("Intro" or "Cabin")`.
4. **Load** → `Loader.LoadScene(Loader.ValidateShelter())`.
5. **Tutorial** → `Loader.LoadScene("Tutorial")`.
6. In-game `Transition.Interact()` drives subsequent scene changes.
7. Death → `Loader.LoadScene("Death")`.

## Gotchas

- **Every hardcoded path assumes the `/root/Map/Core/...` layout.** Override authors must respect this — moving `UI` or `Camera` breaks dozens of get_node calls.
- **Shelter vs outdoor isn't just `.tscn` vs `.scn`** — it's `Map.mapType`. Shelters have `mapType = "Shelter"`. Tutorial and Template are special cases (`DecorMode` treats them like shelters).
- **Core.tscn is instanced, not inherited.** If you need different Core behavior per map (e.g. an outdoor-only AI), branch on `mapType` inside the Core scripts rather than forking `Core.tscn`.
- **`Loader.randomScenes = [School, Highway, Outpost]`** is hardcoded. Adding a new outdoor zone as a random destination means patching this array.
- **`Template.scn` is the only non-shelter with decor mode enabled** (`DecorMode.currentMap.mapName == "Template"`). Useful for authoring furniture but not intended as a real playable map.
- **The Menu scene has no `/root/Map`.** Scripts that `get_tree().current_scene.get_node("/root/Map/...")` will crash if called from the menu context. Check `gameData.menu` first.
