# Walkthrough: The Item Spawner Mod

> Walkthroughs | [ToDOnClock](todon-clock.md)

## What It Does

Press `INSERT` to open a searchable item catalog. Pick an item, click spawn, and it appears in your inventory or gets placed in the world for furniture. The catalog auto-populates from the game's database.

## Structure

```
ItemSpawner.vmz
├── mod.txt
├── mods/ItemSpawner/
│   ├── ItemSpawner.gd        ← main script
│   └── ItemSpawner.tscn      ← UI scene (Window + ItemList + controls)
└── .godot/exported/...        ← compiled scene data
```

### mod.txt

```ini
[mod]
name="ItemSpawner Compatibility Edition"
id="item-spawner-ce"
version="1.0.0"

[autoload]
ItemSpawner="res://mods/ItemSpawner/ItemSpawner.tscn"

[updates]
modworkshop=55672
```

**Key decisions:** The mod uses a scene-based autoload rather than a script, and contains **zero script overrides**. This design reads game data without modifying game scripts, ensuring compatibility alongside other mods.

## CanvasLayer Root

The root node is a `CanvasLayer`, which renders on top of the 3D world independently of the game camera:

```gdscript
extends CanvasLayer

@export var window: Window
@export var list: ItemList
@export var categoriesButton: OptionButton
```

The `@export` variables are wired to child nodes in the scene file. Using `CanvasLayer` means the mod avoids touching game UI scripts — the custom UI simply floats on top.

## Input Handling

```gdscript
func _input(event: InputEvent) -> void:
    var ui_manager = _get_ui_manager()
    if get_tree().current_scene == null:
        return
    if get_tree().current_scene.scene_file_path == "res://Scenes/Menu.tscn":
        return
    if ui_manager == null:
        return

    if event is InputEventKey and event.is_pressed() and event.keycode == KEY_INSERT:
        if window.visible or _ui_interface_open(ui_manager):
            toggleVisibility()
```

Extensive null checks prevent crashes when the game changes between updates.

## Building the Item Catalog

The catalog pulls from two sources with automatic fallback.

### Primary Path: Database.master.items

```gdscript
func _collect_itemdata_entries(dedupe: Dictionary) -> void:
    if typeof(Database) == TYPE_NIL:
        return
    if !("master" in Database):
        return

    var master = Database.master
    if master == null or !("items" in master):
        return

    for item in master.items:
        if item == null:
            continue
        var item_name = _safe_item_name(item)
        if item_name == "":
            continue

        var key = "itemdata|" + item_name
        if dedupe.has(key):
            continue
        dedupe[key] = true

        catalog.append({
            "name": item_name,
            "icon": _safe_item_icon(item),
            "type": _safe_item_type(item),
            "spawn_mode": "item_data",
            "item_data": item,
            "scene": null,
            "key": key,
        })
```

Each property access includes guards (`typeof()` checks, field existence verification) to survive database restructures across game versions.

### Fallback: Scene Crawling

If direct access fails, the code crawls the database script's constants for `PackedScene` entries:

```gdscript
func _collect_scene_entries(dedupe: Dictionary) -> void:
    var map := {}
    var database_class: GDScript = Database.get_script()

    while database_class:
        map.merge(database_class.get_script_constant_map())
        database_class = database_class.get_base_script()

    for p in map:
        if str(p).ends_with("_Rig"):
            continue
        var v = map.get(p)
        if v is not PackedScene:
            continue
        # ... instantiate and extract item data
```

The `get_base_script()` loop walks the entire inheritance chain, capturing items from both the original database and any mod that replaces it.

## Spawning

Two paths exist depending on item type.

### Normal Items (Inventory)

```gdscript
func _spawn_from_itemdata(entry: Dictionary) -> bool:
    var item = entry.get("item_data", null)
    var interface = _get_interface()
    if interface == null:
        return false

    var slot_data = SlotData.new()
    slot_data.itemData = item
    slot_data.amount = _safe_default_amount(item)

    # Furniture items get routed to world placement
    if str(_safe_item_type(item)) == "Furniture":
        return _spawn_entry_as_world_scene(entry)

    # Normal items: try auto-stacking (ammo, meds), then create new slot
    if _safe_call_bool(interface, "AutoStack", [slot_data, interface.inventoryGrid]):
        _safe_call(interface, "UpdateStats", [false])
        _safe_call(interface, "PlayEquip")
        return true

    if _safe_call_bool(interface, "Create", [slot_data, interface.inventoryGrid, false]):
        _safe_call(interface, "UpdateStats", [false])
        _safe_call(interface, "PlayEquip")
        return true

    _safe_call(interface, "PlayError")
    return false
```

### Furniture (World Placement)

```gdscript
func _spawn_scene_for_context_place(scene: PackedScene) -> bool:
    var iface = _get_interface()
    var item = scene.instantiate()
    add_child(item)

    iface.contextItem = item
    if iface.has_method("ContextPlace"):
        iface.ContextPlace.call_deferred()
        (func():
            if is_instance_valid(iface):
                iface.contextItem = null
        ).call_deferred()
        return true
    return false
```

`call_deferred()` allows the game's placement system to process the item on the next frame, avoiding state conflicts.

## Takeaways

**No script overrides prevents conflicts.** This mod reads game state but never modifies game scripts, enabling coexistence with other mods.

**Defensive coding is essential in early access.** All property access is guarded. The `_safe_call()` pattern wraps `has_method()` + `callv()` into one utility:

```gdscript
func _safe_call(obj, method_name: String, args: Array = []) -> Variant:
    if obj == null or !obj.has_method(method_name):
        return null
    return obj.callv(method_name, args)
```

Use this pattern whenever calling game methods that might be renamed in updates.

**Dual data paths** (direct database access plus scene crawl fallback) make the mod resilient to database changes.

**Scene-based autoloads** let you build complex UI in the editor rather than constructing it all in code.

## What Next?

- [Walkthrough: ToDOnClock](todon-clock.md) — script override chaining example
- [Publishing](../guides/publishing.md) — distribute your mod on ModWorkshop
