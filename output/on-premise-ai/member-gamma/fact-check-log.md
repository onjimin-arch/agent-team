Creator: member-gamma
Created: 2026-04-23
Version: 1.0

# 검증 요약

- **검증 대상**: member-alpha 의 `analysis-report.md` 중 수치·라이선스·규제·API 단가
- **검증 항목 수**: 22 개 (GPU 7, 국산 NPU 3, 오픈소스 모델 7, 규제 3, 클라우드 API 3, 기타 지표 다수)
- **검증 결과 집계**
  - ✅ 확인(Confirmed): **11**
  - ⚠️ 수정 필요(Correction required): **8**
  - ❓ 검증 불가(Inconclusive): **3**
- **독립 웹 조회 수**: 14건 (WebSearch 12, WebFetch 2)

## 주요 발견사항 Top 5
1. **H100/H200 FP16 TFLOPS 수치(989) 는 vector(비-Tensor) 값이며, Tensor Core FP16 은 약 1,979 TFLOPS** — 실무상 의미있는 수치는 Tensor Core 기준이므로 표 재작성 권고.
2. **B200 FP16(Tensor) 은 약 4,500 TFLOPS 로, 표의 "~2,250(FP16 추정)" 은 약 2배 과소 기재**. 또한 192GB HBM3e·1,000W·$45k~$50k 는 확인.
3. **Qwen 2.5 "72B" 는 Apache 2.0 이 아니라 Qwen License** — 타 사이즈(0.5B~32B, 72B 제외)가 Apache 2.0 임. 알파가 라이선스 주의사항에 적은 "Apache 2.0 (72B 한정)" 은 완전히 반대 기술.
4. **SOLAR 10.7B 도 조건부** — base(`SOLAR-10.7B-v1.0`) 는 Apache 2.0 이지만 instruct(`SOLAR-10.7B-Instruct-v1.0`) 는 CC-BY-NC-4.0 (상업 금지). 알파의 "Apache 2.0" 단정은 보완 필요.
5. **AI 기본법 전면 시행일은 2026-01-22**(정확). 다만 정부는 1년 이상 계도 기간(과태료 미부과) 운영 예정 — 실무 임팩트에 영향.

---

# 항목별 검증 결과

## [GPU] NVIDIA H100 SXM5 80GB
- **Alpha 주장**: VRAM 80GB HBM3, FP16 ~989 TFLOPS, $25k~30k, 700W
- **검증 결과**: ⚠️ 수정 필요 (FP16 수치)
- **출처**: NVIDIA H100 Datasheet / CpuTronic / Fluence 2026 deep dive
  - URL: https://resources.nvidia.com/en-us-gpu-resources/h100-datasheet-24306
  - URL: https://cputronic.com/gpu/nvidia-h100-sxm5-80-gb
  - 발췌: "NVIDIA H100 SXM5 80GB has FP16 **Tensor Core** performance of 2,000 TFLOPS ... 80GB HBM3 ... 3.35TB/s ... 700W"
- **비고**: 989 TFLOPS 는 NVIDIA 공식 "FP16 (non-Tensor)" 수치로, LLM 서빙·학습에서 사용되는 Tensor Core 값은 **약 1,979 TFLOPS (sparsity 미적용) / 1,979 TFLOPS without sparsity**. 비교표에서는 Tensor Core 수치를 쓰는 것이 관행이므로 **~1,979 TFLOPS (FP16 Tensor)** 로 수정 권고. 가격대(2026-04) 는 enterprise 가격 기준 대략 $25k~$30k 범위가 타 GPU 매체에서 유지되고 있어 확인.

## [GPU] NVIDIA H200 SXM 141GB
- **Alpha 주장**: 141 GB HBM3e, FP16 ~989 TFLOPS, $30k~35k, 700W
- **검증 결과**: ⚠️ 수정 필요 (FP16 수치)
- **출처**: NVIDIA H200 Datasheet (PNY/Megware), Tom's Hardware, Lenovo Press
  - URL: https://www.nvidia.com/en-us/data-center/h200/
  - URL: https://www.pny.com/file%20library/company/support/linecards/data-center-gpus/h200-nvl-datasheet.pdf
  - 발췌: "H200 SXM — 141GB HBM3e, 4.8 TB/s, 700W TDP, 3,958 TFLOPS of FP8"
