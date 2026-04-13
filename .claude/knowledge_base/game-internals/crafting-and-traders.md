# Crafting & Traders

Both systems live inside `Interface` (the inventory UI). Traders are physical world NPCs with their own supply pool + task list; crafting is a resource-driven recipe catalog with proximity requirements (heat, workbench, shelter).

## Traders

### `TraderData` (`TraderData.gd`)
```gdscript
extends Resource
class_name TraderData

@export var icon: Texture2D
@export var name: String              # "Generalist" / "Doctor" / "Gunsmith" / "Grandma"
@export var resupply = 10.0           # minutes between supply rerolls
@export var tax = 100.0               # percent markup
@export var tasks: Array[TaskData]

@export_group("Voices")
@export var randomVoices: AudioEvent
@export var startVoices: AudioEvent
@export var endVoices: AudioEvent
@export var tradeVoices: AudioEvent
@export var taskVoices: AudioEvent
```

One `.tres` per trader, stored under `res://Traders/`. Referenced by the in-world `Trader` node and by trader task panels in `Interface`.

### `Trader` (`Trader.gd`, class_name Trader)

`extends Node3D`. The physical NPC at the trader's post. In group `"Trader"` — `EventSystem.ActivateTrader/DeactivateTrader` find them by group.

#### Exports
- `traderData: TraderData`, `skeleton: Skeleton3D`, `animations: AnimationPlayer`, `timer: Timer`, `display: Node3D`.
- Debug: `force: bool` — start Activated regardless of events.

#### Runtime state
- `tasksCompleted: Array[String]` — task name strings (matches `TraderSave.<trader>`).
- `supply: Array[SlotData]` — the rolled stock currently for sale.
- `traderBucket: Array[ItemData]` — filtered pool from `LT_Master` items where `item.generalist/doctor/gunsmith` flag matches.
- `shelterUnlocked = false`, `tax = 100.0`.

#### `_ready()`
1. Starts resupply `Timer` at `traderData.resupply * 60` seconds.
2. Small random delay, plays `"Trader_Idle"` animation.
3. Switches animation + skeleton to **manual process** mode (`MODIFIER_CALLBACK_MODE_PROCESS_MANUAL`) — `Animate(delta)` drives them at a throttled rate.
4. `FillTraderBucket()` — scans `LT_Master.items`, appends each whose `generalist/doctor/gunsmith` flag matches `traderData.name`.
5. `CreateSupply()` — rolls 40 `SlotData`s picked randomly from `traderBucket`, applying `defaultAmount` for non-magazine stackables.
6. `Deactivate()` unless `force`.

#### `Activate()` / `Deactivate()`
Flips `process_mode` and visibility. `EventSystem`'s trader-event functions drive these for daily availability.

#### `Animate(delta)` LOD
Distance-scaled animation tick rate:
- `>50m` → 1Hz
- `>25m` → 15Hz
- `≤25m` → 60Hz

Manually advances `animations` + `skeleton` each tick. Saves a huge amount of skeleton work when the trader is off-screen.

#### `SupplyTimer()`
Per-frame: while trading, writes `interface.traderResupply.text` as `MM:SS` countdown. When the timer expires:
- `CreateSupply()` — reroll stock.
- If currently trading: `interface.Resupply()` + `PlayTraderReset()` sound.
- Restart the timer.

#### `Interact()`
`UIManager.OpenTrader(self)`. Sets `gameData.isTrading = true` and wires the trader's supply into the interface trader panel.

#### Trades
The player → trader flow is driven by `Interface` (see `StartInput / Trade` methods). On a successful trade:
- Consumed slot is removed from `inventoryGrid`.
- `trader.RemoveFromSupply(itemData)` deletes the first matching supply entry.
- `PlayTraderTrade()` sound + voice.

#### `CompleteTask(taskData: TaskData)`
Called by `Interface.Complete` on successful task delivery:
- Appends `taskData.name` to `tasksCompleted`.
- `PlayTraderTask()` (sound + voice).
- `Loader.Message("Task Completed: <name>", GREEN)`.
- Non-tutorial: `Loader.SaveTrader(traderData.name)` + `Loader.UpdateProgression()`.

#### `Voices(delta)`
At `voiceCycle` intervals (starts 60s, reroll 30–60s), if no active voice AND player within 20m → `PlayTraderRandom()`.

Voice plays are guarded by `is_instance_valid(activeVoice)` so they don't stack. `activeVoice` is assigned to the `AudioInstance3D` node; when it queue_frees itself, the guard opens again.

Voice playback types (all follow the same `AudioInstance3D` pattern at `(0, 1.7, 0)` with `unit_size=10, max_distance=100`):
- `PlayTraderStart` — fires `UITraderOpen` + `startVoices`.
- `PlayTraderEnd` — fires `UITraderClose` + `endVoices`.
- `PlayTraderReset` — just `UITraderReset` sound.
- `PlayTraderRandom` — just `randomVoices`.
- `PlayTraderTrade` — `UITraderTrade` + `tradeVoices`.
- `PlayTraderTask` — `UITraderTask` + `taskVoices`.

### `TraderDisplay` (`TraderDisplay.gd`)
5-line helper for the counter display — freezes and disables collision on any child `Pickup`, locks any child `LootContainer`. Lets the trader's physical item spread be decorative/untouchable.

