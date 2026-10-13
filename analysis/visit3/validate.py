"""One bounded SYNTHETIC validation sweep; no network, decisions or source edits."""
import argparse
import ast
import copy
import csv
import difflib
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from extract_cells import ORDER, ROOT, HERE, check
from oracle import calculate
from run_cells import OUT, canonical, execute, run, selected

spec = importlib.util.spec_from_file_location("make_synthetic", str(ROOT / "synthetic/visit3/make_synthetic.py"))
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("SYNTHETIC_" + name + ".json")).write_text(json.dumps(canonical(value), ensure_ascii=False, indent=2), encoding="utf-8")


def hashes():
    paths = [ROOT / "docs/topics/T2_visit3_plan.md", ROOT / "docs/topics/T2_visit3_checklist.md"]
    for folder in ["analysis/visit2", "tests/visit2", "synthetic/visit2", "9_11_데이터분석결과물", "9_18_데이터분석 결과물"]:
        paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def read_exports(folder):
    result = {}
    for p in folder.glob("EXPORT_*_SYNTHETIC.csv"):
        index = [0, 1] if "regime" in p.name else 0
        result[p.name] = pd.read_csv(p, encoding="utf-8-sig", index_col=index, keep_default_na=True)
        # Empty district is an intentional string key, not a missing index value.
        if "u2" in p.name:
            result[p.name].index = result[p.name].index.fillna("")
    return result


def export_check(exports, reg_dongs=None, meal_dongs=None):
    r = exports["EXPORT_m4_dong_regime_SYNTHETIC.csv"]
    t = exports["EXPORT_m4_dong_total_SYNTHETIC.csv"]
    u = exports["EXPORT_m4_u2_gungu_status_SYNTHETIC.csv"]
    a = exports["EXPORT_m5_amount_hist_SYNTHETIC.csv"]
    blank = r.n.isna()
    counts = blank.groupby(level=1).sum().astype(int).to_dict()
    k = blank.groupby(level=0).sum()
    one = k[k == 1].index
    missing_totals = bool(t.reindex(one).n.isna().all())
    absent = len(reg_dongs - meal_dongs) if reg_dongs is not None else len(t.index.difference(r.index.get_level_values(0)))
    effective_formula = int(t.n.isna().sum()) - absent
    direct = int(t.loc[t.index.isin(r.index.get_level_values(0)), "n"].isna().sum())
    issues = []
    if not missing_totals:
        issues.append("regime_k1_total_visible")
    issues.extend("regime_single_blank_" + k for k, v in counts.items() if v == 1)
    for name, count in [("total_effective", effective_formula), ("total_shops", int(t.shops.isna().sum())),
                        ("u2", int(u.isna().sum().sum())), ("amount_meal", int(a.n.isna().sum()))]:
        if count == 1:
            issues.append(name + "_single_blank")
    columns = [str(c) for f in exports.values() for c in f.columns]
    indexes = [str(x) for f in exports.values() for x in f.index.tolist()]
    if any(c in ["SHOP_ID", "CUST_ID"] for c in columns) or any("SYNTHETIC_S" in x or "SYNTHETIC_C" in x for x in indexes):
        issues.append("raw_id")
    if any(x in ["합계", "전체", "total", "TOTAL", "All"] for x in indexes):
        issues.append("total_row")
    return {"issues": issues, "regime_blanks": counts, "k1_total_masked": missing_totals,
            "effective_formula": effective_formula, "effective_direct": direct, "absent_meal_dongs": absent,
            "formula_matches": effective_formula == direct, "shops_blanks": int(t.shops.isna().sum()),
            "u2_blanks": int(u.isna().sum().sum()), "amount_meal_blanks": int(a.n.isna().sum()),
            "general_lt5_visible": int(((a.n_general < 5) & a.n_general.notna()).sum()),
            "dong_name_approval": "확인 요청: 센터의 동 이름 반출 승인은 로컬에서 확인할 수 없음"}


