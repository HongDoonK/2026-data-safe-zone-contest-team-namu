# V2-07 반출 전 누적 점검 — `export_check.py`

> 상위: [README.md](README.md) · 근거: 방문 계획 §9 A1·A3·A10, §10.3(7단계 이중 점검), 설계서 §7.2 · 의존: V2-00(메타 사이드카·공개 합계 등록부), M0~M4
> 현장 소요 목표: **5분 이내 실행**, 사람 검토 포함 60분

## 1. 목적

반출 신청 직전에 **이번 반출물 + 이미 반출된 모든 표**를 함께 놓고, 표끼리 맞춰 봤을 때 억제 칸 값이 좁혀지거나 복원되는지 기계적으로 확인한다. 1차 반출물은 표 하나하나는 억제 기준을 지켰지만 두 표의 합계 차이로 억제 칸 값이 복원됐다(§9 A1). 사람 눈으로는 이 조합을 다 볼 수 없다.

`suppress()`가 표를 만들 때 이미 노출 점검을 하지만, 그 시점에는 **나중에 만들어진 표**를 모른다. 이 스크립트는 모든 표가 만들어진 뒤 전체를 다시 본다.

## 1.5 구현 단계와 V2-00과의 경계 (2026-09-18 추가)

**2차 방문(9/22~23) 전 필수는 단계 A뿐이다.** 단계 B는 3차 방문 전까지.

| 단계 | 범위 | 기한 | 빠지면 |
|---|---|---|---|
| **A** | C1~C7, C9 + **C8-lite**: 이번 표 각각을 **1차 반출물 두 표와만** 한 쌍씩 대조(§4의 1~4·6·7단계, 5단계 전파 없음) | **9/21** | 방문 당일 7단계 점검을 전부 수작업으로 해야 한다 |
| B | C8 전체: 이번 표끼리 포함 관계 탐색 + 여러 쌍에 걸친 가능 범위 전파(§4의 2·5단계), `test_cross_module_chain` | 3차 방문 전 | 2차 반출은 모듈별 `suppress()` 노출 점검 + C8-lite로 방어 |

**V2-00과 나눠 갖는 코드** — 중복 구현 금지:
- 칸별 가능 범위 계산은 `lib/suppress.py`에 **`exposure_ranges(S, k, lo, hi) -> list[(min, max)]`** 순수 함수로 두고 `suppress()`와 `export_check.py`가 함께 쓴다. V2-00이 아직 없으면 이 함수부터 만들고 V2-00 구현 시 그대로 가져가게 한다.
- 시간 키 매핑(`hour`→`hour3`→`hour_bucket`, `ym`→`R`)은 `lib/timeparse.py`의 함수를 쓴다.
- 메타 사이드카·`status` 값 정의는 V2-00 §3.6·§3.7이 기준이다. V2-00 구현 전에는 **이 명세 §2의 픽스처 형식**으로 테스트하고, V2-00 완료 후 실제 M0~M4 출력으로 end-to-end를 한 번 더 돌린다.

**`reference/reference_meta.json` 형식** (손으로 작성, 저장소에 커밋):

```json
{
  "export_0911_month":     {"keys": ["ym"], "metrics": ["n", "n_shop", "n_cust"],
                            "population": "0911_unknown", "zero_policy": "absent_row",
                            "time_only": true, "night_bucket_applied": false},
  "export_0911_week_hour": {"keys": ["dow", "hour"], "metrics": ["n", "n_shop", "n_cust"],
                            "population": "0911_unknown", "zero_policy": "absent_row",
                            "time_only": true, "night_bucket_applied": false}
}
```

- `zero_policy="absent_row"`: 행이 없으면 0, 빈칸이면 억제 → 억제 칸 범위 **[1, n_min−1]**. 1차 반출물이 이 방식이다.
- `population="0911_unknown"`은 M0 재현 성공 후 사람이 해시로 바꾼다. `unknown`인 동안 C8은 **급식 표 전부를 같은 모집단일 수 있다고** 보고 대조한다.
- `n_shop`·`n_cust`는 칸끼리 더할 수 없으므로 C8 대조는 **`n`만** 한다(고유 수는 합산 관계가 성립하지 않음). 고유 수 억제 여부는 C4에서만 본다.

