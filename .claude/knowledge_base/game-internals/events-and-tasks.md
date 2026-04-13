# Events & Tasks

Two separate resource-driven systems that happen to share a UI panel under `Interface`.

- **Events** — timed world-state triggers (jets flying over, airdrops, Police/BTR patrols, helicopter encounters, the Cat rescue). Managed by `EventSystem`.
- **Tasks** — trader-issued delivery jobs (hand over items → receive items). Managed by `Interface` + trader data.

## Event resources

### `EventData` (`EventData.gd`)
```gdscript
extends Resource
class_name EventData

@export var day: int           # earliest Simulation.day on which this event is eligible
@export var name: String
@export var type: String       # "Dynamic" / "Trader" / "Special"
@export var map: String        # "" = any; otherwise must match Map.mapName
@export var zone: String       # "" = any; otherwise must match Map.mapType
@export var function: String   # name of a method on EventSystem to invoke
@export_multiline var description: String

@export_group("Dynamic Rules")
@export var instant = false
@export var possibility: int   # 0..100 roll; 0 = guaranteed
```

### `Events` (`Events.gd`)
```gdscript
extends Resource
class_name Events
@export var events: Array[EventData]
```
Canonical catalog at `res://Events/Events.tres` — preloaded by `EventSystem`.

## EventSystem (`EventSystem.gd`)

`extends Node3D`. Present in outdoor maps. Scene children:
```
EventSystem
├── Paths          — waypoint chains for Police / BTR (used as randomPath)
└── Crashes        — candidate spawn points for the Helicopter crash site
```

### Boot sequence
`_ready()` awaits 5s (so the map/nav is ready), then:
1. `GetAvailableEvents()` — filters `events.events` by `day <= Simulation.day`, optional `map`, optional `zone`. Bins by `type` into `dynamicEvents / traderEvents / specialEvents`.
2. `ActivateDynamicEvent()` — picks **one** random dynamic event, rolls `randi_range(0,100) < possibility`. If hit:
   - `instant = true` → calls `event.function` immediately via `Callable(self, name)`.
   - `instant = false` → awaits `randi_range(0, 300)` seconds, then calls.
3. `ActivateTraderEvent()` — calls **every** matching trader event's function (no roll). These toggle trader availability for the day.
4. `ActivateSpecialEvent()` — calls every matching special event's function (no roll). Used for gated story triggers.

### Built-in event functions (named in `EventData.function`)

| Function | What it spawns |
|---|---|
| `FighterJet()` | `Fighter_Jet.tscn` overflight. |
| `Airdrop()` | `CASA.tscn` dropping a supply crate. |
| `Police()` | `Police.tscn` patrol; picks a random child of `Paths`, random direction (`inversePath`), spawns at the path endpoint. |
| `Helicopter()` | `Helicopter.tscn` — flyby / attack. |
| `CrashSite()` | `Helicopter_Crash.tscn` parented to a random child of `Crashes`. |
| `BTR()` | Same pattern as Police. |
| `ActivateTrader()` / `DeactivateTrader()` | Iterates group `"Trader"` and calls `Activate()/Deactivate()`. |
| `Cat()` | Short-circuits on `catFound || catDead`. Picks a random group-`"Well"` node, spawns `Cat.tscn` at its `Bottom` child in `Rescue` state, and a `Rescue.tscn` prompt 3m above. |
| `Transmission()` | Iterates group `"Radio"` and calls `Transmission()` on each, flipping the next playback to the transmission clip pool (see audio-system.md). |

Adding a new event function means declaring it on `EventSystem` and referencing its name (string) in the EventData. Typo in `function` fails silently — `Callable.call()` just errors at runtime.

## Event UI panel (`Event.gd`)

`extends PanelContainer`. One row per available event inside the Interface's Events panel.

`Initialize(event: EventData, interface)`:
- Fills `day`, `title`, `type`, `description`, `location` ("All maps & zones" / map / zone), `possibility` ("Guaranteed" if 0, else `~N%  / map instance`).
- If `Simulation.day >= event.day` → `Active()` (green). Else → `Default()` with "In N Days" countdown.
- Toggleable `Show/Hide` content body; plays `UIClick`.

## Task resources

### `TaskData` (`TaskData.gd`)
```gdscript
extends Resource
class_name TaskData

@export var trader: String     # "Generalist" / "Doctor" / "Gunsmith" / "Grandma"
@export var name: String
@export var difficulty: String # "Easy" / "Intermediate" / "Hard"
@export_multiline var description: String
@export var deliver: Array[ItemData]
@export var receive: Array[ItemData]
```

Lives in trader `.tres` resources — see crafting-and-traders.md.

### Persistence
Completed tasks are stored as **name strings** in `TraderSave` (`generalist / doctor / gunsmith / grandma: Array[String]`). Pinned notes are stored as `Array[TaskData]` (resource references). See save-system.md.

