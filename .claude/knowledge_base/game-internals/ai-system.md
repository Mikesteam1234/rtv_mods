# AI System

All hostile/neutral NPCs in Road to Vostok. Agent scenes live under `res://AI/<Name>/AI_<Name>.tscn`. Shared logic is in `Scripts/AI.gd`. Vehicles (BTR, Police, Helicopter) are standalone `RigidBody3D`/`Node3D` classes with their own state machines.

## Agent roster

- `AI/Bandit/AI_Bandit.tscn` — Area05 zone wanderers
- `AI/Guard/AI_Guard.tscn` — BorderZone patrols
- `AI/Military/AI_Military.tscn` — Vostok zone
- `AI/Punisher/AI_Punisher.tscn` — boss, spawned from `B_Pool`
- `AI/Tools/` — authoring helpers: `AI_SP`, `AI_WP`, `AI_PP`, `AI_CP`, `AI_HP`, `AI_VP` (point markers)

## AI (`AI.gd`, 2023 lines — second-largest script after `WeaponRig`)

`extends CharacterBody3D`. No `class_name` (looked up by duck-typing / scene instance). One per agent scene.

### Scene subtree (from `AI_*.tscn`)

```
AI_<Name> (CharacterBody3D, script: AI.gd, group: "AI")
├── Agent (NavigationAgent3D)
├── Detector (Area3D)                   — proximity trigger
├── Raycasts
│   ├── LOS        — line-of-sight to target
│   ├── Fire       — muzzle clearance
│   ├── Below      — grounded check
│   └── Forward    — obstacle probe
├── Poles                                — lateral cover probes
│   ├── AI_Pole_N1 / N2                  — north side
│   └── AI_Pole_S1 / S2                  — south side
├── Gizmo                                — debug visualisation
├── Skeleton3D (Ragdoll.gd)              — physical bones for death
├── AnimationTree + AnimationPlayer
├── Weapons (Node3D)                     — rig instances for hands
├── Backpacks (Node3D)                   — visible backpack models
├── Container (Node3D)                   — loot container activated on death
└── Flash (Flash, OmniLight3D)           — muzzle light
```

### Exports

- **References:** `boss: bool`, `spineData: SpineData`, `eyes: BoneAttachment3D`, `head: PhysicalBone3D`, `weapons: Node3D`, `backpacks: Node3D`, `skeleton: Skeleton3D`, `mesh: MeshInstance3D`, `chest: PhysicalBone3D`, `animator: AnimationTree`, `collision: CollisionShape3D`, `container: Node3D`, `flash: Flash`, `clothing: Array[Material]`.
- **Equipment toggles:** `allowClothing`, `allowBackpacks`.
- **Voice banks:** `idleVoices`, `combatVoices`, `damageVoices`, `deathVoices` (`AudioEvent`).

### State machine

```gdscript
enum State { Idle, Wander, Guard, Patrol, Hide, Ambush, Cover,
             Defend, Shift, Combat, Hunt, Attack, Vantage, Return }
var currentState = State.Idle
```

`ChangeState(state: String)` is the single entry point. It:
1. Sets `speed`, `turnSpeed`, `movementVelocity`, `agent.target_desired_distance`.
2. Picks a target point (`GetPatrolPoint()` / `GetWanderWaypoint()` / `GetCombatWaypoint()` / `GetShiftWaypoint()`). If none, falls back to a simpler state.
3. Calls `ResetAnimator()`, then sets an animator flag (e.g. `animator["parameters/Rifle/conditions/Combat"] = true`). There's a parallel set for `Pistol`.
4. Initialises per-state timers (`guardTimer/Cycle`, `combatTimer/Cycle`, `shiftTimer/Cycle`, `huntTimer/Cycle`, etc.).

`States(delta)` dispatches per-frame to the matching handler (`Guard(delta)`, `Combat(delta)`, `Shift(delta)`, `Hunt(delta)`, `Attack(delta)`, `Return()`, etc).