def traps(exports):
    def frames():
        return {
            "EXPORT_m4_dong_regime_SYNTHETIC.csv": pd.DataFrame([[np.nan, np.nan, np.nan], [8, 3, 5]], index=pd.MultiIndex.from_tuples([("SYNTHETIC_d", "방학"), ("SYNTHETIC_d", "학기")]), columns=["n", "n_shop", "n_cust"]),
            "EXPORT_m4_dong_total_SYNTHETIC.csv": pd.DataFrame([[3, np.nan]], index=["SYNTHETIC_d"], columns=["shops", "n"]),
            "EXPORT_m4_u2_gungu_status_SYNTHETIC.csv": pd.DataFrame([[np.nan, 3]], index=["SYNTHETIC_gu"], columns=["01", "02"]),
            "EXPORT_m5_amount_hist_SYNTHETIC.csv": pd.DataFrame([[np.nan, np.nan, 1], [8, 5, 10]], index=[0, 500], columns=["n", "n_cust", "n_general"])}
    f = frames()
    initial = export_check(f)
    f["EXPORT_m4_dong_total_SYNTHETIC.csv"].loc["SYNTHETIC_d", "n"] = 9
    leak = export_check(f)
    f = frames()
    f["EXPORT_m4_dong_total_SYNTHETIC.csv"].loc["SYNTHETIC_d", "shops"] = np.nan
    shops = export_check(f)
    f = frames()
    f["EXPORT_m4_dong_total_SYNTHETIC.csv"].loc["합계"] = [3, 9]
    totals = export_check(f)
    f = frames()
    f["EXPORT_m4_dong_total_SYNTHETIC.csv"]["SHOP_ID"] = "SYNTHETIC_S99"
    ids = export_check(f)
    return {"regime_single": "regime_single_blank_방학" in initial["issues"],
            "regime_k1_total": "regime_k1_total_visible" in leak["issues"],
            "total_effective_single": "total_effective_single_blank" in initial["issues"],
            "shops_single": "total_shops_single_blank" in shops["issues"],
            "u2_single": "u2_single_blank" in initial["issues"],
            "amount_single": "amount_meal_single_blank" in initial["issues"],
            "general_lt5": initial["general_lt5_visible"] == 1, "total_row": "total_row" in totals["issues"],
            "raw_id": "raw_id" in ids["issues"], "formula_hand": initial["effective_formula"] == initial["effective_direct"] == 1}


def p0_tests(paths, shop):
    conditions, details = {}, {}
    for name, pay in paths.items():
        ns, records, folder = run(pay, shop, "P0_" + name, cells=["S1", "P1", "P1b", "P2"])
        a = ns["a"]
        meal = a.loc["아동급식카드"]
        earlier = a.reset_index()
        earlier = earlier[(earlier.ym >= "202201") & (earlier.ym < "202306")]
        period_meal = meal.loc[(meal.index >= "202306") & (meal.index <= "202312")]
        code_table = a.groupby(level=0).sum()
        card = code_table.loc["카드"]
        happy = earlier[earlier.PAY_GBN == "행복페이"]
        by_month = happy.set_index("ym").n_disc
        vac = by_month.index.str[4:6].isin(["01", "02", "08"])
        annual = {}
        for year in ["2022", "2023"]:
            portions = {}
            for code in ["행복페이", "카드"]:
                x = a.loc[code]
                x = x[x.index.str.startswith(year)]
                portions[code] = float(x.loc[x.index.str[4:6].isin(["01", "02", "08"]), "n"].sum()/x.n.sum())
            annual[year] = portions
        # Test conditions only: never emit a production A/B/C decision function.
        if name == "A":
            conditions[name] = int(earlier.n_disc.sum()) == 0 and int(period_meal.n_disc.sum()) > 0
        elif name == "B":
            conditions[name] = len(by_month[by_month > 0]) == 17 and by_month[vac].mean() > by_month[~vac].mean() and all(annual[y]["행복페이"] > annual[y]["카드"] for y in annual) and int(period_meal.n_disc.sum()) > 0
        elif name == "C1":
            conditions[name] = card.n_disc == card.n and int(period_meal.n_disc.sum()) > 0
        else:
            conditions[name] = int(earlier.n_disc.sum()) == 0 and int(period_meal.n_disc.sum()) == 0
        details[name] = {"condition_pass": conditions[name], "expected_fixture_label": name,
                         "pre_dated_markers": int(earlier.n_disc.sum()), "meal_202306_12_markers": int(period_meal.n_disc.sum()),
                         "happy_pre_marker_share": float(happy.n_disc.sum()/happy.n.sum()),
                         "annual_vac_share_SYNTHETIC": annual, "log_folder": str(folder),
                         "exception": [r["exception"] for r in records if r["exception"]]}
    dump("P0_conditions", details)
    return conditions


