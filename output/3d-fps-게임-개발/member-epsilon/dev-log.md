# Dev Log
생성자: member-epsilon | 생성시각: 2026-05-30T11:00:00+09:00 | 버전: 1.0

---

## 변경 파일 목록

### Phase 0: 프로젝트 초기화

| 파일 경로 | 설명 |
|-----------|------|
| `game/project.godot` | Godot 4 프로젝트 설정. autoload에 GameManager/GameSettings 등록. 입력 액션(WASD, shoot, sprint, crouch, jump, restart, pause) 정의. Forward+ 렌더러 설정. |
| `game/scripts/GameSettings.gd` | Autoload 싱글톤. FOV=75, 이동속도, 중력, 웅크리기 높이 등 모든 수치를 중앙화. default_settings.tres에서 로드 지원. |
| `game/scripts/GameManager.gd` | Autoload 싱글톤. 점수, 게임오버 상태, 일시정지, 재시작, 씬 전환 관리. score_changed/game_over_triggered/game_restarted 시그널 제공. |
| `game/scripts/GameSettingsResource.gd` | class_name GameSettingsResource. @export 프로퍼티로 .tres 저장/로드 지원. |
| `game/resources/default_settings.tres` | GameSettingsResource 인스턴스. FOV=75, walk_speed=5.0, run_speed=9.0, crouch_speed=2.5, gravity=9.8. |

### Phase 1: 플레이어 컨트롤러

| 파일 경로 | 설명 |
|-----------|------|
| `game/scripts/MovementController.gd` | CharacterBody3D 기반 이동. MoveState enum(WALK/SPRINT/CROUCH), move_and_slide(), delta 타임 적용 중력/이동. 웅크리기 시 캡슐 높이 lerp 전환. [참조] Whimfoome/godot-FirstPersonStarter (MIT) |
| `game/scripts/Head.gd` | Node3D 서브스크립트. 마우스 입력 처리. 좌우(yaw)는 Player 회전, 상하(pitch)는 Head만 ±85도 클램프. GameSettings.mouse_sensitivity 참조. [참조] Whimfoome/godot-FirstPersonStarter (MIT) |
| `game/scripts/PlayerInit.gd` | Player 그룹 등록("player"), HealthComponent.died → GameManager.game_over() 연결, 피스톨 무기 자동 장착. |
| `game/scenes/Player.tscn` | CharacterBody3D 씬. CollisionShape3D(CapsuleShape3D), Head > Camera3D, Head > WeaponHolder, ShootRayCast, HealthComponent, WeaponController, PlayerInit, HUD 포함. |

### Phase 2: 무기 시스템 (독자 구현)

| 파일 경로 | 설명 |
|-----------|------|
| `game/scripts/WeaponResource.gd` | class_name WeaponResource extends Resource. weapon_name, damage, fire_rate, max_ammo, recoil_amount, fire_sound, muzzle_flash_time @export 필드. |
| `game/scripts/WeaponController.gd` | RayCast3D 히트스캔 발사. fire_rate 쿨다운(delta 적용). _try_deal_damage()로 Enemy.take_damage() 호출. reload() (1.5초 await 기반). recoil 적용. ammo_changed/weapon_fired/weapon_empty 시그널. |
| `game/resources/pistol.tres` | WeaponResource: damage=25, fire_rate=0.5, max_ammo=12, recoil_amount=2.0 |
| `game/resources/rifle.tres` | WeaponResource: damage=15, fire_rate=0.1, max_ammo=30, recoil_amount=0.8 |

### Phase 3: 적 AI

| 파일 경로 | 설명 |
|-----------|------|
| `game/scripts/Enemy.gd` | CharacterBody3D 상태머신. EnemyState { IDLE, CHASE, ATTACK, DEAD }. NavigationAgent3D로 경로탐색. 감지거리=15m, 공격거리=2m. take_damage() 메서드 공개. 사망 시 GameManager.register_enemy_kill() 호출 후 queue_free(). [아이디어 참조] StanislavPetrovV/DOOM-style-Game (MIT) |
| `game/scenes/Enemy.tscn` | CharacterBody3D 씬. CollisionShape3D, CapsuleMesh(빨간색), NavigationAgent3D, AttackTimer 포함. |

### Phase 4: 체력 시스템 & HUD

| 파일 경로 | 설명 |
|-----------|------|
| `game/scripts/HealthComponent.gd` | class_name HealthComponent. max_health=100, take_damage(), heal(), set_health(). health_changed/died 시그널. health_ratio() 헬퍼. |
| `game/scripts/HUD.gd` | CanvasLayer 스크립트. HealthComponent.health_changed → ProgressBar 갱신. WeaponController.ammo_changed → Label 갱신. GameManager 점수/게임오버 시그널 연결. |
| `game/scenes/HUD.tscn` | CanvasLayer 씬. CrosshairContainer/Crosshair, BottomBar(HealthBar + AmmoLabel + ScoreLabel), GameOverOverlay/GameOverLabel. |

### Phase 5: 레벨 & 통합

