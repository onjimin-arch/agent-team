# 회의 녹음 텍스트 변환을 통한 회의록 작성 앱 — 구현 완료 보고서

**작성일**: 2026-05-27  
**Task Type**: dev  
**활성 멤버**: member-alpha (분석), member-epsilon (구현)

---

## 1. 프로젝트 개요

회의 음성을 녹음하거나 오디오 파일을 업로드하면 **OpenAI Whisper**로 텍스트를 변환하고, **Claude claude-sonnet-4-6 API**를 통해 자동으로 구조화된 회의록(요약·결정사항·액션아이템)을 생성하는 웹 앱이다.

### 핵심 가치
- 로컬 Whisper 모델 사용 → **무제한 무료 STT**, 외부 API 불필요
- Claude AI 활용 → **고품질 한국어 회의록** 자동 생성
- 의존성 최소화 → CDN 없는 순수 HTML/CSS/JS 프론트엔드

---

## 2. 기술 스택

| 레이어 | 기술 | 버전 |
|--------|------|------|
| 백엔드 | Python + FastAPI | 3.11+ / 0.115+ |
| STT | openai-whisper (base 모델) | 20240930+ |
| LLM | Anthropic Claude claude-sonnet-4-6 | anthropic SDK 0.40+ |
| 프론트엔드 | HTML + CSS + Vanilla JS | — |
| 오디오 처리 | pydub | 0.25.1+ |
| 서버 | uvicorn | 0.32+ |

---

## 3. 프로젝트 구조

```
output/회의-녹음-텍스트-변환을-회의록/app/
├── main.py                  # FastAPI 앱 진입점
├── requirements.txt         # 의존성 목록
├── .env.example             # 환경변수 템플릿
├── routers/
│   ├── transcribe.py        # POST /api/transcribe
│   └── minutes.py           # POST /api/minutes
├── services/
│   ├── whisper_service.py   # Whisper STT (싱글턴 모델)
│   └── claude_service.py    # Claude 회의록 생성
├── static/
│   ├── index.html           # 메인 UI
│   ├── style.css            # 반응형 스타일
│   └── app.js               # 프론트엔드 로직
└── uploads/                 # 임시 파일 (자동 정리)
```

---

## 4. API 명세

### `POST /api/transcribe`
오디오 파일을 업로드받아 Whisper로 텍스트 변환

**Request**: `multipart/form-data`
```
file: <오디오 파일> (mp3, wav, m4a, ogg, flac, webm / 최대 50MB)
```

**Response**: `200 OK`
```json
{
  "transcript": "회의 전사 텍스트 전문...",
  "language": "ko",
  "segments": [
    {"start": 0.0, "end": 5.2, "text": "안녕하세요"},
    ...
  ]
}
```

### `POST /api/minutes`
전사 텍스트를 받아 Claude AI로 회의록 생성

**Request**: `application/json`
```json
{"transcript": "전사 텍스트 전문..."}
```

**Response**: `200 OK`
```json
{
  "minutes": "## 회의 요약\n...\n## 결정사항\n...\n## 액션아이템\n..."
}
```

---

## 5. 주요 구현 내용

### 5-1. Whisper STT (`services/whisper_service.py`)
```python
_model: whisper.Whisper | None = None

def _get_model():
    global _model
    if _model is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        _model = whisper.load_model(model_name)
    return _model

def transcribe_audio(audio_path):
    model = _get_model()
    result = model.transcribe(str(audio_path), language="ko", task="transcribe")
    return {"transcript": result["text"].strip(), ...}
```
- 싱글턴 패턴으로 모델을 1회만 로딩 → 응답 속도 향상
- `language="ko"` 고정으로 한국어 인식 정확도 최적화

### 5-2. Claude 회의록 생성 (`services/claude_service.py`)
```python
def generate_minutes(transcript: str) -> str:
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT_TEMPLATE.format(transcript=transcript)}],
    )
    return message.content[0].text
```
- **구조화 출력 프롬프트**: 요약 / 참석자 / 논의사항 / 결정사항 / 액션아이템 테이블 강제
- `max_tokens=4096`으로 긴 회의도 완전 처리

### 5-3. 파일 업로드 보안 (`routers/transcribe.py`)
```python
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 50)) * 1024 * 1024

# 처리 후 반드시 삭제
try:
    result = transcribe_audio(tmp_path)
finally:
    if tmp_path.exists():
        tmp_path.unlink()
```

### 5-4. 브라우저 녹음 (`static/app.js`)
```js
async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = () => {
    recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
    stream.getTracks().forEach(t => t.stop());
    updateSubmitState();
  };
  mediaRecorder.start();
}
```
- `MediaRecorder API` 활용으로 별도 녹음 라이브러리 불필요

---

## 6. 앱 실행 방법

### 사전 요구사항
- Python 3.11+
- `ffmpeg` (pydub 오디오 처리 의존)
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg
  # macOS
  brew install ffmpeg
  # Windows: https://ffmpeg.org/download.html
  ```
- Anthropic API 키

### 실행 순서
```bash
# 1. 앱 디렉터리 이동
cd "output/회의-녹음-텍스트-변환을-회의록/app"

# 2. 의존성 설치 (첫 실행 시 약 145MB Whisper 모델 다운로드 포함)
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에서 ANTHROPIC_API_KEY 값 입력