def empty_table_example(pay, shop):
    with Path(pay).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        if not row["CARD_APP_TIME"].strip():
            row["CHILD_DISC_AMT"] = "0"
    path = generator.write_rows(generator.HERE / "data_SYNTHETIC/SYNTHETIC_empty_table.csv", generator.PAY_COLS, rows)
    _, records, _ = run(path, shop, "empty_table_example", cells=["S1", "P1"])
    dump("empty_dataframe_example", records[-1])
    return "Empty DataFrame" in records[-1]["stdout"]


def diagnostics(pay, shop, ns):
    folder = OUT / "SYNTHETIC_errors"
    cases = []
    def attempt(name, cell, state, source=None, p=pay, s=shop, reason="", repair="", detect=""):
        target = dict(state)
        record = execute(cell, target, p, s, folder / ("SYNTHETIC_" + name), source_override=source, snapshot=False)
        if not record["exception"] and cell == "M2":
            record["observed_meal_count"] = len(target["m"])
            record["observed_regime_labels"] = sorted(target["m"].R.unique().tolist())
        if name.startswith("regime_"):
            follow = execute("M4", target, p, s, folder / ("SYNTHETIC_" + name), snapshot=False)
            record["M4_followup_stdout"] = follow["stdout"]
            record["M4_followup_exception"] = follow["exception"]
            record["checklist_label_detection"] = sorted(target["m"].R.unique().tolist()) != ["방학", "전환", "학기"]
        if not record["exception"] and cell == "M6":
            record["observed_U2"] = len(target["sel"])
            record["observed_live"] = len(target["live"])
            record["oracle_value_changed"] = len(target["sel"]) != len(ns["sel"]) or len(target["live"]) != len(ns["live"])
            record["fixed_live_expectation_in_checklist"] = False
        record.update(case=name, cause=reason, minimum_retype=repair, detection=detect,
                      last_line=(record["exception"].strip().splitlines()[-1] if record["exception"] else "SYNTHETIC: no exception (silent change or tolerated)") )
        cases.append(record)
        return record
    def source(c):
        return (HERE / "cells" / (c + ".py")).read_text(encoding="utf-8")
    attempt("usecols_typo", "P1", dict(ns, C_GBN="PAY_GBN_TYPO"), reason="usecols 컬럼명 불일치", repair='S1 5줄 C_GBN="PAY_GBN"; P1 전체', detect="ValueError 마지막 줄")
    attempt("direct_column_typo", "M1", ns, source("M1").replace("sh.GUNGU_NM", "sh.GUNGU_TYPO"), reason="셀 내부 컬럼명 오타", repair="M1 2줄 GUNGU_NM 복구; M1 전체", detect="S1 헤더와 대조")
    attempt("keyerror_typo", "A2", dict(ns, C_DISC="CHILD_DISC_TYPO"), reason="DataFrame 조회 컬럼명 오타", repair='S1 6줄 C_DISC 복구; A2 전체', detect="KeyError")
    attempt("path_typo", "S1", {}, p=pay.with_name("SYNTHETIC_missing.csv"), reason="경로 오타", repair="S1 2줄 PAY 수정; S1 전체", detect="FileNotFoundError")
    badenc = generator.HERE / "data_SYNTHETIC/SYNTHETIC_cp949.csv"
    badenc.write_bytes(pay.read_text(encoding="utf-8").encode("cp949"))
    attempt("encoding", "S1", {}, p=badenc, reason="cp949 파일을 utf-8로 읽음", repair='S1 4줄 ENC="cp949"; S1 전체', detect="UnicodeDecodeError")
    bom = generator.HERE / "data_SYNTHETIC/SYNTHETIC_BOM.csv"
    bom.write_bytes(b"\xef\xbb\xbf" + pay.read_bytes())
    attempt("BOM_header", "S1", {}, p=bom, reason="UTF-8 BOM 실제 파일", repair='로컬은 자동 제거; 현장 첫 헤더에 BOM이 남으면 ENC="utf-8-sig"; S1', detect="S1 첫 헤더가 SHOP_ID인지 확인")
    attempt("parenthesis", "P1", ns, source("P1").replace("keep_default_na=False):", "keep_default_na=False:"), reason="닫는 괄호 누락", repair="P1 3줄 ): 복구; P1 전체", detect="SyntaxError")
    attempt("quote", "S1", {}, source("S1").replace('ENC = "utf-8"', 'ENC = "utf-8'), reason="닫는 따옴표 누락", repair="S1 4줄 따옴표 복구; S1 전체", detect="SyntaxError")
    attempt("indent", "P1", ns, source("P1").replace("    ch =", "ch =", 1), reason="for 본문 들여쓰기 누락", repair="P1 4줄 앞 공백 4개; P1 전체", detect="IndentationError")
    attempt("skip_order", "M5", {}, reason="커널 재시작 뒤 M5만 실행", repair="S1→M1→M2→M3→M4→M5", detect="NameError")
    shops, _, _ = generator.build()
    duplicate = generator.write_rows(generator.HERE / "data_SYNTHETIC/SYNTHETIC_duplicate_shop.csv", generator.SHOP_COLS, shops + [dict(shops[0])])
    dn, _, _ = run(pay, duplicate, "duplicate_prep", cells=["S1", "M1"])
    attempt("duplicate_shop", "M2", dn, s=duplicate, reason="SHOP_ID 중복으로 map의 키가 유일하지 않음", repair="자동 삭제 금지; 중복 건수·키를 현장 내부 확인 후 보고, M1→M2", detect="InvalidIndexError")
    attempt("meal_value_typo", "M2", dict(ns, MEAL=["아동급식카드_오타"]), reason="급식 코드 한글 값 오타", repair="S1 7줄 MEAL 복구; M2부터 필요한 후속 셀", detect="예외 없음, M2 len=0을 독립 기대값과 대조")
    attempt("done_value_typo", "M2", dict(ns, DONE="완로"), reason="완료 값 오타", repair="S1 7줄 DONE 복구; M2부터", detect="예외 없음, M2 len=0")
    for label in ["방학", "전환", "학기"]:
        attempt("regime_" + label, "M2", ns, source("M2").replace('"' + label + '"', '"' + label + '_오타"'), reason="레짐 한글 값 오타", repair="M2 10~11줄 해당 문자열 복구; M2→M4→M5", detect="예외 없음; M4 레짐 이름·순서·합계 대조")
    attempt("Y_typo", "M6", ns, source("M6").replace('== "Y"', '== "YY"'), reason="등록 Y 값 오타", repair="M6 5줄 Y 복구; M6 전체", detect="예외 없음; U2 대상=0")
    attempt("status01_typo", "M6", ns, source("M6").replace('== "01"', '== "1"'), reason="문자열 01의 선행 0 누락", repair="M6 11줄 01 복구; M6 전체", detect="예외 없음; live=0, U2 총수는 그대로")
    attempt("serviceN_typo", "M6", ns, source("M6").replace('== "N"', '== "NN"'), reason="서비스 N 값 오타", repair="M6 11줄 N 복구; M6 전체", detect="예외 없음; live=0")
    for c in ["P1b", "P2"]:
        attempt("after_A1_" + c, c, ns, reason="A1이 P1의 a를 덮어씀", repair="P1→P1b→P2", detect="KeyError 또는 중복 인덱스 pivot ValueError")
    recovered = dict(ns)
    rr = [execute(c, recovered, pay, shop, folder / "SYNTHETIC_recovered") for c in ["P1", "P1b", "P2"]]
    _, restart, _ = run(pay, shop, "restart_M5", cells=selected("M5"))
    dump("errors", cases)
    return cases, not any(r["exception"] for r in rr + restart)


