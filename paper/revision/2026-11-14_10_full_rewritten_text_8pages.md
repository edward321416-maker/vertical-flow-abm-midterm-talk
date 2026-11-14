# 최종 졸업논문 개정 텍스트 (2026-11-14)

> 실제 조판·그림·표·8쪽 검증은 사용자에게 전달한 `Thesis8_Revision2.pdf` 기준입니다. 이 파일은 GitHub에서 문장과 논증을 검토하기 위한 텍스트 전용 복제본입니다. 개정본의 세 도판(1,2,5)은 기존 GitHub SVG와 구성이 다르므로 구판 도판 파일과 혼동하지 마세요.

# 가상 다층 상업시설의 프로그램 유인과 수직동선 조건에 따른 층간 상행유량 변화

*― 에이전트 기반 시뮬레이션을 활용한 민감도 및 수직 배치 비교 ―*

Variations in Inter-Floor Upward Flow by Program Attraction and Vertical Circulation Conditions in a Synthetic Multi-Level Commercial Facility: An Agent-Based Sensitivity and Allocation Study

봉 성 현*    /    Bong, Seong-Hyun

* 성균관대학교 건축학과 학사과정 / B.Arch. Candidate, Sungkyunkwan University, Korea

## Abstract

In multi-level commercial facilities, vertical travel resistance and destination attractiveness may jointly influence pedestrian circulation, making their separate roles difficult to identify from observations alone. This study examines upward boundary-crossing flows using a non-spatial agent-based model of a synthetic nine-floor commercial facility. Experiment E1 compares four assumed levels of destination-program attraction (γ = 0, 2, 4, and 8) and two vertical circulation conditions, with 200 replicates per condition. Experiment E2 compares four program-allocation patterns under an equal total allocation, with 100 replicates per condition. Under γ = 0 with continuous circulation, the mean four-day cumulative flow declined from 12,346 crossings at the first upward boundary to 448 at the uppermost boundary. Under γ = 4 with continuous circulation, adding the upper-floor program share to a boundary- and replicate-adjusted quasi-Poisson model reduced its remaining deviance by 60.1%, compared with 39.7% for the mean share above the boundary and 10.2% for the adjacent-floor contrast. Fragmented circulation reduced baseline upward flow, while a statistically distinguishable reduction in attraction sensitivity was found only at γ = 2. Under the equal-allocation comparison, the uppermost-to-first-boundary flow index was 58.7% for the top-concentrated pattern and 14.0% for the stepping pattern. These results demonstrate conditional relationships within the specified model rather than externally validated design effects. They suggest that vertical circulation resistance and destination-program allocation should be evaluated together, subject to validation using observed pedestrian movements and spatially explicit models.

Keywords: multi-level commercial facility; upward boundary flow; destination attraction; vertical circulation; agent-based simulation; program allocation

## 1. 서론

### 1.1 연구 배경과 문제 제기

다층 상업시설의 건축계획에서는 방문객이 여러 층을 거쳐 이동하도록 만드는 수직동선의 구조와 각 층에 배치되는 상업·문화 프로그램을 함께 고려해야 한다. 상층부로 이동하려면 수단을 선택하고, 층간 이동에 소요되는 시간과 비용을 감수해야 한다. 반면 특정 목적지가 충분히 매력적이라면 방문객은 중간 층을 지나서라도 상부층을 선택할 수 있다. 따라서 상층부로 이어지는 보행 흐름은 이동 저항만으로 설명할 수도, 프로그램의 집객력만으로 설명할 수도 없다.

본 연구는 이러한 비교 문제를 층간 경계를 위쪽으로 통과하는 누적 유량으로 좁힌다. 개별 매장 앞 체류 인원이나 전체 건물 방문객 수가 아니라, 연속한 두 층 사이의 상향 통과 이벤트를 동일한 단위로 집계한다. 이를 통해 이동 조건을 바꾼 경우와 프로그램 유인 강도 또는 배치만 바꾼 경우의 결과를 비교한다. 연구의 관심은 특정 실제 쇼핑몰의 설계를 재현하는 데 있지 않고, 명시한 층 선택 규칙에 따라 나타나는 상행유량 분포와 그 민감도를 살펴보는 데 있다.

기존 건축·도시공간 연구는 보행량의 형성에 공간구조와 목적지 유인이 함께 관련된다는 논의를 제시해 왔다. Hillier 등(1993)의 자연 이동 이론은 통로 및 연결망의 구성과 유인 요소를 구분하는 이론적 관점을 제공하며, Chang과 Penn(1998)은 다층 도시 복합공간의 이동에 여러 공간적 제약이 작용하는 문제를 검토하였다. 최근의 상업시설 연구에서는 실제 평면과 가시성 분석 또는 에이전트 기반 모형을 통해 보행 분포를 예측하고 비교하는 접근도 나타난다(Zhong et al., 2024; Kwon & Kim, 2025). 다만 실제 시설을 대상으로 할 때는 매장 구성, 면적, 출입구와 동선 조건이 동시에 달라지기 때문에, 특정 조건을 바꾸었을 때의 보행 흐름 변화를 별도로 비교하기 어렵다. 본 연구는 이와 달리 시설의 층 수와 기본 조건을 고정하고, 수직동선의 이동 저항과 목적지 프로그램의 유인 강도를 각각 변화시킨다. 이를 통해 동일한 건물 조건에서도 어떤 변수가 상층 경계의 통과량을 더 잘 설명하는지 살펴보며, 비교 결과를 실제 시설의 직접적인 효과로 일반화하지 않는다는 범위를 분명히 한다.

