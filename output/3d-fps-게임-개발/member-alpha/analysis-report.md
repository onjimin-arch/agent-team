# 구현 방향 분석 보고서
생성자: member-alpha | 생성시각: 2026-05-30T10:00:00+09:00 | 버전: 1.0

---

## 개요

### 선택 스택과 근거

**선택 스택: Godot 4.x + GDScript**

| 항목 | 결정 |
|------|------|
| 엔진 | Godot 4.x (최신 안정 버전) |
| 언어 | GDScript (주) / C# (성능 병목 발생 시 선택적 도입) |
| 렌더러 | Godot 4 Forward+ (데스크톱 타겟) |
| 플랫폼 | Windows / Linux / macOS (데스크톱 멀티플랫폼) |
| 빌드 방식 | Godot 에디터 내 Export (별도 빌드 툴 불필요) |

**선택 근거 (vs 옵션 B Unity, 옵션 C Python)**

1. **라이선스 자유도**: Godot 4는 MIT 라이선스 엔진이므로 엔진 자체 제약이 없음. Unity는 수익화 시 Runtime Fee 정책 적용 대상이며 소스 비공개.
2. **오픈소스 생태계 적합성**: 탐색된 6개 레포 중 MIT 라이선스로 직접 활용 가능한 레포들이 모두 Godot 기반이며 Asset Library에 등록됨.
3. **빠른 프로토타이핑**: GDScript는 Python 유사 문법으로 초기 개발 속도가 Unity C# 대비 빠르며, 실행 환경 별도 설치 불필요.
4. **참조 레포 품질**: Whimfoome/godot-FirstPersonStarter(MIT, ~909 stars, 2026-04 최신 릴리즈)와 expressobits/character-controller(MIT, ~300 stars)가 Asset Library 에셋으로 등록됨.
5. **Python(옵션 C) 제외 이유**: 레이캐스팅 기반 의사(pseudo) 3D 구조로 실제 3D FPS 불가. 알고리즘 학습 전용으로만 유효.

---

### 목표 결과물 정의

**장르**: 싱글플레이어 3D FPS (First-Person Shooter)
**플레이어 수**: 1인 (싱글플레이어 완성 후 멀티플레이어 확장 구조 설계)
**핵심 루프**:
- FPS 이동 (걷기/달리기/웅크리기)
- 레이캐스트 기반 총격 (즉시 히트 판정)
- 적 AI (경로탐색, 공격)
- 체력/사망/재시작 시스템
- 최소 1개 플레이어블 레벨

**목표 완성 수준**: 플레이어블 데모 (5~10분 분량의 실행 가능한 게임)

---

## 분석 결과

### 스택 선택 결정

엔진: Godot 4.x
언어: GDScript
렌더러: Forward+ (기본값 유지)
물리: Godot 내장 PhysicsServer3D (CharacterBody3D 기반)
AI: Godot NavigationServer3D (NavigationAgent3D)
오디오: Godot AudioStreamPlayer3D

**Godot 4 핵심 노드 구조 결정**:

```
World (Node3D)
├── Player (CharacterBody3D)
│   ├── CollisionShape3D
│   ├── Head (Node3D)            - 카메라 피치 분리
│   │   └── Camera3D
│   ├── WeaponHolder (Node3D)
│   └── HUD (CanvasLayer)
├── NavigationRegion3D           - AI 경로탐색 영역
├── EnemySpawner (Node3D)
├── Level (Node3D)
└── GameManager (Autoload Singleton)
```

---

### 오픈소스 참조 범위 (MIT만, 출처 명기 규칙 포함)

#### 직접 참조 가능 레포 (MIT 라이선스 확인됨)

| # | 레포 | 참조할 구체적 내용 | 위치 |
|---|------|----------------|------|
| A | Whimfoome/godot-FirstPersonStarter (MIT) | CharacterBody3D 이동 로직, 마우스 피치/요 분리 패턴, Sprint 구현 | Player/MovementController.gd, Player/Head.gd |
| B | expressobits/character-controller (MIT) | Walk/Crouch/Sprint 상태 모듈 분리 패턴, FPS 헤드밥 구현 | addons/character_controller/ 구조 패턴 |
| C | StanislavPetrovV/DOOM-style-Game (MIT) | settings 중앙화 패턴을 Godot GameSettings Resource로 변환, NPC 경로탐색 알고리즘 구조 | settings.py, npc.py |

#### 아키텍처 참조 전용 (코드 직접 복사 금지)

| # | 레포 | 참조 목적 | 제약 |
|---|------|---------|------|
| D | unfa/liblast (GPL v3) | Godot 4 멀티플레이어 아키텍처 구조 파악 | 코드 직접 복사 절대 금지 |
| E | Unity-Technologies/FPSSample (Unity Companion License) | 무기 데이터 구조 패턴, 네트워크 권한 분리 개념 | Unity 전용 라이선스, 구조 개념만 참조 |

