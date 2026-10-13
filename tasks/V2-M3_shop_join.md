# V2-M3 가맹점 테이블 프로파일 + 결제⋈가맹점 첫 결합

> 상위: [README.md](README.md) · 근거: 방문 계획 §4 M3, 설계서 §1.5·§1.10-C·E·F3·미해결 A3·B10·B11, 레드팀 R01·R02 · 의존: V2-00, M0, M1
> 현장 소요 목표: **60분**

## 1. 목적

1. 가맹점 테이블(`INS_004`)을 처음으로 열어 **키 유일성·값 체계·동 이름 체계**를 확인한다.
2. 결제 테이블과 `SHOP_ID`로 결합해 **`CHILD_ABLE_YN`이 실제 급식결제 발생과 얼마나 맞는지**(정합률·활성률)를 본다.
3. 대구로 **내부 연계의 첫 산출물**을 만든다.

> 결과 해석(“의미가 다르다” 등)은 하지 않는다. 방문 계획 §4 M3의 “읽는 법”은 사람이 적용한다.

## 2. 스크립트 `40_m3_shop.py`

### 1단계 — 가맹점 테이블 프로파일 (파일이 작으므로 전체 로드)

| 표 | 파일 | 내용 |
|---|---|---|
| T3-a1 | `m3_shop_keys.csv` | `rows`, `unique_shop_id`, `dup_shop_id_count`(2회 이상 등장한 ID 수), `empty_shop_id` |
| T3-a2 | `m3_shop_values.csv` | `column, value, n` — `child_able`, `good_able`, `store_status`, `service_closed`의 값 분포(빈 값은 `<EMPTY>`) |
| T3-a3 | `m3_shop_status_cross.csv` | `child_able × store_status × service_closed` 가맹점 수 |
| T3-a4 | `m3_shop_closed_year.csv` | `closed_at` 앞 4자리 연도 × `store_status` 가맹점 수. 형식이 `YYYYMM`이 아닌 값은 `<INVALID>`로 묶음 |
| T3-a5 | `m3_gungu.csv` | `gungu, n_shop, n_dong_unique, n_child_able_y` — **군위군 등장 여부**를 콘솔에 따로 출력 |
| T3-a6 | `m3_dong_name_length.csv` | `gungu, len_chars, n_dong_unique, n_shop`, 그리고 `ends_with_digit_dong`(이름이 `숫자+동`으로 끝나는 고유 동 수) — 법정동/행정동 판단 재료 |

- 중복 `SHOP_ID`가 있으면: 중복 행을 internal에 저장하고, 결합에는 **첫 행이 아니라** "중복 ID는 결합 제외" 규칙을 쓴다(임의 선택 금지). 제외 규모를 T3-b 메타에 기록.
- 동 이름 목록 원본(`gungu, dong` 고유 쌍)은 **internal**에 저장. export 여부는 센터 확인 후 M4에서 결정 `[ASK]`.

### 2단계 — 결제 집계 (결제 파일 1회 순회)

모집단: M2와 같은 상태 필터·기간·`time_invalid=False`.

가맹점 단위 누적:
- `pay_n_all` (전체 결제 행), `pay_n_meal` (급식 행)
- `first_ym_all`, `last_ym_all`, `first_ym_meal`, `last_ym_meal`

→ internal `m3_shop_pay_summary.csv`로 저장(pyarrow가 없을 수 있으므로 Parquet 금지). M4가 재사용한다.

### 3단계 — 결합과 교차표

가맹점 단위 합집합 `U = (가맹점 테이블 ID) ∪ (결제에 등장한 ID)`에 대해:

| 파생 | 값 |
|---|---|
| `in_shop_table` | Y / N |
| `child_able` | Y / N / `<EMPTY>` / `<NOT_IN_TABLE>` |
| `has_pay` | 모집단 결제 ≥1 |
| `has_meal_pay` | 모집단 급식 결제 ≥1 |

**T3-b** `m3_shop_meal_x_able.csv`: `in_shop_table, child_able, has_pay, has_meal_pay, n_shop`