### 1.2 연구 목적, 질문과 범위

본 연구의 주된 질문은 다음과 같다. 가상 다층 상업시설에서 수직동선의 저항과 목적지 프로그램의 유인은 층간 상행유량에 어떻게 관계하며, 동일한 프로그램 총량을 수직으로 다르게 배분할 때 유량 분포가 어떻게 달라지는가? 이를 네 단계의 연구질문으로 구분하였다. RQ1은 목적성 앵커의 추가 유인이 없는 기준조건에서 높이에 따른 유량 변화를 확인한다. RQ2는 인접층의 프로그램 비중 차이와 경계 위쪽 프로그램 비중 가운데 무엇이 경계 유량을 더 잘 설명하는지 비교한다. RQ3는 동선 분절에 따른 유량의 절대 수준 변화와 프로그램 반응 민감도의 변화를 구분한다. RQ4는 앵커 총량이 동일할 때 수직 배치별 상단 경계 유량비를 비교한다.

연구 대상은 1F부터 9F까지의 가상 9층·8개 경계로 제한한다. 시뮬레이션은 각 층을 선택할 확률과 이동수단 선택, 체류·퇴장 및 경계 통과를 계산하는 층 단위 비공간적 선택모형이다. 실제 건축물의 층별 평면, 매장 내부 보행 궤적, 아트리움 시야, 보행 혼잡과 임대 수익은 모형에 포함하지 않는다. 따라서 이 연구의 결과는 설정한 가상 조건에서의 비교이며, 실측 보행량으로 검증된 일반적 설계법칙으로 해석하지 않는다.

## 2. 이론적 틀과 연구질문

### 2.1 공간구조의 저항과 목적지 프로그램의 유인

자연 이동 이론은 보행분포를 이해할 때 공간구조의 연결 특성과 상업적·사회적 유인을 구분할 필요가 있음을 설명한다(Hillier et al., 1993). 다층공간에서는 이동 거리가 수평으로만 발생하지 않으며, 층간 이동수단과 환승·우회가 추가적인 선택 비용을 만든다(Chang & Penn, 1998). 한편 상업시설 이용자는 공간적 접근성뿐 아니라 방문하고자 하는 점포나 목적지의 매력에 반응한다. Huff(1964)의 상업 목적지 선택과 McFadden(1974)의 이산선택 접근, Borgers와 Timmermans(1986)의 소매 보행 선택모형은 이러한 선택을 효용의 차이로 이해하는 방법론적 배경을 제공한다.

본 연구는 이러한 이론을 직접적인 공간구문론 지표의 검증에 사용하지 않는다. 실제 가시성 그래프, 통합도, 연결도 또는 경로의 기하학적 형태를 계산하지 않았기 때문이다. 대신 공간구조는 층 간 이동비용과 수직동선 시나리오로, 목적지 유인은 층별 프로그램 비중에 곱해지는 효용계수로 단순화한다. 이 단순화는 두 조건을 명확하게 비교할 수 있다는 장점이 있지만, 실제 입체 상업공간의 복잡성을 표현하지 못한다는 한계를 가진다.

### 2.2 층 선택의 효용과 경계별 상행유량

가상 방문객은 먼저 이동할 목적지 층을 선택하고, 그곳까지 이동하는 데 필요한 수단과 비용을 고려한다. 높은 층이 목적지로 매력적일수록 선택 가능성이 커지지만, 이동거리나 환승·우회 비용이 늘면 그 선택은 불리해진다. 이 균형을 표현한 효용의 핵심 구성은 다음과 같다.

즉, 목적지 층의 기본 매력과 앵커 유인(γ × x)이 클수록, 그곳까지의 이동거리·환승·수단비용이 작을수록 해당 층을 선택할 가능성이 커진다. 방향에 따른 선택 편향도 모형에 포함된다.

여기서 γ는 목적성 앵커 비중에 부여하는 가정된 유인 강도로서 0, 2, 4, 8의 민감도 분석값이다. 실제 식당이나 영화관에서 추정한 선호계수가 아니다. 수직동선 조건은 에스컬레이터 이동에 수반되는 시간과 고유 불편 비용을 변경하는 별도의 축이다. 두 축을 독립적으로 설정해야 γ를 마찰계수처럼 해석하는 오류를 피할 수 있다.