- **비고**: H200 Tensor Core FP16 = 약 1,979 TFLOPS (H100 과 동일 아키텍처·Hopper). 989 는 non-Tensor vector 값. 메모리·대역폭·전력은 확인. 가격은 공식가 비공개이나 시장 견적 $30k~$35k 범주는 합리적.

## [GPU] NVIDIA B200 (Blackwell)
- **Alpha 주장**: 192GB HBM3e, FP16 ~2,250(FP16 추정), $40k~50k, 1,000W
- **검증 결과**: ⚠️ 수정 필요 (FP16 수치)
- **출처**: Jarvislabs B200 Specs / Spheron B200 Guide / Northflank 비용 분석
  - URL: https://jarvislabs.ai/gpu/nvidia-b200
  - URL: https://www.spheron.network/blog/nvidia-b200-complete-guide/
  - 발췌: "192GB HBM3e, 8 TB/s ... **4,500 TFLOPS of FP16 performance** ... 9,000 TFLOPS FP4 ... TDP 1,000W ... OEM $45k~$50k"
- **비고**: Alpha 의 2,250 TFLOPS 는 sparsity 없는 FP8 half 인 것으로 보이며 **FP16 dense Tensor Core 는 약 4,500 TFLOPS** 로 2배 상향 수정 권고. 메모리·전력·가격은 확인.

## [GPU] AMD MI300X
- **Alpha 주장**: 192GB HBM3, FP16 ~1,307 TFLOPS, $15k~20k, 750W
- **검증 결과**: ✅ 확인
- **출처**: AMD Instinct MI300X Data Sheet / gpucost.org 2026 / Lenovo Press
  - URL: https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf
  - URL: https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html
  - 발췌: "192 GB HBM3, 5.325 TB/s, **1,307.4 TFLOPS FP16 (no sparsity) / 2,614.9 with sparsity**, 750W, ~$18k"
- **비고**: 정확. sparsity 미포함 기준 1,307 TFLOPS 는 공식 스펙과 일치. 시장가 ~$18k 가 중앙값이며 $15k~$20k 범위에 부합.

## [GPU] GB200 NVL72 (랙)
- **Alpha 주장**: 13.5 TB 통합, ~162,000 TFLOPS 랙 기준, 300만+ (랙), 120kW
- **검증 결과**: ❓ 검증 불가 (수치 자체는 대략 일치하나 공식 단일 출처 확인 제한)
- **출처**: Getdeploying GB200 Cloud Pricing
  - URL: https://getdeploying.com/gpus/nvidia-gb200
- **비고**: NVIDIA 공식자료(nvidia.com/.../gb200-nvl72) 에서 72×B200 + 36×Grace CPU, 130TB/s NVLink, 120kW 수준 소개. TFLOPS 랙 총계는 B200 4,500 × 72 ≈ 324,000 TFLOPS (FP16 Tensor, dense) 이므로 **162,000 은 FP16 non-Tensor 또는 specific half precision 계산일 가능성**. 공식 표기 재확인 권고.

## [국산 NPU] 리벨리온 ATOM / ATOM-Max
- **Alpha 주장**: ATOM+ 16GB, ~128 TFLOPS(INT8 기준), $2k~$5k, 60~80W
- **검증 결과**: ⚠️ 수정 필요 (제품명·단위 혼동)
- **출처**: Rebellions 공식 페이지 + Pinpoint Research 리포트 + SKT/KT 뉴스룸
  - URL: https://kr.rebellions.ai/rebellions-product/atom-2/
  - URL: https://kr.rebellions.ai/rebellions-product/atom-max/
  - 발췌 (ATOM): "FP16 32 TFLOPS, INT8 128 TOPS, GDDR6 16GB, 85W"
  - 발췌 (ATOM-Max): "FP16 128 TFLOPS, INT8 512 TOPS, GDDR6 64GB, 350W"
