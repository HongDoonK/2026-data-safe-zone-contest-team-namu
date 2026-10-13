# V3 Codex 검증 보고 — 2026-10-01

## 0. 생성·변경 파일 전체 경로와 재실행 명령

**SYNTHETIC: 이 보고서의 계산·예시·시간·메모리·픽스처 수치는 전부 합성 데이터에서 나온 값이다. 실데이터 결과·해석 문장을 만들지 않았다.**

전체 파일 목록(데이터·로그 포함): [SYNTHETIC_file_inventory.txt](<C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_file_inventory.txt>). 동일한 전체 절대 경로를 아래에도 남겼다.

PowerShell에서 저장소 루트 `C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회`를 작업 폴더로 사용한다. 네트워크 호출·커밋·푸시는 없다.

전체 검증 1줄(소형 oracle·청크·오류·P0·반출 점검·120만 행·200만 행·pytest·문서 생성):

```powershell
python -X utf8 analysis/visit3/validate.py --timing-rows 2000000
```

셀 하나만 1줄(필요한 선행 셀 자동 실행; 아래는 M5):

```powershell
python -X utf8 analysis/visit3/run_cells.py --cell M5 --tag review_M5
```

청크 시험 1줄(120만 행, 997행 청크; 원본 100만 행 로그와 전체 검증에서 비교):

```powershell
python -X utf8 analysis/visit3/run_cells.py --pay synthetic/visit3/data_SYNTHETIC/SYNTHETIC_pay_large.csv --chunksize 997 --tag review_chunk997
```

소형 데이터가 없으면 먼저 `python -X utf8 synthetic/visit3/make_synthetic.py`를 실행한다. `extract_cells.py --write`는 최초 추출용이고 다른 셀 파일을 덮어쓰지 않는다.

<details>
<summary>생성·변경 파일 전체 절대 경로</summary>

```text
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\.gitignore
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\A1.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\A2.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\A3.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\A4.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\M1.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\M2.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\M3.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\M4.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\M5.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\M6.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\P1.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\P1b.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\P2.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\P3.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells\S1.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells_optional\A3.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells_optional\M4.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\cells_optional\S1.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\extract_cells.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\oracle.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\run_cells.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\validate.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\analysis\visit3\write_reports.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\docs\visit3_codex_report.md
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\docs\visit3_error_dictionary.md
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\docs\visit3_output_examples.md
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\docs\visit3_typing_hazards.md
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_BOM.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_P0_A.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_P0_B.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_P0_B_initial.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_P0_C1.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_P0_C2.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_cp949.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_duplicate_shop.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_empty_table.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_large_manifest.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_pay_large.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_pay_small.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_pay_timing.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_shop.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_small_manifest.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\data_SYNTHETIC\SYNTHETIC_timing_manifest.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\make_synthetic.py
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_A\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_B\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C1\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_C2\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_conditions.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_P0_conditions_initial.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_diagnostics_prep\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_dtype_probes.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_duplicate_prep\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_duplicate_prep\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_duplicate_prep\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_duplicate_prep\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_duplicate_prep\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_empty_dataframe_example.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_empty_table_example\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_empty_table_example\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_empty_table_example\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_empty_table_example\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_empty_table_example\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_BOM_header\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_BOM_header\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_Y_typo\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_Y_typo\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_Y_typo\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_after_A1_P1b\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_after_A1_P1b\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_after_A1_P2\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_after_A1_P2\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_direct_column_typo\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_direct_column_typo\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_done_value_typo\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_done_value_typo\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_duplicate_shop\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_duplicate_shop\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_encoding\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_encoding\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_indent\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_indent\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_keyerror_typo\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_keyerror_typo\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_meal_value_typo\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_meal_value_typo\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_parenthesis\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_parenthesis\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_path_typo\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_path_typo\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_quote\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_quote\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_recovered\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_recovered\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_recovered\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_recovered\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_recovered\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_recovered\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_방학\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_방학\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_방학\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_방학\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_방학\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_전환\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_전환\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_전환\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_전환\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_전환\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_학기\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_학기\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_학기\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_학기\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_regime_학기\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_serviceN_typo\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_serviceN_typo\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_serviceN_typo\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_skip_order\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_skip_order\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_status01_typo\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_status01_typo\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_status01_typo\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_usecols_typo\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors\SYNTHETIC_usecols_typo\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_file_inventory.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_fixtureB_red.log
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_full_validation.log
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\EXPORT_m5_amount_hist_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_A4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_P3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_chunk997\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\EXPORT_m5_amount_hist_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_A4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_P3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_large_original\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\EXPORT_m5_amount_hist_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_A4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_P3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_optional\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_oracle.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_pytest.log
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_restart_M5\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\EXPORT_m5_amount_hist_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_A4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_P3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_chunk997\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\EXPORT_m5_amount_hist_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_A4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_P3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_original\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_small_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\EXPORT_m4_dong_regime_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\EXPORT_m4_dong_total_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\EXPORT_m4_u2_gungu_status_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\EXPORT_m5_amount_hist_SYNTHETIC.csv
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_A4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M4_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M4_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M5_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M5_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M6_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_M6_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P1b_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P1b_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P2_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P2_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P3_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_P3_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_S1_record.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_S1_stdout.txt
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_timing\SYNTHETIC_run.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_validation.json
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\tasks\README.md
C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\tests\visit3\test_visit3.py
```

