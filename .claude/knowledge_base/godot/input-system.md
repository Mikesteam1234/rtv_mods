# Input System

> Godot 4.6 | [Lifecycle](notifications-and-lifecycle.md) | [Scene Tree](scene-tree-and-nodes.md)

## InputEvent Hierarchy

All input in Godot flows through `InputEvent` objects. Key subclasses:

| Class | Represents |
|-------|-----------|
| `InputEventKey` | Keyboard key press/release |
| `InputEventMouseButton` | Mouse click (button, position, double-click) |
| `InputEventMouseMotion` | Mouse movement (position, relative, velocity) |
| `InputEventJoypadButton` | Controller button |
| `InputEventJoypadMotion` | Controller analog stick/trigger |
| `InputEventScreenTouch` | Touchscreen press/release |
| `InputEventScreenDrag` | Touchscreen drag |
| `InputEventAction` | Programmatically generated action event |
| `InputEventShortcut` | Shortcut key combination |

## Input Propagation Order

Events flow through the tree in this order. **Each step can consume the event, stopping further propagation.**

1. **`_input(event)`** — Called on nodes in reverse depth-first order (leaf nodes first). Can consume with `get_viewport().set_input_as_handled()`
2. **`Control._gui_input(event)`** — GUI controls process the event. Can consume with `accept_event()`
3. **`_shortcut_input(event)`** — Keyboard and joypad button events only
4. **`_unhandled_key_input(event)`** — Keyboard events not consumed above
5. **`_unhandled_input(event)`** — All events not consumed above
6. **Physics picking** — 3D/2D collision-based input detection

```gdscript
# _input: runs first, before GUI. Use to intercept events.
func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
        get_viewport().set_input_as_handled()
        toggle_pause()

# _unhandled_input: runs after GUI. Best for gameplay input.
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("jump"):
        jump()
```

> **Best practice:** Use `_unhandled_input` for gameplay input so UI elements naturally block it. Use `_input` only when you need to intercept before the GUI.

## InputMap & Actions

Actions map human-readable names to one or more input events. Configure in **Project > Project Settings > Input Map**.

### Checking Actions

```gdscript
func _physics_process(delta: float) -> void:
    # Held down (continuous)
    if Input.is_action_pressed("move_forward"):
        move(Vector3.FORWARD * speed * delta)

    # Just pressed this frame (one-shot)
    if Input.is_action_just_pressed("jump"):
        jump()

    # Just released this frame
    if Input.is_action_just_released("fire"):
        release_charged_shot()

    # Analog strength (0.0 to 1.0)
    var strength: float = Input.get_action_strength("accelerate")
```

### Input Vectors and Axes

```gdscript
# 2D movement vector from 4 actions
var direction: Vector2 = Input.get_vector(
    "move_left", "move_right", "move_up", "move_down"
)

# Single axis from 2 actions (-1.0 to 1.0)
var horizontal: float = Input.get_axis("move_left", "move_right")
```

### Modifying InputMap at Runtime

```gdscript
# Add a new action
InputMap.add_action("custom_action")
var event := InputEventKey.new()
event.keycode = KEY_G
InputMap.action_add_event("custom_action", event)

# Remove all events from an action (suppress it)
var events: Array[InputEvent] = InputMap.action_get_events("weapon_high")
for ev: InputEvent in events:
    InputMap.action_erase_event("weapon_high", ev)

# Re-add later to restore
for ev: InputEvent in saved_events:
    InputMap.action_add_event("weapon_high", ev)

# Check if action exists
if InputMap.has_action("my_action"):
    pass
```

## The Input Singleton

### Mouse Mode

```gdscript
Input.mouse_mode = Input.MOUSE_MODE_CAPTURED   # FPS-style (hidden, centered)
Input.mouse_mode = Input.MOUSE_MODE_VISIBLE     # Normal
Input.mouse_mode = Input.MOUSE_MODE_CONFINED    # Can't leave window
Input.mouse_mode = Input.MOUSE_MODE_HIDDEN      # Hidden but tracks position
```

### Programmatic Input

```gdscript
# Inject an action event (useful for testing or virtual buttons)
var action := InputEventAction.new()
action.action = "jump"
action.pressed = true
Input.parse_input_event(action)
```

### Other Useful Methods

```gdscript
Input.is_key_pressed(KEY_SHIFT)
Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)
Input.get_mouse_position()        # viewport coordinates
Input.get_last_mouse_velocity()
Input.start_joy_vibration(0, 0.5, 0.5, 0.3)  # device, weak, strong, duration
```

## Consuming Events

```gdscript
# In _input or _unhandled_input:
func _input(event: InputEvent) -> void:
    if event.is_action_pressed("pause"):
        get_viewport().set_input_as_handled()  # stops further propagation
        toggle_pause()

# In Control._gui_input:
func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        accept_event()  # Control-specific, stops propagation
```

## Keyboard Input Details

```gdscript
func _input(event: InputEvent) -> void:
    if event is InputEventKey:
        if event.pressed and not event.echo:  # ignore key repeat
            match event.keycode:
                KEY_W:
                    print("W pressed")
                KEY_SPACE:
                    print("Space pressed")

        # Check modifiers
        if event.ctrl_pressed:
            pass
        if event.shift_pressed:
            pass
        if event.alt_pressed:
            pass
```

## Mouse Input Details

```gdscript
func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.pressed:
            match event.button_index:
                MOUSE_BUTTON_LEFT:
                    shoot()
                MOUSE_BUTTON_RIGHT:
                    aim()
                MOUSE_BUTTON_WHEEL_UP:
                    zoom_in()

    if event is InputEventMouseMotion:
        # FPS camera rotation
        rotation.y -= event.relative.x * mouse_sensitivity
        rotation.x -= event.relative.y * mouse_sensitivity
        rotation.x = clampf(rotation.x, -PI / 2, PI / 2)
```

## RTV Modding Notes

- RTV's `Inputs.gd` wraps the input system. See [player system](../game-internals/player-system.md)
- `set_input_as_handled()` only blocks `_unhandled_input` — it does NOT block `_input()` or `Input.is_action_just_pressed()` polling in other scripts. See CLAUDE.md override gotchas
- To suppress a polled action (like `weapon_high`/`weapon_low` in `Handling.gd`), use `InputMap.action_erase_events()` to temporarily remove bindings, then `action_add_event()` to restore them. This is the only way to block polled input from scripts you can't override
- RTV uses 120 physics ticks/second — `_physics_process` delta is ~0.0083s, not the default 0.016s
