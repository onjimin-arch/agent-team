# GitHub Research Report
생성자: member-eta (GitHub Researcher) | 생성시각: 2026-05-30T00:00:00+09:00 | 버전: v1

---

## 에스컬레이션 공지

> **[ESCALATION] gh CLI 미인증 상태**
>
> `gh auth status` 실행 결과: "You are not logged into any GitHub hosts."
>
> - `gh search repos` 및 `git clone --depth=1` 명령 실행 불가
> - 대안 조치: WebSearch 도구를 통해 GitHub 웹 인덱스 기반으로 레포 정보를 수집하였으며,
>   shallow clone 없이 웹 탐색 결과 및 훈련 데이터(지식 기준일: 2025년 8월)를 조합하여 보고서 작성
> - 권고: `gh auth login` 실행 후 재탐색 시 더 정확한 star 수 및 최신 커밋 날짜 확인 가능
> - 클론 기반 구조 분석은 수행되지 않음 (조건부 섹션에 명시)

---

## 탐색 조건

| 항목 | 값 |
|------|-----|
| 검색 키워드 | "3d fps game", "first person shooter", "fps game engine", "godot fps", "unity fps tutorial", "python fps game" |
| 언어 필터 | Python, C#, GDScript, C++, C |
| 품질 기준 | Stars 100+, 최근 18개월 이내 커밋 |
| 라이선스 우선순위 | MIT / Apache 2.0 우선, GPL은 참조 전용(플래그 표시) |
| 탐색 목표 | 5개 이상 레포 선정 |
| 탐색 방법 | WebSearch + 훈련 데이터 기반 (gh 미인증으로 인한 대안) |

---

## 탐색 결과 요약

총 **6개** 레포 최종 선정 (Stars 100+ 조건 충족 확인 또는 강하게 추정)

| # | 레포 | 언어 | Stars (추정) | 라이선스 | 선정 이유 |
|---|------|------|-------------|----------|-----------|
| 1 | `Whimfoome/godot-FirstPersonStarter` | GDScript | ~909 | MIT | Godot 4 FPS 컨트롤러 템플릿, 모듈화 구조, 활발한 유지보수 |
| 2 | `StanislavPetrovV/DOOM-style-Game` | Python | ~272 | MIT | Python Pygame 레이캐스팅 FPS 완성 예제, 교육용 최적 |
| 3 | `Unity-Technologies/FPSSample` | C# | ~5,100 | Unity Companion License | Unity 공식 멀티플레이어 FPS 예제, ECS + HDRP 아키텍처 참조 |
| 4 | `expressobits/character-controller` | GDScript | ~300 (추정) | MIT | Godot 4 모듈형 캐릭터 컨트롤러, FPS 포함 다중 이동 모드 |
| 5 | `unfa/liblast` | GDScript | ~121 | GPL v3 ⚠️ | Godot 4 기반 멀티플레이어 FPS 완성 게임, 아키텍처 참조용 |
| 6 | `InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source-` | C# | ~100+ | MIT (추정) | Unity 2023 하이퍼-무브먼트 FPS 프레임워크 (대시/슬라이드/월런) |

> ⚠️ GPL 레포 주의: `unfa/liblast`는 GPL v3 라이선스로, 코드 직접 사용 시 파생 저작물도 GPL 공개 의무 발생. 아키텍처 참조 전용으로만 활용 권장.

---

## 레포별 상세 분석