### Per-tick pipeline

`_physics_process(delta)`:
- `Sensor(delta)` — 10Hz LOS + detection update (`sensorCycle = 0.1`). Writes `playerVisible`, `playerPosition`, `playerDistance3D/2D`, `lastKnownLocation`.
- `FireDetection(delta)` — watches the `Fire` group for suppressed threats (`fireDetectionTime = 5.0`).
- `Movement(delta)` — drives `velocity` from `pathTarget` via `NavigationAgent3D`. `pathCycle = 0.1` throttles pathfinding.
- `Aim(delta)` — rotates the spine bone (`spineData.bone`, default 12) toward `spineTarget`; X/Y/Z offsets read from `SpineData` per state (e.g. `rifleCombatN`).
- `Fire(delta)` — timed burst/semi fire. `FireFrequency()` and `FireAccuracy()` pick cadence + spread. `Selector(delta)` toggles semi/auto.
- `Voices(delta)` — plays `idle/combat/damage/death` `AudioEvent`s, cycled by `voiceCycle = 30.0`. Clears `activeVoice` on death/headshot.
- `States(delta)` — the current state handler.
- `MoveToPoint(origin)` — steer helper used by patrol/wander.

### Activation paths

`AISpawner` calls one of:
- `ActivateWanderer()` — normal roaming
- `ActivateHider()` — from a hide point
- `ActivateGuard()` — patrol loop
- `ActivateMinion()` — boss support
- `ActivateBoss()` — Punisher path

Each sets initial state (typically `Idle` → `Wander`/`Patrol`/`Hide`) and seeds timers.

### Damage

`WeaponDamage(hitbox: String, damage: float)` (line 1484):
- Subtracts `damage` from `health` (starts at 100).
- Sets `impact = true`, resets `impulseTimer` to push the spine based on hitbox:
  - `"Head"` / `"Torso"` → rearward impact centered on `spineTarget - spineData.impact`.
  - `"Leg_L"` / `"Leg_R"` → lateral impact toward that side.
- On `health <= 0`: clears `activeVoice`, plays death voice (unless headshot), calls `Death(gameData.playerVector, 40)`.

`ExplosionDamage(direction)` → `Death(direction, 100)` (always lethal).

`Death(direction, force)`:
- Disables raycasts, detector, animator, collision.
- Activates loot container via `ActivateContainer()`.
- Re-enables collisions on `weapon`/`secondary`/`backpack` so they drop.
- `skeleton.Activate(direction, force)` — see Ragdoll below.
- `AISpawner.activeAgents -= 1`.
- Boss death: `Loader.Message("Boss Killed", Color.GREEN)`.

`Hitbox.gd` (in weapons-and-combat.md) is what actually calls `owner.WeaponDamage(type, finalDamage)`.

## AISpawner (`AISpawner.gd`, 343 lines)

`extends Node3D`. One per level. Manages a pool of pre-instantiated agents and activates them near the player.

### Exports
- `active: bool`
- `zone: Zone { Area05, BorderZone, Vostok }` → chooses `bandit`/`guard`/`military` scene.
- `spawnFrequency: Frequency { Low, Medium, High, Debug }` — controls `spawnTime` reroll ranges (60–120 / 10–60 / 1–10 / 1).
- `spawnDistance = 100` — agents only spawn at points further than this from the player.
- `spawnLimit = 3` — max concurrent agents.
- `spawnPool = 10` — how many pre-instantiated agents live in `A_Pool`.
- `initialGuard: bool` — spawn a guard on `_ready`.
- `initialHider: bool` — 25% chance to spawn a hider on `_ready`.
- `noHiding: bool` — level-wide disable for the Hide state.

### Pools

Two child nodes `A_Pool` and `B_Pool` held at `(0, 1000, 0)`. `CreatePools()`:
- Instantiates `spawnPool` copies of `agent` into `A_Pool`, each `.Pause()`'d.
- Instantiates one `punisher` into `B_Pool` as the boss.
- Each pooled agent gets `AISpawner = self`.

