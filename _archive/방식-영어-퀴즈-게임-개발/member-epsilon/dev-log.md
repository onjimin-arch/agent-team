# Dev Log
Creator: member-epsilon | Created: 2026-05-29 11:30

## 변경 파일 목록

| 파일 경로 | 상태 | 라인 수 | 역할 |
|----------|------|--------|------|
| `game/data/categories.js` | 수정 | 86 | QUESTION_TYPES, GAME_MODES, WILDCARD_SETTINGS, SM-2 상수 추가 |
| `game/data/questions.js` | 확장 | 1486 | 기존 60제 + 신규 60제 (fill_blank 17 + matching 16 + sentence_complete 17 + multiple 10) |
| `game/sm2-algorithm.js` | 신규 생성 | 87 | SuperMemo-2 알고리즘 독자 구현 (sm2CreateItem, sm2Update, sm2LoadItems, sm2SaveItems 등) |
| `game/audio.js` | 신규 생성 | 38 | Web Speech API TTS 헬퍼 (speakWord, stopSpeaking) |
| `game/game.js` | 대폭 리팩토링 | 970 | 5가지 문제 유형, 3가지 게임 모드, 타이머, 와일드카드, 생명 시스템, SM-2, 키보드 단축키 |
| `game/index.html` | 중간 변경 | 177 | 게임 모드 선택, 타이머 HUD, 와일드카드 바, 빈칸/매칭/문장완성 UI, 생명 표시, 음성 버튼 추가 |
| `game/style.css` | 중간 변경 | 637 | 신규 스타일 210줄 추가 (타이머, 와일드카드, fill-blank, matching, sentence-complete, pulse 애니메이션) |
| `src/` (모든 파일) | 신규 생성 | — | 프로젝트 사본 `output/방식-영어-퀴즈-게임-개발/src/` 하위에 배포 |

**총 파일 수:** 8개 | **총 라인 수:** 약 3,548줄

## 자체 검증 결과

| 검증 항목 | 결과 | 비고 |
|---------|------|------|
| 총 120문제 데이터셋 | PASS | 120개 id 확인 (vocab 24, gram 24, prep 24, phrv 24, idio 24) |
| 5가지 문제 유형 | PASS | multiple:60, truefalse:10, fill_blank:17, matching:16, sentence_complete:17 |
| 카테고리별 균등 분포 | PASS | 각 24문제 |
| 3가지 게임 모드 | PASS | Classic(10문제, 무제한), Timed(10문제, 180초), Speed(15문제, 12초/문제) |
| 와일드카드 3종 | PASS | 50:50(오답 제거), +Time(15초 추가), Shield(스트릭 보호) — 각 1회 기본 지급, 5연속 정답 시 +1 |
| SM-2 복습 스케줄링 | PASS | sm2CreateItem, sm2Update, sm2IsDue, sm2GetDueItems 등 8개 함수 구현 |
| 생명 시스템 | PASS | 5개 → 오답 시 -1, 0되면 게임오버, Shield 사용 시 보존 |
| 오답 재출제 | PASS | wrongQueue (max 2회 반복) |
| 타이머 로직 | PASS | Timed(전체 180초), Speed(12초/문제), 10초 미만 pulse 애니메이션 |
| 키보드 단축키 | PASS | 1-4/A-D=선택, H=힌트, W=와일드카드, Space/Enter=다음 |
| Web Speech API TTS | PASS | speakWord(), 브라우저 미지원 시 silent fallback |
| localStorage 영속성 | PASS | SM-2 ("englishQuizSM2Items"), 점수 ("englishQuizHighScores") |
| 스크립트 로드 순서 | PASS | categories.js → questions.js → sm2-algorithm.js → audio.js → game.js |
| 외부 의존성 없음 | PASS | CDN/API 참조 0건 |
| 반응형 디자인 | PASS | mobile-first, 400px/480px/600px/768px 브레이크포인트 |
| file:// 로컬 실행 | PASS | index.html 직접 열기로 실행 가능 |
| fill_blank 정답 판정 | PASS | acceptable_answers 배열 대소문자 무시 비교 |
| matching 정답 판정 | PASS | 전체 쌍 select 비교, all-or-nothing |
| sentence_complete 정답 판정 | PASS | blanks별 select 비교, all-or-nothing |
| 피드백 및 설명 표시 | PASS | 정답/오답 시 explanation + feedback area 표시 |

**전체 검증 결과: PASS (19/19)**

## 배포 결과

- **로컬 실행:** `game/index.html` 또는 `src/index.html` 을 브라우저에서 직접 열어 실행 가능 (file:// 프로토콜)
- **작업 디렉터리:** `output/방식-영어-퀴즈-게임-개발/game/` (원본) 및 `output/방식-영어-퀴즈-게임-개발/src/` (배포본)
- **인터넷 연결 불필요:** 외부 리소스 참조 없음 (완전 오프라인)
- **GitHub Pages:** `/game` 또는 `/src` 폴더를 Pages source로 지정 시 바로 배포 가능