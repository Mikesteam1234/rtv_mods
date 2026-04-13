# Installing Mods

> Getting Started | [First Mod](first-mod.md) | [Decompiling](decompiling.md)

You don't need to know anything about modding to play with mods. This page gets you from zero to playing with mods in a few minutes.

## Install the Mod Loader

1. Download the latest Metro Mod Loader release from ModWorkshop. You'll get two files: `override.cfg` and `modloader.gd`
2. Put `override.cfg` in your game install folder. Right-click Road to Vostok in Steam → Manage → Browse local files, and drop it next to the game .exe
3. Put `modloader.gd` in `%APPDATA%/Road to Vostok/`. Hit Win+R and paste that path

That's it. The mod loader is installed.

## Create the Mods Folder

Make a folder called `mods` in the game install directory (same place you put `override.cfg`):

```
Road to Vostok/
├── override.cfg
├── Road to Vostok.exe
├── Road to Vostok.pck
└── mods/                 ← make this
```

## Install a Mod

1. Download a mod from ModWorkshop
2. Drop the `.vmz` or `.zip` file directly into the `mods/` folder
3. Launch the game

The mod loader UI pops up before the main menu. You'll see your mods listed. Check the boxes to enable the ones you want and hit Launch.

## Managing Mods

The launcher has two tabs visible by default, plus one for developers:

- **Mods** — enable/disable mods and set their load order priority
- **Updates** — check ModWorkshop for newer versions of your installed mods
- **Compatibility** — run a scan to check for conflicts before launching *(only visible when Developer Mode is enabled via the checkbox at the bottom of the launcher)*

Your enable/disable and priority settings are saved automatically, so you don't need to reconfigure every time you play.

## If Something Goes Wrong

Check the log at `%APPDATA%/Road to Vostok/logs/godot.log` for error messages. The [Troubleshooting](../guides/troubleshooting.md) page covers the common issues.

To disable all mods quickly, just remove `override.cfg` from the game folder. The game will start normally without the mod loader.
