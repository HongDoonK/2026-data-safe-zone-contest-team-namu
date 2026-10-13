"""SYNTHETIC hand-computable contracts for the stage-0 gate."""
import importlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def module(name):
    # A missing implementation is an explicit failed contract, not collection failure.
    try:
        return importlib.import_module("lib." + name)
    except ModuleNotFoundError:
        pytest.fail("missing stage-0 implementation: " + name)


def config():
    root = Path(__file__).resolve().parents[2]
    path = root / "analysis/visit2/config/visit2.json"
    assert path.exists(), "configuration implementation is missing"
    return json.loads(path.read_text(encoding="utf-8"))


def frame(values):
    return pd.DataFrame({"key": list(range(len(values))), "n": values,
                         "n_shop": [3] * len(values), "n_cust": [5] * len(values)})


@pytest.mark.parametrize("S,k,lo,hi,want", [
    (11, 10, 1, 4, [(1, 2)] * 10), (11, 10, 0, 4, [(0, 4)] * 10),
    (11, 3, 0, 4, [(3, 4)] * 3), (0, 3, 0, 4, [(0, 0)] * 3),
    (12, 3, 0, 4, [(4, 4)] * 3), (3, 1, 0, 4, [(3, 3)]),
    (0, 0, 0, 4, [])])
def test_exposure_boundaries(S, k, lo, hi, want):
    assert module("suppress").exposure_ranges(S, k, lo, hi) == want


@pytest.mark.parametrize("args", [(1, 0, 0, 4), (5, 1, 0, 4), (-1, 2, 0, 4),
                                 (1, -1, 0, 4), (1, 2, 4, 0), (1.5, 2, 0, 4)])
def test_exposure_inconsistent_input(args):
    with pytest.raises(ValueError):
        module("suppress").exposure_ranges(*args)


def test_time_rows_retained_and_dow():
    tp = module("timeparse")
    src = pd.DataFrame({"app_time": ["202409%02d12" % day for day in range(16, 23)]
                       + ["202409161", "ABCDEFGHIJ", "2024023012", ""]})
    out = tp.add_time_fields(src)
    assert len(out) == 11
    assert out.time_invalid.tolist() == [False] * 7 + [True] * 4
    assert [tp.label_dow(x) for x in out.dow.iloc[:7]] == ["월", "화", "수", "목", "금", "토", "일"]
    assert out.hour3.iloc[:7].tolist() == [4] * 7
    assert out.is_weekend.iloc[:7].tolist() == [False] * 5 + [True] * 2


def test_regime_modes():
    tp = module("timeparse")
    df = tp.add_time_fields(pd.DataFrame({"app_time": ["2024011912", "2024012012", "2024030312", "2024030412"]}))
    assert tp.assign_regime(df, {"mode": "month", "month_map": {"1": "방학"}, "default": "학기"}).tolist() == ["방학", "방학", "학기", "학기"]
    cfg = {"mode": "date_ranges", "default": "학기", "date_ranges": [
        {"start": "20240120", "end": "20240303", "label": "방학"}]}
    assert tp.assign_regime(df, cfg).tolist() == ["학기", "방학", "방학", "학기"]


def test_exact_filter_padding_and_status():
    f = module("filters")
    df = pd.DataFrame({"pay_gbn": [" SYN_MEAL_A  ", "SYN_MEAL_A_X", ""],
                       "card_pay_gbn": ["완료 ", "취소", "기타"], "ym": [202306, 202307, 202505]})
    assert f.meal_flag(df, ["SYN_MEAL_A"]).tolist() == [True, False, False]
    cfg = {"mode": "complete_only", "complete_values": ["완료"], "cancel_values": ["취소"]}
    assert f.status_mask(df, cfg).tolist() == [True, False, False]
    cfg["mode"] = "exclude_cancel"
    assert f.status_mask(df, cfg).tolist() == [True, False, True]
    cfg["mode"] = "all"
    assert f.status_mask(df, cfg).all()
    assert f.period_mask(df, {"start_ym": "202306", "end_ym": "202307"}).tolist() == [True, True, False]


def test_encoding_mapping_and_chunks(case_dir):
    io = module("io")
    path = case_dir / "SYNTHETIC_cp949.csv"
    path.write_bytes("가맹점코드,지급구분\n S1 , SYN_MEAL_A \n S1 , \n S1 , SYN_MEAL_A\n S1 , SYN_MEAL_A\n".encode("cp949"))
    enc = io.detect_encoding(path, ["utf-8-sig", "utf-8", "cp949"])
    assert enc == "cp949"
    mapping = {"shop_id": "가맹점코드", "pay_gbn": "지급구분"}
    chunks = list(io.iter_chunks(path, list(mapping), mapping, enc, 3))
    assert [len(x) for x in chunks] == [3, 1]
    assert chunks[0].shop_id.tolist() == ["S1"] * 3
    assert pd.isna(chunks[0].pay_gbn.iloc[1])
    with pytest.raises(ValueError) as err:
        list(io.iter_chunks(path, ["shop_id"], {"shop_id": "SHOP_ID"}, enc, 3))
    assert "shop_id" in str(err.value) and "SHOP_ID" in str(err.value) and "가맹점코드" in str(err.value)


def test_distinct_chunk_boundary():
    d = module("distinct").DistinctAccumulator(["g"])
    c = module("distinct").CountAccumulator(["g"])
    df = pd.DataFrame({"g": ["A"] * 4, "cust_id": ["C1"] * 4})
    for chunk in [df.iloc[:3], df.iloc[3:]]:
        d.update(chunk, "cust_id")
        c.update(chunk)
    assert d.finalize()["nunique"].tolist() == [1]
    assert c.finalize().n.tolist() == [4]


