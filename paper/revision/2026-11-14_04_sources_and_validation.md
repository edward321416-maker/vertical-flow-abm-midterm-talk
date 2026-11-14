# 근거 원장, 재현 경로, 검증 상태와 남은 과제 (2026-11-14)

**원본 보존:** 이 연구의 검토 대상은 사용자 업로드 9쪽 PDF. SHA-256: `8efa8801790a9ff706456cc53bbfa56c3905131876c8d3609d9e93897ab90c07`. 로컬 파일은 GitHub에 복제하거나 공개하지 않았으며 이 문서는 원고의 주장과 **공개 가능한 프로젝트 원천**만 기록한다. 원문 PDF의 저자 이메일·개인정보는 이 문서에 재게시하지 않는다.

## 1. 원천 파일의 역할과 현재 검증 상태

| 유형 | 파일/URL | 무엇을 검증하는가 | 제한 |
|---|---|---|---|
| 논문 최종 원고 | 업로드 `봉성현 논문 최종.pdf`, 9p (2026-11-14 사용자가 제공) | 저자가 실제 기술한 제목·초록·연구방법·결론의 현재 표현 | 업로드 파일은 공개 repo의 기존 텍스트와 같다고 단정하지 않음 |
| 연구 모형 | [simulation/vertical_flow.gaml](../../simulation/vertical_flow.gaml) | 비공간 층/이동수단 선택 구조, `gamma*x_fnb[j]` 모델, 경계 crossing 집계 | 실제 건축 단면/XY 경로 아님 |
| 사전 계획 | [docs/simulation/aik_experiment_plan.md](../../docs/simulation/aik_experiment_plan.md) | 9층, E1/E2, 도착률 및 입력 가정, θ2=0, 통계량 정의, 실물 외삽 금지 | 원문 PDF의 모든 설명이 계획과 일치하는 것은 아님 |
| E1/E2 생성 | [analysis/R/experiments/aik_program_circulation.R](../../analysis/R/experiments/aik_program_circulation.R) | E1 8셀×200 / E2 10셀×100, TOP1/STEP3/UNIFORM/LOW3 비중 | 4일 개별 반복의 원 run 폴더는 공유 repo에 전부 없을 수 있음 |
| 분석 코드 | [analysis/R/experiments/aik_analysis.R](../../analysis/R/experiments/aik_analysis.R) | A1~A4 분석방법 및 두타 참조 시뮬레이션 집계 코드 | 이 코드·CSV를 단독 외부 실증 검증으로 오해 금지 |
| 실제 출력 A1 | [aik_a1_profile.csv](../../analysis/outputs/aik/aik_a1_profile.csv) | γ0 연속/분절 U·AUFR·RUI 반복 평균 | count event, 4일 누적, 200회 |
| 실제 출력 A2b | [aik_a2b_constructs.csv](../../analysis/outputs/aik/aik_a2b_constructs.csv) | 프로그램 예측변수별 `U` deviance 설명 비율 | A2의 `logAUFR`에 대한 분석 아님 |
| 실제 출력 A3 | [aik_a3_moderation.csv](../../analysis/outputs/aik/aik_a3_moderation.csv) | γ2,4,8의 프로그램 효과 잠식과 95% 부트스트랩 CI | 상행유량 기본값 감소율과는 다른 추정량 |
| 실제 출력 A4 | [aik_a4_reach.csv](../../analysis/outputs/aik/aik_a4_reach.csv) | E2 상단경계 대비 첫경계 T, 평균 R 및 CI | 고유 방문객의 실제 도달 확률 아님 |
| E2 contrasts | [aik_a4_contrasts.csv](../../analysis/outputs/aik/aik_a4_contrasts.csv) | 네 유형 중 사전 지정 쌍대 비교·Holm 보정 | 매출/공실을 최적화하지 않음 |
| 두타 참조 결과 | [aik_doota_reference.csv](../../analysis/outputs/aik/aik_doota_reference.csv) | 2F–3F 등 3개 경계의 과거 `audit1` 시뮬레이션 AUFR | **실측 아님**; `aik_analysis.R` 155–172행은 `truth.csv` 시뮬레이션 값 집계 |

