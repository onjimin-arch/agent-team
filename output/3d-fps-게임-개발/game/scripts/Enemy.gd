## Enemy.gd
## State machine AI: IDLE → CHASE → ATTACK → DEAD
## Uses NavigationAgent3D for pathfinding (Godot 4 NavigationServer3D).
## Fully independent implementation — no GPL code referenced.
##
## [아이디어 참조] StanislavPetrovV/DOOM-style-Game (MIT)
## https://github.com/StanislavPetrovV/DOOM-style-Game
## NPC 상태머신 (idle/attack) 구조 아이디어 참조 (2D → 3D로 재설계).

extends CharacterBody3D

# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------
signal enemy_died()

# ---------------------------------------------------------------------------
# Exported configuration
# ---------------------------------------------------------------------------
@export var max_health: float = 60.0
@export var move_speed: float = 3.5
@export var detection_range: float = 15.0
@export var attack_range: float = 2.0
@export var attack_damage: float = 10.0
@export var attack_cooldown: float = 1.2
@export var score_reward: int = 100

# ---------------------------------------------------------------------------
# Node references
# ---------------------------------------------------------------------------
@onready var nav_agent: NavigationAgent3D = $NavigationAgent3D
@onready var attack_timer: Timer = $AttackTimer

# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------
enum EnemyState { IDLE, CHASE, ATTACK, DEAD }
var _state: EnemyState = EnemyState.IDLE
var _current_health: float = 0.0
var _player: CharacterBody3D = null

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	_current_health = max_health

	# Configure NavigationAgent
	nav_agent.path_desired_distance = 0.5
	nav_agent.target_desired_distance = 0.5

	# Attack cooldown timer
	attack_timer.wait_time = attack_cooldown
	attack_timer.one_shot = false
	attack_timer.timeout.connect(_on_attack_timer_timeout)
	attack_timer.start()

	# Find player in the scene tree
	_player = get_tree().get_first_node_in_group("player") as CharacterBody3D
	if not _player:
		# Deferred search in case player hasn't entered the tree yet
		call_deferred("_deferred_find_player")

func _deferred_find_player() -> void:
	_player = get_tree().get_first_node_in_group("player") as CharacterBody3D

func _physics_process(delta: float) -> void:
	if _state == EnemyState.DEAD:
		return
	if not _player:
		return

	var dist := global_position.distance_to(_player.global_position)

	# ---- State transitions ----
	match _state:
		EnemyState.IDLE:
			if dist <= detection_range:
				_change_state(EnemyState.CHASE)

		EnemyState.CHASE:
			if dist <= attack_range:
				_change_state(EnemyState.ATTACK)
			elif dist > detection_range * 1.5:
				_change_state(EnemyState.IDLE)
			else:
				_navigate_toward_player(delta)

		EnemyState.ATTACK:
			if dist > attack_range * 1.2:
				_change_state(EnemyState.CHASE)
			else:
				# Face the player while attacking
				_look_at_player()

func _change_state(new_state: EnemyState) -> void:
	_state = new_state
	match new_state:
		EnemyState.IDLE:
			velocity = Vector3.ZERO
		EnemyState.CHASE:
			nav_agent.set_target_position(_player.global_position)
		EnemyState.ATTACK:
			velocity = Vector3.ZERO

# ---------------------------------------------------------------------------
# Navigation movement — delta applied
# ---------------------------------------------------------------------------
func _navigate_toward_player(delta: float) -> void:
	# Refresh target every frame so the path stays accurate
	nav_agent.set_target_position(_player.global_position)

	if nav_agent.is_navigation_finished():
		return

	var next_pos := nav_agent.get_next_path_position()
	var direction := (next_pos - global_position).normalized()

	# Apply gravity
	if not is_on_floor():
		velocity.y -= GameSettings.gravity * delta
	else:
		velocity.y = 0.0

	velocity.x = direction.x * move_speed
	velocity.z = direction.z * move_speed

	move_and_slide()

	# Face movement direction
	if direction.length_squared() > 0.01:
		var look_target := global_position + Vector3(direction.x, 0, direction.z)
		look_at(look_target, Vector3.UP)

func _look_at_player() -> void:
	var target := Vector3(_player.global_position.x,
	                      global_position.y,
	                      _player.global_position.z)
	if global_position.distance_to(target) > 0.01:
		look_at(target, Vector3.UP)

# ---------------------------------------------------------------------------
# Attack
# ---------------------------------------------------------------------------
func _on_attack_timer_timeout() -> void:
	if _state != EnemyState.ATTACK or not _player:
		return
	# Call take_damage on the player's HealthComponent
	var health_comp = _player.get_node_or_null("HealthComponent")
	if health_comp and health_comp.has_method("take_damage"):
		health_comp.take_damage(attack_damage)

# ---------------------------------------------------------------------------
# Damage & death — called by WeaponController via take_damage()
# ---------------------------------------------------------------------------
func take_damage(amount: float) -> void:
	if _state == EnemyState.DEAD:
		return

	_current_health -= amount

	# Chase the attacker (player) as soon as hit
	if _state == EnemyState.IDLE and _player:
		_change_state(EnemyState.CHASE)

	if _current_health <= 0.0:
		_die()

func _die() -> void:
	_state = EnemyState.DEAD
	velocity = Vector3.ZERO
	emit_signal("enemy_died")
	GameManager.register_enemy_kill()
	# Remove from scene after a short delay (can add death animation here)
	var timer := get_tree().create_timer(0.5)
	await timer.timeout
	queue_free()
