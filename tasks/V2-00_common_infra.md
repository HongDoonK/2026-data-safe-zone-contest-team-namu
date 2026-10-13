# V2-00 공통 기반 — 설정·로더·시간 파생·억제·실행 기록·합성 데이터

> 상위: [README.md](README.md) · 근거: 설계서 §1.2·§1.5·§1.10·§7.2, 결과 문서 §1·§6(Q1~Q4), AGENTS.md §2·§4
> 이 작업이 끝나야 M0~M4가 돌아간다. **가장 먼저 구현한다.**

## 1. 목적

모듈 5개가 같은 CSV를 같은 방식으로 읽고, 같은 기준으로 억제하고, 같은 형식으로 실행 조건을 남기게 한다. 1차 반출의 문제(필터 조건 미기록, 요일 `와` 버그, 억제분 합계 역산)가 다시 생기지 않게 **구조적으로** 막는 것이 목적이다.

## 2. 설정 파일 `config/visit2.json`

현장에서는 **이 파일만** 고친다. 코드는 고치지 않는다. JSON만 사용(PyYAML이 없을 수 있다).

```json
{
  "run_label": "visit2",
  "paths": {
    "pay":  "D:/data/INS_DAEGURO_PAY.csv",
    "shop": "D:/data/INS_DAEGURO_SHOP.csv",
    "out_root": "out"
  },
  "encoding_candidates": ["utf-8-sig", "utf-8", "cp949"],
  "chunksize": 1000000,
  "columns": {
    "active": "en",
    "en": {
      "pay":  {"shop_id": "SHOP_ID", "cust_id": "CUST_ID", "pay_gbn": "PAY_GBN",
               "card_pay_gbn": "CARD_PAY_GBN", "dest_pay_gbn": "DEST_PAY_GBN",
               "app_time": "CARD_APP_TIME", "tot_amt": "TOT_AMT", "app_amt": "CARD_APP_AMT"},
      "shop": {"shop_id": "SHOP_ID", "gungu": "GUNGU_NM", "dong": "DONG_NM",
               "child_able": "CHILD_ABLE_YN", "good_able": "GOOD_ABLE_YN",
               "store_status": "STORE_STATUS", "closed_at": "CLOSED_AT",
               "service_closed": "SERVICE_CLOSED"}
    },
    "ko": {
      "pay":  {"shop_id": "가맹점코드", "cust_id": "고객코드", "pay_gbn": "지급구분",
               "card_pay_gbn": "카드결제_구분", "dest_pay_gbn": "현장결제_구분",
               "app_time": "승인일시", "tot_amt": "합계금액", "app_amt": "승인금액"},
      "shop": {"shop_id": "가맹점코드", "gungu": "군구명", "dong": "행정동명",
               "child_able": "아동급식_가능_유무", "good_able": "착한매장_유무",
               "store_status": "운영상태", "closed_at": "폐업일자",
               "service_closed": "대구로_서비스상태"}
    }
  },
  "meal_pay_values": ["<M1 값 목록을 보고 사람이 채운다>"],
  "status_filter": {"mode": "all", "complete_values": ["완료"], "cancel_values": ["취소"]},
  "period": {"start_ym": "202306", "end_ym": "202506"},
  "regime": {
    "mode": "month",
    "month_map": {"1": "방학", "2": "방학", "8": "방학", "7": "전환", "12": "전환"},
    "default": "학기",
    "date_ranges": []
  },
  "suppression": {"n_min": 5, "shop_min": 3, "cust_min": 5, "zero_policy": "mask"},
  "export": {
    "max_axes": 3,
    "time_only_axes_exception": false,
    "split_axis": "R",
    "night_bucket": {"enabled": true, "hours": [23, 0, 1, 2, 3, 4, 5], "label": "23-05"}
  },
  "reference_exports": {
    "export_0911_month": "reference/export_0911_month.json",
    "export_0911_week_hour": "reference/export_0911_week_hour.json"
  },
  "id_patterns": ["<현장에서 가맹점·고객 코드 샘플을 보고 정규식 입력>"],
  "bootstrap": {"reps": 500, "seed": 20260918},
  "publish_rule": {"count_share_thresholds": [0.9, 0.8, 0.7], "primary": 0.9}
}
```

