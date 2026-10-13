# V2-M2 비교군 — 급식 vs 일반 결제, 학기/방학 분리, 가맹점 내 대조 (H1)

> 상위: [README.md](README.md) · 근거: 방문 계획 §4 M2, 설계서 §3.2 H1·§4.3·§7.2 R-8, 결과 문서 §5 H1·§8 요청 2·3, 레드팀 R17 · 의존: V2-00, M0(상태 필터 확정), M1(급식 값 확정)
> 현장 소요 목표: **90분**

## 1. 목적

H1의 핵심 — **"급식카드 결제의 시간 분포가 일반 결제와 다른가"** — 을 검정할 집계를 만든다. 가게 구성 차이를 제거한 **가맹점 내 대조**와, 반복 이용을 반영한 **가맹점 블록 부트스트랩 CI**를 포함한다.

> 레짐(학기/방학/전환) 분리는 방문 계획이 **기술 층화**로 사용하는 것이다. 결과 문서 D2(모든 분석의 레짐 층화)의 채택을 뜻하지 않는다.

## 2. 정의

| 기호 | 정의 |
|---|---|
| 모집단 | 결제 행 중 `status_filter`(M0에서 확정한 조합) 통과, `period` 안(기본 2023-06~2025-06), `time_invalid=False` |
| `G` | `meal`: `meal_pay_values`에 일치 / `general`: 그 외 모든 값 (빈 값 포함 — 빈 값 행 수는 internal에 별도 기록) |
| `R` | `assign_regime()` 결과 |
| `daytype` | `weekday`(월~금) / `weekend`(토·일). 공휴일 미반영 — `filter_definition.txt`에 명시 |
| `hour3` | 0~7 (3시간 구간) |
| **both-shop** | 모집단 전체 기간에서 `meal` 행과 `general` 행이 **둘 다 1건 이상** 있는 가맹점 |

## 3. 산출 표

결제 파일 **1회 순회**로 T2-a~c와 T2-d의 입력 행렬을 모두 만든다. both-shop 집합은 순회 중엔 알 수 없으므로, 가맹점×G×R×daytype×hour3 건수를 먼저 누적한 뒤 사후에 걸러낸다(가맹점 수 × 2 × 3 × 2 × 8 셀 — 메모리 확인).

> **공통 변경 (방문 계획 §9 A1·A3·A10 반영, 2026-09-18)**
> - **G(급식/일반)로 파일을 나눈다.** 기존 T2-b(G×R×요일×시)와 T2-c(G×R×평일주말×3시간대)는 4축이었다. G별로 나누면 각 파일이 3축이 되어 센터 답변과 무관하게 `max_axes=3`을 지킨다. 두 G의 비교는 반출 후 밖에서 한다.
> - **비중 열(`share_*`)은 export하지 않는다.** 비중과 건수를 함께 내면 분모가 복원되어 억제 칸 합이 드러난다. 비중은 반출된 건수로 밖에서 계산한다.
> - 모든 표는 `zero_policy="mask"`, `known_totals` = 공개 합계 등록부(M0 `m0_month` 포함) + `reference_exports`.

### T2-a `m2_month_group.csv` — 월별 급식 비중 s_t
`ym, G, n, n_shop, n_cust` (3축 아님 — 키는 `ym`, `G` 2축)
- `share_meal`은 export하지 않는다(위 공통 변경). s_t는 밖에서 `n_meal / (n_meal + n_general)`로 계산.
- margin_groups: `[["G"], ["ym"]]`
- `meal` 월별 값은 M0 `m0_month`(= 1차 `t_month`)와 같아야 한다. 다르면 모집단이 달라진 것이므로 internal에 차이를 기록하고 `population` 메타를 구분한다.

### T2-b 대구 전체 요일×시 프로파일 — G별 2개 파일
| 파일 | 키 | 행 수 |
|---|---|---|
| `m2_meal_regime_dow_hour.csv` | `R, dow, hour_bucket` — **`night_bucket` 적용**(06~22시 + `23-05`) | 3×7×18 = 378 |
| `m2_general_regime_dow_hour.csv` | `R, dow, hour` — 24시간 그대로 | 3×7×24 = 504 |

- 열: 키 + `n, n_shop, n_cust`. 격자는 0으로 채운 뒤 `mask`로 억제.
- 대구 전체 집계이므로 시간 단위 허용(설계서 R-8).
- margin_groups: `[["R"], ["R","dow"], ["R","hour_bucket"]]` (general은 `hour`)
- `meal` 파일은 1차 `t_week_hour`와 모집단이 겹친다. `known_totals`에 1차 요일×시 공개 칸과 월 합계를 반드시 포함해 노출 점검한다(§9 A10).

### T2-c 가맹점 내 대조 — G별 2개 파일
both-shop 가맹점의 행만 사용.

| 파일 | 키 | 행 수 |
|---|---|---|
| `m2_within_shop_meal.csv` | `R, daytype, hour3` | 3×2×8 = 48 |
| `m2_within_shop_general.csv` | `R, daytype, hour3` | 48 |

- 열: 키 + `n, n_shop, n_cust`. 비중 열 없음.
- `m2_within_shop_meta.csv`: **both-shop 가맹점 수**, both-shop의 `meal` 행 수(구간 표기 `<1,000` / `1,000-9,999` / `10,000+`) — 전체 `meal` 대비 비중은 등록부 합계로 역산되지 않게 구간으로만.
- margin_groups: `[["R","daytype"], ["R","hour3"]]`

### T2-d `m2_within_shop_ci.csv` — 가맹점 블록 부트스트랩
각 (R, daytype)에 대해 hour3 8구간의 `diff = share_meal − share_general`와 95% CI.

