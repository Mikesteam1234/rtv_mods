extends "res://Scripts/Controller.gd"

const crouchTargets := [0.5, 0.6833, 0.6667, 0.75, 0.8333, 0.9167, 1.0]
const suppressedActions := ["weapon_high", "weapon_low"]
const suppressAimAction := "rail_movement"

var crouchLevel: int = 1
var crouchHeld: bool = false
var scrolledWhileHeld: bool = false
var stashedEvents: Dictionary = {}
var suppressedRailOptics: Dictionary = {}

func _input(event):
	super._input(event)
	if not (event is InputEventMouseButton and event.pressed and Input.is_action_pressed("crouch")):
		return
	if gameData.freeze or gameData.isFlying or not is_on_floor():
		return

	scrolledWhileHeld = true

	var prevLevel: int = crouchLevel
	if event.button_index == MOUSE_BUTTON_WHEEL_UP:
		crouchLevel = min(crouchLevel + 1, crouchTargets.size())
	elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		crouchLevel = max(crouchLevel - 1, 1)
	else:
		return
	if crouchLevel == prevLevel:
		return

	var shouldStand: bool = crouchLevel == crouchTargets.size()
	if shouldStand and above.is_colliding():
		crouchLevel = prevLevel
		return

	if shouldStand and gameData.isCrouching:
		gameData.isCrouching = false
		standCollider.disabled = false
		crouchCollider.disabled = true
	elif not shouldStand and not gameData.isCrouching:
		gameData.isCrouching = true
		standCollider.disabled = true
		crouchCollider.disabled = false

func Crouch(delta):
	var held: bool = Input.is_action_pressed("crouch")

	if held and not crouchHeld:
		scrolledWhileHeld = false
		for action in suppressedActions:
			stashedEvents[action] = InputMap.action_get_events(action)
			InputMap.action_erase_events(action)
		Input.action_press(suppressAimAction)
	elif not held and crouchHeld:
		if not scrolledWhileHeld:
			_toggleCrouch()
		for action in suppressedActions:
			for evt in stashedEvents.get(action, []):
				InputMap.action_add_event(action, evt)
		stashedEvents.clear()
		Input.action_release(suppressAimAction)
		for optic in suppressedRailOptics:
			if is_instance_valid(optic):
				optic.railMovement = suppressedRailOptics[optic]
		suppressedRailOptics.clear()
	crouchHeld = held

	if held:
		var optic = _getActiveOptic()
		if optic != null and not suppressedRailOptics.has(optic):
			suppressedRailOptics[optic] = optic.railMovement
			optic.railMovement = false

	if gameData.isCrouching and crouchLevel == crouchTargets.size():
		crouchLevel = 1
	elif not gameData.isCrouching and crouchLevel != crouchTargets.size():
		crouchLevel = crouchTargets.size()

	pelvis.position.y = lerp(pelvis.position.y, crouchTargets[crouchLevel - 1], delta * 5.0)

func _toggleCrouch():
	if gameData.isCrouching:
		if above.is_colliding():
			return
		gameData.isCrouching = false
		standCollider.disabled = false
		crouchCollider.disabled = true
		crouchLevel = crouchTargets.size()
		gameData.standImpulse = true
	else:
		gameData.isCrouching = true
		standCollider.disabled = true
		crouchCollider.disabled = false
		crouchLevel = 1
		gameData.crouchImpulse = true

func _getActiveOptic():
	if rigManager == null or rigManager.get_child_count() == 0:
		return null
	var rig = rigManager.get_child(rigManager.get_child_count() - 1)
	if not (rig is WeaponRig):
		return null
	return rig.activeOptic
