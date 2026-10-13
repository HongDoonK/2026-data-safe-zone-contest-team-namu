# V2 구현 결과 — 단계 0 관문 실패로 중단

2026-09-18. **현장용 전체 구현은 완료되지 않았다. 현장 반출 판단에 사용하면 안 된다.**
사용자가 정한 "단계 0 또는 단계 1이 통과하지 못하면 전체 중단" 규칙을 적용했다.
연구 해석·기획서 문구·사전 등록 기준 변경은 하지 않았다.

## 1. 단계별 상태

| 단계 | 상태 | 근거 |
|---|---|---|
| 0 V2-00 | **미완** | 공통 모듈·설정·selfcheck·합성 생성기 초안 구현. 42개 통과, 보완 억제 인수 테스트 1개 실패 |
| 1 V2-07 A | 미착수 | 단계 0 관문 미통과. export_check 및 reference JSON 미생성 |
| 2 M1 | 미착수 | 같은 중단 규칙 |
| 3 M0 | 미착수 | 같은 중단 규칙 |
| 4 M3 | 미착수 | 같은 중단 규칙 |
| 5 M2 | 미착수 | 같은 중단 규칙 |
| 6 M4·승격 | 미착수 | 같은 중단 규칙 |
| 7 run_all·end-to-end | 미착수 | 같은 중단 규칙 |

## 2. 반복 기록

- 테스트 선작성: 기본 29개 실패(구현 부재) → 구현 후 29개 통과. 실행 도구 3개 실패 → 구현 후 32개 통과. 이는 인수 검증 바퀴 이전 개발 과정이다.
- **단계 0, 1바퀴:** 보완 억제의 고정 범위 문제 재현. 테스트 42 통과 / 1 실패, selfcheck 통과, 소형 영문·한글 실행 통과, 경계값·환경 점검 통과. 보수적으로 `unresolved` 처리하고 `write_export`가 반출을 거부한다.
- **구현 수정 없이 최종 재확인:** 동일한 42 통과 / 1 실패, pytest 종료 1. selfcheck 종료 0. 소형 실행·범위·환경 점검 재현 스크립트는 관문 FAIL을 기록하고 종료 1.
- **"수정 없이 통과"한 바퀴는 없다.** 계산 규칙·인수 기준 확인이 필요한 실패라 기대값을 바꾸거나 동일 실행을 6번 반복하지 않았다.
- 테스트를 skip/xfail 처리하지 않았다. 실패는 `test_stage0_acceptance.py::test_suppress_secondary_group`에 남겼다.

증거:

- `tests/visit2/fixtures/SYNTHETIC_pytest_final.txt`
- `tests/visit2/fixtures/SYNTHETIC_stage0_evidence.json`
- `tests/visit2/fixtures/SYNTHETIC_secondary_group.csv`

## 3. 적대적 입력 기대 / 실제

아래 수치와 입력은 모두 **SYNTHETIC**이다.

| 단계 0 항목 | 기대 | 실제 |
|---|---|---|
| a 패딩·빈 값·잘못된 시각 | strip·NA, 오류 표시, 행 유지 | 통과. 영문·한글 각 48행 유지, 오류 2행 |
| b 한글 헤더에 영문 매핑 | 논리명·실제명·실제 헤더를 담은 오류 | 통과. ValueError로 명확히 거부 |
| c cp949 | 감지 후 정상 읽기 | 통과. 64KB 경계에서 한글 문자가 잘리는 사례도 통과 |
| d 청크 경계의 같은 고객 | 중복 합산 없이 고유 수 1 | 통과 |
| e 범위 6사례·k=0 | 손계산 일치, 빈 그룹 예외 처리 | 통과. 아래 범위 표 참고 |
| f 모든 칸 억제·합계 공개 | unresolved, 저장 거부 | 통과. 반출 CSV 생성 안 됨 |
| g 상태 없음·unresolved·4축 | 거부 또는 split_axis 분할 | 통과. 분할 뒤 3축, 고정 축은 메타에 보존 |
| h 2024-09-16~22 | 월~일 | 통과 |
| i mask 0·소수 칸 | 동일한 빈 값·suppressed | 통과 |
| j 자리표시자 급식 값 | 일반 로드 거부, M1 탐색 예외 | 통과. `load_discovery_config` 분리 |
| 추가: 보완 억제 성공 인수 | 공개 칸을 추가 억제해 해결 | **실패. 추가 억제는 되지만 범위 불일치로 unresolved** |
| 추가: n≥5·고유 가맹점 미달 | 잘못된 범위로 안전 판정하지 않음 | 통과. 범위 계약 불일치로 거부 |
| 추가: 점검 후 표 변조 | write_export 거부 | 통과 |
| 추가: 지역 4축·예외 true | 지역 예외 불허 | 통과 |

| S,k,lo,hi | 칸별 결과 |
|---|---|
| 11,10,1,4 | [1,2] |
| 11,10,0,4 | [0,4] |
| 11,3,0,4 | [3,4] |
| 0,3,0,4 | [0,0] |
| 12,3,0,4 | [4,4] |
| 3,1,0,4 | [3,3] |
| 0,0,0,4 | [] |