#### 사용 제외 레포

| # | 레포 | 제외 사유 |
|---|------|---------|
| F | InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source- | MIT 라이선스 미확인(추정 only), Unity 전용 구조 |

#### 출처 명기 규칙 (epsilon 준수 사항)

코드 파일 상단 또는 관련 함수 상단에 다음 형식으로 출처 주석 기재:

```gdscript
# [참조] Whimfoome/godot-FirstPersonStarter (MIT)
# https://github.com/Whimfoome/godot-FirstPersonStarter
# Player/MovementController.gd 의 move_and_slide() 패턴 참조
```

- 아키텍처 아이디어만 참조한 경우: `# [아이디어 참조]` 접두사 사용
- GPL 레포(liblast)는 어떤 형태로도 코드 복사 금지. 참조 주석도 작성하지 않음.

---

### 독자 구현 범위

다음 시스템은 참조 없이 완전히 독자 구현한다:

| 시스템 | 독자 구현 이유 | 핵심 설계 방향 |
|--------|-------------|-------------|
| 무기 시스템 | 참조 레포들의 무기 구조가 Unity ScriptableObject 기반이라 Godot Resource로 재설계 필요 | WeaponResource (Godot Resource) 데이터 기반 설계 |
| 적 AI | npc.py 알고리즘은 2D 레이캐스팅 전용. 3D NavigationAgent3D와 결합 필요 | NavigationAgent3D + 상태머신 (Idle/Chase/Attack/Dead) |
| HUD/UI | 게임 특유의 UI 디자인 | Godot CanvasLayer + Control 노드 구성 |
| GameManager | 게임 상태(점수, 체력, 레벨) 전역 관리 | Godot Autoload Singleton 패턴 |
| 레벨 디자인 | 오픈소스 레포의 데모 레벨 사용 불가 | MeshInstance3D + CSGBox3D로 플레이어블 레벨 1개 제작 |
| 사운드 시스템 | 레포별 사운드 에셋 라이선스 확인 불가 | AudioStreamPlayer3D, CC0 에셋 사용 |

---

### 구현 단계별 계획 (epsilon이 실행할 순서)

#### Phase 0: 프로젝트 초기화

목표: Godot 4 프로젝트 생성 및 기본 구조 세팅

작업:
1. Godot 4 프로젝트 생성 (project.godot)
2. 폴더 구조 생성: /scenes/, /scripts/, /resources/, /assets/, /addons/
3. GameManager Autoload Singleton 등록
4. GameSettings Resource 클래스 정의 (FOV, 이동속도, 중력 등 중앙화)

완료 기준: 빈 씬에서 게임 실행 가능

---

#### Phase 1: 플레이어 컨트롤러

목표: 1인칭 이동 및 카메라 시스템 구현
참조: Whimfoome/godot-FirstPersonStarter (MIT)

작업:
1. Player 씬 생성 (CharacterBody3D + CollisionShape3D + Head/Camera3D)
2. MovementController.gd 작성:
   - move_and_slide() 기반 이동
   - 중력 처리 (get_gravity())
   - 달리기/걷기 전환 (shift 키), 웅크리기 (ctrl 키)
   - delta 타임 필수 적용 (안티패턴 회피)
3. Head.gd (마우스 입력):
   - Input.set_mouse_mode(CAPTURED)
   - 좌우 회전: Player 노드 rotate_y()
   - 상하 회전: Head 노드 rotate_x() + clamp(-85~85도)
4. GameSettings Resource에서 이동속도/FOV 로드

완료 기준: WASD 이동 + 마우스 시점 이동 정상 동작

---

#### Phase 2: 무기 시스템 (독자 구현)

목표: 레이캐스트 기반 총격 + 데이터 기반 무기 설계
참조: 없음 (독자 구현)

작업:
1. WeaponResource 클래스 정의 (Resource 상속):
   - weapon_name: String
   - damage: float
   - fire_rate: float
   - max_ammo: int
   - recoil_amount: float
2. WeaponController.gd 작성:
   - RayCast3D 노드 활용 (Camera3D 자식)
   - 발사: Input.is_action_just_pressed("shoot")
   - ray.get_collider()로 피격 대상 감지 후 take_damage(damage) 호출
   - fire_rate 기반 쿨다운
3. 기본 무기 Resource 파일 2종 생성 (Pistol, Rifle)
4. 총구 화염 효과 (GPUParticles3D 또는 flash)

완료 기준: 클릭 시 레이캐스트 발사, 벽/오브젝트 히트 확인 가능

---

#### Phase 3: 적 AI

목표: 플레이어를 추적하고 공격하는 적 NPC
참조: StanislavPetrovV/DOOM-style-Game AI 상태 구조 (개념 참조)