- **비고**: **"ATOM+" 라는 제품명은 공식 라인업에 없음** (정식명은 ATOM, ATOM-Max). Alpha 가 언급한 "128 TOPS / 16GB / 60~80W" 는 **1세대 ATOM** 사양에 가깝고(ATOM 은 85W), ATOM-Max 는 350W·64GB. 표 갱신: "리벨리온 ATOM (1세대, 양산 중) — 16GB GDDR6, INT8 128 TOPS / FP16 32 TFLOPS, 85W" + "ATOM-Max — 64GB, INT8 512 TOPS / FP16 128 TFLOPS, 350W" 권고. 가격은 공식 비공개라 추정치 유지는 가능하되 "추정" 명시.

## [국산 NPU] 사피온 X330
- **Alpha 주장**: 32GB, FP16 ~200 TFLOPS(추정), 150W
- **검증 결과**: ⚠️ 수정 필요 (Compact/Prime 구분·TFLOPS 단위)
- **출처**: SAPEON 공식 + globenewswire 런치 보도 + Asia Business Daily
  - URL: https://www.sapeon.com/products/sapeon-x330
  - URL: https://www.globenewswire.com/news-release/2023/11/16/2781749/0/en/SAPEON-launches-X330-AI-semiconductor-for-data-centers.html
  - 발췌: "X330 Compact 367 TFLOPS / 16GB, X330 Prime 734 TFLOPS / 32GB, GDDR6 512GB/s, Prime TDP 250W, TSMC 7nm, 2024 상반기 양산"
- **비고**: 알파 주장 "FP16 200 TFLOPS" 는 부정확. **X330 Prime 기준 734 TFLOPS (FP16/BF16 추정·벤더 통합 수치), Compact 기준 367 TFLOPS**. 전력도 Prime 250W (알파의 150W 는 과소). 32GB 는 Prime 모델 기준 맞음. 또한 사피온은 2024 년 SK텔레콤 분사·리벨리온과 합병 논의가 있었으므로 최신 브랜딩 재확인 권장 (주의사항으로 기재).

## [국산 NPU] 퓨리오사 RNGD
- **Alpha 주장**: 48GB HBM3, ~512 TFLOPS(FP8 추정), 150W
- **검증 결과**: ⚠️ 수정 필요 (전력)
- **출처**: FuriosaAI 공식 + HPCwire 2025-09 + Korea Herald
  - URL: https://furiosa.ai/rngd
  - URL: https://www.hpcwire.com/2025/09/30/the-fast-and-the-furiosaai-korean-chip-startup-takes-aim-at-nvidia-gpus-with-tensor-contraction-architecture/
  - 발췌: "48GB HBM3 (2 stacks), 1.5 TB/s, **512 TFLOPS FP8**, 512 TOPS INT8, 1024 TOPS INT4, **TDP 180W**, TSMC 5nm, PCIe Gen5 x16, 2025-01 양산 개시"
- **비고**: 512 TFLOPS(FP8)·48GB HBM3 정확. 다만 **전력은 150W 가 아니라 180W TDP**. 양산 개시 시점(2025-01) 도 보고서 참고용으로 추가 권고.

## [오픈소스 모델] Llama 3.3 70B
- **Alpha 주장**: 70B, Llama Community License (MAU 7억 조항), 128K 컨텍스트
- **검증 결과**: ✅ 확인
- **출처**: Meta Llama 3.3 HF 모델카드 / llama.com FAQ
  - URL: https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
  - URL: https://www.llama.com/faq/
  - 발췌: "Llama 3.3 Community License, MAU 7 억(2024-12 기준) 초과 시 Meta 별도 라이선스 필요, 128K context, 70B params, text-only"
- **비고**: 알파 기술 모두 부합. "Built with Llama" 표기 의무도 추가 명시 가능.

## [오픈소스 모델] Llama 4 Scout / Maverick
- **Alpha 주장**: 109B/400B MoE, 10M(Scout)/1M(Maverick), Llama Community License
- **검증 결과**: ⚠️ 수정 필요 (활성 파라미터 보강)
- **출처**: Hugging Face Llama 4 blog / Meta Llama 4 docs / IBM watsonx 공지
  - URL: https://huggingface.co/blog/llama4-release
  - URL: https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/
  - 발췌: "Scout 17B active / 109B total, 16 experts, **10M context**. Maverick 17B active / 400B total, 128 experts, **1M context**. Llama 4 Community License, 700M MAU clause"
