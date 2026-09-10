## MovementController.gd
## Handles all player movement: WASD walk/run, crouch, jump, gravity.
## Attached to the Player (CharacterBody3D) node.
##
## [참조] Whimfoome/godot-FirstPersonStarter (MIT)
## https://github.com/Whimfoome/godot-FirstPersonStarter
## move_and_slide() 패턴, sprint/crouch 상태 전환 패턴 참조.
##
## [아이디어 참조] expressobits/character-controller (MIT)
## https://github.com/expressobits/character-controller
## Walk/Crouch/Sprint 상태 모듈 분리 패턴 참조.

extends CharacterBody3D

# ---------------------------------------------------------------------------
# Node references (assigned in _ready via $Path)
# ---------------------------------------------------------------------------
@onready var head: Node3D = $Head
@onready var collision_shape: CollisionShape3D = $CollisionShape3D
@onready var health_component: Node = $HealthComponent

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
enum MoveState { WALK, SPRINT, CROUCH }
var _current_state: MoveState = MoveState.WALK

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
var _target_height: float       # lerp target for capsule height
var _current_height: float      # actual capsule half-height this frame

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	_current_height = GameSettings.stand_height
	_target_height  = GameSettings.stand_height
	_apply_capsule_height(_current_height)

func _physics_process(delta: float) -> void:
	_update_state()
	_apply_gravity(delta)
	_apply_movement(delta)
	_update_crouch_height(delta)
	move_and_slide()

# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------
func _update_state() -> void:
	if Input.is_action_pressed("crouch"):
		_current_state = MoveState.CROUCH
	elif Input.is_action_pressed("sprint") and is_on_floor():
		_current_state = MoveState.SPRINT
	else:
		_current_state = MoveState.WALK

func _current_speed() -> float:
	match _current_state:
		MoveState.SPRINT:  return GameSettings.run_speed
		MoveState.CROUCH:  return GameSettings.crouch_speed
		_:                 return GameSettings.walk_speed

# ---------------------------------------------------------------------------
# Gravity  — delta applied; uses project physics gravity setting
# ---------------------------------------------------------------------------
func _apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= GameSettings.gravity * delta
	else:
		if Input.is_action_just_pressed("jump") and _current_state != MoveState.CROUCH:
			velocity.y = GameSettings.jump_velocity

# ---------------------------------------------------------------------------
# Horizontal movement — delta applied via speed * delta in direction vector
# ---------------------------------------------------------------------------
func _apply_movement(delta: float) -> void:
	var input_dir := Vector2.ZERO
	input_dir.x = Input.get_action_strength("move_right")  - Input.get_action_strength("move_left")
	input_dir.y = Input.get_action_strength("move_backward") - Input.get_action_strength("move_forward")

	# Transform input to world-space direction relative to player facing
	var direction := (transform.basis * Vector3(input_dir.x, 0.0, input_dir.y)).normalized()

	var speed := _current_speed()

	if direction.length_squared() > 0.0:
		velocity.x = direction.x * speed
		velocity.z = direction.z * speed
	else:
		# Decelerate to zero using lerp for a snappier feel
		velocity.x = move_toward(velocity.x, 0.0, speed * delta * 10.0)
		velocity.z = move_toward(velocity.z, 0.0, speed * delta * 10.0)

# ---------------------------------------------------------------------------
# Crouch — smoothly interpolate capsule height
# ---------------------------------------------------------------------------
func _update_crouch_height(delta: float) -> void:
	_target_height = GameSettings.crouch_height if _current_state == MoveState.CROUCH \
	                                             else GameSettings.stand_height

	_current_height = lerp(_current_height, _target_height,
	                       GameSettings.crouch_transition_speed * delta)
	_apply_capsule_height(_current_height)

	# Move Head node down/up proportionally
	head.position.y = _current_height - 0.1

func _apply_capsule_height(h: float) -> void:
	var shape := collision_shape.shape as CapsuleShape3D
	if shape:
		shape.height = h
	collision_shape.position.y = h * 0.5
