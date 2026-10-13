"""SYNTHETIC stage-A export checks; real references are tested read-only."""
import json
import subprocess
import sys
from pathlib import Path

from export_check import check_references, check_run


ROOT = Path(__file__).resolve().parents[2]


def _setup(case_dir, patterns=None):
    ref = case_dir / "reference"
    ref.mkdir()
    (ref / "SYNTHETIC_month.json").write_text(json.dumps([{"ym": "2023-06", "n": 10}], ensure_ascii=False), encoding="utf-8")
    (ref / "SYNTHETIC_week.json").write_text(json.dumps([
        {"dow": "금", "hour": 22, "n": 7},
        {"dow": "금", "hour": 23, "n": None},
        {"dow": "토", "hour": 23, "n": None},
    ], ensure_ascii=False), encoding="utf-8")
    (ref / "reference_meta.json").write_text(json.dumps({
        "SYNTHETIC_month": {"keys": ["ym"], "metrics": ["n"], "population": "0911_unknown", "zero_policy": "absent_row"},
        "SYNTHETIC_week": {"keys": ["dow", "hour"], "metrics": ["n"], "population": "0911_unknown", "zero_policy": "absent_row"},
    }), encoding="utf-8")
    cfg = {"suppression": {"n_min": 5, "shop_min": 3, "cust_min": 5},
           "export": {"max_axes": 3, "time_only_axes_exception": False,
                      "night_bucket": {"enabled": True, "hours": [23, 0, 1, 2, 3, 4, 5], "label": "23-05"}},
           "reference_exports": {"SYNTHETIC_month": "reference/SYNTHETIC_month.json",
                                 "SYNTHETIC_week": "reference/SYNTHETIC_week.json"},
           "id_patterns": patterns if patterns is not None else ["^SYNID[0-9]+$"]}
    config = case_dir / "config.json"
    config.write_text(json.dumps(cfg), encoding="utf-8")
    run = case_dir / "run"
    (run / "export").mkdir(parents=True)
    (run / "internal").mkdir()
    (run / "export" / "filter_definition.txt").write_text(
        "급식 값 SYN_MEAL 상태 필터 all 기간 202306~202506 레짐 month 지표 n n_shop n_cust 심야 합치기 23-05 0 처리 mask",
        encoding="utf-8")
    (run / "export" / "run_manifest.json").write_text("{}", encoding="utf-8")
    return config, run


def _table(run, name, rows, meta, header=None):
    if header is None:
        header = list(rows[0])
    path = run / "export" / (name + ".csv")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        import csv
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    (run / "export" / (name + ".meta.json")).write_text(json.dumps(meta), encoding="utf-8")
    return path


def _meta(keys, kind="meal", **kw):
    data = {"keys": keys, "metrics": ["n"], "population": "SYNTHETIC_meal",
            "population_kind": kind, "zero_policy": "mask", "time_only": True,
            "night_bucket_applied": False}
    data.update(kw)
    return data


def _status(result, code):
    return [item["status"] for item in result["checks"] if item["code"] == code]


def test_0911_known():
    result = check_references(ROOT / "analysis/visit2/config/visit2.json")
    assert result["fail_count"] == 0
    assert result["known_count"] == 10
    assert all(item["range"] == [1, 2] for item in result["exposures"] if item["status"] == "KNOWN")


def test_absolute_reference_paths_use_adjacent_metadata(case_dir):
    config, run = _setup(case_dir)
    cfg = json.loads(config.read_text(encoding="utf-8"))
    cfg["reference_exports"] = {key: str((case_dir / value).resolve())
                                for key, value in cfg["reference_exports"].items()}
    relocated = case_dir / "SYNTHETIC_settings"
    relocated.mkdir()
    config = relocated / "SYNTHETIC_config.json"
    config.write_text(json.dumps(cfg), encoding="utf-8")
    assert check_run(config, run, reference_only=True)["fail_count"] == 0


def test_new_hidden_cell_recovered_by_old_total(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_fine", [
        {"ym": "2023-06", "g": "a", "n": 8, "status": "published"},
        {"ym": "2023-06", "g": "b", "n": "", "status": "suppressed"}],
        _meta(["ym", "g"], coverage_complete=True))
    result = check_run(config, run)
    assert any(x["status"] == "FAIL" and x["table"] == "SYNTHETIC_fine"
               and x["range"] == [2, 2] for x in result["exposures"])