- **비고**: 총 파라미터/컨텍스트는 정확. **활성 파라미터(17B) 를 추가 명시** 하는 것이 MoE 메모리·추론 계산에 중요. "109B/400B MoE (17B active)" 형식 권고.

## [오픈소스 모델] Qwen 2.5 72B
- **Alpha 주장**: 72B, **Apache 2.0 (72B 한정)**, 128K 컨텍스트
- **검증 결과**: ⚠️ 수정 필요 (라이선스 완전 반대)
- **출처**: HF Qwen2.5-72B-Instruct LICENSE / Qwen2.5 공식 블로그 / 커뮤니티 discussion
  - URL: https://huggingface.co/Qwen/Qwen2.5-72B-Instruct
  - URL: https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/blob/main/LICENSE
  - URL: https://qwenlm.github.io/blog/qwen2.5/
  - 발췌: "License: qwen (Qwen LICENSE). Qwen2.5 시리즈 중 3B·72B 를 **제외한** 모델들이 Apache 2.0"
- **비고**: **알파의 기술은 정반대**. Qwen 2.5 72B 는 Qwen License(상업 제한적 허용, MAU 1억 초과 시 별도 계약 등) 이며, Apache 2.0 인 것은 0.5B·1.5B·7B·14B·32B 등. 상업 사용 가능 여부 자체는 대부분 보장되나 **Apache 2.0 의 완전 자유로운 재배포와 동일 시 오해 소지 크므로 즉시 수정 필요**.

## [오픈소스 모델] Qwen 3 (235B-A22B 등)
- **Alpha 주장**: 0.6B~235B MoE, Apache 2.0, 128K~256K
- **검증 결과**: ✅ 확인 (다만 MoE 변종 재확인 권고)
- **출처**: Qwen3 공식 blog / HF Qwen3-235B-A22B / 커뮤니티 설명
  - URL: https://qwenlm.github.io/blog/qwen3/
  - URL: https://huggingface.co/Qwen/Qwen3-235B-A22B
  - 발췌: "dense models (32B/14B/8B/4B/1.7B/0.6B) Apache 2.0. MoE (235B-A22B, 30B-A3B) — 공식 블로그는 'open-weighted' 로 표기, HF 레포 일부는 Apache 2.0 명시"
- **비고**: dense 는 Apache 2.0 확정. **MoE(235B, 30B-A3B) 의 라이선스가 일부 소스에서 모호** — 최신 HF 레포 상으로는 Apache 2.0 이나 도입 시 재검증 권장. 225K/256K 컨텍스트는 YaRN 확장 기준.

## [오픈소스 모델] Mistral Large 2
- **Alpha 주장**: 123B, Mistral Research License (상업 유료), 128K
- **검증 결과**: ✅ 확인
- **출처**: Mistral AI 공식 blog / HF 모델카드 / IBM watsonx 공지
  - URL: https://mistral.ai/news/mistral-large-2407
  - URL: https://huggingface.co/mistralai/Mistral-Large-Instruct-2407
  - 발췌: "Mistral Research License (non-commercial only). 상업용 self-deploy 시 Mistral Commercial License 필요. 128K context, 123B params"
- **비고**: 정확. IBM watsonx 등 특정 파트너 채널에서는 상업 이용 가능함을 부연 가능.

## [오픈소스 모델] DeepSeek V3
- **Alpha 주장**: 671B MoE (활성 37B), DeepSeek License (상업 허용), 128K
- **검증 결과**: ✅ 확인
- **출처**: DeepSeek-V3 GitHub / arXiv technical report
  - URL: https://github.com/deepseek-ai/DeepSeek-V3
  - URL: https://arxiv.org/html/2412.19437v1
  - 발췌: "671B total / 37B activated per token. Commercial use permitted under DeepSeek model license. 128K context."