### 1. `Whimfoome/godot-FirstPersonStarter`
- **URL**: https://github.com/Whimfoome/godot-FirstPersonStarter
- **언어**: GDScript (Godot 4)
- **라이선스**: MIT
- **최신 릴리즈**: v1.3 (2026년 4월 확인)
- **Godot Asset Library 등록**: 있음 (asset #424)

**아키텍처 패턴**
- Player 노드를 3개의 분리된 파일로 모듈화: `MovementController`, `Head`, `Sprint`
- CharacterBody3D 기반 물리 처리
- 마우스 캡처 및 카메라 피치/요 분리 처리

**핵심 코드 위치 (웹 탐색 기반)**
- `Player/` — 플레이어 컨트롤러 루트
- `Levels/Main/` — 데모 레벨
- `Player/MovementController.gd` — 이동 로직
- `Player/Head.gd` — 카메라 회전 로직

**주요 인사이트**
- Godot 4의 `CharacterBody3D` + `move_and_slide()` 패턴 표준 구현
- 헤드밥(headbob) 없이 최소한의 의존성으로 구성 → 초보자 온보딩 최적
- Asset Library 등록으로 직접 Godot 에디터에서 임포트 가능

---

### 2. `StanislavPetrovV/DOOM-style-Game`
- **URL**: https://github.com/StanislavPetrovV/DOOM-style-Game
- **언어**: Python (Pygame)
- **라이선스**: MIT (확인됨)
- **Stars**: ~272 / Forks: ~110

**아키텍처 패턴**
- 클래식 레이캐스팅(Raycasting) 알고리즘으로 의사(pseudo) 3D 렌더링
- 파일 단위 역할 분리: `main.py`, `player.py`, `npc.py`, `map.py`, `raycasting.py`, `object_renderer.py`, `sound.py`, `settings.py`

**핵심 코드 위치**
- `raycasting.py` — 레이캐스팅 렌더링 엔진 핵심
- `player.py` — 1인칭 이동, 마우스 시야각 처리
- `npc.py` — 적 AI 경로탐색 로직
- `map.py` — 타일 기반 레벨 데이터
- `settings.py` — 해상도, FOV, 게임 파라미터 중앙화

**주요 인사이트**
- 순수 Python으로 구현된 레이캐스팅 FPS의 교과서적 예제
- A* 또는 BFS 기반 경로탐색 AI 포함 (npc.py)
- 240×160 저해상도 타일 렌더링 → 성능 병목 없이 학습 가능
- `settings.py` 단일 설정 파일 패턴: FOV, MAP_SIZE, FPS 등 중앙 관리

---

### 3. `Unity-Technologies/FPSSample`
- **URL**: https://github.com/Unity-Technologies/FPSSample
- **언어**: C# (Unity)
- **라이선스**: Unity Companion License (⚠️ 상업 프로젝트에 Unity 필요, 비-Unity 엔진 사용 불가)
- **Stars**: ~5,100
- **상태**: 아카이브됨 (Unity 2018.3 기반, 적극 유지보수 없음)

**아키텍처 패턴**
- DOTS (Data-Oriented Technology Stack) + ECS (Entity Component System) 조기 적용 사례
- HDRP (High Definition Render Pipeline) 기반 그래픽스
- 신규 네트워크 Transport Layer 적용 (당시 실험적 기능)
- 멀티플레이어 권한(authority) 분리: 서버 로직 / 클라이언트 예측

**핵심 코드 위치**
- `Assets/Scripts/` — 게임플레이 C# 스크립트 전체
- `Assets/` — 모델, 텍스처, 애니메이션 에셋 포함
- 무기 시스템: 데이터 기반(scriptable objects) 무기 설계

**주요 인사이트**
- Unity 공식 팀 작성 → 코드 품질 높음, 구조 참조에 적합
- ECS 기반 성능 최적화 패턴 학습 가능 (특히 다수 개체 동시 처리)
- 아카이브 상태이므로 직접 실행보다는 코드 구조 참조 목적으로 활용
- 라이선스가 Unity Companion License: 다른 엔진으로 이식 시 법적 제약 있음

---

### 4. `expressobits/character-controller`
- **URL**: https://github.com/expressobits/character-controller
- **언어**: GDScript (Godot 4)
- **라이선스**: MIT
- **Godot Asset Library**: asset #1567

**아키텍처 패턴**
- **모듈형(Modular)** 설계: 이동 모드별 독립 컴포넌트 (Walk, Crouch, Sprint, Swim, Fly)
- FPS 헤드밥 + 카메라 기울기 지원
- 각 이동 상태를 독립 노드로 attach/detach 가능한 플러그인 방식

**핵심 코드 위치**
- `addons/character_controller/` — Godot 애드온 구조
- FPS 모드: `FPSCharacter` 씬 또는 관련 GDScript 파일

**주요 인사이트**
- 단순 템플릿이 아닌 Godot Asset Library 정식 등록 애드온
- 수영/비행 모드 포함 → 다양한 게임 장르로 확장 가능
- MIT 라이선스로 상업적 활용 완전 자유

---

### 5. `unfa/liblast` ⚠️ GPL v3 참조 전용
- **URL**: https://github.com/unfa/liblast
- **언어**: GDScript (Godot 4)
- **라이선스**: GPL v3 (파생 저작물 공개 의무)
- **Stars**: ~121
- **현황**: GitHub는 레거시 아카이브, 현재 개발은 Codeberg로 이전 (https://codeberg.org/Liblast/liblast-framework)

**아키텍처 패턴**
- 100% 오픈소스 툴체인 (에셋 포함 소스 공개)
- Godot 4 멀티플레이어 네트워크 아키텍처
- 게임 에셋(사운드, 3D 모델 소스 파일)까지 오픈소스

**주요 인사이트**
- 완전한 멀티플레이어 FPS 아키텍처 참조에 적합
- GPL이므로 코드를 직접 복사 사용하면 파생 저작물도 GPL 공개 의무 발생
- 아키텍처 패턴과 Godot 멀티플레이어 구조 학습 목적으로만 참조 권장

---

### 6. `InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source-`
- **URL**: https://github.com/InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source-
- **언어**: C# (Unity 2023)
- **라이선스**: MIT (추정, 확인 권장)
- **Stars**: 100+ (추정)

**아키텍처 패턴**
- 하이퍼-무브먼트 FPS: 대시(Dash), 슬라이드(Slide), 월런(Wall-Run) 통합
- Unity 2023 기반 최신 스택

**핵심 코드 위치**
- 이동 시스템: 상태머신 기반 하이퍼 무브먼트 컨트롤러
- 무기 시스템: 프레임워크 형태로 제공

**주요 인사이트**
- 현대적 FPS의 운동감(movement feel) 구현 참조에 적합
- Titanfall/Apex Legends 스타일의 고기동성 FPS 개발 시 참고

---

## 크로스 레포 공통 패턴

### 1. 플레이어 컨트롤러 분리
모든 프로젝트가 플레이어 이동 로직을 카메라/시야 로직에서 분리:
- Godot: `CharacterBody3D`(이동) + `Camera3D`(시야)가 별도 노드
- Unity: `CharacterController` + `MouseLook` 분리
- Python: `player.py`가 이동과 시야각 모두 담당하나 설정은 `settings.py` 분리

### 2. 설정 중앙화
- `settings.py` (Python), `ScriptableObject` (Unity), `autoload Singleton` (Godot) 패턴으로 게임 파라미터를 한 곳에서 관리

### 3. 레이캐스팅 기반 히트 감지
- 2D 레이캐스팅 렌더링(Python)과 3D 레이캐스트 충돌 감지(Godot/Unity)는 개념적으로 연결됨
- 총기 발사: 물리 기반 Rigidbody 발사체보다 즉시 레이캐스트 히트 처리가 지배적

### 4. 모듈형 무기 시스템
- 데이터 기반(ScriptableObject/Resource) 무기 정의가 공통 패턴
- 무기 교체: 인벤토리 + 현재 활성 무기 참조 패턴

### 5. 상태 머신(State Machine) 플레이어 로직
- 달리기/걷기/웅크리기/공중 상태를 FSM으로 관리하는 패턴이 Godot, Unity 모두에서 등장

---

## 안티패턴 (품질 신호 기반)

| 안티패턴 | 설명 | 신호 |
|---------|------|------|
| **God Script** | 플레이어 이동, 무기, 카메라, 체력을 단일 스크립트에 몰아넣기 | 파일 수가 3개 이하인 소형 레포에서 발견 |
| **하드코딩 수치** | FOV, 이동 속도, 중력값이 코드 내 리터럴로 산재 | settings 파일/ScriptableObject 없는 레포 |
| **비활성 레포 복사** | Stars가 높지만 마지막 커밋이 3년 전인 레포 참조 | FPSSample이 대표 사례 (아카이브됨) |
| **GPL 코드 무단 활용** | GPL 코드를 MIT 프로젝트에 복사 시 라이선스 오염 | liblast, ET:Legacy 등 |
| **델타 타임 미적용** | `dt` 없이 프레임레이트 의존 이동 처리 | 저품질 교육용 레포에서 자주 발견 |
| **단일 씬/레벨** | 레벨 로딩 시스템 없이 단일 씬에 모든 것 배치 | 프로토타입 수준 레포의 공통 문제 |

---

## Planner를 위한 권고 스택·접근법

### 권고 스택

#### 옵션 A: Godot 4 (추천)
```
엔진:       Godot 4.x (GDScript 또는 C#)
참조 레포:  Whimfoome/godot-FirstPersonStarter (컨트롤러)
            expressobits/character-controller (모듈화 패턴)
            unfa/liblast (멀티플레이어 아키텍처 참조, GPL 주의)
라이선스:   MIT 컴포넌트만 사용
장점:       무료/오픈소스 엔진, 경량, GDScript 빠른 프로토타이핑
단점:       C++/Unity 생태계 대비 에셋 풀 제한적
```

#### 옵션 B: Unity 2023
```
엔진:       Unity 2023 LTS (C#)
참조 레포:  InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source- (무브먼트)
            Unity-Technologies/FPSSample (아키텍처 참조, 아카이브)
라이선스:   Unity Personal/Pro 라이선스 필요
장점:       에셋 스토어, 대형 커뮤니티, 취업 시장 친화적
단점:       엔진 자체가 소스비공개, 수익화 시 요금 발생
```

#### 옵션 C: Python (교육/프로토타입 전용)
```
엔진:       Python + Pygame
참조 레포:  StanislavPetrovV/DOOM-style-Game
라이선스:   MIT
장점:       진입장벽 최저, 알고리즘 학습 최적
단점:       성능 한계로 진짜 3D FPS 불가 (의사 3D만 가능)
```

### 개발 접근법 권고

1. **프로토타이핑 단계**: Python/Pygame으로 레이캐스팅 개념 학습 → 이후 Godot/Unity 전환
2. **단일 플레이어 FPS**: Godot 4 + `Whimfoome/godot-FirstPersonStarter` 기반으로 시작
3. **멀티플레이어 FPS**: Godot 4 + `unfa/liblast` 아키텍처 참조 (코드 직접 사용 금지, GPL)
4. **상업 프로젝트**: Unity 2023 + `InboraStudio/Unity-Hyper-FPS-FrameWork` (MIT 라이선스 확인 후)
5. **무기 시스템**: 데이터 기반(ScriptableObject/Resource) 패턴 도입 — 하드코딩 안티패턴 회피
6. **네트워킹**: Godot의 내장 MultiplayerAPI 또는 Unity Netcode for GameObjects 활용

---

## 출처 목록

| # | 레포명 | Stars | 라이선스 | URL |
|---|--------|-------|----------|-----|
| 1 | Whimfoome/godot-FirstPersonStarter | ~909 | MIT | https://github.com/Whimfoome/godot-FirstPersonStarter |
| 2 | StanislavPetrovV/DOOM-style-Game | ~272 | MIT | https://github.com/StanislavPetrovV/DOOM-style-Game |
| 3 | Unity-Technologies/FPSSample | ~5,100 | Unity Companion | https://github.com/Unity-Technologies/FPSSample |
| 4 | expressobits/character-controller | ~300 | MIT | https://github.com/expressobits/character-controller |
| 5 | unfa/liblast | ~121 | GPL v3 ⚠️ | https://github.com/unfa/liblast |
| 6 | InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source- | 100+ | MIT (요확인) | https://github.com/InboraStudio/Unity-Hyper-FPS-FrameWork-Open-Source- |

### 추가 참조 레포 (Stars 미확인 또는 100 미만)

| 레포명 | 언어 | URL | 비고 |
|--------|------|-----|------|
| dragon1freak/fps-template | GDScript | https://github.com/dragon1freak/fps-template | Godot 4 상태머신 FPS 템플릿 |
| peppermintCybe/FPS-engine-raylib | C | https://github.com/peppermintCybe/FPS-engine-raylib | raylib 기반 C언어 FPS |
| miarolfe/MiniFPS | C++ | https://github.com/miarolfe/MiniFPS | C++11 + SDL2 레트로 FPS |
| AxelReviron/Godot-FPS-Template | GDScript | https://github.com/AxelReviron/Godot-FPS-Template | Godot 4.4 상태기반 플레이어 + 모듈 무기 |
| FinFetChannel/RayCastingPythonMaze | Python | https://github.com/FinFetChannel/RayCastingPythonMaze | Python 레이캐스팅 미로 |

---

## 탐색 제약 사항 및 신뢰도 노트

- **gh CLI 미인증**: shallow clone 수행 불가, 파일 구조 직접 분석 미수행
- **Stars 수치**: WebSearch 결과 및 훈련 데이터 기반 추정값 (2026-05-30 기준 실제값과 다를 수 있음)
- **라이선스**: 일부 레포(#6)는 직접 LICENSE 파일 확인 필요
- **커밋 신선도**: 최근 18개월 커밋 여부는 직접 `git log` 확인 미수행 (Whimfoome/godot-FirstPersonStarter는 2026년 4월 릴리즈 확인으로 신선도 충족)
- **재탐색 권고**: `gh auth login` 완료 후 `gh search repos "fps game" --language GDScript --sort=stars --limit=20` 등으로 정밀 탐색 권장
