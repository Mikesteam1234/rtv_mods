# UI System

All UI lives under `Core/UI` (in-world) or as sibling Controls on the menu/death scenes. Navigation between panels is managed by `UIManager`. The inventory/trader/crafting/tools root is `Interface` (documented in items-and-loot.md).

## Scene layout (`Core/UI`)

```
Core/UI (Control, script: UIManager.gd)
├── HUD (Control, HUD.gd)
├── Interface (Control, Interface.gd)     ← inventory/crafting/etc
├── Settings (Control, Settings.gd, class_name Settings)
├── NVG (Control, NVG.gd)
├── Effects (Control, Effects.gd)          ← screen-space damage/health shaders
└── Tooltip (Control, Tooltip.gd)          ← item hover panel
```

The menu scene has a different tree (`Menu.gd` on the root) and no `Core`.

## UIManager (`UIManager.gd`)

`extends Control`. At `/root/Map/Core/UI`. The "pause menu / inventory / container / trader" router.

### Onready
- `NVG`, `HUD`, `settings`, `interface` — direct child lookups.

### Input gating

`_input(event)` early-outs on any of:
```
isDead, isCaching, isTransitioning, isReloading, isInserting, isChecking,
isPlacing, isSleeping, (container && isOccupied), isCrafting
```
Then dispatches:
- **`settings` key** (Esc) — toggles Settings panel; if interface is open, acts as Return.
- **`interface` key** (Tab) — toggles inventory; blocked while swimming/submerged/inspecting.
- **`interact`** — when a container or trader is open, closes it.

### Public API (called by containers, traders, etc.)

| Method | Purpose |
|---|---|
| `ToggleInterface()` | Normal inventory open/close. Pauses/unpauses mouse, shows/hides HUD. |
| `ToggleSettings()` | Pauses the tree, shows Settings. |
| `Return()` | Closes whichever is open. |
| `OpenContainer(container)` | Enters container-inspect mode — `interface.container = container`. |
| `OpenTrader(trader)` | Enters trader mode — sets `gameData.isTrading = true`. |
| `UIOpen()` / `UIClose()` | Common hooks: sets `gameData.freeze`, swaps mouse mode between CONFINED and CAPTURED, hides/shows HUD. |

**Mouse mode quirk:** `UIClose()` calls `MOUSE_MODE_HIDDEN` then immediately `MOUSE_MODE_CAPTURED` — the intermediate state is required on some platforms to reacquire capture cleanly.

## HUD (`HUD.gd`, ~150 lines)

`extends Control`. The always-on heads-up layer.

### Children
- `Info/Map` — map name label (`"Highway (Area 05)"`).
- `Info/FPS/Frames` — FPS counter.
- `Tooltip/Label` — world-hover tooltip (different from item-hover Tooltip above).
- `Permadeath` — red overlay for ironman / difficulty 3.
- `Decor`, `Placement`, `Magnet` — build-mode UIs.
- `Magazine`, `Chamber` — ammo-check popups (driven by `UIPosition.gd`).
- `Stats/Vitals`, `Stats/Medical`, `Stats/Oxygen` — bars.
- `Malfunction` — jam warning.
- `Transition/Elements/*` — destination, zone, cost (time/energy/hydration), details (permadeath warning, lock hint).

### `_physics_process`

Throttled 10Hz via `Engine.get_physics_frames() % 10 == 0`. Flips visibility based on gameData flags:
```
tooltip      = interaction && !transition
transition   = transition && !interaction && !isPlacing && !isInserting
oxygen       = isSwimming
permadeath   = permadeath || difficulty == 3
magazine     = isChecking
chamber      = isChecking
malfunction  = jammed
magnet       = magnet
```

`Transition(data)` populates the destination panel when a `Transition` is hovered. Special cases:
- `nextZone == "Vostok"` → red "Permadeath Zone" hint.
- `locked && shelterEnter` → green "Unlock with <keyName>" hint.

`Show*(state)` public toggles called from Settings (Map/FPS/Vitals/Medical/Placement/Decor).

## UIPosition (`UIPosition.gd`)

`extends Node3D`. Tiny helper on weapon-rig magazine/chamber attach points. In `_physics_process`, projects its 3D position to 2D and writes to `HUD.chamber` / `HUD.magazine` positions — that's how ammo-check popups track the real weapon part.

