# Resources Reference

Where data lives on disk. This is a path-only map — for what the resources *do*, cross-reference the system-specific docs.

## Top-level dirs

```
res://
├── AI/                 agent scenes + authoring tools
├── Assets/             vehicle scenes (Helicopter, Fighter_Jet, BTR, Police, CASA)
├── Audio/              raw WAV/OGG clips used by AudioEvent resources
├── Crafting/           RecipeData .tres files + the Recipes.tres catalog
├── Editor/             @tool-only helpers
├── Effects/            VFX (particles, decals, blood, flash)
├── Environment/        skybox, sun/moon textures, post-process materials
├── Events/             EventData .tres + the Events.tres catalog
├── Fonts/              UI fonts
├── Items/              ItemData + Pickup scenes, per-category
├── Loot/               LootTable .tres + LootSimulation scenes + starting kits
├── Modular/            shared shader materials + modular meshes
├── Nature/             trees, rocks, foliage scenes
├── Prefabs/            composite props (doors, beds, fires, etc.)
├── Resources/          core autoload scenes + the GameData/AudioLibrary singletons
├── Scenes/             top-level scenes (see scenes-reference.md)
├── Scripts/            all GDScript source
├── Shaders/            .gdshader source
├── Terrains/           per-map terrain meshes + vegetation Spawner scenes
├── Traders/            TraderData + Trader scenes + task files
└── UI/                 UI Control scenes and elements
```

## `res://Resources/` — core singletons and prefabs

| File | Role |
|---|---|
| `GameData.tres` | **The** shared-state resource. Preloaded by every script. |
| `AudioLibrary.tres` | Canonical catalog of all `AudioEvent`s. Preloaded by every script that plays sound. |
| `Loader.tscn` | Autoload instance — holds fade overlay + messages. |
| `Database.tscn` | Autoload — scene registry keyed by `ItemData.file`. |
| `Simulation.tscn` | Autoload — global clock. |
| `AI.tscn` | Empty node used as the Agents parent template? (Deprecated) |
| `AnimatorBasic.tscn` / `AnimatorManual.tscn` | Reusable AnimationTree setups. |
| `AudioInstance2D.tscn` / `AudioInstance3D.tscn` | Self-freeing audio players (see audio-system.md). |
| `Cache.tscn` | Shader / resource precompile helper. |
| `FishPool.tscn` | Fishing pool base (see shelter-and-interactables.md). |
| `Flash.tscn` | Muzzle flash OmniLight3D (see weapons-and-combat.md). |
| `Furniture.tscn` | Base Furniture component scene. |
| `Inputs.tscn` | Input rebind UI. |
| `Killbox.tscn` | Out-of-world safety volume. |
| `PropsSetup.tscn` | Editor helper. |
| `RemapButton.tscn` | Input rebind button. |
| `Ribbon.tscn` | Border ribbon element. |
| `Spawn.tscn` | Transition spawn marker. |
| `Spawners.tscn` | Spawner container prefab. |
| `Transition.tscn` | Base door/gate scene. |
| `TreeRenderer.tscn` | Shared tree renderer. |
| `Viewport.tscn` | Picture-in-picture viewport prefab. |
| `World.tscn` | Base sky + TOD scene (instanced under each map). |

## `res://Items/` — item catalog

One directory per category. Each item is typically a sub-dir containing:
- `<Name>.tres` — the `ItemData` (or subclass like `WeaponData`, `FishingData`, `NVGData`).
- `<Name>.tscn` — the base 3D model scene.
- `<Name>_<WxH>.tscn` — grid-display variants (e.g. `Ammo_9x19_1x1.tscn`).
- `<Name>_Magazine.tres/tscn` — mag variants for weapons.
- `<Name>_Rig.tscn` — first-person rig (weapons only).
- `<Name>_Mount.tscn` — display-wall attach variant.
- `<Name>_Static.tscn` — no-physics variant.
- `Audio/` — subdirectory with per-item AudioEvent resources.
- `Files/` — misc extras.

