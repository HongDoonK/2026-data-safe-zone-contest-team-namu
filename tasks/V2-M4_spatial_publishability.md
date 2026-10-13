# V2-M4 공간 공표 가능성(G1 사다리) + 군구·동 집계

> 상위: [README.md](README.md) · 근거: 방문 계획 §4 M4, 설계서 §3.2 H1-b·§7.2 R-5·R-7·R-8, 결과 문서 D5, 레드팀 C-5 G1·R10 · 의존: V2-00, M0, M1, M3
> 현장 소요 목표: **60분**

## 1. 목적

1. 급식 결제를 **어느 공간·시간 단위까지 공표할 수 있는지**를 억제 기준 통과율로 측정하고, 사전 고정 규칙으로 주 지도 단위를 정한다.
2. 그 단위로 **급식 결제의 지역 분포(H1-b 초판)** 를 반출한다.

지역은 **가맹점 소재지**(`INS_004`의 군구·동)이며 이용자 거주지가 아니다. 모든 export 표의 `filter_definition.txt` 항목과 콘솔 헤더에 이 문장을 넣는다.

## 2. 결합 규칙

- M3의 결합 규칙을 그대로 쓴다: `SHOP_ID` → (`gungu`, `dong`). 중복 ID는 제외.
- 테이블에 없는 가맹점의 결제는 `gungu="<NOT_IN_TABLE>"`, `dong="<NOT_IN_TABLE>"`. 동이 빈 값이면 `dong="<EMPTY>"`.
- 이 두 버킷은 사다리 비율 계산의 **분모에 포함**하고, 셀로는 별도 표시한다(지도에서 누락되는 규모를 드러내기 위함).
- 동 식별자는 `gungu + "|" + dong` (구가 다른 동명 이의어 방지).

## 3. 스크립트 `50_m4_space.py`

모집단: M2와 같음. 가맹점 매핑을 메모리에 올린 뒤 결제 파일 **1회 순회**.

### 1단계 — G1 사다리

각 단계의 셀별 `n, n_shop, n_cust`를 `G`(meal/general)별로 누적한다.

| 단계 | 키 |
|---|---|
| L1 | 동 × R × hour3 |
| L2 | 동 × R |
| L3 | 동 (전 기간) |
| L4 | 군구 × R × hour3 |
| L5 | 군구 × R |

**`G1` `m4_g1_publishability.csv`** — 단계 × G 한 행:

| 열 | 정의 |
|---|---|
| `level`, `G` | |
| `cells_total` | 관측 셀 수(`n>0`). 0 셀은 세지 않는다 |
| `cells_pass` | 1차 억제 기준(n≥5, shop≥3, cust≥5) 통과 셀 수 |
| `cell_pass_share` | `cells_pass / cells_total` |
| `count_pass_share` | 통과 셀의 `n` 합 / 전체 `n` |
| `not_in_table_share` | `<NOT_IN_TABLE>`·`<EMPTY>` 버킷의 `n` 비중 |

- **이 표에는 건수 절댓값을 넣지 않는다.** 셀 수와 비율만.
- 보완 억제 전 기준이다(사다리 비교 목적). 실제 export 표는 보완 억제 후 통과율이 더 낮을 수 있으므로, 선택된 단위에 대해서는 보완 억제 후 `count_pass_share_after_secondary`를 추가로 기록.

### 2단계 — 사전 고정 규칙 적용

`meal` 행 기준으로, **`count_pass_share ≥ threshold`인 가장 세밀한 단계**를 선택한다. 세밀함 순서: L1 > L2 > L3, L4 > L5, 그리고 동 단계가 군구 단계보다 세밀. 비교 순서는 `L1, L2, L4, L3, L5`로 고정한다(시간 해상도 있는 동 → 시간 없는 동 → 시간 있는 군구 → 전 기간 동 → 군구).

> 이 순서는 이 명세가 정한 운영 규칙이다. L3(전 기간 동)과 L4(군구×레짐×3시간) 중 무엇을 우선할지는 방문 계획에 없던 판단이므로, **완료 보고에 명시해 Claude 확인을 받는다.**

**`m4_map_unit_decision.csv`**: `threshold`(0.9/0.8/0.7) × `selected_level`, `count_pass_share`. `primary` 임계값(설정 `publish_rule.primary`)의 선택이 주 단위다. 어떤 단계도 기준을 못 넘으면 `selected_level="none"`.

