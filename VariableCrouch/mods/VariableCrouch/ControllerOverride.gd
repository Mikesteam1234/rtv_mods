# Override of res://Scripts/Controller.gd that adds 7 incremental crouch heights
# driven by the mouse wheel while the `crouch` action is held. Releasing crouch
# without scrolling behaves as a normal toggle; scroll-wheel height changes
# suppress the release toggle and skip the impulse dip.
extends "res://Scripts/Controller.gd"

const CROUCH_TARGETS: Array[float] = [0.5, 0.5833, 0.6667, 0.75, 0.8333, 0.9167, 1.0]
const STAND_LEVEL: int = 7  # 1-based; standing == top of CROUCH_TARGETS (size())
const BLOCKED_ACTIONS: Array[StringName] = [&"weapon_high", &"weapon_low"]
const FORCED_AIM_ACTION: StringName = &"rail_movement"
const HEIGHT_LERP_SPEED: float = 5.0
const IMPULSE_STRENGTH: float = 0.1

var crouch_level: int = STAND_LEVEL
var crouch_held: bool = false
var scrolled_while_held: bool = false
var stashed_events: Dictionary = {}
var suppressed_rail_optics: Dictionary = {}

var _stand_shape_height: float = 0.0
var _crouch_shape_height: float = 0.0
var _stand_collider_y: float = 0.0
var _crouch_collider_y: float = 0.0
var _can_resize_crouch_shape: bool = false
var _last_resized_level: int = -1

func _ready() -> void:
	super._ready()
	if crouchCollider.shape is CapsuleShape3D and standCollider.shape is CapsuleShape3D:
		_stand_shape_height = standCollider.shape.height
		_crouch_shape_height = crouchCollider.shape.height
		_stand_collider_y = standCollider.position.y
		_crouch_collider_y = crouchCollider.position.y
		crouchCollider.shape = crouchCollider.shape.duplicate()
		_can_resize_crouch_shape = true
	else:
		var stand_class: String = standCollider.shape.get_class() if standCollider.shape != null else "<null>"
		var crouch_class: String = crouchCollider.shape.get_class() if crouchCollider.shape != null else "<null>"
		push_warning("VariableCrouch: expected CapsuleShape3D colliders but got stand=%s crouch=%s; skipping per-level resize." % [stand_class, crouch_class])

func _input(event: InputEvent) -> void:
	super._input(event)
	if not _is_crouch_scroll_event(event):
		return
	if not _can_change_crouch_level():
		return

	var wheel_delta: int = _wheel_delta_from(event.button_index)
	if wheel_delta == 0:
		return

	scrolled_while_held = true

	var new_level: int = clamp(crouch_level + wheel_delta, 1, STAND_LEVEL)
	if new_level == crouch_level:
		return
	var should_stand: bool = new_level == STAND_LEVEL
	if should_stand and above.is_colliding():
		return

	crouch_level = new_level
	if should_stand and gameData.isCrouching:
		_set_crouching(false)
	elif not should_stand and not gameData.isCrouching:
		_set_crouching(true)

func _wheel_delta_from(button_index: int) -> int:
	if button_index == MOUSE_BUTTON_WHEEL_UP:
		return 1
	if button_index == MOUSE_BUTTON_WHEEL_DOWN:
		return -1
	return 0

func _is_crouch_scroll_event(event: InputEvent) -> bool:
	return event is InputEventMouseButton \
		and event.pressed \
		and Input.is_action_pressed("crouch")

func _can_change_crouch_level() -> bool:
	return not gameData.freeze \
		and not gameData.isFlying \
		and is_on_floor()

func Crouch(delta: float) -> void:
	var held: bool = Input.is_action_pressed("crouch")
	if held and not crouch_held:
		_begin_crouch_hold()
	elif not held and crouch_held:
		_end_crouch_hold()
	crouch_held = held
	if held:
		_suppress_active_optic_rail()
	_call_super_neutralized(delta)
	_resync_crouch_level_with_game_data()
	pelvis.position.y = lerpf(pelvis.position.y, CROUCH_TARGETS[crouch_level - 1], delta * HEIGHT_LERP_SPEED)
	_resize_crouch_collider_for_level()