```gdscript
enum Type{Magazine, Chamber}
@export var type = Type.Magazine
```

## Tooltip (`Tooltip.gd`)

`extends Control`. Item-hover detail panel (lives inside Interface). ~340 lines mapping `ItemData`/`SlotData` fields to labels.

### `Reset()` hides every row, then `Update(item: Item)` shows the ones applicable:
- **Always:** `title` (+ "(RIP)" for dead Cat), `rarity` (color-coded), `type`, separator.
- **Condition** (`showCondition`): color-coded (≤25 red, ≤50 yellow, >50 green).
- **Weight** (`item.Weight()`), **Value** (`item.Value()`), both per-instance.
- **Weapon:** `damage`, `penetration` ("Level N"), `caliber`.
- **Armor/Helmet:** `protection` "Level N". Rig with nested armor shows both condition + nested protection.
- **Capacity** (`+Nkg`), **Insulation** (`+N`).
- **Equipment:** `slots` joined with `" / "` (Grenades display "Grenade").
- **Vitals:** `health/energy/hydration/mental/temperature` if `usable`; green for +, red for −.
- **Cures:** icon strip for each medical flag.
- **Nested:** comma-separated attached item display names.
- **Compatible:** for magazines/weapons shows ammo names; carriers append "Armor Plates".

`Info(hoverInfo)` — simpler mode used by non-item hovers (recipes, tasks, events): `title`, `type`, `info` only.

## Settings (`Settings.gd`, class_name Settings)

`extends Control`. Pause-menu settings panel. Also reused on the Menu scene (via `$Settings / UI_Settings`).

### Exports
`HUD`, `interface`, `audio`, `camera` — manually wired per scene.

### Onready (selected)
- **Audio:** `masterSlider`, `ambientSlider`, `musicSlider` → `AudioServer.get_bus_index("Master"/"Ambient"/"Music")`.
- **Music preset:** `Music_Off / Dynamic / Shelter / Area_05 / Border / Vostok`.
- **Camera:** `Interpolate_On/Off`, `FOV_Slider`, `Headbob_Slider`.
- **Mouse:** `Look/Aim/Scope` sliders.
- **Color:** `Exposure/Contrast/Saturation` sliders.
- **Image:** `Sharpness` slider.
- **HUD toggles:** `Map`, `FPS`, `Vitals`, `Medical`, `Placement`, `Decor` — call `HUD.Show*(state)`.
- **Tooltip, PIP, Shadows, Water Reflections** — on/off pairs.
- **Inputs** — `$Settings/Inputs` runs `Inputs.gd` (see player-system.md).

All values are persisted through `Preferences.gd` (see save-system.md).

## NVG (`NVG.gd`)

`extends Control`. Green-tinted night-vision overlay + environment exposure boost.

- Hardcoded: `NVGSlot = interface.equipmentUI.get_child(17)` — equipment child 17 is the NVG slot.
- `Activate()` / `Deactivate()` toggled by the `nvg` input when the slot is non-empty and condition > 0.
- Exposure boost by `NVGData.power`:
  - Low → `tonemap_exposure = 2.0`
  - Medium → `2.5`
  - High → `3.0`
- Tint color from `NVGData.color` applied as shader param `"tint"` on the overlay material.
- `Consumption(delta)` drains condition at `0.05 / 0.1 / 0.2 per second` (Low/Med/High), × 2.0 in winter.
- `ResetCheck()` (10Hz): auto-deactivates if submerged, sleeping, slot empty, or condition 0.
- `Load()` — called by `Loader.LoadCharacter()` to restore active state from save.

## Effects (`Effects.gd`)

`extends Control`. Full-screen shader overlays driven by gameData flags. Updates 30Hz (`physics_frames % 2 == 0`).

| Effect | Trigger | Behavior |
|---|---|---|
| `ImpactEffect` | `gameData.impact = true` | Lerps opacity up to 10.0 fast, then auto-clears `impact` flag when > 5.0. Bullet-impact feedback. |
| `DamageEffect` | `gameData.damage = true` | Lerps to 1.0, clears flag at > 0.5. |
| `HealthEffect` | `gameData.health < 50` | Opacity = `inverse_lerp(100, 0, health)` — intensifies as you bleed out. |
| `SleepingEffect` | `gameData.isSleeping` | Slow lerp in (/ 2 rate), fast lerp out. |
| `SubmergedEffect` | `gameData.isSubmerged` | Hard on/off. |

