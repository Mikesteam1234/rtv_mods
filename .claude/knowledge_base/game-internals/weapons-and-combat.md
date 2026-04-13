# Weapons & Combat

Weapons live as scenes under `res://Items/Weapons/<Name>/<Name>.tscn` plus a rig variant `<Name>_Rig.tscn`. Same split for knives (`Items/Knives/*/`), grenades (`Items/Grenades/`), fishing rods (`Items/Fishing/`), instruments (`Items/Instruments/*/*_Rig.tscn`).

## RigManager (`RigManager.gd`, 445 lines)

`extends Node3D`. Lives at `Core/Camera/Manager`. The host that equips/unequips a rig into the camera rig, reads equipment slots from the `Interface`, and listens for input to draw/holster.

### Preloads
- `muzzleFlash`, `muzzleSmoke` (`res://Effects/Muzzle_*.tscn`)
- `casingPistol`, `casingRifle`, `casingShotgun` (`res://Effects/Casing_*.tscn`)
- `hitDefault`, `hitBlood`, `hitKnife` (`res://Effects/Hit_*.tscn`)
- Default clothing materials for arms/gloves.

### Equipment slot references

Wired from `interface.equipmentUI` by child index (set in `_ready()`):
```
primarySlot   = equipmentUI.get_child(1)
secondarySlot = equipmentUI.get_child(2)
knifeSlot     = equipmentUI.get_child(3)
grenade1Slot  = equipmentUI.get_child(4)
grenade2Slot  = equipmentUI.get_child(5)
torsoSlot     = equipmentUI.get_child(10)
handsSlot     = equipmentUI.get_child(14)
```

If you rearrange equipment children you break weapon drawing. The slot order is effectively API.

### Per-tick logic

- `Malfunction()` every 20 physics frames (`Engine.get_physics_frames() % 20`).
- Blocks input while busy: `isInspecting || isReloading || isInserting || isChecking || isClearing || isSwimming || isSubmerged`.
- Draw actions: `primary`, `secondary`, `knife`, `grenade_1`, `grenade_2` keybinds call `DrawPrimary/Secondary/...` with the slot's `slotData`.
- `LoadPrimary/LoadSecondary/LoadKnife/LoadGrenade1/LoadGrenade2` — resumption paths called by `Loader.LoadCharacter()`.

## WeaponRig (`WeaponRig.gd`, 1299 lines — largest gameplay script)

`extends Node3D, class_name WeaponRig`. One per weapon scene. Bound to a `WeaponData` resource.

### Exports (editor-populated)
- **References:** `data` (`WeaponData`), `animator` (`AnimationTree`), `animations` (`AnimationPlayer`), `skeleton` (`Skeleton3D`), `recoil`, `ejector`, `muzzle`, `raycast` (`RayCast3D`), `collision`, `arms` / `cartridge` / `magazine` (`MeshInstance3D`), `bullets`, `attachments`.
- **Dynamic rig:** `dynamicSlide`, `dynamicSelector`, `dynamicHammer`, `slideOptic`, `slideIndex`, `selectorIndex`, `hammerIndex`, `backSightIndex`, `frontSightIndex` — indices into the skeleton bones that animate per-frame from weapon state.

### Runtime state
- `fireRate / fireTimer / fireImpulse / fireImpulseTimer`
- `slideLocked / slideValue / slideOffset`
- `selectorValue / initialSelectorRotation / selectorRotation`
- `hammerLocked / hammerValue`
- `activeOptic`, `activeMuzzle`, `aimOffset`, `aimPosition`, `opticOffset`, `muzzlePosition`
- `reloadPressed`, `reloadHoldTimer` — tap vs. hold reload
- `zoomLevel`, `ocularOpacity`, `reticleSize`

`_ready()` pulls the active slot via `rigManager.primarySlot` or `secondarySlot`, fetches the interface at `/root/Map/Core/UI/Interface`, sets `animator.active = true`, clears the bullet placeholders, and exposes `data.weaponAction` on `gameData.weaponAction`.

