# Signals & Groups

> Godot 4.6 | [Scene Tree](scene-tree-and-nodes.md) | [Resources](resources-and-loading.md)

## Signals

Signals are messages that nodes emit when something happens. They implement the observer pattern — objects react to events without direct coupling. In Godot 4, signals are first-class types.

### Declaring Custom Signals

```gdscript
signal health_changed(old_value: int, new_value: int)
signal died
signal item_picked_up(item: Item, quantity: int)
```

### Connecting Signals

```gdscript
func _ready() -> void:
    # Connect a signal to a method
    $Button.pressed.connect(_on_button_pressed)

    # Connect with arguments bound
    $Timer.timeout.connect(_on_timeout.bind("my_timer"))

    # One-shot: automatically disconnects after first emission
    $AnimationPlayer.animation_finished.connect(
        _on_animation_done, CONNECT_ONE_SHOT
    )

func _on_button_pressed() -> void:
    print("Button pressed")

func _on_timeout(timer_name: String) -> void:
    print(timer_name, " timed out")

func _on_animation_done(anim_name: StringName) -> void:
    print(anim_name, " finished")
```

### Emitting Signals

```gdscript
var health: int = 100

func take_damage(amount: int) -> void:
    var old: int = health
    health -= amount
    health_changed.emit(old, health)
    if health <= 0:
        died.emit()
```

### Disconnecting

```gdscript
$Button.pressed.disconnect(_on_button_pressed)

# Check if connected first
if $Button.pressed.is_connected(_on_button_pressed):
    $Button.pressed.disconnect(_on_button_pressed)
```

### Await (Coroutines)

Pause execution until a signal is emitted:

```gdscript
func spawn_enemy() -> void:
    var enemy: Node = enemy_scene.instantiate()
    add_child(enemy)
    # Wait until this specific enemy dies
    await enemy.died
    print("Enemy defeated!")
    spawn_next_wave()

# Await with a timer
await get_tree().create_timer(2.0).timeout
print("2 seconds passed")
```

### Signal as Variable

Signals are `Signal` typed values — you can pass them around:

```gdscript
func wait_for(sig: Signal) -> void:
    await sig
    print("Signal received")
```

### Common Built-in Signals

| Node Type | Signal | When |
|-----------|--------|------|
| `Button` | `pressed` | Button clicked |
| `Timer` | `timeout` | Timer expires |
| `Area3D` | `body_entered(body)` | Physics body enters |
| `AnimationPlayer` | `animation_finished(name)` | Animation ends |
| `HTTPRequest` | `request_completed(...)` | HTTP response received |
| `Node` | `ready` | Node is ready |
| `Node` | `tree_entered` | Node entered the tree |
| `Node` | `tree_exiting` | Node about to leave tree |

---

## Groups

Groups are string tags you assign to nodes. They enable batch operations without direct node references.

### Adding and Checking

```gdscript
func _ready() -> void:
    add_to_group("enemies")
    add_to_group("damageable")

func _exit_tree() -> void:
    remove_from_group("enemies")

# Check membership
if node.is_in_group("enemies"):
    node.alert()
```

### Getting Nodes in a Group

```gdscript
# Returns Array[Node]
var enemies: Array[Node] = get_tree().get_nodes_in_group("enemies")
for enemy: Node in enemies:
    enemy.retreat()
```

### Calling Methods on a Group

```gdscript
# Call a method on every node in the group
get_tree().call_group("enemies", "retreat")

# With arguments
get_tree().call_group("damageable", "take_damage", 50)

# Call deferred (next idle frame)
get_tree().call_group_flags(
    SceneTree.GROUP_CALL_DEFERRED, "enemies", "retreat"
)
```

### Group Notification

```gdscript
get_tree().notify_group("enemies", Node.NOTIFICATION_PAUSED)
```

### Practical Patterns

```gdscript
# Event bus pattern — signal all listeners without direct references
func alert_all_guards() -> void:
    get_tree().call_group("guards", "enter_alert_state")

# Count entities
func enemy_count() -> int:
    return get_tree().get_nodes_in_group("enemies").size()

# Check if any exist
func has_enemies() -> bool:
    return not get_tree().get_nodes_in_group("enemies").is_empty()
```

## RTV Modding Notes

- RTV uses groups extensively: `Furniture`, `Interactable`, `AI`, `Player`, `Slot`, etc. See [game internals index](../game-internals/index.md) for the full list
- Connecting to game signals is a primary modding technique — e.g., connecting to `Database` signals for item events. See [modding techniques](../techniques/modding-techniques.md)
- When overriding scripts, existing signal connections from `.tscn` files are preserved. Your override inherits them automatically