### Spawn points

`GetPoints()` scans groups once at `_ready()`:
```
spawns    ← group "AI_SP"
waypoints ← group "AI_WP"
patrols   ← group "AI_PP"
covers    ← group "AI_CP"
hides     ← group "AI_HP"
vehicle   ← group "AI_VP"
```

(Matches the global-groups list in `project.godot`.)

### Spawn functions

- `SpawnWanderer()` — picks a random `spawns` point further than `spawnDistance` from the player, reparents an agent out of `A_Pool` to `Agents`, calls `ActivateWanderer()`.
- `SpawnGuard()` — picks from `patrols`.
- `SpawnHider()` — picks from `hides`.
- `SpawnMinion(spawnPosition)` — drops an agent at an arbitrary world position (boss summons).
- `SpawnBoss(spawnPosition)` — pulls from `B_Pool`.
- `CreateHotspot(location, relay)` — for each active agent: waits 0.5–2s, forces `ChangeState("Attack")` with `lastKnownLocation = location`, `attackReturn = true`. After 10s, if `relay`, re-aims them at the current player position.
- `DestroyAllAI()` — clears the `Agents` node.
- `AIHide()` / `AIShow()` — freeze/unfreeze all agents (used during transitions).

### Runtime

`_physics_process` ticks `spawnTime` down and rerolls from the `Frequency` table when it hits zero, calling `SpawnWanderer()` while `activeAgents < spawnLimit`.

## AIPoint (`AIPoint.gd`)

Tiny helper attached to point markers:
```gdscript
extends Node3D
var occupied: bool

func _ready():
    for child in get_children():
        if child is Area3D: continue
        child.queue_free()
```
It strips visual children (gizmos/meshes) at runtime, leaving only the Area3D for occupancy tracking. Groups on the scene (`AI_SP`/`AI_WP`/...) are what `AISpawner` actually reads.

## Waypoints (`Waypoints.gd`)

`@tool extends Node3D`. Editor-time grid generator. Exports `terrain: Mesh`, `generate: bool`, `clear: bool`. `ExecuteGenerate()` builds a `25m` grid over a `380m` square, raycasts to the terrain, compares against `MeshDataTool` vertex Y, and instances `res://AI/Tools/AI_WP.tscn` at each valid hit. Run once to pre-populate `AI_WP` nodes.

## SpineData (`SpineData.gd`)

`extends Resource, class_name SpineData`. Per-agent tuning for the spine-IK / impact system.

- `bone = 12`, `weight = 1.0` — which bone to rotate, blend weight.
- `impulse`, `recovery`, `impact`, `recoil` — impact kinematics.
- `pistolDefend` / `rifleDefend` (`Vector3`) — neutral aim offsets.
- `pistolCombatN/S`, `rifleCombatN/S` — combat-state aim offsets (north/south facing).
- `pistolHuntN/S`, `rifleHuntN/S` — hunt-state offsets.
- `pistolAttackN`, `rifleAttackN` — attack-state offsets.

`AI.Aim()` picks the right triple per state × weapon type and lerps the spine toward it.

## AIWeaponData (`AIWeaponData.gd`)

```gdscript
extends Resource
class_name AIWeaponData
@export var itemData: ItemData
@export var position: Vector3
@export var target: Vector3
```

One-liner resource listing a weapon an agent can carry + its mount offsets. Loadouts live as `.tres` arrays on the agent scene.

## Ragdoll (`Ragdoll.gd`)

`extends Skeleton3D`. Sits on the agent's `Skeleton3D` node.