단계 1 a~i, 단계 2 a~e, 단계 3 a~e, 단계 4 a~f, 단계 5 a~h, 단계 6 a~g, 단계 7 a~c는 모두 **미실행**이다.
`selfcheck` 통과는 공통 함수의 최소 확인일 뿐 전체 단계 완료를 뜻하지 않는다.

## 4. 성능·환경

- **200만 행 SYNTHETIC 성능은 미측정.** 단계 2~7이 미착수라 모듈별 시간·최대 메모리를 제시할 근거가 없다.
- 최종 pytest: 43개 중 42 통과 / 1 실패, 4.87초. 이 시간은 성능 벤치마크가 아니다.
- 소형 SYNTHETIC: 영문·한글 각각 48행, chunksize=3, 16청크, 고유 고객 12, 시각 오류 2.
- 실행 환경: Python 3.13.1, pandas 2.2.3, numpy 2.2.1. **Python 3.8에서 직접 실행하지는 않았다.**
- 반입 대상 코드와 생성기 11개 Python 파일은 `ast.parse(feature_version=(3,8))` 통과.
- rg import 점검 및 AST 점검: 표준 라이브러리·pandas·numpy·자체 lib 이외 외부 import 없음. pytest는 로컬 테스트만 사용.
- rg로 `:=`, match 구문, X|Y 형식 검색 결과 없음. dict 합집합 연산 미사용. 네트워크 호출 없음.

## 5. 생성·변경 파일

기준 경로: `C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회`

신규 구현:

- `analysis/visit2/config/visit2.json` — V2-00 §2 JSON 예시 복사, 자리표시자 유지
- `analysis/visit2/lib/__init__.py`
- `analysis/visit2/lib/config.py`
- `analysis/visit2/lib/io.py`
- `analysis/visit2/lib/timeparse.py`
- `analysis/visit2/lib/filters.py`
- `analysis/visit2/lib/distinct.py`
- `analysis/visit2/lib/suppress.py`
- `analysis/visit2/lib/manifest.py`
- `analysis/visit2/lib/stats.py`
- `analysis/visit2/selfcheck.py`
- `synthetic/visit2/make_synthetic.py`

신규 테스트·검증 자료:

- `tests/visit2/conftest.py`
- `tests/visit2/test_common.py`
- `tests/visit2/test_common_adversarial.py`
- `tests/visit2/test_stage0_tools.py`
- `tests/visit2/test_stage0_acceptance.py`
- `tests/visit2/fixtures/SYNTHETIC_secondary_group.csv`
- `tests/visit2/fixtures/SYNTHETIC_verify_stage0.py`
- `tests/visit2/fixtures/README.md`
- `.gitignore` 4개: `analysis/visit2/`, `synthetic/visit2/`, `tests/visit2/`, `tests/visit2/fixtures/` 아래
- `docs/visit2_implementation_log.md`, 이 보고서

자동 생성된 SYNTHETIC 실행 자료는 fixtures 아래에만 두고 Git에서 제외했다. 실제 두 CSV는 열어 구조를 확인했으며 수정하지 않았다. 기존 사용자 변경인 AGENTS.md, CLAUDE.md, docs/DECISIONS.md, 방문 계획 등은 수정하지 않았다. 커밋하지 않았다.

## 6. 실행 명령과 현장 설정

현재 실행 가능한 것은 **개발 검증 명령**뿐이다. 저장소 루트에서:

```powershell
pytest tests/visit2 -q
python analysis/visit2/selfcheck.py
python synthetic/visit2/make_synthetic.py --rows 48 --out tests/visit2/fixtures/SYNTHETIC_stage0
python tests/visit2/fixtures/SYNTHETIC_verify_stage0.py
```

첫 명령과 마지막 명령은 현재 각각 인수 실패와 관문 실패 때문에 **종료 코드 1**이 정상 재현 결과다.
모듈별 실행 명령·run_all·export_check는 스크립트가 미구현이므로 실행 가능 명령으로 제시하지 않는다.

현장에서 추후 고칠 키: `paths`, `columns.active` 및 활성 pay/shop 매핑, `encoding_candidates`, `chunksize`, `meal_pay_values`, `status_filter`, `period`, `regime`, `id_patterns`, `reference_exports`. `bootstrap.reps`는 시간 여건에 맞춰 명세 허용 범위 내에서 설정한다. 축 예외는 센터 확인 후에만 바꾼다. 억제·게이트 임계값은 결과를 보고 바꾸지 않는다.

향후 export_check FAIL 시 대처 3줄:

1. 해당 실행의 반출 신청을 보류하고 internal 점검 보고서를 확인한다.
2. 명세가 허용한 해상도 축소·반출 제외 또는 모듈 재실행으로 처리하며 결과 CSV를 손으로 고치지 않는다.
3. 과거 반출물까지 포함해 다시 점검하고 FAIL 0과 사람의 이중 점검을 확인한 뒤 신청한다.

