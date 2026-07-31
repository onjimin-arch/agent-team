## GameSettingsResource.gd
## Serialisable Resource class so settings can be saved to / loaded from disk.
## Mirrors the properties in the GameSettings autoload.

class_name GameSettingsResource
extends Resource

@export var fov: float = 75.0
@export var mouse_sensitivity: float = 0.3
@export var walk_speed: float = 5.0
@export var run_speed: float = 9.0
@export var crouch_speed: float = 2.5
@export var jump_velocity: float = 4.5
@export var gravity: float = 9.8
@export var stand_height: float = 1.8
@export var crouch_height: float = 0.9
