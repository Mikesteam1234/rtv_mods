# Override of res://Scripts/Controller.gd that adds 7 incremental crouch heights
# driven by the mouse wheel while the `crouch` action is held. Releasing crouch
# without scrolling behaves as a normal toggle; scroll-wheel height changes
# suppress the release toggle and skip the impulse dip.
extends "res://Scripts/Controller.gd"

const CROUCH_TARGETS: Array[float] = [0.5, 0.5833, 0.6667, 0.75, 0.8333, 0.9167, 1.0]
const STAND_LEVEL_INDEX: int = 7  # must equal CROUCH_TARGETS.size()
const BLOCKED_ACTIONS: Array[StringName] = [&"weapon_high", &"weapon_low"]
const FORCED_AIM_ACTION: StringName = &"rail_movement"
const HEIGHT_LERP_SPEED: float = 5.0
const IMPULSE_STRENGTH: float = 0.1

var crouch_level: int = 1
var crouch_held: bool = false
var scrolled_while_held: bool = false
var stashed_events: Dictionary = {}
var suppressed_rail_optics: Dictionary = {}

func _input(event: InputEvent) -> void:
	super._input(event)
	if not (event is InputEventMouseButton and event.pressed and Input.is_action_pressed("crouch")):
		return
	if gameData.freeze or gameData.isFlying or not is_on_floor():
		return

	scrolled_while_held = true

	var prev_level: int = crouch_level
	if event.button_index == MOUSE_BUTTON_WHEEL_UP:
		crouch_level = min(crouch_level + 1, STAND_LEVEL_INDEX)
	elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		crouch_level = max(crouch_level - 1, 1)
	else:
		return
	if crouch_level == prev_level:
		return

	var should_stand: bool = crouch_level == STAND_LEVEL_INDEX
	if should_stand and above.is_colliding():
		crouch_level = prev_level
		return

	if should_stand and gameData.isCrouching:
		_set_crouching(false)
	elif not should_stand and not gameData.isCrouching:
		_set_crouching(true)

func Crouch(delta: float) -> void:
	var held: bool = Input.is_action_pressed("crouch")

	if held and not crouch_held:
		scrolled_while_held = false
		for action in BLOCKED_ACTIONS:
			stashed_events[action] = InputMap.action_get_events(action)
			InputMap.action_erase_events(action)
		Input.action_press(FORCED_AIM_ACTION)
	elif not held and crouch_held:
		if not scrolled_while_held:
			_toggle_crouch()
		for action in BLOCKED_ACTIONS:
			for evt: InputEvent in stashed_events.get(action, []):
				InputMap.action_add_event(action, evt)
		stashed_events.clear()
		Input.action_release(FORCED_AIM_ACTION)
		for optic: Node3D in suppressed_rail_optics:
			if is_instance_valid(optic):
				optic.railMovement = suppressed_rail_optics[optic]
		suppressed_rail_optics.clear()
	crouch_held = held

	if held:
		var optic: Node3D = _get_active_optic()
		if optic != null and not suppressed_rail_optics.has(optic):
			suppressed_rail_optics[optic] = optic.railMovement
			optic.railMovement = false

	# Call super for its unrelated side effects, but neutralize every mutation
	# that would collide with this override's state machine. Super toggles
	# gameData.isCrouching + colliders on crouch press and sets the 0.1 impulse
	# — we don't want that on press (a scroll may follow). _toggle_crouch()
	# applies the impulse itself on release-with-no-scroll. Pelvis is re-lerped
	# below against CROUCH_TARGETS instead of super's binary 0.5/1.0.
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
	if gameData.isCrouching and crouch_level == STAND_LEVEL_INDEX:
		crouch_level = 1
	elif not gameData.isCrouching and crouch_level != STAND_LEVEL_INDEX:
		crouch_level = STAND_LEVEL_INDEX

	pelvis.position.y = lerpf(pelvis.position.y, CROUCH_TARGETS[crouch_level - 1], delta * HEIGHT_LERP_SPEED)

func _toggle_crouch() -> void:
	if gameData.isCrouching:
		if above.is_colliding():
			return
		_set_crouching(false)
		if crouch_level == 1:
			standImpulse = IMPULSE_STRENGTH
		crouch_level = STAND_LEVEL_INDEX
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