### Trader save/load
See save-system.md. `Loader.SaveTrader("Generalist"/...)` serializes `tasksCompleted` into the matching `TraderSave` field. `Loader.LoadTrader` reverses it and calls `interface.UpdateTraderInfo()`.

## Crafting

### `Recipes` catalog (`Recipes.gd`)
```gdscript
extends Resource
class_name Recipes
@export var consumables / medical / equipment / weapons / electronics / misc / furniture: Array[RecipeData]
```
Canonical instance at `res://Crafting/Recipes.tres` — `Interface` iterates these to populate the crafting panel tabs.

### `RecipeData` (`RecipeData.gd`)
```gdscript
extends Resource
class_name RecipeData

@export var name: String
@export var time: float           # seconds to craft
@export var audio: AudioEvent     # looped during craft
@export var input:  Array[ItemData]
@export var output: Array[ItemData]
@export var repair  = false       # repair path — output is input-at-100%
@export var upgrade = false       # input grid shows filled (keeps existing instance)

@export_group("Proximity")
@export var heat: bool
@export var workbench: bool
@export var testbench: bool
@export var shelter: bool
```

Proximity flags gate the Start Input button. `gameData.heat/PRX_Heat/PRX_Workbench/shelter` are written by `Detector.gd` (heat/workbench) and by shelter area detection.

### `Recipe` UI (`Recipe.gd`)

`extends PanelContainer`. One row per recipe inside the crafting panel.

#### `Initialize(recipe, interface)`
- Fills title, `MM:SS` time label, proximity icons.
- Completion button text: "Repair" if `recipe.repair`, else "Craft".
- Populates `inputGrid` with one display-only `Item` per `input` entry. If `recipe.upgrade` → pass `filled = false` (Display mode shows the real item context); else `filled = true` (silhouette).
- Populates `outputGrid`. For repair recipes, the output string appends `" [100%]"`.

#### Input flow (driven by `Interface`)
Same pattern as Task: Start Input → selects matching slots from inventory via `CanInput`/`AddInputItem`/`RemoveInputItem`. When all slots are filled (`CanComplete()`), the Craft button enables. Clicking Craft → `interface.Craft(recipeData)`, which:
1. Consumes inputs.
2. Starts a craft timer for `recipe.time`, during which `recipe.audio` loops.
3. On completion, spawns `output` items into the inventory (or restores the input item at 100% condition for repair recipes).

#### `UpdateProximity()`
Called each frame while the crafting panel is open. Reads `gameData.heat / PRX_Heat / PRX_Workbench / shelter` and greens/grays the proximity icons. Blocks the Input button with a label like `"Heat required"` / `"Workbench required"` / `"Shelter required"` when missing.

Note: `testbench` is authored in data but the gating branch isn't present in `UpdateProximity()`'s code — only Heat, Workbench, and Shelter actually lock the button. Testbench stays visual-only unless you add the matching branch.

#### States
- `Default` — closed, button says "Start Input".
- `Selected` — Input toggled on, button says "Stop Input", highlight white.
- `Active` — crafting in progress, all buttons disabled, highlight green.
- `Collapse / Expand` — content body toggle.

## Crafting-vs-trader vs task flow comparison

All three use the same `inputGrid` / `outputGrid` + `Interface.StartInput / AddInputItem / RemoveInputItem / ResetInput` plumbing. The diff:

| | Trader trade | Task delivery | Crafting |
|---|---|---|---|
| Input source | `trader.supply[]` | `taskData.deliver[]` | `recipe.input[]` |
| Output | Moves supply item into inventory, deducts currency | `taskData.receive[]` items spawn in inventory | `recipe.output[]` items spawn (or repaired input) |
| Proximity gate | none | "Furniture" hint if receive has furniture | heat/workbench/shelter flags |
| Time | instant | instant | `recipe.time` seconds with audio loop |
| Save | supply isn't saved; per-trader task strings are (`TraderSave`) | task name string → `TraderSave.<trader>` | none (one-shot) |

## Gotchas

- **`traderBucket` is filtered by `ItemData.generalist/doctor/gunsmith` booleans.** Grandma has no corresponding flag — she doesn't get a rolled supply (tasks only). If you add a new trader, add the flag to `ItemData` and a branch in `FillTraderBucket()`.
- **Supply size is hardcoded to 40.** `for index in 40` in `CreateSupply()`.
- **`tax = 100.0`** on both `TraderData` and the runtime `Trader.tax` is a percent — the trade price math lives in `Interface`, not here.
- **Animation manual-mode** (`MODIFIER_CALLBACK_MODE_PROCESS_MANUAL`) means the trader won't animate at all without `Animate(delta)` running. If you override `_physics_process`, call through to super or animations freeze.
- **`CompleteTask` appends the task NAME** (`taskData.name`) as the completion key. Two tasks with the same name collide — names must be unique per trader.
- **`Recipe.UpdateProximity()` has no `testbench` branch.** The icon shows based on `recipeData.testbench` but the button isn't gated. Watch for this if authoring testbench recipes.
- **`gameData.isTrading`** is the switch that makes `SupplyTimer()` write the countdown label. Don't flip it manually — use `UIManager.OpenTrader/Return`.
- **`Voices` activeVoice guard is by `is_instance_valid`.** Voices stop layering because the `AudioInstance3D` self-frees. If you pool-reuse audio instances in a mod, the guard never opens → trader goes silent.
