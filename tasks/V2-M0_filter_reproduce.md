# V2-M0 헤더 확인 · 1차 반출 필터 재현 · 필터 정의 기록

> 상위: [README.md](README.md) · 근거: 방문 계획 §4 M0, 결과 문서 §1·§6(Q1·Q3·Q4) · 의존: V2-00
> 현장 소요 목표: **20분**

## 1. 목적

1차 반출물(`t_month.csv` 339,713건)이 **어떤 필터로 나왔는지 코드로 재현하고 기록**한다. 재현되지 않으면 이후 모든 급식 수치의 정의가 흔들리므로, M1~M4보다 먼저 돌린다.

## 2. 스크립트

### 2.1 `00_headers.py`
- 결제·가맹점 파일 각각: 감지된 인코딩, 실제 헤더 목록, 앞 3행(**internal에만**), 파일 크기.
- 설정의 활성 매핑과 대조: 논리명별 `OK` / `MISSING`.
- 콘솔 출력 + `internal/headers.txt`. 매핑이 하나라도 `MISSING`이면 종료 코드 1.

### 2.2 `10_m0_reproduce.py`

**기준값**: 1차 반출물 두 표를 `analysis/visit2/reference/export_0911_month.json`, `export_0911_week_hour.json`에 넣는다(설정 `reference_exports`). 저장소의 `9_11_데이터분석결과물/t_month.csv`·`t_week_hour.csv`에서 값을 그대로 옮긴다(수치 생성 아님, 복사). 빈칸(억제)은 `null`, 행이 없는 요일×시는 넣지 않는다. 요일 `와`는 `화`로만 교정한다. 이 파일 반입 가능 여부는 센터 확인 사항 `[ASK]` — 반입 불가 시 기준값 없이 표만 만들고 비교 단계는 건너뛴다.

**계산** — 결제 파일 1회 순회로 아래 조합을 모두 집계한다.

| 축 | 값 |
|---|---|
| 급식 값 집합 | 설정 `meal_pay_values` (M1 전에 돌릴 경우를 위해 `--meal-values "값1,값2"` 인자 허용) |
| 상태 필터 | `all` / `complete_only` / `exclude_cancel` 세 가지 **전부** |
| 기간 | 제한 없음(전체) |

각 조합별로:
- `m0_month_<status>.csv`: `ym, n, n_shop, n_cust` (1차 `t_month`와 같은 구조)
- `m0_dow_hour_<status>.csv`: `dow, hour, n, n_shop, n_cust` (1차 `t_week_hour`와 같은 구조, 요일은 숫자로 계산 후 라벨)

**비교** — 기준값이 있으면 조합별로:
- 월별 `n`·`n_shop`·`n_cust` 차이, 완전 일치 월 수 / 25
- 총합 차이
- `dow_hour` 총합 vs `month` 총합 차이(1차에서 11건이었던 값의 재현 여부)

→ `internal/m0_reproduce_compare.csv`, 콘솔에 **조합별 한 줄 요약**:
`status=complete_only  월 일치 25/25  총합 차 0  n_shop 일치 25/25  n_cust 일치 25/25`

**무엇을 export하는가**
- 일치하는 조합이 **정확히 하나**면:
  - `export/m0_month.csv` — 1차 `t_month`와 같은 값이므로 새 정보는 없다. **공개 합계 등록부에 월별·전체 합계를 올리는 용도**로 export한다.
  - `export/m0_dow_hour_night.csv` — **1차 `t_week_hour`의 대체본이 아니라 공표용 교정본**이다(방문 계획 §9 A1). `night_bucket`으로 23~05시를 한 칸으로 합치고, `zero_policy="mask"`, `known_totals`에 `m0_month` 전체 합계와 `reference_exports`를 넣어 노출 점검을 통과시킨다. 기획서의 요일×시간 히트맵은 이 표로 그린다.
  - **시간 단위(24칸) 요일×시 표는 export하지 않는다.** 1차 표에서 이미 억제 칸 값이 복원되므로 같은 해상도를 다시 내지 않는다.
  - `filter_definition.txt`에 "1차 반출 재현 조합: …" 기록.
- 일치 조합이 **없거나 둘 이상**이면: export하지 않는다. 콘솔에 `재현 실패` 또는 `재현 조합 불확정`을 출력하고 종료 코드 2. 사람이 판단한다.

**추가 점검** (internal만)
- `time_invalid` 행 수, 급식 행 중 `time_invalid` 수
- 급식 행의 `card_pay_gbn` 값 분포, `dest_pay_gbn` 값 분포
- `n_shop`이 `nunique(shop_id)`, `n_cust`가 `nunique(cust_id)`임을 코드 주석과 `filter_definition.txt`에 명시

## 3. 테스트

- 픽스처에서 상태 필터 3종의 월별 기대값을 손으로 계산해 검증.
- 기준값 JSON을 픽스처의 한 조합에 맞춰 만들고, 그 조합만 `25/25`(픽스처 월 수 기준 전부) 일치로 판정되는지 확인.
- 일치 조합이 둘인 경우 종료 코드 2.
- export 폴더에 24칸 요일×시 표가 없고, `m0_dow_hour_night`의 시간 키가 `06`~`22`와 `23-05` 18칸인지.
- 1차 반출물과 같은 구조의 픽스처(억제 칸 합이 억제 칸 수 + 1)를 넣었을 때 `m0_dow_hour_night`가 노출 점검을 통과하는지.

## 4. 완료 기준

- [ ] 합성 데이터(영문·한글 헤더 각각)로 `00_headers.py` → `10_m0_reproduce.py` 실행 성공
- [ ] 요일 라벨이 `월~일`, 수치 열이 정수로 저장
- [ ] 재현 실패 시 export 폴더에 급식 수치 표가 생기지 않음
- [ ] 완료 보고에 현장 실행 명령어 2줄 포함