# 4. 서버 실행
uvicorn main:app --reload --port 8000

# 5. 브라우저에서 접속
# http://localhost:8000
```

---

## 7. 사용 흐름

```
사용자
  ├─ [탭 1] 🎙 녹음하기
  │    └─ "녹음 시작" 클릭 → 마이크 권한 허용 → 녹음 → "녹음 중지"
  │
  └─ [탭 2] 📁 파일 업로드
       └─ 오디오 파일 드래그앤드롭 또는 클릭 업로드

       ↓ "회의록 생성" 버튼 클릭

[프로그레스 표시]
  1. 📤 오디오 업로드
  2. 🎙 음성 텍스트 변환 (Whisper)
  3. ✍️ 회의록 생성 (Claude AI)

[결과]
  ├─ 전사 텍스트 (펼치기/접기)
  ├─ 📋 회의록 (마크다운 렌더링)
  └─ ⬇ Markdown 다운로드
```

---

## 8. 알려진 제약사항 및 확장 방향

| 항목 | 현재 상태 | 개선 방향 |
|------|-----------|-----------|
| Whisper 모델 | base (빠름, 정확도 보통) | `small`/`medium` 모델로 전환 가능 |
| 동시 요청 | 싱글톤 모델 공유 (미검증) | 프로세스별 worker 분리 |
| 오디오 길이 제한 | 50MB 파일 크기 제한 | 청크 분할 처리 추가 |
| 화자 분리 | 미지원 | pyannote.audio 통합 가능 |
| 회의록 편집 | 미지원 | 인라인 편집 기능 추가 가능 |
| 히스토리 저장 | 미지원 | SQLite + 조회 UI 추가 가능 |

---

## 9. 품질 검증 체크리스트

- [x] 필수 섹션 포함 (alpha: 개요/분석/결론, epsilon: 변경목록/검증/배포)
- [x] 보안: 파일 확장자 검증, 크기 제한, 임시 파일 자동 삭제, API 키 환경변수 분리
- [x] 의존성: requirements.txt 버전 핀 완료
- [x] 실행 가능: 단일 `uvicorn` 명령으로 즉시 실행
- [x] 사용자 경험: 단계별 프로그레스, 에러 메시지, 다운로드 기능

---

## 10. 오픈소스 활용 현황

**결론: 예, 백엔드 의존성 전체가 오픈소스입니다.** 유일한 비오픈소스 요소는 Anthropic Claude API 서비스(유료 API 키 필요)이며, SDK 자체는 MIT입니다.

| 라이브러리 | 역할 | 라이선스 | 비고 |
|------------|------|----------|------|
| [openai-whisper](https://github.com/openai/whisper) | 음성→텍스트 STT | MIT | OpenAI 공개 모델, 로컬 실행 가능 |
| [FastAPI](https://github.com/tiangolo/fastapi) | 백엔드 웹 프레임워크 | MIT | Python 비동기 API 서버 |
| [uvicorn](https://github.com/encode/uvicorn) | ASGI 서버 | BSD-3-Clause | FastAPI 런타임 |
| [pydub](https://github.com/jiaaro/pydub) | 오디오 포맷 변환 | MIT | ffmpeg 래퍼 |
| [python-multipart](https://github.com/Kludex/python-multipart) | 파일 업로드 파싱 | Apache-2.0 | FastAPI 파일 처리 필수 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 환경변수 로딩 | BSD-3-Clause | .env 파일 지원 |
| [anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) | Claude API 클라이언트 | MIT | SDK는 오픈소스, 서비스는 유료 |

### 라이선스 호환성 요약
- MIT · BSD · Apache-2.0 모두 **상업적 이용 허용**, 재배포 시 저작권 고지 필요
- GPL 계열 라이선스 없음 → 독점 소프트웨어로 배포 시에도 문제 없음
- ffmpeg 는 시스템 의존성(LGPL/GPL)이지만 pydub이 서브프로세스로 호출하므로 앱 코드에 직접 링킹하지 않음

### 유료 API 의존성
- **Anthropic Claude API**: 오픈소스 아님. 사용량 기반 과금. `ANTHROPIC_API_KEY` 발급 필요.
  - 오픈소스 대안: Ollama + llama3/mistral 등 로컬 LLM (품질 차이 있음)

---

## 11. 다운로드 및 사용 방법

### 앱 코드 다운로드
- **ZIP 파일**: `output/회의-녹음-텍스트-변환을-회의록/final/meeting-minutes-app.zip` (약 10KB)
  - 포함 파일: `app/` 전체 (main.py, routers, services, static)
  - 압축 해제 후 `app/` 디렉터리에서 바로 실행 가능

### 문서 / Notion 링크
- **Notion 페이지**: https://www.notion.so/36c363ae08db817784a1f6802e67d76f
  - 전체 구현 보고서 + API 명세 + 실행 가이드 포함

### 빠른 실행 (ZIP 압축 해제 후)
```bash
cd app
pip install -r requirements.txt
cp .env.example .env      # ANTHROPIC_API_KEY 입력
uvicorn main:app --reload --port 8000
# → 브라우저에서 http://localhost:8000 접속
```

> **참고**: 이 앱은 로컬 서버 앱입니다. 별도의 공개 호스팅 URL은 없으며, 위 절차대로 로컬에서 실행해야 합니다.
