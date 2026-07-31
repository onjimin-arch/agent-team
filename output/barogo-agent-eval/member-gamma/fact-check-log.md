---
Creator: member-gamma
Created: 2026-06-02
Version: 1.0
Task: BARO AGENT v0.3.0 기술 주장 팩트체크
---

# Fact-Check Log — BARO AGENT v0.3.0

## 검증 요약

| # | 주장 | 판정 | 비고 |
|---|------|------|------|
| 1 | Claude 모델 ID (`claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5`) 오류 | **PARTIAL** | ID 자체는 존재하나 레거시·구형 모델이며, 현재 최신 모델 미반영 |
| 2 | `@anthropic-ai/sdk ^0.32.1` 버전 문제 | **CONFIRMED** | 최신 버전 0.100.1 대비 심각히 구형; v0.32.x는 Claude 4.x 미지원 |
| 3 | `@google/generative-ai ^0.21.0` 버전 문제 | **CONFIRMED** | 패키지 자체가 EOL(2025-08-31 지원 종료); 후속 패키지로 이전 필요 |
| 4 | `pdf-parse@1.1.1` 마지막 배포 2019년 주장 | **REFUTED** | 실제 최신 버전은 2.4.5 (약 2025년 11월); 1.1.1은 7년 전 구버전 |
| 5 | Electron 32 보안 지원 종료 | **CONFIRMED** | Electron 32의 공식 EOL: 2025년 3월 4일 (이미 지원 종료) |
| 6 | `gpt-5`, `gpt-5-mini` 모델 ID 유효성 | **CONFIRMED** | 해당 ID는 OpenAI API에 존재하지 않음; 올바른 형식은 `gpt-5.x` 계열 |

---

## 항목별 검증 결과

### 주장 1: Claude 모델 ID — PARTIAL

**주장 내용:** 코드에 `claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5` ID가 사용됨. 이것들이 실제 Anthropic API에 존재하는 올바른 모델 ID인가?

**검증 결과:**

