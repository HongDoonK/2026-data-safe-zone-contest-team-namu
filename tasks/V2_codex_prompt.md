# Codex 프롬프트 — 2차 방문 코드 전체 (V2-00 + V2-07 단계 A + M1·M0·M3·M2·M4)

> 작성: Claude, 2026-09-18. 아래 코드 블록 전체를 Codex에 한 번에 붙여넣는다.
> 이전에 따로 드린 두 프롬프트(V2-07 단계 A / V2-00~M4)를 합친 것이다. **둘 중 하나를 이미 넘겼다면 이 파일은 쓰지 않는다.**

```text
너는 이 저장소의 구현 담당(Codex)이다. 이번 작업은 2차 안심구역 방문(9/22~23)에서 실행할 코드 전체를 구현하는 것이다.
범위(이 순서): tasks/V2-00_common_infra.md → tasks/V2-07_export_check.md의 "단계 A" → V2-M1 → V2-M0 → V2-M3 → V2-M2 → V2-M4.
기한: 2026-09-21. 이 코드는 팀원이 인터넷이 차단된 안심구역 PC에 반입해 실데이터(결제 약 788만 행, 616MB)에 실행한다.
너는 실데이터를 볼 수 없다.

[먼저 읽어라 — 다 읽기 전에는 코드를 쓰지 마라]
1. AGENTS.md — 작업 규칙 전체 (특히 §2 환경, §4 절대 규칙)
2. tasks/README.md — 디렉터리 구조, 공통 규칙 1~7
3. tasks/V2-00_common_infra.md — 전체 (특히 §2 설정, §3.6 노출 점검 억제, §3.7 write_export 거부 조건)
4. tasks/V2-07_export_check.md — 전체. §1.5(단계 A/B 구분, V2-00과 공유하는 함수)를 먼저 본다
5. tasks/V2-M1_paygbn_meaning.md, V2-M0_filter_reproduce.md, V2-M3_shop_join.md, V2-M2_comparison_h1.md, V2-M4_spatial_publishability.md
6. docs/topics/T2_visit2_plan.md — §4(모듈 목적), §9 A1·A2·A3·A10, §10.3(현장 진행표: 모듈별로 쓸 수 있는 시간)
7. docs/topics/T2_export_0911_results.md — §1, §6 Q2
8. docs/topics/T2_child_meal_card.md — §1.2·§1.5(컬럼), §1.10(실측: 헤더 한글 가능, 전 컬럼 VARCHAR, 결제수단 값이 정의서와 다름), §7.2(억제 규칙)
9. 9_11_데이터분석결과물/t_month.csv, t_week_hour.csv — 실제로 열어서 구조를 확인

[현재 상태]
- analysis/, tests/, synthetic/ 폴더가 아직 없다. 모든 코드를 새로 만든다.
- 함수·파일 이름과 시그니처는 명세 그대로 쓴다. 특히 lib/suppress.py 의 exposure_ranges(S, k, lo, hi)는
  suppress()와 export_check.py가 함께 쓰는 단일 구현이다. 두 곳에 따로 만들지 마라.

[진행 방식 — 단계 관문]
단계 0: V2-00 공통 기반(lib/ 전체, config/visit2.json, selfcheck.py) + 합성 데이터 생성기(synthetic/visit2/make_synthetic.py)
단계 1: V2-07 단계 A (export_check.py, reference/ JSON 3개) — 단계 B(C8 전파)는 만들지 않는다
단계 2: M1 (20_m1_paygbn.py)
단계 3: M0 (00_headers.py, 10_m0_reproduce.py)
단계 4: M3 (40_m3_shop.py)
단계 5: M2 (30_m2_compare.py)
단계 6: M4 (50_m4_space.py, promote_internal.py)
단계 7: run_all.py + 전체 end-to-end

각 단계는 아래 [반복 검증]을 "한 바퀴 수정 없이 통과"해야 다음 단계로 간다.
- 단계 0 또는 단계 1이 통과하지 못하면 전체를 멈추고 보고한다(이후 모든 모듈이 억제 함수와 반출 점검에 의존).
- 그 외 단계가 통과하지 못하면 그 단계를 "미완"으로 기록하고, 그 단계에 의존하지 않는 다음 단계는 계속한다.
  의존: M0←M1(급식 값 설정), M3←M0, M2←M0, M4←M3. 합성 데이터에서는 설정값을 직접 채워 의존을 풀어도 된다.

[반드시 지킬 것]
- Python 3.8 호환, 표준 라이브러리 + pandas + numpy만. 네트워크 호출 없음. YAML 금지(JSON 설정).
- 입력 CSV는 dtype=str, keep_default_na=False, strip, usecols + chunksize. 모듈당 결제 파일 순회는 1회가 목표.
- 컬럼명·경로·급식 값·필터는 전부 config/visit2.json에서 받는다. '아동급식카드' 같은 값을 하드코딩하지 마라.
- export/에 쓰는 모든 표는 suppress()와 write_export()를 통과한다. 우회 경로를 만들지 마라.
- 억제는 V2-00 §3.6의 노출 점검 방식이다. "억제 칸이 1개면 하나 더" 같은 단순 규칙으로 대체하지 마라.
- 기본 zero_policy="mask". M1의 T1-b만 "show" 예외(명세 §3의 구간 표기 처리 포함).
- 급식 시간 단위 export 표는 23~05시를 night_bucket으로 합친다. 비중(share_*) 열은 export하지 않는다
  (M4 T4-b의 share_meal·lq는 명세대로 예외).
- export 표의 키 축은 max_axes(3) 이하. M2는 명세대로 G별 파일로 나눈다.
- export 어디에도 원자료 가맹점·고객 ID, p99·최댓값, p값을 넣지 않는다.
- 요일은 숫자(0=월)로 계산하고 라벨은 출력 직전에 DOW_LABELS로만 붙인다.
- reference/export_0911_month.json, export_0911_week_hour.json은 9_11_데이터분석결과물의 CSV 값을 그대로 복사한다.
  빈칸은 null, 없는 행은 넣지 않는다, 요일 '와'만 '화'로 교정한다. 계산·보정·반올림 금지.
  reference_meta.json은 V2-07 §1.5의 JSON 그대로.
- export_check.py의 리포트·콘솔에는 억제 칸의 실제 값을 쓰지 않는다(좁혀진 범위만). C8-lite 대조는 n 열만 한다.
  1차 반출물 자체의 노출은 KNOWN, 이번 표가 그 범위를 더 좁히면 FAIL. 자동 수정은 하지 않는다.
- 합성 데이터는 synthetic/visit2/ 와 tests/visit2/fixtures/ 에만, 파일명에 SYNTHETIC. 형식만 맞추고 실제 같은 분포를 만들지 마라.
  9_11_데이터분석결과물/ 은 읽기만 한다.
- 결과 해석 문장, 기획서 문구, 판정 자동화(급식 값 자동 선택, K1~K5 결정)를 만들지 마라.
  스크립트는 판정 재료와 사전 등록 규칙의 기계적 적용만 출력한다.
- 명세가 모호하거나 충돌하면 추측으로 메우지 말고 "확인 요청"에 적은 뒤, 더 적게 공개하는(보수적인) 쪽으로 구현한다.
  특히 M4 §3 2단계의 단위 비교 순서와 L1 분리 규칙은 명세대로 구현하되 확인 요청에 반드시 포함한다.

[반복 검증 — 각 단계마다]
한 바퀴:
 1. 테스트: pytest tests/visit2 -q (이전 단계 테스트 전부 포함 — 회귀 확인), python analysis/visit2/selfcheck.py
 2. 소형 픽스처 실행: 손계산 가능한 수십 행 픽스처로 해당 단계를 실행하고 결과가 손계산과 일치하는지 확인
 3. 대형 합성 실행(단계 2~7): synthetic/visit2/ 의 약 200만 행 결제 파일(영문 헤더판, 한글 헤더판 각각)로 실행.
    소요 시간과 최대 메모리 기록
 4. 적대적 입력: 아래 단계별 목록을 fixtures로 만들어 각각 실행하고 기대 판정 확인
 5. 반출 점검(단계 2~7): 그 단계의 export 폴더에 export_check.py를 실행해 FAIL 0 확인
 6. 환경 점검: 서드파티 import(pandas·numpy 외) 없음, 3.8 불가 문법(:=, match, X|Y 타입, dict | dict) 없음을 grep으로 확인

한 바퀴에서 문제가 하나라도 나오면 고치고 1부터 다시 돈다. 단계당 최대 6바퀴.

단계별 적대적 입력 (기대 판정):
 단계 0 (V2-00)
  a. 패딩 공백 값, 빈 문자열, 9자리·문자 섞인 시각 → strip 후 매칭, time_invalid 표시되고 행 유지
  b. 한글 헤더 CSV를 active="en"으로 실행 → 매핑·실제 헤더를 담은 오류로 중단(크래시 아님)
  c. cp949 인코딩 CSV → detect_encoding이 찾아 정상 실행
  d. 같은 고객이 청크 경계 양쪽에 있음(chunksize=3) → 고유 수 1
  e. exposure_ranges: (S=11,k=10,lo=1,hi=4) → 각 칸 [1,2] / (S=11,k=10,lo=0,hi=4) → [0,4] 유지 /
     (S=11,k=3,lo=0,hi=4) → [3,4] / (S=0,k=3,lo=0,hi=4) → [0,0] / (S=12,k=3,lo=0,hi=4) → [4,4] / k=1 → [S,S]
  f. 그룹의 모든 칸이 억제됐는데 합계 알려짐 → unresolved → write_export 거부
  g. status 없는 표, unresolved 있는 표 → 거부 / 4축 표(예외 false) → split_axis로 분할
  h. 2024-09-16~22 → 요일 월~일, 출력 어디에도 '와' 없음
  i. mask에서 0 칸과 억제 칸의 export 값·status가 완전히 같음
  j. meal_pay_values가 자리표시자 → M1 외 모듈 로드 시 즉시 오류
 단계 1 (V2-07 단계 A)
  a. 1차 반출물 두 표만 입력 → FAIL 0, t_week_hour 억제 10칸이 KNOWN이고 각 칸 범위 [1,2], 종료 코드 0
  b. 1차 표 + 금요일 23시 한 칸만 공개된 새 표 → FAIL (KNOWN 범위를 더 좁힘)
  c. 1차 표 + 심야를 23-05 한 칸으로 합친 mask 표 → FAIL 0
  d. 가명 ID 형식 문자열이 셀 값에 / 열 이름에 섞인 표 → 각각 C2 FAIL
  e. dong 키가 있는 4축 표 + time_only_axes_exception=true → C5 FAIL
  f. status 열 없음, .meta.json 없음, 허용 외 status 값 → C3 FAIL
  g. 급식 표에 23시 개별 칸 → C6 FAIL
  h. 빈 export 폴더, 깨진 CSV(열 수 불일치), cp949 CSV → 크래시 없이 명확한 FAIL 메시지
  i. 리포트·콘솔 grep → 억제 칸 실제 값·합성 ID 문자열 0건
 단계 2 (M1)
  a. SYN_MEAL_A(~2023-05) → SYN_MEAL_B(2023-06~) 전환 + 공통 고객 → T1-c에 gap 1, overlap 기대값
  b. 총 7건 희귀 값 → T1-b 노출 → T1-a 구간 표기 → 재점검 통과
  c. meal_pay_values 미설정 → 1~3단계 실행, 4단계 건너뜀 메시지
  d. 분기 반례(N=100000, N_SHOP=500, MONTHS=18) → branch_count_true=0, "규칙상 미정"
  e. N_SHOP이 월별 최대와 전 기간 고유가 다른 픽스처 → 전 기간 고유값 사용
 단계 3 (M0)
  a. 상태 필터 3종 중 하나만 기준값과 일치 → export 생성, 조합 기록
  b. 일치 0개 / 2개 → export에 급식 수치 표 없음, 종료 코드 2
  c. reference JSON 없음 → 비교 건너뛰고 표만 생성
  d. export에 24칸 요일×시 표 없음, m0_dow_hour_night 시간 키 18칸
  e. 1차 구조 픽스처(억제 칸 합 = 억제 칸 수 + 1)를 known_totals로 → 노출 점검 통과
 단계 4 (M3)
  a. 가맹점 테이블 중복 SHOP_ID → 결합 제외, dup_id_excluded_shops 기대값
  b. 결제에만 있는 가맹점 → child_able=<NOT_IN_TABLE>
  c. 분모 0 → 비율 NaN(0 아님) / 분자·분모 3 미만 → 비율 NaN
  d. 급식결제 가맹점 49곳 → T3-c 전부 NaN / 50곳 → 값 생성
  e. '비산1동' → ends_with_digit_dong 포함, '비산동' → 미포함
  f. export 폴더 전체에서 합성 ID 문자열 grep → 0건
 단계 5 (M2)
  a. 가맹점 3곳(2곳 both-shop, 1곳 급식만) → T2-c에서 급식만 가맹점 제외
  b. 행 수: T2-b meal 378, general 504, T2-c 각 48 (0 채움)
  c. 급식 시간 표에 23·0~5시 개별 칸 없음, share_* 열 없음, 모든 export 3축 이하
  d. 부트스트랩: 가맹점 1곳 → CI 폭 0 / seed 고정 두 번 실행 → 동일 / n_shops_used<30 → CI NaN
  e. cramers_v: 독립 표 → 0, 완전 연관 2×2 → 1
  f. T2-f: 일반·급식 모두 01~05시 0건 규칙 심음 → days_with_any 0 양쪽 / 일반만 심야 결제 → 일반만 >0
  g. T2-a meal 월별 값이 m0_month와 다른 픽스처 → internal에 차이 기록, population 메타 구분
  h. bootstrap.reps=200으로 바꿔도 정상 동작(현장 시간 부족 대비)
 단계 6 (M4)
  a. 사다리 L1~L5 통과율 손계산 일치, cells_total에 0 칸 미포함
  b. 모의 통과율 {L1:0.5, L2:0.92, L4:0.95, L3:0.97, L5:0.99} → L2 선택 / 전부 0.9 미만 → "none"
  c. L1 선택 → T4-b 두 파일로 분리, 어떤 표도 4축 아님
  d. 동명 이의어(중구|대신동, 서구|대신동) → 별도 칸
  e. 모든 동 급식 비중 동일 → lq=1
  f. T4-a 공개 후 T4-b 동 칸이 군구 합계로 좁혀지는 픽스처 → 추가 억제 또는 거부
  g. G1 표에 건수 절댓값 열 없음 / promote_internal.py 사유 없이 실행 → 거부
 단계 7 (end-to-end)
  a. run_all.py를 합성 데이터(영문·한글 헤더 각각)로 처음부터 끝까지 → 모든 모듈 성공, export_check.py FAIL 0
  b. 중간 모듈이 실패하도록 설정 오류를 심음 → run_all이 그 단계에서 멈추고 이후 모듈 미실행, 오류 메시지 명확
  c. 200만 행 기준 모듈별·전체 소요 시간이 현장 진행표(§10.3) 시간 안에 드는지 기록. 모듈별 10분 초과면 원인과 개선안 보고

반복할 때 지킬 것:
- 테스트를 통과시키려고 기대값·테스트·명세 기준을 바꾸지 마라. 기대값이 틀렸다고 판단되면 고치지 말고
  근거와 함께 "확인 요청"에 적는다.
- 실패를 try/except로 삼키지 마라. 예외는 명확한 메시지와 0이 아닌 종료 코드로 드러나야 한다.
- 새로 발견한 실패 유형은 먼저 fixtures에 테스트로 추가한 뒤 고친다.
- 명세 밖 기능(V2-07 단계 B, M5·M6, 그림, 해석, 자동 판정)은 반복 중에도 추가하지 않는다.
- 성능 문제로 명세의 계산 방식을 바꿔야 한다면 바꾸지 말고 확인 요청에 적는다
  (청크 크기·집계 순서 같은 구현 세부는 조정 가능).

[완료 보고 형식]
1. 단계별 상태: 완료 / 미완(남은 실패와 원인 추정) / 미착수
2. 단계별 반복 기록: 바퀴마다 발견한 문제 → 수정 내용 (마지막 바퀴는 "수정 없이 통과" 명시)
3. 단계별 적대적 입력 판정표 (항목마다 기대 / 실제)
4. 성능: 모듈별 소요 시간·최대 메모리 (200만 행 합성, SYNTHETIC 표시)
5. 생성·변경 파일 목록
6. 현장 실행 명령어: 모듈별 1줄 + run_all 1줄 + export_check 1줄 + 설정 파일에서 현장에서 고칠 키 목록
   + export_check FAIL이 나왔을 때 대처 3줄
7. Claude 리뷰용 요약 (각 5줄 이내):
   - exposure_ranges 식과 suppress()의 노출 점검·보완 억제 알고리즘
   - known_totals / 공개 합계 등록부가 모듈 사이에 전달되는 방식
   - export_check C8-lite 대조 방식
   - M2 가맹점 블록 부트스트랩 구현
8. 확인 요청 (M4 단위 비교 순서·L1 분리 규칙 포함)
9. V2-07 단계 B로 미룬 것 목록
10. 반입 목록: analysis/visit2/ 아래 반입할 파일 전체 경로 (tests·synthetic 제외)
```