def test_hidden_unregistered_metric_is_rejected(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_extra", [{"g": "a", "n": "", "amount": 987654,
                                    "status": "suppressed"}], _meta(["g"]))
    result = check_run(config, run)
    assert "FAIL" in _status(result, "C4")
    assert "987654" not in Path(result["report_path"]).read_text(encoding="utf-8")


def test_new_table_narrows_known(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_new", [{"dow": "금", "hour": 23, "n": 1, "status": "published"}],
           _meta(["dow", "hour"], kind="meal"))
    result = check_run(config, run)
    assert "FAIL" in _status(result, "C8")


def test_night_bucket_safe(case_dir):
    config, run = _setup(case_dir)
    days = ("월", "화", "수", "목", "금", "토", "일")
    old = [{"dow": day, "hour": hour, "n": 5} for day in days for hour in range(6, 23)]
    old += [{"dow": "금", "hour": 23, "n": None}, {"dow": "토", "hour": 23, "n": None}]
    ref = case_dir / "reference"
    (ref / "SYNTHETIC_month.json").write_text(json.dumps([{"ym": "2023-06", "n": 598}]), encoding="utf-8")
    (ref / "SYNTHETIC_week.json").write_text(json.dumps(old, ensure_ascii=False), encoding="utf-8")
    rows = [{"dow": day, "hour_bucket": "%02d" % hour, "n": 5, "status": "published"}
            for day in days for hour in range(6, 23)]
    rows += [{"dow": day, "hour_bucket": "23-05", "n": "", "status": "suppressed"} for day in days]
    _table(run, "SYNTHETIC_night", rows,
           _meta(["dow", "hour_bucket"], night_bucket_applied=True, coverage_complete=True))
    assert check_run(config, run)["fail_count"] == 0


def test_projected_bucket_narrows_reference(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_bucket", [{"dow": "금", "hour_bucket": "23-05", "n": 1, "status": "published"}],
           _meta(["dow", "hour_bucket"], night_bucket_applied=True))
    assert "FAIL" in _status(check_run(config, run), "C8")


