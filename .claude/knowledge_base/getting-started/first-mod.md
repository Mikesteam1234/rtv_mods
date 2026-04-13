# Your First Mod

> [Installing Mods](installing-mods.md) | Getting Started | [Decompiling](decompiling.md)

This page walks you through making a real, working mod from scratch. By the end you'll have a mod that loads into the game, prints to the log, and responds to a keypress. The whole thing is three files.

## What You Need

- The mod loader installed ([Installing Mods](installing-mods.md) if you haven't yet)
- A text editor (Notepad works, VS Code is better)
- A way to make zip files (Windows built-in or 7-Zip)

## Step 1: Create Your Mod Folder

Make a new folder somewhere on your computer. Call it `HelloWorld`. Inside it, you're going to create two files.

## Step 2: Write mod.txt

Every mod needs a `mod.txt` at the root of its archive. This tells the mod loader what your mod is called and what scripts to run. Create a file called `mod.txt` inside your `HelloWorld` folder:

```ini
[mod]
name="Hello World"
id="hello-world"
version="1.0.0"

[autoload]
HelloWorld="res://mods/HelloWorld/Main.gd"
```

The `[mod]` section is your mod's identity. The `[autoload]` section tells the mod loader to create a node running your `Main.gd` script when the game starts.

## Step 3: Write Main.gd

Create a folder called `mods` inside your `HelloWorld` folder, then a folder called `HelloWorld` inside that, then a file called `Main.gd`:

```
HelloWorld/
├── mod.txt
└── mods/
    └── HelloWorld/
        └── Main.gd
```

Open `Main.gd` and write:

```gdscript
extends Node

func _ready():
    print("[HelloWorld] My first mod is running!")
```

That's it. That's a working mod. `_ready()` runs when the mod loader creates your autoload node, and `print()` writes to the game's log file.

## Step 4: Zip It Up

Select **both** `mod.txt` and the `mods/` folder, then right-click and compress them into a zip. The important thing is that `mod.txt` is at the root of the zip, not nested inside another folder.

```
HelloWorld.zip
├── mod.txt              ← at the root, not inside a subfolder
└── mods/
    └── HelloWorld/
        └── Main.gd
```

If you're using 7-Zip: select both items, right-click, 7-Zip → Add to archive, pick zip format.

> If you want, rename `.zip` to `.vmz`. They're the same thing; `.vmz` is just the community convention.

## Step 5: Test It

1. Copy `HelloWorld.zip` into the game's `mods/` folder (inside the game install directory)
2. Launch Road to Vostok
3. The mod loader UI appears. You should see "Hello World" in the list
4. Check the box to enable it, hit Launch
5. Once the game loads to the main menu, open the log file at `%APPDATA%/Road to Vostok Demo/logs/godot.log`
6. Search for `[HelloWorld]`. You should see:

```
[HelloWorld] My first mod is running!
```

If you see that, congratulations. You made a mod.

## Step 6: Make It Do Something

Printing to the log proves your mod loads, but let's make it do something you can actually see in-game. Update your `Main.gd`:

```gdscript
extends Node

func _ready():
    print("[HelloWorld] My first mod is running!")

func _unhandled_input(event):
    if event is InputEventKey and event.pressed and event.keycode == KEY_F8:
        print("[HelloWorld] F8 was pressed!")
```

Re-zip, replace the old zip in `mods/`, relaunch the game. Now every time you press F8 in-game, a line appears in the log. You have a mod that runs code in response to player input.

## What Just Happened?

Here's what the mod loader did with your zip:

1. Mounted `HelloWorld.zip` into Godot's virtual filesystem. Your `Main.gd` is now accessible at `res://mods/HelloWorld/Main.gd`
2. Read `mod.txt`, found the `[autoload]` section
3. Created a node, set its script to your `Main.gd`, added it to the scene tree
4. Your `_ready()` ran and printed to the log
5. Your `_unhandled_input()` runs every time a key is pressed

This is the same autoload pattern that every Vostok mod uses. The ToDOnClock and Item Spawner walkthroughs are built on the exact same foundation, just with more code.

## Where to Go from Here

You've got a mod that loads and runs code. Here's how to start doing real things with it:

**Learn what the game's code looks like.** [Decompile the game](decompiling.md) to extract the scripts and scenes. You'll need this to know what to override, what methods to call, and what paths to use.

**Understand the core modding techniques.** [Modding Techniques](../techniques/modding-techniques.md) covers the four things you can do: replace assets, run autoload scripts, override game scripts, and load custom files.

**See real mods broken down.** The [ToDOnClock walkthrough](../walkthroughs/todon-clock.md) shows how to override game scripts and chain with other mods. The [Item Spawner walkthrough](../walkthroughs/item-spawner.md) shows how to build a UI and read game data without touching any game scripts.

**Know how to package and publish.** [Mod Structure](../reference/mod-structure.md) covers the `mod.txt` format and packaging rules. [Publishing](../guides/publishing.md) covers uploading to ModWorkshop.
