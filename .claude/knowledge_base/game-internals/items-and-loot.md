# Items & Loot

Every tradeable/usable thing in the game is an `ItemData` resource. UI representation is the `Item` panel. Storage is a `Grid` of `Item`s indexed by `SlotData`. Random generation goes through `LootTable` + `LootContainer`. World pickups are `Pickup` rigid bodies.

## ItemData (`ItemData.gd`)

`extends Resource, class_name ItemData`. The base type for every item. Subclasses: `WeaponData`, `AttachmentData`, `KnifeData`, `GrenadeData`, `FishingData`, `InstrumentData`, `CasetteData`.

### Fields by group

- **Naming:** `file` (must match `Database` const name — see autoloads doc), `name`, `inventory`, `rotated`, `equipment`, `display` — all string labels shown in different UI contexts.
- **Stats:** `type` (`"Weapon"`, `"Armor"`, `"Helmet"`, `"Rig"`, `"Ammo"`, `"Electronics"`, `"Furniture"`, ...), `subtype` (`"Magazine"`, `"Optic"`, `"Muzzle"`, `"Light"`, `"NVG"`, `"Casette"`, ...), `weight`, `value`, `rarity` (`Common`/`Rare`/`Legendary`/`Null`). `Null` excludes from loot generation.
- **Icons:** `icon: Texture2D` (inventory icon), `tetris: PackedScene` (in-grid sprite scene), `size: Vector2` (grid cells).
- **Scaling:** 7 (scale, offset) pairs for the in-grid sprite when the weapon has magazine, optic, suppressor, or combinations. Applied by `Item.UpdateSprite()`.
- **Use:** `usable`, `phrase` (verb for the context menu), `audio: AudioEvent`, `used: Array[ItemData]` (replacement after use).
- **Vitals:** `health`, `energy`, `hydration`, `mental`, `temperature` — deltas applied when used.
- **Medical:** cure flags `bleeding`, `fracture`, `burn`, `insanity`, `rupture`, `headshot`.
- **Combine:** `compatible: Array[ItemData]` — what can be nested into this (magazines → ammo, weapons → attachments, rigs → armor plates).
- **Equipment:** `slots: Array[String]` (which equipment slots accept it), `material: Material`, `capacity` (storage size if it's a container), `insulation` (winter temp bonus).
- **Details:** `showCondition`, `showAmount`, `defaultAmount`, `maxAmount`, `stackable`, `freezable`.
- **Electronic:** `power: {None, Low, Medium, High}`, `color: Color`.
- **Armor:** `plate`, `carrier`, `helmet`, `protection: int`, `rating: String` (e.g. "IV", "VI").
- **Crafting:** `tool`, `repairs`, `returns` — recipe-return flags.
- **Loot Tables / Types:** `civilian`, `industrial`, `military` — which container types this appears in.
- **Loot Tables / Traders:** `generalist`, `doctor`, `gunsmith`, `grandma`.
- **Placement:** `orientation`, `wallOffset` — for the Placer.

### Subclasses

- `WeaponData` — see weapons-and-combat.md.
- `AttachmentData` — `scope`, `variable`, `secondary`, `hasMount`, `reticleSize`, `reticleSizeP` + the optic parameters.
- `KnifeData` — melee damage + audio.
- `GrenadeData` — explosion radius/damage/fuse.
- `FishingData` — rod stats.
- `InstrumentData` — playable instrument params.
- `CasetteData` — track playlist + battery drain for the casette player.

## SlotData (`SlotData.gd`)

`extends Resource, class_name SlotData`. The **runtime instance** of an item — what an `ItemData` becomes when it's in someone's inventory.

```gdscript
@export var itemData: ItemData             # the definition
@export var nested: Array[ItemData]        # attached accessories (mag, optic, suppressor, plate)
@export var storage: Array[SlotData]       # contents if this is a container (rig, backpack, furniture)
@export var condition = 100                # durability %
@export var amount = 0                     # ammo count / stack size / battery
@export var position = 0                   # optic rail position (float)
@export var mode = 1                       # firemode index
@export var zoom = 1                       # variable-optic zoom
@export var chamber: bool                  # weapon: round in chamber
@export var casing: bool                   # weapon: spent casing still in chamber
@export var state: String                  # "", "Jammed", "Frozen"

@export var gridPosition: Vector2          # saved grid cell
@export var gridRotated = false            # saved rotation
@export var slot: String                   # saved equipment slot name
```

Methods:
- `Update(other)` — deep-copies another SlotData (duplicates `nested` and `storage` arrays).
- `Reset()` — clears to defaults.
- `GridSave(position, rotated)` / `SlotSave(name)` — persistence helpers called by Loader save path.

## Item (`Item.gd`, ~900 lines)

`extends Panel, class_name Item`. The UI element. One per item in a grid or equipment slot. Script at `res://UI/Elements/Item.tscn`.

### Children
`Fill`, `Icon`, `Details` (`Abbreviation`, `Condition`, `Amount`, `Frost`, `Error`), `Details/Symbols` (`Modded`, `Furniture`, `Returns`, `Malfunction`, `Frozen`).

### Key members

- `slotData: SlotData` — the bound data.
- `sprite: Sprite2D` — instanced from `slotData.itemData.tetris`.
- `equipSlot`, `equipped`, `rotated`, `optic`, `magazine`, `suppressor`, `selected` — state flags. The three attachment flags are recomputed in `UpdateAttachments()` by scanning `slotData.nested` for subtypes `"Optic"`, `"Magazine"`, `"Muzzle"`.

### Core methods

| Method | Purpose |
|---|---|
| `Initialize(source, data)` | Wires the Item into an interface + applies `SlotData`. Instances the tetris sprite, runs `UpdateDetails/Attachments/Sprite`. |
| `Display(source, data, showReturns)` | Trader-panel variant (grid-less display). Uses `icon` + `abbreviation`, hides condition/amount unless amount is meaningful. |
| `Remove(nestedIndex)` | Detach an attachment. Magazine detach zeroes `amount`; optic detach zeroes `position`. |
| `Combine(itemDragged)` | Attach an item. Magazine into weapon transfers rounds (respecting `chamber`). Armor into rig transfers `condition`. |
| `CombineSwap(itemDragged)` | Replaces the matching nested slot and returns the old one. Handles optic-subtype match, rig-armor match, casette-casette match. |
| `UpdateSprite()` | Re-scales/re-positions the sprite based on which attachments are present. 7-way branch picks scale+offset fields from ItemData. |
| `UpdateDetails()` | Populates the label + icons: weapon shows `"X + 1"` chamber counter; armor/helmet show condition% + rating; casings, modded, malfunction, frozen icons. |
| `UpdateAttachments()` | Shows/hides sprite children whose `.name` matches a nested item's `.file`. Sets `magazine`/`optic`/`suppressor` flags. |
| `Value() → int` | Composite market value: `itemData.value * (condition * 0.01)` (except Electronics), plus per-round ammo value for loaded weapons/mags, plus nested items recursively. |
| `Weight() → float` | Same pattern as Value — base weight, plus ammo weight proportional to `amount / defaultAmount`, plus nested items. |
| `State(state)` | Visual state toggle: `"Static"`, `"Free"`, `"Display"`, `"Selected"`. |

## Slot (`Slot.gd`)

`extends Panel, class_name Slot`. One-liner — just holds `@export var hint: Label`. Equipment slots under `Interface/Equipment`. The equipment-slot child-index mapping is hard-coded (see `RigManager` in weapons-and-combat.md — primary=1, secondary=2, knife=3, grenades=4/5, torso=10, hands=14).

## Grid (`Grid.gd`)

`extends TextureRect, class_name Grid`. Tetris-style inventory grid. `cellSize = 64`.

- `grid = {}` — 2D boolean dict `grid[x][y]` = cell occupied.
- `items = []` — items currently placed.
- `CreateGrid()` — auto-sizes from panel size.
- `CreateContainerGrid(containerSize)` — fixed size clamped to 4..8 × 1..13.
- `Spawn(item)` — auto-finds first free cell by scanning Y-then-X.
- `Place(item)` — commits at cursor position if space free (calls `CheckGridSpace` + `UpdateGrid`).
- `Pick(item)` — removes and returns, clearing cells.

## Interface (`Interface.gd`, 1200+ lines)

`extends Control`. The inventory/trader/tasks/crafting/tools root. Lives at `/root/Map/Core/UI/Interface`. Basically every other system pokes it.

### Onready children (top-level UIs)

```
Catalog, Inventory, Container, Equipment, Character, Trader, Supply,
Tasks, Deal, Tools/{Events, Crafting, Notes, Map, Casette}
```

Corresponding grids: `inventoryGrid`, `containerGrid`, `supplyGrid`, `catalogGrid`.

### Hard node references (parent-relative)

```
camera      = $"../../Camera"
placer      = $"../../Camera/Placer"
character   = $"../../Controller/Character"
rigManager  = $"../../Camera/Manager"
UIManager   = $".."
settings    = $"../Settings"
```

Moving these nodes breaks the interface silently.

### Key methods (subset of 40+)

| Method | Purpose |
|---|---|
| `Open()` / `Close()` | Show/hide the inventory root + pause the world. |
| `UpdateStats(updateLabels)` | Re-computes weight/capacity across inventory + equipment. |
| `AutoStack(slotData, grid)` | Tries to merge an incoming stack into existing stacks first. Called by `Pickup.Interact()`. |
| `Create(slotData, grid, trader)` | Instances an `Item`, `Initialize`s it, calls `grid.Spawn(item)`. |
| `OpenContainer(container)` | Switches to container mode, fills the container grid from `container.storage` or freshly generated `container.loot`. |
| `FillContainerGrid()` / `ClearContainerGrid()` / `StorageContainerGrid()` | Manage the right-hand container panel. |
| `Craft(recipeData)` | Consumes recipe inputs, produces outputs. See crafting-and-traders.md. |
| `InitializeRecipes(type)` | Switches the crafting list to a category (`_on_consumables_pressed` etc). |
| `UpdateProximity()` | Lights the heat/workbench/testbench/shelter icons based on `gameData.PRX_*`. |
| `InitializeEvents()` / `UpdateEvents()` | Refreshes the Events panel. |
| `InitializeNotes()` | Refreshes the pinned-tasks panel from `TraderSave.taskNotes`. |
| `Map()` / `FocusMap()` | Shows the paper map. |
| `CasettePlayer()` / `PlayCasette(track)` / `CasetteConsumption(delta)` | Casette-tape player: drains battery, plays OggVorbis. |

### Gotchas
- Crafting-type buttons (`_on_consumables_pressed` etc.) call `InitializeRecipes(int)`. Type is an integer — `0 = Consumables`, up through `6 = Furniture`. `defaultType` seeds the active tab on load.
- `const events = preload("res://Events/Events.tres")` and `const recipes = preload("res://Crafting/Recipes.tres")` — replacing those resources at runtime requires `take_over_path` since they're preloaded.

## LootTable (`LootTable.gd`)

```gdscript
extends Resource
class_name LootTable
@export var items: Array[ItemData]
```

That's it. Pure flat list. `res://Loot/LT_Master.tres` is populated by `Database` @tool (see autoloads doc). Per-level custom tables under `res://Loot/Custom/`. Kit tables under `res://Loot/Kits/`.

## LootContainer (`LootContainer.gd`)

`extends Node3D, class_name LootContainer`. A searchable container scene (drawer, crate, locker).

### Exports
- **Container:** `containerName`, `containerSize = Vector2(8, 13)`, `audioEvent`.
- **Generation:** `civilian`, `industrial`, `military` (rolls against matching items in `LT_Master`), `limit: String` (restrict to type), `exclude: String` (skip type).
- **Modified:** `custom: LootTable` (override pool), `force` (bypass rarity roll, spawn everything in `custom`), `joker` (treat roll as 100), `stash` (90% chance hidden), `locked` (no generation, no open), `furniture` (no generation; used as runtime storage only).

### Generation roll

`GenerateLoot()` rolls `1..100`:
- `roll == 1` → 10% chance, 1 legendary. ← effectively 1/1000.
- `roll ≤ 5` → 0..1 rare.
- `roll ≤ 25` → 0..4 commons.
- `roll == 100` (only reachable with `joker = true`) → 1..2 rare + 4..10 commons.
- Otherwise: empty.

Buckets filled by `FillBuckets()`: scans `LT_Master.items`, filters by `civilian`/`industrial`/`military` + `limit`/`exclude`, bucketed by `rarity`.

### Created loot
`CreateLoot(item)`:
- New `SlotData` with `itemData = item`.
- Non-tutorial: `amount = randi_range(1, item.defaultAmount)`, weapons/lights/NVG get `condition = randi_range(25, 100)`.
- Tutorial: full amount, skip random condition.
- Winter (`Simulation.season == 2`) + `freezable` → 10% chance `state = "Frozen"`.
- Appended to `loot: Array[SlotData]`.

### Opening
`Interact()` → calls `UIManager.OpenContainer(self)` (hard path `/root/Map/Core/UI`). `Storage(containerGrid)` snapshots the final arrangement back into `storage: Array[SlotData]` — that's what `Loader.SaveShelter()` reads.

## LootSimulation (`LootSimulation.gd`)

`extends Node3D`. World-scattered loot (not a container — loose pickups on the ground). Same bucket/roll logic as `LootContainer`, but `SpawnItems()` instantiates `Database.get(itemData.file)` scenes directly into the world, calls `pickup.Unfreeze()`, and boots them in a random direction with `linear_velocity = dir * 10.0`. Used for outdoor drop points.

## Pickup (`Pickup.gd`)

`extends RigidBody3D, class_name Pickup`. A world item you can walk up to and pick up.

- `slotData: SlotData` (the data), `mesh`, `collision`.
- Starts in `Freeze()` mode (`freeze = true`, `FREEZE_MODE_STATIC`) to avoid physics cost.
- `Kinematic()` — used while held/placed.
- `Unfreeze()` — drops into active physics, auto-sleeps after 1s.
- `Interact()`:
  1. Try `interface.AutoStack(slotData, inventoryGrid)` — merge into existing stack.
  2. Else try `interface.Create(slotData, inventoryGrid, false)` — new grid placement.
  3. Else play error sound.
- `UpdateTooltip()` — shows `name [x5]` for stackables, `name [IV]` for armor carriers (with plate), or just `name`. Cat gets `(RIP)` suffix if dead.
- `UpdateAttachments()` — same attachment visibility pattern as `Item`, plus weapon `Bullets` (0/1/2 child visibility for 0/1/2+ rounds loaded).
- `Explode()` — spawns `Effects/Explosion.tscn` and frees self. Used by grenades on impact.

Pickup scenes live under each item folder: `Items/Weapons/<Name>/<Name>.tscn`, `Items/Ammo/<Caliber>/<Variant>.tscn`, etc.

## ItemSave (`ItemSave.gd`)

```gdscript
extends Resource
class_name ItemSave
@export var name: String
@export var slotData: SlotData
@export var position: Vector3
@export var rotation: Vector3
```

Packed struct used by `Loader.SaveShelter()` for each item on the ground.

## Resource tree

```
res://Items/
├── Ammo/<Caliber>/*.tres + *.tscn         # ItemData per variant + pickup scene
│   └── Cartridges/                         # manual-load cartridge scenes
├── Attachments/
│   ├── Optics/<Optic>/                     # scope scene + AttachmentData
│   ├── Suppressors/
│   └── Mounts/
├── Weapons/<Name>/
│   ├── <Name>.tscn                         # pickup
│   ├── <Name>_Rig.tscn                     # first-person rig
│   ├── <Name>.tres                         # WeaponData
│   └── Magazine_<Name>.tscn + .tres
├── Knives/<Name>/                          # same split
├── Grenades/
├── Fishing/
├── Instruments/<Name>/<Name>_Rig.tscn
├── Clothing/, Armor/, Helmets/, Belts/, Backpacks/
├── Consumables/, Medical/, Electronics/, Misc/, Lore/, Keys/, Books/
└── Furniture/                              # placeable items
res://Loot/
├── LT_Master.tres                          # built by Database @tool
├── Kits/                                   # starting-kit tables
├── Simulations/                            # LootSimulation presets
└── Custom/                                 # per-container overrides
```

## Gotchas

- `ItemData.file` must exactly match the `const <name> = preload(...)` identifier in `Database.gd`. `Database.get(file)` is how new pickups are spawned.
- `SlotData.Update()` duplicates `nested` and `storage` arrays — but shallowly. Mutating a nested `ItemData`'s fields leaks across instances. Treat `ItemData` as immutable.
- `condition` is a float internally but rendered as `int(round(...))`. Don't compare to integer thresholds in new code — use `> 25.0` etc.
- `LootContainer._ready()` generates on scene instance. Loading a shelter via `Loader.LoadShelter()` overwrites the fresh roll from `storage`. Containers with `locked = true` or `furniture = true` skip generation entirely.
- `Rarity.Null` excludes from `LT_Master`. New item definitions default to `Common` — set to `Null` if you don't want them looted.
