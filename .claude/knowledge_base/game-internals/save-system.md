# Save System

All persistence is Godot `Resource` files written to `user://` via `ResourceSaver.save(resource, path)` and read with `load(path) as Type`. There is no custom serializer, no JSON, no versioning layer. The `Loader` autoload is the single entry point.

## `user://` layout

```
user://
├── Validator.tres      # integrity stamp (ID = "Taikuri")
├── Preferences.tres    # settings — survives FormatSave
├── Character.tres      # player vitals + inventory + equipment + catalog
├── World.tres          # difficulty, season, day, time, weather
├── Traders.tres        # per-trader completed task strings + task notes
├── Cabin.tres          # one ShelterSave per shelter
├── Attic.tres
├── Classroom.tres
├── Tent.tres
└── Bunker.tres
```

Shelter file basename must match the `shelters` const in `Loader.gd`: `["Cabin", "Attic", "Classroom", "Tent", "Bunker"]`.

## Save resource schemas

### `Validator` (`Validator.gd`)
```gdscript
@export var warning = "WARNING: Do not touch this..."
@export var ID: String     # matched against Loader.ID = "Taikuri"
```
A save-format version stamp. Change `Loader.ID` and every existing save is wiped by `ValidateID()` → `FormatAll()`.

### `Preferences` (`Preferences.gd`, class_name Preferences)
All settings: audio volumes, music preset, FOV, headbob, sensitivities, color grading, HUD toggles, render quality, display mode, input rebinds (`actionEvents: Dictionary`), casette volume, etc.

Static API:
```gdscript
func Save():                                  # instance method
    ResourceSaver.save(self, "user://Preferences.tres")

static func Load() -> Preferences:
    var p = load("user://Preferences.tres") as Preferences
    if !p: p = Preferences.new()
    return p
```

Survives `FormatSave()`. Wiped by `FormatAll()` (which creates a fresh default).

### `CharacterSave` (`CharacterSave.gd`)
- **Vitals:** `health / energy / hydration / temperature / mental` (all default 100).
- **Pet:** `cat = 100`, `catFound`, `catDead`.
- **Stamina:** `bodyStamina`, `armStamina`.
- **Medical flags:** `overweight / starvation / dehydration / bleeding / fracture / burn / frostbite / insanity / rupture / headshot`.
- **New-run state:** `initialSpawn: bool`, `startingKit: LootTable` — consumed by `LoadCharacter()` on first load after `NewGame`.
- **Inventory:** `inventory / equipment / catalog: Array[SlotData]`.
- **Weapon carry flags:** `primary / secondary / knife / grenade1 / grenade2 / flashlight / NVG` + `weaponPosition`.

### `WorldSave` (`WorldSave.gd`)
```
difficulty = 1     # 1 Standard / 2 Darkness / 3 Ironman
season = 1         # 1 Summer / 2 Winter (2 triggers winter code paths)
day = 1
time = 1200        # 0..2400
weather = "Neutral"
weatherTime = 600.0
shelters = 0
```

### `ShelterSave` (`ShelterSave.gd`)
```
initialVisit = false   # true = stub, shelter never entered yet
lastVisit: int         # (day * 10000) + time — picked by ValidateShelter() to find most recent
furnitures: Array[FurnitureSave]
items:      Array[ItemSave]
switches:   Array[SwitchSave]
```

### `FurnitureSave` (`FurnitureSave.gd`)
```
name, container, position, rotation, scale
itemData: ItemData
storage:  Array[SlotData]   # if the furniture is a LootContainer
gridPosition: Vector2
gridRotated: bool
```

### `ItemSave` (`ItemSave.gd`)
```
name
slotData: SlotData
position: Vector3
rotation: Vector3
```

### `SwitchSave` (`SwitchSave.gd`)
```
name: String
active: bool
```

### `ContainerSave` (`ContainerSave.gd`)
```
name: String
storage: Array[SlotData]
```
Used by world/outdoor containers that persist between visits (loot table containers roll fresh on each entry; storaged containers use this).

### `TraderSave` (`TraderSave.gd`)
```
generalist / doctor / gunsmith / grandma: Array[String]   # completed task IDs
taskNotes: Array[TaskData]                                 # pinned notes in UI
```

## Loader API (save/load)

Everything lives in `Loader.gd` (autoload at `/root/Loader`).

### Validator
| Method | Purpose |
|---|---|
| `CreateValidator()` | Writes `user://Validator.tres` with `ID = "Taikuri"`. |
| `ValidateID() -> bool` | True if Validator exists and ID matches. Called by `Menu._ready()`. |
| `ValidateShelter() -> String` | Scans `user://` for any `ShelterSave` and returns the basename of the one with the newest `lastVisit`. Empty string if none exist (disables Load button). |

### Format
| Method | Scope |
|---|---|
| `FormatAll()` | Deletes **every** `.tres` under `user://`, then writes a fresh `Preferences.tres`. |
| `FormatSave()` | Deletes every `.tres` **except** `Validator.tres` and `Preferences.tres`. Called by `NewGame()` and by permadeath. |

### New game
`NewGame(difficulty, season)`:
1. `FormatSave()`.
2. Writes a `WorldSave` (difficulty 1 → `time = 800, weather = "Neutral"`; otherwise randomized).
3. Writes a `CharacterSave` (difficulty 1 → `initialSpawn = true` + random `startingKit` from `startingKits: Array[LootTable]`; otherwise randomized vitals in `[25..100]`).
4. Writes empty `Traders.tres`.
5. Writes stub `Cabin.tres` and `Tent.tres` with `initialVisit = true` (both unlocked from the start).

`ResetCharacter()` — rarely-used: wipes the character but preserves cat state.

