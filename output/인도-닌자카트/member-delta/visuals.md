---
Creator: member-delta
Created: 2026-04-24
Version: 1.0
---

# 시각자료: 인도 닌자카트 분석

## 시각자료 개요

본 문서는 `member-alpha/analysis-report.md`의 분석 결과를 기반으로 아래 시각자료를 제공합니다:

1. **닌자카트 비즈니스 모델 공급망 구조도** (Mermaid flowchart)
2. **투자 라운드 타임라인** (Mermaid timeline)
3. **인도 애그리테크 경쟁사 비교 테이블**
4. **운영 규모 핵심 수치 테이블**
5. **닌자카트 vs. 전통 유통 구조 비교도** (Mermaid flowchart)

---

## Mermaid 다이어그램

### 다이어그램 1: 닌자카트 B2B 공급망 구조도

*닌자카트가 전통 유통 다단계를 단축하는 핵심 흐름을 나타낸 구조도*

```mermaid
flowchart LR
    subgraph 공급측["공급측 (농가)"]
        F1["🌾 농가 A\n(벵갈루루 근교)"]
        F2["🌾 농가 B\n(첸나이 근교)"]
        F3["🌾 농가 C\n(푸네 근교)"]
    end

    subgraph 닌자카트["닌자카트 플랫폼"]
        APP["📱 닌자카트 앱\n(수요 예측 & 주문 매칭)"]
        CC["🏭 집하 센터\n(Collection Centre)\n품질 선별·등급화"]
        LOG["🚚 물류 네트워크\n(당일/익일 새벽 배송)"]
    end

    subgraph 구매측["구매측 (소매상·기업)"]
        R1["🏪 독립 소매상"]
        R2["🏬 현대식 소매(MT)"]
        R3["🍽️ 식품기업·HoReCa"]
    end

    F1 -->|수매/위탁| CC
    F2 -->|수매/위탁| CC
    F3 -->|수매/위탁| CC
    APP -->|수요·재고 실시간 매칭| CC
    CC -->|선별 완료 물량| LOG
    LOG -->|새벽 배송| R1
    LOG -->|새벽 배송| R2
    LOG -->|새벽 배송| R3

    style 닌자카트 fill:#fff3cd,stroke:#ffc107
    style 공급측 fill:#d4edda,stroke:#28a745
    style 구매측 fill:#cce5ff,stroke:#0066cc
```

---

### 다이어그램 2: 전통 유통 구조 vs. 닌자카트 비교

*중간상 단계 수와 마진 손실 비교*

```mermaid
flowchart TD
    subgraph 전통["❌ 전통 유통 구조 (5~7단계)"]
        TF["농가"] --> TA1["마을 아르티\n(Village Arathi)"]
        TA1 --> TA2["APMC 도매상"]
        TA2 --> TA3["2차 도매상"]
        TA3 --> TA4["지역 유통업자"]
        TA4 --> TR["소매상"]
        TR --> TC["소비자"]
    end

    subgraph 닌자["✅ 닌자카트 구조 (2~3단계)"]
        NF["농가"] --> NP["닌자카트 플랫폼\n(집하·품질·물류)"]
        NP --> NR["소매상"]
        NR --> NC["소비자"]
    end

    style 전통 fill:#f8d7da,stroke:#dc3545
    style 닌자 fill:#d4edda,stroke:#28a745
```

---

### 다이어그램 3: 투자 라운드 타임라인

*2015년 창업 이후 주요 투자 이벤트*

```mermaid
timeline
    title 닌자카트 투자 타임라인
    2015 : Seed 라운드
         : Accel, Saha Fund 참여
    2016 : Series A ($3M)
         : Qualcomm Ventures 참여
    2017 : Series B ($7M)
         : Tiger Global 첫 참여
    2018 : Series C ($100M)
         : Tiger Global 리드
    2019 : Walmart 전략적 투자 ($30M)
         : Walmart, 주요 주주로 부상
    2020-2021 : Series D (~$145M)
              : Walmart, Tiger Global 후속 참여
    2022 : 누적 조달액 $350M+ 달성
```

---

## 핵심 수치 테이블

### 테이블 1: 닌자카트 운영 규모 (2022~2023년 기준)

| 지표 | 수치 | 비고 |
|---|---|---|
| 연결 농가 수 | 약 150,000명 이상 | 2021~2022년 기준 |
| 등록 소매상 수 | 약 90,000~100,000개 | 보도 시점별 범위 |
| 일 처리 물량 | 최대 약 1,400톤 | 피크 기준 보고됨 |
| 운영 도시 수 | 약 25개 이상 | 대도시 + 2선 도시 |
| 직원 수 | 약 4,000명 내외 | 시점에 따라 변동 |
| 누적 투자 유치액 | $350M 이상 | 2022년 기준 |

---

### 테이블 2: 인도 주요 애그리테크 경쟁사 비교

| 기업 | 설립 | 주요 모델 | 커버리지 | 주요 투자자 | 차별점 |
|---|---|---|---|---|---|
| **Ninjacart** | 2015 | B2B 신선 농산물 공급망 | 전국 25개+ 도시 | Walmart, Tiger Global | 물류 일체형, Walmart 파트너십 |
| **WayCool Foods** | 2015 | B2B 신선+가공 식품 | 남인도 중심 | Lightbox, Chiratae Ventures | 자체 브랜드·가공 제품 추가 |
| **DeHaat** | 2012 | 농자재+구매+금융 통합 | 비하르·UP 중심 | SoftBank, Prosus | 농업 전 가치사슬(Full-stack) |
| **Agribazaar** | 2016 | B2B 온라인 거래 플랫폼 | 전국 | 국내 펀드 | 디지털 거래 특화, 물류 미포함 |
| **BigBasket B2B** | 2011 | B2B/B2C 하이브리드 | 전국 | Tata Group | 소비자 브랜드 인지도, Tata 지원 |

---

### 테이블 3: 전통 유통 vs. 닌자카트 - 핵심 지표 비교

| 지표 | 전통 유통 구조 | 닌자카트 플랫폼 |
|---|---|---|
| 유통 단계 수 | 5~7단계 | 2~3단계 |
| 농가 수취가 비율 | 소비자가의 20~30% | 소비자가의 45~55% 수준 (추정) |
| 신선 농산물 폐기율 | 30~40% | 약 20% 이하 (추정, 업계 대비 개선) |
| 농산물 소비자 도달 시간 | 2~5일 | 당일~익일 |
| 가격 투명성 | 낮음 | 높음 (앱 기반 실시간 가격) |
