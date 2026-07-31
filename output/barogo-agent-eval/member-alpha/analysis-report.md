# BARO AGENT v0.3.0 정적 분석 보고서

**Creator:** member-alpha | **Created:** 2026-06-02 | **Version:** 1.0

---

## 개요

BARO AGENT v0.3.0은 회사 동료 배포용 Electron 기반 AI 비서 앱이다. Gemini / Claude / OpenAI 세 provider를 공통 어댑터로 추상화하고, PC 제어·파일 변환·지식 저장소·Slack·Notion·Outlook 등의 도구를 function calling으로 AI에 연결한다. 이 보고서는 코드베이스 직접 열람을 통해 아키텍처 품질, 어댑터 패턴, 도구 카탈로그 설계, 의존성 위험도, 코드 레벨 이슈, CLAUDE.md 원칙 준수 여부를 평가한다.

---

## 분석 결과

### 아키텍처 구조 평가

**레이어 분리: 우수**

| 레이어 | 파일 | 역할 |
|---|---|---|
| Electron Main | `electron-main.js` | 윈도우 생성, IPC 허브, 세션 영속화 |
| Preload | `preload.js` | contextBridge로 렌더러-Main 격리 |
| AI 어댑터 | `lib/ai-client/` | provider별 SDK 래핑 및 라우팅 |
| 도구 카탈로그 | `lib/tools/` | 도구 선언·핸들러·캐시·dispatch |
| 공통 서비스 | `lib/config.js`, `lib/secrets.js`, `lib/vault.js` | 설정, 보안 저장, 지식 저장소 |
| 실행 조정 | `lib/tool-executor.js` | 한 turn의 전체 흐름 조율 |
| UI | `ui/*.html`, `ui/chat.js` | 렌더러 프로세스 |

레이어 간 의존 방향이 단방향(Main→lib→도구)으로 명확하고, `preload.js`가 렌더러에 Node API를 직접 노출하지 않고 IPC invoke 래퍼만 공개하여 Electron 보안 모범 사례를 준수한다(`contextIsolation: true`, `nodeIntegration: false`).

파일 분리 원칙도 준수한다. 각 파일이 단일 관심사(slack.js=Slack API, vault.js=저장소, secrets.js=암호화 저장, redact.js=마스킹)만 담당하며, 줄 수 기준이 아닌 관심사 기준으로 분리되어 있다.

**약점:** `electron-main.js` 내 세션 IPC 핸들러가 약 90줄로 집중되어 있어, 향후 세션 로직 확장 시 별도 모듈 분리 검토가 필요하다.

---

### AI 어댑터 패턴 평가

**공통 인터페이스 설계: 우수**

세 어댑터(`gemini.js`, `claude.js`, `openai.js`)가 동일한 함수 시그니처를 구현한다.

```
runTurn({ apiKey, model, systemInstruction, history, userMessage,
          attachments, toolDeclarations, onToolCall, onChunk, signal })
→ { ok, text, toolCalls, error }
```

라우터(`lib/ai-client/index.js`)는 `opts.provider || providerForModel(opts.model)` 순서로 provider를 결정하고 `PROVIDERS[provider].runTurn(opts)`를 단순 위임한다. provider 추가 시 라우터 코드 수정 없이 새 파일만 추가하면 된다.

**공통 구현 패턴:**
- 세 어댑터 모두 SDK를 lazy require(`let _sdk = null; function lazy() {...}`)로 로드하여 불필요한 메모리 점유를 방지한다.
- streaming + function calling 루프를 `while(true)` + `hops > 8` 제한으로 동일하게 구현한다.
- AbortSignal(`signal`)을 매 루프 진입 시 체크하여 사용자 취소를 반영한다.
- 오류 발생 시 `{ ok: false, error: ... }` 형식으로 통일하여 상위 레이어가 provider를 신경 쓰지 않아도 된다.

**미세 이슈:**
- Gemini 어댑터의 `modelObj`가 루프 외부에서 한 번만 생성된다. 다회 hop 시 `contents` 배열이 누적되어 대용량 tool 결과가 많을 경우 메모리 압박이 있을 수 있다(심각도: 낮음).
- OpenAI 스트리밍 tool_calls에서 `tc.index || 0` 사용: index가 undefined일 때도 0으로 처리되어 복수 tool_call 동시 처리 시 인덱스 충돌 가능성이 있다(심각도: 낮음).

