extends Node

func _ready():
	overrideScript("res://mods/VariableCrouch/ControllerOverride.gd")
	if get_tree().current_scene != null:
		get_tree().reload_current_scene()
	queue_free()

func overrideScript(overrideScriptPath: String):
	var script: Script = load(overrideScriptPath)
	script.reload()
	var parentScript = script.get_base_script()
	var parentPath: String = parentScript.resource_path
	script.take_over_path(parentPath)
	var resolved := load(parentPath)
	print("[VariableCrouch] override ", overrideScriptPath, " -> ", parentPath, " resolves to ", resolved.resource_path, " same=", resolved == script)
	return script
