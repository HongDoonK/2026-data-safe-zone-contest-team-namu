# V2-M1 지급구분 의미 확인 — 전체 값 · 월 교차표 · 게이트 재계산

> 상위: [README.md](README.md) · 근거: 방문 계획 §4 M1, 설계서 §1.10-B·§4.2·미해결 N1~N4, 결과 문서 §8 요청 1 · 의존: V2-00
> 현장 소요 목표: **60분** (M0보다 먼저 돌려도 된다 — 급식 값 목록을 정하는 단계이므로)

## 1. 목적

"급식카드"를 **어떤 문자열로 걸러야 하는지**, 그리고 **2023-06 도입이 사실인지 표기 변경의 착시인지** 판단할 표를 만든다. 스크립트는 판정하지 않는다. 판정 규칙은 방문 계획 §4 M1 표에 사전 고정돼 있고 사람이 적용한다.

## 2. 스크립트 `20_m1_paygbn.py`

`meal_pay_values`가 비어 있거나 자리표시자여도 **실행된다**(1~3단계). 4단계만 값 목록이 필요하다.

### 1단계 — 전체 값 목록 (결제 파일 1회 순회)

`T1-a` `m1_paygbn_values.csv`

| 열 | 정의 |
|---|---|
| `pay_gbn` | strip 후 값. 빈 값은 `<EMPTY>` |
| `card_pay_gbn` | 같은 방식 |
| `n` | 행 수 |
| `n_shop`, `n_cust` | 고유 수 |
| `first_ym`, `last_ym` | 관측 첫·마지막 연월 |
| `months_observed` | `n>0`인 월 수 |
| `vacation_share` | 해당 값 행 중 1·2·8월 비중 (설정 `regime` 무관, 고정 정의) |
| `len_chars` | 값의 글자 수 (마스킹 추론 대조용, 설계서 §1.10) |

정렬: `n` 내림차순.

### 2단계 — 값 × 연월 (전 기간, 2022-01부터)

`T1-b` `m1_paygbn_month.csv`: `ym, pay_gbn, n, n_shop, n_cust` (상태 필터 `all`)
- 기간 제한 없이 파일에 있는 모든 월. 관측 없는 (값, 월) 조합은 **0 행으로 채운다**(값별 전체 월 격자).
- **이 표만 `zero_policy="show"`** 를 쓴다. 표기 전환 탐지는 "그 달에 0건"이라는 사실이 핵심이기 때문이다. 대신 0을 드러내면 억제 칸 범위가 [1,4]로 좁아지므로(방문 계획 §9 A1), `known_totals`에 **T1-a의 값별 `n`** 을 넣어 노출 점검을 반드시 통과시킨다. §3의 처리 규칙을 따른다.

`T1-b2` `m1_paygbn_month_wide.csv`: 행=`ym`, 열=`pay_gbn`, 값=`n`. 사람이 눈으로 표기 전환을 찾기 위한 표.

### 3단계 — 표기 전환 점검 보조표 (판정 아님)

`T1-c` `m1_value_transitions.csv` — `n` 상위 15개 값의 모든 쌍 (A, B)에 대해:

| 열 | 정의 |
|---|---|
| `a_last_ym`, `b_first_ym` | A의 마지막 관측월, B의 첫 관측월 |
| `gap_months` | `b_first_ym − a_last_ym` (월 단위) |
| `cust_overlap` | A와 B를 **둘 다** 쓴 고유 고객 수 |
| `cust_overlap_share_a` | `cust_overlap / A의 n_cust` |
| `shop_overlap`, `shop_overlap_share_a` | 가맹점 기준 같은 값 |

- 고객·가맹점 집합은 상위 15개 값에 대해서만 누적한다(메모리 제한). 
- `gap_months`가 −1~+2인 쌍만 export(나머지는 internal) — 전환 후보만 보이게.

### 4단계 — 게이트 재계산 (`meal_pay_values`가 채워졌을 때)

`T1-d` `m1_gate.csv` — 상태 필터 3종 각각:

| 열 | 정의 |
|---|---|
| `status_mode` | all / complete_only / exclude_cancel |
| `N` | 급식 행 수 |
| `N_SHOP` | 전 기간 고유 가맹점 수 (**월별 최대가 아니라 전 기간 고유**) |
| `MONTHS` | `n>0`인 월 수 |
| `FIRST_YM`, `LAST_YM` | |
| `share_of_all_rows` | 급식 N / 같은 상태 필터 전체 행 |
| `branch_full`, `branch_reduced`, `branch_fb1`, `branch_fb2` | 설계서 §4.2 분기 조건을 **글자 그대로** 적용한 True/False (임계값은 코드 상수로, 설계서 절 번호 주석) |
| `branch_count_true` | 참인 분기 수. 0 또는 2 이상이면 `branch_note="규칙상 미정 — 사람 판단"` (레드팀 R05의 공백·중복 사례) |

- `branch_fb2`의 "`PAY_GBN`에 급식 값이 실재하지 않음" 조건은 `N == 0`으로 구현.
- 이 표는 가맹점·고객 수가 크므로 억제 대상이 아니지만, `write_export` 규칙상 `suppress`를 거친다(값은 그대로 통과).

## 3. 억제

- `T1-a`, `T1-b`: 표준 억제. **소수 값(예: 결제 몇 건짜리 희귀 지급구분)은 억제되어 이름만 남는다** — 값 이름 자체는 개인정보가 아니므로 유지.
- `T1-b` margin_groups: `[["pay_gbn"], ["ym"]]`, `zero_policy="show"`, `known_totals` = T1-a의 값별 `n`.
- **노출이 해결되지 않는 값**(희귀 값이라 월 칸이 거의 다 억제되는데 T1-a 합계가 공개된 경우): T1-a에서 그 값의 `n`·`n_shop`·`n_cust`를 **구간 표기**(`<50` / `50-99` / `100-499`)로 바꾸고 `status="banded"`로 둔 뒤 T1-b를 다시 점검한다. 그래도 남으면 T1-b에서 그 값의 행을 빼고 `m1_paygbn_values`의 `note`에 "월별 표 제외(노출)"를 적는다. T1-a는 T1-b보다 **나중에** 확정한다.
- `m1_paygbn_month_wide`도 같은 억제 결과를 그대로 펼친 것이어야 한다(따로 억제하지 않는다).
- `T1-c`: `cust_overlap < 5` 또는 `shop_overlap < 3`이면 두 overlap 열과 share 열을 NaN.

## 4. 콘솔 요약 (사람이 현장에서 바로 볼 것)

```text
[M1] 지급구분 값 12종 (빈 값 포함)
  상위: 카드 / 신용/체크카드 / ... (n 내림차순 10개, 값만)
  first_ym이 202306 인 값: [...]
  last_ym이 202305 이하인 값: [...]
  전환 후보 쌍(gap -1~+2): 3쌍 → export/m1_value_transitions.csv 확인
  meal_pay_values: 미설정 → 게이트 계산 건너뜀
```

## 5. 테스트

- 합성 픽스처에 `SYN_MEAL_A`(2022-01~2023-05) → `SYN_MEAL_B`(2023-06~) 전환과 공통 고객을 넣고, `T1-c`에서 해당 쌍의 `gap_months=1`, `cust_overlap` 기대값 검증.
- 0 채움 격자: 값 3종 × 월 4개 = 12행.
- 희귀 값(총 7건, 3개월에 분산) 픽스처: T1-b 노출 점검 → T1-a 구간 표기 → 재점검 통과 순서로 처리되는지.
- 게이트 분기: `N=100000, N_SHOP=500, MONTHS=18`을 모의 입력으로 넣어 `branch_count_true=0` 확인(레드팀 C-5 반례) — **함수 단위 테스트이며 데이터 예측이 아니다.**

## 6. 완료 기준

- [ ] `meal_pay_values` 미설정 상태에서 1~3단계 실행 성공, 4단계는 건너뜀 메시지
- [ ] 설정 후 4단계 실행 성공
- [ ] `N_SHOP`이 전 기간 고유값임을 테스트로 확인(월별 최대와 다른 픽스처)