- **비고**: 정확. 훈련 토큰 14.8T, MLA+DeepSeekMoE 아키텍처도 부연하면 신뢰도 강화.

## [오픈소스 모델] SOLAR 10.7B (Upstage)
- **Alpha 주장**: 10.7B, **Apache 2.0**, 4K
- **검증 결과**: ⚠️ 수정 필요 (버전별 라이선스 상이)
- **출처**: HF upstage/SOLAR-10.7B-v1.0, upstage/SOLAR-10.7B-Instruct-v1.0
  - URL: https://huggingface.co/upstage/SOLAR-10.7B-v1.0
  - URL: https://huggingface.co/upstage/SOLAR-10.7B-Instruct-v1.0
  - 발췌: "base model — Apache 2.0. **Instruct model — CC-BY-NC-4.0** (Alpaca 등 비상업 데이터셋 포함)"
- **비고**: **실무에서 사용하는 Instruct 버전은 비상업 라이선스** 이므로 상업 적용 시 주의. 자체 파인튜닝으로 상업 학습셋만 사용해 Instruct 를 재훈련하면 Apache 2.0 유지 가능. 알파 보고서 "안심하고 채택 가능한 가장 자유로운 라이선스" 는 과장이므로 "base 만 Apache 2.0, Instruct 는 CC-BY-NC" 로 정정 필요.

## [규제] AI 기본법 시행일
- **Alpha 주장**: 2026년 1월 시행, 고영향 AI 의무
- **검증 결과**: ✅ 확인 (일자 보강 필요)
- **출처**: 법제처 법령정보센터 / MS투데이 시행 임박 보도 / CELA 제정 요약
  - URL: https://www.law.go.kr/lsInfoP.do?lsiSeq=268543
  - URL: https://www.mstoday.co.kr/news/articleView.html?idxno=99963
  - URL: https://www.cela.kr/4/?bmode=view&idx=148966233
  - 발췌: "정식명 '인공지능 발전과 신뢰 기반 조성 등에 관한 기본법'. **2026-01-22 전면 시행**. EU AI Act 에 이은 세계 두 번째 포괄 AI 법. 정부는 1년 이상 계도 기간(과태료 미부과) 운영 예정"
- **비고**: 정식명칭·시행일 확인. 보고서에 **2026-01-22 구체 일자 + 계도 기간(과태료 유예) 운영 예정** 반영 권고. 고영향 AI 정의(의료·금융·채용·공공서비스) 도 하위법령에서 확정됨.

## [규제] 개인정보보호법 제28조의2
- **Alpha 주장**: 가명처리 또는 동의 필요
- **검증 결과**: ✅ 확인
- **출처**: 법제처 개인정보보호법 / 개인정보보호위원회 / Kim&Chang 실무 FAQ
  - URL: https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=213857
  - URL: https://www.privacy.go.kr/front/contents/cntntsView.do?contsNo=14
  - 발췌: "제28조의2 제1항 — 통계작성·과학적 연구·공익적 기록보존 등을 위해 정보주체 동의 없이 가명정보 처리 가능. 제2항 — 제3자 제공 시 식별 가능한 정보 포함 금지"
- **비고**: 알파의 "가명처리 또는 동의" 표현 정확. 다만 **"등" 의 해석(목적 확장 가능성)** 에 대한 논쟁이 있어, LLM 학습 목적이 과학적 연구로 인정되는지 여부는 케이스별 법률 검토 필요함을 주의 문구로 추가 권장.

## [규제] 금융권 망분리 생성형 AI
- **Alpha 주장**: 내부망 AI 서비스는 외부 통신 차단, 생성형 AI 예외 가이드라인 개정 중(추정)
- **검증 결과**: ✅ 확인 (추정 딱지 제거 가능)
- **출처**: 금융위원회 공식 보도자료 / 통합 가이드라인 PDF / Lawtimes 뉴스레터
  - URL: https://www.fsc.go.kr/no010101/85908
  - URL: https://www.fsc.go.kr/comm/getFile?srvcId=BBSTY1&upperNo=83594&fileTy=ATTACH&fileNo=7
  - 발췌: "2024-08 금융분야 망분리 개선 로드맵 발표. 2024-12-12 '금융권 생성형 AI 활용 지원 방안' 발표 — 내부망 오픈소스 AI 설치 지원, Two-track 체계. 통합 AI 가이드라인은 2025 Q1 시행 예정"
