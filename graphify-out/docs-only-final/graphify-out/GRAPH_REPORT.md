# Graph Report - .  (2026-08-10)

## Corpus Check
- 663 files · ~590,182 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 949 nodes · 1980 edges · 54 communities (48 shown, 6 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 211 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- claude framework core
- output 현장 지역담당자 영업활동
- output market intelligence report
- jeonsasonik
- output erp sonik bunseokhaeseo
- output 방식 영어 퀴즈
- output 이번 전사 경영
- output 2026 배달 시장
- patch
- ax
- baro
- output 소화물 인증 등록제
- youtube
- archive
- output 회의 녹음 텍스트
- output on premise ai
- ax
- member
- ax
- youtube
- output slack self healing
- erp
- output 3d fps 게임
- slack
- concept
- output 전남 광주 지역
- output ax management system
- hrflow
- output gpu 지원 받는
- output ax ax member
- 4륜
- output jeonnam gwangju ai
- output 마켓 대시보드에서 이번주
- output 배달시장 ms member
- output 3개월 시장 동향
- meeting
- output 광주전남 농축수산물 폐기율
- ai
- ax
- output agent team eval
- meeting
- output 도심물류 os member
- output ai 기업 gpu
- ax
- tetris
- ax
- meeting
- output github researcher final
- n8n
- toast
- eu
- graphify
- output gwangju jeonnam nongchuksusanmul
- 배달대행사

## God Nodes (most connected - your core abstractions)
1. `member-alpha (조사) AGENT.md` - 26 edges
2. `member-alpha (조사)` - 22 edges
3. `member-beta (보고서)` - 22 edges
4. `member-gamma (팩트체크)` - 22 edges
5. `Team Lead Agent (CLAUDE.md)` - 21 edges
6. `member-delta (시각화)` - 20 edges
7. `인수인계_현행_2026-06-14.md (정본 인수인계)` - 20 edges
8. `member-beta (보고서) AGENT.md` - 19 edges
9. `Agent Team Framework README` - 17 edges
10. `On-Premise AI - Analysis Report (member-alpha)` - 17 edges

## Surprising Connections (you probably didn't know these)
- `민감정보 자동 마스킹 및 대화 감사 정책 (회사 보안 정책, 개인 비활성화 불가)` --semantically_similar_to--> `HR 데이터 민감도에 따른 '1단계 보안 최소화 원칙 미적용' 결정`  [INFERRED] [semantically similar]
  baro-agent/ui/settings.html → hrflow/hrflow_design.md
- `BARO AGENT 워크플로우(예약 자동화) 화면` --semantically_similar_to--> `onboarding-orchestrator 서브에이전트 (온보딩·오프보딩 체크리스트 자동화)`  [INFERRED] [semantically similar]
  baro-agent/ui/workflow.html → hrflow/hrflow_design.md
- `채널 우선 표본조사 (Channel-First Panel Sampling)` --semantically_similar_to--> `yt-search Skill (yt-dlp keyword search)`  [INFERRED] [semantically similar]
  youtube-ai-trend-agent/memory/channel-first-collection.md → youtube-intelligence-agent/skills/yt-search/SKILL.md
- `intelligence-analyst (existing agent project)` --semantically_similar_to--> `member-alpha (조사) AGENT.md`  [INFERRED] [semantically similar]
  C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/agent-team-framework-design.md → C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/.claude/agents/member-alpha(조사)/AGENT.md
- `resource-analyst (existing agent project)` --semantically_similar_to--> `member-alpha (조사) AGENT.md`  [INFERRED] [semantically similar]
  C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/agent-team-framework-design.md → C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/.claude/agents/member-alpha(조사)/AGENT.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Member AGENT.md Template Structure Pattern (Assignment/Execution/Revision/Skills/Constraints)** — claude_agents_member_template_agent, claude_agents_member_alpha_research_agent, claude_agents_member_beta_report_agent, claude_agents_member_delta_viz_agent, claude_agents_member_gamma_factcheck_agent [INFERRED 0.75]
- **Pre-Research-Then-Synthesize Pipeline Pattern (specialist researcher runs before generalist analyst)** — claude_agents_member_eta_oss_research_agent, claude_agents_member_theta_policy_research_agent, claude_agents_member_gamma_factcheck_agent, claude_agents_member_iota_pr_monitoring_agent, claude_agents_member_alpha_research_agent [INFERRED 0.85]
- **Deterministic Quality Gate Pattern (Phase 3/4 validation + isolated review)** — claude_phase_3, claude_phase_4, validate_artifact_py, review_artifact_py, claude_agents_member_reviewer_review_agent [INFERRED 0.85]
- **gamma→alpha→delta→beta 데이터 인용 계보 (2026 배달 시장 점유율 분석)** — archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_gamma_fact_check_log, archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_alpha_analysis_report, archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_delta_visuals, archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_beta_draft_report [EXTRACTED 1.00]
- **배달 시장 점유율 분석 — Phase 3 REASSIGN→재실행→APPROVE 리뷰 사이클** — archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_alpha_analysis_report, archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_beta_draft_report, archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_member_delta_visuals, archive_2026_07_29_cleanup_slack_bridge_output_2026_배달_시장_점유율_분석해줘_review_log [EXTRACTED 1.00]
- **research-report 4단계 실행 파이프라인 (gamma→alpha→delta→beta, 2026 배달 시장 분석)** — output_2026_배달_시장_분석해줘_member_gamma_fact_check_log, output_2026_배달_시장_분석해줘_member_alpha_analysis_report, output_2026_배달_시장_분석해줘_member_delta_visuals, output_2026_배달_시장_분석해줘_member_beta_draft_report [EXTRACTED 1.00]
- **research-report 4단계 실행 파이프라인 (gamma→alpha→delta→beta, 점유율 분석, 재사용 데이터 기반)** — output_2026_배달_시장_점유율_분석해줘_member_gamma_fact_check_log, output_2026_배달_시장_점유율_분석해줘_member_alpha_analysis_report, output_2026_배달_시장_점유율_분석해줘_member_delta_visuals, output_2026_배달_시장_점유율_분석해줘_member_beta_draft_report [EXTRACTED 1.00]
- **2026 세제개편안 부가가치세 리서치 사이클 (gamma→alpha→delta→beta→최종본)** — output_2026_세제개편안_부가가치세_member_gamma_fact_check_log, output_2026_세제개편안_부가가치세_member_alpha_analysis_report, output_2026_세제개편안_부가가치세_member_delta_visuals, output_2026_세제개편안_부가가치세_member_beta_draft_report, output_2026_세제개편안_부가가치세_final_final_artifact [INFERRED 0.85]
- **3D FPS 개발 파이프라인 (eta→alpha→epsilon→최종본, dev 타입 선행 규칙)** — output_3d_fps_게임_개발_member_eta_github_research_report, output_3d_fps_게임_개발_member_alpha_analysis_report, output_3d_fps_게임_개발_member_epsilon_dev_log, output_3d_fps_게임_개발_final_final_artifact [EXTRACTED 1.00]
- **3개월 시장 동향 분석 AUTO 모드 사이클 (plan→alpha→review→최종본→retrospective)** — output_3개월_시장_동향_분석해서_바로고_plan, output_3개월_시장_동향_분석해서_바로고_member_alpha_analysis_report, output_3개월_시장_동향_분석해서_바로고_review_log, output_3개월_시장_동향_분석해서_바로고_final_final_artifact, output_3개월_시장_동향_분석해서_바로고_retrospective [INFERRED 0.85]
- **3개월 시장 동향 리서치 사이클 (beta·gamma·delta·reviewer 협업)** — ws_3gaewol_sijang_donghyang, member_beta, member_gamma, member_delta, member_reviewer [EXTRACTED 1.00]
- **github-plan 타입 선행 파이프라인 (eta→alpha→beta)** — member_eta, member_alpha, member_beta, concept_github_plan_task_type [EXTRACTED 1.00]
- **AX 거버넌스 엔진을 구성하는 4대 도메인 메커니즘** — concept_ri_metric, concept_ai_adoption_4_stages, concept_maker_checker_approval, concept_value_chain_swimlane [EXTRACTED 1.00]
- **인증 신뢰 사슬 단일 실패점 (DEV_AUTH 백도어 + 자기승인 + ax-management-system)** — concept_dev_auth_backdoor, concept_self_approval_f4, ax_management_system [INFERRED 0.85]
- **AX 관리 시스템 6인 평가 사이클 (eta·alpha·gamma·zeta·delta·beta)** — member_eta, member_alpha, member_gamma, member_zeta, member_delta, member_beta [EXTRACTED 1.00]
- **AX 대시보드 전사 현황 리서치 사이클 (alpha·gamma·delta·beta + AX 대시보드)** — member_alpha, member_gamma, member_delta, member_beta, ax_dashboard [EXTRACTED 1.00]
- **BARO AGENT eval production/review pipeline (alpha→gamma/delta→beta→final)** — output_barogo_agent_eval_member_alpha_analysis_report, output_barogo_agent_eval_member_gamma_fact_check_log, output_barogo_agent_eval_member_delta_visuals, output_barogo_agent_eval_member_beta_draft_report, output_barogo_agent_eval_final_final_artifact [EXTRACTED 1.00]
- **ERP 손익 분석 워크스페이스 생산/리뷰 사이클 (alpha→gamma/delta→beta→final)** — output_erp_sonik_bunseokhaeseo_allyeojwo_member_alpha_analysis_report, output_erp_sonik_bunseokhaeseo_allyeojwo_member_gamma_fact_check_log, output_erp_sonik_bunseokhaeseo_allyeojwo_member_delta_visuals, output_erp_sonik_bunseokhaeseo_allyeojwo_member_beta_draft_report, output_erp_sonik_bunseokhaeseo_allyeojwo_final_final_artifact [EXTRACTED 1.00]
- **member-eta(GitHub Researcher) 신규 멤버 프레임워크 반영** — claude_member_zeta, claude_member_alpha, claude_agents_member_eta_agent, claude_skills_github_researcher_skill, output_github_researcher_team_config_patch [EXTRACTED 1.00]
- **GPU 지원 받는 방법 — 4멤버 순차 리서치 파이프라인** — output_gpu_지원_받는_방법_member_alpha_analysis_report, output_gpu_지원_받는_방법_member_gamma_fact_check_log, output_gpu_지원_받는_방법_member_delta_visuals, output_gpu_지원_받는_방법_member_beta_draft_report [EXTRACTED 1.00]
- **중앙펀드 × 전남인프라 × 광주실증 3축 연동 구조** — output_jeonnam_gwangju_ai_national_growth_fund_final_final_artifact_국민성장펀드, output_jeonnam_gwangju_ai_national_growth_fund_final_final_artifact_해남_국가ai컴퓨팅센터, output_jeonnam_gwangju_ai_national_growth_fund_final_final_artifact_광주_ax_실증밸리 [EXTRACTED 1.00]
- **On-Premise AI research-report 팀 사이클 (alpha 분석 → gamma 검증 → beta 종합 → delta 시각화)** — output_on_premise_ai_member_alpha_analysis_report, output_on_premise_ai_member_gamma_fact_check_log, output_on_premise_ai_member_beta_draft_report, output_on_premise_ai_member_delta_visuals [EXTRACTED 1.00]
- **session-validation code-review 검증 사이클 (alpha 코드 스캔 → gamma 환경 검증 → beta 요약 → final)** — output_session_validation_member_alpha_analysis_report, output_session_validation_member_gamma_fact_check_log, output_session_validation_member_beta_draft_report, output_session_validation_final_final_artifact [EXTRACTED 1.00]
- **Slack Self-Healing Pipeline 5개 패치 세트 (queue_server/CLAUDE.md/deploy-heal/epsilon-agent/team-config)** — patch_01_queue_server, patch_02_claude_md_auto, patch_03_deploy_heal_skill, patch_04_epsilon_agent, patch_05_team_config_auto [EXTRACTED 1.00]
- **광주전남 농축수산물 폐기율 리서치 협업 파이프라인** — member_alpha, member_gamma, member_delta, member_beta, output_광주전남_농축수산물_폐기율_final_final_artifact [EXTRACTED 1.00]
- **AUTO 모드 대시보드 사용 -> 고위험 승인 오버라이드 흐름** — scripts_dashboard_fetch, market_dashboard_api, high_risk_dashboard_override_rule, output_마켓_대시보드에서_이번주_인사이트_요약해줘_plan [EXTRACTED 1.00]
- **W32 마켓 인텔리전스 분석 파이프라인 (gamma→alpha→delta→beta→통합)** — w32_report_market_intel, output_market_intelligence_report_member_gamma_fact_check_log, output_market_intelligence_report_member_alpha_analysis_report, output_market_intelligence_report_member_delta_visuals, output_market_intelligence_report_member_beta_draft_report, output_market_intelligence_report_final_final_artifact [EXTRACTED 1.00]
- **메이트완 리포트 팩트체크 수정 전파 파이프라인 (alpha 원안→gamma 수정→delta/beta/최종 반영)** — output_matewan_local_commerce_member_alpha_analysis_report, output_matewan_local_commerce_member_gamma_fact_check_log, output_matewan_local_commerce_member_delta_visuals, output_matewan_local_commerce_member_beta_draft_report, output_matewan_local_commerce_final_final_artifact [EXTRACTED 1.00]
- **바로고 정책 모니터링 채널 분류·우선순위 산출 흐름 (gamma 수집 → alpha 분석 → delta 시각화 → beta 보고서)** — output_바로고가_정부_정책_기관_대응하기_member_gamma_fact_check_log, output_바로고가_정부_정책_기관_대응하기_member_alpha_analysis_report_ws, output_바로고가_정부_정책_기관_대응하기_member_delta_visuals, output_바로고가_정부_정책_기관_대응하기_member_beta_draft_report [EXTRACTED 0.90]
- **영어 퀴즈 게임 dev 파이프라인 (eta OSS 리서치 → alpha 구현전략 → epsilon 코드 개발/검증)** — output_방식_영어_퀴즈_게임_개발_member_eta_github_research_report, output_방식_영어_퀴즈_게임_개발_member_alpha_analysis_report_game, output_방식_영어_퀴즈_게임_개발_member_epsilon_dev_log, output_방식_영어_퀴즈_게임_개발_game_index_html [EXTRACTED 0.90]
- **배달대행사 PG사 이슈 리서치 협업 파이프라인 (alpha→gamma→delta→beta)** — output_배달대행사_pg사_이슈_member_alpha_analysis_report, output_배달대행사_pg사_이슈_member_gamma_fact_check_log, output_배달대행사_pg사_이슈_member_delta_visuals, output_배달대행사_pg사_이슈_member_beta_draft_report [INFERRED 0.85]
- **소화물배송대행서비스 제도 이원화 — 현행 인증제·등록제 전환 법안·근거법** — output_소화물_인증_등록제_final_final_artifact_인증제, output_소화물_인증_등록제_final_final_artifact_등록제_전환_법안, output_소화물_인증_등록제_final_final_artifact_생활물류서비스산업발전법 [EXTRACTED 0.90]
- **바로고 현장실적·업계동향 리서치 파이프라인 (gamma→alpha→delta→beta→final)** — output_이번_바로고_현장_배송_실적이랑_member_gamma_fact_check_log, output_이번_바로고_현장_배송_실적이랑_member_alpha_analysis_report, output_이번_바로고_현장_배송_실적이랑_member_delta_visuals, output_이번_바로고_현장_배송_실적이랑_member_beta_draft_report, output_이번_바로고_현장_배송_실적이랑_final_final_artifact [EXTRACTED 1.00]
- **바로고 마켓 인텔리전스 W32 데이터의 워크스페이스 간 교차 재사용 (실적 워크스페이스 ↔ 손익 워크스페이스)** — output_이번_바로고_현장_배송_실적이랑_member_gamma_fact_check_log, output_이번_전사_경영_실적_손익_market_주간_리포트_w32, output_마켓_대시보드에서_이번주_인사이트_요약해줘_final_final_artifact [INFERRED 0.85]
- **사내 대시보드 소스 + 해석 한계(캐비엇) 명시 패턴** — output_이번_전사_경영_실적_손익_member_delta_visuals, output_현장_지역담당자_영업_활동_현황_plan, output_현장_지역담당자_영업_활동_현황_final_final_artifact [INFERRED 0.75]
- **ERP 대시보드 사용 → human_approval override → Notion 예외 실행 흐름** — output_이번_전사_경영_실적_손익_erp_대시보드, output_이번_전사_경영_실적_손익_human_approval_override, output_이번_전사_경영_실적_손익_notion_예외_정책_변경, output_이번_전사_경영_실적_손익_final_final_artifact [EXTRACTED 1.00]
- **research-report 4단계 파이프라인 패턴 (alpha 조사 → gamma/delta 검증·시각화 → beta 보고서)** — output_인도_닌자카트_plan, output_전남_광주_지역_기반의_ai_plan, output_현장_지역담당자_영업_활동_현황_plan [INFERRED 0.85]
- **Phase 3-1 REASSIGN -> 재작성 -> APPROVE 리뷰 사이클 (member-beta)** — output_현장_지역담당자_영업활동_분석해줘_member_beta_draft_report, output_현장_지역담당자_영업활동_분석해줘_member_beta_review_verdict, output_현장_지역담당자_영업활동_분석해줘_member_beta_review_verdict_2 [EXTRACTED 1.00]
- **회의록 앱 프론트엔드 정적 자산 (index.html + style.css + app.js)** — output_회의_녹음_텍스트_변환을_회의록_final_meeting_minutes_app_app_static_index, output_회의_녹음_텍스트_변환을_회의록_app_static_style, output_회의_녹음_텍스트_변환을_회의록_app_static_app [EXTRACTED 1.00]
- **회의록 앱 STT→LLM 처리 파이프라인 (main→routers→services)** — output_회의_녹음_텍스트_변환을_회의록_app_main, output_회의_녹음_텍스트_변환을_회의록_app_routers_transcribe, output_회의_녹음_텍스트_변환을_회의록_app_services_whisper_service, output_회의_녹음_텍스트_변환을_회의록_app_routers_minutes, output_회의_녹음_텍스트_변환을_회의록_app_services_claude_service [INFERRED 0.85]
- **dev task type 실행 파이프라인 (alpha 분석 -> epsilon 구현)** — claude_member_alpha, claude_member_epsilon, output_회의_녹음_텍스트_변환을_회의록 [EXTRACTED 1.00]
- **Slack Bridge 팀장 에이전트 호출 흐름 (app.py→agent_runner→state/slug)** — slack_bridge_app, slack_bridge_agent_runner, slack_bridge_state, slack_bridge_slug [INFERRED 0.85]
- **파일 기반 오케스트레이터-서브에이전트 패턴 (3개 프로젝트 공통)** — 4륜_정산_시스템_claude_오케스트레이터, ai_media_agent_claude_오케스트레이터, ax_analysis_agent_ai_analysis_agent_claude_오케스트레이터 [INFERRED 0.85]
- **Redash 기반 보고/집계 자동화 공통 패턴** — ax_management_system_valuechain_brand_logistics_ops_team, ax_management_system_valuechain_finance_accounting_team, ax_management_system_valuechain_channel_business_team, ax_management_system_valuechain_integrated_ops_team, tool_redash [INFERRED 0.75]
- **이싸인온 기반 계약서 자동화 공통 패턴** — ax_management_system_valuechain_channel_business_team, ax_management_system_valuechain_connect_ops_team, ax_management_system_valuechain_integrated_ops_team, tool_esignon [INFERRED 0.75]
- **AX 관리 시스템 종합 평가 산출물군 (평가 및 개선 폴더)** — ax_management_system_eval_final_artifact_report, ax_management_system_uibench_report [EXTRACTED 0.85]
- **BARO AGENT 사내 AD 로그인 관련 문서군** — baro_agent_ad_auth_doc, baro_agent_readme_ldap_auth, baro_agent_guide_ad_login_section, baro_agent_progress_v07_ad_login [INFERRED 0.85]
- **BARO AGENT 지식 보관소(vault) 계획→구현 계보** — baro_agent_plan_vault_doc, baro_agent_plan_v03_doc, baro_agent_readme_vault, baro_agent_progress_doc [INFERRED 0.85]
- **BARO AGENT 데스크톱 AI 에이전트 플랫폼 (채팅 + 워크플로우 + 설정 통합)** — baro_agent_ui_index_chat_ui, baro_agent_ui_settings_settings_screen, baro_agent_ui_workflow_workflow_screen [INFERRED 0.80]
- **DEBTFLOW → HRFLOW 기술 스택·UX 패턴 계승 라인** — debtflow_v2_debtflow_readme_deployment_guide, debtflow_v2_debtflow_앱_메뉴_구성_menu_spec, hrflow_hrflow_design_master [INFERRED 0.90]
- **YouTube AI Trend Pipeline (S1-S6 Orchestration)** — youtube_ai_trend_agent_claude_orchestrator, youtube_ai_trend_agent__claude_skills_youtube_collector_skill_youtube_collector, youtube_ai_trend_agent__claude_skills_video_classifier_skill_video_classifier, youtube_ai_trend_agent__claude_skills_week_aggregator_skill_week_aggregator, youtube_ai_trend_agent__claude_skills_report_builder_skill_report_builder [EXTRACTED 1.00]
- **n8n Self-host Documentation Set (Infra + LLM Design + User Guide)** — n8n_selfhost_n8n_selfhost_guide_selfhost_guide, n8n_selfhost_n8n_llm_llm_workflow_design_guide, n8n_selfhost_n8n_user_guide_md [INFERRED 0.85]
- **Standardized Korean Educational Video Report Template** — youtube_intelligence_agent_agents, youtube_intelligence_agent_output_5kj_cuwmcny_report, youtube_intelligence_agent_output_gkxuctqgl5e_report, youtube_intelligence_agent_output_niwcnd7qp3c_report, youtube_intelligence_agent_output_qajivleoeqi_report, youtube_intelligence_agent_output_프로젝트_자료_jopf8yre1t8_report, youtube_intelligence_agent_output_프로젝트_자료__rgy8nliqcs_report, youtube_intelligence_agent_output_프로젝트_자료_jywddt_3l8q_report, youtube_intelligence_agent_output_프로젝트_자료_k_t4mrheqxw_report, youtube_intelligence_agent_output_프로젝트_자료_vsw3osvbsm0_report, youtube_intelligence_agent_output_프로젝트_자료_wutrtrndbly_report [EXTRACTED 0.95]
- **Reused 2026 AI-workforce benchmark/glossary content across episodes (E2B/E4B scores, 독파모/AXK1)** — youtube_intelligence_agent_output_5kj_cuwmcny_report, youtube_intelligence_agent_output_niwcnd7qp3c_report, youtube_intelligence_agent_output_프로젝트_자료_jopf8yre1t8_report, youtube_intelligence_agent_output_프로젝트_자료_k_t4mrheqxw_report [INFERRED 0.75]
- **확정월+라이브월 하이브리드 PL 모델 구현** — jeonsasonik_erp_concept_confirmed_live_month_model, jeonsasonik_erp_apply_june_engine, jeonsasonik_erp_load_confirmed_month_py, jeonsasonik_erp_erp_db [EXTRACTED 0.95]
- **회사서버 배포·상시구동 파이프라인** — jeonsasonik_erp_server_sync_script, jeonsasonik_erp_serve_erp_py, jeonsasonik_erp_erp_db, jeonsasonik_erp_server_work_guide_claude [EXTRACTED 0.90]
- **AD 로그인 첫 배포 장애 대응 사건** — jeonsasonik_erp_2026_08_10_ad_incident, jeonsasonik_erp_ad_login_feature, jeonsasonik_erp_serve_erp_py, jeonsasonik_erp_requirements [EXTRACTED 0.90]
- **사업계획 목표-실적 관리 흐름 (목표입력 → 실적입력 → 목표vs실적 비교)** — erp_frontend_plan_edit_page, erp_frontend_plan_actual_edit_page, erp_frontend_plan_page, erp_frontend_plan_api_plan [INFERRED 0.90]
- **ERP 계정 인증·접근 관리 (AD 로그인 + 화이트리스트 등록)** — erp_frontend_login_page, erp_frontend_login_auth_login_api, erp_frontend_settings_page, erp_frontend_settings_ad_user_management [INFERRED 0.85]

## Communities (54 total, 6 thin omitted)

### Community 0 - "claude framework core"
Cohesion: 0.07
Nodes (88): Agent Team Framework 설계서 v1.3, ADR-1: Team-Lead-Mediated vs Free-form Collaboration, ADR-2: Config-driven vs Template-based Team Composition, ADR-3: Modification-Scale-Based Direct-Edit vs Reassign Branching, ai-solution-designer (existing agent project), intelligence-analyst (existing agent project), Original 5-Phase Workflow (PLAN-EXECUTE-REVIEW-INTEGRATE-DISTRIBUTE), report-dispatcher (existing agent project) (+80 more)

### Community 1 - "output 현장 지역담당자 영업활동"
Cohesion: 0.08
Nodes (60): .claude/agents/member-eta/AGENT.md, 현장 종합 대시보드 API (crm.ax.barogo.io), member-alpha (조사), member-beta (보고서), member-delta (시각화), member-eta (OSS리서치), member-gamma (팩트체크), member-zeta (설계) (+52 more)

### Community 2 - "output market intelligence report"
Cohesion: 0.13
Nodes (44): 배달의민족 (우아한형제들), 바로고 (Barogo), Barogo Intelligence Dashboard (market 대시보드), 쿠팡이츠 (쿠팡이츠서비스 유한), 고위험(사내 대시보드 데이터 사용) human_approval override 규칙, 바로고 정부 정책·기관 대응 모니터링 채널 체계 (우선 8 / 보조 3), 마켓 인텔리전스 키워드 레지스트리 (api/keywords), 메이트완 (Matewan) (+36 more)

### Community 3 - "jeonsasonik"
Cohesion: 0.14
Nodes (35): 2026-08-10 AD 로그인 배포 중 서버 전체 장애 사고, AD(LDAP) 로그인 + 사전등록 허용목록 기반 접근제어, apply_june.py (라이브월 PL 계산 엔진), HANDOVER.md (폐기, 예전 일별운영 ERP 설계), plan.md (폐기, 초기 계획서), b2b_월예상 테이블 (당월 B2B·로드샵 월말 예상), backend/routers/board.py (API 본체), _build_plan_targets.py (사업계획 목표 ETL) (+27 more)

### Community 4 - "output erp sonik bunseokhaeseo"
Cohesion: 0.13
Nodes (35): research-report task type, @anthropic-ai/sdk ^0.32.1 버전 낙후, BARO AGENT v0.3.0 (Electron AI 비서 앱), Claude 모델 ID 오류/레거시 이슈 (claude-opus-4-5 등), Electron 32 EOL 위험, BARO AGENT v0.3.0 종합 평가 보고서 (Final Artifact), @google/generative-ai EOL → @google/genai 마이그레이션 필요, GPT-5/GPT-5-mini 모델 ID 미존재 (+27 more)

### Community 5 - "output 방식 영어 퀴즈"
Cohesion: 0.11
Nodes (34): sanidhyy/duolingo-clone (GitHub, MIT, 552★), RickCarlino/KoalaCards (GitHub, MIT, 48★), cosmoart/quiz-game (Quizi, GitHub, MIT, 90★), VienDinhCom/supermemo (GitHub, MIT, 336★), subconcept-labs/ulangi (GitHub, GPL-3.0, 457★), baturyilmaz/wordpecker-app (GitHub, MIT, 2103★), GPL-3.0 라이선스 리스크 (ulangi, 코드 복사 금지), 고객확인(KYC)·가상계좌 통제 병목 리스크 (+26 more)

### Community 6 - "output 이번 전사 경영"
Cohesion: 0.13
Nodes (34): AUTO 실행 로그 (이번 바로고 현장 배송 실적이랑), 최종 산출물: 이번 바로고 현장 배송 실적과 최근 업계 동향, 현장 실적·업계 동향 분석 보고서 (member-alpha), Alpha analysis-report 리뷰 판정 (APPROVE), 경영진 공유용 보고서 초안 (member-beta), Beta draft-report 리뷰 판정 (APPROVE), Delta visuals 리뷰 판정 (APPROVE), 현장 실적·업계 동향 시각자료 (member-delta) (+26 more)

### Community 7 - "output 2026 배달 시장"
Cohesion: 0.12
Nodes (33): 쿠팡 AI·로보틱스 물류 투자 (NVIDIA DGX SuperPOD 협업), 배달의민족 (Baemin), 배달의민족(우아한형제들) 매각 이슈, 쿠팡이츠 (Coupang Eats), Windows 멀티바이트 한글 UTF-8 인코딩 깨짐 이슈, 시장 집중도 분석 (CR1/CR3/HHI), 2026 배달 시장 분석 — auto-log.md, 2026 배달 시장 분석 — final-artifact.md (+25 more)

### Community 8 - "patch"
Cohesion: 0.12
Nodes (32): BUG-01: alpha·gamma 역할 중복 (이중 웹 검색), BUG-02: 새 작업마다 slug 확인 인터럽트, BUG-03: 과거 리서치 재사용 불가, BUG-04: trigger 첫 번째 매칭으로 task type 오결정, CLAUDE.md, dev task type, github-plan task type, member-epsilon team-config.yaml 미등록 (+24 more)

### Community 9 - "ax"
Cohesion: 0.09
Nodes (31): xlsx-writer 스킬, column_mapping.md (xlsx 컬럼 ↔ 내부 필드명 매핑 정의서), 4륜사업부 운영지원팀 업무 가치사슬 — AX 설계 기반, AI 도입 우선순위 4단계 (Quick Win/표준자동화/자체데이터활용/복합시스템), AX 업무 자동화 실행 가이드 — 부서 담당자용 (ax-analysis-agent), 리소스 지수 (RI, Resource Index), B2B 실수행 조사 — 조사착수·시스템등록 상세 프로세스, B2B 실수행 조사 — 조사착수·시스템등록 프로세스 플로우차트 (+23 more)

### Community 10 - "baro"
Cohesion: 0.09
Nodes (30): 사내 AD 계정 연동 방식 (AD-AUTH.md), lib/auth-ldap.js (LDAPS bind 검증), core/ai_client.js 어댑터 패턴 (자두, 참조 only), 자두 프로젝트 (별개, 패턴 참조용), BARO AGENT 프로젝트 지침 (CLAUDE.md), BARO AGENT 같이 만들어가는 사내 AI 프로젝트 (docs/CLAUDE.md), v0.9.0 민감정보 마스킹 정식화, 버전 히스토리 v0.1.0~v0.9.0 (+22 more)

### Community 11 - "output 소화물 인증 등록제"
Cohesion: 0.13
Nodes (30): 배달대행사-PG사-이슈 (워크스페이스), 배달대행사 PG사 이슈 분석 보고서 (member-alpha), KYC·가맹점 심사 부담 증가 — 다층 참여자 구조에서 실질 가맹점/최종 수취인 식별 곤란, 정산 유동성 리스크 — 얇은 마진 구조에서 실시간 주문과 D+3~D+7 정산 지연 충돌, 정산자금 외부관리 규제로 심화 가능, 배달대행사 PG사 이슈 보고서 초안 (member-beta), 배달대행사 PG사 이슈 시각자료 (member-delta), 배달대행사 PG사 이슈 팩트체크 로그 (member-gamma), Google News RSS 제목 스캔 (PG 규제 관련 보도) (+22 more)

### Community 12 - "youtube"
Cohesion: 0.11
Nodes (27): Channel-First Collection Decision Memo, collect_channels.py (S1' panel uploads collection), discover_channels.py (S0 panel discovery), 채널 우선 표본조사 (Channel-First Panel Sampling), Windows UTF-8 Env Requirement Memo, Windows cp949 콘솔 UnicodeEncodeError 이슈, YouTube Intelligence Agent — Main Orchestrator (AGENTS.md), video-processor Sub-Agent Spec (+19 more)

### Community 13 - "archive"
Cohesion: 0.13
Nodes (26): 2026-07-29 정리 보관함 README, AUTO 실행 로그 (2026-배달-시장-점유율-분석해줘, 구버전 사본), 2026년 배달 시장 점유율 분석 최종본 (구버전 사본), analysis-report.md (member-alpha, 재실행본), member-alpha 2차 리뷰 판정 (APPROVE), draft-report.md (member-beta, 재실행본), member-beta 2차 리뷰 판정 (APPROVE), member-delta 2차 리뷰 판정 (APPROVE) (+18 more)

### Community 14 - "output 회의 녹음 텍스트"
Cohesion: 0.18
Nodes (26): member-epsilon (개발), 회의-녹음-텍스트-변환을-회의록 워크스페이스, app/main.py (FastAPI 진입점), app/requirements.txt (회의-녹음-텍스트-변환을-회의록), app/routers/minutes.py, app/routers/transcribe.py, app/services/claude_service.py, app/services/whisper_service.py (+18 more)

### Community 15 - "output on premise ai"
Cohesion: 0.18
Nodes (24): AI 기본법 (인공지능 발전과 신뢰 기반 조성 등에 관한 기본법), Claude Sonnet 4.6 API Pricing, 금융권 망분리 / 통합 AI 가이드라인, 퓨리오사 RNGD, Gemini 2.5 Pro API Pricing, GPT-4o API Pricing, Llama 4 Scout (17B active / 109B total), NVIDIA B200 (Blackwell, FP16 Tensor Core 4,500 TFLOPS) (+16 more)

### Community 16 - "ax"
Cohesion: 0.15
Nodes (19): ai-solution-designer 서브에이전트, resource-analyst 서브에이전트, AI 도입 우선순위 4단계 분류 기준 상세, ai-priority-classifier 스킬, resource-analyzer 스킬, xlsx-reader 스킬, 업무조사표 AI 분석 에이전트 오케스트레이터, AI-BPM (스마트 BPM 3가지 AI 역할) (+11 more)

### Community 17 - "member"
Cohesion: 0.29
Nodes (18): 실행 계획 plan.md (2026-배달-시장-점유율-분석해줘, 구버전 사본), member-alpha (조사), member-beta (보고서), member-delta (시각화), member-gamma (팩트체크), AX 대시보드 전사 현황 Team Capability Retrospective, ax-management-system-benchmark plan.md, 바로고 AX 통합 관리 시스템 평가 계획서 (ax-management-system-eval plan.md) (+10 more)

### Community 18 - "ax"
Cohesion: 0.19
Nodes (18): 바로고 AX 통합 관리 시스템 목업 (index.html), 4륜사업부 운영지원팀 업무 가치사슬 (AX 설계 기반), 브랜드물류 물류운영팀 가치사슬 AX 분석, 채널비즈니스팀 가치사슬 AX 분석, 커넥트운영팀 가치사슬 AX 분석, 재무회계팀 업무 가치사슬 (AX 설계 기반), 통합운영팀 가치사슬 AX 분석, 법무실 업무 가치사슬 (AX 설계 기반) (+10 more)

### Community 19 - "youtube"
Cohesion: 0.18
Nodes (18): report-builder 스킬 (S6 출력), 13개 카테고리 정의·우선순위·키워드 사전, video-classifier 스킬 (S2/S3), week-aggregator 스킬 (S4), youtube-collector 스킬 (S1), YouTube AI 트렌드 집계 에이전트 — 오케스트레이터, YouTube AI 트렌드 대시보드 (HTML/Chart.js), 채널 우선 수집 전환 (Channel-first Collection) (+10 more)

### Community 20 - "output slack self healing"
Cohesion: 0.23
Nodes (17): AUTO 모드 인터럽트 처리 규칙 ①~⑧, deploy-heal Skill (.claude/skills/deploy-heal/SKILL.md), Get-ServiceType 함수 (서비스 타입 자동 감지), Slack Self-Healing Pipeline Patch (final), Slack Self-Healing Pipeline - Analysis Report (member-alpha), Slack Self-Healing Pipeline - Draft Report (member-beta), Slack Self-Healing Pipeline - Dev Log (member-epsilon), Slack Self-Healing Pipeline - Design Spec (member-zeta) (+9 more)

### Community 21 - "erp"
Cohesion: 0.17
Nodes (17): 일일보드 대시보드 (#tab-daily-board iframe), 사업조직 BM 배부 테이블 (조직 × 종목 직접이익), B2B 타입별(A/B/D) 월예상 실손익, 월예상 산출 기준 (경과일 기반 연장계수 추정), 입력 — 사업BM/부서 페이지 (input.html), 자동/전월건당/전월기반/수기 데이터 출처 태그 분류, /auth/login 엔드포인트, 로그인 페이지 (login.html) (+9 more)

### Community 22 - "output 3d fps 게임"
Cohesion: 0.28
Nodes (16): Godot 4.x 엔진 (MIT 라이선스), 3D FPS 게임 개발 최종 산출물, Enemy.gd (IDLE/CHASE/ATTACK/DEAD 상태머신, 아이디어 참조), Head.gd (마우스 룩, 피치/요 분리, MIT 참조), MovementController.gd (CharacterBody3D 이동, MIT 참조), member-alpha 구현 방향 분석 보고서 (Godot 4 스택 선택), member-epsilon Dev Log (22개 파일 생성), member-epsilon Diff Summary (라이선스 귀속 요약) (+8 more)

### Community 23 - "slack"
Cohesion: 0.27
Nodes (15): app-B-*.py .gitignore 패턴 누락 (중간 심각도), Session Validation - Final Artifact (세션 검증 최종 보고서), Session Validation - Analysis Report (member-alpha), Session Validation - Draft Report (member-beta), Session Validation - Fact-Check Log (member-gamma), Session Validation Plan, Session Validation - Review Log, scripts/notion_publish.py (+7 more)

### Community 24 - "concept"
Cohesion: 0.24
Nodes (15): AI 도입 4단계 (Quick Win→표준자동화→자체데이터활용→복합시스템), 배달대행비 하락(-40%) vs 배달앱 이용료 상승(+40.9~59%) 비용 프레임, 필드 단위 maker-checker 승인 워크플로우, 프로세스 마이닝 (인접 영역, 예: IBM Process Mining), reduction_rate (AX 케이스 절감률 지표), 리소스 지수(RI = 총투입시간 × 반복성 가중치), RI 리소스 지수 (총투입시간 × 반복성 가중치), 가치사슬 Track→Stage 스윔레인 (+7 more)

### Community 25 - "output 전남 광주 지역"
Cohesion: 0.26
Nodes (15): 인도 닌자카트(Ninjacart) 종합 분석 보고서, Ninjacart 시장 조사 분석 보고서 (member-alpha), Ninjacart 종합 분석 보고서 초안 (member-beta), Ninjacart 시각자료 (member-delta), Ninjacart 팩트체크 로그 (member-gamma), Ninjacart(닌자카트), Review Log: 인도 닌자카트, Walmart 전략적 투자 (2019, 약 $30M) (+7 more)

### Community 26 - "output ax management system"
Cohesion: 0.38
Nodes (14): ax-management-system (평가 대상 코드베이스, FastAPI+SQLAlchemy+SQLite), AX_관리시스템_설계서.md (기준 설계 문서 §0~§9), DEV_AUTH 백도어 (F1 Critical, 인증 전면 우회), 오버엔지니어링 회피 권고 (Casbin·amis-admin 전면도입·PostgreSQL 전환 채택 금지), 자기승인 가능 결함 (F4 Critical, maker-checker 위배), member-zeta (설계), 바로고 AX 통합 관리 시스템 종합 평가 보고서 (Final Artifact), AX 시스템 코드품질·아키텍처 분석 (eval, member-alpha) (+6 more)

### Community 27 - "hrflow"
Cohesion: 0.22
Nodes (14): 워크(에이전트) 설정 모달 — cron 스케줄 + Node.js 스크립트, BARO AGENT Chat UI (index.html), 민감정보 자동 마스킹 및 대화 감사 정책 (회사 보안 정책, 개인 비활성화 불가), BARO AGENT 설정 화면, BARO AGENT 워크플로우(예약 자동화) 화면, BAROGO DEBTFLOW 앱 진입점 (index.html, React root), DEBTFLOW 배포 가이드 (README), BAROGO DEBTFLOW 앱 메뉴 구성 (Slack 인증·RBAC·6개 메뉴+어드민 명세) (+6 more)

### Community 28 - "output gpu 지원 받는"
Cohesion: 0.32
Nodes (13): GPU 지원 프로그램 현황 및 활용 방안 (최종본), AWS Activate, GPU 지원 현황 분석 보고서 (alpha), GPU 지원 프로그램 현황 및 활용 방안 보고서 초안 (beta), 시각화 산출물 — GPU 지원 현황 (delta), 팩트체크 로그 — GPU 지원 현황 분석 보고서 (gamma, 내부 정합성 검토), gpu-지원 리뷰 승인 판정, GPU 지원 받는 방법 — 최종 보고서 (+5 more)

### Community 29 - "output ax ax member"
Cohesion: 0.50
Nodes (12): AX 대시보드 (사내 API: api/v1/export/cases, api/v1/export/reports), 사내 대시보드 데이터 사용 시 human_approval override 규칙, AX 대시보드 전사 현황 워크스페이스 AUTO 실행 로그, AX 대시보드 전사 AX 진행 현황 요약 (Final Artifact), AX 대시보드 전사 AX 파이프라인 분석 보고서 (member-alpha), AX 대시보드 전사 현황 요약 초안 (member-beta), AX 대시보드 전사 현황 시각자료 (member-delta), AX 대시보드 cases/reports 원문 팩트체크 로그 (member-gamma) (+4 more)

### Community 30 - "4륜"
Cohesion: 0.29
Nodes (11): SP 유형 분류 (직계약/협력사/용차), 멀티 에이전트 구조 채택 근거, 삼성웰스토리 (화주사), 수식 삽입 필수 정책 (동적 엑셀), 4륜사업부 정산 시스템, 정산 워크플로우 (Step1~7), data-intake 서브에이전트, invoice-generator 서브에이전트 (+3 more)

### Community 31 - "output jeonnam gwangju ai"
Cohesion: 0.42
Nodes (11): 전남광주 AI 정부 사업 — 국민성장펀드 축으로 본 2026년 통합 리포트, SK-OpenAI 메가 데이터센터 ('한국판 스타게이트'), 광주 AX 실증밸리, 국민성장펀드, 신안우이 해상풍력 (국민성장펀드 공식 1호 투자), 해남 국가AI컴퓨팅센터 (삼성SDS 컨소시엄 SPC), Analysis Report — 전남광주 AI 정부 사업 (alpha), Draft Report — 전남광주 AI 정부 사업 (beta) (+3 more)

### Community 32 - "output 마켓 대시보드에서 이번주"
Cohesion: 0.33
Nodes (9): 사내 대시보드 사용 시 human_approval override 규칙, barogo-intel market 대시보드 API (api/report, api/keywords), 마켓 대시보드 인사이트 요약 auto-log.md, 마켓 대시보드 인사이트 요약 final-artifact.md, 마켓 대시보드 alpha analysis-report.md, 마켓 대시보드 beta draft-report.md, 마켓 대시보드 delta visuals.md, 마켓 대시보드 인사이트 요약 retrospective.md (+1 more)

### Community 33 - "output 배달시장 ms member"
Cohesion: 0.44
Nodes (9): 배달시장 MS 분석 (워크스페이스), 국내 배달 플랫폼 시장점유율(MS) 분석 보고서 (최종), 쿠팡이츠 (쿠팡) — MAU 기준 MS ~24%, 배달시장 MS 분석 보고서 (member-alpha), 배달시장 MS 보고서 초안 (member-beta), 배달시장 MS 시각자료 (member-delta), 배달시장 MS 팩트체크 로그 (member-gamma), 배달시장 MS 분석 계획 (plan.md) (+1 more)

### Community 34 - "output 3개월 시장 동향"
Cohesion: 0.39
Nodes (8): 배민-배달대행 6개사 위치추적 표준연동, 라이더 근로자성 판결 확정(서울고법·상고포기), 3개월 시장 동향 draft-report.md (member-beta), 3개월 시장 동향 .review-verdict.md (member-delta 대상), 3개월 시장 동향 visuals.md (member-delta), 3개월 시장 동향 fact-check-log.md (member-gamma), 3개월 시장 동향 .review-verdict.md (member-gamma 대상), 3개월-시장-동향-분석해서-바로고 workspace

### Community 35 - "meeting"
Cohesion: 0.32
Nodes (8): Notion Integration Subagent, NotionBlockConverter, NotionSyncService, Build Android APK Workflow, Release APK Workflow, n8n 워크플로우 LLM 설계 & JSON 빌더 사용 가이드, n8n 셀프호스팅 구축 가이드, n8n 사용자 가이드 (Markdown)

### Community 36 - "output 광주전남 농축수산물 폐기율"
Cohesion: 0.57
Nodes (8): 광주전남 농축수산물 폐기율 final-artifact.md, 광주전남 폐기율 alpha analysis-report.md, 광주전남 폐기율 beta draft-report.md, 광주전남 폐기율 delta visuals.md, 광주전남 폐기율 gamma fact-check-log.md, 광주전남 농축수산물 폐기율 review-log.md, 가격 폭락-산지 폐기 악순환, 전남 도서·산간 콜드체인 인프라 부족

### Community 37 - "ai"
Cohesion: 0.38
Nodes (7): 병렬 API 호출 (DALL-E3/SDXL/Runway), AI 미디어 제작 에이전트 통합 설계서, 5단계 워크플로우 (프롬프트→생성→선별→편집→승인), media-generator 서브에이전트, prompt-engineer 서브에이전트, 바로고 AI 미디어 제작 에이전트 오케스트레이터, ImportError: get_session_dirs (config.py)

### Community 38 - "ax"
Cohesion: 0.43
Nodes (7): apply_june.py (손익 계산 엔진), 전사손익 ERP 서버 작업 가이드 (Claude용), NSSM 2.24 ChangeLog.txt, NSSM 2.24 README.txt, backend/routers/board.py (대시보드 API), 서버_코드동기화_ERP.ps1 (배포 스크립트), NSSM (The Non-Sucking Service Manager)

### Community 39 - "output agent team eval"
Cohesion: 0.48
Nodes (7): 파일 오너십 비강제(텍스트 규칙 의존), 순차 실행 구조 (병렬 실행 부재), member-eta (OSS리서치), agent-team-eval final-artifact.md, agent-team-eval analysis-report.md (member-alpha), agent-team-eval draft-report.md (member-beta), agent-team-eval github-research-report.md (member-eta)

### Community 40 - "meeting"
Cohesion: 0.43
Nodes (7): Android 빌드 버전 고정 규칙 (Kotlin 2.1.0 / AGP 8.5.2 / Gradle 8.10.2), notion-integration 서브에이전트 (Notion 페이지 생성·마크다운 블록 변환), Meeting Assistant CLAUDE.md 오케스트레이터 지침, Meeting Assistant 개발 완료 및 배포 가이드 (DEPLOYMENT.md), APK 한 파일로 폰에 설치하기 — GitHub Actions 빌드 가이드, Meeting Assistant 앱 설계서 (온디바이스 Whisper Tiny + Gemma 4 2B 원안), STT/LLM 엔진 선택 아키텍처 결정 (완전 온디바이스 → 클라우드/온디바이스 하이브리드 전환)

### Community 41 - "output 도심물류 os member"
Cohesion: 0.52
Nodes (7): 도심물류 OS final-artifact.md, 도심물류 OS alpha analysis-report.md, 도심물류 OS beta draft-report.md, 도심물류 OS delta visuals.md, 도심물류 OS gamma fact-check-log.md, 도심물류 OS (Urban Logistics Operating System), 도심물류 OS 9개 기능 모듈

### Community 42 - "output ai 기업 gpu"
Cohesion: 0.67
Nodes (6): 전력·데이터센터·HBM·운영인력 병목, 2026년 AI컴퓨팅자원 활용기반 강화사업(2조 805억원), ai-기업-gpu-지원 final-artifact.md, ai-기업-gpu-지원 analysis-report.md (member-alpha), ai-기업-gpu-지원 draft-report.md (member-beta), ai-기업-gpu-지원 review-log.md

### Community 43 - "ax"
Cohesion: 0.50
Nodes (5): F1 Critical: DEV_AUTH 백도어 (fail-open), F4 Critical: 자기승인 가능 (maker-checker 위배), 바로고 AX 통합 관리 시스템 종합 평가 보고서, P0 우선순위 로드맵 (배포 전제조건), 바로고 AX 관리시스템 기능·UI 경쟁 벤치마크 보고서

### Community 44 - "tetris"
Cohesion: 0.70
Nodes (5): Collision Detection (collide()), Game Loop (update/draw), Line Clearing (merge()/clearLines()), Piece class, Tetris Web Game

### Community 45 - "ax"
Cohesion: 0.50
Nodes (4): B2B 트랙 (4건), 허브 트랙 (14건), T022-T023 야간·주말·시스템이슈 응대 (700h/월), 현장총괄본부 가치사슬 AX 분석 (문서)

### Community 46 - "meeting"
Cohesion: 0.50
Nodes (4): AI Pipeline Subagent (Whisper + Gemma 온디바이스 통합), WhisperSTTService, Meeting Assistant (Flutter App), record_linux Dependency Override

### Community 47 - "output github researcher final"
Cohesion: 1.00
Nodes (3): github-plan task type, member-eta (GitHub Researcher), team-config-patch.yaml

## Ambiguous Edges - Review These
- `team-config.yaml` → `README/Config Documentation Drift (stale task type and member list)`  [AMBIGUOUS]
  C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/README.md · relation: conceptually_related_to
- `AUTO 모드 인터럽트 처리 규칙` → `ADR-3: Modification-Scale-Based Direct-Edit vs Reassign Branching`  [AMBIGUOUS]
  C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/CLAUDE.md · relation: conceptually_related_to
- `Agent Team Framework README` → `README/Config Documentation Drift (stale task type and member list)`  [AMBIGUOUS]
  C:/Users/jmlee/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team/README.md · relation: conceptually_related_to
- `AI 미디어 제작 에이전트 통합 설계서` → `ImportError: get_session_dirs (config.py)`  [AMBIGUOUS]
  ai-media_agent/streamlit_err.txt · relation: conceptually_related_to
- `전사손익 ERP 서버 작업 가이드 (Claude용)` → `NSSM (The Non-Sucking Service Manager)`  [AMBIGUOUS]
  ax-management-system/서버작업가이드_클로드용.md · relation: conceptually_related_to

## Knowledge Gaps
- **38 isolated node(s):** `Fable-Style Response Guide`, `crisis-comms Skill`, `Quick Query 실행 절차 (데이터소스 식별→직접호출→감사로그→승인게이트→응답전달)`, `SQL Reader Skill`, `Git Pre-commit Hook (문서 노후화 방지)` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `team-config.yaml` and `README/Config Documentation Drift (stale task type and member list)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `AUTO 모드 인터럽트 처리 규칙` and `ADR-3: Modification-Scale-Based Direct-Edit vs Reassign Branching`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Agent Team Framework README` and `README/Config Documentation Drift (stale task type and member list)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `AI 미디어 제작 에이전트 통합 설계서` and `ImportError: get_session_dirs (config.py)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `전사손익 ERP 서버 작업 가이드 (Claude용)` and `NSSM (The Non-Sucking Service Manager)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `member-alpha (조사)` connect `member` to `output 마켓 대시보드에서 이번주`, `output market intelligence report`, `output 광주전남 농축수산물 폐기율`, `output agent team eval`, `patch`, `output 도심물류 os member`, `output ai 기업 gpu`, `archive`, `concept`, `output ax management system`, `output ax ax member`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `agent-self-review analysis-report.md (member-alpha)` connect `patch` to `member`, `output ax management system`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._