**알고리즘** (`lib/stats.share_diff_bootstrap`)
1. both-shop 가맹점 `S`개에 대해 행렬 `M ∈ ℕ^{S×8}`(meal 건수), `Gm ∈ ℕ^{S×8}`(general 건수)를 (R, daytype)별로 만든다.
2. 관측 diff: `M.sum(0)/M.sum()` − `Gm.sum(0)/Gm.sum()`.
3. `rng = np.random.default_rng(seed)`; 반복 `reps`회: 가맹점 인덱스 `S`개를 복원추출 → 가중치 `w = np.bincount(idx, minlength=S)` → `(w[:,None]*M).sum(0)` 로 재계산. 분모 0이면 해당 반복 NaN.
4. 2.5·97.5 백분위(`np.nanpercentile`), 유효 반복 수 기록.

**열**: `R, daytype, hour3, diff, ci_low, ci_high, reps_valid, n_shops_used`
- `n_shops_used < 30`이면 CI 열을 NaN으로 두고 `note="가맹점 수 부족"`. (30은 이 명세의 운영 기준이며 설계서 임계값이 아니다.)
- 해당 (R, daytype, hour3)의 T2-c `meal` 셀이 억제됐으면 그 행의 `diff`·CI도 NaN.
- 이 표는 `n` 열이 없으므로 `suppress`에 `n_col=None`으로 넘기고, 위 두 규칙을 적용한 뒤 `status` 열을 채운다.

### T2-e `m2_effect_summary.csv` — 요약 통계
(R, daytype)별:
- `cramers_v_all`: T2-b를 hour3로 합친 2×8 표(G × hour3, 해당 daytype)
- `cramers_v_within`: T2-c의 2×8 표
- `max_abs_diff_hour3`, `max_abs_diff`, 그 행의 `ci_low`, `ci_high` (T2-d에서)
- **p값은 산출하지 않는다.**
- 억제된 셀이 포함된 (R, daytype)은 요약값을 NaN으로 두고 `note` 기록(억제 전 값으로 계산한 통계가 억제된 셀 정보를 흘리지 않게).

### T2-f `m2_hour_edge.csv` — 하루 양 끝 절벽 진단 (방문 계획 §9 A2)

**질문**: 23~05시에 결제가 거의 없는 것이 **이용 행동**인가, **주문·결제 가능 시간 규칙**인가. 규칙이라면 "주문할 수 없는 시간"을 데이터로 가를 수 있게 된다(레드팀 R01). 스크립트는 판정하지 않고 판정 재료만 만든다.

| 파일 | 키 | 값 | 억제 |
|---|---|---|---|
| `m2_hour_edge_general.csv` | `hour`(0~23), `daytype` | `n`, `days_with_any`(그 시간에 1건 이상 있었던 날 수), `days_in_period` | 표준(`mask`) |
| `m2_hour_edge_meal.csv` | `hour_bucket`(06~22 + `23-05`), `daytype` | 같음 | 표준(`mask`) |
| `m2_edge_by_month.csv` | `ym`, `G` | `days_in_month`, `days_with_23_05`(23~05시에 1건 이상 있었던 날 수), `n_23_05` | `n_23_05` 기준 표준 억제. `days_with_23_05`도 같은 칸이 억제되면 NaN |

- `days_with_any`는 `DistinctAccumulator(keys=[hour, daytype], id_col=ymd)`로 센다.
- `m2_edge_by_month`는 **규칙이 기간 중 바뀌었는지**(예: 어느 달부터 심야가 0이 되는지)를 보는 표다.
- internal 전용: `general`의 날짜별 첫·마지막 결제 시간 분포(p1/p50/p99), `meal`도 같음. 현장에서 A·B가 "일반 결제도 같은 시각에 끊기는가"를 바로 확인하는 용도.

## 4. internal 전용 점검

- 모집단 행 수, `G`별 행 수, 빈 `pay_gbn` 행 수, `time_invalid` 제외 수
- both-shop 가맹점 수와 `meal`만 있는 가맹점 수
- T2-b 억제 전후 합계 차이, 부트스트랩 소요 시간

## 5. 테스트

- 픽스처: 가맹점 3곳(둘은 both-shop, 하나는 meal만) — T2-c가 meal-only 가맹점을 제외하는지.
- `cramers_v`: 완전 독립 표 → 0, 완전 연관 2×2 → 1.
- 부트스트랩: 가맹점 1곳만 있을 때 CI 폭 0; seed 고정 시 두 번 실행 결과 동일.
- T2-b 보완 억제: R 그룹에 억제 셀 1개인 픽스처에서 추가 억제 발생.
- T2-b meal: 1차 반출물과 같은 구조의 픽스처(억제 칸 합 = 억제 칸 수 + 1)를 `known_totals`로 넣었을 때 노출 점검 통과.
- T2-f: 합성 데이터에 "일반 결제는 01~05시 0건, 급식도 0건" 규칙을 심어 `days_with_any=0`이 두 G 모두에서 나오는지. 반대로 일반만 심야 결제가 있는 경우도.
- 성능: 합성 200만 행에서 순회+부트스트랩 500회 소요 시간을 완료 보고에 기록.

## 6. 완료 기준

- [ ] 합성 데이터로 T2-a~f 생성, 모든 export 표에 `status` 열과 `.meta.json`
- [ ] T2-b meal 378행·general 504행, T2-c 각 48행 (0 채움 확인)
- [ ] **어떤 export 표도 키 축이 3개를 넘지 않음**, 비중 열(`share_*`) 없음
- [ ] 급식 시간 단위 표에 23·0~5시 개별 칸이 없음(`23-05`로만)
- [ ] p값 열이 어디에도 없음
- [ ] 그림은 만들지 않는다(반출 후 로컬에서 별도 작업)
