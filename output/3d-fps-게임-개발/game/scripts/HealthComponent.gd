## HealthComponent.gd
## Reusable component for anything that can take damage or heal.
## Attach as a child Node to Player, Enemy, or any damageable object.
## Fully independent implementation.

class_name HealthComponent
extends Node

# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------
signal health_changed(new_health: float, max_health: float)
signal died()

# ---------------------------------------------------------------------------
# Exported
# ---------------------------------------------------------------------------
@export var max_health: float = 100.0
@export var invincible: bool = false      # set true during cutscenes, etc.

# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------
var current_health: float = 0.0

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
func _ready() -> void:
	current_health = max_health

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

## Inflict damage. Ignored if invincible or already dead.
func take_damage(amount: float) -> void:
	if invincible:
		return
	if current_health <= 0.0:
		return

	current_health = maxf(current_health - amount, 0.0)
	emit_signal("health_changed", current_health, max_health)

	if current_health <= 0.0:
		emit_signal("died")

## Restore health, capped at max_health.
func heal(amount: float) -> void:
	if current_health <= 0.0:
		return   # cannot heal when dead

	current_health = minf(current_health + amount, max_health)
	emit_signal("health_changed", current_health, max_health)

## Set health directly (useful for save-game loading).
func set_health(value: float) -> void:
	current_health = clampf(value, 0.0, max_health)
	emit_signal("health_changed", current_health, max_health)

## True if the owner is alive.
func is_alive() -> bool:
	return current_health > 0.0

## Health as 0.0 – 1.0 ratio (for ProgressBar).
func health_ratio() -> float:
	return current_health / max_health if max_health > 0.0 else 0.0
