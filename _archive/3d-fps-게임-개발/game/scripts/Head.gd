## Head.gd
## Manages first-person camera look via mouse input.
## Yaw (left/right) rotates the parent Player body; pitch (up/down) rotates
## only this Head node, clamped to ±85 degrees to prevent gimbal flip.
##
## [참조] Whimfoome/godot-FirstPersonStarter (MIT)
## https://github.com/Whimfoome/godot-FirstPersonStarter
## 피치/요 분리 패턴 및 Input.set_mouse_mode(CAPTURED) 초기화 방식 참조.

extends Node3D

# ---------------------------------------------------------------------------
# Node references
# ---------------------------------------------------------------------------
@onready var camera: Camera3D = $Camera3D
@onready var player: CharacterBody3D = get_parent()  # Player (CharacterBody3D)

# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------
var _pitch_deg: float = 0.0   # accumulated pitch in degrees

const PITCH_LIMIT_DEG: float = 85.0

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	camera.fov = GameSettings.fov

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and \
	   Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		_handle_mouse_motion(event as InputEventMouseMotion)

	# Release cursor with Escape (useful in editor / windowed mode)
	if event.is_action_just_pressed("ui_cancel"):
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

# ---------------------------------------------------------------------------
# Mouse look
# ---------------------------------------------------------------------------
func _handle_mouse_motion(event: InputEventMouseMotion) -> void:
	var sensitivity := GameSettings.mouse_sensitivity * 0.1  # scale to reasonable range

	# Yaw  — rotate the whole player body left/right
	player.rotate_y(-event.relative.x * sensitivity)

	# Pitch — rotate only the Head node up/down, clamped
	_pitch_deg = clampf(_pitch_deg - event.relative.y * sensitivity,
	                    -PITCH_LIMIT_DEG, PITCH_LIMIT_DEG)
	rotation_degrees.x = _pitch_deg