## 7. Claude 리뷰 요약

### exposure_ranges와 suppress

1. 칸별 범위는 `[max(lo,S-(k-1)*hi), min(hi,S-(k-1)*lo)]`이며 S,k,lo,hi는 정수다.
2. k=0,S=0은 빈 목록, 음수·역전·불가능한 합계는 명시적 오류다.
3. 1차 억제 후 전체·margin_groups·known_totals를 검사하고, 좁아지면 같은 그룹의 공개 n 최솟값 칸을 추가 억제한다.
4. 공개 후보 소진·범위 불일치는 unresolved로 남기며 write_export가 거부한다.
5. 고유 수 미달·보완 억제 칸의 n이 hi보다 큰 문제는 임의 범위 확장 없이 차단했다. 이 때문에 성공 인수 관문이 막힌다.

### known_totals / 공개 합계 등록부

1. suppress는 명세의 `{(그룹 키 튜플, 값 튜플): 합계}`를 받는다.
2. writer는 공개 값만으로 완전히 합산 가능한 그룹의 n만 `internal/published_totals.json`에 기록한다.
3. population·원본 표·고정 분할 축을 기록하며 n_shop/n_cust는 합산하지 않는다.
4. 모듈 간 등록부 재로드와 시간·모집단 매핑을 포함한 통합 검증은 아직 수행하지 않았다.

### C8-lite

미구현. 이번 표와 1차 두 표의 n만 쌍별 비교하고, 과거 자체 노출 KNOWN과 신규 축소 FAIL을 나누는 단계 A는 미착수다.

### M2 가맹점 블록 부트스트랩

1. lib/stats의 순수 계산 함수만 구현·단위 검증했다. M2 파일은 미구현이다.
2. 같은 가맹점 순서의 두 행렬을 받고 가맹점 인덱스를 복원추출한다.
3. 두 G에 같은 bincount 가중치를 적용하며 분모 0 반복은 NaN, 유효 반복 수를 기록한다.
4. seed 재현성과 가맹점 1곳의 CI 폭 0을 확인했다.
5. 30곳 미만 CI 비공개·억제 결과 연동은 M2 호출부의 역할이며 아직 구현하지 않았다.

## 8. 확인 요청

**진행을 막는 항목:** V2-00 §3.6의 억제 칸 범위 정의와 §5 보완 억제 성공 기준을 확인해야 한다.

- SYNTHETIC `[1,9]`, 공개 합계 10에서 한 칸을 숨기면 정확히 복원된다. 다른 칸까지 숨겨도 두 칸 모두 `[0,4]`라는 전제를 적용하면 최대 합계가 8이라 모순이다.
- `n=100,n_shop=2` 같은 칸도 1차 억제 대상이지만 n은 `[0,4]`에 들어가지 않는다.
- 현재 인수 테스트는 §5의 성공을 **추가 억제 후 unresolved 없음**으로 해석했다. 이 입력은 거부가 정상이라는 뜻인지, 아니면 보완 억제에도 유효한 범위 계약을 고쳐야 하는지 확인이 필요하다. 인수 기대값은 임의로 완화하지 않았다.
- 보완 억제 사유별 범위가 공개되면 그것도 정보가 될 수 있어, 단순히 내부 실제값을 상한으로 쓰는 수정은 하지 않았다.

추가 확인:

- share 열의 분모 그룹이 suppress 인자에 명시되지 않았다. 임의로 추론하지 않고 `share_denominator_group_unspecified`로 거부한다. M4 share/LQ와 연결하기 전에 계약이 필요하다.
- `hour3=7`은 21~23시라 `23-05` 심야 구간에 통째로 대응하지 않는다. hour→hour3, hour→hour_bucket 순수 보조 함수만 제공했다. `ym→R` 역시 날짜 레짐이면 월 하나가 여러 레짐에 걸칠 수 있다.
- load_config(path)의 인자는 유지하고 M1의 자리표시자 예외는 별도 `load_discovery_config(path)`로 분리했다.
- M4 비교 순서는 명세대로 **L1,L2,L4,L3,L5**로 구현할 예정이며 Claude 확인이 필요하다(현재 미구현).
- M4 L1 분리는 **meal: 동×R×hour3 / share: 동×R**라는 명세를 확인해야 한다. 시간축을 없앤 share의 재집계·억제 방식도 구현 전 확인 대상이다.

## 9. 단계 B로 미룬 것

- 이번 반출물끼리의 포함 관계 탐색
- 여러 표 쌍에 걸친 범위 교집합·반복 전파
- `test_cross_module_chain`

이는 단계 A 미완과 별개로 원래 요청에서 제외한 항목이다.

## 10. 반입 목록

**현장 실행용 반입 승인 목록은 아직 없다. 아래는 현재 존재하는 코드 검토용 파일의 전체 경로다.** tests·synthetic·캐시는 제외했다.

```text
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\config\visit2.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\__init__.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\config.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\io.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\timeparse.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\filters.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\distinct.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\suppress.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\manifest.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\lib\stats.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit2\selfcheck.py
```
