# GDScript Style Guide

> Godot 4.6 | [Basics](gdscript-basics.md) | [Typing & Exports](gdscript-typing-and-exports.md)

## Complete Example

```gdscript
class_name StateMachine
extends Node
## Hierarchical State machine for the player.
##
## Initializes states and delegates engine callbacks
## to the active state.

signal state_changed(previous, new)

@export var initial_state: Node
var is_active = true:
    set = set_is_active

@onready var _state = initial_state:
    set = set_state
@onready var _state_name = _state.name


func _init():
    add_to_group("state_machine")


func _ready():
    state_changed.connect(_on_state_changed)
    _state.enter()


func _unhandled_input(event):
    _state.unhandled_input(event)


func _physics_process(delta):
    _state.physics_process(delta)


func transition_to(target_state_path, msg={}):
    if not has_node(target_state_path):
        return
    var target_state = get_node(target_state_path)
    _state.exit()
    self._state = target_state
    _state.enter(msg)


func set_is_active(value):
    is_active = value
    set_physics_process(value)
    set_process_unhandled_input(value)


func set_state(value):
    _state = value
    _state_name = _state.name


func _on_state_changed(previous, new):
    state_changed.emit()
```

## Formatting

- **Encoding:** LF line endings, UTF-8, no BOM
- **Indentation:** Tabs (editor default). Use 2 indent levels for continuation lines
- **Trailing commas:** Use in multiline arrays/dicts/enums (better diffs)
- **Blank lines:** Two between functions/classes; one for logical sections within functions
- **Line length:** Keep under 100 characters, aim for 80
- **One statement per line** (exception: ternary expressions)
- **Boolean operators:** Prefer `and` / `or` / `not` over `&&` / `||` / `!`
- **Comments:** `# ` with space; `## ` for doc comments; `#region`/`#endregion` no space
- **Whitespace:** Space around operators and after commas. Space inside single-line dicts: `{ key = "value" }`
- **Quotes:** Double quotes preferred; single quotes to avoid escaping
- **Numbers:** Always include leading/trailing zeros (`0.5` not `.5`, `2.0` not `2.`). Lowercase hex. Use `_` separators for large numbers: `1_000_000`

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| File names | snake_case | `yaml_parser.gd` |
| Class names | PascalCase | `class_name YAMLParser` |
| Node names | PascalCase | `Camera3D`, `Player` |
| Functions | snake_case | `func load_level():` |
| Variables | snake_case | `var particle_effect` |
| Private | _prefix | `var _counter`, `func _recalculate():` |
| Signals | snake_case, past tense | `signal door_opened` |
| Constants | CONSTANT_CASE | `const MAX_SPEED = 200` |
| Enum names | PascalCase, singular | `enum Element` |
| Enum members | CONSTANT_CASE | `{EARTH, WATER, AIR, FIRE}` |

## Code Order

```
01. @tool, @icon, @static_unload
02. class_name
03. extends
04. ## doc comment

05. signals
06. enums
07. constants
08. static variables
09. @export variables
10. remaining regular variables
11. @onready variables

12. _static_init()
13. remaining static methods
14. _init()
15. _enter_tree()
16. _ready()
17. _process()
18. _physics_process()
19. remaining virtual methods
20. public methods
21. private methods
22. inner classes
```

**Rules of thumb:**
1. Properties and signals before methods
2. Public before private
3. Virtual callbacks before custom methods
4. Construction/init before runtime methods

## Static Typing Style

Use explicit types when the type is ambiguous; use `:=` inference when the type is obvious:

```gdscript
# Explicit — could be int or float
var health: int = 0

# Inferred — type is clearly Vector3
var direction := Vector3(1, 2, 3)

# get_node() needs explicit type (compiler can't infer)
@onready var health_bar: ProgressBar = get_node("UI/LifeBar")

# Alternative: as cast (also type-safe)
@onready var health_bar := get_node("UI/LifeBar") as ProgressBar
```

Wrap multiline conditions with parentheses, `and`/`or` at start of continuation line:

```gdscript
if (
        position.x > 200 and position.x < 400
        and position.y > 300 and position.y < 400
):
    pass
```

## RTV Modding Notes

- RTV's own scripts don't consistently follow this style guide — the decompiled source uses mixed conventions. Follow this guide for your mod code, but match the game's naming when overriding its methods/variables
- Use `snake_case` for all new mod functions and variables. Signal names should be past tense (`item_picked_up`, not `pick_up_item`)