이때 방문객은 바로 위층에만 이동하는 것이 아니다. 예를 들어 2F에 있는 방문객이 7F를 목적지로 선택했다면, 이동 중 통과하는 2F→3F부터 6F→7F까지의 상향 경계에 각각 통과 기록이 남는다. 따라서 특정 경계에서 집계한 상행유량에는 바로 위층을 방문하려는 이동과 그보다 높은 층을 향하는 이동이 함께 포함된다. 이 특성 때문에 인접층 간 프로그램 차이뿐 아니라 경계 위층의 유인 자체도 분석할 필요가 있다.

*[그림 1 — 최종 8쪽 PDF에 삽입된 실제 도판 참고]*

*Figure 1. Conceptual model of destination attraction, travel resistance and upward boundary crossings.*

### 2.3 경쟁 설명과 연구질문

인접층 사이의 프로그램 비중 차이가 상행 흐름을 유인한다는 가정을 먼저 설정할 수 있다. 경계 b의 바로 위층 앵커 비중을 x_upper, 아래층 비중을 x_lower라 하면 그 차이는 Δx_b = x_upper − x_lower로 나타난다. 그러나 방문객이 여러 층 위의 목적지를 직접 선택하는 구조라면, 상대적인 차이보다 경계 바로 위층의 앵커 비중(x_upper) 또는 경계 위쪽 층들의 평균 앵커 비중(M_above)이 유량과 더 밀접하게 연결될 수 있다. 본 연구는 이 세 지표를 경쟁적인 설명으로 비교한다. 이는 인접층 대비의 관련성이 전혀 없다는 가설을 미리 전제하는 것이 아니다.

세 지표는 유사해 보여도 답하는 질문이 다르다. 바로 위층 비중(x_upper)이 같아도 아래층 비중이 달라지면 인접층 차이(Δx)는 달라진다. 반대로 아래층이 같아도 경계 위의 여러 층에 프로그램을 나누어 두면 상층 평균(M_above)은 달라질 수 있다. 따라서 이 연구는 세 지표를 서로 대체하지 않고, 어떤 표현이 상향 경계 유량의 변동을 더 잘 설명하는지 비교한다.

**Table 1. Research questions, outcome measures and experiments**

| RQ | Target | Measure | Exp. |
| --- | --- | --- | --- |
| 1 | Baseline attenuation | U, AUFR, RUI | E1, g=0 |
| 2 | Program predictors | AUFR; U deviance | E1, g>0 |
| 3 | Circulation interaction | U1; slope erosion | E1 |
| 4 | Vertical allocation | T, R | E2 |

RQ1은 결과 해석의 기준선이며, RQ2가 논문의 중심적인 설명변수 비교, RQ3가 그 설명의 동선 조건, RQ4가 공간계획적 배치 시나리오에 해당한다. 이 연구질문들은 서로 독립적인 실험의 단순한 나열이 아니라, 동일한 선택모형 안에서 순차적으로 비교 범위를 넓히는 구조를 가진다.

## 3. 연구방법

### 3.1 모형의 공간적 범위와 행동 과정

분석 대상은 S00(1F)부터 S08(9F)까지의 가상 상업시설이며, 상향 경계는 b1(1F→2F)부터 b8(8F→9F)까지 8개다. 1F에 가상 주출입구를 두고, 각 경계에서 계단·에스컬레이터·엘리베이터 이용을 모형화하였다. 층별 면적의 기준값을 동일하게 유지했으며 운영일과 시간대의 기본 틀에는 별도로 구축된 두타몰 참고 템플릿의 일부 운영 프로파일을 사용했다. 실제 두타몰의 7개 판매층 단면이나 보행 실측자료를 9층 모형에 복제한 것은 아니다.

에이전트의 행동은 (1) 입장과 집단 생성, (2) 체류 및 퇴장 판단, (3) 층 목적지 선택, (4) 이동수단 선택, (5) 지나가는 경계별 상행 이벤트 기록으로 구분한다. 동일한 개인 또는 집단이 여러 차례 경계를 통과할 수 있으므로 경계 통과량의 총합은 고유 방문객 수와 일치하지 않는다. 모형의 시간·상태변수와 세부 처리 순서는 GAMA 소스와 실험계획서를 통해 추적할 수 있다. 모형 보고는 에이전트 시뮬레이션의 재현성을 위해 제안된 ODD 방식(Grimm et al., 2020)의 취지에 따라 목적·규칙·입력·출력·검증 범위를 구분해 정리하였다.

*[그림 2 — 최종 8쪽 PDF에 삽입된 실제 도판 참고]*

*Figure 2. Synthetic nine-floor structure and the locations of the eight upward boundaries.*

### 3.2 유인 강도와 동선 조건

E1에서 목적성 앵커는 층별 프로그램 비중 x_j로 입력되고, 유인 강도 γ는 0, 2, 4, 8의 네 수준으로 설정했다. γ=0은 앵커 비중에 의한 추가 효용만 제거하는 조건이다. 방문객의 체류·퇴장과 이동거리 비용 등 다른 행동 메커니즘까지 제거하는 조건은 아니므로, 그 결과를 ’동선 마찰만의 순수 효과’로 해석해서는 안 된다.

