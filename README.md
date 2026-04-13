# rtv_mods

Mods and tooling for [Road to Vostok](https://roadtovostok.com/), a Godot-based game.

## Mods

### QuickExit

Skips the exit confirmation dialog on the main menu so the Quit button closes the game immediately. The mod autoloads `Main.gd`, which swaps the base `Menu.gd` script for `MenuOverride.gd` via `take_over_path`, then reloads the current scene.

Files:
- `QuickExit/mod.txt` — mod manifest
- `QuickExit/mods/QuickExit/Main.gd` — autoload entry point that installs the override
- `QuickExit/mods/QuickExit/MenuOverride.gd` — replacement `_on_quit_pressed` that calls `get_tree().quit()` directly

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
- `Scripts/` — deployment and decompilation helpers
- `Decomp/` — gitignored output of `decomp.py`; the recovered game project used as a reference

## License

See [LICENSE](LICENSE).
