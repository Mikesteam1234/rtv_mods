# Player System

Everything the player controls, lives under `Core` in the level scene. Core is instanced from `res://Scenes/Core.tscn` by every gameplay map.

## Scene layout (from `Core.tscn`)

```
Core (Node3D)
├── Camera (Camera3D, script: Camera.gd)
│   ├── Manager (Node3D, script: RigManager.gd) — the weapon-rig host
│   ├── Placer (Node3D, script: Placer.gd) — furniture/item placement preview
│   ├── Interactor (RayCast3D, script: Interactor.gd) — "what am I looking at"
│   ├── Flashlight (Node3D, script: Flashlight.gd) — World + FPS light
│   ├── Flash (Node3D) — muzzle flash light pair (World + FPS)
│   └── LOS (MeshInstance3D + StaticBody3D) — tagged in group "Player" for AI LOS checks
├── Controller (CharacterBody3D, script: Controller.gd, group "Player")
│   ├── Character (Node3D, script: Character.gd)
│   ├── Stand (CollisionShape3D)
│   ├── Crouch (CollisionShape3D)
│   ├── Raycasts/Above/Below/Left/Right — environmental probes
│   ├── Pelvis (Node3D)
│   │   └── Riser (Node3D, script: Riser.gd)
│   │       └── Head (Node3D)
│   │           └── Bob (Node3D) — headbob translation
│   │               └── Impulse (Node3D, script: Impulse.gd) — jump/land/crouch impulses
│   │                   └── Damage (Node3D, script: Damage.gd) — hit-reaction camera shake
│   │                       └── Noise (Node3D, script: CameraNoise.gd) — perlin sway
│   │                           └── Camera (Camera3D) — the actual view camera
│   └── Detector (Area3D) — proximity trigger (shelter/heat/workbench)
└── ... (UI, Audio, Tools — see ui-system.md / audio-system.md)
```

Two `Camera3D`s: the one under `Controller/.../Noise` is the *source* (animated, bobbing). `Core/Camera` is the *render* camera and is a separate `Camera.gd` that interpolates toward the source every frame — this decouples render rate from physics tick. `interpolate = true` is the smooth path; `interpolate = false` (`Follow()`) is rigid.

## Controller (`Controller.gd`, 738 lines)

`extends CharacterBody3D, class_name Controller`. The physics/movement brain.

### Key members

- Movement speeds: `walkSpeed = 2.5`, `sprintSpeed = 5.0`, `crouchSpeed = 1.0`, `swimSpeed = 2.0`, `lerpSpeed = 5.0`, `inertia = 1.0`.
- Headbob constants: `headbobWalkSpeed = 10.0`, `headbobSprintSpeed = 20.0`, `headbobCrouchSpeed = 8.0`, `headbobSwimSpeed = 6.0`, plus matching `*Intensity` values.
- Jump: `jumpVelocity = 7.0`, `jumpControl = 8.0`, `gravityMultiplier = 2.0`.
- Impulse system: `jumpImpulse`, `landImpulse`, `crouchImpulse`, `standImpulse` (plus their `*Timer`) feed `Impulse.gd` via `gameData`.
- `sprintToggle: bool` — toggle vs. hold (driven by `gameData.sprintMode`).
- `gravity = ProjectSettings.get_setting("physics/3d/default_gravity")`.
- `fallStartLevel`, `fallThreshold = 5.0` — damage threshold on landing.

### Processing pipeline (`_physics_process`)

```gdscript
if gameData.isCaching: return
if gameData.isFlying: Fly()
elif gameData.isSwimming: Swim(delta); Headbob(delta)
else:
    SurfaceDetection(delta)
    Movement(delta)
    Inertia(delta)
    Gravity(delta)
    Falling()
    Landing(delta)
    Crouch(delta)
    Jump(delta)
    # ... more helpers in the rest of the file
```

### Mouse look (`_input`)

Applies rotations based on `gameData.isScoped` / `isAiming` / idle, with separate sensitivities (`scopeSensitivity`, `aimSensitivity`, `lookSensitivity`) and an inversion toggle (`gameData.mouseMode == 2`). Clamps `head.rotation.x` to `±90°`.

The head chain rotates on `head` (pitch); the body on `self` (yaw). Headbob translates `bob`. Lean rotates `riser` on Z and offsets `position.x` (see below).

## Character (`Character.gd`, 517 lines)

`extends Node3D`. Per-physics-tick vitals simulation. Reads and writes `gameData` directly.

### Subsystems (each its own `_physics_process` helper)

- `Health(delta)` — applies per-condition bleed: bleeding/fracture/burn take `delta/5`, rupture and headshot take a full `delta` per second. Any condition drains health. `<= 0` triggers `Death()`.
- `Stamina(delta)` — body + arm stamina.
- `Energy(delta)` — decays `delta/30`, transitions to/from `starvation` at zero.
- `Hydration(delta)` — decays `delta/20`, transitions to/from `dehydration`.
- `Mental(delta)` — gains `delta/4` while near heat; otherwise decays `delta/5` when any physical condition is active, or `delta/35` baseline. `<= 0` → `insanity`.
- `Temperature(delta)` — winter+submerged is `-delta * 8.0 * insulation`; shelter/summer/heat replenishes. Zero → `frostbite`.
- `Cat(delta)` — starves the cat when away, gains when fed.
- `Oxygen(delta)` — drops while submerged; zero → drowning damage.
- `BurnDamage(delta)` — if `gameData.isBurning`.
- `Clamp()` — clamps each vital to 0..100.