def optional(pay, shop, original):
    additions = {"A3": ('e.index.name =', 'e.loc[e.n_general < 5, "n_general"] = np.nan\n'),
                 "M4": ('k = bad.', 'print("레짐별 억제:", bad.groupby(level=1).sum().to_string())\n'),
                 "S1": (None, 'print("pandas:", pd.__version__)\n')}
    results = {}
    folder = HERE / "cells_optional"
    folder.mkdir(exist_ok=True)
    for cell, (anchor, line) in additions.items():
        text = (HERE / "cells" / (cell + ".py")).read_text(encoding="utf-8")
        changed = text + line if anchor is None else text.replace(anchor, line + anchor, 1)
        (folder / (cell + ".py")).write_text(changed, encoding="utf-8")
    _, records, optional_dir = run(pay, shop, "optional", variant="optional")
    original_exports, optional_exports = read_exports(original), read_exports(optional_dir)
    for cell in additions:
        before = (HERE / "cells" / (cell + ".py")).read_text(encoding="utf-8")
        after = (folder / (cell + ".py")).read_text(encoding="utf-8")
        rec = next(r for r in records if r["cell"] == cell)
        results[cell] = {"lines_before": len(before.splitlines()), "lines_after": len(after.splitlines()),
                         "exception": rec["exception"], "diff": "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="cells/"+cell, tofile="cells_optional/"+cell)),
                         "stdout": rec["stdout"]}
    results["changed_exports"] = [k for k in original_exports if canonical(original_exports[k]) != canonical(optional_exports[k])]
    results["general_lt5_after"] = export_check(optional_exports)["general_lt5_visible"]
    dump("optional", results)
    return results


