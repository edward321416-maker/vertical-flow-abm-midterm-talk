# 연구방법 시각자료: 실제 GAMA GUI 실행 화면 캡처 — 2026-11-03

**판정: SELECTED / NOT YET CAPTURED / 별도 화면 구성 필요**

## 사용자 의도
- 직접 제작하는 PPT에 넣을 **실제 GAMA 프로그램 실행 화면**이 필요하다. AI 생성 대시보드나 Blender 렌더링이 아니라, 네 논문의 모형을 실행하는 GAMA 화면이어야 한다.
- GAMA 공식 모델 스크린샷은 **UI 참고용**이고 사용자 논문의 실험 증거로 제시하지 않는다.
- 기존 2400×1350 CSV 재구성 다이어그램은 실제 GAMA 캡처가 아니므로 본 요구의 최종 산출물이 아니다.

## 원자료/코드 확인
- `simulation/vertical_flow.gaml` SHA `21ec0dba06f1ec460f37d7825e5fb1ae1afacc54`, 708–711행: `experiment headless_run type: gui { parameter "cell_file" var: cell_file; parameter "rep_id" var: rep_id; }`. **output/display/monitor가 아직 없음.** `type: gui` 키워드만으로 시각화 장면을 자동 제공하지 않는다.
- `simulation/README.md`에 따르면 실제 실험은 사용자 Windows `D:\\tools\\GAMA_2025.06.4\\headless\\gama-headless.bat` 및 XML 플랜 기반 헤드리스 배치 실행을 사용했다. 현재 프로젝트 결과는 그때 저장된 CSV이고 **실행 당시 뷰포트 스크린샷이 기록되었다는 근거는 없음**.
- 모형은 비공간적 층 단위 nested-logit. 층의 좌표/실제 3D 경로가 없는 모델이므로 GUI 화면도 **9개 층 밴드와 8개 경계 이벤트를 도식으로 표시**해야 한다. 에이전트를 실제 3D 공간에서 추적했다고 오인시킬 보행자 궤적, 공간 렌더, 실제 두타몰 층별 도면은 금지.
- 공식 GAMA 2025-06 GUI 문서 `https://gama-platform.org/wiki/DefiningGUIExperiment`: GUI `experiment`에 `output`을 정의하여 `display`, `monitor`와 `layout`을 지정할 수 있다.
- 실제 프로그램 예제 화면 `https://gama-platform.org/wiki/ContinuousMove` (3D 에이전트) 및 `https://gama-platform.org/wiki/comparison_ABM_EBM_SIR` (에이전트 분포와 그래프 나란히) 참고. 둘 다 **사용자 논문 실행 장면이 아님**.

## 권장 실제 캡처 구성(연구 코어는 유지하고 표시만 추가)
1. 기존 `headless_run`은 **연구 재현용으로 보존**한다. 시각화용 GUI experiment를 별도 정의하거나 병렬 시각화 스크립트를 분리한다. 실험 결과값이 바뀌지 않도록 설정/seed/입력/출력을 구분한다.
2. GAMA 프로그램을 **Windows에서 실제로 실행**하고, 연구의 cell/rep 파라미터와 `GAMA 2025.06.4` 버전 확인.
3. GAMA 내 레이아웃:
   - 좌측: `cell_id`, `rep_id`, `gamma`, `circ`, 가상 날짜와 실행 상태 등 **실제로 읽힌 파라미터**만 표시.
   - 중앙: `S00=1F ... S08=9F`의 층별 단순 그래픽. 에이전트는 층별 집계 또는 층 상태를 점/막대로 표현하고, 실제 X/Y 보행 좌표가 없다는 주석 표시.
   - 오른쪽: 8개 경계별 상행 이벤트 수 `U_b` 차트와 모니터. 특정 실행의 live event 값과 200회 반복 CSV 평균값은 **반드시 별도 라벨**로 분리.
   - 상단 GAMA의 **진짜 프로그램 툴바/실행 탭**은 보존, 화면 합성으로 가짜 인터페이스 만들지 않음.
4. 녹화 또는 화면 캡처에는 실험 조건, 시드, 실행 날짜, 실제 타임스텝이 확인되어야 하며, 수치는 기록된 crossing truth와 대조한다. GAMA 공식 Display toolbar의 snapshot 기능은 모델 폴더의 `snapshots`에 PNG로 저장할 수 있다 (공식 Displays 가이드).
5. 발표 화면에는 GAMA 캡처 **원본 16:9 화면을 통째로 넣기보다 중앙 뷰포트 중심으로 크롭**하되, 실제 프로그램의 타이틀 바/툴바 일부가 남도록 한다. 캡션: **"GAMA 2025.06 · 층 단위 에이전트 시뮬레이션 실행 화면"**. 캡처가 실제로 생성된 뒤에만 이 캡션 사용.
6. 기존 결과 CSV를 외부 그래프에 추가하는 경우, 캡션으로 **"기존 E1 시뮬레이션 200회·4일 합산 유량의 반복 평균"**을 명확히 표시하고 단일 실시간 프레임의 결과로 오인시키지 않는다.

## 다음 실무 단계
- **실제 연구 모형에 표시 기능이 없어 UI 자체를 구체적으로 추가·검증해야 한다.** 사용자 Windows의 GAMA가 접근 가능한 환경에서 새 표시-only GUI experiment 생성 → 컴파일/실행 확인 → PNG 캡처 → 실제 `cell_id` / 집계 이벤트 재대조.
- 현 세션은 Windows GAMA GUI 원격 접근이 없으므로, 진짜 연구 화면을 현재 캡처했다고 주장할 수 없다.
- 논문 모델이나 기존 결과를 바꾸는 일은 연구방법 재설계이므로 피하고, 별도 표시용 기능을 구축하는 것을 우선한다.