동선은 연속형(C_cont)과 분절형(C_frag)을 비교하였다. 연속형은 에스컬레이터 고유 불편 비용 1.0, 경계당 이동시간 25초로, 분절형은 고유 불편 비용 2.45, 경계당 이동시간 55초로 가정하였다. 이 설정값은 실측 보정치가 아니라 비교를 위한 모델 가정이다. 그 밖의 도착률·체류시간과 선택계수는 분석계획의 기준 파라미터로 고정했다.

각 반복의 프로그램 비중은 E1에서 0–0.5 사이의 균등분포로 생성했고, E2에서는 지정한 고정 비중을 사용했다. E2에서 S00(1F)의 x=.05는 고정하고 2F–9F의 앵커 비중 합계만 1.60으로 통제하였다. 전체 면적의 실제 임대 가능 비율을 계측해 20%로 고정했다는 뜻이 아니라, 동일한 크기의 가상 여덟 층에 대한 층별 프로그램 비중의 산술합을 통제한 것이다.

**Table 2. Experimental conditions and simulation replications**

| Cell | Conditions | Runs | Purpose |
| --- | --- | --- | --- |
| E1 | 4 attraction x 2 circulation | 8 x 200 = 1600 | RQ1-3 |
| E2 | 4 patterns x 2 circulation | 8 x 100 = 800 | RQ4 |
| Null | TOP1/UNI, g=0, continuous | 2 x 100 = 200 | Control |
| Total | 18 experiment cells | 2600 | 4 days/run |

**Table 3. Program allocation schemes in E2 (S00=1F)**

| Pattern | Shares on 2F-9F | Emphasis |
| --- | --- | --- |
| TOP1 | 9F .85; 2-8F .107143 | 9F |
| STEP3 | 3, 6, 9F .45; others .05 | 3/6/9F |
| UNIFORM | all 2-9F .20 | distributed |
| LOW3 | 2,3,4F .45; others .05 | 2/3/4F |

### 3.3 분석지표와 통계적 검증

본 연구의 기본 단위는 개별 방문객의 최종 도착 여부가 아니라, 특정 층간 경계를 위로 통과한 사건의 합계다. 반복실험 r의 경계 b에서 4일 동안 기록된 상향 통과량을 U(r,b)로 표기한다. 예를 들어 U(r,5)는 5F→6F를 위로 지난 인원 이벤트를 합산한 값이다. 같은 방문객이 두 번 통과했다면 두 번 기록될 수 있으므로 전체 입장객 수와 혼동하지 않는다.

층간 상행유량비 AUFR(r,b)는 바로 아래 경계와 비교한다. 즉 AUFR(r,5)=U(r,5)/U(r,4)는 5F→6F 통과량이 4F→5F 통과량의 얼마인지를 보여준다. 값이 0.60이라면 두 경계의 통과 이벤트 수를 비교할 때 위쪽 경계가 아래쪽의 약 60%라는 뜻이지, 한 사람이 다음 층으로 올라갈 확률이 60%라는 뜻은 아니다.

상대 상행유량 지수 RUI(r,b)=U(r,b)/U(r,1)은 각 경계의 통과량을 1F→2F의 첫 상향 경계와 비교한다. 최상단 지수 T는 RUI(r,8), 평균 지수 R은 RUI(r,2)~RUI(r,8)의 산술평균이다. T와 R은 모두 반복별 비율을 먼저 계산한 뒤 평균하며, 전체 방문객 중 최상층에 실제 도달한 고유 인원 비율로 해석하지 않는다.

분석 단계에서는 각 연구질문마다 종속변수가 다르다. RQ1에서는 γ=0인 기준조건의 U, AUFR, RUI를 층 높이에 따라 비교하고, log(U)가 단순한 직선처럼 감소하는지도 검정한다. RQ2는 두 갈래로 분석한다. 먼저 인접층 비중 차이(Δx)가 0.1 증가할 때 AUFR이 얼마나 달라지는지 확인한다. 이어서 경계 통과량 U를 설명할 때 Δx, 바로 위층 비중, 경계 위쪽 평균 비중 중 어느 지표가 더 많은 잔여 편차를 줄이는지 별도의 준포아송 회귀모형으로 비교한다.

RQ3에서는 먼저 두 동선에서 기본 통과량의 절대값이 얼마나 다른지 살펴보고, 다음으로 Δx에 대한 AUFR의 반응 기울기가 달라지는지 확인한다. 잠식률은 1−(분절형 기울기/연속형 기울기)로 정의한다. 이 비율이 0이라면 두 동선에서의 반응 크기가 같은 것이며, 양수라면 분절형에서 상대적으로 완만하다는 뜻이다. 2,000회 부트스트랩의 95% 신뢰구간이 0을 포함하는지도 함께 확인한다. RQ4에서는 동등한 앵커 총량의 네 배치에 대해 최상단 지수 T와 평균 지수 R을 비교한다.

