## WorldManager.gd
## Attached to the World root node.
## Bakes the NavigationMesh at runtime, then signals EnemySpawner to spawn.

extends Node3D

func _ready() -> void:
	var nav_region: NavigationRegion3D = $NavigationRegion3D
	var spawner: Node3D = $EnemySpawner

	if not nav_region:
		push_error("WorldManager: NavigationRegion3D not found.")
		return

	# Bake finished → tell spawner to go
	nav_region.bake_finished.connect(func():
		if spawner and spawner.has_method("spawn_all"):
			spawner.spawn_all()
	)

	# Start baking (async, runs on background thread in Godot 4)
	nav_region.bake_navigation_mesh()
