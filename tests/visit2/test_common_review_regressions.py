"""SYNTHETIC regressions for common export safety boundaries."""
import json
from pathlib import Path

import pandas as pd
import pytest

from lib.manifest import start_run
from lib.suppress import suppress


ROOT = Path(__file__).resolve().parents[2]


def config(case_dir):
    cfg = json.loads((ROOT / "analysis/visit2/config/visit2.json").read_text(encoding="utf-8"))
    cfg["paths"]["out_root"] = str(case_dir / "SYNTHETIC_out")
    cfg["run_label"] = "SYNTHETIC"
    cfg["reference_exports"] = {}
    return cfg


def meta(keys, fixed=None):
    return {"population": "SYNTHETIC_same_population", "keys": keys, "metrics": ["n"],
            "time_only": True, "zero_policy": "mask", "night_bucket_applied": False,
            "fixed_keys": fixed or {}}


def test_unlisted_numeric_value_cannot_escape_suppressed_row(case_dir):
    source = pd.DataFrame({"cell": ["SYNTHETIC_A", "SYNTHETIC_B", "SYNTHETIC_C"],
                           "n": [1, 2, 2], "amount": [11, 22, 33]})
    out, report = suppress(source, ["cell"])
    assert report["unresolved"] == []
    assert out.status.eq("suppressed").all()
    assert out.amount.isna().all()
    ctx = start_run(config(case_dir))
    paths = ctx.write_export(out, "SYNTHETIC_values", report, meta(["cell"]))
    saved = pd.read_csv(paths[0], encoding="utf-8-sig")
    assert saved.amount.isna().all()


def test_prior_public_group_total_blocks_later_detailed_export(case_dir):
    ctx = start_run(config(case_dir))
    summary = pd.DataFrame({"g": ["X", "Y"], "n": [5, 8]})
    public, report = suppress(summary, ["g"])
    ctx.write_export(public, "SYNTHETIC_summary", report, meta(["g"]))
    detail_meta = meta(["g", "cell"])
    known = ctx.known_totals(detail_meta)
    assert known[(("g",), ("X",))] == 5
    detail = pd.DataFrame({"g": ["X"] * 2 + ["Y"] * 8,
                           "cell": list(range(10)), "n": [1, 4] + [1] * 8})
    out, report = suppress(detail, ["g", "cell"])
    assert report["unresolved"] == []
    with pytest.raises(ValueError, match="노출|합계"):
        ctx.write_export(out, "SYNTHETIC_detail", report, detail_meta)
    assert not (ctx.export / "SYNTHETIC_detail.csv").exists()


def test_reference_known_total_requires_exact_population_and_fixed_keys(case_dir):
    cfg = config(case_dir)
    ref_dir = case_dir / "reference"
    ref_dir.mkdir()
    (ref_dir / "reference_meta.json").write_text(json.dumps({"SYNTHETIC_ref": {
        "population": "SYNTHETIC_same_population", "keys": ["g"], "metrics": ["n"],
        "fixed_keys": {"R": "vacation"}}}), encoding="utf-8")
    (ref_dir / "SYNTHETIC_ref.json").write_text(json.dumps([
        {"g": "X", "n": 5}, {"g": "Y", "n": 8}]), encoding="utf-8")
    cfg["reference_exports"] = {"SYNTHETIC_ref": "reference/SYNTHETIC_ref.json"}
    cfg["_config_path"] = str(case_dir / "config" / "visit2.json")
    ctx = start_run(cfg)
    assert ctx.known_totals(meta(["g", "cell", "R"]))[(("g", "R"), ("X", "vacation"))] == 5
    assert ctx.known_totals(meta(["g", "cell"], {"R": "term"})) == {}
    different = meta(["g", "cell", "R"])
    different["population"] = "SYNTHETIC_other_population"
    assert ctx.known_totals(different) == {}


def test_countless_banded_mode_keeps_status_and_masks_hidden_metrics():
    source = pd.DataFrame({"cell": ["SYNTHETIC_A", "SYNTHETIC_B"],
                           "status": ["banded", "suppressed"],
                           "n_band": ["<50", "<50"], "ci_low": [0.1, 0.2],
                           "note": ["kept", "hidden"]})
    out, report = suppress(source, ["cell"], n_col=None, shop_col=None, cust_col=None)
    assert report["unresolved"] == []
    assert out.status.tolist() == ["banded", "suppressed"]
    assert out.loc[0, "n_band"] == "<50"
    assert pd.isna(out.loc[0, "ci_low"])
    assert pd.isna(out.loc[1, "n_band"])
    assert pd.isna(out.loc[1, "ci_low"])
    assert pd.isna(out.loc[1, "note"])


def test_countless_mode_cannot_bypass_small_numeric_n():
    source = pd.DataFrame({"cell": ["SYNTHETIC_A"], "n": [1]})
    with pytest.raises(ValueError, match="n_col=None|건수"):
        suppress(source, ["cell"], n_col=None, shop_col=None, cust_col=None)
def test_mixed_and_meal_population_totals_connect():
    from lib.pipeline import population
    from lib.totals import known_totals_for
    cfg = {"meal_pay_values": ["SYN_MEAL"], "status_filter": {"mode": "all"},
           "period": {"start_ym": "202301", "end_ym": "202312"}}
    mixed = population(cfg, "mixed")
    meal = population(cfg, "meal")
    entries = [{"population": mixed, "metric": "n", "keys": ["G"], "values": ["meal"],
                "total": 10, "fixed_keys": {}}]
    mapped = known_totals_for({"population": meal, "keys": ["R"], "fixed_keys": {"G": "meal"}}, entries)
    assert mapped == {((), ()): 10}


def test_reference_projection_never_sums_through_hidden_count(case_dir):
    cfg = config(case_dir)
    reference = case_dir / "SYNTHETIC_reference.json"
    reference.write_text(json.dumps([{"dow": "월", "hour": 6, "n": 5, "n_shop": 999},
                                     {"dow": "월", "hour": 7, "n": None, "n_shop": None}]), encoding="utf-8")
    (case_dir / "reference_meta.json").write_text(json.dumps({"SYNTHETIC_reference": {
        "keys": ["dow", "hour"], "metrics": ["n", "n_shop"], "population": "0911_unknown",
        "zero_policy": "absent_row"}}), encoding="utf-8")
    cfg["reference_exports"] = {"SYNTHETIC_reference": str(reference)}
    target = dict(meta(["dow", "hour3"], {"G": "meal"}), population_kind="meal")
    known = start_run(cfg).known_totals(target)
    assert (("dow", "hour3"), ("월", 2)) not in known
    assert known[(("dow", "hour3"), ("화", 2))] == 0


def test_confirmed_reference_population_still_maps_to_meal_slice(case_dir):
    cfg = config(case_dir)
    reference = case_dir / "SYNTHETIC_reference.json"
    reference.write_text(json.dumps([{"ym": "2023-06", "n": 10}]), encoding="utf-8")
    (case_dir / "reference_meta.json").write_text(json.dumps({"export_0911_month": {
        "keys": ["ym"], "metrics": ["n"], "population": "SYNTHETIC_same_population",
        "zero_policy": "absent_row"}}), encoding="utf-8")
    cfg["reference_exports"] = {"export_0911_month": str(reference)}
    target = dict(meta(["ym", "g"], {"G": "meal"}), population_kind="meal")
    known = start_run(cfg).known_totals(target)
    assert known[(("ym",), (202306,))] == 10