### Subdirs
```
Items/
├── 0 - Shared/         shared meshes/materials
├── Ammo/               Ammo_9x19, Ammo_9x18, Ammo_762x39, Ammo_762x54R, Ammo_545x39,
│                       Ammo_223, Ammo_308, Ammo_12x70, Ammo_46x30, Ammo_45ACP
├── Armor/              plate carriers and plates
├── Attachments/        ACOG, ANPEQ, EXPS, HMR, Hybrid, Kobra, Leopard, MRO, Micro,
│                       Common (flashlights, lasers, grips) + others
├── Backpacks/          carry slot items
├── Belts/              belts (grenade slots)
├── Books/              readable lore items
├── Clothing/           shirts/pants
├── Consumables/        Beer, Canned_*, Coffee*, Cooked_*, Cat_Food, Chocolate_War,
│                       Cigarettes, Cigars (lots of food/drink)
├── Electronics/        radios, tapes, batteries, NVGs
├── Fishing/            rods (FishingData + FishingRig)
├── Grenades/           grenade items
├── Helmets/            HelmetData
├── Instruments/        casette tapes + misc
├── Keys/               shelter keys (consumed by Transition.CheckKey)
├── Knives/             knife items + rigs
├── Lore/               Cat.tscn, Rescue.tscn, story items
├── Medical/            bandages, splints, tourniquets, stims
├── Misc/               tools, parts, misc
├── Physics/            ragdoll/physics props
├── Rigs/               K19, LVPC, Vest_Fishing (carrier rigs)
└── Weapons/            AK-12, AKM, AKS-74U, Colt_1911, Common, Glock_17, HK416, KAR-21,
                        KP-31, M4A1, Mosin, MP5K, Makarov, Remington, etc.
```

`Database.gd` walks this tree at boot and populates its `get(file: String)` map keyed by `ItemData.file` — see autoloads-and-boot.md.

## `res://Loot/` — loot tables and starting kits

```
Loot/
├── LT_Master.tres          — master item pool; each entry flags generalist/doctor/gunsmith availability + rarity
├── Custom/
│   ├── LT_Airdrop.tres         — airdrop crate roll
│   ├── LT_Oil_Sample.tres
│   ├── LT_Patient_Report.tres
│   └── LT_Punisher.tres        — boss drop
├── Kits/                   — difficulty-1 starting kits (pick_random)
│   ├── Kit_Colt.tres
│   ├── Kit_Glock.tres
│   ├── Kit_MP5K.tres
│   ├── Kit_Makarov.tres
│   ├── Kit_Mosin.tres
│   └── Kit_Remington.tres
├── Lore/                   — scripted story pickups
│   ├── LS_Oil_Sample.tscn
│   └── LS_Patient_Report.tscn
├── Simulations/            — LootSimulation scenes (per-zone pre-spawned containers)
│   ├── LS_Civilian.tscn
│   ├── LS_Industrial.tscn
│   └── LS_Military.tscn
└── Tutorial/
    ├── LT_Ammo.tres
    ├── LT_Armor.tres
    ├── LT_Attachments.tres
    ├── LT_Equipment.tres
    ├── LT_Grenades.tres
    ├── LT_Items.tres
    ├── LT_Medical.tres
    ├── LT_Weapons_01..04.tres
```

Starting kits are referenced by `Loader.startingKits: Array[LootTable]` and picked at random on `NewGame` difficulty 1.

## `res://Crafting/`

```
Crafting/
├── Recipes.tres           — master Recipes resource (consumables/medical/equipment/weapons/electronics/misc/furniture arrays)
├── Consumables/           Coffee_Brewed, Cooked_Fish_Soup, Cooked_Meatballs, Cooked_Pea_Soup,
│                           Cooked_Tomato_Soup, Energy_Drink, Kilju, Kompot, ...
├── Medical/               Improvised_Bandage, Improvised_Splint, Improvised_Tourniquet, ...
├── Electronics/           — electronics recipes
├── Furniture/             Bed_Civilian, Bed_Nomad, ...
├── Weapons/               — weapon repair/upgrade recipes
│                          AK-12_Repair, AKM_Repair, AKS-74U_Repair, Colt_1911_Repair,
│                          Glock_17_Repair, HK416_Repair, KAR-21_223_Repair,
│                          KAR-21_308_Repair, KAR-21_Upgrade, KP-31_Repair, ...
```

Each `.tres` is a `RecipeData` instance. `Recipes.tres` groups them by panel tab.

## `res://Events/`

```
Events/
├── Events.tres            — master Events resource (Array[EventData])
└── List/
    ├── D1_Generalist.tres
    ├── D2_Doctor.tres
    ├── D3_Fighters.tres
    ├── D4_Cat.tres
    ├── D5_Punisher.tres
    ├── D6_Airdrops.tres
    ├── D7_BTR.tres
    ├── D8_Helicopters.tres
    ├── D9_Crashes.tres
    ├── D10_Gunsmith.tres
    ├── D20_Outpost.tres
    ├── D30_Escape.tres
    ├── D40_Return.tres
    └── D50_Transmission.tres
```

File-prefix `D<n>` = `EventData.day` (earliest eligible simulation day). `Events.tres` aggregates them into the array `EventSystem` iterates.

## `res://Traders/`