</details>

## 1. 환경

실행: Python 3.13.1 / pandas 2.2.3 / numpy 2.2.1 / pytest 9.0.3 / Windows. Python은 `C:\Program Files\Python313\python.exe`다.
로컬 설치 환경만 사용했다. pandas 1.5.x 환경과 Python 3.8 실행기는 없어 실행하지 않았다. 네트워크 호출·추가 설치는 하지 않았다. 모든 .py의 Python 3.8 문법은 ast.parse(feature_version=(3,8))로 검사했다(3.8 실실행 검증과는 다르다).

계획서·체크리스트, visit2 세 폴더, 9_11·9_18 반출물의 실행 전후 SHA-256이 일치했다. 기존 작업 변경분은 보존했다. 해시는 SYNTHETIC_validation.json에 있다.

합성 입력: 고정 시드 1002, 소형 SYNTHETIC 766행·19개 결제수단·15/8열; 대형 SYNTHETIC 1,200,000행; 시간용 SYNTHETIC 2,000,000행. 경계 사례를 열거·반복했으며 실분포를 흉내 내지 않았다. 모든 입력은 UTF-8 문자열로 저장했다.

## 2. 셀별 판정

**원본 실행·정답 대조 통과와 반출 가능 판정은 별개다.** oracle은 csv 행 순회·Counter·set·NumPy로 별도 계산했다. 셀의 groupby 코드를 복사하지 않았다. 모든 셀 관측값과 CSV 4개를 소형에서 독립 대조했고, 청크 불변은 소형 및 120만 행에서 stdout와 CSV 바이트까지 비교했다.

| 셀 | 줄 수 | 동기화 | 실행 | 정답 대조 | 청크 불변 | 경고 | 결과 |
|---|---:|---|---|---|---|---|---|
| S1 | 9 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| P1 | 13 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| P1b | 1 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| P2 | 6 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| P3 | 12 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| M1 | 8 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| M2 | 13 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| M3 | 10 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| M4 | 9 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| M5 | 13 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| M6 | 12 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| A1 | 15 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| A2 | 7 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |
| A3 | 9 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과·선택 a 검토 |
| A4 | 4 | 일치 | 예외 없음 | 일치 | 일치 | 0 | 통과 |

현재 pytest: **26 passed**. 로그는 `C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_pytest.log`.
구조 확인: P1 19행 = 결제수단 수, P1b 26행(빈 ym 포함), M4 방학→전환→학기 순서. 실데이터 확인 숫자는 테스트에 쓰지 않았다. A1은 15줄 그대로다.

## 3. 발견한 문제와 수정 제안

원본 셀에서 예외 또는 명세 의도와 다른 계산은 발견하지 못해 **cells_proposed는 만들지 않았다.** A3 일반 건수 억제는 요청에서 정한 선택 변형 a로만 검증했다. 계획서·체크리스트는 고치지 않았다.

하네스 수정 두 건: Windows 메모리 측정에서 포인터 폭을 지정하지 않아 RSS가 0으로 기록된 것을 실패 테스트로 잡고 ctypes HANDLE 형식을 수정했다. 메모리 표는 수정 뒤 재측정값이다. P0 B 초기 픽스처에서 할인 양수 행을 복제해 C1과 겹칠 수 있던 문제는 실패 테스트 뒤 교정했다. B는 날짜 있는 이전 각 월에서 표지 비중 SYNTHETIC 1%이고 방학 건수만 늘어난다. 초기 근거는 SYNTHETIC_P0_conditions_initial.json·SYNTHETIC_P0_B_initial.csv·SYNTHETIC_fixtureB_red.log에 보존했다. 교정 뒤 해당 P0·오류 관측만 재시험했고 대형 전체 검증을 반복하지 않았다.