## 2. 입력

| 입력 | 출처 |
|---|---|
| 이번 실행의 `out/<run_id>/export/*.csv` + `*.meta.json` | M0~M4 |
| 과거 반출물 | 설정 `reference_exports` (1차 `t_month`, `t_week_hour`) + 추가 인자 `--past <폴더>`(3차 이후: 2차 반출 승인본) |
| 설정 | `config/visit2.json` (`suppression`, `export`) |

과거 반출물에는 메타 사이드카가 없으므로 `reference/reference_meta.json`에 손으로 정의한다: 1차 두 표의 `population`은 **M0가 재현에 성공한 조합의 population 해시**와 같게 둔다. M0 재현에 실패했으면 `population="0911_unknown"`으로 두고 모든 급식 표와 **같은 모집단일 수 있다고 보수적으로** 가정한다.

## 3. 점검 항목

실행: `python analysis/visit2/export_check.py --config analysis/visit2/config/visit2.json --run out/<run_id>`

| # | 점검 | 실패 시 |
|---|---|---|
| C1 | **파일 목록**: export 폴더에 `.csv`, `.meta.json`, `filter_definition.txt`, `run_manifest.json` 외 파일이 없음 | FAIL |
| C2 | **가명 ID 없음**: 모든 CSV의 모든 셀에서 원자료 가맹점·고객 코드 형식(설정 `id_patterns`, 현장에서 샘플 3개를 보고 정규식 입력)과 일치하는 문자열 0건 | FAIL |
| C3 | **메타·상태 열**: 모든 CSV에 `.meta.json`과 `status` 열이 있고, `status` 값은 `published`/`suppressed`/`zero`(show 표만)/`banded`뿐 | FAIL |
| C4 | **억제 기준 위반 없음**: `status=published`인 급식 관련 칸에 `n<5`·`n_shop<3`·`n_cust<5`가 없음 | FAIL |
| C5 | **축 수**: 키 열 수 ≤ `max_axes`. 예외는 `meta.time_only=True`이고 설정 `time_only_axes_exception=true`일 때만. 지역 키(`gungu`, `dong`)가 있는 표는 예외 불가 | FAIL |
| C6 | **급식 시간 단위 표의 심야**: `population`이 급식이고 키에 시간이 있는 표에 23·0~5시 개별 칸이 없음 | FAIL |
| C7 | **비중 열**: `share_*` 열과 그 분모 그룹의 `n` 열이 같은 표에 함께 있으면 경고 | WARN |
| **C8** | **누적 노출 점검** (§4) | FAIL |
| C9 | `filter_definition.txt`에 급식 값·상태 필터·기간·레짐·지표 정의·심야 합치기·0 처리 방식이 모두 적혀 있음 | FAIL |

## 4. C8 누적 노출 점검 — 알고리즘

1. **표 등록**: 모든 표(이번 + 과거)를 `(population, metric)`별로 모은다. 한 표는 `keys` 집합과 칸 목록(키 값, 공개 값 또는 억제)으로 표현한다.
2. **포함 관계 찾기**: 같은 `(population, metric)` 안에서 표 A의 키가 표 B의 키를 **포함**하면(B가 A를 합친 것), 또는 A·B의 키를 공통 키로 올려 합칠 수 있으면(예: `ym`과 `R`은 `ym→R` 매핑으로, `hour`와 `hour_bucket`·`hour3`는 시간 매핑으로 연결), 둘을 비교 쌍으로 만든다. 키 매핑은 `lib/timeparse`의 정의를 재사용한다.
3. **그룹별 억제 합 계산**: 거친 표(B)의 공개된 칸마다, 세밀한 표(A)에서 그 칸에 속하는 칸들의 `S = B값 − A 공개 칸 합`, 억제 칸 수 `k`를 구한다.
4. **가능 범위**: 각 A 억제 칸의 범위 `[lo, hi]`는 그 표의 `zero_policy`에 따른다(`mask` → [0, n_min−1], `show` → [1, n_min−1]). `suppress()` §3.6과 같은 식으로 칸별 가능 범위를 계산한다. 반대 방향(B가 억제되고 A가 공개)도 본다.
5. **여러 표에 걸친 제약**: 같은 억제 칸이 여러 쌍에 등장하면 가능 범위를 교집합으로 좁힌 뒤 한 번 더 전파한다(변화가 없을 때까지, 최대 10회).
6. **판정**: 어떤 억제 칸이든 최종 가능 범위가 원래 범위보다 좁으면 **노출**. 보고에 `표 이름, 칸 키, 원래 범위, 좁혀진 범위, 원인이 된 표 쌍`을 적는다.
7. **과거 반출물 자체의 노출**은 이미 공개된 사실이므로 FAIL로 세지 않고 `KNOWN`으로 따로 적는다(예: 1차 `t_week_hour` 심야 칸). 단 **이번 표가 그 노출을 더 좁히면**(예: 범위 [1,2] → [1,1]) FAIL.