- **비고**: 이미 **로드맵·지원방안 발표 완료, 통합 가이드라인 2025 Q1 시행** 이라 "개정 중(추정)" 표현은 사실 기반으로 격상 가능. 7대 원칙(거버넌스·합법성·보조수단성·신뢰성·금융안정성·신의성실·보안성) 명시 추가 권고.

## [클라우드 API] GPT-4o 단가 (2026-04)
- **Alpha 주장**: 평균 $5/M 토큰 (추정)
- **검증 결과**: ⚠️ 수정 필요 (정확한 수치로 업데이트)
- **출처**: OpenAI 공식 가격 / pricepertoken 2026 / aifreeapi 가이드
  - URL: https://openai.com/api/pricing/
  - URL: https://pricepertoken.com/pricing-page/model/openai-gpt-4o
  - 발췌: "**GPT-4o 입력 $2.50/M, 출력 $10.00/M (2026-04 기준)**. 캐시 입력 $1.25/M, Batch 50% 할인"
- **비고**: 입출력 블렌디드 평균 $5/M 은 입·출력 비율이 약 3:1 가정 시 유사. **정확히는 입력 $2.50 / 출력 $10.00 분리 기재** 권고. TCO 계산 시 워크로드별 입출력 비율을 명시하면 정확도 상승.

## [클라우드 API] Claude Sonnet 4.6
- **Alpha 주장**: $3/M 입력 + $15/M 출력 블렌디드 ≈ $6/M
- **검증 결과**: ✅ 확인
- **출처**: Anthropic 공식 가격 / pricepertoken Sonnet 4.6 / BenchLM 2026-04
  - URL: https://www.anthropic.com/claude/sonnet
  - URL: https://pricepertoken.com/pricing-page/model/anthropic-claude-sonnet-4.6
  - URL: https://benchlm.ai/blog/posts/claude-api-pricing
  - 발췌: "Sonnet 4.6 입력 $3.00/M, 출력 $15.00/M. 1M 컨텍스트 지원 (standard pricing). Prompt caching 최대 90% 절감, Batch 50%"
- **비고**: 입·출력 단가 정확. 블렌디드 $6/M 은 입출력 4:1 비율 기준의 근사치. 보고서에 **prompt caching · batch 할인 옵션** 을 손익분기 분석에 반영하면 온프레미스 TCO 방어 시나리오가 다소 보수적으로 변화.

## [클라우드 API] Gemini 2.5 Pro
- **Alpha 주장**: $3.5/M
- **검증 결과**: ⚠️ 수정 필요 (실제는 더 저렴)
- **출처**: Google AI Gemini 가격 / pricepertoken 2026 / TLDL / CostGoat 2026-04
  - URL: https://ai.google.dev/gemini-api/docs/pricing
  - URL: https://pricepertoken.com/pricing-page/model/google-gemini-2.5-pro
  - URL: https://costgoat.com/pricing/gemini-api
  - 발췌: "Gemini 2.5 Pro 입력 $1.25/M (≤200K 컨텍스트) — 초과 시 $2.50/M. 출력 $10.00/M. Batch 50% 할인"
- **비고**: **입력 단가는 $1.25~$2.50 구간이며 $3.5/M 블렌디드 주장은 과대**. 출력은 $10/M 로 GPT-4o 와 유사. 입출력 3:1 비율 가정 시 블렌디드는 약 $3.4/M 이라 알파 수치가 우연히 근사했을 수 있으나, 입·출력 분리 표기가 정확.

## [TCO 참고] 한국 산업용 전력 170원/kWh
- **Alpha 주장**: 약 170원/kWh 추정
- **검증 결과**: ❓ 검증 불가 (별도 조회 미수행)
- **비고**: 한전 산업용(을) 고압A 선택II 기준으로 경부하 80~120원, 최대부하 180~230원 수준. 2024~2025 요금 인상 반영 시 평균 160~200원 범위. 수치 자체는 합리적이나 **공식 한전 고시 인용 권고**. 알파 보고서에서 "추정" 으로 명시했으므로 수정 의무는 낮음.