선택 변형의 최소 diff와 줄 수는 §9에 있다. 이는 채택 결정이 아니다.

## 4. 반출 전 점검 재현

소형 원본 출력과, 일부러 한 칸만 비운 별도 SYNTHETIC DataFrame 픽스처를 모두 검사했다.

| 체크리스트 §3 항목 | SYNTHETIC 원본 관측 / 별도 함정 검사 |
|---|---|
| 합계 행·원자료 ID 없음 | 원본 CSV 4개 모두 없음. 합계 행과 SHOP_ID 열을 넣은 함정은 각각 탐지 |
| k==1 동의 total 합계 공란 | SYNTHETIC k==1 동 2개가 모두 공란. 하나를 복원한 함정은 탐지 |
| 레짐별 빈칸 수 !=1 | SYNTHETIC 방학 1 / 전환 0 / 학기 1: 방학·학기를 보류 대상으로 탐지 |
| total 유효 억제 !=1 | SYNTHETIC 5 − (9 − 6) = 2; regime에 존재하는 억제 동을 직접 세어도 2. 한 칸 함정 탐지 |
| total shops 공란 !=1 | SYNTHETIC 3칸; 별도 1칸 함정 탐지 |
| u2 공란 !=1 | SYNTHETIC 4칸; 별도 1칸 함정 탐지 |
| amount 급식 n 공란 !=1 | SYNTHETIC 2칸; 별도 1칸 함정 탐지. 일반 전용 구간의 n 결측도 원본 체크리스트 식에 포함됨 |
| amount 일반 5미만 잔존 | SYNTHETIC n_general 1건인 구간 1개가 그대로 남음. 선택 a 적용 후 잔존 0개 |
| 동 이름 반출 승인과 내용 일치 | 로컬에서 승인 여부 확인 불가. 원본의 이름 키가 포함된 것은 검사했고 승인 여부는 확인 요청 |

위 점검은 체크리스트 §3 재현이다. 가능한 모든 표 간 연립 역산을 증명하는 검사로 확대하지 않았다. 특히 레짐·U2의 기존 공개 합계는 합성값과 직접 비교하지 않고 '합계가 공개돼 있을 때 한 칸 공란이 역산됨'이라는 구조만 시험했다.

## 5. P0 판정 픽스처 조건 확인

판정 자동화 함수는 만들지 않았다. 테스트는 체크리스트 §2 순서에서 볼 조건만 확인한다. A/B/C는 픽스처 기대 라벨이며 실데이터 판정이 아니다.

| SYNTHETIC 픽스처 | 확인한 조건 | 결과 |
|---|---|---|
| A | 날짜 있는 이전 표지 0, 2023-06~12 급식 표지 있음 (모두 SYNTHETIC) | 조건 통과 |
| B | 17개월 반복, 방학 표지 건수 2 대 학기 1, 이전 행복페이 각 월 표지 비중 1%; 두 해 방학 비중이 카드보다 큼 (모두 SYNTHETIC) | 조건 통과 |
| C1 | 급식 외 카드 행의 표지 비중 100%; C 우선 조건 (모두 SYNTHETIC) | 조건 통과 |
| C2 | 2023-06~12 급식 표지 0; 이전 표지가 없어도 C 우선 조건 (모두 SYNTHETIC) | 조건 통과 |

빈 ym의 급식 취소 표지는 이전 기간 증거로 세지 않았다. '흔함'과 '거의 0'의 정량 경계는 원문에 없으므로 임의로 판정 기준을 추가하지 않았다. B의 1%는 픽스처 성질일 뿐 판정 임계값이 아니다.

## 6. 오류 사전 요약

조용한 실패 우선 점검: ① MEAL·DONE 오타(M2 0행) ② 레짐 문자열 오타(M2 건수는 그대로, M4 이름·순서 대조) ③ 01·N 오타(U2 총수 그대로, live만 바뀜; 고정 기대값이 없어 직접 문자열 대조 필요).
컬럼 usecols 오타·직접 컬럼 오타·KeyError·경로·cp949·BOM·괄호·따옴표·들여쓰기·셀 건너뜀·SHOP_ID 중복을 실제 재현했다. 오류 마지막 줄과 최소 수정 줄은 [오류 사전](visit3_error_dictionary.md)에 있다.