**T3-b-rates** `m3_join_rates.csv` (한 행, 비율과 분모를 함께):

| 열 | 정의 |
|---|---|
| `ref_rate_rows` | 결제 행 중 `in_shop_table=Y` 가맹점의 행 비율 |
| `ref_rate_shops` | 결제 등장 가맹점 중 `in_shop_table=Y` 비율 |
| `ref_rate_meal_rows` | 급식 결제 행 기준 같은 값 |
| `match_rate_y_given_meal` | `has_meal_pay` 가맹점 중 `child_able=Y` 비율 (분모: `in_shop_table=Y`인 것만, 분모 수도 기록) |
| `active_rate_meal_given_y` | `child_able=Y` 가맹점 중 `has_meal_pay` 비율 |
| `active_rate_any_given_y` | `child_able=Y` 가맹점 중 `has_pay` 비율 |
| `dup_id_excluded_shops` | 1단계 중복 규칙으로 제외된 가맹점 수 |

비율 열 옆에 반드시 `_num`, `_den` 열을 둔다. 분모 0이면 NaN(0 아님).

**T3-c** `m3_meal_shop_distribution.csv` — `has_meal_pay` 가맹점의 가맹점별 급식 건수 분포:
- `p50, p75, p90`, `top10pct_share`(상위 10% 가맹점의 급식 건수 점유율), `n_shops`
- `n_shops < 50`이면 전부 NaN. **p99·최댓값은 출력하지 않는다**(개별 가맹점 추정 방지, 설계서 R-6).
- 같은 표를 `child_able`(Y / N / NOT_IN_TABLE)별로 한 행씩.

**T3-d** `m3_meal_ym_by_able.csv` — `ym × child_able` 급식 결제 `n, n_shop, n_cust`. "현재 Y 가맹점이 과거에도 급식을 받았는가"의 시간 모양을 보는 재료(레드팀 R02). 표준 억제, margin_groups `[["ym"], ["child_able"]]`. **월별 급식 합계는 M0 `m0_month`·1차 `t_month`로 이미 공개돼 있으므로** `known_totals`에 등록부 값을 넣어 노출 점검한다(방문 계획 §9 A10). `zero_policy="mask"`.

## 3. 억제

- T3-a 계열: 가맹점 수 셀 `< 3`이면 억제(`n_col`에 가맹점 수, `shop_col=None`, `cust_col=None`, `n_min=3`).
- T3-b: 같은 규칙. margin_groups `[["in_shop_table","child_able"], ["has_pay","has_meal_pay"]]`.
- T3-b-rates: 분자·분모 중 하나라도 `< 3`이면 그 비율 3열 NaN.

## 4. 콘솔 요약

```text
[M3] 가맹점 테이블 rows=… unique=… dup_ids=…
  CHILD_ABLE_YN 값: Y / N / <EMPTY> (가맹점 수 비공개, export 참조)
  군위군 등장: 예/아니오
  동 이름 글자수: 3자 …%, 4자 …% (고유 동 기준)
  결합: 결제 가맹점 참조율 …, 급식결제 가맹점 중 Y …, Y 중 급식결제 발생 …
```
(콘솔도 억제 규칙을 따른다: 3 미만 수치는 `<3`으로 표시)

## 5. 테스트

- 픽스처: 테이블 중복 ID 1건 → 결합 제외, `dup_id_excluded_shops=1`
- 결제에만 있는 가맹점 → `child_able=<NOT_IN_TABLE>`
- `match_rate` 분모 0 → NaN
- `T3-c` 가맹점 49곳 → 전부 NaN, 50곳 → 값 생성
- 동 이름 `비산1동`은 `ends_with_digit_dong`에 포함, `비산동`은 미포함

## 6. 완료 기준

- [ ] 합성 데이터로 T3-a1~a6, T3-b, rates, T3-c, T3-d 생성
- [ ] 가맹점 단위 요약 CSV가 internal에 저장되고 M4가 읽을 수 있음
- [ ] export 어디에도 `SHOP_ID`·`CUST_ID` 값이 없음(테스트로 확인: export 폴더 전체에서 합성 ID 문자열 검색 결과 0건)