## 4. 분석 결과

### 4.1 목적성 앵커 유인이 없는 기준상태의 감쇠(RQ1)

γ=0 기준조건에서도 상층 경계로 올라갈수록 상행 통과량이 감소하였다. 연속형의 4일 누적 U 반복 평균은 첫 경계에서 12,346회, 마지막 경계에서 448회였으며, 반복별 U8/U1의 평균은 3.63%였다. 분절형에서는 같은 지표가 9,802회 → 408회, 4.17%로 나타났다. 따라서 분절형은 첫 경계 통과량과 마지막 경계 통과량의 절대값 모두에서 연속형보다 작았지만, 분모가 다른 U8/U1 지수만 보면 분절형의 비율이 더 높았다. 이를 분절형 동선이 상층 이동에 더 유리하다는 근거로 해석해서는 안 된다.

*[그림 3 — 최종 8쪽 PDF에 삽입된 실제 도판 참고]*

*Figure 3. Mean four-day upward boundary crossings under neutral attraction (E1, n=200 per circulation condition).*

경계별 AUFR은 연속형에서 대략 0.60–0.67(2–7번째 경계)이고 8번째 경계에서는 0.517이었다. 그러나 이러한 감쇠는 단일한 로그-선형 법칙과 같지 않았다. 최대 로그 잔차가 연속형 0.131, 분절형 0.152로 사전 기준 0.10을 넘었으며, 경계별 효과를 허용한 모형과의 비교에서도 단일 선형 감소 가설이 지지되지 않았다. 따라서 결과는 ‘상층으로 갈수록 크게 감소하지만, 감쇠의 모양은 경계에 따라 달라진다’고 요약하는 것이 타당하다.

이 기준선은 프로그램 유인을 추가했을 때 무엇이 달라지는지 비교하는 출발점이다. 경계별 유량이 이미 높이에 따라 크게 감소하기 때문에, 단순히 위층이 아래층보다 매력적인지의 차이만으로 상행 흐름을 설명할 수 있는지 추가 검토가 필요하다. 다음 절에서는 인접층 차이가 AUFR과 관련되는지 확인하고, 경계 상행유량 자체를 가장 잘 설명하는 프로그램 지표를 비교한다.

### 4.2 인접층 대비와 상층 프로그램 지표의 설명력(RQ2)

인접층 프로그램 비중 차이 Δx와 상행유량비 사이에는 양의 관련성이 나타났다. E1·γ=4·연속형에서 Δx가 0.1 커질 때 AUFR의 추정 승수는 1.109배(95% 신뢰구간 1.104–1.115)였다. 따라서 인접층의 상대적 차이가 전혀 무관하다고 볼 수는 없다. 다만 이 값은 AUFR에 대한 연관성의 크기이며, 프로그램 지표들 사이의 설명력 비교와는 다른 분석 결과다.

그러나 AUFR의 변화와 실제 경계 통과량 U의 변동은 서로 다른 질문이다. 경계 위치와 반복실험 차이를 통제한 준포아송 기준모형에 프로그램 지표를 하나씩 추가하면, γ=4·연속형에서 바로 위층 앵커 비중(x_upper)은 기준모형의 잔여 deviance를 60.1% 줄였다. 경계 위쪽 평균(M_above)은 39.7%, 인접층 차이(Δx)는 10.2%였다. 이 비율은 비교한 모형의 설명력 지표이며, 앵커가 사람의 60.1%를 실제로 이동시켰다는 뜻이 아니다.

*[그림 4 — 최종 8쪽 PDF에 삽입된 실제 도판 참고]*

*Figure 4. Reduction in baseline residual deviance by adding each program predictor separately (E1, gamma=4, continuous).*

인접층 대비의 양의 연관성과 위층 앵커 비중의 더 높은 설명력은 모순되지 않는다. 방문객이 여러 층 위의 목적지를 직접 선택하는 모형에서, 경계 위층의 프로그램 비중은 그 경계를 지나는 상향 이동의 구조와 직접 연결된다. 본 결과는 기준조건 안에서 바로 위층 프로그램 비중이 세 구성개념 중 U 변동을 상대적으로 더 잘 설명한다는 사실을 보여준다. 다만 목적지 유인이 효용함수에 γ×x_j로 입력되었으므로 이 설명력의 우위는 부분적으로 모형의 설정에 의존하며, 독립적인 실물 인과법칙의 발견으로 확장할 수 없다.

이 순위는 관찰된 현실의 보행 인과관계를 그대로 발견했다는 의미와 구별해야 한다. 원래 모형이 목적지 층의 효용에 앵커 비중을 직접 반영하도록 설계되었기 때문에, 위층 프로그램 비중의 설명력이 상대적으로 높게 나타날 구조적 가능성이 있다. 또한 세 변수는 일부 정보를 공유하므로 각 설명률을 더해 전체 효과를 구할 수 없다. 본 연구의 기여는 이 가정 아래에서 세 지표를 동일한 분석조건으로 비교했다는 데 있다.

