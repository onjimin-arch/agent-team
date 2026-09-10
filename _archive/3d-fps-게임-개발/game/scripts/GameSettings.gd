## GameSettings.gd
## Autoload singleton: central store for all tunable game constants.
## No hardcoded numbers anywhere else — all values load from here.
##
## [아이디어 참조] StanislavPetrovV/DOOM-style-Game (MIT)
## https://github.com/StanislavPetrovV/DOOM-style-Game
## settings.py 중앙화 패턴을 Godot 4 Autoload로 변환.

extends Node

# ---------------------------------------------------------------------------
# Camera / Look
# ---------------------------------------------------------------------------
var fov: float = 75.0
var mouse_sensitivity: float = 0.3

# ---------------------------------------------------------------------------
# Movement speeds  (m/s)
# ---------------------------------------------------------------------------
var walk_speed: float = 5.0
var run_speed: float = 9.0
var crouch_speed: float = 2.5
var jump_velocity: float = 4.5

# ---------------------------------------------------------------------------
# Physics
# ---------------------------------------------------------------------------
var gravity: float = 9.8

# ---------------------------------------------------------------------------
# Crouch geometry
# ---------------------------------------------------------------------------
var stand_height: float = 1.8
var crouch_height: float = 0.9
var crouch_transition_speed: float = 8.0

# ---------------------------------------------------------------------------
# Persistence helper — save/load via a .tres resource if desired
# ---------------------------------------------------------------------------
func load_from_resource(res: Resource) -> void:
	if not res:
		return
	fov                    = res.get("fov")               if res.get("fov")               != null else fov
	mouse_sensitivity      = res.get("mouse_sensitivity") if res.get("mouse_sensitivity") != null else mouse_sensitivity
	walk_speed             = res.get("walk_speed")        if res.get("walk_speed")        != null else walk_speed
	run_speed              = res.get("run_speed")         if res.get("run_speed")         != null else run_speed
	crouch_speed           = res.get("crouch_speed")      if res.get("crouch_speed")      != null else crouch_speed
	jump_velocity          = res.get("jump_velocity")     if res.get("jump_velocity")     != null else jump_velocity
	gravity                = res.get("gravity")           if res.get("gravity")           != null else gravity

func _ready() -> void:
	# Attempt to load saved settings from disk; silently skip if absent.
	var path := "res://resources/default_settings.tres"
	if ResourceLoader.exists(path):
		var res = ResourceLoader.load(path)
		load_from_resource(res)