## 2. 집계 수치 검증 테이블: 수치와 무엇을 뜻하는지 함께 보존

| 증거 ID | 실험, 조건 | 정확 값 | 본문에 쓸 수 있는 표현 |
|---|---|---|---|
| E1-A1-CONT-U1 | E1 γ0 cont 200반복 4일 | U1=12346.405 | 1F→2F 첫 상향 경계 통과량 반복 평균 ≈ 12,346 |
| E1-A1-CONT-U8 | E1 γ0 cont 200반복 4일 | U8=447.76 | 8F→9F 최상향 경계 통과량 반복 평균 ≈ 448 |
| E1-A1-CONT-RUI8 | E1 γ0 cont 200반복 4일 | 0.0363039287507832 | 반복별 `U8/U1` 평균 ≈ 3.63% |
| E1-A1-FRAG-U1 | E1 γ0 frag 200반복 4일 | 9802.105 | 분절형 첫 상향 경계 평균 ≈ 9,802 |
| E1-A1-FRAG-U8 | E1 γ0 frag 200반복 4일 | 408.29 | 분절형 마지막 상향 경계 평균 ≈ 408 |
| E1-A1-FRAG-RUI8 | E1 γ0 frag 200반복 4일 | 0.0416571036224497 | 반복별 최상단/첫 경계 유량비 평균 ≈ 4.17% |
| E1-A2b-Xupper | E1 γ4 cont | .601230739337442 | 경계·반복 효과 조정 기준모형에 x_upper 추가 시 남은 deviance 감소 **60.1%** |
| E1-A2b-M | E1 γ4 cont | .397414074470003 | M_above 모델 **39.7%** |
| E1-A2b-Delta | E1 γ4 cont | .102205537786509 | Δx 모델 **10.2%** |
| E1-A3-g2 | E1 γ2 | erosion=.0672308209787521, CI [.0268894606,.105124014] | γ2에서 유인 반응 기울기 잠식 6.72%, 95% CI 2.69–10.51% |
| E1-A3-g4 | E1 γ4 | erosion=.00771559776419, CI [−.0411400544,.0522439559] | 0.77%, CI −4.11~5.22% (**0 포함**) |
| E1-A3-g8 | E1 γ8 | erosion=.0167037769666, CI [−.0640581709,.0855536599] | 1.67%, CI −6.41~8.56% (**0 포함**) |
| E2-A4-TOP1 | E2 γ4 cont 100반복 | T=.58749753933521, R=.554377179614336 | U8/U1 약 58.7%, 평균 상대 경계 유량 지수 약 .554 |
| E2-A4-STEP3 | E2 γ4 cont 100반복 | T=.140279887035909, R=.408646036516915 | T 14.0%, R .409 |
| E2-A4-UNIFORM | E2 γ4 cont 100반복 | T=.0587550550738161, R=.311350234930786 | T 5.9%, R .311 |
| E2-A4-LOW3 | E2 γ4 cont 100반복 | T=.0150399698665353, R=.284094758279213 | T 1.5%, R .284 |
| DOOTA-AUDIT-REFERENCE | 기존 `audit1` GAMA 시뮬레이션 | AUFR mean .512036/.514365/.429464 | 두타 설정 참조한 이전 시뮬레이션 모델 값, **현장 실측치 아님** |

**중요한 통계적 미세 구분:** `mean_r(U8_r/U1_r)`은 일반적으로 `mean_r(U8_r)/mean_r(U1_r)`와 다르다. 원 CSV의 `RUI_mean` 값은 반복별 비율의 평균이다. p-value, CI, R²/deviance 등의 표기에는 원 코드가 무엇을 계산했는지 우선 확인한다.

## 3. 수직 프로그램 배치 매핑 (코드 우선)

9층: S00=1F, S01=2F, S02=3F, S03=4F, S04=5F, S05=6F, S06=7F, S07=8F, S08=9F.

E2에서는 1F S00 `x=.05` 고정, 2F~9F 8개 층의 프로그램 비중 합은 **1.60**.

