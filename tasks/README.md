# tasks/ — Codex 작업 명세 목록

> 작성: Claude, 2026-09-18. 근거: [docs/topics/T2_visit2_plan.md](../docs/topics/T2_visit2_plan.md) §4~§5.
> Codex는 작업 전 [AGENTS.md](../AGENTS.md)를 읽는다. 이 폴더의 명세와 AGENTS.md가 충돌하면 AGENTS.md가 우선한다.

## 2차 방문(V2) 스크립트 묶음

**목표 시한: 2026-09-21(일)까지 합성 데이터로 끝까지 실행 가능.** 2차 방문 목표일은 9/22~23이다.

| 순서 | ID | 파일 | 내용 | 의존 |
|---|---|---|---|---|
| 1 | **V2-00** | [V2-00_common_infra.md](V2-00_common_infra.md) | 설정·로더·시간 파생·억제 함수·실행 기록·합성 데이터 | — |
| 2 | **V2-M0** | [V2-M0_filter_reproduce.md](V2-M0_filter_reproduce.md) | 헤더 확인, 1차 반출 필터 재현, 필터 정의 기록 | V2-00 |
| 3 | **V2-M1** | [V2-M1_paygbn_meaning.md](V2-M1_paygbn_meaning.md) | 지급구분 전체 값·월 교차표, 게이트 재계산 | V2-00 |
| 4 | **V2-M2** | [V2-M2_comparison_h1.md](V2-M2_comparison_h1.md) | 급식 vs 일반 비교군, 가맹점 내 대조, 부트스트랩 CI | V2-00, M0 |
| 5 | **V2-M3** | [V2-M3_shop_join.md](V2-M3_shop_join.md) | 가맹점 테이블 프로파일, 결제⋈가맹점 결합 | V2-00, M0 |
| 6 | **V2-M4** | [V2-M4_spatial_publishability.md](V2-M4_spatial_publishability.md) | 공간 단위 공표 가능성 사다리, 군구·동 집계 | V2-00, M0, M3 |
| 7 | **V2-07** | [V2-07_export_check.md](V2-07_export_check.md) | 반출 전 누적 점검: ID·축·억제 기준 + **과거 반출물까지 포함한 억제값 역산 점검** | V2-00, M0~M4 |

M5(금액)·M6(결합 사전 진단)은 선택 모듈이라 이번 묶음에 넣지 않았다. 필요하면 별도 명세를 쓴다.

## 모든 V2 작업의 공통 규칙

1. **실행 환경**: 안심구역 PC. 인터넷 차단, 설치 가능 라이브러리 미확인 → **Python 표준 라이브러리 + pandas + numpy만** 사용. 3.8에서도 돌아가는 문법(`match`, `X | Y` 타입 표기 금지).
2. **디렉터리 구조**

   ```text
   analysis/visit2/
     config/visit2.json          ← 현장에서 고치는 유일한 파일
     lib/                        ← V2-00 공통 모듈
     00_headers.py
     10_m0_reproduce.py
     20_m1_paygbn.py
     30_m2_compare.py
     40_m3_shop.py
     50_m4_space.py
     export_check.py             ← V2-07 반출 전 누적 점검
     promote_internal.py         ← internal → export 수동 승격 (사유 필수)
     reference/                  ← 1차 반출물 JSON + reference_meta.json
     run_all.py                  ← 순서대로 실행, 한 단계 실패 시 중단
     selfcheck.py                ← pytest 없이 도는 최소 검증
   tests/visit2/                 ← 로컬 pytest
   synthetic/visit2/             ← SYNTHETIC 합성 CSV (V2-00이 생성)
   ```

3. **출력은 두 갈래로 나눈다**
   - `out/<run_id>/export/` — **반출 후보.** 억제를 통과한 집계표 + `filter_definition.txt` + `run_manifest.json`만
   - `out/<run_id>/internal/` — **절대 반출 금지.** 억제 전 표, 점검 로그, 행 수준 샘플 확인 결과
   - 스크립트가 `export/`에 쓰는 모든 표는 `lib.suppress`를 통과해야 한다. 우회 경로를 만들지 않는다.
4. **억제는 표 하나가 아니라 반출물 전체 기준이다** (방문 계획 §9 A1·A10). 0 칸은 억제 칸과 구별되지 않게 표시(`zero_policy="mask"`)하고, 급식 시간 단위 표는 23~05시를 합치며, 비중 열은 반출하지 않는다. 모든 export는 공개 합계 등록부로 노출 점검을 거치고, 반출 신청 전 `export_check.py`(V2-07)가 과거 반출물까지 함께 다시 본다.
5. **키 축은 3개까지** (§9 A3). 4축이 되는 표는 파일을 나눈다. 센터가 시간 축만의 4축을 허용하면 설정 `export.time_only_axes_exception`만 바꾼다.
6. **판정은 사람이 한다.** 스크립트는 판정에 필요한 표와 사전 등록 규칙의 기계적 적용 결과만 출력한다. 해석 문장을 쓰지 않는다.
7. **완료 보고** (AGENTS.md §4-9): 생성·변경 파일, 합성 데이터 실행 결과, 발견한 문제, 미해결 이슈. 합성 데이터로 나온 수치는 보고서에 **SYNTHETIC**으로 표시한다.

## 3차 방문(V3) — 손타이핑 셀 검증

3차 방문은 코드 반입이 불가하다. 팀은 [docs/topics/T2_visit3_plan.md](../docs/topics/T2_visit3_plan.md) §2~§5를 인쇄해 손으로 친다. 그래서 V3는 새 파이프라인을 만들지 않고, **계획서 셀을 글자 그대로 합성 데이터에 실행해 1회 검증**한다.

| ID | 파일 | 내용 |
|---|---|---|
| **V3** | [V3_codex_prompt.md](V3_codex_prompt.md) | 셀 15개(S1·P1·P1b·P2·P3·M1~M6·A1~A4)의 동기화·순서 실행·정답 대조·청크 불변·반출 점검 재현·오류 사전 |

- 산출물 경로: `analysis/visit3/`, `synthetic/visit3/`, `tests/visit3/`
- 보고서: `docs/visit3_codex_report.md`, `docs/visit3_error_dictionary.md`, `docs/visit3_output_examples.md`, `docs/visit3_typing_hazards.md`
- 계획서·체크리스트는 Codex가 고치지 않는다. 수정 제안은 `analysis/visit3/cells_proposed/`에 두고, Claude가 리뷰한 뒤 반영한다.

## Status

- 2026-09-18: V2-00, V2-M0~M4 명세 작성. 구현 전.
- 2026-10-01: V3 프롬프트 작성(손타이핑 셀 검증). 구현 전.
- 2026-09-18: 방문 계획 §9 A1·A2·A3·A10 반영 — 억제를 노출 점검 기반으로 교체(V2-00), 0 칸 마스킹·심야 합치기·비중 열 제거·G별 파일 분할(M0·M1·M2), 심야 절벽 진단표 T2-f 추가(M2), 누적 점검 V2-07 신설.
- 2026-10-01: V3 Codex 검증 완료 — 원본 15셀 동기화·예외 0·독립 정답·120만 행 청크 불변, pytest 26 passed; 억제 위험·선택 변형·미실시 항목은 [검증 보고](../docs/visit3_codex_report.md) 참조.