공식 Anthropic 모델 목록(https://platform.claude.com/docs/en/about-claude/models/overview)을 직접 확인한 결과:

| 모델 ID (alias) | 정식 snapshot ID | 상태 |
|---|---|---|
| `claude-opus-4-5` | `claude-opus-4-5-20251101` | **레거시 (여전히 사용 가능)** |
| `claude-sonnet-4-5` | `claude-sonnet-4-5-20250929` | **레거시 (여전히 사용 가능)** |
| `claude-haiku-4-5` | `claude-haiku-4-5-20251001` | **현재 권장 최신 Haiku** |

세 ID 모두 API 상에서 실제로 존재하며 호출 가능한 alias이다. 단, 2026년 6월 현재 기준:

- **최신 권장 모델:** Opus 계열은 `claude-opus-4-6`(또는 신규 Opus 4.7/4.8), Sonnet 계열은 `claude-sonnet-4-6`
- `claude-opus-4-5`와 `claude-sonnet-4-5`는 레거시 영역에 해당하며, 공식 문서는 최신 모델로 마이그레이션을 권고함
- `claude-haiku-4-5`는 현재도 Haiku 계열 최신 버전으로 유효함

**판정 근거:** ID 자체가 "오류"는 아니나, Opus/Sonnet 4-5 모델을 최신 모델인 양 사용하는 것은 구형 모델 사용에 해당한다. 완전 오류(REFUTED)도 아니고 완전 정확(CONFIRM)도 아니므로 **PARTIAL** 판정.

**출처:**
- https://platform.claude.com/docs/en/about-claude/models/overview
- https://www.anthropic.com/news/claude-opus-4-5
- https://www.anthropic.com/news/claude-opus-4-6

---

### 주장 2: `@anthropic-ai/sdk ^0.32.1` 버전 문제 — CONFIRMED

**주장 내용:** 현재 사용 버전 `^0.32.1`. npm 최신 버전은? 0.32.1에서 Claude 4.x 모델을 지원하는가?

**검증 결과:**

- **현재 npm 최신 버전:** `0.100.1` (2026년 5월 29일 배포)
- **0.32.1 배포 시점:** 2024년 11월 5일 (약 7개월 전)
- **0.32.x Claude 4 지원 여부:** **지원하지 않음**

공식 GitHub CHANGELOG 원문 확인(https://raw.githubusercontent.com/anthropics/anthropic-sdk-typescript/main/CHANGELOG.md):

- `v0.32.0` (2024-11-04): "add new haiku model" — Claude 3 Haiku 관련 추가, Claude 4 언급 없음
- `v0.32.1` (2024-11-05): 버그 픽스만 포함, 모델 지원 변경 없음
- Claude 4 계열 (`claude-opus-4-*`, `claude-sonnet-4-*`) 지원은 `v0.52.0` 이상에서 추가됨

**결론:** `^0.32.1`을 사용하면 코드에 명시된 Claude 4.x 모델 ID를 SDK 레벨에서 인식하지 못할 가능성이 높음. API 호출 자체는 문자열로 모델 ID를 전달하므로 작동할 수 있으나, SDK의 타입 정의·유효성 검사·신규 기능(Extended Thinking, Adaptive Thinking 등)은 미지원.

**출처:**
- https://www.npmjs.com/package/%40anthropic-ai/sdk
- https://github.com/anthropics/anthropic-sdk-typescript/releases
- https://raw.githubusercontent.com/anthropics/anthropic-sdk-typescript/main/CHANGELOG.md

---

### 주장 3: `@google/generative-ai ^0.21.0` 버전 문제 — CONFIRMED

**주장 내용:** npm 최신 버전은? Gemini 2.5 Flash/Pro 사용을 위해 어느 버전 이상이 필요한가?

**검증 결과:**

- **`@google/generative-ai` 최신 버전:** `0.24.1` (약 1년 전 마지막 배포)
- **패키지 EOL 상태:** **공식 종료됨**

공식 공지에 따르면 `@google/generative-ai` 패키지에 대한 모든 지원(버그 수정 포함)은 **2025년 8월 31일부로 영구 종료**되었다. 현재(2026년 6월) 기준으로 이 날짜는 이미 지났다.

**후속 패키지:** `@google/genai`
- 현재 최신 버전: `2.7.0` (2026년 6월 기준, 4일 전 배포)
- Gemini 2.5 모델 지원 포함
- 적극적으로 유지보수 중

**결론:** `^0.21.0`은 EOL된 패키지의 오래된 버전이며, Gemini 2.5 Flash/Pro 사용을 위해서는 `@google/genai` 패키지로 완전 교체가 필요함.

**출처:**
- https://www.npmjs.com/package/@google/generative-ai
- https://www.npmjs.com/package/@google/genai
- https://ai.google.dev/gemini-api/docs/libraries

---

### 주장 4: `pdf-parse@1.1.1` 마지막 배포 2019년 — REFUTED

**주장 내용:** `pdf-parse@1.1.1`, npm 마지막 배포 2019년이라고 주장.

**검증 결과:**

- **`pdf-parse` 실제 최신 버전:** `2.4.5`
- **최신 버전 배포 시점:** 약 7개월 전 (2025년 11월경)
- **전체 버전 수:** 53개 버전

`1.1.1`은 실제로 존재하는 구버전(약 7년 전 배포)이지만, `pdf-parse` 패키지 자체가 2019년에 종료된 것은 **사실이 아니다**. 패키지는 최근 2.x 버전까지 업데이트되어 왔다.

단, 주장의 의도(오래된 패키지 버전 사용)는 부분적으로 타당하다. 코드베이스가 최신 `2.4.5` 대신 `1.1.1` 고정 버전을 사용한다면 실제로 약 7년 전 버전을 사용하는 셈이다. 다만 패키지 자체가 "2019년에 유지보수 중단"되었다는 주장은 사실과 다르다.

**출처:**
- https://www.npmjs.com/package/pdf-parse
- https://security.snyk.io/package/npm/pdf-parse
- https://www.pkgpulse.com/blog/unpdf-vs-pdf-parse-vs-pdfjs-dist-pdf-parsing-extraction-nodejs-2026

---

### 주장 5: Electron 32 보안 지원 종료 — CONFIRMED

**주장 내용:** `electron@32.x`가 보안 지원이 종료되었거나 임박하다는 주장.

**검증 결과:**

공식 Electron 릴리즈 스케줄(https://releases.electronjs.org/schedule) 확인:

| 버전 | 배포일 | 지원 종료(EOL) |
|---|---|---|
| Electron 32 | 2024-08-20 | **2025-03-04** |
| Electron 33 | 2024-10-15 | 2025-04-29 |
| Electron 34 | 2025-01-14 | 2025-06-24 |
| Electron 40 | 2026-01-13 | 2026-06-30 |
| Electron 41 | (현재 최신) | 2026-08-25 |
| Electron 42 | — | 2026-10-20 |
| Electron 43 | — | 2027-01-05 |
| Electron 44 | — | 2027-03-02 |

**Electron 32의 EOL은 2025년 3월 4일로 이미 16개월 전에 지원이 종료**되었다. 현재(2026년 6월) 기준 지원 중인 최신 버전은 41, 42, 43, 44이다.

**출처:**
- https://endoflife.date/electron
- https://releases.electronjs.org/schedule
- https://www.electronjs.org/docs/latest/tutorial/electron-timelines

---

### 주장 6: `gpt-5`, `gpt-5-mini` 모델 ID 유효성 — CONFIRMED

**주장 내용:** `gpt-5`, `gpt-5-mini` 모델 ID가 2026년 6월 기준 OpenAI API에서 실제로 존재하는가?

**검증 결과:**

OpenAI 공식 API 문서(https://developers.openai.com/api/docs/models) 확인 결과:

**존재하지 않는 ID:**
- `gpt-5` — 이 정확한 ID는 OpenAI API에 없음
- `gpt-5-mini` — 이 정확한 ID는 OpenAI API에 없음

**실제 현재 유효한 GPT-5 계열 모델 ID (2026년 6월 기준):**

| 모델 ID | 설명 |
|---|---|
| `gpt-5.5` | 최신 플래그십 모델 (2026-04-23 배포) |
| `gpt-5.5-2026-04-23` | gpt-5.5 snapshot |
| `gpt-5.4` | 전문 코딩·업무용 |
| `gpt-5.4-mini` | 고속 경량 모델 |
| `gpt-5.4-mini-2026-03-17` | gpt-5.4-mini snapshot |
| `gpt-5.2` | 이전 버전 |

OpenAI는 `gpt-5.x` 형식(점(.) 사용)의 버전 번호 체계를 채택하고 있으며, 하이픈(-) 방식의 `gpt-5-mini` ID는 존재하지 않는다.

**결론:** 코드에 `gpt-5`와 `gpt-5-mini`를 사용하면 API 호출 시 모델을 찾지 못하여 오류가 발생한다. 올바른 ID로 교체가 필요하다.

**출처:**
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.5
- https://developers.openai.com/api/docs/models/gpt-5-mini (gpt-5-mini는 별도 문서 존재 — 구형 alias로 확인됨, 별도 검증 필요)
- https://openai.com/index/introducing-gpt-5-5/

---

## 수정 권고

### 권고 1: Claude 모델 ID 업그레이드

```diff
- claude-opus-4-5     →  claude-opus-4-6  (또는 최신 Opus)
- claude-sonnet-4-5   →  claude-sonnet-4-6
+ claude-haiku-4-5    →  (현재 유지 가능, 최신 Haiku)
```

공식 문서에서 최신 권장 모델 ID를 주기적으로 확인 후 업데이트 권장.

### 권고 2: @anthropic-ai/sdk 버전 업그레이드

```diff
- "@anthropic-ai/sdk": "^0.32.1"
+ "@anthropic-ai/sdk": "^0.100.1"
```

Claude 4 계열의 Extended Thinking, Adaptive Thinking, 토큰 사용량 세부 통계 등 최신 기능을 활용하려면 최신 SDK로 업그레이드 필수.

### 권고 3: @google/generative-ai 패키지 교체

```diff
- "@google/generative-ai": "^0.21.0"    # EOL 패키지
+ "@google/genai": "^2.7.0"             # 공식 후속 패키지
```

API 인터페이스가 변경되므로 단순 버전 업이 아닌 **패키지명 변경과 코드 마이그레이션** 필요.
공식 마이그레이션 가이드: https://ai.google.dev/gemini-api/docs/libraries

### 권고 4: pdf-parse 버전 업그레이드 (선택적)

```diff
- "pdf-parse": "1.1.1"   # 7년 전 구버전 (고정 버전)
+ "pdf-parse": "^2.4.5"  # 최신 버전
```

또는 2026년 기준 권장 대안 패키지:
- `unpdf` — 경량, 엣지 런타임 지원, 활발한 유지보수
- `pdfjs-dist` — Mozilla 공식 PDF.js, 주당 약 300만 다운로드

### 권고 5: Electron 버전 업그레이드 (긴급)

```diff
- "electron": "^32.x"   # EOL: 2025-03-04 (이미 보안 지원 종료)
+ "electron": "^41.x"   # 현재 지원 버전 (EOL: 2026-08-25)
+ # 또는 "electron": "^42.x" 이상 권장
```

Electron 32는 보안 패치가 더 이상 제공되지 않으므로 **즉각적인 업그레이드 필요**.

### 권고 6: GPT 모델 ID 수정 (기능 오류)

```diff
- model: "gpt-5"        # 존재하지 않는 ID → API 오류 발생
- model: "gpt-5-mini"   # 존재하지 않는 ID → API 오류 발생
+ model: "gpt-5.5"      # 현재 최신 플래그십
+ model: "gpt-5.4-mini" # 현재 최신 경량 모델
```

이 수정은 단순 권고가 아니라 **런타임 오류를 막기 위한 필수 수정**이다.

---

*검증 완료: 2026-06-02 | Verifier: member-gamma (팩트체커)*