def test_config_placeholder_exception(case_dir):
    cfg = config()
    path = case_dir / "SYNTHETIC_config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="meal_pay_values"):
        module("config").load_config(path)
    # M1's explicit loader shares schema validation but permits discovery.
    assert module("config").load_discovery_config(path)["cols_pay"]["shop_id"] == "SHOP_ID"


def test_config_valid_and_missing_key(case_dir):
    cfg = config()
    cfg["meal_pay_values"] = ["SYN_MEAL_A"]
    path = case_dir / "SYNTHETIC_config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    assert module("config").load_config(path)["meal_pay_values"] == ["SYN_MEAL_A"]
    del cfg["suppression"]
    path.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="suppression"):
        module("config").load_config(path)


def test_mask_zero_indistinguishable():
    out, report = module("suppress").suppress(frame([0, 1, 4, 20]), ["key"])
    assert out.iloc[:3][["n", "n_shop", "n_cust"]].isna().all().all()
    assert out.status.iloc[:3].tolist() == ["suppressed"] * 3
    assert report["primary_cells"] == 3


def test_suppress_thresholds():
    df = pd.DataFrame({"key": list(range(4)), "n": [4, 5, 5, 5],
                       "n_shop": [3, 3, 2, 3], "n_cust": [5, 5, 5, 4]})
    out, report = module("suppress").suppress(df, ["key"])
    assert report["primary_cells"] == 3
    assert out.loc[[0, 2, 3], ["n", "n_shop", "n_cust"]].isna().all().all()
    assert report["unresolved"]  # Hidden n>=5 cannot use the specified [0,4] domain.


def test_all_suppressed_known_total_refused(case_dir):
    out, report = module("suppress").suppress(frame([4, 4, 3]), ["key"], known_totals={((), ()): 11})
    assert report["unresolved"]
    cfg = config()
    cfg["paths"]["out_root"] = str(case_dir / "SYNTHETIC_out")
    cfg["run_label"] = "SYNTHETIC"
    ctx = module("manifest").start_run(cfg)
    with pytest.raises(ValueError, match="unresolved"):
        ctx.write_export(out, "SYNTHETIC_blocked", report, meta(["key"]))
    assert not list(ctx.export.glob("*.csv"))


def test_secondary_suppression_attempted():
    out, report = module("suppress").suppress(frame([1, 5, 10]), ["key"], known_totals={((), ()): 16})
    assert report["secondary_cells"] >= 1
    assert report["unresolved"]


def test_share_implies_total():
    df = frame([1, 5, 10])
    df["share_total"] = df.n / 16
    out, report = module("suppress").suppress(df, ["key"])
    assert report["unresolved"]
    assert out.loc[out.status == "suppressed", "share_total"].isna().all()


def test_night_bucket_preserves_distinct_guard():
    s = module("suppress")
    cfg = {"enabled": True, "hours": [23, 0, 1, 2, 3, 4, 5], "label": "23-05"}
    df = pd.DataFrame({"dow": [0, 0, 0], "hour": [23, 0, 6], "n": [2, 3, 7]})
    out = s.apply_night_bucket(df, "hour", cfg)
    assert sorted(out.n.tolist()) == [5, 7]
    assert set(out.hour_bucket) == {"23-05", "06"}
    df["n_shop"] = [2, 3, 7]
    with pytest.raises(ValueError):
        s.apply_night_bucket(df, "hour", cfg)


def meta(keys):
    return {"keys": keys, "metrics": ["n"], "population": "SYNTHETIC_meal",
            "time_only": True, "zero_policy": "mask", "night_bucket_applied": False}


def test_manifest_guards_and_split(case_dir):
    cfg = config()
    cfg["paths"]["out_root"] = str(case_dir / "SYNTHETIC_out")
    cfg["run_label"] = "SYNTHETIC"
    ctx = module("manifest").start_run(cfg)
    df = pd.DataFrame({"R": ["A", "B"], "dow": [1, 1], "hour3": [2, 2], "G": ["meal", "meal"], "n": [5, 6]})
    with pytest.raises(ValueError, match="status"):
        ctx.write_export(df, "SYNTHETIC_no_status", {"unresolved": []}, meta(["R", "dow", "hour3", "G"]))
    df, report = module("suppress").suppress(df, ["R", "dow", "hour3", "G"], shop_col=None, cust_col=None)
    paths = ctx.write_export(df, "SYNTHETIC_split", report, meta(["R", "dow", "hour3", "G"]))
    assert len(paths) == 2
    for path in paths:
        details = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
        assert len(details["keys"]) == 3
        assert "R" in details["fixed_keys"]
        assert "5.0" not in path.read_text(encoding="utf-8-sig")
    totals = json.loads((ctx.internal / "published_totals.json").read_text(encoding="utf-8"))
    assert totals and all(item["metric"] == "n" for item in totals)
    ctx.finish("SYNTHETIC_test", {"read_rows": 2})
    assert (ctx.export / "run_manifest.json").exists()
    assert (ctx.export / "filter_definition.txt").exists()


def test_stats_independence_and_association():
    s = module("stats")
    assert s.cramers_v([[10, 10], [10, 10]]) == pytest.approx(0)
    assert s.cramers_v([[10, 0], [0, 10]]) == pytest.approx(1)


def test_bootstrap_single_shop_and_seed():
    s = module("stats")
    meal = np.array([[2, 0]])
    gen = np.array([[0, 2]])
    a = s.share_diff_bootstrap(meal, gen, 20, 7)
    b = s.share_diff_bootstrap(meal, gen, 20, 7)
    pd.testing.assert_frame_equal(a, b)
    assert a["diff"].tolist() == [1.0, -1.0]
    assert (a.ci_low == a.ci_high).all()