func _resize_crouch_collider_for_level() -> void:
	if not _can_resize_crouch_shape or crouchCollider.disabled:
		_last_resized_level = -1
		return
	if crouch_level == _last_resized_level:
		return
	var t: float = float(crouch_level - 1) / float(STAND_LEVEL - 1)
	crouchCollider.shape.height = lerpf(_crouch_shape_height, _stand_shape_height, t)
	crouchCollider.position.y = lerpf(_crouch_collider_y, _stand_collider_y, t)
	_last_resized_level = crouch_level

func _begin_crouch_hold() -> void:
	scrolled_while_held = false
	for action: StringName in BLOCKED_ACTIONS:
		stashed_events[action] = InputMap.action_get_events(action)
		InputMap.action_erase_events(action)
	Input.action_press(FORCED_AIM_ACTION)

func _end_crouch_hold() -> void:
	if not scrolled_while_held:
		_toggle_crouch()
	for action: StringName in BLOCKED_ACTIONS:
		for evt: InputEvent in stashed_events.get(action, []):
			InputMap.action_add_event(action, evt)
	stashed_events.clear()
	Input.action_release(FORCED_AIM_ACTION)
	for optic: Node3D in suppressed_rail_optics:
		if is_instance_valid(optic):
			optic.railMovement = suppressed_rail_optics[optic]
	suppressed_rail_optics.clear()

func _suppress_active_optic_rail() -> void:
	var optic: Node3D = _get_active_optic()
	if optic != null and not suppressed_rail_optics.has(optic):
		suppressed_rail_optics[optic] = optic.railMovement
		optic.railMovement = false

# Call super for its unrelated side effects, but neutralize every mutation
# that would collide with this override's state machine. Super toggles
# gameData.isCrouching + colliders on crouch press and sets the 0.1 impulse
# — we don't want that on press (a scroll may follow). _toggle_crouch()
# applies the impulse itself on release-with-no-scroll. Pelvis is re-lerped
# by the caller against CROUCH_TARGETS instead of super's binary 0.5/1.0.
func _call_super_neutralized(delta: float) -> void:
	var cached_is_crouching: bool = gameData.isCrouching
	var cached_stand_disabled: bool = standCollider.disabled
	var cached_crouch_disabled: bool = crouchCollider.disabled
	var cached_pelvis_y: float = pelvis.position.y
	var cached_crouch_impulse: float = crouchImpulse
	var cached_stand_impulse: float = standImpulse
	super.Crouch(delta)
	gameData.isCrouching = cached_is_crouching
	standCollider.disabled = cached_stand_disabled
	crouchCollider.disabled = cached_crouch_disabled
	pelvis.position.y = cached_pelvis_y
	crouchImpulse = cached_crouch_impulse
	standImpulse = cached_stand_impulse

# Defensive: resync crouch_level if gameData.isCrouching is mutated
# externally (other mods, cutscenes, death/revive).
func _resync_crouch_level_with_game_data() -> void:
	if gameData.isCrouching and crouch_level == STAND_LEVEL:
		crouch_level = 1
	elif not gameData.isCrouching and crouch_level != STAND_LEVEL:
		crouch_level = STAND_LEVEL

func _toggle_crouch() -> void:
	if gameData.isCrouching:
		if above.is_colliding():
			return
		_set_crouching(false)
		if crouch_level == 1:
			standImpulse = IMPULSE_STRENGTH
		crouch_level = STAND_LEVEL
	else:
		_set_crouching(true)
		crouch_level = 1
		crouchImpulse = IMPULSE_STRENGTH

func _set_crouching(value: bool) -> void:
	gameData.isCrouching = value
	standCollider.disabled = value
	crouchCollider.disabled = not value

func _get_active_optic() -> Node3D:
	if rigManager == null or rigManager.get_child_count() == 0:
		return null
	var rig: Node = rigManager.get_child(rigManager.get_child_count() - 1)
	if not (rig is WeaponRig):
		return null
	return rig.activeOptic
