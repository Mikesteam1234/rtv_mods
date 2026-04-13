extends "res://Scripts/Menu.gd"

func _on_quit_pressed():
	PlayClick()
	DeactivateButtons()
	blocker.mouse_filter = MOUSE_FILTER_STOP
	get_tree().quit()