| 배치 | 2F~9F의 값 | 핵심 층 | 기호의 합 |
|---|---|---|---|
| TOP1 | 9F .85 + 2F~8F 각 .107143 | 9F | 약 1.60 |
| STEP3 | 3,6,9F 각 .45 + 나머지 다섯 층 .05 | 3F, 6F, 9F | 1.60 |
| UNIFORM | 2F~9F 모든 층 .20 | 특정 집중 없음 | 1.60 |
| LOW3 | 2,3,4F 각 .45 + 나머지 다섯 층 .05 | 2F, 3F, 4F | 1.60 |

원문 p4의 `S02=2F` 또는 `S01=1F`처럼 읽히는 매핑은 원 코드 기준으로 정정해야 함.

## 4. 독립 외부자료 등록 (URL은 출처, 연구 성능 검증이 아님)

**수상 확인(공식 기관):**
- RIBA Dissertation Medal 2025: https://www.riba.org/news/riba-announces-presidents-medals-2025/ — 수상·제목·평가 요약만 검토.
- RIBA Dissertation Medal 2024: https://www.ucl.ac.uk/bartlett/news/2024/dec/bartlett-students-recognised-2024-riba-presidents-medals — 공식 수상·개요.
- RIBA Dissertation Medal 2023: https://architecturetoday.co.uk/2023-riba-presidents-medal/ — 수상 보도·개요.
- EDRA Best Paper 2023/24/25: https://www.edra.org/best-paper-award — 수상 명단. 2023 원문 회의록 검색: https://cdn.ymaws.com/www.edra.org/resource/resmgr/proceedings/fullproceedings/edra54_proceedings_ch1-12.pdf .
- ASCE JAE Best Paper 2022: https://ascelibrary.org/jaeied/best_paper_awards / 저자 수상 논문 상세 초록 https://epublications.marquette.edu/civengin_fac/374/ .

**직접 관련된 학술 연구(수상 이력 주장하지 않음):**
- KCI 2025, 권예진·김동식, DOI 10.14774/JKIID.2025.34.6.009: https://www.auric.or.kr/User/Rdoc/DocRdoc.aspx?dn=450088&returnVal=RD_R .
- eCAADe 2024 Zhong et al. 상업시설 보행 시뮬레이션 및 현장 검증: https://ecaade.org/current/wp-content/uploads/2024/10/eCAADe2024_Volume2_240927-R.pdf .
- Buildings 2024 Zhou et al. DOI 10.3390/buildings14061782: https://www.mdpi.com/2075-5309/14/6/1782 .
- Buildings 2024 Hosseini et al. DOI 10.3390/buildings14092724: https://www.mdpi.com/2075-5309/14/9/2724 .
- ODD 재현성 기준: https://jasss.soc.surrey.ac.uk/23/2/7.html .
- 공간구문론 이론 원전: https://doi.org/10.1068/b200029 .
- 다층 복합단지 관측 원전: https://doi.org/10.1068/b250507 .
- 소매보행 선택 원전: https://doi.org/10.1111/j.1538-4632.1986.tb00086.x .

**집필/투고 지침:**
- AIK 국문논문 투고안내: https://www.aik.or.kr/pages_submission/ko_journal.vm — **2026-11-30부터 별도 개정지침이 적용될 수 있으므로 현재 접수/학부 졸업 제출양식과 혼동 금지**.
- Nature writing: https://www.nature.com/articles/nmeth.4532 .
- Elsevier structuring: https://www.elsevier.com/connect/11-steps-to-structuring-a-science-paper-editors-will-take-seriously .
- UC Berkeley Library: https://guides.lib.berkeley.edu/publish/writing .

## 5. 아직 확인하지 못한 사실 / 논문에 함부로 써서는 안 되는 것

