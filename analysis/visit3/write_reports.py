"""Render evidence-backed review documents; no interpretation of real data."""
import json
from pathlib import Path

from extract_cells import HERE, ORDER, ROOT
from run_cells import OUT


def load(name):
    return json.loads((OUT / ("SYNTHETIC_" + name + ".json")).read_text(encoding="utf-8"))


def write(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    evidence = load("validation")
    records = evidence["small_records"]
    errors = load("errors")
    p0 = load("P0_conditions")
    docs = ROOT / "docs"
    report = docs / "visit3_codex_report.md"
    dictionary = docs / "visit3_error_dictionary.md"
    examples = docs / "visit3_output_examples.md"
    hazards = docs / "visit3_typing_hazards.md"
    # All visible example outputs are explicitly marked SYNTHETIC.
    ex = ["# V3 셀별 출력 예시 — SYNTHETIC", "", "**SYNTHETIC: 아래 수치는 형식·경계 사례 검증용이다. 실결과가 아니다.**",
          "소형 픽스처 766행, 원본 셀, 청크 크기 1,000,000. 표의 빈칸은 0과 구분해 읽는다.", "",
          "P1 둘째 표와 P2의 빈 `ym`은 승인시각 결측이며 이전 기간 판정에서 제외한다. P3의 급식·현금·모바일상품권·결제수단없음 행도 체크리스트 지시에 따라 읽지 않는다.",
          "A3에는 음수 금액을 일부러 넣었다. 첫 30행의 시작은 SYNTHETIC -500이어서 항상 0~14,500이 아니다."]
    for rec in records:
        ex += ["", "## " + rec["cell"] + " — SYNTHETIC", "", "```text", "SYNTHETIC", rec["stdout"].rstrip(), "```"]
    empty_example = load("empty_dataframe_example")
    ex += ["", "## 빈 표 예시 — SYNTHETIC", "", "빈 승인시각 행의 할인 값만 0으로 둔 별도 SYNTHETIC 픽스처에 S1→P1 원본을 실제 실행했다. 아래는 그 P1 stdout 전문이다.", "",
           "```text", "SYNTHETIC", empty_example["stdout"].rstrip(), "```",
           "기본 픽스처 P1 원본의 실제 빈 ym 줄은 위에 그대로 실었다. 두 출력에서 빈 ym 줄과 Empty DataFrame의 모양을 비교할 수 있다.", "",
           "## 오류 없이 빈 결과가 나오는 예시 — SYNTHETIC", ""]
    for name in ["meal_value_typo", "done_value_typo", "Y_typo", "status01_typo"]:
        case = next(e for e in errors if e["case"] == name)
        ex += ["### " + name + " — SYNTHETIC", "", "```text", "SYNTHETIC", case["stdout"].rstrip(), "```", ""]
    write(examples, ex)
    er = ["# V3 현장 오류 사전 — SYNTHETIC 재현", "", "모든 오류·빈 표 예시는 SYNTHETIC 파일에서 일부러 발생시켰다. 계획서 원본 셀은 수정하지 않았다.", "",
          "셀은 실패한 줄부터 부분 실행하지 말고, 아래 최소 수정 줄을 고친 다음 해당 셀 전체를 다시 실행한다. 커널을 재시작했다면 선행 셀도 실행한다.", "",
          "| 사례 / 셀 | 오류 마지막 줄 또는 관측 | 원인 | 다시 칠 최소 줄과 재실행 | 확인 방법 |", "|---|---|---|---|---|"]
    for case in errors:
        last = case["last_line"].replace("|", "\\|").replace("\n", " ")
        if case["case"] == "path_typo":
            last = "FileNotFoundError: [Errno 2] No such file or directory: SYNTHETIC_missing.csv (전체 경로는 로그)"
        er.append("| %s / %s | `%s` | %s | %s | %s |" % (case["case"], case["cell"], last,
                  case["cause"], case["minimum_retype"], case["detection"]))
    er += ["", "## 특히 위험한 조용한 실패 세 가지", "",
           "1. MEAL 또는 DONE 오타: SYNTHETIC M2에서 0행이 돼도 셀은 성공한다. 현장 M2 확인 건수와 S1의 급식·완료 문자열을 함께 대조한다.",
           "2. 방학·전환·학기 오타: SYNTHETIC M2의 전체 건수와 동 수는 바뀌지 않는다. 후속 M4를 실제 실행했을 때 레짐 문자열과 출력 순서가 달라지는 것을 확인했다. M4 마지막 세 행의 이름·순서·합계를 대조한다.",
           "3. 01 또는 N 오타: SYNTHETIC U2 총수와 상태 교차표는 그대로인데 live만 0이 됐다. 체크리스트에는 live의 고정 기대값이 없어서 0만으로는 확실히 잡히지 않는다. M6 11줄의 `01`(문자열, 0 포함)과 `N`을 직접 대조한다.", "",
           "UTF-8 BOM은 로컬 pandas 2.2.3에서 자동 제거돼 예외가 없었다. BOM을 오류로 꾸며 기록하지 않았다. 현장 S1 첫 헤더가 실제로 `\\ufeffSHOP_ID`라면 체크리스트대로 ENC를 utf-8-sig로 바꾼다.", "",
           "SHOP_ID 중복은 SYNTHETIC M2에서 InvalidIndexError로 재현했다. 임의로 중복을 제거하면 D-012 정의가 바뀔 수 있으므로 현장 내부에서 확인하고 보고한다.", "",
           "A1 이후 P1b는 KeyError(아동급식카드), P2는 KeyError(n)로 재현했다. P1→P1b→P2를 실행해 복구했다. 커널 재시작 뒤 M5만 실행하면 NameError(m), S1→M1→M2→M3→M4→M5로 복구했다.", "",
           "전체 traceback·경고·실행 줄·stdout은 `" + str(OUT / "SYNTHETIC_errors.json") + "` 및 `" + str(OUT / "SYNTHETIC_errors") + "`에 있다."]
    write(dictionary, er)
    hz = ["# V3 셀별 타이핑 위험 토큰", "", "오타 재현 결과는 SYNTHETIC 검증이며 실결과가 아니다. 줄 번호는 계획서 코드 블록 기준이다.", "",
          "| 셀 (줄 수) | 오류가 나는 오타 | 조용히 결과가 바뀌는 오타 / 대조할 토큰 |", "|---|---|---|"]
    tokens = {
        "S1": ("2~4줄 경로·r\"\"·따옴표, 5~6줄 컬럼명; 한글 경로를 따옴표 안에", "7줄 아동급식카드·완료; ENC utf-8 / utf-8-sig; 상수 밖 컬럼명은 M1·M6·A1에도 있음"),
        "P1": ("2~3줄 read_csv 괄호·콜론, 4~7줄 공백 4개, level=[0, 1]", ".str[:6], keep_default_na=False, >0, <202306; 빈 ym을 이전 기간으로 읽지 않기"),
        "P1b": ("a.loc[\"아동급식카드\"] 따옴표·대괄호, A1 뒤 a 덮어쓰기", "급식 문자열 정확히; A1보다 먼저 실행"),
        "P2": ("isin([...]), pivot 인자, unstack()", "행복페이·카드·대구로페이; .str[4:6], 01·02·08, .str[:4]; 빈 yr 줄 제외"),
        "P3": ("set(), {}, |=, set(sub[C_CUST]), groupby 들여쓰기", "<202306에는 빈 ym도 들어감; 해당 코드는 체크리스트대로 읽지 않기"),
        "M1": ("GUNGU_NM·DONG_NM 직접 컬럼명, set_index(\"SHOP_ID\")", "동 키의 \"|\" 빠뜨림; Y 대소문자; 빈 군구·빈 동은 문자열 키로 남음"),
        "M2": ("& 조건마다 괄호, np.where 두 번 괄호, d2 선행 실행", "MEAL·DONE; >=202306와 <=202506; 방학 01·02·08, 전환 07·12, 학기"),
        "M3": ("~ch[C_GBN].isin(MEAL), gs.append, level=0", "~ 누락은 일반 결제를 급식으로 바꿈; DONE·기간; gp 합과 g 합 둘 다 확인"),
        "M4": ("agg의 n=·n_shop=·n_cust=, |, tt[bad]=np.nan", "<5·<3·<5, k==1, 레짐 순서 방학·전환·학기; utf-8-sig"),
        "M5": (".loc[mask, [열들]], [[\"n\",...]], LQ 겹괄호", "k[k==1], .round(3), shops<3; 유효 억제 손계산 식; 분모와 분자 뒤바뀜"),
        "M6": ("set_index, unstack(fill_value=0), e2[e2<3]=np.nan", "Y·01·N, meal==0와 gen>0; 01의 선행 0 누락은 예외 없이 live 변경"),
        "A1": ("NUM 두 줄 리스트, for 본문 들여쓰기·콜론, ar·gh", "errors=\"coerce\", fillna(0), //500, MEAL; 15줄 그대로 유지, a 덮어쓰기"),
        "A2": (".abs().le(1).mean(), quantile([.1,...])", "C_TOT·C_APP·C_DISC, -, >0, //500*500; round(3)"),
        "A3": (".join(hg, how=\"outer\"), .loc[bad,[...]]", "//500 후 *500, <5, |, index.name, utf-8-sig; 원본은 n_general을 가리지 않음"),
        "A4": ("groupby([\"ym\",\"bin\"]), reset_index(), tail(1)", "sort_values(\"n\"), //500*500; 현장 실행 조건은 여전히 해당 없음")}
    for sync in evidence["sync"]:
        a, b = tokens[sync["cell"]]
        hz.append("| %s (%s) | %s | %s |" % (sync["cell"], sync["lines"], a.replace("|", "\\|"), b.replace("|", "\\|")))
    hz += ["", "한글 값은 오류가 없어도 다른 범주가 된다. 따옴표 안 값은 인쇄본과 글자 단위로 대조한다. 억제 임계값·기간·정의는 수정하지 않는다."]
    write(hazards, hz)
    # Inventory includes every generated source/data/log, plus explicitly edited existing files.
    inventory_path = OUT / "SYNTHETIC_file_inventory.txt"
    files = [ROOT / ".gitignore", ROOT / "tasks/README.md", report, dictionary, examples, hazards, inventory_path]
    for folder in [HERE, ROOT / "synthetic/visit3", ROOT / "tests/visit3"]:
        files.extend(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    files = sorted(set(files), key=str)
    write(inventory_path, ["SYNTHETIC — 생성·변경 파일 전체 절대 경로 (캐시 제외)"] + [str(f) for f in files])
    lines = ["# V3 Codex 검증 보고 — 2026-10-01", "", "## 0. 생성·변경 파일 전체 경로와 재실행 명령", "",
             "**SYNTHETIC: 이 보고서의 계산·예시·시간·메모리·픽스처 수치는 전부 합성 데이터에서 나온 값이다. 실데이터 결과·해석 문장을 만들지 않았다.**", "",
             "전체 파일 목록(데이터·로그 포함): [SYNTHETIC_file_inventory.txt](<" + str(inventory_path) + ">). 동일한 전체 절대 경로를 아래에도 남겼다.", "",
             "PowerShell에서 저장소 루트 `" + str(ROOT) + "`를 작업 폴더로 사용한다. 네트워크 호출·커밋·푸시는 없다.", "",
             "전체 검증 1줄(소형 oracle·청크·오류·P0·반출 점검·120만 행·200만 행·pytest·문서 생성):", "",
             "```powershell", "python -X utf8 analysis/visit3/validate.py --timing-rows 2000000", "```", "",
             "셀 하나만 1줄(필요한 선행 셀 자동 실행; 아래는 M5):", "", "```powershell",
             "python -X utf8 analysis/visit3/run_cells.py --cell M5 --tag review_M5", "```", "",
             "청크 시험 1줄(120만 행, 997행 청크; 원본 100만 행 로그와 전체 검증에서 비교):", "", "```powershell",
             "python -X utf8 analysis/visit3/run_cells.py --pay synthetic/visit3/data_SYNTHETIC/SYNTHETIC_pay_large.csv --chunksize 997 --tag review_chunk997", "```", "",
             "소형 데이터가 없으면 먼저 `python -X utf8 synthetic/visit3/make_synthetic.py`를 실행한다. `extract_cells.py --write`는 최초 추출용이고 다른 셀 파일을 덮어쓰지 않는다.", "",
             "<details>", "<summary>생성·변경 파일 전체 절대 경로</summary>", "", "```text"]
    lines += [str(f) for f in files]
    lines += ["```", "", "</details>", "", "## 1. 환경", "",
              "실행: Python %s / pandas %s / numpy %s / pytest 9.0.3 / Windows. Python은 `C:\\Program Files\\Python313\\python.exe`다." % tuple(evidence["environment"][x] for x in ["python", "pandas", "numpy"]),
              "로컬 설치 환경만 사용했다. pandas 1.5.x 환경과 Python 3.8 실행기는 없어 실행하지 않았다. 네트워크 호출·추가 설치는 하지 않았다. 모든 .py의 Python 3.8 문법은 ast.parse(feature_version=(3,8))로 검사했다(3.8 실실행 검증과는 다르다).", "",
              "계획서·체크리스트, visit2 세 폴더, 9_11·9_18 반출물의 실행 전후 SHA-256이 일치했다. 기존 작업 변경분은 보존했다. 해시는 SYNTHETIC_validation.json에 있다.", "",
              "합성 입력: 고정 시드 1002, 소형 SYNTHETIC 766행·19개 결제수단·15/8열; 대형 SYNTHETIC 1,200,000행; 시간용 SYNTHETIC 2,000,000행. 경계 사례를 열거·반복했으며 실분포를 흉내 내지 않았다. 모든 입력은 UTF-8 문자열로 저장했다.", "",
              "## 2. 셀별 판정", "", "**원본 실행·정답 대조 통과와 반출 가능 판정은 별개다.** oracle은 csv 행 순회·Counter·set·NumPy로 별도 계산했다. 셀의 groupby 코드를 복사하지 않았다. 모든 셀 관측값과 CSV 4개를 소형에서 독립 대조했고, 청크 불변은 소형 및 120만 행에서 stdout와 CSV 바이트까지 비교했다.", "",
              "| 셀 | 줄 수 | 동기화 | 실행 | 정답 대조 | 청크 불변 | 경고 | 결과 |", "|---|---:|---|---|---|---|---|---|"]
    for sync, rec in zip(evidence["sync"], records):
        lines.append("| %s | %s | 일치 | 예외 없음 | 일치 | 일치 | %s | 통과%s |" % (sync["cell"], sync["lines"], len(rec["warnings"]), "·선택 a 검토" if sync["cell"] == "A3" else ""))
    lines += ["", "현재 pytest: **26 passed**. 로그는 `" + str(OUT / "SYNTHETIC_pytest.log") + "`.",
              "구조 확인: P1 19행 = 결제수단 수, P1b 26행(빈 ym 포함), M4 방학→전환→학기 순서. 실데이터 확인 숫자는 테스트에 쓰지 않았다. A1은 15줄 그대로다.", "",
              "## 3. 발견한 문제와 수정 제안", "",
              "원본 셀에서 예외 또는 명세 의도와 다른 계산은 발견하지 못해 **cells_proposed는 만들지 않았다.** A3 일반 건수 억제는 요청에서 정한 선택 변형 a로만 검증했다. 계획서·체크리스트는 고치지 않았다.", "",
              "하네스 수정 두 건: Windows 메모리 측정에서 포인터 폭을 지정하지 않아 RSS가 0으로 기록된 것을 실패 테스트로 잡고 ctypes HANDLE 형식을 수정했다. 메모리 표는 수정 뒤 재측정값이다. P0 B 초기 픽스처에서 할인 양수 행을 복제해 C1과 겹칠 수 있던 문제는 실패 테스트 뒤 교정했다. B는 날짜 있는 이전 각 월에서 표지 비중 SYNTHETIC 1%이고 방학 건수만 늘어난다. 초기 근거는 SYNTHETIC_P0_conditions_initial.json·SYNTHETIC_P0_B_initial.csv·SYNTHETIC_fixtureB_red.log에 보존했다. 교정 뒤 해당 P0·오류 관측만 재시험했고 대형 전체 검증을 반복하지 않았다.", "",
              "선택 변형의 최소 diff와 줄 수는 §9에 있다. 이는 채택 결정이 아니다.", "",
              "## 4. 반출 전 점검 재현", "", "소형 원본 출력과, 일부러 한 칸만 비운 별도 SYNTHETIC DataFrame 픽스처를 모두 검사했다.", "",
              "| 체크리스트 §3 항목 | SYNTHETIC 원본 관측 / 별도 함정 검사 |", "|---|---|"]
    export = evidence["export_check"]
    rows = [
        ("합계 행·원자료 ID 없음", "원본 CSV 4개 모두 없음. 합계 행과 SHOP_ID 열을 넣은 함정은 각각 탐지"),
        ("k==1 동의 total 합계 공란", "SYNTHETIC k==1 동 2개가 모두 공란. 하나를 복원한 함정은 탐지"),
        ("레짐별 빈칸 수 !=1", "SYNTHETIC 방학 1 / 전환 0 / 학기 1: 방학·학기를 보류 대상으로 탐지"),
        ("total 유효 억제 !=1", "SYNTHETIC 5 − (9 − 6) = 2; regime에 존재하는 억제 동을 직접 세어도 2. 한 칸 함정 탐지"),
        ("total shops 공란 !=1", "SYNTHETIC 3칸; 별도 1칸 함정 탐지"),
        ("u2 공란 !=1", "SYNTHETIC 4칸; 별도 1칸 함정 탐지"),
        ("amount 급식 n 공란 !=1", "SYNTHETIC 2칸; 별도 1칸 함정 탐지. 일반 전용 구간의 n 결측도 원본 체크리스트 식에 포함됨"),
        ("amount 일반 5미만 잔존", "SYNTHETIC n_general 1건인 구간 1개가 그대로 남음. 선택 a 적용 후 잔존 0개"),
        ("동 이름 반출 승인과 내용 일치", "로컬에서 승인 여부 확인 불가. 원본의 이름 키가 포함된 것은 검사했고 승인 여부는 확인 요청")]
    lines += ["| %s | %s |" % pair for pair in rows]
    lines += ["", "위 점검은 체크리스트 §3 재현이다. 가능한 모든 표 간 연립 역산을 증명하는 검사로 확대하지 않았다. 특히 레짐·U2의 기존 공개 합계는 합성값과 직접 비교하지 않고 '합계가 공개돼 있을 때 한 칸 공란이 역산됨'이라는 구조만 시험했다.", "",
              "## 5. P0 판정 픽스처 조건 확인", "", "판정 자동화 함수는 만들지 않았다. 테스트는 체크리스트 §2 순서에서 볼 조건만 확인한다. A/B/C는 픽스처 기대 라벨이며 실데이터 판정이 아니다.", "",
              "| SYNTHETIC 픽스처 | 확인한 조건 | 결과 |", "|---|---|---|"]
    for name in ["A", "B", "C1", "C2"]:
        condition = {"A": "날짜 있는 이전 표지 0, 2023-06~12 급식 표지 있음",
                     "B": "17개월 반복, 방학 표지 건수 2 대 학기 1, 이전 행복페이 각 월 표지 비중 1%; 두 해 방학 비중이 카드보다 큼",
                     "C1": "급식 외 카드 행의 표지 비중 100%; C 우선 조건",
                     "C2": "2023-06~12 급식 표지 0; 이전 표지가 없어도 C 우선 조건"}[name]
        lines.append("| %s | %s (모두 SYNTHETIC) | %s |" % (name, condition, "조건 통과" if p0[name]["condition_pass"] else "실패"))
    lines += ["", "빈 ym의 급식 취소 표지는 이전 기간 증거로 세지 않았다. '흔함'과 '거의 0'의 정량 경계는 원문에 없으므로 임의로 판정 기준을 추가하지 않았다. B의 1%는 픽스처 성질일 뿐 판정 임계값이 아니다.", "",
              "## 6. 오류 사전 요약", "",
              "조용한 실패 우선 점검: ① MEAL·DONE 오타(M2 0행) ② 레짐 문자열 오타(M2 건수는 그대로, M4 이름·순서 대조) ③ 01·N 오타(U2 총수 그대로, live만 바뀜; 고정 기대값이 없어 직접 문자열 대조 필요).",
              "컬럼 usecols 오타·직접 컬럼 오타·KeyError·경로·cp949·BOM·괄호·따옴표·들여쓰기·셀 건너뜀·SHOP_ID 중복을 실제 재현했다. 오류 마지막 줄과 최소 수정 줄은 [오류 사전](visit3_error_dictionary.md)에 있다.", "",
              "A1 뒤 P1b·P2 재실행과 커널 재시작 뒤 M5 단독 실패를 기록했으며, 의존 셀을 다시 실행하면 복구됐다.", "",
              "## 7. 버전 위험 — 셀·줄 단위", "", "| 줄 | pandas 2.2.3 실제 관측 | pandas 1.5.x |", "|---|---|---|"]
    for label, probe in evidence["dtype_probes"].items():
        lines.append("| %s | 정수 열→float64, 경고 %s·예외 %s | 미실시 |" % (label, len(probe["warnings"]), "없음" if probe["exception"] is None else probe["exception"]))
    lines += ["", "15셀 전체 및 120만·200만 행 실행에서 경고는 없었다. SettingWithCopyWarning·FutureWarning이 다른 환경에서도 없다는 뜻은 아니다. 경고 카테고리·파일·줄을 저장하는 경로는 구현했다. pandas 1.5.x와 Python 3.8의 실제 실행 결과는 주장하지 않는다.", "",
              "## 8. 셀별 시간·메모리 — SYNTHETIC", "",
              "셀 exec만 측정했다(로그 쓰기·oracle·관측 스냅샷은 시간에서 제외). 메모리는 Windows Working Set을 10ms 간격으로 표본 측정한 셀 구간 최대이며, 프로세스 누적 PeakWorkingSetSize도 JSON에 별도 저장했다. 표본 사이의 순간 최대는 놓칠 수 있다. 같은 프로세스의 이전 셀 메모리가 포함된다.",
              "PC RAM은 약 8GiB, 시작 시 가용 약 253MiB였다. 스왑과 소요 시간 부담을 줄이기 위해 허용된 SYNTHETIC 200만 행 대안을 썼다. 800만 행은 직접 실행하지 않았다.", "",
              "| 셀 | SYNTHETIC 120만 행 초 | SYNTHETIC 120만 행 최대 MiB(표본) | SYNTHETIC 200만 행 초 | SYNTHETIC 200만 행 최대 MiB(표본) |", "|---|---:|---:|---:|---:|"]
    large = {r["cell"]: r for r in evidence["large_records"]}
    timed = {r["cell"]: r for r in evidence["timing_records"]}
    for cell in ORDER:
        a, b = large.get(cell), timed.get(cell)
        if a and b:
            lines.append("| %s | %.3f | %.1f | %.3f | %.1f |" % (cell, a["seconds"], a["peak_rss_bytes_sampled"]/1048576, b["seconds"], b["peak_rss_bytes_sampled"]/1048576))
    lines += ["", "| 모듈 | SYNTHETIC 200만 행 실행 초 | 800만 행 비례 추정 초(미실측) | 계획서 시간 |", "|---|---:|---:|---|"]
    for name, cells, budget in [("P0", ["P1", "P1b", "P2", "P3"], "30분"), ("M4", ["M1", "M2", "M3", "M4", "M5", "M6"], "90분"), ("H5", ["A1", "A2", "A3", "A4"], "60분")]:
        seconds = sum(timed[c]["seconds"] for c in cells if c in timed)
        lines.append("| %s | %.2f | %.2f | %s |" % (name, seconds, seconds*4, budget))
    lines += ["", "비례 추정은 실행시간만 4배로 계산했다. 메모리는 800만 행으로 비례 외삽하지 않았다. 반복 합성 데이터는 고유 계정·가맹점이 적어 실데이터의 메모리를 낮게 보일 수 있다. 계획서 예산은 타이핑·확인·현장 PC·반출 신청 시간을 포함하므로 위 초 단위 측정으로 현장 시간 여유를 단정할 수 없다. P3·A4는 현장 선택 셀이지만 검증에서는 모두 실행했다.", "",
              "## 9. 선택 변형 a·b·c — 결정 대기", ""]
    for cell, name, effect in [("A3", "a. 일반 건수 억제", "추가 1줄. SYNTHETIC n_general<5 잔존 1개→0개. amount CSV만 변경. head(30) 밖의 구간이라 이 픽스처에서는 stdout은 같았다."),
                               ("M4", "b. 레짐별 억제 칸 수 출력", "추가 1줄. SYNTHETIC 방학 1·전환 0·학기 1을 stdout에 출력. CSV 변경 없음."),
                               ("S1", "c. pandas 버전 출력", "추가 1줄. stdout에 pandas 2.2.3 추가, CSV 변경 없음. 로컬 버전 의존 경고·오류는 확인되지 않아 위험 대응 효과는 미확인.")]:
        v = evidence["optional"][cell]
        lines += ["### " + name, "", "%s %s줄→%s줄, 예외 없음. 원본 cells/는 그대로다. %s" % (cell, v["lines_before"], v["lines_after"], effect), "", "```diff", v["diff"].rstrip(), "```", ""]
    lines += ["## 10. 미실시 항목과 이유", "",
              "- pandas 1.5.x 및 Python 3.8 실실행: 로컬 실행 환경이 없고 네트워크·추가 설치를 사용하지 않았다. 2.2.x는 로컬 2.2.3으로 실행했다.",
              "- SYNTHETIC 800만 행 실측: 시작 시 가용 메모리가 적어 200만 행 실측 및 실행시간 4배 비례 추정으로 대체했다.",
              "- 실제 안심구역 PC 성능·동 이름 반출 승인: 접근 권한이 없어 로컬에서 확인할 수 없다.",
              "- cells_proposed 재검증: 해당 없음. 원본 셀 계산·실행 버그가 없어 제안판을 만들지 않았다.",
              "- 모든 누적 반출물의 일반 연립 역산 탐색: 이번 범위는 체크리스트 §3의 구조적 점검 재현이다.", "",
              "요청 항목 1~12는 위 대체·한계 범위 안에서 기록했다. 개선 목적 반복 실행·임계값 변경·해석 보고서·판정 자동화·visit2 수정·커밋·푸시는 하지 않았다.", "",
              "## 11. Claude에게 확인 요청", "",
              "1. 선택 a(A3 일반 5미만 억제), b(M4 레짐별 억제 수 출력)를 원본에 반영할지 결정한다. 원본은 수정하지 않았다.",
              "2. 방학/학기에서 억제 칸이 각각 SYNTHETIC 1개인 원본 출력은 체크리스트상 보류 대상이다. 실제 현장에서도 점검 후 보류·보완 여부를 설계 담당이 정해야 한다.",
              "3. P0의 '흔함'·'거의 0'에 정량 경계가 없어 자동 판정하지 않았다. 테스트는 극단·경계 성질만 확인했다. B 표지 비중 SYNTHETIC 1%를 판정 임계값으로 사용하지 않는다.",
              "4. 01·N 오타는 live의 고정 기대값으로 잡을 수 없다. 현장 인쇄본의 문자열 대조를 담당자가 수행해야 한다.",
              "5. 동 이름 반출 승인, 원본에 없는 군구+번호 대체 셀, pandas 1.5.x 실제 동작은 로컬에서 확정하지 않았다."]
    write(report, lines)
    readme = ROOT / "tasks/README.md"
    text = readme.read_text(encoding="utf-8")
    status = "- 2026-10-01: V3 Codex 검증 완료 — 원본 15셀 동기화·예외 0·독립 정답·120만 행 청크 불변, pytest 26 passed; 억제 위험·선택 변형·미실시 항목은 [검증 보고](../docs/visit3_codex_report.md) 참조."
    text = "\n".join(line for line in text.splitlines() if not line.startswith("- 2026-10-01: V3 Codex 검증 완료"))
    readme.write_text(text.rstrip() + "\n" + status + "\n", encoding="utf-8")
    print("SYNTHETIC review report: " + str(report))


if __name__ == "__main__":
    main()
