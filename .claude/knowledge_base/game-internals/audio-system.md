# Audio System

Road to Vostok uses four audio buses (`Master`, `Ambient`, `SFX`, `Music`) and a resource-driven "event" model for every in-game sound. The canonical event catalog is `AudioLibrary.tres`.

## Buses

Declared in `default_bus_layout.tres`. Bus index convention:
- 0 = **Master** — global output. Effect[0] = LowPass (indoor muffle), effect[1] = Amplify (fade).
- 1 = **Ambient** — nature/birds/wind. Effect[0] = LowPass (indoor muffle), effect[1] = Amplify.
- 2 = **SFX** — gunshots, impacts, UI.
- 3 = **Music** — background music + casette. Effect[0] = Amplify (duck when casette plays).

Manipulated directly by name in `Audio.gd`, `Loader.gd`, `Settings.gd`. Indexes are hardcoded — moving a bus breaks everything.

## AudioEvent (`AudioEvent.gd`)

```gdscript
extends Resource
class_name AudioEvent

@export var audioClips: Array[AudioStreamWAV]
@export_range(-20.0, 20.0, 1.0) var volume = 0.0
@export var randomPitch = false
```

The **atom** of sound design — a clip pool + volume + optional pitch randomization. Everything else picks one `audioEvent` and plays it through an instance scene.

## AudioInstance2D (`AudioInstance2D.gd`)

`extends AudioStreamPlayer`. Self-freeing non-positional player.

```gdscript
func PlayInstance(audioEvent: AudioEvent):
    stream = audioEvent.audioClips.pick_random()
    if audioEvent.randomPitch:
        volume_db = randf_range(audioEvent.volume - 1.0, audioEvent.volume)
        pitch_scale = randf_range(0.9, 1.0)
    else:
        volume_db = audioEvent.volume
    play()

func _process(_delta):
    if !is_playing(): queue_free()
```

Use pattern everywhere:
```gdscript
var audio = audioInstance2D.instantiate()
some_node.add_child(audio)
audio.PlayInstance(audioLibrary.pickup)
```

## AudioInstance3D (`AudioInstance3D.gd`)

`extends AudioStreamPlayer3D`. Same pattern + positional params:

```gdscript
func PlayInstance(audioEvent, unitSize, maxDistance):
    stream = audioEvent.audioClips.pick_random()
    unit_size = unitSize
    max_distance = maxDistance
    # ... volume + pitch as above
```

Typical call: `audio.PlayInstance(audioLibrary.hitGrass, 5, 50)` (5m unit size, 50m max).

## AudioLibrary (`AudioLibrary.gd`)

`extends Resource, class_name AudioLibrary`. Lives at `res://Resources/AudioLibrary.tres`, preloaded by every script that plays sound.

### Field groups (~200 events total)

- **Character:** `damage`, `impact`, `armor`, `armorBreak`, `death`.
- **Medical:** `indicator`, `overweight`, `starvation`, `dehydration`, `bleeding`, `fracture`, `burn`, `insanity`, `frostbite`, `rupture`, `headshot`.
- **Doors:** `doorWood`, `doorMetal`, `doorUnlock`.
- **Interaction:** `pickup`, `equip`, `unequip`, `transition`, `flashlight`, `radio`, `firemodeSemi/Auto`, `ignite`, `extinguish`, `container`, `switch`, `sleep`.
- **UI:** `UIClick`, `UIEquip/Unequip/Drop/Attach/Armor/Error/Stack/Load/Teleport`, `UICasettePlay/Stop`, `UIFurniture`, `UITraderOpen/Close/Trade/Reset/Task`.
- **Malfunctions:** `malfunction`, `malfunctionClearPistol`, `malfunctionClearRifle`.
- **Bullets:** `bulletCrack`, `bulletFlyby`, `hitGeneric/Grass/Dirt/Asphalt/Rock/Wood/Metal/Concrete/Target/Water/SnowSoft/SnowHard`.
- **Footstep:** `footstep<Surface>` and `footstep<Surface>Land` pairs for Generic/Grass/Dirt/Asphalt/Rock/Wood/Metal/Concrete/SnowSoft/SnowHard/Water.
- **Movement:** `movementCloth`, `movementGear`.
- **Water:** `waterGasp`, `waterDive`, `waterSurface`, `swimSurface`, `swimSubmerged`.
- **Inspect:** `inspectStart/Rotate/End`.
- **Ammo:** `ammoLoad`, `ammoLoadInstant`.
- **Ragdoll:** `ragdoll`.
- **Airdrop:** `airdropRelease`, `airdropBounce`.
- **Casings:** `casingDrop<Soft/Hard/Wood>`, `shellDrop<Hard/Soft>`.
- **Fishing:** `rodThrowStart/Reset/End`, `rodReelEnd`, `rodHooked`, `rodCatch`, `lureImpact<Water/Generic>`.
- **Knives:** full set — draw/holster/slash/stab/throw/inspect + bounce/stick/hit per surface (soil/wood/metal/flesh).
- **Explosions:** `explosionTinnitus`, `explosionMedium<Close/Near/Far/Debris>`.
- **Grenades:** throw prep/low/high, pin/handle, bounce per surface, explosion indoor/outdoor × close/near/far + tinnitus.