### Character
- `SaveCharacter()` — reads from `gameData` + Interface (`inventoryGrid`, `equipment`, `catalogGrid`) to rebuild a `CharacterSave`. Per-slot logic: grid items call `SlotData.GridSave(pos, rotated)`; equipment calls `SlotData.SlotSave(slotName)`; catalog items additionally copy `storage`.
- `LoadCharacter()` — awaits 0.1s, then restores. If `initialSpawn && startingKit`, auto-creates each item in inventory. Replays `interface.LoadGridItem / LoadSlotItem`, then restores weapon-carry flags and calls `rigManager.LoadPrimary/Secondary/Knife/Grenade1/Grenade2`, `flashlight.Load()`, `NVG.Load()`. Finishes with `UpdateProgression()`.

### World
- `SaveWorld()` — pulls from `Simulation` autoload (`season/time/day/weather/weatherTime`) + `gameData.difficulty`.
- `LoadWorld()` — writes back into `Simulation`. **Permadeath latch:** if `world.difficulty == 3 && !gameData.tutorial` → sets `gameData.permadeath = true`.

### Shelter
- `SaveShelter(targetShelter)` — scans groups `"Furniture"`, `"Item"`, `"Switch"` under the scene, packs each into its save struct, writes to `user://<targetShelter>.tres`. `lastVisit = day*10000 + time`. Skips items with non-finite transforms or `y < -10` (fell through floor).
- `LoadShelter(targetShelter)` — awaits 0.1s. If `initialVisit` is true, calls `UpdateProgression()` and exits (no furniture to load). Otherwise deletes all current `Furniture` group nodes (by y=-100 + queue_free), then recreates furniture via `Database.get(itemData.file).instantiate()`, re-pickups each item, re-toggles switches.
- `UnlockShelter(targetShelter)` — writes a stub `ShelterSave` with `initialVisit = true`. Called by `Transition.CheckKey()` when the player unlocks a shelter.
- `CheckShelterState(name) -> bool` — file-exists check.

### Trader
- `SaveTrader(trader)` — trader is `"Generalist"/"Doctor"/"Gunsmith"/"Grandma"`. Clears that trader's string array, appends all `interface.trader.tasksCompleted`.
- `LoadTrader(trader)` — populates `interface.trader.tasksCompleted` from the named array, then `UpdateTraderInfo()`.
- `SaveTaskNotes(task: TaskData, add: bool)` / `LoadTaskNotes() -> Array[TaskData]` — pinned-notes layer. `add = true` appends (dedup), `false` erases.

### Progression
`UpdateProgression()`:
- No-op in tutorial.
- Writes `interface.day.text` (Simulation.day), `interface.tasks.text` (sum of all four trader task-string arrays), `interface.shelters.text` (count of `.tres` files whose basename is in the `shelters` const).

Called at the tail of `LoadCharacter()`, `LoadShelter()` (when initialVisit), `UnlockShelter()`, and by `Transition.UpdateSimulation()` on day rollover.

## Boot flow

On `Menu._ready()`:
1. `ValidateID()` — if false, `FormatAll()` + `CreateValidator()` + flash the Tutorial button green (first-run cue).
2. `ValidateShelter()` — non-empty enables the Load button.

On `LoadScene(...)` for an outdoor/shelter map:
- `LoadCharacter()` runs after the new scene's nodes are ready (via the 0.1s timer).
- `LoadWorld()` restores Simulation.
- If shelter: `LoadShelter(mapName)` restores furniture/items/switches.
- `LoadTrader(...)` is called per-trader when their UI panel opens.

On `Transition.Interact()` for an inter-map move:
- `UpdateSimulation()` advances the clock.
- `Loader.LoadScene(nextMap)` → `Loader.SaveCharacter()` + `Loader.SaveWorld()`.
- If `shelterExit`: also `Loader.SaveShelter(currentMap)`.

On death (see player-system.md `Character.Death()`):
- Non-permadeath → `SaveShelter` of the last shelter, `ResetCharacter()`, `LoadScene("Death")`.
- Permadeath → `FormatSave()` before going to Death screen (all saves wiped).

## Gotchas

- **`Loader.ID = "Taikuri"`** is the save-format version. Any code change that breaks save compat should bump this so `ValidateID()` forces `FormatAll()`.
- **`FormatSave` vs `FormatAll`:** `FormatSave` preserves Validator + Preferences; `FormatAll` nukes both and re-creates Preferences. Don't confuse them — `FormatAll` is a factory reset.
- **Shelter basename convention:** `Loader.shelters` lists the valid names. A new shelter added to the map must be added here too or `UpdateProgression()` won't count it.
- **`lastVisit = day*10000 + time`** is a single monotone integer used to pick the most-recent shelter. If `time` ever exceeds 9999 this breaks — current max is 2400.
- **Save async:** `LoadCharacter`, `LoadShelter`, `LoadTrader` all `await get_tree().create_timer(0.1).timeout` before touching nodes. If you call them synchronously from an override, you'll race the scene's `_ready()`.
- **`initialSpawn`/`startingKit` are one-shot.** `SaveCharacter` immediately sets them to `false`/`null` so the kit is never re-granted.
- **Permadeath latch:** `LoadWorld()` sets `gameData.permadeath = true` *only* if `difficulty == 3 && !gameData.tutorial`. If you add a new difficulty mode, replicate the latch.
- **Items dropped below y=-10** are silently discarded at save time. Design `SaveShelter` overrides accordingly — don't rely on items at low Y being persisted.
- **Furniture lookup is by `itemData.file`** through the `Database` autoload. If you mod in new furniture, register the scene path in `Database` or it will silently fail to rehydrate from save.
- **Per-trader task arrays are String arrays** (task ID strings), but `taskNotes` is `Array[TaskData]` (resource references). Don't mix the two.
