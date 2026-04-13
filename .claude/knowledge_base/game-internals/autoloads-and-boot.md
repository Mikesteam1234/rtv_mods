# Autoloads & Boot Flow

Three autoloads run before any scene. Declared in `project.godot`:

```ini
Loader="*res://Resources/Loader.tscn"
Database="*res://Resources/Database.tscn"
Simulation="*res://Resources/Simulation.tscn"
```

All three are scene autoloads (not raw scripts), so their trees are addressable via `$NodeName` from inside. They're accessed by the global name `Loader`, `Database`, `Simulation` from every script.

## Loader (`res://Scripts/Loader.gd`, 1146 lines)

`extends CanvasLayer`. Does scene transitions, save/load, fade animations, cursor control, and the message HUD. It is the single most-referenced script in the codebase.

### Scene tree (`Resources/Loader.tscn`)
```
Loader (CanvasLayer)
├── Screen (Control)
│   ├── Background (TextureRect)
│   ├── Circle (TextureRect) — loading spinner
│   └── Label (Label) — "Loading <scene>..."
├── Overlay (TextureRect)
├── Animation (AnimationPlayer) — "Fade_In", "Fade_Out", "Fade_In_Loading", "Fade_Out_Loading"
└── Messages (VBoxContainer) — in-world notifications
```

### Key members

- `var ID = "Taikuri"` — save validator token. `Loader.gd:10`.
- `scenePath: String` — target scene for the next `LoadScene()`.
- Scene path constants — `Menu`, `Intro`, `Death`, `Tutorial`, `Cabin`, `Attic`, `Classroom`, `Tent`, `Bunker`, `Village`, `School`, `Highway`, `Outpost`, `Minefield`, `Apartments`, `Terminal`, `Template`. Note `.tscn` vs `.scn` split per level.
- `randomScenes = [School, Highway, Outpost]` — pool for `LoadSceneRandom()`.
- `shelters = ["Cabin", "Attic", "Classroom", "Tent", "Bunker"]` — drives the shelter save-file scan.
- `@export var startingKits: Array[LootTable]` — populated in editor; picked at new-game time on difficulty 1.
- `var masterBus / masterAmplify / masterValue / masterActive` — smooths audio master volume during fades via bus effect `AudioServer.get_bus_effect(0, 1)`.

### Core APIs

| Function | Purpose |
|---|---|
| `LoadScene(scene: String)` | Fade in, set `gameData.shelter`/`tutorial`/`permadeath` flags for `scene`, then `change_scene_to_file()` after a 2s timer. Switches on a string name — not the path. |
| `LoadSceneRandom()` | Like above but picks from `randomScenes`. |
| `NewGame(difficulty, season)` | `FormatSave()`, then writes fresh `WorldSave`, `CharacterSave`, `TraderSave`, and initial `Cabin`/`Tent` `ShelterSave` resources. Difficulty 1 seeds a starting kit; difficulty ≠1 randomizes vitals and world time. |
| `ResetCharacter()` | Wipes `CharacterSave` but preserves cat progression. |
| `SaveCharacter()` / `LoadCharacter()` | Serialize inventory, equipment, catalog, vitals, weapon state to `user://Character.tres`. Pull nodes via hardcoded paths: `/root/Map/Core/UI/Interface`, `/root/Map/Core/Camera/Manager`, `/root/Map/Core/Camera/Flashlight`, `/root/Map/Core/UI/NVG`. |
| `SaveWorld()` / `LoadWorld()` | Persist `Simulation.season/time/day/weather/weatherTime` + `gameData.difficulty` to `user://World.tres`. |
| `SaveShelter(target)` / `LoadShelter(target)` | Iterates `get_tree().get_nodes_in_group("Furniture")`, `"Item"`, `"Switch"`; writes/restores positions, rotations, storage, active state to `user://<target>.tres`. On load, all existing furniture is deleted before restoring. |
| `CheckShelterState(target)` | Just a `FileAccess.file_exists` wrapper. |
| `UnlockShelter(target)` | Writes a minimal `ShelterSave` with `initialVisit = true`. |
| `SaveTrader(trader)` / `LoadTrader(trader)` | Mirrors a trader's `tasksCompleted` list to/from `user://Traders.tres`. |
| `SaveTaskNotes(task, add)` / `LoadTaskNotes()` | Manages the player's pinned-task list on `TraderSave.taskNotes`. |
| `UpdateProgression()` | Refreshes day/tasks/shelter-count counters on the `Interface` node. Called on new day, load, and shelter unlock. |
| `Message(text, color)` | Spawns `res://UI/Elements/Message.tscn` under `Messages`. The public in-game notification API. |
| `ValidateID()` / `CreateValidator()` | Checks `user://Validator.tres` against `ID`. Mismatch triggers `FormatAll()` — a full wipe of `user://*.tres`. |
| `ValidateShelter()` | Scans all `*.tres` in `user://` that deserialize to `ShelterSave`, returns the one with the highest `lastVisit` (packed as `day * 10000 + time`). |
| `FormatAll()` / `FormatSave()` | Nuke all `.tres` (former also resets `Preferences.tres`; latter preserves `Validator.tres` + `Preferences.tres`). |
| `FadeIn/Out()`, `FadeInLoading/FadeOutLoading()` | Run the matching `AnimationPlayer` clip + transition sound + cursor capture. |
| `ShowCursor/HideCursor()` | Wraps `Input.set_mouse_mode`. |
| `Quit()` | Fade + `get_tree().quit()`. |

