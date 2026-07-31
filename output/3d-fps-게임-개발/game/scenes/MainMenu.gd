## MainMenu.gd
## Handles Start and Quit button presses on the main menu screen.

extends Control

func _ready() -> void:
	# Release mouse cursor on menu
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

	# Connect buttons
	var start_btn := get_node_or_null("CenterContainer/VBoxContainer/StartButton") as Button
	var quit_btn  := get_node_or_null("CenterContainer/VBoxContainer/QuitButton") as Button

	if start_btn:
		start_btn.pressed.connect(_on_start_pressed)
	if quit_btn:
		quit_btn.pressed.connect(_on_quit_pressed)

func _on_start_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/World.tscn")

func _on_quit_pressed() -> void:
	get_tree().quit()
