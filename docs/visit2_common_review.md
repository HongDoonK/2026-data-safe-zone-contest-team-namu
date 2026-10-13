# V2-00 공통 기반 검토 (2026-09-18)

범위: `tasks/V2-00_common_infra.md`, `analysis/visit2/lib/*.py`, 현재 `test_common*`를 읽기 전용으로 검토했다. 합성 입력만 메모리에서 실행했으며 이 문서 외 파일은 수정하지 않았다. 사용자 결정대로, 큰 칸의 보완 억제 후 고정 범위가 양립하지 않을 때 `unresolved`로 기록하고 `write_export`가 거부하는 동작은 정상으로 보았다.

## 1. [높음] 억제 행의 추가 수치 열이 그대로 반출될 수 있음

- 위치: `analysis/visit2/lib/suppress.py:140-144`, `analysis/visit2/lib/manifest.py:88-92,124-130`
- 재현 입력: `pd.DataFrame({"cell":["A","B","C"], "n":[1,2,2], "amount":[11,22,33]})`를 `suppress(df, ["cell"])`에 넣는다. 실제 출력은 세 행 모두 `status="suppressed"`, `n=NaN`이지만 `amount=11,22,33`이 남고 `report.unresolved=[]`이다. `write_export`는 `meta.metrics=["n"]`이면 억제 행의 `n`만 비었는지 검사하며, `amount` 열을 거부하거나 지우지 않는다.
- 영향: 호출자가 `value_cols=["amount"]`를 빠뜨리거나 `meta.metrics`에 일부 열만 넣으면, 억제 기준 미달 행의 값이 CSV에 기록된다. 비중·합계·금액 열이면 작은 셀의 규모를 직접 드러내거나 역산할 수 있다. `suppress`를 거쳤다는 digest 검사도 이 입력을 막지 못한다.
- 필요한 조치: 공개 표의 키·상태 외 모든 값 열이 억제 대상에 등록되었는지 검증하고, 등록되지 않은 열이 있으면 `write_export` 전에 실패하도록 한다. 적어도 억제 행의 모든 공개 수치 열이 비었는지 검사해야 한다.

## 2. [높음] 이미 공개한 부분합을 다음 표의 `known_totals`로 자동 연결하지 않음

- 위치: `analysis/visit2/lib/manifest.py:131-160`은 공개된 부분합을 `self.totals`와 `published_totals.json`에 기록하지만, `analysis/visit2/lib/suppress.py:83-95`는 호출자가 직접 넘긴 `known_totals`만 본다. 공통 라이브러리에 등록부·`reference_exports`를 읽어 다음 억제 호출에 넘기는 경로가 없다.
- 재현 입력: 앞선 공개 표가 동일 모집단의 `g=X: n=5`, `g=Y: n=8`을 공개했다고 가정한다. 다음 표는 `g=[X,X,Y×8]`, `cell=0..9`, `n=[1,4,1,1,1,1,1,1,1,1]`이다. `suppress(df,["g","cell"])`는 열 칸 모두 억제하면서도 `unresolved=[]`을 반환한다. 같은 입력에 `known_totals={(("g",),("X",)):5}`를 넣으면 `X` 그룹이 `reason="narrowed"`로 `unresolved`가 된다. 앞선 표의 X 합계 5와 다음 표의 X 억제 칸 두 개를 함께 보면, 각 칸의 가능 범위가 기본 `[0,4]`에서 `[1,4]`로 좁아진다.
- 영향: 각 표 단독의 `write_export` 검사는 통과해도, 두 표를 함께 공개하면 명세 §3.6의 표 간 노출 점검을 놓친다. `reference_exports`의 기공개 합계에도 같은 문제가 적용된다.
- 필요한 조치: 다음 표를 억제하기 전에 동일 모집단·기간·키 기준으로 등록부와 기공개 합계를 매칭해 `known_totals`에 공급하는 공통 경로를 만들고, 누락·매칭 불확실성은 공개 전에 거부한다. 적용 뒤 위 입력이 거부되는지 검증한다.

현재 검토에서 위 두 항목 외 즉시 실행을 막는 결함은 확인하지 못했다. 이 검토는 전체 파이프라인의 인수 시험을 대체하지 않는다.

## 후속 수정 및 사용법

두 항목을 공통 라이브러리에서 보강했다. `suppress`는 억제 행의 키·상태 이외 모든 열을 기본으로 비우고, `write_export`도 같은 조건을 다시 검사한다. `n_col=None` 통계·구간 표는 입력 `status`를 유지하되 `banded` 행의 수치와 `suppressed` 행의 모든 비키 값을 비운다. 숫자 `n`을 넣어 건수 검사를 우회하는 입력은 거부한다.

표를 억제하기 전에 `known = ctx.known_totals(meta)`를 얻어 `suppress(raw, keys, known_totals=known)`로 넘긴다. `ctx.known_totals(meta)`는 같은 실행의 `published_totals.json` 등록 내용과 설정의 `reference_exports` JSON을 읽어, `population`이 정확히 같고 고정 키가 양립하는 **완전 공개 건수 합계**만 돌려준다. `write_export`도 해당 합계로 새 표의 `n`을 다시 점검하므로 호출자가 `known_totals` 전달을 빠뜨려도 좁아지는 억제 범위는 거부한다. 참조 표는 `reference/reference_meta.json`의 모집단·키 메타를 사용하며, 설정 경로가 `.../config/visit2.json`이면 참조 경로는 `.../visit2/` 기준이다. 현재 1차 참조 메타의 `population="0911_unknown"`은 새 표의 다른 모집단과 **자동 일치시키지 않는다**. `ym→R`, `hour→hour3` 등 서로 다른 시간 키로의 변환도 지원하지 않으며 임의 추정하지 않는다.

검증: 추가 회귀 테스트는 수정 전 5개 실패를 확인했다. 수정 후 `test_common.py`, `test_common_adversarial.py`, `test_stage0_acceptance.py`, 새 `test_common_review_regressions.py`를 함께 실행해 **45개 통과**했다. 합성 입력만 사용했고 실제 데이터 품질이나 현장 환경은 검증하지 않았다.