def test_id_in_cell_and_header_is_masked(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_cell", [{"g": "SYNID123", "n": 5, "status": "published"}], _meta(["g"]))
    _table(run, "SYNTHETIC_header", [{"SYNID456": "x", "n": 5, "status": "published"}], _meta(["SYNID456"]))
    result = check_run(config, run)
    assert _status(result, "C2").count("FAIL") >= 2
    report = (run / "internal/export_check_report.txt").read_text(encoding="utf-8")
    assert "SYNID123" not in report and "SYNID456" not in report


def test_region_four_axes_even_with_exception(case_dir):
    config, run = _setup(case_dir)
    cfg = json.loads(config.read_text(encoding="utf-8"))
    cfg["export"]["time_only_axes_exception"] = True
    config.write_text(json.dumps(cfg), encoding="utf-8")
    keys = ["dong", "R", "dow", "hour3"]
    _table(run, "SYNTHETIC_axes", [dict(zip(keys, ["동", "학기", "금", 7]), n=5, status="published")],
           _meta(keys, time_only=True))
    assert "FAIL" in _status(check_run(config, run), "C5")


def test_status_and_meta_fail_closed(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_missing_status", [{"g": "x", "n": 5}], _meta(["g"]))
    _table(run, "SYNTHETIC_bad_status", [{"g": "y", "n": 5, "status": "hidden"}], _meta(["g"]))
    path = _table(run, "SYNTHETIC_no_meta", [{"g": "z", "n": 5, "status": "published"}], _meta(["g"]))
    path.with_suffix(".meta.json").unlink()
    assert _status(check_run(config, run), "C3").count("FAIL") >= 3


def test_meal_individual_night_hour(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_late", [{"hour": 23, "n": 5, "status": "published"}], _meta(["hour"]))
    assert "FAIL" in _status(check_run(config, run), "C6")


def test_empty_malformed_and_cp949_fail_without_exception(case_dir):
    config, run = _setup(case_dir)
    assert check_run(config, run)["fail_count"] > 0
    path = _table(run, "SYNTHETIC_bad", [{"g": "x", "n": 5, "status": "published"}], _meta(["g"]))
    path.write_bytes(b"g,n,status\nx,5,published,extra\n")
    assert "FAIL" in _status(check_run(config, run), "C3")
    path.write_bytes("g,n,status\n한글,5,published\n".encode("cp949"))
    assert "FAIL" in _status(check_run(config, run), "C3")


def test_placeholder_ids_fail_normal_but_reference_only_na(case_dir):
    config, run = _setup(case_dir, patterns=["<현장 입력>"])
    _table(run, "SYNTHETIC_ok", [{"g": "x", "n": 5, "status": "published"}], _meta(["g"]))
    assert "FAIL" in _status(check_run(config, run), "C2")
    assert "N/A" in _status(check_run(config, run, reference_only=True), "C2")


def test_null_reference_exports_warns(case_dir):
    config, run = _setup(case_dir)
    cfg = json.loads(config.read_text(encoding="utf-8"))
    cfg["reference_exports"] = None
    config.write_text(json.dumps(cfg), encoding="utf-8")
    result = check_run(config, run, reference_only=True)
    assert result["fail_count"] == 0
    assert "WARN" in _status(result, "C8")


def test_cli_exit_codes_and_past_rejection(case_dir):
    config, run = _setup(case_dir)
    script = ROOT / "analysis/visit2/export_check.py"
    base = [sys.executable, str(script), "--config", str(config), "--run", str(run)]
    assert subprocess.run(base + ["--reference-only"], capture_output=True).returncode == 0
    _table(run, "SYNTHETIC_id", [{"g": "SYNID123", "n": 5, "status": "published"}], _meta(["g"]))
    bad = subprocess.run(base, capture_output=True)
    assert bad.returncode == 1 and b"SYNID123" not in bad.stdout
    assert subprocess.run(base + ["--past", "x"], capture_output=True).returncode != 0


def test_banded_count_is_not_csv_format_error(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_band", [{"g": "x", "n": "<50", "status": "banded"}],
           _meta(["g"], kind="diagnostic"))
    result = check_run(config, run)
    assert "FAIL" not in _status(result, "C3")


def test_hour3_is_not_individual_night_hour(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_hour3", [{"hour3": 7, "n": 5, "status": "published"}],
           _meta(["hour3"], kind="meal"))
    result = check_run(config, run)
    assert "FAIL" not in _status(result, "C6")


def test_finer_table_without_coverage_proof_fails_c8(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_finer", [{"ym": "2023-06", "g": "x", "n": "", "status": "suppressed"}],
           _meta(["ym", "g"]))
    assert "FAIL" in _status(check_run(config, run), "C8")


def test_status_and_numeric_value_must_agree(case_dir):
    config, run = _setup(case_dir)
    cfg = json.loads(config.read_text(encoding="utf-8"))
    cfg["reference_exports"] = None
    config.write_text(json.dumps(cfg), encoding="utf-8")
    _table(run, "SYNTHETIC_blank_public", [{"g": "a", "n": "", "status": "published"}], _meta(["g"]))
    _table(run, "SYNTHETIC_false_zero", [{"g": "a", "n": 5, "status": "zero"}], _meta(["g"], zero_policy="show"))
    assert _status(check_run(config, run), "C3").count("FAIL") == 2


def test_invalid_export_config_is_fail_not_exception(case_dir):
    config, run = _setup(case_dir)
    cfg = json.loads(config.read_text(encoding="utf-8"))
    cfg["export"]["max_axes"] = "invalid"
    cfg["id_patterns"] = [123]
    config.write_text(json.dumps(cfg), encoding="utf-8")
    _table(run, "SYNTHETIC_bad_cfg", [{"g": "a", "n": 5, "status": "published"}], _meta(["g"]))
    assert check_run(config, run)["fail_count"] > 0


def test_invalid_fixed_keys_metadata_is_fail_not_exception(case_dir):
    config, run = _setup(case_dir)
    _table(run, "SYNTHETIC_bad_meta", [{"g": "a", "n": 5, "status": "published"}], _meta(["g"], fixed_keys=[]))
    assert "FAIL" in _status(check_run(config, run), "C3")


def test_mixed_group_table_compares_only_meal_slice(case_dir):
    config, run = _setup(case_dir)
    rows = [{"ym": "202306", "G": "meal", "n": 10, "status": "published"},
            {"ym": "202306", "G": "general", "n": 20, "status": "published"}]
    _table(run, "SYNTHETIC_mixed", rows, _meta(["ym", "G"], kind="mixed", coverage_complete=True))
    assert check_run(config, run)["fail_count"] == 0
