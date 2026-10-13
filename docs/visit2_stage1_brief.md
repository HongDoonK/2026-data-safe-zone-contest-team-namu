# 단계 1 구현 작업 범위

요구사항 원본: tasks/V2-07_export_check.md 전체(특히 §1.5 단계 A), tasks/V2-00_common_infra.md §3.3/3.6/3.7. AGENTS.md와 CLAUDE.md도 읽을 것. 원본 CSV는 읽기만.

담당 파일: analysis/visit2/export_check.py, 필요한 lib/timeparse.py 보조 함수 추가, tests/visit2/test_export_check.py. 다른 구현 파일은 변경하지 말 것. reference JSON과 selfcheck는 주 에이전트 담당.

구현할 CLI: python analysis/visit2/export_check.py --config analysis/visit2/config/visit2.json --run <run_folder> [--reference-only]. --reference-only는 빈 export FAIL과 과거 두 표만 검사하는 요구를 구분하는 명시적 검증 모드이다. --past는 단계 B 미지원이면 명확히 거부(조용히 무시 금지).

reference는 list-of-records JSON. 열명 ym/dow/hour/n/n_shop/n_cust. 수치는 원본 2063.0같은 JSON 숫자, ym은 원본 YYYY-MM 문자열 유지, dow='와'만 '화'로 수정, hour는 원본 숫자, 누락값 null. 기준 경로는 visit2 아래이며 reference_meta.json은 명세 그대로. 9_11 CSV는 절대 수정하지 않는다.

필수 C1~C7,C9,C8-lite. C8는 n만, 각 신규 표와 두 reference만 비교. 단계 B 표간 연쇄 전파 구현 금지. 기존 과거자료 노출은 KNOWN, 신규로 더 좁아지면 FAIL. 리포트는 internal/export_check_report.txt, 콘솔은 한 화면, 실패시 exit1. 억제 실제값이나 ID 문자열을 리포트/콘솔에 출력하지 말 것. 파일명/헤더/키도 ID형식이면 마스킹.

API는 check_run(config_path, run_path, reference_only=False) -> 결과 객체(문서화)와 check_references(cfg) -> 결과 객체를 제공하면 root selfcheck에서 사용. export_check 설정 로드는 full load_config가 meal placeholder를 거부하므로 이 도구에 필요한 suppression/export/reference_exports/id_patterns만 별도 검증해도 된다. 입력 CSV는 utf-8-sig/utf-8만 허용: cp949는 크래시 없이 C3 FAIL. width mismatch는 csv.reader strict+열수 확인, 빈 export명확FAIL, 메타/status 없는표FAIL. id_patterns 자리표시자: 일반실행FAIL, reference-only에서는 해당 검사N/A.

표 모집단 해시만으로 급식 여부를 판별할 수 없으면 conservative meal 취급. meta에 추가 population_kind='meal'/'general'/'mixed'/'shop'/'diagnostic'를 향후 모듈이 전달할 예정. 원본 unknown은 급식표와만 가능한 동일모집단으로 대조. G열이나 fixed_keys.G로 부분집합 구분. 단순 부분표를 전체표와 합계 같다고 가정하지 말 것. 서로 확실히 불일치하는 population은 비교하지 않음. 비교 불가능·메타 부족은 silent pass 금지, WARN 또는 FAIL 구분 기록.

시간키 hour, hour3, hour_bucket, ym/R(월모드만) 매핑을 timeparse에 공유. hour3=7은 21~23으로 night과 교차하므로 결정적 hour3→night 매핑은 없음. 대응이 명확한 경우만 쌍 비교. 양방향 범위 계산으로 옛/새 숨김칸 모두 고려. 과거표에서 이미 알 수 있는 새 집계 범위는 추가노출 아님(기존 공개정보와 신규 정보 차이 구분).

필수 테스트:
1. test_0911_known: reference두표만 FAIL0, week_hour10칸 KNOWN 각[1,2], exit0.
2. test_new_table_narrows_known: 1차+금23 한칸공개 → C8 FAIL (C4/C6에 의존해서 통과시키지 말 것).
3. test_night_bucket_safe: 과거와 동일 주간값, 7요일 night23-05 bucket 모두 마스킹, FAIL0.
4. ID 문자열이 셀 및 열 이름에 → 각각 C2 FAIL. 보고서 미유출.
5. dong있는4축+예외true → C5 FAIL.
6. status없음, meta없음, 허용외status각 C3 FAIL.
7. 급식23시개별 → C6 FAIL.
8. 빈폴더, 깨진CSV열수, cp949 → 크래시없이명확FAIL.
9. exposure 경계는 기존함수만 import. n_shop/n_cust합산 금지.

테스트 먼저 작성해 실패 확인 후 구현. synthetic는 tests/visit2/fixtures 내부SYNTHETIC 파일/폴더만. 네트워크 없음, Python3.8 문법, stdlib+pandas+numpy. 기존 tests/visit2/conftest.py의 case_dir 사용. 개발 테스트 실행후 세부 결과와 해결못한 모호함을 docs/visit2_stage1_agent_report.md에 기록. 추가 에이전트 생성·커밋·전체 계획 재작성 금지. 요약만 반환.

사용자 결정: 보완 억제로 가려진 큰 칸을 명세 범위로 표현할 수 없으면 unresolved와 write_export 거부는 정상이다. stage0 테스트43개와 selfcheck 모두 통과한 상태. 이것을 이유로 멈추지 말고 fail-closed 처리.