## WeaponData (`WeaponData.gd`)

`extends ItemData, class_name WeaponData`. All tunable numbers live here.

- **Action:** `weaponType` (category string), `weaponAction` (animation layer key).
- **Audio (custom per-weapon):** `fireSemi`, `fireAuto`, `fireSuppressed`, `charge`, `reloadEmpty`, `reloadTactical`, `magazineAttachEmpty/Tactical`, `magazineDetach`, `ammoCheck`, `tailOutdoor`, `reload`, `insertStart/End/insert`.
- **Audio (modular tail):** `tailIndoor`, `tailIndoorSuppressed`, `tailOutdoorSuppressed`.
- **Caliber:** `ammo: ItemData`, `caliber: String`, `casing: enum {None, Pistol, Rifle, Shell}`.
- **Fire:** `damage`, `penetration`, `fireRate`, `magazineSize`.
- **Recoil:** `kick`, `kickPower`, `kickRecovery`, `verticalRecoil`, `horizontalRecoil`, `rotationPower`, `rotationRecovery`.
- **Rig animation:** slide/selector/hammer direction + extents + speed/lock, fold-sights, `useMount`, `nativeSuppressor`.
- **Handling poses:** `lowPosition/Rotation`, `highPosition/Rotation`, `aimPosition/Rotation`, `cantedPosition/Rotation`, `inspectPosition/Rotation`, `collisionPosition/Rotation`.

## Handling (`Handling.gd`)

`extends Node3D`. Per-rig script that interpolates the rig's local transform toward the pose stored in `data` based on `gameData` flags.

- `handlingSpeed = 7.5` (lerp rate)
- `aimToggle`, `canted`, `offset`
- `_ready()`: `data = owner.data`; `collision = owner.collision`; seed `position = Vector3(0, -0.5, -0.5)`.
- `_physics_process`:
  - `WeaponData` → `WeaponPosition()` (reads `weapon_high`/`weapon_low` inputs → `gameData.weaponPosition`) + `WeaponHandling(delta)` (lerp toward `targetPosition`/`targetRotation`).
  - `KnifeData / GrenadeData / FishingData` → `BasicHandling(delta)` (simpler pose).

The caller (rig scripts) writes `targetPosition`/`targetRotation` from `WeaponData.aimPosition` etc., according to `gameData.isAiming`/`isCanted`/`weaponPosition`.

## Recoil (`Recoil.gd`) / Sway (`Sway.gd`) / Tilt (`Tilt.gd`)

Siblings in the rig hierarchy that layer per-shot impulses, idle sway, and aim tilt onto the rig. Driven by `WeaponData.kick*` and `*Recoil` values plus input state.

## Optic (`Optic.gd`)

`@tool extends Node3D`. Optic scopes — attached to rails.
- `attachmentData: AttachmentData`, `reticle: Material`, `secondary: Node3D`
- PIP-capable scopes: `mesh`, `viewport`, `camera`, `PIP` material, `mask`, `maskIndex` (which layer mask to sample).
- Abilities: `railMovement`, `slideFollow`. Rail bounds: `minPosition`, `maxPosition`.
- Editor-time `calculate` button auto-fills `defaultPosition`.

## MuzzleFlash (`MuzzleFlash.gd`)

`extends OmniLight3D, class_name Flash`. Used both for weapon flashes and spawned hit lights.

## GrenadeRig (`GrenadeRig.gd`)

`extends Node3D`. Separate throw modes:
- `grenade_throw_high` / `grenade_throw_low` input pair drives `highPrepared` / `lowPrepared` prepare-then-release.
- Exports `throwPoint: Node3D`, `throw: PackedScene` (the thrown grenade scene), `handle: PackedScene` (detached spoon).
- Animator conditions: `Throw_High_Start`, `Throw_High_End`, `Throw_High_Reset`, plus Low equivalents.
- On throw: instances `throw` at `throwPoint`, applies velocity, plays `grenadeThrowLow/High`, writes `gameData.isFiring = false` etc.

