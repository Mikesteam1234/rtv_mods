# World & Levels

Maps are either `.tscn` (shelters — small, hand-authored) or `.scn` (outdoor — heavy, packed binary). Every map instantiates `res://Scenes/Core.tscn` under the root and has a sibling `World` node running `World.gd`.

## Map wrapper (`Map.gd`)

```gdscript
extends Node3D
@export var mapName: String         # "Cabin", "Highway", "Tutorial" ...
@export var mapType: String         # "Shelter", "Area 05", "Border Zone", "Vostok", "Intro"
@export_group("Details")
@export var shelterLocation: String
```

Attached to the level's root `/root/Map` node. Everything that needs to know "where am I" reads `/root/Map.mapName` and `.mapType`. Used by `DynamicAmbient`, `Killbox`, `Transition`, `AudioLibrary`.

## World (`World.gd`, ~600 lines)

`@tool extends Node3D`. The sky, time-of-day, weather, and ambient audio. Lives at `/root/Map/World`.

### Exports

- **Time of Day:** `enable`, `audio`, `shelter`, `intro`, `time: 0..2400`, `tick`.
- **Weather flags (booleans):** `winter`, `overcast`, `wind`, `rain`, `snow`, `thunder`, `fog`, `aurora`. Set based on `Simulation.weather` at spawn.
- **Gradients** (`GradientTexture1D` / `CurveTexture`): `ambientColor`, `overcastColor`, `skyColor`, `horizonColor`, `groundColor`, `sunColor`, `sunScatter`, `moonColor`, `underwaterColor`, `sunEnergy`, `skyReflection`, `fogDensity`. All sampled by current `time / 2400.0`.
- **Materials:** `skyMaterial`, `waterMaterial`, `underwaterMaterial`.
- **Editor rendering/lighting presets:** `RLow/Medium/High/Ultra`, `LLow/Medium/High/Ultra`, `detailsShadowsOn/Off`, `waterReflectionsOn/Off`, `showIndicators/hideIndicators`, `showSpawns/hideSpawns` — @tool setters that flip project rendering settings in-editor.

### Scene tree

```
World
├── Planet
│   ├── Sun / Light (DirectionalLight3D)
│   └── Moon / Light (DirectionalLight3D)
├── Audio
│   ├── Dawn, Day, Dusk, Night                # TOD beds
│   ├── Wind_Light, Wind_Heavy, Wind_Howl
│   ├── Rain, Thunder, Strike
├── VFX
│   ├── Rain (GPUParticles3D)
│   └── Snow (GPUParticles3D)
└── Environment (WorldEnvironment)
```

### Per-tick pipeline

`_process(delta)`:
- Throttled by `tickTimer >= tick`.
- If `intro` → `Static()` (fixed lighting for the intro cutscene).
- If `shelter` → `Static()` + play `windLightAudio` at low volume.
- Otherwise → `Weather(delta)`, `Audio(delta)`, `TOD()`.

`TOD()` samples the gradients at `time / 2400` and writes `sunLight.light_color`, `skyMaterial` params, `environment.ambient_light_color`, etc. Updates `gameData.TOD` (integer enum 1=Dawn / 2=Day / 3=Dusk / 4=Night), `gameData.fog`.

`Weather(delta)` lerps each `*Value` (`winterValue`, `overcastValue`, `rainValue`, `snowValue`, `fogValue`, `auroraValue`) toward its flag (0.0 or 1.0) at `blendingSpeed = 20.0 * delta`. Writes the sky/water material uniforms. Toggles rain/snow VFX `emitting`.

`Audio(delta)` cross-fades the 10 audio streams based on `TOD` + weather flags + `gameData.indoor`.

### `shelter = true` behaviour

Shelters don't need a full sky sim. `Static()` holds everything at a fixed state and just plays the light-wind ambient bed. Weather doesn't advance while indoors.

## Transition (`Transition.gd`)

`extends Node3D`. Door/gate/portal between levels. In group `"Transition"`.