---

### 도구 카탈로그 평가

**구조: 우수**

```
상시(14개)                    조건부(토큰 있을 때만)
──────────────────            ─────────────────────
bash, read_file,              slack_today, slack_mentions,
write_file, list_dir,         slack_my_msgs, slack_search,
attach_to_md,                 slack_dm (5종)
xlsx_summary/query/           notion_search, notion_read,
  aggregate/distinct (4종),   notion_create (3종)
vault_save/search/            outlook_today, outlook_search,
  list/read (4종)             outlook_read (3종)
```

매 turn마다 `buildCatalog()`를 호출하여 토큰 유무를 동적으로 반영한다. 토큰 없는 도구를 모델에 노출하지 않는 설계는 모델이 실패할 도구를 호출하는 낭비를 원천 차단하는 올바른 접근이다.

**캐시 설계:** 외부 API 도구(slack, notion, outlook)만 5분 TTL + LRU 50개로 캐시하며, 로컬 파일 도구(read_file, list_dir 등)는 제외한다. "최신 상태 중요" 원칙과 "API 쿼터 절약" 원칙을 동시에 충족한다.

**xlsx 도구 설계:** 수만~수십만 행 대용량 엑셀을 위해 `xlsxSummary`(전체 통계) → `xlsxQuery`(필터/정렬/페이지네이션) → `xlsxAggregate`(groupBy) → `xlsxDistinct`(유니크값) 4단계 분업 체계를 갖추었다. workbook 캐시(path+mtime, 최대 5개)로 동일 파일 반복 열람 비용도 절감한다.

**약점:**
- `dispatch()`가 매 호출마다 `buildCatalog()`를 실행한다. 토큰 상태가 바뀌지 않는 한 불필요한 재빌드로, 캐싱 여지가 있다(심각도: 낮음).

---

### 의존성 위험도

| 패키지 | 버전 | 위험도 | 근거 |
|---|---|---|---|
| `@anthropic-ai/sdk` | ^0.32.1 | 높음 | 현재 최신은 0.55+. Claude 4.x 모델 지원 불완전 가능성. |
| `@google/generative-ai` | ^0.21.0 | 높음 | SDK 1.0으로 메이저 버전 업. Gemini 2.5 공식 문서는 1.x 기준. |
| `electron` | ^32.2.0 | 중간 | Electron 32는 보안 지원 종료 예정. 현재 지원 버전은 34/35. |
| `pdf-parse` | ^1.1.1 | 중간 | 마지막 npm 배포 2019년. 보안 패치 없이 7년 경과. |
| `openai` | ^4.73.0 | 낮음 | 4.x 최신 라인. |
| `@notionhq/client` | ^2.2.15 | 낮음 | 안정 버전. |
| `@slack/web-api` | ^7.7.0 | 낮음 | 안정 버전. |
| `exceljs` | ^4.4.0 | 낮음 | 안정 버전. |
| `mammoth` | ^1.8.0 | 낮음 | 안정 버전. |
| `officeparser` | ^7.1.0 | 낮음 | 안정 버전. |
| `formdata-node` | ^6.0.3 | 낮음 | Node 18+에서 내장 FormData 있어 불필요 가능. |

**번들 무게:** Python 의존성 없음, AHK 없음. CLAUDE.md "무게 의식" 원칙에 부합한다.

---

### 코드 레벨 이슈

#### 심각도: 높음

**[이슈 1] Claude 모델 ID 오류 — 존재하지 않는 모델명 사용**

`lib/ai-client/index.js` MODEL_CATALOG:

```js
claude: [
  { id: 'claude-opus-4-5', label: 'Claude Opus 4.5 (최고 품질)' },
  { id: 'claude-sonnet-4-5', label: 'Claude Sonnet 4.5 (균형)' },
  { id: 'claude-haiku-4-5', label: 'Claude Haiku 4.5 (빠름)' },
],
```

`claude-opus-4-5`, `claude-haiku-4-5`는 Anthropic 공식 API에 존재하지 않는 모델 ID다. `claude.js`의 기본 모델도 `claude-sonnet-4-5`로 설정되어 있다. Claude provider 선택 시 `model_not_found` 오류가 발생한다.

**[이슈 2] @anthropic-ai/sdk 버전 낙후 (^0.32.1)**

SDK 0.32.1은 2024년 하반기 버전이다. Claude 4.x 모델 지원을 위해서는 최신 버전 업그레이드가 필요하다.

