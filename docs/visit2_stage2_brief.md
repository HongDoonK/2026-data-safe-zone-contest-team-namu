# 단계 2: M1과 모듈 실행 공통 연결

요구사항: AGENTS.md/CLAUDE.md, tasks/V2-M1_paygbn_meaning.md 전체와 tasks/V2-00_common_infra.md. 먼저 모두 읽을 것. 구현 순서 stage0→stage1→M1이며 root가 앞 관문 통과 후에만 이 작업을 시작시킨다.

담당 파일: analysis/visit2/20_m1_paygbn.py, analysis/visit2/lib/pipeline.py, analysis/visit2/lib/m1.py, tests/visit2/test_m1.py. lib/config/distinct/timeparse/suppress/manifest/stats 등의 기존 API는 되도록 수정하지 않고, 필요한 변경은 root에 즉시 알린다. 다른 모듈 파일은 만들지 않는다.

공통 pipeline 인터페이스(후속 M0/M3/M2/M4 재사용):
- open_context(cfg, run_path=None) -> RunContext. run_path 있으면 같은 run의 export/internal와 등록부를 읽어 이어서 사용, 없으면 start_run. 기존 결과 덮어쓰기 금지.
- read_pay(cfg, usecols=None) -> chunk iterator: dtype=str/strip/usecols/chunksize IO→add_time_fields. nrows/readtimeinvalid 등은 모듈에서누적.
- population(cfg, kind='meal', subset=None) -> deterministic hash+kind identifier (필터/기간/급식값/부분집합 반영). 메타 population_kind 반드시 함께 넣는다.
- aggregate 클래스: CountAccumulator+DistinctAccumulator를 활용하여 .update(df), .finalize() => keys+n+n_shop+n_cust, 누락ID를유일ID로세지말것. 작은 fixed SYNTHETIC뿐아니라 청크간exact distinct.
- emit(ctx, df, name, keys, kind='meal', ..., suppression overrides) -> 공개 결과/거부 정보. 반드시 ctx.known_totals(meta)를 suppress에 넘기고 write_export를 통과. unresolved 정상거부는 internal에 structured명시, console 실제숨김값출력금지. 거부를 공개 성공으로 표시하지말고 결과 summary에 rejected_tables 기록. run_manifest도finish.
- CLI --config REQUIRED --run OPTIONAL. M1은 discovery설정허용. config/error시traceback없이message와exit1, 정상거부경로는 처리자체성공하되반출불가표목록명시. 다른 예외조용히삼키지말것.

M1 구현 상세는 원명세 그대로. T1-a 값별 보조첫월/마지막/방학비중 등도 억제시 숨긴다. all months grid, T1-b show only, T1-b의 공개 합계와 T1-a banded fallback/월별제외 trace 내부기록. T1-a 확정은마지막. T1-b wide는 안전한 long 결과와 같은마스킹을재사용하되 suppress/write_export 관문유지(독립재억제금지, 순수형태변환 검증 helper설계 필요). 구현방식모호하면 더 적게공개하고보고. T1-c top15원자료셋은이미 distinct누적했던자료재사용해 추가패스최소화; 결과값자동선택금지. T1-d Gate정확식은설계서§4.2상수로literal.

필수 테스트(손계산 가능한 fixtures SYNTHETIC):
- A~202305→B202306 gap1 공통고객·가맹점 교집합기대값
- 3값×4월 12행zero격자
- 희귀값7건(0,3,4 같은분산) T1-b노출→T1-a banded→재점검(or명세허용제외) 순서
- meal 미설정 1~3실행4건너뜀
- gate N100000,SHOP500,MONTHS18 → branch_count_true0/규칙상미정
- 월별max와다른전기간unique SHOP
- CLI small실행 export_check FAIL0 (reference_exports:null 지원)

기존 config JSON은원예시보존. 테스트때 case_dir fixture만사용해customjson세팅. synthetic/visit2/SYNTHETIC_config_en.json 및 kojson에2m파일준비돼있음:성능은root측정. test 파일명/데이터명SYNTHETIC조건. Python3.8, stdlib+pandas+numpy only. pvalue/rawID public금지. n_shop/n_cust합산금지. 결과해석/주제변경/추가subagent/커밋금지. 상세보고 docs/visit2_stage2_agent_report.md 작성 후짧게반환.

주의: 사용자 2026-09-18 승인대로큰칸보완억제범위불일치 unresolved→write_export거부는정상이다. 반출후보를 손으로고쳐통과시키지않는다. 명세와판정양립불가면더적게공개하고명확히기록한다.
