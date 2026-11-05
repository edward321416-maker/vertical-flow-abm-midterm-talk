# 레퍼런스 검토 기록

## 1. 외부 레퍼런스 접근 상태

이 세션에서는 아래 6개 지정 URL을 **하나도 열지 못했다.** 웹 검색 결과 요약만 확인했고, 원문 본문이나 그림은 보지 못했다.

| 시도 | 방법 | 결과 |
|---|---|---|
| 1차 (2026-11-05 00:2x UTC) | curl (에이전트 프록시) | 403/502 `CONNECT tunnel failed`. 프록시가 호스트를 거부 |
| 1차 | WebFetch 서브에이전트 | `getaddrinfo ENOTFOUND`. 세션의 허용 도메인 밖 |
| 2차 (2026-11-05 00:47 UTC) | curl 재시도 | 6개 모두 연결 실패(HTTP 000) |
| 보조 | WebSearch | 검색 결과의 제목·URL·요약만 받음 |

따라서 아래 외부 자료는 모두 **「검색 결과만 확인」**이다. 슬라이드의 어떤 그림도 외부 그림을 복사하거나 트레이싱하지 않았다. 모든 도식은 저장소 CSV로 새로 그린 벡터다.

| 출처 | URL | 확인 수준 | 검색 요약에서 확인한 내용 | 적용 |
|---|---|---|---|---|
| Nature Research Figure Guide | https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/ | 검색 결과만 | 글꼴 5–7pt, 89/183mm 폭, WCAG 2.1 AA | 일관된 단일 서체와 접근성 대비만 적용. 5–7pt는 발표 화면에 맞지 않아 적용하지 않음(본문 최소 10pt) |
| Nature Reviews artwork guide | https://www.nature.com/documents/natrev-artworkguide.pdf | 검색 결과만(존재·제목) | 내용 미확인 | 근거로 사용하지 않음 |
| CCC Architecture, diagrams | https://www.cccarchitecture.org/analyzing-architecture-through-diagrams | 열람 실패 | 내용 미확인 | 근거로 사용하지 않음 |
| Cornell AAP Erciyes | https://es.aap.cornell.edu/research/erciyes/ | 열람 실패 | 내용 미확인 | 근거로 사용하지 않음 |
| Datawrapper Academy, 신뢰구간 오버레이 | https://www.datawrapper.de/academy/confidence-intervals-error-bars-datawrapper-bar-charts | 검색 결과만 | 구간의 종류(95% CI, 범위, 표준편차 등)를 독자가 알 수 없으니 제목·주석에 명시하라는 요약 | 12·14장은 「95% 신뢰구간」, 11장은 「200회 반복값의 2.5–97.5 백분위 구간(평균의 신뢰구간 아님)」, 13장은 「여섯 조건의 최솟값–최댓값 범위(신뢰구간 아님)」로 구간 종류를 각각 명시 |
| Datawrapper, dot/range plot 예시 | https://www.datawrapper.de/academy/examples-of-datawrapper-dot-charts | 검색 결과만 | 점 그래프·범위 그래프 분류 | 13장 점+범위 표시 |
| 건축 다이어그램 유형 개요 (illustrarch, novatr 등 교육·블로그) | 검색 결과 | 검색 결과만 | 프로그램·순환·단면 다이어그램을 구분 | 7장(측정 위치)과 8장(확대 단면), 15장(층별 프로그램 비중 매트릭스)의 정보 유형을 분리 |

외부 레퍼런스로 「건축 다이어그램 4건 이상, 학술 그래픽 4건 이상을 실제로 열람」하라는 요구는 **충족하지 못했다.**

## 2. 실제로 열어 확인한 자료 (저장소 안)

디자인과 내용의 최종 근거는 아래 자료다. 모두 이 세션에서 직접 열어 읽었다.

| 자료 | 경로 | 사용한 내용 |
|---|---|---|
| 수정 논문 8쪽 | `cloud_task/inputs/paper_revised_8pages_v2(2).pdf` | 지표 정의 식 (3)–(6). 그림 1–3의 구성(절대 U와 AUFR 분리, 승수와 CI, 잠식률과 CI, RUI 궤적·T·U₈ 분리). γ=0의 의미(4.1절: 「이동 마찰만의 자연 상태로 해석할 수는 없다」). E2 배치 정의(3.2절) |
| 기존 18장 발표 PDF | `cloud_task/inputs/vertical_flow_presentation_clear_titles.pdf` | 페이지 대응, 기존 문구와 수치 |
| 실행 단위 결과 CSV | `analysis/outputs/aik/aik_boundary_rep.csv` (20,800행) | 모든 핵심 수치를 독립 재계산 (`qa/verify_numbers.py`) |
| 요약 CSV | `analysis/outputs/aik/aik_a1_*.csv`, `aik_a2_theta.csv`, `aik_a2b_constructs.csv`, `aik_a3_moderation.csv`, `aik_a4_reach.csv`, `aik_e2_profile.csv`, `aik_checks.csv` | 그래프 데이터와 CI |
| 시각화 기획안 | `presentation/plans/plan_03_visualization_principles.html` | 「한 장에 한 질문」, 「그림 면적의 대부분이 데이터」, 연속형=남색·분절형=갈색의 고정 색 의미. 이 원칙을 유지함 |
| 메시지 설계 | `docs/talk_message_design.md` | 발표 흐름. 다만 「프로그램이 없으면(γ=0)」, 「최상층 도달」 같은 표현은 수정 논문 기준에 맞지 않아 따르지 않음 |