작업:
1. NavigationRegion3D 설정 (레벨에 NavMesh 베이크)
2. Enemy 씬 생성: CharacterBody3D + NavigationAgent3D + CollisionShape3D + MeshInstance3D
3. Enemy.gd 상태머신 구현:
   - enum EnemyState { IDLE, CHASE, ATTACK, DEAD }
   - IDLE: 대기, 플레이어 감지 시 CHASE
   - CHASE: NavigationAgent3D.set_target_position()으로 추적
   - ATTACK: 사거리 내 진입 시 take_damage 호출
   - DEAD: 처리 후 queue_free()
4. EnemySpawner: 레벨 내 여러 위치에 적 인스턴스화

완료 기준: 적이 플레이어를 감지하고 추적 후 공격

---

#### Phase 4: 체력 시스템 및 GameManager

목표: 플레이어/적 체력, 사망, 게임 상태 관리

작업:
1. HealthComponent.gd (컴포넌트 분리):
   - max_health, current_health
   - take_damage(amount: float), heal(amount: float)
   - signal health_changed(new_val), signal died
2. Player에 HealthComponent 추가 (died 시그널 → GameManager.game_over())
3. GameManager (Autoload): game_over(), restart(), score 관리
4. HUD: 체력 표시 (ProgressBar), 탄약 표시, 크로스헤어

완료 기준: 플레이어 사망 시 Game Over 화면, R키로 재시작

---

#### Phase 5: 레벨 디자인 및 통합

목표: 플레이어블 레벨 1개 제작 + 전체 통합

작업:
1. 간단한 레벨 제작:
   - StaticBody3D + MeshInstance3D 조합
   - 복도/방 구조 (최소 3개 구역)
   - NavigationRegion3D NavMesh 베이크
   - 적 스폰 포인트 배치, 조명 (DirectionalLight3D + OmniLight3D)
2. 씬 전환 시스템 (메인메뉴 → 게임 씬)
3. 사운드: AudioStreamPlayer3D, CC0 라이선스 에셋 사용
4. 최종 통합 테스트

완료 기준: 처음부터 끝까지 플레이 가능한 데모 실행 가능

---

#### Phase 6: 빌드 및 검증

목표: 실행 가능한 빌드 생성 및 버그 수정

작업:
1. Godot Export 프리셋 설정 (Windows)
2. 핵심 버그 픽스: 적 NavMesh 이탈, 총기 쿨다운, 마우스 감도 연동
3. 성능 확인: 60FPS 기준 프레임 드랍 없을 것

완료 기준: 외부 배포 가능한 빌드 생성

---

## 결론

### epsilon에게 전달할 핵심 지시사항 요약

1. **엔진**: Godot 4.x, GDScript 사용. Unity/Python 사용 금지.
2. **시작점**: Phase 0부터 순서대로 실행. 각 Phase 완료 기준 충족 후 다음 단계 진입.
3. **참조 코드 사용 시**: 반드시 파일 상단에 `# [참조] {레포명} (MIT)` 형식의 주석 기재.
4. **하드코딩 금지**: 이동속도, FOV, 중력 등 모든 수치는 `GameSettings` Resource에서 로드.
5. **delta 타임 필수 적용**: 모든 프레임 의존 이동/물리 계산에 delta 곱셈 적용.
6. **GPL 코드 사용 절대 금지**: unfa/liblast 코드 직접 복사 금지. 아키텍처 개념만 참조.
7. **모듈화 원칙**: 이동/카메라/무기/체력을 분리된 스크립트로 관리. God Script 안티패턴 금지.
8. **산출물**: WS/member-epsilon/dev-log.md에 각 Phase 완료 기록 포함.

### 라이선스 준수 체크리스트

- [ ] 참조한 모든 MIT 코드에 출처 주석 기재 완료
- [ ] unfa/liblast (GPL v3) 코드 직접 복사 여부 확인 — 없어야 함
- [ ] Unity-Technologies/FPSSample 코드 직접 복사 여부 확인 — 없어야 함
- [ ] InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source- 미사용 확인 (라이선스 미확인)
- [ ] 사운드/텍스처 에셋 라이선스 확인 완료 (CC0 또는 CC-BY 이상 사용)
- [ ] 최종 빌드에 사용된 오픈소스 목록 (THIRD_PARTY.md 또는 게임 내 크레딧) 작성
- [ ] Godot 엔진 자체 MIT 라이선스 고지 포함 (빌드 시 Godot 자동 처리)

---

*본 보고서는 member-eta의 GitHub 리서치 결과(2026-05-30)를 기반으로 작성되었습니다.*
*참조 레포 목록 및 라이선스 정보 출처: WS/member-eta/github-research-report.md*