### 4.3 수직동선 분절과 프로그램 반응의 관계(RQ3)

동선 분절의 영향은 유량의 절대 수준과 프로그램 비중 변화에 대한 반응으로 구분할 필요가 있다. γ=0 조건에서 분절형의 첫 경계 평균 U1은 연속형의 약 79.4%였으므로, 기준 상행 통과량의 절대값은 약 20.6% 작았다. 반면 프로그램 대비 Δx에 따른 AUFR의 기울기가 줄어드는 정도는 γ 값에 따라 달랐다.

*[그림 5 — 최종 8쪽 PDF에 삽입된 실제 도판 참고]*

*Figure 5. Erosion in the program-response slope under fragmented circulation, with bootstrap 95% confidence intervals.*

γ=2의 추정 잠식률은 6.72%(95% CI 2.69–10.51%)로 신뢰구간이 0을 포함하지 않았다. 반면 γ=4는 0.77%(−4.11–5.22%), γ=8은 1.67%(−6.41–8.56%)로 두 조건 모두 0과 구분할 충분한 근거가 확인되지 않았다. 이 결과를 ’γ가 클수록 마찰이 작아진다’라고 해석해서는 안 된다. γ는 프로그램 유인 강도이고, 동선 마찰은 연속형·분절형 시나리오에서 변경한 별도 입력이다.

따라서 분절형 동선은 상향 경계 유량의 기본 수준을 낮추는 조건으로 나타났지만, 프로그램 비중 차이에 대한 반응까지 일률적으로 감소시키지는 않았다. γ=2에서는 반응 기울기의 유의한 감소가 확인되었고, γ=4와 8에서는 그 방향을 뚜렷하게 식별하지 못했다. 이는 마찰이 앵커의 집객 효과를 언제나 제거하거나 항상 보존한다는 단정이 아니라, 유인 강도에 따라 반응이 달라질 수 있다는 조건부 결과다. 다음 RQ4는 이 선택 반응을 전제로 같은 앵커 총량을 어디에 배치할지 비교한다.

### 4.4 동일 앵커 총량 아래 수직 배치 시나리오 비교(RQ4)

앞선 분석에서는 어떤 프로그램 지표가 경계 통과량과 더 긴밀히 연결되는지 확인했다. 다음으로는 사용할 수 있는 앵커 비중의 합계를 같은 수준으로 고정하고, 이를 층별로 어디에 배치하는지 비교했다. E2에서 2F~9F의 앵커 비중 합계는 모든 조건에서 1.60이다. 이때 TOP1·STEP3·UNIFORM·LOW3의 네 시나리오를 비교한 γ=4·연속형 결과에서, 최상단 대 첫 경계 유량비 T는 차례로 58.7%, 14.0%, 5.9%, 1.5%였다.

*[그림 6 — 최종 8쪽 PDF에 삽입된 실제 도판 참고]*

*Figure 6. Four equal-budget vertical program allocations and relative upper-boundary flow indices (E2, gamma=4, continuous).*

최상층 집중과 징검다리형의 T 차이는 약 0.447이었으며 사전 지정된 비교에서 통계적으로 구분되었다. 징검다리형의 T는 최상층 집중보다 낮았지만 균등 분산보다 약 0.082 높았다. 이는 징검다리형이 네 가지 시나리오 중 ’가장 효율적’이라는 뜻이 아니라, 최상층 집중과 균등 분산 사이의 중간 수준에서 상층 유량을 확보한 대안이라는 의미다. 또한 γ=0 대조군에서 균등형과 최상층 집중형의 T·R 차이가 뚜렷하지 않았으므로, 배치에 따른 차이는 모형에 프로그램 유인 강도가 부여된 조건과 연결된다.

배치 자체가 만들어 낸 차이인지 점검하기 위해 γ=0에서 균등형과 최상층 집중형을 비교한 대조실험도 수행했다. 목적성 프로그램이 효용에 더해지지 않는 이 조건에서는 T의 차이가 약 −0.000085(p=0.817), R의 차이가 약 −0.000063(p=0.914)으로 0과 구별되지 않았다. 따라서 γ=4에서 나타난 배치별 차이는 프로그램 효용을 부여한 모형 조건과 연결해서 해석해야 한다.

특히 TOP1의 9F 앵커 비중 0.85는 분석을 위한 강한 집중 시나리오다. 본 연구는 이러한 면적 구성이 실제 임대·피난·운영 조건에서 가능한지 또는 수익·혼잡을 포함한 종합 성과를 극대화하는지는 검토하지 않았다. 따라서 선정된 네 가상 배치 중 상향 경계 유량에 가장 유리한 조건과 현실의 종합적으로 최적인 건축계획을 명확히 구분해야 한다.

## 5. 논의 및 결론

### 5.1 연구 결과의 통합적 해석