### Hardcoded node paths (override carefully)

Any script that replaces `Loader.gd` must preserve:

- `/root/Map/Core/UI/Interface` — inventory root
- `/root/Map/Core/Camera/Manager` — `RigManager`
- `/root/Map/Core/Camera/Flashlight`
- `/root/Map/Core/UI/NVG`

## Database (`res://Scripts/Database.gd`, 420 lines)

`@tool extends Node`. Giant table of `const <ItemName> = preload("res://Items/.../X.tscn")` entries, one per content type:

- Consumables, Medical, Electronics, Misc, Lore, Keys, Instruments, Books, Clothing, Armor, Ammo, Cartridges, Attachments (all optics + suppressors + magazines), Weapons (every rifle/pistol/SMG + their `_Rig` variants), Knives, Grenades, Backpacks, Helmets, Belts, Fishing, Physics, Furniture.

Scripts look up items by string file name via `Database.get(slotData.itemData.file)` (see `Loader.gd:817`, `Loader.gd:861`). The `file` field on `ItemData` must match the constant name here.

### `@tool` export (editor-only)

```gdscript
@export var master: LootTable     # Target LootTable
@export var update: bool          # Toggle to rebuild
```

When `update = true`, scans all `const` entries whose name does not contain `_Rig` and whose matching `.tres` exists and deserializes to `ItemData`. Appends them to `master.items`. This is how `res://Loot/LT_Master.tres` gets populated.

### Scene tree
```
Database (Node)
```
— that's it. It's only a node so it can be autoloaded and have its preloads live until shutdown.

## Simulation (`res://Scripts/Simulation.gd`, 58 lines)

`extends Node`. In-game clock and weather state machine.

```gdscript
@export var season = 1          # 1 = Summer, 2 = Winter, 3 = Dynamic (assigned at NewGame)
@export var day = 1
@export var simulate = false    # Toggled false on menu, true in-game
@export var time = 1200.0       # 0..2400 (matches GradientTexture1D sampling in World.gd)
@export var rate = 0.2777       # time units per second (so one day ≈ 144 real minutes)
@export var weather = "Neutral"
@export var weatherTime = 600.0 # seconds until next WeatherChange()
```

`_process(delta)` advances `time` by `rate * delta`, rolls over at 2400 (day++, calls `Loader.UpdateProgression()`), decrements `weatherTime`, and triggers `WeatherChange()` when it hits 0.

`WeatherChange()` picks from a weighted pool — `randi_range(0,100)`: 0 = Aurora, 1–10 = Storm, 11–20 = Rain, 21–30 = Overcast, 31–40 = Wind, 41–100 = Neutral. Next rotation is `randf_range(300, 1200)` seconds.

## GameData (`res://Scripts/GameData.gd` / `Resources/GameData.tres`)

`extends Resource, class_name GameData`. Single in-memory instance preloaded by every gameplay script:

```gdscript
var gameData = preload("res://Resources/GameData.tres")
```

Godot returns the same resource handle to every loader, so this is effectively a singleton. Subsystems mutate fields on it, then other systems read those fields in their own `_process`/`_physics_process`. This is the primary inter-system communication channel.

### Field categories (~130 fields total)