def dtype_probes():
    probes = {
        "M4:5": ('tt = pd.DataFrame({"n": [1, 5], "n_shop": [1, 3], "n_cust": [1, 5]}); bad = pd.Series([True, False])', 'tt[bad] = np.nan', "tt"),
        "M5:8": ('tot = pd.DataFrame({"n": [1, 5], "n_shop": [1, 3], "n_cust": [1, 5], "lq": [1., 2.]}); bad2 = pd.Series([True, False])', 'tot.loc[bad2, ["n", "n_shop", "n_cust", "lq"]] = np.nan', "tot"),
        "M6:9": ('e2 = pd.DataFrame({"01": [1, 3]})', 'e2[e2 < 3] = np.nan', "e2"),
        "A3:6": ('e = pd.DataFrame({"n": [1, 5], "n_cust": [1, 5]}); bad = pd.Series([True, False])', 'e.loc[bad, ["n", "n_cust"]] = np.nan', "e")}
    result = {}
    for label, (setup, line, var) in probes.items():
        state = {"pd": pd, "np": np}
        exec(setup, state)
        before = state[var].dtypes.astype(str).to_dict()
        exception = None
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                exec(line, state)
            except Exception as e:
                exception = type(e).__name__ + ": " + str(e)
        result[label] = {"pandas": pd.__version__, "before": before, "after": state[var].dtypes.astype(str).to_dict(),
                         "warnings": [w.category.__name__ + ": " + str(w.message) for w in caught], "exception": exception}
    dump("dtype_probes", result)
    return result