## 5. 출력

- `out/<run_id>/internal/export_check_report.txt` — 항목별 PASS/WARN/FAIL/KNOWN, 노출 칸 목록, 제안 조치
- 콘솔 요약 한 화면. 종료 코드: 전부 PASS/WARN/KNOWN이면 0, FAIL 하나라도 있으면 1.
- **리포트에는 억제 칸의 실제 값을 쓰지 않는다**(좁혀진 범위만). 리포트도 internal에만 둔다.

**제안 조치**(자동 수정은 하지 않는다):

| 원인 | 제안 |
|---|---|
| 세밀한 표 칸이 거친 표 합계로 좁혀짐 | 세밀한 표에서 같은 그룹 공개 칸 추가 억제 → 해당 모듈 재실행 |
| 과거 반출물과의 조합 | 이번 표의 해상도를 낮추거나(심야 합치기, 시간→3시간) 이번 반출에서 제외 |
| 0 표시(`show`) 표 | 그 표를 `mask`로 바꾸거나 합계 쪽을 구간 표기 |

## 6. 테스트

| 테스트 | 확인 |
|---|---|
| `test_0911_known` | 1차 두 표만 넣으면 `t_week_hour` 억제 10칸이 `KNOWN`(범위 [1,2])으로 나오고 FAIL은 0 |
| `test_new_table_narrows_known` | 1차 + "금요일 23시 칸만 공개된 새 표" → 나머지 칸 범위가 더 좁아져 FAIL |
| `test_night_bucket_safe` | 1차 + M0 `m0_dow_hour_night`(mask) → FAIL 0 |
| `test_cross_module_chain` | M2 T2-a(월×G) + M3 T3-d(월×등록여부) + M4 T4-a(군구×R×G)의 합계 사슬로 T4-b 동 칸이 좁혀지는 픽스처 → FAIL |
| `test_id_pattern` | 합성 ID 문자열이 비중 열 이름·값 어디에 있어도 C2 FAIL |
| `test_axes_region_no_exception` | `dong` 키가 있는 4축 표는 예외 설정이 true여도 C5 FAIL |

**단계 A 필수 테스트**: `test_0911_known`, `test_new_table_narrows_known`, `test_night_bucket_safe`, `test_id_pattern`, `test_axes_region_no_exception`, 그리고 `exposure_ranges`의 경계 사례(1차 사례 `S=11,k=10,[1,4]` → 각 칸 `[1,2]`; `mask` 범위 `[0,4]` → 전 범위 유지; `S=11,k=3,[0,4]` → `[3,4]`).
**단계 B 추가**: `test_cross_module_chain`.

## 7. 완료 기준

**단계 A (9/21)**
- [ ] 픽스처 입력으로 C1~C7, C9, C8-lite 동작, 단계 A 필수 테스트 통과
- [ ] `exposure_ranges`가 `lib/suppress.py`에 있고 `export_check.py`가 import해 씀
- [ ] `reference/reference_meta.json`과 1차 JSON 두 개(저장소 CSV에서 복사)가 커밋됨
- [ ] `selfcheck.py`에 `test_0911_known` 추가

**단계 B (3차 방문 전)**
- [ ] 합성 데이터로 M0~M4 → `export_check.py` 전 과정이 5분 이내
- [ ] 위 테스트 전부 통과, `selfcheck.py`에 `test_0911_known` 추가
- [ ] 현장 명령어 1줄과 FAIL 시 대처 3줄을 완료 보고에 포함
- [ ] pandas·numpy 외 import 없음