- **World:** `zone`, `currentMap`, `previousMap`, `menu`, `shelter`, `tutorial`, `permadeath`, `flycam`, `difficulty`, `season`, `TOD`, `fog`.
- **Vitals:** `health`, `energy`, `hydration`, `mental`, `temperature`, `oxygen`, `bodyStamina`, `armStamina`.
- **Cat progression:** `cat`, `catFound`, `catDead`.
- **Medical conditions (booleans):** `overweight`, `starvation`, `dehydration`, `bleeding`, `fracture`, `burn`, `frostbite`, `insanity`, `poisoning`, `rupture`, `headshot`.
- **Camera/input:** `inputDirection`, `cameraPosition`, `playerPosition`, `playerVector`, `baseFOV`, `aimFOV`, `isScoped`, `headbob`, `lookSensitivity`, `aimSensitivity`, `scopeSensitivity`.
- **UI state:** `settings`, `interface`, `decor`, `magnet`, `mouseMode`, `sprintMode`, `leanMode`, `aimMode`, `musicPreset`, `tooltip`, `interaction`, `transition`, `indicator`.
- **Environment proximity:** `indoor`, `heat`, `PRX_Heat`, `PRX_Workbench`.
- **Weapon state:** `primary`, `secondary`, `knife`, `grenade1`, `grenade2`, `weaponAction`, `weaponPosition`, `inspectPosition`, `firemode`, `jammed`, `PIP`, `secondaryOptic`, `flashlight`, `NVG`.
- **Player action flags:** `freeze`, `vehicle`, `isDead`, `isGrounded`, `isFalling`, `isFlying`, `isWater`, `isSwimming`, `isSubmerged`, `isIdle`, `isMoving`, `isWalking`, `isRunning`, `isCrouching`, `isAiming`, `isCanted`, `isFiring`, `isColliding`, `isReloading`, `isInspecting`, `isInserting`, `isChecking`, `isClearing`, `isDrawing`, `isDragging`, `isBurning`, `isOccupied`, `isCrafting`, `isTrading`, `isTransitioning`, `isCaching`, `isPlacing`, `isSleeping`.
- **Surface/impact:** `surface`, `jump`, `land`, `crouch`, `stand`, `damage`, `impact`.
- **Lean state:** `leanLBlocked`, `leanRBlocked`.

### `Reset()`

Re-initialises everything to defaults. Called by `Menu._ready()` when returning to the main menu. Does **not** persist to disk — `GameData` is never saved; durable state lives in the `*Save` resources (see [save-system.md](save-system.md)).

## Boot flow (high level)

1. Godot loads `project.godot`, instantiates autoloads (`Loader`, `Database`, `Simulation`).
   - `Loader._ready()` initialises the master bus amplify.
   - `Database._ready()` does nothing at runtime (@tool logic only fires in editor).
   - `Simulation` starts with `simulate = false`.
2. Main scene `Menu.tscn` loads.
   - `Menu._ready()` calls `gameData.Reset()`, `gameData.menu = true`, `Simulation.simulate = false`, `Loader.FadeOut()`, `Loader.ValidateID()` → possibly `FormatAll() + CreateValidator()`, then `ValidateShelter()` to enable/disable the Load button.
3. User picks a menu path:
   - **Tutorial:** `Loader.LoadScene("Tutorial")`.
   - **New:** `_on_modes_enter_pressed()` → `Loader.NewGame(difficulty, season)` → either `Loader.LoadScene("Intro")` (with intro on) or `Loader.LoadScene("Cabin")` (difficulty 1) or `Loader.LoadSceneRandom()` (higher difficulty).
   - **Load:** `Loader.LoadScene(Loader.ValidateShelter())`.
4. `Loader.LoadScene` sets `gameData.freeze = true`, `shelter/tutorial/permadeath` flags based on the target name, runs `FadeInLoading` animation + plays the transition sound, waits 2 seconds, then `get_tree().change_scene_to_file(scenePath)`.
5. In the new level, a `Map` (either a shelter `.tscn` or an outdoor `.scn`) is the root. Its child `Core` (instance of `res://Scenes/Core.tscn`) carries everything the player needs; the matching `Map.gd`/`World.gd`-derived script wires up references and calls `Loader.LoadCharacter()`/`LoadShelter()`/`LoadTrader()` as appropriate. Transitions between levels go through `Transition.gd` which calls `Loader.SaveCharacter()`, `Loader.SaveWorld()`, and conditionally `Loader.SaveShelter()` before the next `LoadScene`.
