# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working directives

- Always reference this repo's local `.claude/` directory first before consulting `~/.claude/`. Project-local config and context take precedence over the user-global one.
- Before planning or implementing anything, read [.claude/knowledge_base/index.md](.claude/knowledge_base/index.md) and load any entries whose summary is relevant to the task into context. Treat `knowledge_base/` as the primary source of task-specific context — the index exists so you can find the right file without scanning the tree.

## Repository purpose

Mods and tooling for [Road to Vostok](https://roadtovostok.com/), a Godot 4 game shipped as a `.pck`. This repo contains GDScript mods plus Python helpers to decompile the game (for reference) and deploy built mod zips into the installed game directory.

## Commands

All scripts are Python 3 (never bash). Both read config from `Scripts/.env`.

- Deploy a mod: `Scripts/deploy_mod.py <ModFolder>` — zips `<ModFolder>/` as `<ModFolder>.vmz` (community convention for RTV mods — a zip with a renamed extension) and rsyncs it to `$RTV_PATH/mods/`.
- Decompile the game: `Scripts/decomp.py` — extracts `$RTV_PATH/RTV.pck` via `godotpcktool` and recovers a Godot project to `$RECOVER_PATH` (default `/mnt/c/Dev/RTV/Decomp`) using `gdre_tools.x86_64`. Both tools must be on `PATH`.

Env vars (in `Scripts/.env`): `RTV_PATH` (game install dir), `DCMP_PATH` (scratch), `RECOVER_PATH` (recovered project out).

There is no build step, test suite, or linter — mods are plain GDScript loaded at runtime by the game.

## Architecture

### Mod loading pattern

A mod folder at the repo root (e.g. `QuickExit/`) is the exact layout that gets zipped and dropped into `$RTV_PATH/mods/`. Inside:

- `mod.txt` — manifest with `[mod]` metadata and an `[autoload]` section pointing at the mod's `Main.gd`.
- `mods/<ModId>/Main.gd` — autoload entry point. Runs on game start.
- `mods/<ModId>/*.gd` — override scripts that replace game scripts.

### Script override technique (see `QuickExit/mods/QuickExit/Main.gd`)

Because the game's scripts are baked into the pck, mods replace them by:
1. `load()`-ing the override script, whose `extends` points at the target game script path (e.g. `res://Scripts/Menu.gd`).
2. Calling `script.take_over_path(parentScript.resource_path)` so the override takes the base script's `res://` path.
3. Reloading the current scene so nodes re-instantiate with the overridden script.
4. `queue_free()`-ing the autoload node.

When writing a new override, `extends "res://..."` must point at the real decompiled path, and the override must keep signatures/fields referenced elsewhere intact. Use `Decomp/` (populated by `decomp.py`) to look up original scripts.

### Override gotchas

- **Call `super.<method>(...)` in every override.** Overriding `_input`, `_ready`, `_physics_process`, etc. replaces the base entirely — mouse look, scene init, input chains all break unless you call super. The ModLoader warns about missing super in lifecycle methods and also breaks other mods' override chains.
- **`Node` has no `_ready` to super-call.** If the autoload's `Main.gd` `extends Node`, don't write `super._ready()` — it's a parse error. Override chains only apply when extending another script that actually defines the method.
- **`reload_current_scene()` fails during boot.** Autoloads run before the main scene is set; guard with `if get_tree().current_scene != null`. `take_over_path` persists for the process lifetime regardless, so the reload is only useful when the override's target is in the currently-loaded scene.
- **`take_over_path` doesn't reach scripts referenced by UID in `.tscn` files.** Godot 4 `.tscn` ext_resources for scripts use `uid://…`, which resolves independently of the resource cache that `take_over_path` patches. Script overrides for scripts attached to weapon rigs, item rigs, etc. silently do nothing — the original script is still instantiated on those nodes. See `knowledge_base/techniques/advanced-techniques.md` ("Scene Inheritance for UID Stripping") for the documented workaround: ship an inherited `.tscn` that re-specifies the script by path. If you only need to suppress an input-driven behavior (not change the node's logic), manipulating `InputMap` at runtime is often simpler — see next bullet.
- **Polled input (`Input.is_action_just_pressed`) bypasses `_input()`.** `set_input_as_handled()` on the viewport only blocks `_unhandled_input` — other nodes' `_input` and direct `Input.*` polling (used by `Handling.gd` for `weapon_high`/`weapon_low`, for example) still fire. To suppress a polled action under a condition, stash and `InputMap.action_erase_events(name)` while the condition holds, then `action_add_event` back to restore. This works even against scripts you can't override.

### Decomp/

Gitignored. Recovered Godot project from the shipped pck — treat as read-only reference when authoring overrides. Do not edit or commit.
