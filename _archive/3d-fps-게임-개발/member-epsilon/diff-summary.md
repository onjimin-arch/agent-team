# Diff Summary
생성자: member-epsilon | 생성시각: 2026-05-30T11:00:00+09:00

---

## 신규 생성 파일 (19개)

### 프로젝트 루트

```
game/project.godot                     (+85 lines)   Godot 4 프로젝트 설정, autoload, input map
```

### scripts/

```
game/scripts/GameSettings.gd           (+55 lines)   Autoload: 수치 중앙화 싱글톤
game/scripts/GameManager.gd            (+75 lines)   Autoload: 게임 상태 관리 싱글톤
game/scripts/GameSettingsResource.gd   (+15 lines)   Resource class: .tres 직렬화 지원
game/scripts/MovementController.gd     (+95 lines)   CharacterBody3D 이동 컨트롤러
game/scripts/Head.gd                   (+50 lines)   1인칭 마우스 룩 (피치/요 분리)
game/scripts/PlayerInit.gd             (+35 lines)   그룹 등록, 무기/체력 배선
game/scripts/WeaponResource.gd         (+25 lines)   무기 데이터 Resource class
game/scripts/WeaponController.gd       (+110 lines)  레이캐스트 발사, 쿨다운, 재장전
game/scripts/HealthComponent.gd        (+60 lines)   범용 체력 컴포넌트
game/scripts/HUD.gd                    (+65 lines)   HUD 시그널 연결 및 갱신
game/scripts/Enemy.gd                  (+125 lines)  IDLE/CHASE/ATTACK/DEAD 상태머신 AI
game/scripts/EnemySpawner.gd           (+40 lines)   레벨 로드 시 적 인스턴스 생성
```

### scenes/

```
game/scenes/Player.tscn                (+70 lines)   플레이어 씬 (CharacterBody3D)
game/scenes/Enemy.tscn                 (+35 lines)   적 씬 (CharacterBody3D + NavigationAgent3D)
game/scenes/HUD.tscn                   (+55 lines)   HUD CanvasLayer 씬
game/scenes/MainMenu.tscn              (+55 lines)   메인 메뉴 씬
game/scenes/MainMenu.gd                (+20 lines)   메인 메뉴 버튼 로직
game/scenes/World.tscn                 (+120 lines)  메인 게임 씬 (레벨 + 조명 + 내비게이션)
```

### resources/

```
game/resources/default_settings.tres  (+12 lines)   GameSettingsResource 인스턴스
game/resources/pistol.tres             (+10 lines)   피스톨 WeaponResource (damage=25, fire_rate=0.5)
game/resources/rifle.tres              (+10 lines)   라이플 WeaponResource (damage=15, fire_rate=0.1)
```

---

## 변경 파일

없음 (신규 프로젝트)

---

## 삭제 파일

없음

---

## 라이선스 귀속 요약

| 파일 | 참조 레포 | 라이선스 | 참조 유형 |
|------|----------|---------|---------|
| MovementController.gd | Whimfoome/godot-FirstPersonStarter | MIT | 코드 패턴 참조 (주석 기재됨) |
| Head.gd | Whimfoome/godot-FirstPersonStarter | MIT | 코드 패턴 참조 (주석 기재됨) |
| Enemy.gd | StanislavPetrovV/DOOM-style-Game | MIT | 아이디어 참조 (주석 기재됨) |
| GameSettings.gd | StanislavPetrovV/DOOM-style-Game | MIT | 아이디어 참조 (주석 기재됨) |
| WeaponController.gd | 독자 구현 | — | 없음 |
| HealthComponent.gd | 독자 구현 | — | 없음 |
| HUD.gd | 독자 구현 | — | 없음 |
| GameManager.gd | 독자 구현 | — | 없음 |

GPL(unfa/liblast) 코드: **미사용** 확인
Unity FPSSample 코드: **미사용** 확인

---

## 아키텍처 다이어그램

```
World (Node3D)
├── DirectionalLight3D
├── OmniLight3D × 2
├── WorldEnvironment
├── NavigationRegion3D
│   ├── Floor (StaticBody3D)
│   ├── Ceiling (StaticBody3D)
│   ├── WallNorth/South/East/West (StaticBody3D × 4)
│   └── Cover1/2/3 (StaticBody3D × 3)
├── Player (CharacterBody3D) [group: "player"]
│   ├── CollisionShape3D
│   ├── Head (Node3D) — Head.gd (마우스 룩)
│   │   ├── Camera3D (FOV = GameSettings.fov)
│   │   │   └── ShootRayCast (RayCast3D)
│   │   └── WeaponHolder (Node3D)
│   ├── WeaponController (Node) — 발사/탄약
│   ├── HealthComponent (Node) — HP/시그널
│   ├── PlayerInit (Node) — 그룹 등록/배선
│   └── HUD (CanvasLayer)
│       ├── Crosshair
│       ├── BottomBar (HealthBar + AmmoLabel + ScoreLabel)
│       └── GameOverOverlay
├── EnemySpawner (Node3D)
└── Enemy instances × 5 (CharacterBody3D)
    ├── CollisionShape3D
    ├── MeshInstance3D
    ├── NavigationAgent3D
    └── AttackTimer

Autoloads (always present):
  GameManager — 점수, 게임오버, 재시작, 일시정지
  GameSettings — FOV, 속도, 중력 등 수치 중앙화
```
