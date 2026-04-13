# Shelter & Interactables

Shelters are small `.tscn` maps (Cabin, Attic, Classroom, Tent, Bunker) where the player can place furniture, feed the cat, sleep, ignite fires, and flip switches. All of this is implemented by a small set of node scripts exposed via `Interact()` / `UpdateTooltip()` — the interactor pattern (see player-system.md).

## Furniture (`Furniture.gd`, class_name Furniture)

`@tool extends Node3D`. A child component of every placeable prop (the prop's root is the `owner`; Furniture is a child component that holds placement logic).

### Exports
- `itemData: ItemData` — the item this furniture corresponds to in the catalog.
- `mesh: MeshInstance3D`, `colliderR: MeshInstance3D` (render collision), `colliderP: MeshInstance3D` (pathfinding collision).
- `wallElement: bool` — snaps to walls instead of floors.
- `canOverlap: bool` — allows overlap with other Furniture (not generic bodies).

### Scene subtree (authored)
```
Furniture
├── Indicator  — green wireframe shown in decor mode
├── Area       — overlap-test Area3D (sized to mesh AABB - 5cm)
├── Parenter   — Area3D 5cm larger than mesh; catches nearby Pickups to reparent with furniture while moving
├── Rays       — 5 RayCast3Ds: center + 4 corners
└── Hint       — flat ghost silhouette shown at target position
```

### `ExecuteInitialize` (@tool setter)
Editor button. Reads `mesh.get_aabb()`, regenerates the Area collision (mesh AABB - 5cm), the Parenter collision (mesh AABB + 5cm), positions the 5 ray probes (center + 4 corners). Wall elements orient differently:
- Floor furniture: rays point `(0, -0.2, 0)` (down-probe for floor snap).
- Wall elements: rays point `(0, 0, -0.2)` (z-probe for wall snap).

### Runtime
`_ready()` (non-editor): caches `sourceMaterials` from the mesh, hides indicator/hint, configures Area + Ray collision layers.

Furniture Area collision layers/masks:
- Layer 1.
- Mask 1, 2, 3, 4, 5, 14 (world/players/items), NOT 6 (pathfinding).

### Move loop (driven by `Placer.gd`)
`StartMove()` — called when the player picks up furniture in decor mode:
- `isMoving = true`, hide indicator.
- Disable `colliderR` and `colliderP` collision (so furniture ghosts through walls).
- Swaps all surface materials to `MT_Furniture.tres` (ghost material, reads `"Valid"` shader param).
- `ActivateRays()`, `ParentItems()` (any Pickup in Parenter area reparents to the furniture owner so items move with it), `FreeHint()` (hint reparents to map for free floating).

Per-tick at 10Hz while `isMoving`: `CheckOverlap()`, `CheckRays()`, `CanPlace()`, `HintPosition()`.

- `CheckOverlap` — writes `areaValid` true if no overlapping bodies (or only Furniture-group if `canOverlap`).
- `CheckRays` — writes `raysValid` true only if all 5 rays are colliding AND no ray hits a `"Transition"`-group node (furniture can't block doors).
- `CanPlace` returns `raysValid && areaValid`, updates the ghost shader's `valid` param.
- `HintPosition` snaps the hint to the center ray's collision point at 0.1m increments.

`ResetMove()` — place the furniture:
- Snaps `global_position` to 0.1m grid based on corner ray collision point.
- Snaps rotation.y: floor = 15°, wall = 90°.
- `canOverlap` items get a tiny `scale.y = randf_range(0.8, 1.0)` for variety.
- Re-enables colliders, restores source materials, plays `UIFurniture` sound, frees parented items, reparents hint.

`Catalog()` — pickup into inventory:
- If moving and carrying items: `DropParentedItems()` first.
- If `owner is LootContainer` with storage: `interface.AddToCatalog(itemData, owner.storage)` + free. Else `AddToCatalog(itemData, null)` + free.
- Plays `pickup` sound.

`GetSnapData()` — returns `{point, normal, valid}` from the center ray. Used by Placer's magnet mode.

## Placer (`Placer.gd`)

`extends Node3D`. Lives at `/root/Map/Core/Camera/Placer` (a child of the camera). Drives both **item placement** (any `Pickup` in inventory) and **furniture placement** (in decor mode).

### Modes
- `gameData.decor = false` → item placement. Distance 0.5..4m with scroll; middle-click cycles `orientationMode 1/2/3` (upright / tipped X / tipped Z); right-click rotates on roll axis. Collision-sensitive: `Collided(body)` auto-attaches Weapon/Attachment/Knife/Grenade to a `"Display"`-group mount using `wallOffset` + `orientation` from ItemData.
- `gameData.decor = true` → furniture placement. Same scroll + rotate, but:
  - Left-click toggles `gameData.magnet` — when magnet is on and the center ray hits a surface, the furniture snaps to that surface (wall projection for wallElements, Y-lift for floor).
  - `interact` finalizes via `furniture.Catalog()` (pocket it) instead of `ResetMove()`.

Input guards: all early-out on `freeze / isReloading / isInspecting`. Placement input gated by `gameData.isPlacing`.

### `ContextPlace(target)`
Programmatic placement entry — used by Interface when you drop an item from inventory ("Place from inventory") or instantiate new furniture from the catalog. In decor mode this runs StartMove on the furniture; in normal mode it positions the item 1m in front and freezes+kinematics it after a 0.1s wait.

## DecorMode (`DecorMode.gd`)

`extends Node`. The decor-mode toggle. Enabled only in shelters, tutorial, or the Template map.

- `_ready()` (after 1s): if not in shelter/tutorial/Template → `gameData.decor = false` + hide all furniture indicators.
- `_physics_process`: listens for `"decor"` action (default: toggle key), flips `gameData.decor`, calls `FurnitureVisibility(visibility)` which shows/hides every `Furniture.indicator` and every `Transition.owner.spawn` marker.

Guards: won't toggle while `freeze / isPlacing / isOccupied / interface / settings`.

## Bed (`Bed.gd`)

Sleep interactable. `randomSleep = randi_range(6, 12)` chosen on `_ready`.

`Interact()` → on success:
1. `Simulation.simulate = false`, `gameData.isSleeping = true`, `freeze = true`.
2. `UpdateSimulation(randomSleep * 100.0)` — advances `Simulation.time`, handles 2400→0 day rollover + `weatherTime` deduction.
3. Plays `transition` + `sleep` sounds.
4. Awaits `randomSleep` seconds (real-time, scaled to in-game hours).
5. Applies `energy -= 20`, `hydration -= 20`, `mental += 20`.
6. Rotates controller 180° (wake up facing away).
7. `Loader.Message("You slept N hours", GREEN)`.
8. Unfreezes, `canSleep = false` (one nap per bed per load).

Tooltip: `"Sleep (Random sleep: 6-12h)"` if `canSleep`, else empty.

## Fire (`Fire.gd`)

Campfire/stove/fireplace. Exports `effect` (VFX), `light: OmniLight3D`, `lightRange`, looped `audio`, `fireArea` (damage trigger), `heatArea` (gameData.heat source), `force: bool`.

- On `_ready()`: `matchesSlot = interface.equipmentUI.get_child(15)` (hardcoded equipment index). Rolls `1..100 <= 2` (2% chance of starting lit), or forced on.
- `Interact()`:
  - Off → requires `matchesSlot` to contain matches; `Activate()` + `ignite` sound + `ConsumeMatch()` (decrement amount; free if 0).
  - On → `Deactivate()` + `extinguish` sound.
- `Activate()/Deactivate()` toggles: effect visibility, light (`flicker` + omni_range + process_mode), audio play/stop, `fireArea.monitorable`, `heatArea.monitorable`.

Tooltip is context-aware — tells you whether matches are equipped.

## Fuel (`Fuel.gd`)

Placeholder. `UpdateTooltip` prints `"Fuel Tank [89%]"` (hardcoded). `Interact()` plays `UIError`. The real fuel economy isn't wired — this is a stub for future shelter generator work.

## Switch (`Switch.gd`) / in group `"Switch"`

Generic on/off switch for connected targets.
```gdscript
@export var targets: Array[Node3D]
@export var active = false
```
`Interact()` toggles, calls `target.Activate()` / `target.Deactivate()` on every target, plays `switch` sound. Saved as `SwitchSave{name, active}` — restored by `Loader.LoadShelter` via group lookup.

## Door (`Door.gd`, class_name Door)

Swinging door with lock/key, handle animation, and linked-pair logic.

### Exports
- `openAngle: Vector3`, `openOffset: Vector3` — delta from closed pose.
- `audioEvent: AudioEvent`, `handle: Node3D` (the handle that twists).
- `key: ItemData` — if set, spawns `locked = true`.
- `linked: Door` — other side's Door; unlocking one unlocks both.
- `jammed: bool` — permanently inert.

### Runtime
`_ready()`:
- Caches default position/rotation.
- If `key` → `locked = true`.
- Else if `!jammed` → 1-in-6 chance of spawning open (`isOpen = true`, `animationTime += 4`).

`_physics_process` lerps `position` / `rotation_degrees` toward the closed or open target at `openSpeed = 4.0`, while `animationTime > 0`. Handle lerps toward `handleTarget` at `handleSpeed = 10.0` then snaps back to zero.

`Interact()`:
- Locked + key → `CheckKey()`.
- Jammed → nothing.
- `isOccupied` → nothing (5s cooldown).
- Else: flip `isOpen`, add 4s of anim time, set handle target (±45° based on hinge direction), play door sound.

`CheckKey()` scans `interface.inventoryGrid` for the key, unlocks (and `linked.locked = false`), plays `doorUnlock`, consumes the key via `inventoryGrid.Pick(item)` + `queue_free()`.

Tooltip states: `"Open with <key>"`, `"Door [Jammed]"`, `"Door [Occupied]"`, `"Door [Open/Close]"`.

## Cables (`Cables.gd`)

`@tool extends Node3D`. Editor-time utility that builds overhead power-line cables between poles and a blocker wall below them.

Exports `poles: Node3D` (container of pole nodes, each with `.targets: Array[Node3D]`). `generate = true` triggers:
- `ExecuteClear` — removes prior `Mesh` / `Blocker` children.
- `ExecuteGenerateCables` — builds a 2cm-thick quad tube along a sagging Curve3D (4m sag at midpoint), 0.5 points/m, using `MT_Cable.tres`. Shadow casting off.
- `ExecuteGenerateBlocker` — builds an invisible 5m-wide collision strip along the same curve on layer 31 with `Surface = "Cables"`. Prevents flying over.

Poles have `.targets: Array[Node3D]` — the nodes the pole's cables connect to.

## Cat system

### `Cat` (`Cat.gd`) — the animal
`extends Node3D`. State: `enum { Idle, Sit, Bake, Eat, Sleep, Rescue }`.

`_ready()`: if `gameData.catDead` → `Dead()` (play `Cat_Sleep`, stop → corpse). Else `Sit` + animator active.

`Behavior()`:
- If not Rescue: mirrors `box.isOpen` → Sit (box closed) / Idle (box open).
- State-driven animator flags: `Sit / Idle / Bake / Eat / Sleep` (Rescue also uses Sleep animation).
- `Rescue` state overrides `meowCycle = 5s` (constant distress meowing in the well).

`Meow(delta)` — random meow every 30–60s (Rescue: 5s), rotates the jaw bone via `skeleton.set_bone_global_pose_override(jawIndex, ...)`. Direction from `CatData.meowDirection` enum.

`ForceMeow()` — external trigger (used by CatBox on movement + CatFeeder on feeding).

### `CatBox` (`CatBox.gd`) — carrier for the cat
Monitors own motion. If still for `stillThreshold = 10s` without tilt > 5° → `isOpen = true`, activates `feeder`, `cat.ForceMeow()`. Any movement/tilt or `gameData.isFiring || catDead` closes it. Lids (`Lid_01/02`) lerp ±250° when opening/closing at 250°/s.

### `CatFeeder` (`CatFeeder.gd`)
`@export feedItems: Array[ItemData]`. `Interact()`:
- Only if `cat.currentState != Eat`.
- Scans inventory for any item in `feedItems`; first match → sets state `Eat`, `gameData.cat = 100`, consumes the item, `Loader.Message("Cat Fed (name)")`, waits 30s, returns to Idle.

Tooltip: `"Feed cat: [item1, item2, ...]"` built from `feedItems`.

### `CatData` (`CatData.gd`)
```gdscript
extends ItemData
class_name CatData
@export var meow: Resource                  # AudioEvent
@export var meowDirection = MeowDirection.X # enum X/Y/Z — which axis to rotate jaw
@export var meowRotation: Vector2           # (rest, open) degrees
```

### Cat rescue flow (see EventSystem.Cat())
Spawns a Cat in `State.Rescue` at a well's `Bottom` child, plus a `Rescue.tscn` 3m above. Interacting with the Rescue triggers `CatRescue.gd` (not shown here — orchestrates pulling cat from well and setting `gameData.catFound = true`). Rescue meowing (5s cycle) helps the player locate the well.

## Fishing system

### `FishPool` (`FishPool.gd`)
`extends MeshInstance3D`. Invisible volume. On `_ready`: spawns 1–10 random fish from `species: Array[PackedScene]` at random points inside the mesh AABB.

LOD: every 100 physics frames, if `playerDistance3D < 50` activates all children (show + `PROCESS_MODE_INHERIT` + `active = true`); >50 deactivates (hide + disabled + not active). Keeps fish cheap when the player isn't nearby.

### `Fish` (`Fish.gd`, class_name Fish)
```gdscript
@export var slotData: SlotData       # what catching this yields
@export var hookOffset = 0.0
```

Per-tick (while active):
- Not hooked, no lure → `Swim` toward a random waypoint inside the pool's AABB at 0.5 m/s.
- `Sensor` (1Hz) — scans for `Area` of `type == "Lure"`. First unhooked lure → attaches to it, flips `attracted = true`, `lure.hooked = true`.
- Attracted → `Attract` moves fish toward lure at 2 m/s, slerps rotation to face it. If lure rises above `y = -2` (out of water) → release. If close enough (<0.1m) → reparent to lure, `lure.owner.PlayHooked()`, set local pose via `hookOffset`, `hooked = true`.

### `FishingData` (`FishingData.gd`)
```gdscript
extends ItemData
class_name FishingData
# Rig pose offsets: high/low/inspect/collision position+rotation
```

Rod handling poses. The actual rod physics live in `FishingRig.gd` (not documented here — see weapons-and-combat.md for rig pattern).

## Gotchas

- **`Fire.matchesSlot = interface.equipmentUI.get_child(15)`** is another hardcoded equipment child index (same family as NVG at 17 — see ui-system.md). If you add/remove an equipment slot, every hardcoded index shifts.
- **Furniture's `Area` masks 1-5 + 14 but NOT 6.** Pathfinding colliders (layer 6) are intentionally ignored during move overlap tests.
- **Furniture Ray #0 is the center (snap anchor). Rays 1-4 are corners (all-must-collide).** Reordering breaks snap.
- **Door random-open roll:** `randi_range(0, 5) == 0` → ~16.7% spawn open. Mutates state on `_ready`, so reloading the scene re-rolls.
- **`Bed.canSleep = false` after first nap.** Re-entering the shelter rebuilds the bed and resets it. Saving/loading doesn't persist `canSleep` — it's always `true` after load.
- **Placer's `Collided()` hook auto-attaches Weapon/Attachment/Knife/Grenade to `"Display"`-group mounts.** If you add a custom rack, put it in that group + ensure the orientation math works.
- **`CatBox.isOpen` relies on being still for 10s AND not `isFiring`.** Firing a weapon near the box closes it immediately, which also triggers `cat.ForceMeow()`.
- **`FishPool.set_layer_mask_value(1, false)`** — the pool mesh is invisible to the camera. Enable layer 1 if you need to debug-see it.
- **Fish Sensor uses `Area.type == "Lure"`** — the Lure scene must have an `Area` (class_name) child with `type = "Lure"` or fish will ignore it.
- **`CatData.meowDDirection`** (line 116 of Cat.gd) is a typo — the elif reads `meowDDirection`, so only directions 0 and 2 (X and Z/default) are ever selected; `Y` path is dead. Don't rely on the Y axis.
- **Switch targets call `.Activate()/.Deactivate()`** — any target must implement both methods. Doesn't duck-type check; null-methods will crash.