| 번호 | 쟁점 | 왜 미확인인가 | 어떻게 처리해야 하는가 |
|---|---|---|---|
| PENDING-01 | 두타몰 **현장** AUFR/방문객 실측 | 프로젝트의 `audit1`은 실제 GAMA `truth.csv`; 관측 원장·수집일·위치 없음 | 본문 '실측 타당성 검증' 삭제. 실측을 확보하면 수집조건과 출처 검토 후 별도 외부검증 |
| PENDING-02 | 도착률 7집단/분 등이 두타몰 현장에서 추정된 값인지 | 코드의 중심 파라미터 설정은 확인되지만 원 현장 조사 출처 없음 | '두타몰 운영 조건 템플릿 일부 참고/가정치'로 표기 |
| PENDING-03 | γ=2/4/8의 카페/식당/영화관 대응을 실제 조사로 정한 것인지 | 실증적 설문·선호추정·탄력성 근거가 없음 | '가상 유인 강도 3수준'으로 표시하고 업종 예시는 설명용 |
| PENDING-04 | 9F 앵커비중 .85의 법규/임대/운영상 실현 가능성 | 원 모형은 효용의 가상 입력값, 시설 도면/경제성 없음 | 결과는 '선정된 시나리오의 상단 경계 유량비'로만 |
| PENDING-05 | RQ4의 '징검다리형이 가장 균형적인 실제 설계 전략' | 데이터 T, R에서 TOP1이 모두 높으며 균등성·매출은 종속변수 아님 | 근거 없는 우위 해석 삭제 또는 별도 평가 지표 설정 후 새 연구 |
| PENDING-06 | 실제 3D 매장·에스컬레이터 위치·보행 궤적 | GAML은 비공간 선택 모형 | 개념 시각화는 'illustrative, not actual XY traces' 문구 삽입 |
| PENDING-07 | RIBA/EDRA 수상작의 **전체 문장 수준** 집필 비교 | 일부는 보도자료와 제목/초록만 공개 접근됨 | 전체 원문 미독해를 표시. 원문 확보 없이 구체 장·문단 내용 추정 금지 |
| PENDING-08 | 실물 상업시설 상층 공실/매출 효과 | 변수 측정 안 함 | 공간계획상 '추가 검토 가능성' 이상의 표현 금지 |
| PENDING-09 | 학위논문 심사 형식과 대한건축학회 정식 투고 규격 간 관계 | 실제 제출 목적·학과 규격 별도 확인 필요 | 논리 수정과 실측 수정 우선, 최종 포맷은 공식 규격에 맞게 조정 |

## 6. 결과를 재생산·재검증할 때의 체크포인트

1. `aik_program_circulation.R` 패턴 정의를 읽어 논문 p4의 한글 층번호와 일치시키고, E1/E2 반복수를 계산한다.
2. `aik_analysis.R` 59–72행의 **A2b U 변수**와 39–59행의 A2 **log AUFR 변수**를 문단마다 표시한다.
3. `aik_a1_profile.csv` γ0 cont/frag 8개 경계를 비교하며 정확 집계 단위를 '4일 누적 상향 경계 통과 인원 이벤트 평균'으로 적는다.
4. `aik_a3_moderation.csv` γ2/4/8 잠식률 + 신뢰구간이 0을 포함하는지 표기한다.
5. `aik_a4_reach.csv` T/R 순위와 `aik_a4_null_check.csv`의 γ0 대조 결과를 함께 설명한다.
6. `aik_doota_reference.csv`가 어디서 생성됐는지 `aik_analysis.R` 155–172행을 보고 '실측'이 아님을 확인한다.
7. PDF 완성 후 페이지별 렌더링으로 수식 첨자·표·축 범례와 자료의 출처 주석까지 검수한다.

## 7. 현 상태 결론

- **확인 완료:** 원문 PDF 9쪽 읽기/페이지 렌더, GitHub 원 GAML/R/CSV 대조, 수상작·관련 연구·학회 공지의 공개 서지 검증, 논리/지표/결론 오류 판정, 별도 브랜치의 개정 설계도 작성.
- **미완료:** 실제 논문 본문 대체·수정본 PDF 제작, 지도교수 의견, 현장 보행 계측자료 확보, 외부 동료심사, 완전한 건축 설계 최적성 검증.
- **저장 규칙:** 별도 계획 브랜치에 문서만 추가. 원문 PDF와 실험 결과·코드, main, 이전 협업 브랜치는 변경하지 않는다.