- `ko` 매핑의 한글 컬럼명은 **추정치**다(사이트 미리보기 표시명 기반). `00_headers.py` 결과를 보고 현장에서 고친다.
- `status_filter.mode`: `all`(필터 없음) / `complete_only`(완료 값만) / `exclude_cancel`(취소 값 제외). M0이 1차 재현에 맞는 값을 찾는다.
- `regime.mode`: `month`(기본, 결과 문서 §3.1 정의) / `date_ranges`(`[{"start":"20240120","end":"20240303","label":"방학"}, ...]`, 이후 실제 학사일정으로 교체할 때 사용). 두 모드 모두 구현한다.
- `suppression.zero_policy` (방문 계획 §9 A1): `mask`(기본) = **관측 0인 칸도 억제 칸과 똑같이 표시**한다. 0을 따로 드러내면 억제 칸이 "1~4"로 좁혀져 합계로 값이 복원된다(1차 반출물에서 실제로 일어남). `show` = 0을 그대로 표시 — 표 단위로 명시적으로 켤 때만 쓰고, 그 표는 §3.6 노출 점검을 반드시 통과해야 한다.
- `export.max_axes` / `time_only_axes_exception` / `split_axis` (§9 A3): export 표의 키 축이 `max_axes`를 넘으면 `split_axis`(기본 레짐 `R`) 값별로 파일을 나눠 저장한다. 센터가 "지역·인구 축이 없는 시간 축 표는 4축 허용"이라고 답하면 `time_only_axes_exception=true`로 바꾼다. **답을 받기 전 기본값은 분할.**
- `export.night_bucket` (§9 A1·A2): 급식 결제가 들어간 **시간 단위 export 표**에서 23~05시를 한 칸(`23-05`)으로 합친다. 일반 결제의 시간 단위 진단표(M2 T2-f)에는 적용하지 않는다.
- `reference_exports` (§9 A10): 이미 반출된 표(1차 `t_month`, `t_week_hour`)를 JSON으로 옮긴 파일. 저장소 CSV의 값을 그대로 복사한다(수치 생성 아님). §3.6 노출 점검과 V2-07이 "이미 공개된 합계"로 사용한다. 반입 불가 시 `null` — 이 경우 V2-07은 경고를 남기고 반출 전 수작업 대조를 요구한다.
- 설정 로드 시 **스키마 검증**: 필수 키 누락, `meal_pay_values`가 비었거나 `<`로 시작하는 자리표시자 값이면 M1 이외 모듈은 즉시 오류로 중단한다.

## 3. `lib/` 모듈

### 3.1 `lib/config.py`
- `load_config(path) -> dict` — 위 검증 포함. 반환 dict에 `cols_pay`, `cols_shop`(활성 매핑) 편의 키를 추가.

### 3.2 `lib/io.py`
- `detect_encoding(path, candidates) -> str` — 앞 64KB를 후보 순서대로 디코드해 처음 성공한 인코딩.
- `read_header(path, encoding) -> list[str]`
- `iter_chunks(path, usecols_logical, cols_map, encoding, chunksize)` — **논리명**(`shop_id` 등)으로 요청하면 실제 헤더로 `usecols` 읽고 논리명으로 rename해 yield. `dtype=str`, `keep_default_na=False`, 모든 컬럼 `.str.strip()`. 빈 문자열은 `NA`로.
- 요청한 컬럼이 헤더에 없으면 **어떤 논리명이 어떤 실제명으로 매핑됐고 실제 헤더가 무엇인지** 함께 출력하고 중단.

### 3.3 `lib/timeparse.py`
- `add_time_fields(df, col="app_time") -> df` — `YYYYMMDDHH` 10자리 문자열에서 `ym`(int, 202306), `month`(int), `ymd`(int), `hour`(int 0~23), `dow`(int 0=월~6=일), `is_weekend`(bool), `hour3`(int 0~7, `hour // 3`) 생성.
  - 날짜는 `pd.to_datetime(s, format="%Y%m%d%H", errors="coerce")`로 파싱. 10자리가 아니거나 파싱 실패한 행은 `time_invalid=True`로 표시하고 **버리지 말고** 개수를 호출자가 보고하게 한다.