### Exports
- `spawn: Node3D` — where the player appears on arrival (hidden at runtime).
- `time: float` — in-world travel duration (in hours × 10 — see `UpdateSimulation`).
- `nextMap: String`, `nextZone: String`, `currentMap: String`.
- `shelterEnter: bool` / `shelterExit: bool` — marks which direction this is.
- `tutorialExit: bool` — skips the simulation advance.
- `key: ItemData` — lock if set and shelter not yet visited.

### `Interact()`

```
if locked:     CheckKey(); return
if tutorial:   Loader.LoadScene(nextMap)         # short-circuit
else:
    UpdateSimulation()                            # advance clock
    Simulation.simulate = true
    gameData.currentMap/previousMap = ...
    gameData.energy     -= time * 5.0
    gameData.hydration  -= time * 10.0
    Loader.LoadScene(nextMap)
    Loader.SaveCharacter()
    Loader.SaveWorld()
    if shelterExit: Loader.SaveShelter(currentMap)
```

`UpdateSimulation()` advances `Simulation.time` by `time * 100.0`, handles rollover (day++, `Loader.UpdateProgression()`), and decrements `weatherTime`.

### `CheckKey()`

Scans `interface.inventoryGrid` for an item whose `.file == key.file`. If found: unlock, `Loader.UnlockShelter(nextMap)` (writes a stub `ShelterSave` with `initialVisit = true`), consume the key, play unlock sound.

## Border / BorderPoles (`Border.gd`)

`@tool extends Node3D`. Procedurally builds the playable-area boundary — poles, flag ribbons, invisible blockers, and a full-height kill wall.

- **Playable area:** 400 × 400 square. Perimeter = 1600m.
- **Pole spacing:** 10m on ground, 20m on water. Ray-cast down from y=100 to find terrain; picks `Pole_Ribbon_Ground` or `Pole_Ribbon_Water` based on `hit.collider.surface`.
- `ExecuteGenerateRibbon` — builds a 5cm-wide mesh ribbon connecting the poles via `SurfaceTool` + `Curve3D` (2m sag between poles).
- `ExecuteGenerateBlocker` — 5m wide invisible collision strip at y=1.5 (collision layer 31, surface `"Border"`).
- `ExecuteGenerateBorder` — full-height 200m wall (collision layer 32) sealing the box.
- `ExecuteMergePoles` — merges all pole meshes into one draw call for perf.

All of these are `@tool` setters — run once in the editor, don't touch at runtime.

## Killbox (`Killbox.gd`)

`extends Area3D`. The safety net at the bottom of every level. Checks overlaps every 2 seconds.

- `HandleItem(pickup)`:
  - Shelter → teleport the item back to the player's inventory via `interface.Create(slotData, inventoryGrid, true)`.
  - Outdoor → `queue_free()` (dropped items just disappear).
- `HandleController(controller)`:
  - Shelter → teleport back to the Transition's `spawn`, rotated 180°.
  - Outdoor → teleport to a random `AI_WP` waypoint, or `(0, 2, 0)` if none.

`PlayTeleport()` plays `audioLibrary.UITeleport`.

## Area (`Area.gd`)

```gdscript
extends Area3D
class_name Area
@export var type: String
```

Generic tagged trigger. Various systems scan for these — e.g. `Character.Temperature()` checks for `"Shelter"`/`"Heat"` area overlaps.

## Optimizer (`Optimizer.gd`)

`@tool extends Node3D`. Editor-time mesh merger for static scenery.

- `ExecuteMerge()` walks children, finds each `MeshInstance3D` named `Mesh`/`LOD0`, and merges surfaces keyed by material (one draw call per unique material). Also merges `Collider_R` (render collision) and `Collider_P` (pathfinding collision) by surface type (`Generic/Wood/Metal/Concrete/Rock`) — surface strings propagate onto the merged `StaticBody3D`'s `Surface.gd` instance.
- Runtime `_ready()`: if the node is hidden and disabled (pre-merged), `queue_free()` itself. If not cleared, pushes a warning.
- Helpers: `ExecuteSort` (natural-sort children), `ExecuteReindex` (`Name_2`, `Name_3` style).