def compare_runs(first, second, exports1, exports2):
    fail = []
    if len(first) != len(second) or len(first) != len(ORDER):
        fail.append("incomplete_cell_sequence")
    for a, b in zip(first, second):
        if a["stdout"] != b["stdout"] or a.get("snapshot") != b.get("snapshot") or b["exception"]:
            fail.append(a["cell"])
    for path in exports1.glob("EXPORT_*_SYNTHETIC.csv"):
        if path.read_bytes() != (exports2 / path.name).read_bytes():
            fail.append(path.name)
    return fail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timing-rows", type=int, default=2000000)
    parser.add_argument("--skip-large", action="store_true")
    args = parser.parse_args()
    protected = hashes()
    sync = check()
    assert all(r["synced"] for r in sync)
    pay, shop, manifest = generator.make()
    ns, records, folder = run(pay, shop, "small_original")
    expected, expected_exports = calculate(pay, shop)
    wanted = canonical(expected)
    oracle_fails = [r["cell"] for r in records if r.get("snapshot") != wanted[r["cell"]]]
    actual_exports = read_exports(folder)
    for name, frame in expected_exports.items():
        if canonical(frame) != canonical(actual_exports[name]):
            oracle_fails.append(name)
    dump("oracle", expected)
    _, chunked, chunkdir = run(pay, shop, "small_chunk997", chunksize=997)
    chunk_fails = compare_runs(records, chunked, folder, chunkdir)
    export_result = export_check(actual_exports, set(ns["reg"].index), set(ns["m"].dong.unique()))
    export_traps = traps(actual_exports)
    p0_conditions = p0_tests(generator.p0_fixtures(), shop)
    assert empty_table_example(pay, shop)
    cases, recovery = diagnostics(pay, shop, ns)
    optional_result = optional(pay, shop, folder)
    versions = dtype_probes()
    structural = {"P1_rows_equal_codes": len(expected["P1"]["codes"]) == len(manifest["codes"]),
                  "P1b_26_rows": len(expected["P1b"]["monthly_meal"]) == 26,
                  "M4_regime_order": expected["M4"]["regime_order"] == ["방학", "전환", "학기"],
                  "empty_ym_in_P1": "" in expected["P1"]["pre"].index,
                  "empty_ym_in_P2": "" in expected["P2"]["pivot"].index,
                  "meal_cancel_empty_ym_in_P3": "아동급식카드" in expected["P3"]["overlap"].index,
                  "A3_first30_not_always_0_to14500": expected["A3"]["e"].index.min() < 0}
    dump("small_run", {"records": records, "structural": structural, "export_check": export_result})
    large_fail, large_records, timing_records = [], [], []
    if not args.skip_large:
        large, _, large_meta = generator.make("large", 1200000)
        print("SYNTHETIC 1,200,000 rows: original execution", flush=True)
        large_ns, large_records, large_dir = run(large, shop, "large_original")
        del large_ns
        import gc
        gc.collect()
        print("SYNTHETIC 1,200,000 rows: chunksize 997", flush=True)
        large_ns, large_chunks, large_chunkdir = run(large, shop, "large_chunk997", chunksize=997)
        del large_ns
        gc.collect()
        large_fail = compare_runs(large_records, large_chunks, large_dir, large_chunkdir)
        print("SYNTHETIC timing rows: %d" % args.timing_rows, flush=True)
        timing, _, timing_meta = generator.make("timing", args.timing_rows)
        timed_ns, timing_records, _ = run(timing, shop, "timing", snapshot=False)
        del timed_ns
        gc.collect()
    syntax = True
    for tree in [HERE, ROOT / "synthetic/visit3", ROOT / "tests/visit3"]:
        for file in tree.rglob("*.py"):
            try:
                ast.parse(file.read_text(encoding="utf-8"), feature_version=(3, 8))
            except SyntaxError:
                syntax = False
    result = {"label": "SYNTHETIC", "environment": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
              "sync": sync, "exceptions": sum(bool(r["exception"]) for r in records + large_records + timing_records), "oracle_failures": oracle_fails,
              "chunk_failures": chunk_fails, "large_chunk_failures": large_fail,
              "export_check": export_result, "export_trap_tests": export_traps, "p0_conditions": p0_conditions,
              "recovery_ok": recovery, "python38_syntax": syntax, "protected_hashes_unchanged": hashes() == protected,
              "protected_hashes_before": protected, "structural": structural, "optional": optional_result,
              "dtype_probes": versions, "small_records": records, "large_records": large_records, "timing_records": timing_records,
              "timing_rows": args.timing_rows, "large_skipped": args.skip_large}
    dump("validation", result)
    print("SYNTHETIC summary: " + json.dumps({k: result[k] for k in ["exceptions", "oracle_failures", "chunk_failures", "large_chunk_failures", "p0_conditions", "protected_hashes_unchanged"]}, ensure_ascii=False), flush=True)
    if result["exceptions"] or oracle_fails or chunk_fails or large_fail or not all(export_traps.values()) or not all(p0_conditions.values()) or not recovery or not syntax or not result["protected_hashes_unchanged"]:
        raise SystemExit(1)
    tests = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "tests/visit3", "-q", "-p", "no:cacheprovider"],
                           cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    (OUT / "SYNTHETIC_pytest.log").write_text("SYNTHETIC\n" + tests.stdout, encoding="utf-8")
    print(tests.stdout.strip(), flush=True)
    if tests.returncode:
        raise SystemExit(tests.returncode)
    from write_reports import main as write_reports
    write_reports()


if __name__ == "__main__":
    main()