## Task UI (`Task.gd`)

`extends PanelContainer`. Row inside the trader task panel. States: `Default / Selected / Locked / Completed / Note`.

### `Initialize(task, interface)`
- Sets title, difficulty (color-coded: green/orange/red), description, input/output strings.
- Shows a "hint" label if any `receive` item has `type == "Furniture"` (tells player to drop it rather than stash it).
- Populates `inputGrid` with one display-only `Item` per entry in `deliver` (amount = `defaultAmount` except for magazines), and `outputGrid` likewise for `receive`.

### `InitializeNote(task, interface)` — compact variant
Used in the Notes panel. Replaces the difficulty label with the trader name, hides description/buttons.

### Delivery flow (driver = `Interface`)
1. User clicks **Start Delivery** → `Task._on_input_toggled(true)` → `interface.StartInput(task)`.
2. Inventory items that match `deliver` entries become eligible. `Task.CanInput(slotData)` tests name + amount ≥ required.
3. `AddInputItem(slotData)` marks the matching `inputGrid` child as selected; `CanComplete()` enables the Complete button once all inputs are selected.
4. User clicks **Complete** → `Completed()` → `interface.Complete(taskData)`. Interface consumes the delivered items, spawns the `receive` items into inventory, appends `taskData.name` to the trader's completed-task array, and calls `Loader.SaveTrader(trader)`.
5. Canceling runs `ResetInput()` which flips selected children back to `"Display"` state.

### Notes
- **Add to Notes** → `Loader.SaveTaskNotes(taskData, true)` + `interface.InitializeNotes()` to refresh.
- **Remove** → `Loader.SaveTaskNotes(taskData, false)` + refresh.
- `UpdateNoteButtons()` handles button text/disable based on `note / noted / completed` flags.

## Condition (`Condition.gd`)

Not part of events — it's the HUD medical indicator widget. One per medical flag.

`extends Control` with `enum Type { Overweight, Starvation, Dehydration, Bleeding, Fracture, Burn, Frostbite, Insanity, Poisoning, Rupture, Headshot }`.

`_physics_process` at 10Hz: reads `gameData.<flag>` and sets `modulate` to red (active) or faded white (inactive). Dumb display — doesn't drive state.

## Detector (`Detector.gd`)

`extends Area3D`. Lives on the player under `Core/Detector`. The single Area-overlap → gameData flag pipeline.

`_physics_process(delta)`:
- Early-outs on `isCaching`.
- `Indoor(delta)` — drives the global shader uniform `"Indoor"` (0→1 lerp) used by muffle / postfx.
- At `sensorCycle = 0.2`s, calls `Detect()`.

`Detect()` scans `get_overlapping_areas()`; every overlap that is an `Area` (class_name on `Area.gd`) sets flags based on its `type` string:

| `Area.type` | Effect |
|---|---|
| `"Indoor"` | `gameData.indoor = true` |
| `"Mine"` | If `!overlap.owner.isDetonated` → `owner.Detonate()`. |
| `"Fire"` | `isBurning = true`; if not already burned, `character.Burn(true)`. |
| `"Heat"` | `gameData.heat = true` (temperature regen source). |
| `"PRX_Heat"` | `gameData.PRX_Heat = true` (proximity to heat source, e.g. recipe requirement). |
| `"PRX_Workbench"` | `gameData.PRX_Workbench = true` (workbench-adjacent recipes). |

With no overlaps, every flag above is cleared. This is the source of truth for "am I inside" — world code reads `gameData.indoor`, not raycasts.

## Gotchas

- **`EventData.function` is a string.** `Callable(EventSystem, name).call()` fails silently if the name is wrong. Grep `EventSystem.gd` for the list of valid names before authoring a new EventData.
- **One dynamic event per map load.** `ActivateDynamicEvent` picks a single random one and rolls it. Multiple dynamic events in the available pool means only one has a chance to fire per entry.
- **Trader + Special events always fire** when eligible (no possibility roll). `possibility` is only consulted for the Dynamic path.
- **`EventSystem._ready()` waits 5s** before doing anything. Don't trust events to be live immediately after a scene load.
- **`Cat()` hard-exits on `catFound || catDead`.** Re-triggering the Cat event after rescue requires clearing those flags via a save edit or a new run.
- **Task persistence mixes types:** completed task IDs are strings (trader arrays), but pinned notes are resource refs (`taskNotes: Array[TaskData]`). Don't try to unify them.
- **`Detector` is the ONLY writer of `gameData.indoor / isBurning / heat / PRX_*`.** If you need to force one of those states (e.g. cutscene), write a custom area; don't poke gameData directly — `Detector` will overwrite within 200ms.
- **`Condition` only reads gameData** — adding a new medical flag needs both a gameData field and a new enum member here.
