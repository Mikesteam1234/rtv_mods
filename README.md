# rtv_mods

Mods and tooling for [Road to Vostok](https://roadtovostok.com/), a Godot-based game.

## Mods

### QuickExit

Skips the exit confirmation dialog on the main menu so the Quit button closes the game immediately. The mod autoloads `Main.gd`, which swaps the base `Menu.gd` script for `MenuOverride.gd` via `take_over_path`, then reloads the current scene.

Files:
- `QuickExit/mod.txt` — mod manifest
- `QuickExit/mods/QuickExit/Main.gd` — autoload entry point that installs the override
- `QuickExit/mods/QuickExit/MenuOverride.gd` — replacement `_on_quit_pressed` that calls `get_tree().quit()` directly

### VariableCrouch

Replaces the binary crouch toggle with seven variable crouch levels. Press `C` for the default crouch/stand toggle; hold `C` and scroll the mouse wheel to smoothly adjust stance height between full crouch (pelvis `0.5`) and full stand (`1.0`). Scrolling across the boundary swaps the collision shape and applies the same stance-change impulse the base game uses, and `above.is_colliding()` still gates standing up under geometry. While `C` is held, the `weapon_high`/`weapon_low` input actions are temporarily unbound from the InputMap so the wheel doesn't also raise/lower the weapon — they're restored on release.

Files:
- `VariableCrouch/mod.txt` — mod manifest
- `VariableCrouch/mods/VariableCrouch/Main.gd` — autoload entry point that installs the override
- `VariableCrouch/mods/VariableCrouch/ControllerOverride.gd` — extends `res://Scripts/Controller.gd`; adds the level state, scroll-wheel handler, InputMap stash/restore, and re-targets the pelvis lerp to the active level

## Scripts

Python 3 helper scripts in `Scripts/`. Both read configuration from `Scripts/.env` (gitignored); copy `.env.example` and fill in paths before use.

### `decomp.py`

Extracts `RTV.pck` from the installed game and runs [gdre_tools](https://github.com/bruvzg/gdsdecomp) to recover a Godot project into `Decomp/` for reference while modding.

Requires `godotpcktool` and `gdre_tools.x86_64` on `PATH`.

Env vars:
- `RTV_PATH` — directory containing `RTV.pck`
- `DCMP_PATH` — scratch directory for raw extracted files
- `RECOVER_PATH` — output directory for the recovered project (defaults to `/mnt/c/Dev/RTV/Decomp`)

### `deploy_mod.py`

Zips a mod folder from the project root and rsyncs the archive into the game's `mods/` directory.

Usage:

```
Scripts/deploy_mod.py QuickExit
```

Env vars:
- `RTV_PATH` — game install directory (the script writes to `$RTV_PATH/mods`)

## Layout

- `QuickExit/` — the Quick Exit mod, laid out ready to be zipped by `deploy_mod.py`
- `VariableCrouch/` — the Variable Crouch mod, same layout
- `Scripts/` — deployment and decompilation helpers
- `Decomp/` — gitignored output of `decomp.py`; the recovered game project used as a reference

## License

See [LICENSE](LICENSE).
