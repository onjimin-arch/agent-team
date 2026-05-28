---
Creator: member-epsilon
Created: 2026-05-27
Version: 1.0
---

# Dev Log: 회의록 자동 작성 앱

## 변경 파일 목록

| 파일 경로 | 유형 | 설명 |
|----------|------|------|
| `app/main.py` | 신규 | FastAPI 앱 진입점, 라우터 등록, 정적 파일 서빙 |
| `app/requirements.txt` | 신규 | Python 의존성 목록 |
| `app/.env.example` | 신규 | 환경변수 템플릿 |
| `app/routers/__init__.py` | 신규 | 라우터 패키지 초기화 |
| `app/routers/transcribe.py` | 신규 | POST /api/transcribe 엔드포인트 |
| `app/routers/minutes.py` | 신규 | POST /api/minutes 엔드포인트 |
| `app/services/__init__.py` | 신규 | 서비스 패키지 초기화 |
| `app/services/whisper_service.py` | 신규 | Whisper STT 변환 로직 (싱글턴 모델 로딩) |
| `app/services/claude_service.py` | 신규 | Claude claude-sonnet-4-6 회의록 생성 로직 |
| `app/static/index.html` | 신규 | 메인 UI (탭, 녹음, 업로드, 결과 표시) |
| `app/static/style.css` | 신규 | 반응형 스타일시트 (CSS custom properties 활용) |
| `app/static/app.js` | 신규 | 프론트엔드 로직 (MediaRecorder, fetch, 마크다운 렌더) |

총 12개 파일 신규 생성.

---

## 자체 검증 결과

### 코드 구조 검증
- [x] FastAPI 라우터가 `main.py`에 올바르게 등록됨
- [x] `services/` 모듈이 `routers/`에서 정상 import됨
- [x] `UploadFile` 처리 후 임시 파일 `finally` 블록에서 반드시 삭제
- [x] `ANTHROPIC_API_KEY` 미설정 시 `ValueError` 명확히 raise
- [x] 파일 크기 제한(MAX_FILE_SIZE_MB)이 업로드 라우터에 적용됨
- [x] 허용 확장자 목록(`ALLOWED_EXTENSIONS`) 검증 로직 존재

### API 설계 검증
- [x] `POST /api/transcribe`: multipart/form-data, `file` 필드
- [x] `POST /api/minutes`: JSON body, `{"transcript": "..."}`
- [x] 오류 응답: FastAPI `HTTPException` + 상태 코드 400/413/500

### 프론트엔드 검증
- [x] 탭 전환(녹음/업로드) 시 제출 버튼 활성화 로직 분기
- [x] `MediaRecorder.stop()` 이벤트 완료 후 Blob 생성 (비동기 처리 올바름)
- [x] 드래그앤드롭 이벤트 `preventDefault()` 적용됨
- [x] 다운로드: `Blob URL` → `<a download>` 패턴 (메모리 누수 방지 `revokeObjectURL`)
- [x] 3단계 프로그레스 UI 상태 전환 (active → done)

### 보안 검토
- [x] 파일 확장자 허용 목록 검증 (확장자 우회 불가)
- [x] 파일 크기 상한 적용
- [x] 업로드 파일 처리 후 즉시 삭제
- [x] API 키 환경변수 분리 (`.env.example` 제공, `.env` 미포함)

### 알려진 제약사항
- Whisper `base` 모델 첫 실행 시 ~145MB 모델 파일 다운로드 필요
- `pydub`은 `ffmpeg` 바이너리 의존 → 시스템에 `ffmpeg` 설치 필요
- 동시 요청 처리 시 Whisper 싱글턴 모델 공유 (멀티 스레드 안전성 미검증)
- 프로덕션 배포 시 `uvicorn --workers N` 대신 gunicorn+uvicorn worker 권장

---

## 배포 결과

- 서비스 타입: FastAPI (Python)
- PROD_PORT: 8000
- 배포 방식: 로컬 실행 (`uvicorn main:app --reload`)
- 배포 자동화: 미실행 (human_approval 대기 중)
- 배포 commit hash: N/A (신규 프로젝트, 별도 repo 아님)

**실행 명령**:
```bash
cd output/회의-녹음-텍스트-변환을-회의록/app
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY 직접 입력
uvicorn main:app --reload --port 8000
```
