"""SYNTHETIC additional stage-0 failure and serialization checks."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lib.config import load_config
from lib.io import detect_encoding, iter_chunks
from lib.manifest import start_run
from lib.suppress import exposure_ranges, suppress
from lib.timeparse import hour_to_bucket, hour_to_hour3

ROOT = Path(__file__).resolve().parents[2]


def cfg(case_dir):
    result = json.loads((ROOT / "analysis/visit2/config/visit2.json").read_text(encoding="utf-8"))
    result["paths"]["out_root"] = str(case_dir / "SYNTHETIC_out")
    result["run_label"] = "SYNTHETIC"
    return result


def metadata(keys):
    return {"population": "SYNTHETIC_meal", "keys": keys, "metrics": ["n"],
            "time_only": True, "zero_policy": "mask", "night_bucket_applied": False}


def test_no_suppression_needed():
    df = pd.DataFrame({"g": ["SYNTHETIC_A", "SYNTHETIC_B"], "n": [5, 6]})
    out, report = suppress(df, ["g"])
    assert not report["unresolved"]
    assert report["primary_cells"] == report["secondary_cells"] == 0
    assert out.n.tolist() == [5, 6]


def test_empty_table_has_no_exposure():
    out, report = suppress(pd.DataFrame(columns=["g", "n"]), ["g"])
    assert out.empty and not report["unresolved"]


def test_reference_bound_examples_in_suppress():
    df = pd.DataFrame({"g": ["SYNTHETIC_%d" % x for x in range(10)], "n": [2] + [1] * 9})
    out, report = suppress(df, ["g"], zero_policy="mask", known_totals={((), ()): 11})
    assert not report["unresolved"]
    assert all(bound == (0, 4) for group in report["groups"] for bound in group["ranges"])
    out, report = suppress(df, ["g"], zero_policy="show", known_totals={((), ()): 11})
    assert report["unresolved"]
    assert all(bound == (1, 2) for group in report["groups"] for bound in group["ranges"])


def test_high_n_distinct_suppression_never_passes_wrong_domain():
    df = pd.DataFrame({"g": ["SYNTHETIC_A"], "n": [100], "n_shop": [2], "n_cust": [5]})
    out, report = suppress(df, ["g"])
    assert out.n.isna().all()
    assert any(item["reason"] == "hidden_count_outside_specified_domain" for item in report["unresolved"])


def test_changed_frame_is_rejected(case_dir):
    out, report = suppress(pd.DataFrame({"g": ["SYNTHETIC_A"], "n": [5]}), ["g"])
    out.loc[0, "n"] = 1
    ctx = start_run(cfg(case_dir))
    with pytest.raises(ValueError, match="점검 뒤"):
        ctx.write_export(out, "SYNTHETIC_changed", report, metadata(["g"]))


def test_region_exception_never_allows_four_axes(case_dir):
    config = cfg(case_dir)
    config["export"]["time_only_axes_exception"] = True
    df = pd.DataFrame({"dong": ["SYNTHETIC_D"], "a": [0], "b": [0], "c": [0], "n": [5]})
    out, report = suppress(df, ["dong", "a", "b", "c"])
    ctx = start_run(config)
    with pytest.raises(ValueError, match="분할"):
        ctx.write_export(out, "SYNTHETIC_axes", report, metadata(["dong", "a", "b", "c"]))
    assert not list(ctx.export.glob("*.csv"))


def test_show_zero_and_mask_zero():
    df = pd.DataFrame({"g": ["SYNTHETIC_A", "SYNTHETIC_B"], "n": [0, 0]})
    mask, m_report = suppress(df, ["g"])
    show, s_report = suppress(df, ["g"], zero_policy="show")
    assert mask.status.eq("suppressed").all() and mask.n.isna().all()
    assert show.status.eq("zero").all() and show.n.eq(0).all()
    assert m_report["unresolved"] and not s_report["unresolved"]


def test_hour_mapping_respects_overlap():
    night = {"enabled": True, "hours": [23, 0, 1, 2, 3, 4, 5], "label": "23-05"}
    assert [hour_to_bucket(h, night) for h in [0, 5, 6, 22, 23]] == ["23-05", "23-05", "06", "22", "23-05"]
    assert hour_to_hour3(21) == hour_to_hour3(23) == 7
    assert hour_to_bucket(21, night) != hour_to_bucket(23, night)


def test_cp949_multibyte_sample_boundary(case_dir):
    path = case_dir / "SYNTHETIC_cp949_boundary.csv"
    # First byte of a Korean character is byte 65536; the decoder must wait.
    path.write_bytes(b"x\n" + b"a" * 65533 + "가".encode("cp949") + b"\n")
    assert detect_encoding(path, ["utf-8-sig", "utf-8", "cp949"]) == "cp949"


def test_known_total_conflict_does_not_succeed():
    df = pd.DataFrame({"g": ["SYNTHETIC_A"], "n": [5]})
    _, report = suppress(df, ["g"], known_totals={((), ()): 6})
    assert report["unresolved"]
