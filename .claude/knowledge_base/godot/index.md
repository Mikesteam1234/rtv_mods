# Godot 4.6.1 Reference — Knowledge Base Index

Distilled from the [official Godot 4.6 documentation](https://docs.godotengine.org/en/stable/).

---

## GDScript Language

| File | Summary |
|------|---------|
| [gdscript-basics.md](gdscript-basics.md) | Variables, types, operators, control flow, functions, classes, inheritance, enums, annotations |
| [gdscript-typing-and-exports.md](gdscript-typing-and-exports.md) | Static typing, typed arrays/dicts, `@export` annotations, ranges, hints, resource/node exports |
| [gdscript-style-guide.md](gdscript-style-guide.md) | Naming conventions, formatting, file ordering, documentation comments |

## Engine Architecture

| File | Summary |
|------|---------|
| [scene-tree-and-nodes.md](scene-tree-and-nodes.md) | SceneTree lifecycle, `_ready`/`_process`/`_input` order, instancing, node references, scene organization |
| [signals-and-groups.md](signals-and-groups.md) | Signal declaration/connection/emission, custom signals, groups, `get_nodes_in_group()` |
| [resources-and-loading.md](resources-and-loading.md) | Resource vs Node, `load()`/`preload()`, `ResourceLoader`, `res://` vs `user://` paths |
| [autoloads-and-singletons.md](autoloads-and-singletons.md) | Autoload setup, access patterns, when to use autoloads vs node injection |

## Input & Lifecycle

| File | Summary |
|------|---------|
| [input-system.md](input-system.md) | InputEvent hierarchy, InputMap, `_input` vs `_unhandled_input`, `Input` singleton, event consumption |
| [notifications-and-lifecycle.md](notifications-and-lifecycle.md) | NOTIFICATION constants, full lifecycle order, `delta`, `process_mode`, pausing |

## Class Reference (Curated)

| File | Summary |
|------|---------|
| [class-reference-node.md](class-reference-node.md) | Node class: key properties, methods (`get_node`, `add_child`, `queue_free`, `find_child`…), signals, virtual methods |
| [class-reference-essentials.md](class-reference-essentials.md) | SceneTree, Resource, PackedScene, Tween, Timer — curated API for 5 essential classes |

## Patterns & Practices

| File | Summary |
|------|---------|
| [best-practices.md](best-practices.md) | Composition vs inheritance, call down / signal up, duck typing, interfaces, scene vs script |