Surface-event naming mirrors `Surface.gd` strings — `Controller.SurfaceDetection()` picks the matching footstep.

## Audio (`Audio.gd`)

`extends Node3D`. Lives at `/root/Map/Core/Audio`. The per-player audio state brain.

### Children
```
Audio
├── Music          (AudioStreamPlayer, Music bus)
├── Breathing      (AudioStreamPlayer)
├── Heartbeat      (AudioStreamPlayer)
├── Suffering      (AudioStreamPlayer)
└── Suffocating    (AudioStreamPlayer)
```

### Music clip banks (exports)
`area05: Array[AudioStreamMP3]`, `borderZone`, `vostok`, `shelter` — plus an index (`*ClipOrder`) for sequential picks.

### `_physics_process` pipeline
- `Indoor(delta)` — when `gameData.indoor`: sets `ambientLowPass.cutoff_hz = 2000` (muffle), fades rain/snow VFX distance-fade to `(10, 20)`; outdoors resets to `20000 / (0, 10)`. Lerp rate `delta * 2.0`.
- `Breathing(delta)` — fades in when `bodyStamina < 50`.
- `Heartbeat(delta)` — fades in when `health < 10` OR (`isSubmerged && oxygen < 50`).
- `Suffering(delta)` — while `isBurning`.
- `Suffocating(delta)` — while `isSubmerged && oxygen < 25`.
- `Music(delta)`:
  - Ducks music bus (`musicAmplify.volume_db` toward `-80`) while casette is playing with `casetteOverride`.
  - Picks next clip when `music` stops, based on `gameData.musicPreset`:
    - `1` = Off
    - `2` = Dynamic (match `mapType` — Shelter/Area 05/Border Zone/Vostok)
    - `3..6` = Force Shelter/Area 05/Border/Vostok regardless of map.
  - `GetRandomXClip()` (used) vs `GetNextXClip()` (sequential, available but unused).

### Bus effect handles
```
masterLowPass   = AudioServer.get_bus_effect(0, 0)
ambientLowPass  = AudioServer.get_bus_effect(1, 0)
ambientAmplify  = AudioServer.get_bus_effect(1, 1)
musicAmplify    = AudioServer.get_bus_effect(3, 0)
```

Effect indexes are a contract — don't add new effects in earlier slots.

## CasetteData (`CasetteData.gd`)

```gdscript
extends ItemData
class_name CasetteData
@export var preview: Texture2D
@export var artist: String
@export var tracks: Array[TrackData]
@export var licensed = false
```

`TrackData` is a one-liner resource (title + `AudioStreamOggVorbis`). Casette tapes are collectible items — insert into the player's casette deck via the Interface Tools/Casette panel. Drains battery (`CasetteConsumption` in `Interface.gd`).

## Radio (`Radio.gd`)

`extends Node3D`. Classic scan-the-dial radio placed in levels.
- `audioClips` / `tuningClips` / `transmissionClips` — three pools.
- `active`, `isTuning`, `transmission` — state flags.
- Interaction: while `active`, cycles `tuning` clip → `audio` clip → tuning → ... via `_physics_process` when the current clip ends.
- `Transmission()` flips the next audio pick to the transmission pool (used for story events).

## Television (`Television.gd`)

`extends Node3D`. Toggleable furniture. Swaps `defaultMaterial` ↔ `activeMaterial` on screen mesh surface 1, toggles a `SpotLight3D`, plays looping audio.

## Surface (`Surface.gd`)

```gdscript
extends Node3D
class_name Surface
@export var surface: String
```

Tags physical surfaces — `"Grass"`, `"Dirt"`, `"Asphalt"`, `"Rock"`, `"Wood"`, `"Metal"`, `"Concrete"`, `"SnowSoft"`, `"SnowHard"`, `"Water"`, `"Border"`, `"Generic"`. Read by `Controller.SurfaceDetection()`, `Hit.gd`, `KnifeRig`, `GrenadeRig` to pick matching audio + VFX. `Optimizer.gd` propagates the surface string onto merged static colliders.

## Gotchas

- **Bus index 0/1/2/3 order is load-bearing.** Don't reorder. Adding new buses appended at index 4+ is safe.
- **Effect index contracts:** Master[0]/Ambient[0] = LowPass, Ambient[1] = Amplify, Music[0] = Amplify. Inserting anywhere before those indexes breaks indoor muffle and casette ducking.
- `AudioInstance2D/3D` free themselves as soon as `is_playing()` returns false — don't hold references.
- `randomPitch` only randomizes volume in the range `[volume - 1.0, volume]` (not `[volume - 1, volume + 1]`). It's a quiet-down-randomly pattern, not symmetric.
- The `music.is_playing()` check in `Audio.Music()` skips when the player is mid-track. `UpdateMusic()` is the imperative stop — Settings calls it to reset when the preset changes.
- `Simulation.season == 2` (winter) is checked all over the audio code (`DynamicAmbient` silences, NVG doubles drain, etc). If you need a third season, keep that branch explicit.
