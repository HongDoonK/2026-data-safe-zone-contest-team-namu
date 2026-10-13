"""SYNTHETIC hand-countable spatial publication contracts."""
import numpy as np
import pandas as pd
from lib.m4 import select_level, publishability, add_lq, spatial_keys


def test_fixed_ladder_order():
    assert select_level({"L1": .5, "L2": .92, "L4": .95, "L3": .97, "L5": .99}, .9) == "L2"
    assert select_level({key: .5 for key in ("L1", "L2", "L3", "L4", "L5")}, .9) == "none"


def test_zero_cells_not_in_ladder_denominator():
    frame = pd.DataFrame({"dong": ["SYN_G|SYN_A", "SYN_G|SYN_B", "SYN_G|SYN_C"],
                          "n": [5, 1, 0], "n_shop": [3, 1, 0], "n_cust": [5, 1, 0]})
    result = publishability(frame, "dong")
    assert result["cells_total"] == 2 and result["cells_pass"] == 1
    assert result["count_pass_share"] == 5/6


def test_equal_meal_share_has_lq_one():
    frame = pd.DataFrame({"dong": ["SYN_G|A", "SYN_G|A", "SYN_G|B", "SYN_G|B"],
                          "R": ["SYN_R"]*4, "G": ["meal", "general"]*2, "n": [5, 5, 10, 10]})
    result = add_lq(frame, ["dong", "R"])
    assert np.allclose(result.lq, 1)


def test_same_dong_name_in_different_gungu_is_separate():
    frame = pd.DataFrame({"gungu": ["SYN_중구", "SYN_서구"], "dong": ["대신동", "대신동"]})
    assert spatial_keys(frame).dong.nunique() == 2


def test_absent_general_counterpart_does_not_publish_share_one(case_dir):
    from lib.m4 import export_map_candidate
    from lib.pipeline import open_context
    from test_module_cli import _fixture
    cfg, _ = _fixture(case_dir)
    frame = pd.DataFrame({"dong": ["SYN_G|A"], "R": ["SYN_R"], "G": ["meal"],
                          "n": [5], "n_shop": [5], "n_cust": [5]})
    okay, reason = export_map_candidate(open_context(cfg), "L2", {"L2": frame})
    assert not okay


def test_l1_splits_into_two_three_axis_files(case_dir):
    import json
    from lib.m4 import export_map_candidate
    from lib.pipeline import open_context
    from test_module_cli import _fixture
    cfg, _ = _fixture(case_dir)
    rows = [{"dong": "SYN_G|A", "R": "SYN_R", "G": group, "hour3": hour,
             "n": 5, "n_shop": 5, "n_cust": 5} for group in ["meal", "general"] for hour in [0, 1]]
    coarse = [{"dong": "SYN_G|A", "R": "SYN_R", "G": group,
               "n": 10, "n_shop": 5, "n_cust": 5} for group in ["meal", "general"]]
    ctx = open_context(cfg)
    okay, _ = export_map_candidate(ctx, "L1", {"L1": pd.DataFrame(rows), "L2": pd.DataFrame(coarse)})
    assert okay
    assert {p.stem for p in ctx.export.glob("*.csv")} == {"m4_mapunit_meal", "m4_mapunit_share"}
    for path in ctx.export.glob("*.meta.json"):
        assert len(json.loads(path.read_text(encoding="utf-8"))["keys"]) <= 3


def test_gungu_prior_total_blocks_dong_reconstruction(case_dir):
    from lib.m4 import _spatial_prior_safe, _meta
    from lib.pipeline import open_context
    from test_module_cli import _fixture
    cfg, _ = _fixture(case_dir)
    ctx = open_context(cfg)
    meta = _meta(ctx, ["dong", "R"], "meal")
    ctx.totals = [{"population": meta["population"], "metric": "n", "keys": ["gungu", "R", "G"],
                   "values": ["SYN_G", "SYN_R", "meal"], "total": 10}]
    checked = pd.DataFrame({"dong": ["SYN_G|A", "SYN_G|B"], "R": ["SYN_R"]*2,
                            "n": [np.nan, 8], "status": ["suppressed", "published"]})
    assert not _spatial_prior_safe(ctx, checked, meta)


def test_m4_small_cli_and_promotion_requires_reason(case_dir):
    import json
    import subprocess
    import sys
    from test_module_cli import _fixture, _run, ROOT
    from export_check import check_run
    cfg, config = _fixture(case_dir)
    process, run = _run("50_m4_space.py", config)
    assert process.returncode == 0, process.stderr
    g1 = pd.read_csv(run / "export/m4_g1_publishability.csv")
    assert not {"n", "n_meal", "n_general", "count_total"} & set(g1)
    command = [sys.executable, str(ROOT / "analysis/visit2/promote_internal.py"), "--run", str(run), "--file", "m4_dong_names.csv"]
    assert subprocess.run(command, capture_output=True).returncode != 0
    approved = subprocess.run(command + ["--reason", "SYNTHETIC schema-only test approval"], capture_output=True)
    assert approved.returncode == 0, approved.stderr
    manifest = json.loads((run / "export/run_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["manual_actions"]) == 1
    assert check_run(config, run)["fail_count"] == 0