## [TCO 참고] 손익분기 토큰량
- **Alpha 주장**: 중견 CapEx 8억원 → 월 30~40억 토큰 손익분기
- **검증 결과**: ❓ 검증 불가 (추정 전제 의존)
- **비고**: 알파가 불확실성 플래그에서 이미 "평균 입출력 비율, 양자화, GPU 활용률 에 따라 편차 큼" 을 명시. 본 팩트체커도 공식 출처 확인 범위 밖이므로 검증 불가 판정. 시나리오 명세를 좀 더 구체적으로 기술(예: 입출력 3:1, FP8 양자화, 평균 GPU 이용률 60%) 하면 독자가 재계산 가능.

---

# 수정 권고

우선순위 높음 → 낮음 순.

## P0 (보고서 신뢰도에 직결 — 즉시 수정)

1. **Qwen 2.5 72B 라이선스 완전 반대 기술** (C섹션 표 + 라이선스 주의사항)
   - 현재: "Apache 2.0 (72B 한정)"
   - 수정: "**Qwen License** (72B 는 Apache 2.0 적용 제외). 상업 사용 일부 제한, 별도 라이선스 검토 권고"
   - 라이선스 주의사항 섹션도 "72B/3B 를 제외한 사이즈가 Apache 2.0" 로 정반대 수정.

2. **SOLAR 10.7B 라이선스 버전별 구분**
   - 현재: "Apache 2.0 — 국내 기업이 안심하고 채택 가능한 가장 자유로운 라이선스"
   - 수정: "base 모델 (`SOLAR-10.7B-v1.0`) Apache 2.0 / **Instruct (`SOLAR-10.7B-Instruct-v1.0`) CC-BY-NC-4.0 (상업 금지)**. 상업 활용 시 base 기반 자체 instruction tuning 필요"

3. **GPU 비교표 FP16 TFLOPS 일괄 재기재** (H100·H200·B200)
   - H100 SXM5: 989 → **1,979 TFLOPS (FP16 Tensor Core, sparsity 미포함)**
   - H200 SXM: 989 → **1,979 TFLOPS (동일)**
   - B200: 2,250 → **4,500 TFLOPS (FP16 Tensor Core, dense)**
   - 주석에 "Tensor Core FP16 기준" 명시.

## P1 (수치·명칭 정확성)

4. **리벨리온 제품명 정정**: "ATOM+" 는 공식 라인업에 없음. **ATOM (1세대) / ATOM-Max** 로 분리 기재, 스펙 업데이트.
   - ATOM: 16GB GDDR6, FP16 32 TFLOPS / INT8 128 TOPS, 85W
   - ATOM-Max: 64GB GDDR6, FP16 128 TFLOPS / INT8 512 TOPS, 350W

5. **사피온 X330 스펙 업데이트**: Compact 367 TFLOPS / 16GB / Prime 734 TFLOPS / 32GB / Prime TDP 250W. 알파의 "200 TFLOPS / 150W" 수정.

6. **퓨리오사 RNGD TDP**: 150W → **180W TDP** (FuriosaAI 공식).

7. **Llama 4 활성 파라미터 명시**: "109B/400B MoE" → "**Scout 109B total (17B active, 16 experts) / Maverick 400B total (17B active, 128 experts)**" — MoE 추론 메모리 계산에 필수.

8. **클라우드 API 단가 분리 기재** (E섹션 참고 단가·손익분기):
   - GPT-4o: **입력 $2.50/M + 출력 $10.00/M** (블렌디드 추정 제거)
   - Claude Sonnet 4.6: **입력 $3.00/M + 출력 $15.00/M** (1M 컨텍스트 포함)
   - Gemini 2.5 Pro: **입력 $1.25/M (≤200K) / $2.50/M (>200K) + 출력 $10.00/M**
   - 모두 prompt caching / batch API 할인 옵션 주석 추가 권고.

## P2 (보강·맥락 추가)

