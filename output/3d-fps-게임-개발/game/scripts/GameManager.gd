## GameManager.gd
## Autoload singleton: tracks global game state (score, health state,
## game-over flag, restart).  Other nodes emit signals into here;
## GameManager re-emits them so the HUD and other listeners stay decoupled.

extends Node

# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------
signal score_changed(new_score: int)
signal game_over_triggered()
signal game_restarted()
signal enemy_killed()

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
var score: int = 0
var enemies_killed: int = 0
var is_game_over: bool = false
var is_paused: bool = false

# Path to the main game scene — change if the file is renamed.
const WORLD_SCENE := "res://scenes/World.tscn"
const MAIN_MENU_SCENE := "res://scenes/MainMenu.tscn"

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # keep ticking even when tree is paused

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

## Call when the player dies.
func game_over() -> void:
	if is_game_over:
		return
	is_game_over = true
	emit_signal("game_over_triggered")
	# Pause physics/gameplay but keep UI alive.
	get_tree().paused = true

## Call to add points (enemy killed, objective reached, etc.).
func add_score(points: int) -> void:
	score += points
	emit_signal("score_changed", score)

## Call when an enemy is destroyed.
func register_enemy_kill() -> void:
	enemies_killed += 1
	add_score(100)
	emit_signal("enemy_killed")

## Restart: reset state, unpause, reload the world scene.
func restart() -> void:
	score = 0
	enemies_killed = 0
	is_game_over = false
	is_paused = false
	get_tree().paused = false
	emit_signal("game_restarted")
	get_tree().change_scene_to_file(WORLD_SCENE)

## Return to main menu.
func go_to_main_menu() -> void:
	score = 0
	enemies_killed = 0
	is_game_over = false
	is_paused = false
	get_tree().paused = false
	get_tree().change_scene_to_file(MAIN_MENU_SCENE)

## Toggle pause (called by the pause input action).
func toggle_pause() -> void:
	if is_game_over:
		return
	is_paused = !is_paused
	get_tree().paused = is_paused

# ---------------------------------------------------------------------------
# Input — handle restart / pause at the global level
# ---------------------------------------------------------------------------
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_just_pressed("restart") and is_game_over:
		restart()
	if event.is_action_just_pressed("pause") and not is_game_over:
		toggle_pause()