- `DOW_LABELS = ("월","화","수","목","금","토","일")` — **튜플 상수. 라벨은 출력 직전에만 붙인다.** `label_dow(int)` 제공.
- `HOUR3_LABELS = ("00-02","03-05","06-08","09-11","12-14","15-17","18-20","21-23")`
- `assign_regime(df, regime_cfg) -> Series` — `month` 모드와 `date_ranges` 모드. `date_ranges` 모드에서 범위 밖 날짜는 `default`.

### 3.4 `lib/filters.py`
- `meal_flag(df, meal_values) -> bool Series` — `pay_gbn`이 목록에 **정확히 일치**(strip 후). 부분 문자열 매칭 금지.
- `status_mask(df, status_cfg) -> bool Series` — `all`/`complete_only`/`exclude_cancel`.
- `period_mask(df, period_cfg)`.
- `describe_filter(cfg) -> str` — 사람이 읽을 수 있는 필터 조건 문장. `filter_definition.txt`에 그대로 들어간다.

### 3.5 `lib/distinct.py` — 청크 간 고유값 집계
청크별 `nunique`는 합산할 수 없다. 다음 방식으로 통일한다.
- `DistinctAccumulator(keys)` — 청크마다 `df[keys + [id_col]].drop_duplicates()`를 누적하고, `finalize()`에서 전체 `drop_duplicates` 후 `groupby(keys).size()`.
- 누적 프레임이 `max_rows`(기본 5,000,000)를 넘으면 중간에 한 번 `drop_duplicates`로 압축.
- `CountAccumulator(keys)` — 건수 합산.
- 한 번의 파일 순회에서 여러 집계기를 동시에 갱신할 수 있게 한다(모듈당 파일 순회 1회가 목표).

### 3.6 `lib/suppress.py` — 억제 ★ 리뷰 대상
```python
suppress(df, key_cols, n_col="n", shop_col="n_shop", cust_col="n_cust",
         n_min=5, shop_min=3, cust_min=5, zero_policy="mask",
         value_cols=None, margin_groups=None,
         known_totals=None) -> (df_out, report)
```
- **1차 억제**: `n < n_min` 또는 `n_shop < shop_min` 또는 `n_cust < cust_min`인 셀(해당 열이 있을 때만 조건 적용).
  - `zero_policy="mask"`: `n=0` 칸도 억제 칸과 **구별되지 않게** 같은 NaN·같은 `status="suppressed"`로 표시한다(내부 report에만 0 여부 기록). 이때 억제 칸의 가능 범위는 **[0, n_min−1]**.
  - `zero_policy="show"`: 0은 `0`, `status="zero"`. 억제 칸의 가능 범위는 **[1, n_min−1]** — 노출 위험이 크므로 호출하는 쪽이 반드시 `known_totals`를 넘긴다.
- 억제된 셀은 `n`·`n_shop`·`n_cust`·`value_cols` 전부 NaN. export되는 `status`는 `published` / `suppressed` 두 값뿐이다(1차·보완 구분은 internal report에만 — 구분 자체가 "기준 미달" 정보를 흘리므로).
- **보완 억제 — 노출 점검 기반** (방문 계획 §9 A1·A10. 기존 "억제 칸이 1개면 하나 더" 규칙을 대체한다. 1차 반출물은 억제 칸이 10개였는데도 값이 복원됐다.)
  1. 합계가 알려진 그룹을 모은다: `margin_groups`로 지정한 그룹 + 표 전체 + `known_totals`(`{(그룹 열 튜플, 그룹 값 튜플): 합계}`, 다른 export 표나 `reference_exports`에서 온 값).
  2. 각 그룹에서 억제 칸 합 `S = 알려진 합계 − 공개 칸 합`, 억제 칸 수 `k`, 칸별 범위 `[lo, hi]`.
  3. 각 억제 칸의 **가능 범위** `[max(lo, S − (k−1)·hi), min(hi, S − (k−1)·lo)]`를 계산한다.
  4. 어느 칸이든 가능 범위가 원래 범위 `[lo, hi]`보다 **좁아지면 노출**이다. 같은 그룹의 공개 칸 중 `n`이 가장 작은 칸을 추가 억제하고 1로 돌아간다. 노출이 없을 때까지 반복.
  5. 추가 억제할 공개 칸이 없는데도 노출이면 `report.unresolved`에 그룹을 기록하고 **`write_export`가 그 표를 거부**한다. 호출하는 쪽은 합계를 덜 공개하는 방식(심야 합치기, 합계 열 제거, 표 분할 취소)으로 다시 만든다.
  - `margin_groups`에 없어도 **공개된 비중 열이 있으면 그 그룹의 합계는 알려진 것으로 본다**(n ÷ 비중으로 분모 복원 가능).