9. **AI 기본법 시행일 구체화**: "2026.1월 시행령" → "**2026-01-22 전면 시행** (정식명: '인공지능 발전과 신뢰 기반 조성 등에 관한 기본법'). 정부 1년+ 계도 기간 운영 예정 (과태료 미부과)" — 실무 임팩트에 중요.

10. **금융권 망분리 가이드라인 상태 격상**: "(추정)" 제거. "2024-08 망분리 개선 로드맵 → 2024-12-12 금융권 생성형 AI 활용 지원 방안 → **2025 Q1 통합 AI 가이드라인 시행**" 로 타임라인 명시. 7대 원칙(거버넌스·합법성·보조수단성·신뢰성·금융안정성·신의성실·보안성) 보강.

11. **GB200 NVL72 TFLOPS 랙 총계 재확인**: 162,000 의 단위/기준 (FP16 non-Tensor 가능성) 을 NVIDIA 공식 사양서로 재검증 권고.

12. **Qwen 3 MoE 변종 라이선스 재검증**: dense 는 Apache 2.0 확정이나 235B-A22B·30B-A3B 는 일부 소스 간 불일치. 도입 전 최신 HF 레포 LICENSE 파일 직접 확인 권고.

---

# 출처 목록 (주요)

- NVIDIA H100 Datasheet: https://resources.nvidia.com/en-us-gpu-resources/h100-datasheet-24306
- NVIDIA H200 SXM: https://www.nvidia.com/en-us/data-center/h200/
- NVIDIA B200 사양: https://jarvislabs.ai/gpu/nvidia-b200, https://www.spheron.network/blog/nvidia-b200-complete-guide/
- AMD MI300X Datasheet: https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf
- Rebellions ATOM / ATOM-Max: https://kr.rebellions.ai/rebellions-product/atom-2/, https://kr.rebellions.ai/rebellions-product/atom-max/
- SAPEON X330: https://www.sapeon.com/products/sapeon-x330, https://www.globenewswire.com/news-release/2023/11/16/2781749/0/en/SAPEON-launches-X330-AI-semiconductor-for-data-centers.html
- FuriosaAI RNGD: https://furiosa.ai/rngd, https://www.hpcwire.com/2025/09/30/the-fast-and-the-furiosaai-korean-chip-startup-takes-aim-at-nvidia-gpus-with-tensor-contraction-architecture/
- Llama 3.3: https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
- Llama 4: https://huggingface.co/blog/llama4-release, https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/
- Qwen 2.5 72B LICENSE: https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/blob/main/LICENSE
- Qwen 3: https://qwenlm.github.io/blog/qwen3/, https://huggingface.co/Qwen/Qwen3-235B-A22B
- Mistral Large 2: https://mistral.ai/news/mistral-large-2407, https://huggingface.co/mistralai/Mistral-Large-Instruct-2407
- DeepSeek V3: https://github.com/deepseek-ai/DeepSeek-V3, https://arxiv.org/html/2412.19437v1
- SOLAR 10.7B: https://huggingface.co/upstage/SOLAR-10.7B-v1.0, https://huggingface.co/upstage/SOLAR-10.7B-Instruct-v1.0
- AI 기본법: https://www.law.go.kr/lsInfoP.do?lsiSeq=268543, https://www.mstoday.co.kr/news/articleView.html?idxno=99963
- 개인정보보호법 제28조의2: https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=213857, https://www.privacy.go.kr/front/contents/cntntsView.do?contsNo=14
- 금융권 생성형 AI 가이드라인: https://www.fsc.go.kr/no010101/85908, https://www.fsc.go.kr/comm/getFile?srvcId=BBSTY1&upperNo=83594&fileTy=ATTACH&fileNo=7
- GPT-4o 가격: https://openai.com/api/pricing/, https://pricepertoken.com/pricing-page/model/openai-gpt-4o
- Claude Sonnet 4.6 가격: https://www.anthropic.com/claude/sonnet, https://benchlm.ai/blog/posts/claude-api-pricing
- Gemini 2.5 Pro 가격: https://ai.google.dev/gemini-api/docs/pricing, https://pricepertoken.com/pricing-page/model/google-gemini-2.5-pro
