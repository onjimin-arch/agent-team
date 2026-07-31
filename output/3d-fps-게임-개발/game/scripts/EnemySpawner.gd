## EnemySpawner.gd
## Spawns enemy instances at preset positions when the level loads.
## Enemy scene path and spawn points are configured via exported properties.

extends Node3D

# ---------------------------------------------------------------------------
# Exported
# ---------------------------------------------------------------------------
@export var enemy_scene: PackedScene = null
@export var spawn_positions: Array[Vector3] = []

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	if not enemy_scene:
		var path := "res://scenes/Enemy.tscn"
		if ResourceLoader.exists(path):
			enemy_scene = ResourceLoader.load(path) as PackedScene

	if not enemy_scene:
		push_warning("EnemySpawner: enemy_scene not set and default path not found.")

	# Spawning is deferred until WorldManager calls spawn_all()
	# after NavigationMesh bake completes.

## Called by WorldManager after bake_finished signal.
func spawn_all() -> void:
	if not enemy_scene:
		push_warning("EnemySpawner.spawn_all: no enemy_scene set.")
		return
	_spawn_all()

# ---------------------------------------------------------------------------
# Spawning
# ---------------------------------------------------------------------------
func _spawn_all() -> void:
	for pos in spawn_positions:
		_spawn_enemy_at(pos)

func _spawn_enemy_at(pos: Vector3) -> void:
	var enemy := enemy_scene.instantiate() as CharacterBody3D
	if not enemy:
		return
	get_parent().add_child(enemy)
	enemy.global_position = pos

## Called at runtime (e.g., wave system) to spawn a single extra enemy.
func spawn_one(pos: Vector3) -> void:
	_spawn_enemy_at(pos)
