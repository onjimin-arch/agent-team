---
Creator: member-epsilon
Created: 2026-05-27
Version: 1.0
---

# 코드 변경 요약 (Diff Summary)

## 신규 프로젝트: 회의록 자동 작성 앱

기존 코드베이스 없음 → 전체 신규 구현. 총 12개 파일, 약 500줄.

---

## 백엔드 (`app/`)

### `main.py` (24줄)
- FastAPI 인스턴스 생성 및 라우터(`transcribe`, `minutes`) 등록
- `/static` 정적 파일 서빙 마운트
- `uploads/` 디렉터리 자동 생성
- `/` 루트 → `index.html` 반환

### `services/whisper_service.py` (26줄)
- 전역 싱글턴 `_model` 캐싱 (첫 요청 시 1회 로딩, 이후 재사용)
- `transcribe_audio(path)` → `{transcript, language, segments}` 반환
- `language="ko"` 고정으로 한국어 인식 정확도 향상

### `services/claude_service.py` (50줄)
- `anthropic.Anthropic` 싱글턴 클라이언트
- `claude-sonnet-4-6` 모델 사용
- 구조화 회의록 프롬프트: 요약/참석자/논의/결정/액션아이템 섹션 강제
- `max_tokens=4096` (긴 회의도 대응)

### `routers/transcribe.py` (44줄)
- `POST /api/transcribe`: UploadFile 수신 → 임시 저장 → Whisper 호출 → 삭제
- 파일 크기(50MB) 및 확장자 허용 목록 검증
- `uuid4` 기반 임시 파일명 (충돌 방지)

### `routers/minutes.py` (22줄)
- `POST /api/minutes`: JSON `transcript` → Claude 호출 → minutes 반환
- Pydantic `MinutesRequest` 모델로 입력 검증

---

## 프론트엔드 (`app/static/`)

### `index.html` (70줄)
- 탭(녹음/업로드), 프로그레스(3단계), 결과(전사+회의록) 섹션 구조
- CDN 의존성 없음 (완전 오프라인 UI 작동)

### `style.css` (200줄)
- CSS custom properties 기반 테마 시스템
- 3개 상태 `.step`: 기본/active(파란색)/done(초록색)
- 드래그앤드롭 `.drag-over` 시각 피드백
- `@keyframes blink`: 녹음 중 빨간 점 깜빡임

### `app.js` (190줄)
주요 흐름:
```
탭 선택 → (녹음 | 파일 선택)
       → submit 버튼 활성화
       → POST /api/transcribe
       → POST /api/minutes
       → 결과 렌더링 + 다운로드
```
핵심 함수:
- `startRecording()`: getUserMedia → MediaRecorder → Blob
- `setStep(id, state)`: 프로그레스 단계 UI 제어
- `renderMarkdown(md)`: 최소 마크다운 렌더러 (외부 라이브러리 불필요)
- `showResult()`: 전사 텍스트 + 회의록 HTML 렌더 + 다운로드 버튼 설정

---

## 아키텍처 요약

```
Browser
  ├─ 녹음: MediaRecorder API → Blob
  └─ 업로드: <input type=file> → File

     ↓ FormData POST

FastAPI (main.py)
  ├─ /api/transcribe
  │    └─ whisper_service → openai-whisper (로컬)
  └─ /api/minutes
       └─ claude_service → Anthropic SDK → Claude claude-sonnet-4-6
```