- `report`: 1차·보완 억제 셀 수, 0 칸 수, 억제 전/후 `n` 합계, 그룹별 노출 점검 결과, `unresolved`(**internal에만** 기록).
- `export/`에 쓰는 표에는 **억제 전 합계 열을 넣지 않는다.**
- `apply_night_bucket(df, hour_col, cfg) -> df` — `hours` 목록의 시간을 `label` 한 칸으로 합산(고유 수는 원자료에서 다시 계산해야 하므로, 호출하는 쪽은 합치기 **전에** `hour_bucket` 키로 집계기를 돌린다).

### 3.7 `lib/manifest.py`
- `start_run(cfg) -> RunContext` — `run_id = <run_label>_<YYYYMMDD_HHMMSS>`, `out/<run_id>/export`, `out/<run_id>/internal` 생성.
- `ctx.write_export(df, name, report, meta)` — CSV `utf-8-sig`, 정수 열은 `Int64`로 저장(소수점 `.0` 방지, 결과 문서 Q3).
  - **거부 조건**: `status` 열 없음(= `suppress` 미통과) / `report.unresolved` 비어 있지 않음 / 키 축 수 > `export.max_axes`이고 예외 불가.
  - **축 초과 시**: `meta.time_only=True`이고 `time_only_axes_exception=true`면 그대로 저장, 아니면 `split_axis` 값별로 `name__<축>-<값>.csv`로 나눠 저장(분할 후에도 각 파일은 같은 억제 결과를 쓴다).
  - **메타 사이드카** `name.meta.json` (V2-07이 읽는다): `population`(필터 정의 해시 + G 부분집합 + 기간), `keys`(키 열 목록), `metrics`(`n`, `n_shop`, `n_cust` 중 있는 것), `time_only`, `zero_policy`, `night_bucket_applied`.
  - 저장한 표의 그룹 합계를 `internal/published_totals.json`(**공개 합계 등록부**)에 누적한다. 다음 모듈의 `suppress(known_totals=...)`가 이 등록부와 `reference_exports`를 함께 읽는다.
- `ctx.write_internal(df_or_text, name)`
- `ctx.finish(module, extra)` — `run_manifest.json`에 누적: 모듈명, 시작·종료 시각, 입력 파일 경로·크기·수정시각, 인코딩, 읽은 행 수, `time_invalid` 행 수, 설정 전문, `describe_filter()` 결과, git 커밋 해시(없으면 `"unknown"`), Python·pandas·numpy 버전.
- `export/filter_definition.txt` — `describe_filter()` + 컬럼 매핑 + 지표 정의(`n`=행 수, `n_shop`=고유 가맹점코드 수, `n_cust`=고유 고객코드 수) + 레짐 정의.

### 3.8 `lib/stats.py` (M2가 사용)
- `cramers_v(table_2d) -> float` — numpy로 직접 구현.
- `share_diff_bootstrap(counts_meal, counts_gen, reps, seed) -> DataFrame` — 입력은 가맹점×구간 건수 행렬 2개(같은 가맹점 순서). 가맹점을 복원추출해 구간별 비중 차(급식−일반)의 2.5/97.5 백분위. 상세는 V2-M2 §4.

## 4. 합성 데이터 `synthetic/visit2/make_synthetic.py`

- 출력: `synthetic/visit2/SYNTHETIC_INS_DAEGURO_PAY.csv`, `SYNTHETIC_INS_DAEGURO_SHOP.csv`, 그리고 영문 헤더판·한글 헤더판 두 벌.
- **형식만 맞춘다.** 값은 균등 난수 또는 손으로 정한 소량의 고정 패턴. 실제 분포를 흉내 내지 않는다(AGENTS.md §4-3).
- 반드시 들어가야 할 함정 사례:
  - 고정폭 패딩 공백(`"카드      "`), 빈 문자열, 10자리가 아닌 시각 문자열 1행
  - 지급구분 값 최소 5종, 그중 급식 역할의 값 이름은 `SYN_MEAL_A`, `SYN_MEAL_B`(두 표기가 기간에 따라 바뀌는 사례)
  - `CARD_PAY_GBN` 완료·취소
  - 가맹점 테이블에 없는 `SHOP_ID`를 쓰는 결제 행, 가맹점 테이블에 중복 `SHOP_ID` 1건
  - 한 셀에 고객 4명만 있는 급식 셀(억제 경계), 억제 셀이 그룹에 1개만 생기는 사례