본 연구의 결과는 하나의 순서로 연결된다. 먼저 프로그램의 추가 유인이 제거된 조건에서도 상행 경계 유량이 위층으로 갈수록 감소하였다(RQ1). 다음으로 인접층의 프로그램 비중 차이는 AUFR과 양의 관련성을 보였으나, 여러 층을 지나는 상향 이동의 크기를 설명할 때는 경계 바로 위층 앵커 비중이 세 구성개념 중 더 높은 설명력을 보였다(RQ2). 동선 조건을 분절형으로 변경하면 기본 상행유량의 수준은 낮아졌지만, 프로그램 관련 반응의 잠식은 γ 조건에 따라 달랐다(RQ3). 마지막으로 앵커 비중의 총합을 고정해도 층별 배치를 바꾸면 최상단 경계까지 이어지는 유량 분포가 달라졌다(RQ4).

이 네 결과는 ‘상층부로 가는 이동에 비용이 발생한다’는 사실에만 머무르지 않는다. 방문객이 어느 층을 목적지로 인지하고 선택하는가도 수직적 흐름을 설명하는 데 중요하며, 그 유인력을 어디에 배치하는가가 경계별 유량의 분포를 바꿀 수 있다는 것이 본 연구의 핵심이다. 그러나 이 해석은 어디까지나 목적지 효용을 γ×x_j로 설정한 모형 내부의 메커니즘에 관한 것이다. 모형이 공간구문론의 자연 이동 이론을 직접 실증했다거나 실제 상업시설의 설계 원칙을 증명했다고 주장할 수는 없다.

### 5.2 공간계획적 시사점과 결과의 적용 범위

가상 실험에서 얻을 수 있는 공간계획적 시사점은 세 가지로 요약된다. 첫째, 상층부 활성화를 논의할 때 단순히 인접층과의 프로그램 차이를 조절하는 것뿐 아니라 방문 목적지로 인지될 수 있는 상층 프로그램의 위치와 강도를 함께 고려할 필요가 있다. 둘째, 수직동선의 연속성은 기본 유량의 수준에 관계하므로, 프로그램만 강화한 채 이동 저항을 고려하지 않는 계획은 충분하지 않을 수 있다. 셋째, 앵커의 총량이 동일해도 층별 배치에 따라 유량 지표가 크게 달랐으므로 프로그램 수직 배치는 건축계획 초기부터 동선 시나리오와 함께 비교해야 할 의사결정 변수로 볼 수 있다.

이러한 결과를 설계에 적용할 때는 어떤 성과를 우선시하는지 먼저 구분해야 한다. 예컨대 최상단 경계까지 이어지는 흐름을 늘리는 목표에서는 TOP1 시나리오가 가장 높은 지수를 보였지만, 층별 점포의 균형, 공간 경험, 피난 또는 운영 비용을 동시에 최적화한 것은 아니다. 따라서 본 결과는 특정 배치의 정답을 지정하기보다, 수직동선 계획과 함께 여러 프로그램 배치의 효과를 비교해 보아야 한다는 근거로 사용해야 한다.

다만 최상층 집중형이 T와 R에서 가장 높은 것은 본 연구에서 설정한 네 배치, 효용함수, 마찰 가정, 앵커 비중에 관한 결과다. 중간층의 매출, 평면 내 혼잡, 임대료, 방재·피난, 공간의 시각적 연속성, 장시간 체류 등은 평가함수에 포함되지 않았다. 따라서 징검다리형을 ’균형이 가장 우수한 실무 대안’으로, 또는 최상층 집중형을 ’실제 설계의 최적해’로 단정하지 않는다. 실무 적용에서는 유량뿐 아니라 상업성과 혼잡 및 공간구성 목표를 함께 평가해야 한다.

### 5.3 연구의 한계와 후속 과제

본 모형의 가장 큰 한계는 층 단위 비공간적 선택모형이라는 점이다. 가상 방문객의 실제 XY 이동궤적, 상점별 입구, 에스컬레이터의 정확한 배치, 층간 보이드와 시야, 실내 혼잡에 따른 경로 변화는 계산하지 않는다. 따라서 건축 도면 수준에서의 동선 설계 검증이나 공간구문론 지표와의 직접 비교에는 사용할 수 없다. 실제 건축공간을 다룬 상업시설 연구에서는 가시성 기반 분석과 현장 관측을 결합하여 검증하기도 하므로(Zhong et al., 2024), 향후 연구에서는 관련 자료와 직접 비교할 수 있는 단계가 필요하다.

두 번째 한계는 γ, 이동 불편 비용, 앵커 비중 분포 등의 주요 입력이 현장 자료로 추정된 계수가 아닌 비교를 위해 설정한 가정치라는 점이다. 특히 최상층 집중형의 앵커 비중 0.85와 목적지 유인을 효용에 선형으로 더하는 규칙은 특정 시나리오의 결과를 증폭할 수 있다. 또한 모형 안에서는 프로그램 유인이 목적지 선택에 직접 들어가므로, 바로 위층 앵커 비중이 인접층 차이보다 설명력이 높았다는 결과를 실물 세계의 독립적인 인과법칙으로 옮겨 적을 수 없다.