A1 뒤 P1b·P2 재실행과 커널 재시작 뒤 M5 단독 실패를 기록했으며, 의존 셀을 다시 실행하면 복구됐다.

## 7. 버전 위험 — 셀·줄 단위

| 줄 | pandas 2.2.3 실제 관측 | pandas 1.5.x |
|---|---|---|
| M4:5 | 정수 열→float64, 경고 0·예외 없음 | 미실시 |
| M5:8 | 정수 열→float64, 경고 0·예외 없음 | 미실시 |
| M6:9 | 정수 열→float64, 경고 0·예외 없음 | 미실시 |
| A3:6 | 정수 열→float64, 경고 0·예외 없음 | 미실시 |

15셀 전체 및 120만·200만 행 실행에서 경고는 없었다. SettingWithCopyWarning·FutureWarning이 다른 환경에서도 없다는 뜻은 아니다. 경고 카테고리·파일·줄을 저장하는 경로는 구현했다. pandas 1.5.x와 Python 3.8의 실제 실행 결과는 주장하지 않는다.

## 8. 셀별 시간·메모리 — SYNTHETIC

셀 exec만 측정했다(로그 쓰기·oracle·관측 스냅샷은 시간에서 제외). 메모리는 Windows Working Set을 10ms 간격으로 표본 측정한 셀 구간 최대이며, 프로세스 누적 PeakWorkingSetSize도 JSON에 별도 저장했다. 표본 사이의 순간 최대는 놓칠 수 있다. 같은 프로세스의 이전 셀 메모리가 포함된다.
PC RAM은 약 8GiB, 시작 시 가용 약 253MiB였다. 스왑과 소요 시간 부담을 줄이기 위해 허용된 SYNTHETIC 200만 행 대안을 썼다. 800만 행은 직접 실행하지 않았다.

| 셀 | SYNTHETIC 120만 행 초 | SYNTHETIC 120만 행 최대 MiB(표본) | SYNTHETIC 200만 행 초 | SYNTHETIC 200만 행 최대 MiB(표본) |
|---|---:|---:|---:|---:|
| S1 | 0.022 | 99.4 | 0.025 | 144.2 |
| P1 | 2.266 | 208.4 | 4.272 | 247.4 |
| P1b | 0.002 | 137.8 | 0.002 | 194.2 |
| P2 | 0.011 | 137.8 | 0.011 | 194.2 |
| P3 | 1.902 | 249.2 | 3.543 | 295.0 |
| M1 | 0.010 | 178.1 | 0.017 | 268.8 |
| M2 | 2.273 | 410.9 | 4.536 | 572.7 |
| M3 | 1.908 | 487.5 | 3.293 | 701.2 |
| M4 | 0.176 | 453.5 | 0.349 | 711.3 |
| M5 | 0.199 | 432.9 | 0.274 | 694.4 |
| M6 | 0.041 | 302.3 | 0.072 | 619.9 |
| A1 | 7.198 | 721.7 | 11.529 | 1225.3 |
| A2 | 0.065 | 578.0 | 0.144 | 974.3 |
| A3 | 0.072 | 589.5 | 0.123 | 990.4 |
| A4 | 0.077 | 591.7 | 0.141 | 1008.9 |

| 모듈 | SYNTHETIC 200만 행 실행 초 | 800만 행 비례 추정 초(미실측) | 계획서 시간 |
|---|---:|---:|---|
| P0 | 7.83 | 31.31 | 30분 |
| M4 | 8.54 | 34.16 | 90분 |
| H5 | 11.94 | 47.75 | 60분 |

비례 추정은 실행시간만 4배로 계산했다. 메모리는 800만 행으로 비례 외삽하지 않았다. 반복 합성 데이터는 고유 계정·가맹점이 적어 실데이터의 메모리를 낮게 보일 수 있다. 계획서 예산은 타이핑·확인·현장 PC·반출 신청 시간을 포함하므로 위 초 단위 측정으로 현장 시간 여유를 단정할 수 없다. P3·A4는 현장 선택 셀이지만 검증에서는 모두 실행했다.

## 9. 선택 변형 a·b·c — 결정 대기

### a. 일반 건수 억제

