## PlayerInit.gd
## Lightweight script that registers the Player in the "player" group
## so Enemy.gd can find it via get_tree().get_first_node_in_group("player").
## Also wires HealthComponent.died → GameManager.game_over().

extends Node

func _ready() -> void:
	var player := get_parent()
	player.add_to_group("player")

	# Wire health → game over
	var health_comp := player.get_node_or_null("HealthComponent") as HealthComponent
	if health_comp:
		health_comp.died.connect(_on_player_died)

	# Give WeaponController its default weapon (pistol)
	var weapon_ctrl := player.get_node_or_null("WeaponController")
	if weapon_ctrl:
		var pistol_path := "res://resources/pistol.tres"
		if ResourceLoader.exists(pistol_path):
			var pistol := ResourceLoader.load(pistol_path) as WeaponResource
			if pistol:
				weapon_ctrl.default_weapon = pistol
				weapon_ctrl.equip(pistol)

func _on_player_died() -> void:
	GameManager.game_over()