Grenades live as `RigidBody3D` scenes (`Grenade.gd, class_name Grenade`) with explosion (`Explosion.gd`, spawns `Fire.gd` hazards and damage volumes).

## KnifeRig (`KnifeRig.gd`, 235 lines)

`extends Node3D, class_name Knife`. Melee combat.
- `slashTime = 0.4`, `stabTime = 0.6`, combo state via `canCombo`/`attack`/`comboTimer`/`comboTime = 0.5`.
- Two inputs: `slash` (light) / `stab` (heavy). Raycast (`raycast`) + collision raycast for contact detection.
- Knife rigs also support `inspect` toggling `gameData.isInspecting`.

`KnifeData` (extends `ItemData`) holds melee stats (damage + audio). `KnifeHandling.gd` is the pose interpolator equivalent to `Handling.gd` for knives.

## FishingRig (`FishingRig.gd`, 293 lines)

Cast/reel/hook mini-game. Spawns a `Lure` (`RigidBody3D, class_name Lure`) on cast. `Fish` / `FishPool` interact with the lure for bites. `FishingData` (extends `ItemData`) stores rod stats.

## Inspect (`Inspect.gd`, 393 lines)

`extends Control, class_name Inspect`. Holds item examination UI (rotate, zoom). `gameData.isInspecting` toggles it; `inspectPosition` tracks stage.

## Hit / Damage / Hitbox chain

### Raycast pipeline
1. `WeaponRig` fires a `RayCast3D` stored in `WeaponData.ammo` → reads hit info.
2. The hit point spawns an effect scene from `Effects/`:
   - `Hit_Default.tscn` (wraps `Hit.gd`) for world surfaces
   - `Hit_Blood.tscn` for `AI` hits
   - `Hit_Knife.tscn` for melee
3. `Hit.gd` plays the surface-specific impact sound through `AudioInstance3D` using `AudioLibrary.hitGrass/Dirt/...` tables. Surface mapping via `Surface.gd` on the target mesh.
4. `ParticleInstance.gd` drives the impact VFX node.
5. Tween fades the `Decal` over 10 + 2 seconds then `queue_free()`.

### Hitbox / Damage
- `Hitbox.gd` (`class_name Hitbox`) — one per AI body part. `type: String` ∈ `"Head"`, `"Torso"`, `"Leg_L"`, `"Leg_R"`.
- `ApplyDamage(damage)`: head = 100 (instant kill, also clears active voice), torso = full damage, legs = half damage. Delegates to `owner.WeaponDamage(type, finalDamage)` — i.e. `AI.WeaponDamage()`.
- `Damage.gd` (on player head chain) — camera shake / red overlay when player takes a hit.

## Explosion (`Explosion.gd`) / Fire (`Fire.gd`)

- `Explosion.gd` (`Node3D`) — spawns on grenade or mine detonation. Applies radius damage, spawns `Fire` for incendiary variants, plays explosion tail from `AudioLibrary.grenadeExplosion*`.
- `Fire.gd` — fire hazard volume. Applies `isBurning` to anything in the `Player` or `AI` group on contact.
- `Mine.gd` (`class_name Mine`) — proximity trigger + kill volume (used in the Minefield level).

## Cartridge / Ammo

- Ammo items live under `Items/Ammo/<Caliber>/`. Each caliber folder contains `.tres` ammo variants (FMJ, AP, HP, etc).
- `WeaponData.ammo: ItemData` points at the default type.
- Magazine items are `.tscn` + `.tres` under each weapon's folder (e.g. `Items/Weapons/AK-12/Magazine_AK-12.tres`). They carry their own storage via `SlotData.storage`.
- `Cartridges/` (under `Items/Ammo`) holds the physical cartridge pickup scene used for manual loading.

## Malfunction / Jam

`gameData.jammed` flag is driven by `WeaponRig.Malfunction()` / `RigManager.Malfunction()`. Rolled every 20 physics frames. HUD shows `$Malfunction` node while `jammed`. Player clears via the clear-action input (`Actions.gd`).
