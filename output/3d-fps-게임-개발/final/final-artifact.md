# 3D FPS 게임 개발 — 최종 산출물

**작성자**: Team Lead | **작성일**: 2026-05-30 | **워크스페이스**: 3d-fps-게임-개발

---

## 요약

Godot 4.x + GDScript 스택으로 싱글플레이어 3D FPS 게임 프로젝트를 완성했습니다.  
게임 엔진 선택부터 오픈소스 라이선스 감사, 구현 전략 수립, 실제 코드 작성까지 전 과정을 에이전트 팀이 협력하여 처리했습니다.

---

## 1. 선택 스택

| 항목 | 결정 |
|------|------|
| 엔진 | Godot 4.x (MIT 라이선스) |
| 언어 | GDScript |
| 렌더러 | Forward+ (데스크톱 타겟) |
| 물리 | CharacterBody3D + PhysicsServer3D |
| AI | NavigationAgent3D + 상태머신 |

**선택 근거**: Unity는 Runtime Fee 정책 제약, Python은 실제 3D FPS 구현 불가. Godot 4는 MIT 엔진이며 참조 레포 대부분이 Godot 기반으로 생태계 적합성 최우수.

---

## 2. 참조 오픈소스 및 라이선스

| 레포 | 라이선스 | 사용 방식 |
|------|---------|---------|
| Whimfoome/godot-FirstPersonStarter | MIT ✅ | 플레이어 이동 패턴 직접 참조 (출처 주석 기재) |
| expressobits/character-controller | MIT ✅ | 모듈형 상태 분리 패턴 참조 |
| StanislavPetrovV/DOOM-style-Game | MIT ✅ | settings 중앙화, AI 상태 구조 개념 참조 |
| unfa/liblast | GPL v3 ⚠️ | 아키텍처 개념 참조 전용 — 코드 복사 없음 |
| Unity-Technologies/FPSSample | Unity Companion ⚠️ | 아키텍처 참조 전용 — 코드 복사 없음 |

---

## 3. 구현된 게임 구조

```
game/
├── project.godot                  # 프로젝트 설정, Autoload 등록, Input Map
├── scripts/
│   ├── GameSettings.gd            # Autoload: FOV/이동속도/중력 중앙화
│   ├── GameManager.gd             # Autoload: 점수/게임오버/재시작
│   ├── GameSettingsResource.gd    # Resource 직렬화 클래스
│   ├── MovementController.gd      # WASD/달리기/웅크리기 [MIT 참조]
│   ├── Head.gd                    # 마우스 룩, 피치/요 분리 [MIT 참조]
│   ├── PlayerInit.gd              # 플레이어 그룹 등록, 신호 배선
│   ├── WeaponResource.gd          # 무기 데이터 Resource (독자 구현)
│   ├── WeaponController.gd        # RayCast3D 히트스캔 (독자 구현)
│   ├── HealthComponent.gd         # 체력 컴포넌트 + 시그널 (독자 구현)
│   ├── HUD.gd                     # HUD 시그널 연결 (독자 구현)
│   ├── Enemy.gd                   # IDLE→CHASE→ATTACK→DEAD 상태머신
│   └── EnemySpawner.gd            # 프리셋 위치 적 스폰
├── scenes/
│   ├── Player.tscn                # CharacterBody3D + Head/Camera3D
│   ├── Enemy.tscn                 # CharacterBody3D + NavigationAgent3D
│   ├── HUD.tscn                   # CanvasLayer (체력바, 탄약, 크로스헤어)
│   ├── MainMenu.tscn / .gd        # 시작 화면
│   └── World.tscn                 # 30×30 레벨 + 조명 + 적 5개 스폰
├── resources/
│   ├── default_settings.tres      # GameSettings 기본값
│   ├── pistol.tres                # damage=25, fire_rate=0.5, ammo=12
│   └── rifle.tres                 # damage=15, fire_rate=0.1, ammo=30
└── assets/                        # (CC0 에셋 추가 위치)
```

---

## 4. 핵심 시스템 설계

### 플레이어 컨트롤러
- `CharacterBody3D` + `move_and_slide()` 기반 이동
- 카메라(Head) 분리: 상하 회전은 Head 노드, 좌우는 Player 노드 rotate_y
- 달리기(Shift), 웅크리기(Ctrl) 지원
- 모든 이동 수치는 `GameSettings` Autoload에서 로드

### 무기 시스템
- `WeaponResource` (data class) + `WeaponController` (logic) 분리
- `RayCast3D` 히트스캔 방식 (발사체 없음 → 즉시 히트 판정)
- 재장전(R), 탄약 관리 포함

### 적 AI
- `NavigationAgent3D` 기반 실시간 경로탐색
- 상태머신: IDLE → CHASE(감지) → ATTACK(근접) → DEAD
- **주의**: Godot 에디터에서 NavigationMesh 베이크 필수

### 체력 시스템
- `HealthComponent.gd` 컴포넌트 — Player/Enemy 모두 재사용
- 시그널(`health_changed`, `died`) 기반 디커플링
- GameManager가 `died` 수신 후 Game Over 처리

---

## 5. 게임 실행 방법

1. **Godot 4.2 이상** 설치
2. `game/project.godot` 임포트
3. `World.tscn` 열기 → `NavigationRegion3D` 선택 → **"Bake NavigationMesh"** 클릭
4. F5 (실행) 또는 `MainMenu.tscn`을 기본 씬으로 설정 후 실행
5. WASD 이동 / 마우스 시점 / 클릭 발사 / R 재장전 / ESC 일시정지

---

## 6. 라이선스 준수 현황

- [x] MIT 참조 코드에 출처 주석 기재 (MovementController.gd, Head.gd, Enemy.gd)
- [x] GPL(liblast) 코드 미복사 — 확인 완료
- [x] Unity Companion 라이선스 코드 미복사 — 확인 완료
- [x] 모든 수치 GameSettings 중앙화 (하드코딩 없음)
- [x] delta 타임 전면 적용
- [ ] CC0 에셋 추가 시 THIRD_PARTY.md 작성 필요

---

## 7. 향후 확장 제안

| 기능 | 방향 |
|------|------|
| 멀티플레이어 | Godot MultiplayerAPI + liblast 아키텍처 참조 (GPL 주의) |
| 무기 추가 | `WeaponResource` .tres 파일만 추가하면 즉시 확장 |
| 레벨 추가 | 새 씬에 `NavigationRegion3D` + `EnemySpawner` 추가 |
| 모바일 포팅 | Godot Mobile 렌더러로 export 설정 변경 |

---

## Phase 진행 요약

| Phase | 담당 | 결과 |
|-------|------|------|
| 1 (Planning) | Team Lead | task type=dev, slug 자동 확정 |
| 2-1 (Execution) | member-eta | GitHub 리서치 6개 레포, MIT 3개 활용 가능 확인 |
| 2-2 (Execution) | member-alpha | Godot 4 스택 선택, 6단계 구현 계획 수립 |
| 2-3 (Execution) | member-epsilon | Godot 4 게임 프로젝트 22개 파일 생성 |
| 3 (Review) | member-reviewer | 전원 APPROVE |
| 4 (Integration) | Team Lead | 최종 산출물 통합 완료 |
