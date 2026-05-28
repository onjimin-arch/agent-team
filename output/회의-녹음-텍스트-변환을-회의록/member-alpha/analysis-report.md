---
Creator: member-alpha
Created: 2026-05-27
Version: 1.0
---

# 회의록 앱 구현 방향 분석 보고서

## 개요

회의 녹음 및 텍스트 변환을 통한 회의록 자동 작성 앱 개발을 위한 구현 방향을 분석한다.
본 보고서는 기술 스택, 아키텍처, 모듈별 스펙을 정의하여 member-epsilon의 코드 구현 기반이 된다.

### 핵심 기능 요구사항
1. **오디오 입력**: 브라우저 마이크 녹음 또는 오디오 파일 업로드 (mp3, wav, m4a, ogg)
2. **STT 변환**: OpenAI Whisper(로컬 또는 API)를 통한 한국어 음성-텍스트 변환
3. **회의록 생성**: Claude API를 통해 전사 텍스트 → 요약, 결정사항, 액션아이템 추출
4. **결과 표시 및 다운로드**: 웹 UI에서 결과 확인, Markdown 파일 다운로드

---

## 분석 결과

### 1. 기술 스택 선정

| 레이어 | 선택 기술 | 근거 |
|--------|-----------|------|
| 백엔드 | Python 3.11 + FastAPI | 비동기 처리, 파일 업로드 지원, 경량 |
| 프론트엔드 | HTML/CSS/Vanilla JS | 의존성 최소화, 브라우저 MediaRecorder API 사용 |
| STT | openai-whisper (로컬 base 모델) | 오프라인 동작 가능, 한국어 지원, 비용 없음 |
| LLM | Claude claude-sonnet-4-6 (Anthropic SDK) | 한국어 요약 품질 우수, 최신 모델 |
| 파일 처리 | python-multipart, pydub | 오디오 변환 및 파일 스트리밍 |
| 패키지 관리 | uv (또는 pip) | 빠른 의존성 설치 |

**대안 고려 후 제외**:
- Whisper API (유료, 네트워크 필요) → 로컬 Whisper 선택
- Gradio/Streamlit (무거운 프레임워크) → FastAPI + 순수 HTML 선택
- React (빌드 도구 필요) → Vanilla JS 선택 (단순성 우선)

### 2. 프로젝트 디렉터리 구조

```
output/회의-녹음-텍스트-변환을-회의록/app/
├── main.py                  # FastAPI 앱 진입점
├── requirements.txt         # 의존성 목록
├── .env.example             # 환경변수 템플릿
├── routers/
│   ├── __init__.py
│   ├── transcribe.py        # /api/transcribe 엔드포인트
│   └── minutes.py           # /api/minutes 엔드포인트
├── services/
│   ├── __init__.py
│   ├── whisper_service.py   # STT 변환 로직
│   └── claude_service.py    # Claude API 회의록 생성 로직
├── static/
│   ├── index.html           # 메인 UI
│   ├── style.css            # 스타일
│   └── app.js               # 프론트엔드 로직
└── uploads/                 # 임시 오디오 파일 저장 (gitignore)
```

### 3. API 엔드포인트 스펙

#### POST `/api/transcribe`
- Input: `multipart/form-data` — `file: UploadFile` (오디오 파일)
- 처리: pydub으로 wav 변환 → whisper.transcribe()
- Output: `{"transcript": "...", "language": "ko", "duration_sec": 120}`

#### POST `/api/minutes`
- Input: `{"transcript": "전사 텍스트 전문"}`
- 처리: Claude API 호출 (프롬프트: 회의록 구조화 지시)
- Output: `{"minutes": "## 회의 요약\n...\n## 결정사항\n...\n## 액션아이템\n..."}`

#### GET `/` 
- 정적 HTML UI 서빙

### 4. Claude 프롬프트 스펙

```
system: 당신은 전문 회의록 작성 도우미입니다. 회의 전사 텍스트를 분석하여 구조화된 회의록을 작성합니다.

user: 다음 회의 전사 텍스트를 분석하여 아래 형식의 회의록을 작성해주세요:

## 회의 요약
(2-3문장으로 핵심 내용 요약)

## 참석자
(언급된 이름이나 역할 목록)

## 주요 논의사항
(항목별 정리)

## 결정사항
(확정된 사항 목록)

## 액션아이템
| 담당자 | 내용 | 기한 |
|-------|------|------|
...

전사 텍스트:
{transcript}
```

### 5. 프론트엔드 기능 스펙

**녹음 기능 (MediaRecorder API)**:
- 시작/정지 버튼 토글
- 녹음 시간 실시간 표시
- 녹음 완료 시 Blob → FormData로 서버 전송

**파일 업로드**:
- drag-and-drop 또는 파일 선택 (accept: audio/*)
- 파일명, 크기 표시

**처리 흐름 표시**:
- 단계별 로딩 스피너: 업로드 → STT 변환 중 → 회의록 생성 중 → 완료
- 에러 발생 시 메시지 표시

**결과 화면**:
- 전사 텍스트 섹션 (펼치기/접기)
- 회의록 Markdown 렌더링
- "Markdown 다운로드" 버튼

### 6. 환경변수

```env
ANTHROPIC_API_KEY=your_api_key_here
WHISPER_MODEL=base          # tiny / base / small / medium
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=uploads
```

### 7. requirements.txt 구성

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.18
anthropic>=0.40.0
openai-whisper>=20240930
pydub>=0.25.1
python-dotenv>=1.0.0
```

---

## 결론

**구현 우선순위**:
1. FastAPI 기본 구조 + 정적 파일 서빙 설정
2. Whisper STT 서비스 (`whisper_service.py`)
3. Claude 회의록 생성 서비스 (`claude_service.py`)
4. API 라우터 연결
5. 프론트엔드 UI (녹음 + 파일 업로드 + 결과 표시)

**주의사항**:
- Whisper `base` 모델은 첫 실행 시 약 145MB 다운로드 필요 → `README.md`에 명시
- ANTHROPIC_API_KEY 필수 → `.env.example` 파일로 안내
- 업로드 파일은 처리 후 자동 삭제하여 디스크 낭비 방지
- 오디오 파일 50MB 제한 (Whisper 처리 시간 고려)

**예상 실행 방법**:
```bash
cd output/회의-녹음-텍스트-변환을-회의록/app
pip install -r requirements.txt
cp .env.example .env  # ANTHROPIC_API_KEY 설정
uvicorn main:app --reload --port 8000
# http://localhost:8000 접속
```
