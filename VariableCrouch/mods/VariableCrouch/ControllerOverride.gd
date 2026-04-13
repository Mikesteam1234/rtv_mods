extends "res://Scripts/Controller.gd"

const crouchTargets := [0.5, 0.5833, 0.6667, 0.75, 0.8333, 0.9167, 1.0]
const suppressedActions := ["weapon_high", "weapon_low"]

var crouchLevel: int = 1
var crouchHeld: bool = false
var stashedEvents: Dictionary = {}

func _input(event):
	super._input(event)
	if not (event is InputEventMouseButton and event.pressed and Input.is_action_pressed("crouch")):
		return
	if gameData.freeze or gameData.isFlying or not is_on_floor():
		return

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
		standImpulse = 0.1
		standCollider.disabled = false
		crouchCollider.disabled = true
	elif not shouldStand and not gameData.isCrouching:
		gameData.isCrouching = true
		crouchImpulse = 0.1
		standCollider.disabled = true
		crouchCollider.disabled = false

func Crouch(delta):
	var held: bool = Input.is_action_pressed("crouch")
	if held and not crouchHeld:
		for action in suppressedActions:
			stashedEvents[action] = InputMap.action_get_events(action)
			InputMap.action_erase_events(action)
	elif not held and crouchHeld:
		for action in suppressedActions:
			for evt in stashedEvents.get(action, []):
				InputMap.action_add_event(action, evt)
		stashedEvents.clear()
	crouchHeld = held

	super.Crouch(delta)
	if gameData.isCrouching and crouchLevel == crouchTargets.size():
		crouchLevel = 1
	elif not gameData.isCrouching and crouchLevel != crouchTargets.size():
		crouchLevel = crouchTargets.size()
	pelvis.position.y = lerp(pelvis.position.y, crouchTargets[crouchLevel - 1], delta * 5.0)