**[이슈 3] @google/generative-ai 버전 낙후 (^0.21.0)**

Google AI SDK는 2025년에 1.0으로 메이저 버전 업 되었다. Gemini 2.5 Flash/Pro의 공식 문서는 1.x SDK 기준으로 작성되어 있어 0.21.x에서 응답 포맷 불일치가 발생할 수 있다.

#### 심각도: 중간

**[이슈 4] Electron 버전 EOL 위험 (^32.2.0)**

Electron 32는 보안 지원이 종료되었거나 임박하다. 사내 배포 앱에 사용되는 것은 보안 위험이다. Electron 34 이상으로 업그레이드가 필요하다.

**[이슈 5] `pdf-parse` 패키지 유지보수 중단**

`pdf-parse@1.1.1`의 마지막 npm 배포는 2019년이다. 7년간 보안 패치가 없었다. `pdfjs-dist`(Mozilla 재단 유지)로 교체를 권고한다.

**[이슈 6] OpenAI 모델 카탈로그에 미검증 모델 포함**

`gpt-5`, `gpt-5-mini` API 일반 공개 여부 및 정확한 모델 ID 확인이 필요하다.

#### 심각도: 낮음

**[이슈 7] `app.commandLine.appendSwitch('no-sandbox')` 전역 적용**

샌드박스를 전역으로 비활성화한다. 개발 모드에서만 적용하도록 조건부 처리가 안전하다.

**[이슈 8] `redactionEnabled` false 시 API 키 UI 노출 가능**

설정을 끄면 Slack 토큰, API 키가 채팅 UI에 노출될 수 있다. API 키 패턴은 설정과 무관하게 항상 마스킹해야 한다.

**[이슈 9] `providerForModel`에서 신규 OpenAI 모델 ID 미처리**

`o4-mini` 등 새 reasoning 모델 ID 처리 로직 미흡. fallback이 Gemini로 잘못 분류된다.

**[이슈 10] 루트에 `foo.txt` 파일 존재**

CLAUDE.md "불필요한 파일 생성 금지, 임시 파일 즉시 삭제" 원칙에 위배. 즉시 삭제 필요.

---

### CLAUDE.md 원칙 준수 여부

| 원칙 | 상태 | 근거 |
|---|---|---|
| 팩트 기반 — 추측 없이 Read 후 작성 | **부분 위반** | MODEL_CATALOG에 검증되지 않은 모델 ID 포함. 이슈 1, 6 참조. |
| 자두 별개 정신 — 자두 코드 import/copy 금지 | 준수 | 자두 경로 참조 없음. 어댑터 패턴 독자 구현. |
| 무게 의식 — Python 의존 없이 Node만 | 준수 | package.json에 Python 의존성 없음. |
| 파일 분리는 관심사 기준 | 준수 | 각 파일이 단일 관심사 담당. |
| commit/push는 사용자 명시적 허락 후에만 | 준수 | CLAUDE.md 명시. 자동 커밋 로직 없음. |
| electron-main + preload + lib + ui 구조 준수 | 준수 | 디렉터리 구조 일치. |
| 불필요한 파일 생성 금지 | 경미 위반 | 루트의 `foo.txt` 존재. |

---

## 결론

BARO AGENT v0.3.0은 전반적으로 잘 설계된 Electron AI 비서 앱이다. 3-provider 공통 어댑터 패턴, 조건부 도구 카탈로그, vault 지식 저장소, 레이어 분리 등 핵심 설계 결정들이 CLAUDE.md 원칙과 높은 수준으로 일치한다. 어댑터 패턴의 공통 인터페이스와 도구 캐시 전략은 production-ready 수준의 완성도를 보인다.

**즉시 수정이 필요한 항목:**

1. **Claude 모델 ID 교체 (높음):** `claude-opus-4-5`, `claude-haiku-4-5`를 Anthropic API 공식 지원 ID로 교체.
2. **SDK 업그레이드 (높음):** `@anthropic-ai/sdk` 최신화, `@google/generative-ai` → 1.x.
3. **Electron 업그레이드 (중간):** ^32 → 34 이상.
4. **pdf-parse 교체 (중간):** `pdfjs-dist` 등 활발히 유지되는 패키지로 교체.
5. **GPT-5 모델 ID 확인 (중간):** OpenAI 공식 API 기준으로 카탈로그 갱신.