- `DeactivateBones()` / `ActivateBones()` — locks / unlocks all linear + angular axes and `disabled`-toggles each `PhysicalBone3D`'s collision child. Called on `_ready` (off) and by `Activate()`.
- `Activate(direction, force)`:
  - Sets `isActive = true`.
  - `hitBone.linear_velocity = direction * force` — kicks the impacted bone.
  - `ActivateBones()` → awaits 0.5s → `PlayRagdoll()` (spawns `AudioLibrary.ragdoll` at `hitBone`).
- `_physics_process`: counts up to `simulationTime = 10.0`, then `DeactivateBones()`, `owner.Pause()`, `isActive = false`. The body freezes where it fell.

Called from `AI.Death()` via `skeleton.Activate(direction, force)`.

## BTR (`BTR.gd`, 643 lines)

`extends RigidBody3D`. Heavy armoured transport — appears as a roaming threat.

- **State:** `enum State { Idle, Drive, Fast, Suppress, Smoke }`.
- **Exports:** `speed`, `turnSpeed`, `tower/turret/muzzle` (MeshInstance3D), launcher `POD1..POD5`, 8× wheel meshes (FL1/FL2/RL1/RL2/FR1/FR2/RR1/RR2), suspension + tilt tuning (`suspensionRay = 0.65`, `suspensionMovement = 0.3`, `tiltMaxAngle = 10°`).
- **Audio events:** `fireSemi/Auto Near/Close`, `fireFar`, `fireTail`, `smokeLaunch`, `smokeExplode`.
- Dedicated turret `LOS` / `Fire` raycasts. Has its own muzzle flash (`flash: OmniLight3D`) and smoke-screen cartridges (`smokeCartridge`, `smokeShield`).
- Drives along `AI_VP`-group waypoints (same pattern as Police).

## Police (`Police.gd`, 367 lines)

`extends RigidBody3D`. Patrol car. `enum State { Idle, Drive, Boss, Stop, Spawn }`.
- 4 tires, same suspension/tilt model as BTR.
- Audio: `Idle/Drive/Road/Start/End/Door/Music_Exterior/Music_Interior/Siren` — each is an `AudioStreamPlayer3D` child, cross-faded by per-stream volume vars.
- Drives `waypoints: Array[Node3D]` along a `selectedPath`, with `waypointThreshold = 2.0` and an `inversePath` flag for reverse runs.
- Lights: `headlight`, `police` (rotating SpotLight3D).

## Helicopter (`Helicopter.gd`, 321 lines)

`extends Node3D`. Kinematic overflight.
- `enum State { Idle, Flyby, Patrol, Attack }`.
- `flySpeed = 75.0`, `flyHeight = 200.0`.
- Spawns at `(±1000, flyHeight, random)` and faces the origin.
- Rockets: `podL`, `podR`, `rocket: PackedScene`, `rocketLaunch: AudioEvent`.
- Searchlight: `spot` (SpotLight3D) + `omni` (OmniLight3D), swept between `minAngle*`/`maxAngle*` at `searchlightSpeed`. `spotted: bool` latches when LOS catches the player.

## Gotchas

- `AI` has no `class_name` — scripts that need it grep by node group (`"AI"`) or duck-type. Don't rely on `is AI`.
- `AISpawner` holds agents parented under `A_Pool`/`B_Pool` with `process_mode = PROCESS_MODE_DISABLED`-ish `Pause()`. Reparenting them to `Agents` is what "activates" them. Don't free pooled children — the pool count drives the reroll path.
- Spawn-point group names are `AI_SP`/`AI_WP`/`AI_PP`/`AI_CP`/`AI_HP`/`AI_VP`. If you add a new point type, register it in `project.godot`'s `global_group` section first.
- `animator["parameters/Rifle/conditions/*"]` vs `"Pistol/..."` — `ChangeState` always flips both. An override that only touches one desyncs the animator when the agent swaps weapon category.
- `Death()` re-enables collisions on dropped weapons by flipping `process_mode`. If you override a weapon rig and skip `PROCESS_MODE_INHERIT`, weapons vanish when their carrier dies.
