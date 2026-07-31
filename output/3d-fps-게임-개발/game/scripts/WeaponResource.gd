## WeaponResource.gd
## Data-only Resource describing a weapon's stats.
## Instantiated as .tres files (pistol.tres, rifle.tres, etc.).
## No GPL or Unity code referenced — fully independent design.

class_name WeaponResource
extends Resource

## Display name shown in HUD.
@export var weapon_name: String = "Weapon"

## Damage per hit.
@export var damage: float = 25.0

## Seconds between shots (lower = faster fire rate).
@export var fire_rate: float = 0.5

## Maximum magazine capacity.
@export var max_ammo: int = 12

## How much screen-space recoil is applied per shot (degrees).
@export var recoil_amount: float = 1.5

## Sound effect to play on fire (optional — leave empty for silence).
@export var fire_sound: AudioStream = null

## Muzzle flash duration in seconds.
@export var muzzle_flash_time: float = 0.05