Fields: `heavyGear: bool`, `insulation: float` — driven by equipped clothing `ItemData.insulation`. Hard-coded refs: `$"../../UI/Interface"`, `$"../../Camera/Manager"`, `$"../../Audio"`.

## Inputs (`Inputs.gd`, 320 lines)

`extends Control`. The settings UI for remapping. Hosts the `inputs` dictionary — the canonical list of action names the game binds:

- Movement: `forward`, `backward`, `left`, `right`, `crouch`, `jump`, `sprint`, `lean_L`, `lean_R`
- Weapons: `primary`, `secondary`, `knife`, `grenade_1`, `grenade_2`, `weapon_high`, `weapon_low`, `aim`, `canted`, `fire`, `reload`, `ammo_check`, `firemode`, `inspect`, `prepare`, `insert`
- Interaction: `interact`, `place`, `decor`, `flashlight`, `nvg`, `laser`
- Plus `item_rotate`, `item_drop`, `item_transfer`, `item_equip`, `escape`, `interface`, `prepare_throw`, `throw`, `slash`, `stab`, `context`, `settings`, `ragdoll` (debug).

Preferences are written via `Preferences.gd` static `Save/Load`. Reads: `gameData.mouseMode/sprintMode/leanMode/aimMode`.

## Camera (`Camera.gd`)

`extends Camera3D, class_name Camera`. The render camera. Every physics tick:

1. Updates `gameData.cameraPosition = global_position`.
2. Bails if `gameData.isCaching`.
3. `Interpolate(delta)` or `Follow()` — tracks the source camera under the head rig.
4. `FOV(delta)`, `DOF(delta)` — smooth lerp from `fov`/`near`/`far` toward the source `Camera3D`'s.

`translateSpeed = 4.0`, `rotateSpeed = 4.0`. Toggle `interpolate = false` for snap tracking. FOV driven by `gameData.baseFOV`/`aimFOV` and `gameData.isScoped`.

## Lean (`Lean.gd`)

`extends Node3D`. Attached to `Riser`. `leanAngle = 15°`, `leanOffset = 0.2`m, `leanSpeed = 5.0`.

Two modes via `gameData.leanMode`:
- **1 (hold):** `Input.is_action_pressed("lean_L"/"lean_R")`.
- **2 (toggle):** uses `leanLToggle`/`leanRToggle`; pressing the opposite side while toggled cancels.

Respects `gameData.leanLBlocked` / `leanRBlocked` (raycasts against walls). Bails if `gameData.freeze || isFlying`.

## Riser / Bob / Impulse / Damage / Noise / CameraNoise

Each is a thin `Node3D` in the head chain, each with its own script. They compose: `Riser` (height change for stand/crouch), `Bob` (walk bob), `Impulse` (discrete pulses on jump/land/stand/crouch), `Damage` (shake on hit), `Noise`/`CameraNoise` (perlin-style sway). Override any independently; each reads from `gameData` flags.

## Interactor (`Interactor.gd`)

`extends RayCast3D`. The "what am I looking at" probe. Surfaces tooltips, invokes `Interact()` methods on targets (`Transition`, `Furniture`, `Pickup`, `Door`, `Switch`, `Cat`, etc). Drives `gameData.tooltip`, `gameData.interaction`, `gameData.transition`, `gameData.isPlacing`.

## Flashlight (`Flashlight.gd`) / Headlamp / NVG

- `Flashlight.gd` (`Node3D`) toggles two lights: `World` (SpotLight3D, for the scene) + `FPS` (OmniLight3D, for the player's own view). Has `Load()` to restore from save.
- `Headlamp.gd` — similar pattern but attached to a helmet slot.
- `NVG.gd` — `Control` UI, green-tinted overlay plus toggles a higher exposure. Has its own `Load()`.
- `Laser.gd` — weapon laser toggle.

## Surface / Footsteps

`Surface.gd` (`class_name Surface`) tags a mesh's physical surface type: `"Grass"`, `"Dirt"`, `"Asphalt"`, `"Rock"`, `"Wood"`, `"Metal"`, `"Concrete"`, `"SnowSoft"`, `"SnowHard"`, `"Water"`. `Controller.SurfaceDetection()` reads this, writes `gameData.surface`, and `Audio.gd` plays the matching `footstep*` / `footstep*Land` events from `AudioLibrary`.

## Death

`Loader.LoadScene("Death")` transitions to `Death.tscn` (Control-only scene with `Death.gd`). Triggered by `Character.Death()` when `gameData.health <= 0 && !isDead && !decor`.

## Gotchas when overriding

- `Controller` clears `gameData.isFlying` in `_ready()` — if you override and skip `super()`, flycam breaks.
- `Character._physics_process` runs *every tick*; don't add expensive logic without gating on `Engine.get_physics_frames() % N`.
- Hardcoded paths: `Character.gd` looks up `$"../../UI/Interface"`, `$"../../Camera/Manager"`, `$"../../Audio"`. Move the nodes and it breaks silently.
- `Controller` calls `Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)` in `_ready()` — fighting this from an override creates jitter.