### 3단계 — 반출 집계

| 표 | 파일 | 내용 | margin_groups |
|---|---|---|---|
| **T4-a** | `m4_gungu_regime.csv` | `gungu, R, G, n, n_shop, n_cust` | `[["gungu"],["R","G"]]` |
| **T4-b** | `m4_mapunit.csv` | 주 단위 키 × G: `n, n_shop, n_cust` + `share_meal = n_meal/(n_meal+n_general)` + `lq` | 주 단위 키에서 동/군구를 뺀 나머지 축과 동/군구 축 각각 |
| **T4-c** | `m4_dong_able.csv` | `gungu, dong, n_shop_total, n_shop_child_able_y` (가맹점 테이블만 사용, 결제 무관) | `[["gungu"]]` |
| **T4-d** | internal `m4_dong_names.csv` | `gungu, dong, len_chars` 고유 목록 | — |

**누적 노출 점검** (방문 계획 §9 A1·A10): T4-b의 동 칸을 군구별로 더하면 T4-a 군구 합계가 되고, 군구·레짐 합계를 더하면 M2 T2-a 월별 합계와 맞물린다. 따라서 **T4-a를 먼저 export해 등록부에 올리고**, T4-b는 `known_totals`에 T4-a·M2 등록부 값을 넣어 `suppress`한다. 모든 표 `zero_policy="mask"`. 해결되지 않는 노출이 있으면 T4-b를 한 단계 거친 단위(사다리 다음 단계)로 다시 만든다.

**LQ 정의** (T4-b): 같은 시간·레짐 조건 안에서
`lq = (n_meal_d / n_all_d) / (n_meal_total / n_all_total)` — `n_all = n_meal + n_general`
- `total`은 `<NOT_IN_TABLE>`·`<EMPTY>` **제외** 합계로 계산하고 그 사실을 `filter_definition.txt`에 기록.
- `meal` 셀이 억제되면 해당 행 `share_meal`·`lq` NaN. `general` 셀은 억제되지 않았더라도 짝 `meal` 셀이 억제된 행은 `n` 공개 여부를 그대로 두되 `share_meal`·`lq`는 NaN.

**교차 축 제한** (설계서 R-7): export 표는 최대 3축. T4-b의 주 단위가 L1(동×R×hour3)이면 G를 더해 4축이 되므로, **L1이 선택되면 T4-b를 두 표로 나눈다**: `m4_mapunit_meal.csv`(동×R×hour3, meal만)와 `m4_mapunit_share.csv`(동×R, share_meal·lq). 이 경우도 완료 보고에 명시.

**T4-c 억제**: `n_shop_child_able_y`가 1~2면 NaN(0은 공개). `n_shop_total < 3`인 동은 행 전체 억제.

**T4-d**: export하지 않는다. 센터가 동 이름 목록 반출을 허용하면 사람이 `internal`에서 `export`로 옮기며 그 판단을 `run_manifest.json`의 `manual_actions`에 기록하는 **보조 스크립트 `promote_internal.py`** 를 만든다(파일명·사유 인자 필수).

## 4. 콘솔 요약

```text
[M4] 지역 = 가맹점 소재지 기준
  G1 (meal, count_pass_share): L1 …  L2 …  L4 …  L3 …  L5 …
  주 단위(≥0.90): L2 동×레짐   | ≥0.80: …   | ≥0.70: …
  미참조·빈 동 비중: …
```

## 5. 테스트

- 픽스처로 L1~L5 통과율 손계산 검증, `cells_total`에 0 셀 미포함 확인.
- 선택 규칙: 모의 통과율 입력 `{L1:0.5, L2:0.92, L4:0.95, L3:0.97, L5:0.99}` → `L2`.
- 동명 이의어(`중구|대신동`, `서구|대신동` 가정 픽스처)가 별도 셀.
- L1 선택 시 T4-b가 두 표로 분리되고 어떤 export 표도 4축이 아님.
- LQ: 모든 동의 급식 비중이 같으면 `lq=1`.

## 6. 완료 기준

- [ ] 합성 데이터로 G1, 결정표, T4-a, T4-b(또는 분리 2표), T4-c 생성
- [ ] G1 표에 건수 절댓값 열이 없음
- [ ] `promote_internal.py`가 사유 없이 실행되면 거부
- [ ] 완료 보고에 §3 2단계 비교 순서와 L1 분리 규칙에 대한 확인 요청 포함
