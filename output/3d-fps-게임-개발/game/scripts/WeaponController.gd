## WeaponController.gd
## Manages equipping weapons, firing (raycast hit-scan), ammo, and recoil.
## Fully independent implementation — no GPL or Unity code referenced.

extends Node

# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------
signal ammo_changed(current: int, max_ammo: int)
signal weapon_fired()
signal weapon_empty()

# ---------------------------------------------------------------------------
# Exported fields
# ---------------------------------------------------------------------------
@export var default_weapon: WeaponResource = null

# ---------------------------------------------------------------------------
# Node references (set in _ready)
# ---------------------------------------------------------------------------
var _raycast: RayCast3D = null
var _head: Node3D = null
var _weapon_holder: Node3D = null

# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------
var _equipped: WeaponResource = null
var _current_ammo: int = 0
var _fire_cooldown: float = 0.0   # seconds remaining until next shot allowed
var _is_reloading: bool = false

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	# Walk up the tree to find siblings
	var player := get_parent()
	_head          = player.get_node_or_null("Head")
	_weapon_holder = player.get_node_or_null("Head/WeaponHolder")
	_raycast       = player.get_node_or_null("Head/Camera3D/ShootRayCast")

	if default_weapon:
		equip(default_weapon)

func _process(delta: float) -> void:
	# Count down fire cooldown — delta applied
	if _fire_cooldown > 0.0:
		_fire_cooldown -= delta

	# Shooting input
	if Input.is_action_just_pressed("shoot") and not _is_reloading:
		_try_fire()

func _physics_process(_delta: float) -> void:
	pass  # reserved for future recoil recovery

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

## Equip a new weapon resource.
func equip(weapon: WeaponResource) -> void:
	_equipped = weapon
	_current_ammo = weapon.max_ammo
	_fire_cooldown = 0.0
	emit_signal("ammo_changed", _current_ammo, weapon.max_ammo)

## Reload the magazine instantly (animation can be added later).
func reload() -> void:
	if not _equipped:
		return
	_is_reloading = true
	# Simulate a 1.5-second reload delay via a one-shot timer
	var timer := get_tree().create_timer(1.5)
	await timer.timeout
	_current_ammo = _equipped.max_ammo
	_is_reloading = false
	emit_signal("ammo_changed", _current_ammo, _equipped.max_ammo)

# ---------------------------------------------------------------------------
# Firing logic
# ---------------------------------------------------------------------------
func _try_fire() -> void:
	if not _equipped:
		return

	if _current_ammo <= 0:
		emit_signal("weapon_empty")
		reload()
		return

	if _fire_cooldown > 0.0:
		return   # still in cooldown

	# Fire!
	_current_ammo -= 1
	_fire_cooldown = _equipped.fire_rate

	emit_signal("weapon_fired")
	emit_signal("ammo_changed", _current_ammo, _equipped.max_ammo)

	_perform_raycast()
	_apply_recoil()

func _perform_raycast() -> void:
	if not _raycast:
		return

	# RayCast3D must be enabled to query
	_raycast.enabled = true
	_raycast.force_raycast_update()

	if _raycast.is_colliding():
		var collider := _raycast.get_collider()
		var hit_point := _raycast.get_collision_point()
		var hit_normal := _raycast.get_collision_normal()

		# Attempt to call take_damage on the collider or its parent
		_try_deal_damage(collider)

		# Spawn a small hit effect (if a HitEffect scene exists)
		_spawn_hit_effect(hit_point, hit_normal)

func _try_deal_damage(collider: Object) -> void:
	if not collider or not _equipped:
		return

	# Direct method call — works for Enemy.gd which exposes take_damage()
	if collider.has_method("take_damage"):
		collider.take_damage(_equipped.damage)
	elif collider.get_parent() and collider.get_parent().has_method("take_damage"):
		collider.get_parent().take_damage(_equipped.damage)

func _apply_recoil() -> void:
	if not _head or not _equipped:
		return

	# Kick the camera up by recoil_amount degrees (cosmetic only — no aim deviation)
	var head_script := _head as Node3D
	if head_script and head_script.has_method("add_recoil"):
		head_script.add_recoil(_equipped.recoil_amount)
	else:
		# Fallback: directly nudge Head pitch
		var new_rot_x := _head.rotation_degrees.x - _equipped.recoil_amount
		_head.rotation_degrees.x = clampf(new_rot_x, -85.0, 85.0)

func _spawn_hit_effect(pos: Vector3, normal: Vector3) -> void:
	# If a HitEffect.tscn exists, instance it at the hit point.
	# This is optional; silently skip if file is absent.
	var path := "res://scenes/HitEffect.tscn"
	if ResourceLoader.exists(path):
		var packed := ResourceLoader.load(path) as PackedScene
		if packed:
			var effect := packed.instantiate()
			get_tree().current_scene.add_child(effect)
			effect.global_position = pos
			effect.look_at(pos + normal, Vector3.UP)