```
Traders/
├── Doctor/
│   ├── Doctor.tres             — TraderData
│   ├── Doctor.tscn             — in-world Trader node
│   ├── Doctor_Tutorial.tres
│   ├── Files/                   — extra assets
│   ├── Tasks/                   — Array[TaskData] (numbered .tres files, e.g. 01_Foo.tres)
│   └── Tutorial/
├── Generalist/
│   ├── Generalist.tres
│   ├── Generalist.tscn
│   ├── Generalist_Tutorial.tres
│   ├── Files/
│   ├── Tasks/                   — 01_Prime_Time, 02_Bad_Habits, 03_Backpains,
│   │                              04_Coffee_Reserve, 05_Sweaty_Business,
│   │                              06_Handyman, 07_Six_Pack, 08_Old_Friend,
│   │                              09_Road_Trip, 10_Homemade, ...
│   └── Tutorial/
└── Gunsmith/
    └── <same pattern>
```

Note: "Grandma" appears in TraderSave schema but has no trader directory here — she may be unimplemented content or a future addition.

## `res://AI/`

```
AI/
├── Bandit/             Area 05 agent — AI_Bandit.tscn + meshes + voice audio
├── Guard/              Border Zone agent
├── Military/           Vostok agent
├── Punisher/           Boss agent
└── Tools/
    ├── AI_SP.tscn          spawn point (group "AI_SP")
    ├── AI_WP.tscn          waypoint (group "AI_WP")
    ├── AI_PP.tscn          patrol point (group "AI_PP")
    ├── AI_CP.tscn          cover point (group "AI_CP")
    ├── AI_HP.tscn          hide point (group "AI_HP")
    ├── AI_VP.tscn          vehicle waypoint (group "AI_VP")
    ├── AI_Pole_E/N/S/W.tscn — cardinal cover poles
    ├── AI_Container.tscn    — loot container spawned on agent death
    ├── Navblock.tscn        — mesh that blocks AI navigation
    ├── MS_Navblock.obj      — the blocker mesh
    └── Spine.tres           — default SpineData (bone 12, default weights)
```

## `res://Assets/` — vehicles + big props

```
Assets/
├── BTR/                BTR.tscn
├── CASA/               CASA.tscn (airdrop plane)
├── Fighter_Jet/        Fighter_Jet.tscn
├── Helicopter/         Helicopter.tscn + Helicopter_Crash.tscn
├── Police/             Police.tscn
└── ...                 other large set pieces
```

All referenced by `EventSystem.gd` as `preload(...)`.

## `res://Audio/` — raw clips

Organized by logical group (Weapons, UI, Ambient, Movement, Medical, ...). Individual WAV/OGG files referenced by `AudioEvent` resources. Don't preload these directly — go through `AudioLibrary.tres` → `AudioEvent` → `audioClips`.

## `res://Terrains/`

Per-outdoor-map directory. Contains terrain mesh, `Spawner_*.tscn` children (vegetation scatter), LOD assets. Referenced from the outdoor `.scn` files.

## `res://Prefabs/`

Composite interactables:
- Doors (variants + key-locked versions)
- Beds
- Fires (campfire, fireplace, stove)
- Radios / Televisions
- CatBox / CatFeeder
- Fishing rods (rig bases)

Each prefab is referenced by furniture recipes or map geometry.

## `res://UI/`

```
UI/
├── Elements/            Item.tscn, Slot.tscn, Grid.tscn, Message.tscn, Tooltip.tscn, Event.tscn, Task.tscn, Recipe.tscn, ...
├── Panels/              Inventory, Crafting, Trader, Tools (Map, Casette, Tasks, Notes, Events)
├── HUD/                 HUD components (Condition, Vitals, Stats, Transition, Malfunction, Magnet, ...)
├── Menu/                Main menu elements
├── Death/
└── Settings/
```

## Gotchas

- **`Database` keys by `ItemData.file` (string), not by path.** Two items with the same `file` value collide. Names must be unique across the entire Items tree.
- **Starting kits live at `res://Loot/Kits/`** but are referenced by the `startingKits` export on `Loader.tscn`. Adding a new kit file doesn't register it — edit the array on the Loader scene.
- **`LT_Master.tres` flags items with `generalist/doctor/gunsmith` booleans** (see items-and-loot.md). That's what `Trader.FillTraderBucket()` scans — bypasses per-trader directories.
- **`Traders/Grandma/` doesn't exist** in decompile but `TraderSave` and `Interface.trader` logic handle "Grandma" as a valid trader name. Likely unimplemented.
- **Outdoor `.scn` files can't be diffed as text.** Structural changes require opening in Godot.
- **`Events/List/D<n>_Name.tres` prefix is just convention** — `EventData.day` is the authoritative field. Renaming doesn't break anything as long as `Events.tres` still references the file.
- **Item directories often contain multiple `.tscn` variants** (base, _1x1/_6x2, _Mount, _Static, _Rig). The base `.tscn` is what `Database` registers — variants are referenced manually by name from systems that need them (traders, racks, rigs).