Materials are preloaded `.tres` shader resources (`MT_Impact/Damage/Health/Sleeping/Submerged`).

## Menu (`Menu.gd`)

`extends Control`. Main menu root. Not under Core.

### Children
`Main` (New/Load/Tutorial/Settings/Roadmap/About/Quit buttons), `Modes` (Difficulty: Standard/Darkness/Ironman × Season: Dynamic/Summer/Winter), `Roadmap`, `Settings`, `About`, `API` (DirectX/Vulkan indicators), `Profiler`, plus toggles (`Log`, `Hardware`, `Intro`, `Music`).

### `_ready()`
1. `get_tree().paused = false`, `Engine.max_fps = 120`, `Simulation.simulate = false`.
2. `gameData.Reset()`, `gameData.menu = true`.
3. `Loader.FadeOut()`, `Loader.ShowCursor()`.
4. `Loader.ValidateID()` — if invalid (hash mismatch), `FormatAll()` + `CreateValidator()` + flashes the Tutorial button green.
5. `Loader.ValidateShelter()` — enables Load button if any shelter save exists.
6. Detects rendering driver (`d3d12` / `vulkan`) and lights the matching API icon.

### Button flow
- **New** → shows `Modes`. `_on_modes_enter_pressed()` → `Loader.NewGame(difficulty, season)` → scene transition (Intro / Cabin / random).
- **Load** → `Loader.LoadScene(Loader.ValidateShelter())`.
- **Tutorial** → `Loader.LoadScene("Tutorial")`.
- **Settings/Roadmap/About/Quit** — panel toggles + `Loader.Quit()`.

## Death (`Death.gd`)

`extends Control`. The death screen (`res://Scenes/Death.tscn`). Three buttons: Load / Menu / Quit.
- Shows permadeath banner + "All save files deleted" hint if `gameData.permadeath`, otherwise "Character died".
- Load disabled if no shelter save survived (permadeath wipes them).

## Loading (`Loading.gd`)

`extends Control`. Shader-compile screen shown on first launch / cache invalidation.
- `LoadingShaders()` — shows the overlay with "Loading shaders..." label.
- `LoadingFinished()` — plays the Fade animation.
- `Hide()` — force-hide.

## Message (`Message.gd`)

`extends Control`. One-shot in-world notification, spawned by `Loader.Message(text, color)` into `Loader/Messages`.
- Fade-in over ~2s (lerp opacity → 255 at `delta * 2`).
- 5s hold.
- Fade-out 5s.
- `queue_free()`.

## Profiler (`Profiler.gd`)

`extends Control`. Dev overlay toggled by `KP_ENTER` (numpad Enter) when not on menu. Calls `RenderingServer.viewport_set_measure_render_time(true)` and shows CPU time, GPU time, FPS, draw calls, triangles, node count, collision pairs. `Basic()` populates just the hardware string for the menu's bottom banner.

## Preferences (`Preferences.gd`)

Static save/load of settings → `user://Preferences.tres`. Called by `Settings.gd` on every slider change and by `Inputs.gd` on rebinds. Survives `Loader.FormatSave()` but is wiped by `Loader.FormatAll()`.

## Gotchas

- `UIManager._input` is the central input router for pause/inventory. If you intercept `settings`/`interface` from a custom autoload, you'll double-toggle.
- `HUD.tooltip` ≠ item Tooltip — there are two tooltip systems. HUD's is the world-interaction tip driven by `gameData.tooltip`; Interface's Tooltip is the item-hover panel driven by `Tooltip.Update(item)`.
- `NVG.NVGSlot = interface.equipmentUI.get_child(17)` — hardcoded child index for the NVG slot. Same gotcha as `RigManager`'s equipment indices (see weapons-and-combat.md).
- `Effects` auto-clears `gameData.impact` and `gameData.damage` after peaking. Don't hold those flags true — the effect goes one-shot.
- Menu's `blocker.mouse_filter = MOUSE_FILTER_IGNORE` is reset to `STOP` in every click handler to prevent double-clicks during the scene change. If you add a button, mirror that pattern.
- `Settings` has no `class_name` conflict — note `class_name Settings` at the top. If your override reuses `Settings` as a global, it will clash.