- 기대값을 손으로 계산할 수 있는 **소형 고정 픽스처**(수십 행)를 `tests/visit2/fixtures/`에 별도로 둔다. 테스트는 이 픽스처로 정답을 검증하고, 대형 합성 파일은 end-to-end 실행·성능 확인용으로만 쓴다.
- 대형 합성 파일 크기: 결제 약 200만 행(청크 경계 통과 확인용). 생성 시드 고정.

## 5. 테스트 (로컬 pytest) + `selfcheck.py`

| 테스트 | 확인 내용 |
|---|---|
| `test_dow_mapping` | 2024-09-16(월)~22(일) 7일이 `월~일`로 나온다. `와`가 어디에도 없다 |
| `test_timeparse_invalid` | 9자리·문자 섞인 시각이 `time_invalid`로 잡히고 행이 유지된다 |
| `test_regime_month` / `test_regime_ranges` | 두 모드 경계일 |
| `test_meal_flag_exact` | `SYN_MEAL_A_X`는 매칭되지 않는다. 패딩 공백은 strip 후 매칭된다 |
| `test_distinct_across_chunks` | 같은 고객이 두 청크에 걸쳐도 1로 센다 (chunksize=3으로 강제) |
| `test_suppress_boundary` | n=4/5, shop=2/3, cust=4/5 경계 |
| `test_suppress_secondary_group` | 그룹 내 억제 1개 → 최소 셀 추가 억제, 결과적으로 그룹 합계에서 단일 셀 역산 불가 |
| **`test_exposure_0911_case`** | **1차 반출물 재현**: 억제 10칸, 알려진 합계로 `S=11`, `zero_policy="show"`(범위 [1,4]) → 노출 판정. 같은 입력을 `mask`(범위 [0,4])로 → 노출 없음 |
| `test_exposure_high_side` | `k=3`, `S=11`, 범위 [0,4] → 각 칸 가능 범위 [3,4]로 좁아짐 → 노출 → 추가 억제 발생 |
| `test_exposure_unresolved` | 그룹의 모든 칸이 억제됐는데 합계가 알려져 노출 → `unresolved` → `write_export` 거부 |
| `test_share_implies_total` | 비중 열이 있는 표는 `margin_groups` 없이도 그룹 합계가 알려진 것으로 처리 |
| `test_mask_zero_indistinguishable` | `mask`에서 0 칸과 억제 칸의 export 값·`status`가 완전히 같다 |
| `test_night_bucket` | 23·0~5시가 `23-05` 한 칸으로 합쳐지고 고유 수는 합산이 아니라 재계산값 |
| `test_write_export_guard` | `suppress` 안 거친 표 / `unresolved` 있는 표를 `write_export`가 거부 |
| `test_axes_split` | 4축 표 + 예외 false → `split_axis` 값별 파일로 분할, 각 파일 3축 |
| `test_header_mapping_error` | 없는 컬럼 요청 시 매핑·실제 헤더를 담은 오류 메시지 |

`selfcheck.py`는 pytest 없이 위 테스트 중 dow·suppress(**`test_exposure_0911_case` 포함**)·distinct를 `assert`로 실행한다(안심구역 PC에서 5초 내).

## 6. 완료 기준

- [ ] `python analysis/visit2/selfcheck.py` 통과
- [ ] `pytest tests/visit2` 전부 통과
- [ ] 영문·한글 헤더 합성 파일 각각으로 `00_headers.py`가 동작(설정의 `active`만 바꿔서)
- [ ] pandas·numpy 외 import 없음 (`grep`으로 확인해 보고)
- [ ] 완료 보고에 억제 함수의 보완 억제 알고리즘을 5줄 이내로 요약 — **Claude 리뷰 후 M2~M4 반출에 사용**
