# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working directives

- Always reference this repo's local `.claude/` directory first before consulting `~/.claude/`. Project-local config and context take precedence over the user-global one.
- Always check `knowledge_base/` for relevant files before making a plan or implementing anything. Treat it as the primary source of task-specific context.

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

### Decomp/

Gitignored. Recovered Godot project from the shipped pck — treat as read-only reference when authoring overrides. Do not edit or commit.