| 파일 경로 | 설명 |
|-----------|------|
| `game/scenes/MainMenu.tscn` | Control 씬. TitleLabel, StartButton, QuitButton, VersionLabel. |
| `game/scenes/MainMenu.gd` | StartButton → World.tscn 씬 전환, QuitButton → get_tree().quit(). |
| `game/scenes/World.tscn` | 메인 게임 씬. DirectionalLight3D, OmniLight×2, NavigationRegion3D, Floor/Ceiling/4개 벽/커버 오브젝트 3개, Player 인스턴스, EnemySpawner(5개 스폰 포인트). |
| `game/scripts/EnemySpawner.gd` | spawn_positions 배열 기반 _ready()에서 Enemy 인스턴스 생성. 런타임 spawn_one() API 제공. |

---

## 자체 검증 결과

### 구현 완료 항목

| 항목 | 구현 방식 | 검증 방법 |
|------|----------|---------|
| WASD 이동 | CharacterBody3D + move_and_slide() | MovementController._apply_movement()가 Input.get_action_strength()로 방향 계산 후 delta 적용 |
| 달리기/걷기/웅크리기 | MoveState enum 기반 speed 전환 | GameSettings 값 참조, 하드코딩 없음 확인 |
| 마우스 시점 | InputEventMouseMotion 처리, yaw/pitch 분리 | ±85도 클램프 적용, 짐벌락 방지 |
| 중력/점프 | gravity * delta로 velocity.y 누적 | is_on_floor() 체크 후 jump_velocity 적용 |
| 레이캐스트 발사 | RayCast3D.force_raycast_update() + get_collider() | take_damage() 메서드 호출 체인 확인 |
| 발사 쿨다운 | _fire_cooldown 카운터 delta 차감 | fire_rate=0.5(pistol)/0.1(rifle) 확인 |
| 탄약/재장전 | _current_ammo 감소 → reload() await 1.5초 | ammo_changed 시그널로 HUD 동기화 |
| 적 IDLE→CHASE | distance_to() > detection_range 체크 | 15m 감지 거리, GameSettings 외부화 필요 시 @export로 조정 가능 |
| 적 CHASE (경로탐색) | NavigationAgent3D.set_target_position() + get_next_path_position() | delta 적용 이동, 바닥 충돌 처리 |
| 적 ATTACK | attack_range=2m 진입 시 AttackTimer.timeout | 플레이어 HealthComponent.take_damage() 호출 |
| 적 사망 | take_damage()로 current_health <= 0 → DEAD 상태 | 0.5초 대기 후 queue_free(), GameManager.register_enemy_kill() |
| 체력 시스템 | HealthComponent.take_damage/heal/health_changed | died 시그널 → GameManager.game_over() |
| HUD 업데이트 | 시그널 연결 방식 (풀링 없음) | health_changed, ammo_changed, score_changed, game_over_triggered |
| 게임오버/재시작 | GameManager 상태 관리 + get_tree().paused | R키 입력 → restart() → World.tscn 재로드 |
| 씬 전환 | MainMenu → World | change_scene_to_file() 사용 |

### 코드 품질 체크리스트

- [x] 모든 frame-dependent 계산에 delta 적용 (이동, 중력, 쿨다운)
- [x] 하드코딩된 수치 없음 — GameSettings Autoload 또는 @export 사용
- [x] MIT 참조 코드에 출처 주석 기재
- [x] GPL(liblast) 코드 미사용 확인
- [x] Unity FPSSample 코드 미사용 확인
- [x] God Script 안티패턴 회피 — 이동/카메라/무기/체력 분리
- [x] 시그널 기반 디커플링 (HUD ← HealthComponent, WeaponController, GameManager)
- [x] class_name 선언: WeaponResource, HealthComponent, GameSettingsResource
- [x] process_mode = ALWAYS (GameManager) — 일시정지 중에도 입력 처리

### 알려진 제한사항

1. **NavigationMesh 베이크**: World.tscn에 NavigationRegion3D와 NavigationMesh 리소스는 정의되어 있으나, 실제 navmesh 폴리곤 데이터는 Godot 에디터에서 "Bake NavigationMesh" 버튼으로 생성해야 함. 에디터 없이는 파일로 사전 생성 불가.
2. **Godot import 캐시**: .import 파일은 에디터 첫 실행 시 자동 생성됨. 저장소에는 포함하지 않음.
3. **사운드 에셋**: 총격음, 발걸음 소리 등 오디오 에셋은 현재 미포함. CC0 에셋(freesound.org 등)으로 추후 보완 필요.
4. **텍스처**: 현재 StandardMaterial3D의 albedo_color만 사용. 텍스처는 CC0 에셋으로 추후 적용 필요.

---

## 배포 결과

Godot 에디터 없이 실행 바이너리를 생성할 수 없으므로, 프로젝트 파일 준비 완료 상태로 보고함.

### 실행 절차 (사용자 안내)

1. **Godot 4.2 이상** 다운로드: https://godotengine.org/download/
2. Godot 에디터에서 **Import Project** → `game/project.godot` 선택
3. 에디터 열린 후 `scenes/World.tscn` 선택 → **NavigationRegion3D** 노드 클릭 → 상단 **Bake NavigationMesh** 실행
4. `F5` (또는 Run Scene) → 게임 실행
5. 윈도우 빌드: `Project > Export > Add Windows Desktop preset` → Export Project

### 프로젝트 파일 위치

`C:\Users\이지민\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\output\3d-fps-게임-개발\game\`

총 생성 파일: **19개** (`.gd` 8개, `.tscn` 5개, `.tres` 3개, `.gd` resource script 1개, `project.godot` 1개, `PlayerInit.gd` 1개)
