## HUD.gd
## Connects to Player's HealthComponent and WeaponController to display:
##   - Health bar
##   - Ammo counter
##   - Score label
##   - Game-over overlay
## Fully independent implementation.

extends CanvasLayer

# ---------------------------------------------------------------------------
# Node references (populated in _ready)
# ---------------------------------------------------------------------------
var _health_bar: ProgressBar = null
var _ammo_label: Label = null
var _score_label: Label = null
var _game_over_overlay: ColorRect = null

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	# Resolve UI nodes relative to this CanvasLayer
	_health_bar       = get_node_or_null("BottomBar/HealthBar")
	_ammo_label       = get_node_or_null("BottomBar/AmmoLabel")
	_score_label      = get_node_or_null("BottomBar/ScoreLabel")
	_game_over_overlay = get_node_or_null("GameOverOverlay")

	# Connect to Player's HealthComponent
	var player := get_parent()   # HUD is a child of Player
	var health_comp := player.get_node_or_null("HealthComponent") as HealthComponent
	if health_comp:
		health_comp.health_changed.connect(_on_health_changed)
		health_comp.died.connect(_on_player_died)
		# Initialise health bar
		_update_health_bar(health_comp.current_health, health_comp.max_health)

	# Connect to WeaponController
	var weapon_ctrl := player.get_node_or_null("WeaponController")
	if weapon_ctrl:
		weapon_ctrl.ammo_changed.connect(_on_ammo_changed)

	# Connect to GameManager for score updates
	GameManager.score_changed.connect(_on_score_changed)
	GameManager.game_over_triggered.connect(_on_game_over)
	GameManager.game_restarted.connect(_on_game_restarted)

	# Hide overlay at start
	if _game_over_overlay:
		_game_over_overlay.visible = false

# ---------------------------------------------------------------------------
# Signal handlers
# ---------------------------------------------------------------------------
func _on_health_changed(new_health: float, max_hp: float) -> void:
	_update_health_bar(new_health, max_hp)

func _on_player_died() -> void:
	_update_health_bar(0.0, 100.0)

func _on_ammo_changed(current: int, max_ammo: int) -> void:
	if _ammo_label:
		_ammo_label.text = "%d / %d" % [current, max_ammo]

func _on_score_changed(new_score: int) -> void:
	if _score_label:
		_score_label.text = "Score: %d" % new_score

func _on_game_over() -> void:
	if _game_over_overlay:
		_game_over_overlay.visible = true

func _on_game_restarted() -> void:
	if _game_over_overlay:
		_game_over_overlay.visible = false

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
func _update_health_bar(current: float, maximum: float) -> void:
	if _health_bar:
		_health_bar.max_value = maximum
		_health_bar.value = current