Collision layer conventions used: render colliders on layer 5, pathfinding colliders on layer 6, border blocker on layer 31, border wall on layer 32.

## DynamicAmbient (`DynamicAmbient.gd`)

`extends Node3D`. Random distant ambient audio (birds, wolves, distant jets). Lives in each outdoor map.

### Pools (hardcoded)
```
area05Day    — crow, cuckoo, birdAlarm, blackbird, chaffinch, crane, fox,
               goshawk, jackdaw, magpie, plover, rooster, seagull, wren,
               mosquitos, woodBreak
area05Night  — crow, crane, fox, owl, treeCreak, windGust, woodpecker,
               woodpidgeon, mosquitos, woodBreak
borderZoneDay   — bear, crow, birdAlarm, crane, dog, woodBreak, windGust,
                  car, fighterJet, helicopter, tank, rumble
borderZoneNight — + owl, treeCreak, wolf
vostokDay     — fighterJet, helicopter, tank, artillery, explosion, rumble, hit
vostokNight   — + treeCreak, windGust, wolf
```

### Runtime

`_physics_process(delta)` decrements `dynamicTimer`. When ≤0:
- Skip if indoors, in Intro, or winter (`Simulation.season == 2`).
- Spawn `audioInstance3D` at `playerPosition + (±100..200, 0, ±100..200)` (diagonal in all 4 quadrants).
- Pick from the pool matching `map.mapType` + `gameData.TOD` (`4 = Night`).
- `PlayInstance(event, 250, 400)` — 250m attenuation distance, 400m max.
- Reroll `dynamicTimer = randf_range(1, 120)`.

## Spawner (`Spawner.gd` / `SpawnerData.gd` / `SpawnerChunkData.gd` / `SpawnerSceneData.gd`)

`@tool extends Node3D`. Procedural vegetation / prop scatter. Editor-time, but `SpawnerSceneData.runtime = true` flips it to runtime generation.

### `SpawnerData` base

```gdscript
@export var area = 600.0              # square terrain extent
@export var normals = true            # align to face normal
@export var density = 0.01            # close density (per-face)
@export var farDensity = 0.01         # |pos| > 200m density
@export var minDistance = 1.0         # poisson-disk spacing
@export var minScale / maxScale
@export var perimeter: int
@export_enum perimeterType            # Off / Simple / Double / Super
```

- `SpawnerChunkData` adds a `mesh: Mesh` — all candidates baked into one combined mesh.
- `SpawnerSceneData` adds `scenes: Array[PackedScene]` + `runtime: bool` — candidates become scene instances.

### Generation

`ExecuteGenerate()`:
1. Read `Blocker`-tagged rect masks (authored exclusion zones).
2. `MeshDataTool` from `surface`. For each face:
   - Skip faces beyond `area/2`.
   - Pick density (near vs far based on |xz| > 200).
   - Spawn N candidates via `RandomBarycentric(v0, v1, v2)`.
3. `PoisonFilter(candidates, minDistance)` — uniform-ish scatter.
4. For each accepted candidate: skip if inside any blocker rect, otherwise place per-type.

Typical use: `Terrains/<Name>/Spawner_*.tscn` children of the outdoor map.

## Gotchas

- Outdoor maps are `.scn` (binary). Don't try to diff them — regenerate from their source `.tscn` in Godot if you need to inspect.
- The Border system (`Border.gd`) uses specific collision layers (31, 32). If your mod adds physics objects, don't reuse those layers.
- `DynamicAmbient` swallows everything when `Simulation.season == 2` — winter scenes are intentionally silent except for howl wind. If you want winter ambient, patch `PlayDynamicAudio`.
- `Optimizer._ready()` `queue_free`s itself when `clear = true` and the node is already hidden. Don't rely on it existing at runtime.
- `World` is `@tool` — its `_ready()` has `if Engine.is_editor_hint()` gates; skip those if subclassing.