세 번째 한계는 외부 검증의 부재다. 연구 코드에서 확인된 두타몰 참고 AUFR 수치는 기존 시뮬레이션 출력에서 계산된 값이므로 실제 두타몰의 계측값을 의미하지 않는다. 입장·퇴장 보존 검증은 실행 및 집계 오류를 점검하는 데 필요하지만, 관찰자료에 대한 적합성을 보장하지 않는다. 향후에는 실제 시설의 층간 이동 카운트, 방문 OD 자료, 공간의 수직 연결·가시성 데이터를 수집하여 γ와 동선 비용을 교정하고, 고유 방문객의 최상층 도달 확률과 경계 통과량을 서로 구분해 분석할 필요가 있다. 수직접근 요소와 아트리움의 공간 품질을 직접 검토한 기존 연구(Hosseini et al., 2024)는 이러한 확장 시 실제 공간구조를 별도로 다루어야 함을 보여준다.

후속 실증 단계에서는 최소한 같은 영업시간과 동일한 경계 위치에서 측정한 상·하행 통과 횟수, 방문객 도착·체류 특성, 층별 프로그램 비중, 수직 이동수단의 실제 이동·대기시간이 필요하다. 그 자료로 γ와 마찰 관련 계수를 보정하고, 보정에 사용하지 않은 날짜나 층의 유량을 얼마나 재현하는지 별도로 확인해야 한다. 그래야 가상의 민감도 결과를 실제 건축계획의 판단자료로 확대할 범위가 정해질 수 있다.

### 5.4 결론

본 연구는 가상 9층 상업시설에서 층간 상향 경계 통과량을 공통의 분석단위로 설정하고, 목적지 프로그램 유인과 수직동선 조건을 분리해 비교하였다. 그 결과 프로그램 유인이 없는 기준조건에서는 상향 흐름이 높이에 따라 크게 줄었고, 앵커 유인이 존재하는 조건에서는 인접층의 상대적 차이보다 경계 바로 위층 프로그램 비중이 상행유량의 변동을 더 잘 설명하였다. 또한 동일한 앵커 비중 합계에서도 수직 배치에 따른 최상단 경계 유량비의 차이가 나타났다.

본 연구에서 가장 중요한 판단은 두 조건을 따로 보지 않는 것이다. 상층부로 향하는 경계 통과량은 이동 저항의 영향을 받지만, 동시에 사람들이 선택할 목적지 프로그램이 어느 층에 있는지에도 민감하다. 따라서 상업시설의 프로그램 계획에서는 “위층에 무엇을 놓는가”와 “그 층까지 얼마나 수월하게 이동하는가”를 함께 검토할 필요가 있다. 다만 이 연구는 가상 조건 사이의 유량비를 비교한 것이므로, 그 순위를 실제 시설의 매출·공실·보행 만족도를 포함한 최적 설계의 증거로 해석할 수는 없다.

## References

Borgers, A., & Timmermans, H. (1986). A model of pedestrian route choice and demand for retail facilities within inner-city shopping areas. Geographical Analysis, 18(2), 115–128. https://doi.org/10.1111/j.1538-4632.1986.tb00086.x

Chang, D., & Penn, A. (1998). Integrated multilevel circulation in dense urban areas: The effect of multiple interacting constraints on the use of complex urban areas. Environment and Planning B: Planning and Design, 25(4), 507–538. https://doi.org/10.1068/b250507

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. Journal of Artificial Societies and Social Simulation, 23(2), 7. https://doi.org/10.18564/jasss.4259

Hillier, B., Penn, A., Hanson, J., Grajewski, T., & Xu, J. (1993). Natural movement: Or, configuration and attraction in urban pedestrian movement. Environment and Planning B: Planning and Design, 20(1), 29–66. https://doi.org/10.1068/b200029

Hosseini, Z., Yeganeh, M., & Jalali, S. (2024). Exploring the impact of vertical access elements on visual richness and space quality within shopping mall atriums. Buildings, 14(9), 2724. https://doi.org/10.3390/buildings14092724

Huff, D. L. (1964). Defining and estimating a trading area. Journal of Marketing, 28(3), 34–38.

Kwon, Y., & Kim, D. (2025). 에이전트 기반 시뮬레이션을 활용한 지하도상가 평면구조 유형별 보행 성능 분석 및 최적화 방안 연구. 한국실내디자인학회 논문집, 34(6), 9–26. https://doi.org/10.14774/JKIID.2025.34.6.009

McFadden, D. (1974). Conditional logit analysis of qualitative choice behavior. In P. Zarembka (Ed.), Frontiers in Econometrics (pp. 105–142). Academic Press.

Zhong, Y., Tan, Z. S., Mavros, P., Hölscher, C., & Tunçer, B. (2024). Estimating relative pedestrian crowd distribution: A visibility-graph-based analysis workflow for malls during early design stage. In Proceedings of the 42nd eCAADe Conference (Vol. 2, pp. 433–442).