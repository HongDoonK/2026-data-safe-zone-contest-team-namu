"""SYNTHETIC shop-join edge contracts."""
import numpy as np
import pandas as pd
from lib.m3 import clean_shops, safe_ratio, distribution, join_shops


def test_duplicate_ids_are_all_excluded():
    frame = pd.DataFrame({"shop_id": ["SYN_A", "SYN_A", "SYN_B", None], "dong": ["가", "나", "다", "라"]})
    clean, duplicates = clean_shops(frame)
    assert list(clean.shop_id) == ["SYN_B"] and duplicates.shop_id.nunique() == 1


def test_ratio_zero_and_small_denominators():
    assert all(np.isnan(safe_ratio(a, b)[0]) for a, b in [(0, 0), (2, 10), (3, 2)])
    assert safe_ratio(3, 6) == (0.5, 3, 6)


def test_distribution_minimum_shops():
    assert all(pd.isna(x) for x in distribution(pd.Series([5]*49)).values())
    assert distribution(pd.Series([5]*50))["p50"] == 5


def test_missing_shop_bucket_and_digit_dong():
    clean = pd.DataFrame({"shop_id": ["SYN_A", "SYN_B"], "dong": ["비산1동", "비산동"],
                          "gungu": ["SYN_G", "SYN_G"], "child_able": ["Y", "N"]})
    joined = join_shops(pd.DataFrame({"shop_id": ["SYN_A", "SYN_MISSING"]}), clean)
    assert joined.child_able.tolist() == ["Y", "<NOT_IN_TABLE>"]
    assert clean.dong.str.contains(r"[0-9]동$").tolist() == [True, False]


def test_shop_auxiliary_small_counts_are_masked(monkeypatch):
    from lib import m3
    captured = []
    monkeypatch.setattr(m3, "emit", lambda ctx, frame, *args, **kwargs: captured.append(frame))
    frame = pd.DataFrame({"gungu": ["SYN_G"], "n_shop": [5], "n_dong_unique": [1]})
    m3._shop_emit(None, frame, "SYNTHETIC_aux", ["gungu"], "n_shop")
    assert pd.isna(captured[0].n_dong_unique.iloc[0])


def test_m3_small_cli_and_no_export_ids(case_dir):
    import json
    import re
    from test_module_cli import _fixture, _run
    from export_check import check_run
    cfg, config = _fixture(case_dir)
    process, run = _run("40_m3_shop.py", config)
    assert process.returncode == 0, process.stderr
    manifest = json.loads((run / "export/run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["modules"][-1]["extra"]["dup_id_excluded_shops"] == 1
    summary = pd.read_csv(run / "internal/m3_shop_pay_summary.csv")
    assert summary.pay_n_all.sum() == 15 and summary.pay_n_meal.sum() == 15
    for path in (run / "export").glob("*.csv"):
        assert not re.search(r"SYN_(SHOP|CUST)_[0-9]{4}", path.read_text(encoding="utf-8-sig"))
    assert check_run(config, run)["fail_count"] == 0