A3 9줄→10줄, 예외 없음. 원본 cells/는 그대로다. 추가 1줄. SYNTHETIC n_general<5 잔존 1개→0개. amount CSV만 변경. head(30) 밖의 구간이라 이 픽스처에서는 stdout은 같았다.

```diff
--- cells/A3
+++ cells_optional/A3
@@ -4,6 +4,7 @@
 e = hm.join(hg, how="outer")
 bad = (e.n < 5) | (e.n_cust < 5)
 e.loc[bad, ["n", "n_cust"]] = np.nan
+e.loc[e.n_general < 5, "n_general"] = np.nan
 e.index.name = "tot_amt_bin500"
 e.to_csv("EXPORT_m5_amount_hist.csv", encoding="utf-8-sig")
 print(e.head(30).to_string())
```

### b. 레짐별 억제 칸 수 출력

M4 9줄→10줄, 예외 없음. 원본 cells/는 그대로다. 추가 1줄. SYNTHETIC 방학 1·전환 0·학기 1을 stdout에 출력. CSV 변경 없음.

```diff
--- cells/M4
+++ cells_optional/M4
@@ -4,6 +4,7 @@
 tt = t.copy()
 tt[bad] = np.nan
 tt.to_csv("EXPORT_m4_dong_regime.csv", encoding="utf-8-sig")
+print("레짐별 억제:", bad.groupby(level=1).sum().to_string())
 k = bad.groupby(level=0).sum()
 print("억제 칸이 정확히 1개인 동:", int((k == 1).sum()))
 print(t.groupby(level=1).n.sum().to_string())
```

### c. pandas 버전 출력

S1 9줄→10줄, 예외 없음. 원본 cells/는 그대로다. 추가 1줄. stdout에 pandas 2.2.3 추가, CSV 변경 없음. 로컬 버전 의존 경고·오류는 확인되지 않아 위험 대응 효과는 미확인.

```diff
--- cells/S1
+++ cells_optional/S1
@@ -7,3 +7,4 @@
 MEAL, DONE = ["아동급식카드"], "완료"
 print(pd.read_csv(PAY, nrows=1, encoding=ENC, dtype=str).columns.tolist())
 print(pd.read_csv(SHOP, nrows=1, encoding=ENC, dtype=str).columns.tolist())
+print("pandas:", pd.__version__)
```

## 10. 미실시 항목과 이유

- pandas 1.5.x 및 Python 3.8 실실행: 로컬 실행 환경이 없고 네트워크·추가 설치를 사용하지 않았다. 2.2.x는 로컬 2.2.3으로 실행했다.
- SYNTHETIC 800만 행 실측: 시작 시 가용 메모리가 적어 200만 행 실측 및 실행시간 4배 비례 추정으로 대체했다.
- 실제 안심구역 PC 성능·동 이름 반출 승인: 접근 권한이 없어 로컬에서 확인할 수 없다.
- cells_proposed 재검증: 해당 없음. 원본 셀 계산·실행 버그가 없어 제안판을 만들지 않았다.
- 모든 누적 반출물의 일반 연립 역산 탐색: 이번 범위는 체크리스트 §3의 구조적 점검 재현이다.

요청 항목 1~12는 위 대체·한계 범위 안에서 기록했다. 개선 목적 반복 실행·임계값 변경·해석 보고서·판정 자동화·visit2 수정·커밋·푸시는 하지 않았다.

## 11. Claude에게 확인 요청

1. 선택 a(A3 일반 5미만 억제), b(M4 레짐별 억제 수 출력)를 원본에 반영할지 결정한다. 원본은 수정하지 않았다.
2. 방학/학기에서 억제 칸이 각각 SYNTHETIC 1개인 원본 출력은 체크리스트상 보류 대상이다. 실제 현장에서도 점검 후 보류·보완 여부를 설계 담당이 정해야 한다.
3. P0의 '흔함'·'거의 0'에 정량 경계가 없어 자동 판정하지 않았다. 테스트는 극단·경계 성질만 확인했다. B 표지 비중 SYNTHETIC 1%를 판정 임계값으로 사용하지 않는다.
4. 01·N 오타는 live의 고정 기대값으로 잡을 수 없다. 현장 인쇄본의 문자열 대조를 담당자가 수행해야 한다.
5. 동 이름 반출 승인, 원본에 없는 군구+번호 대체 셀, pandas 1.5.x 실제 동작은 로컬에서 확정하지 않았다.
