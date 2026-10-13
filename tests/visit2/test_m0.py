"""SYNTHETIC M0 reference matching contracts."""
import pandas as pd
from lib.m0 import compare_months
from lib.suppress import suppress


def test_month_reference_exact_and_distinct_mismatch():
    frame = pd.DataFrame({"ym": [202306], "n": [7], "n_shop": [3], "n_cust": [5]})
    reference = [{"ym": "2023-06", "n": 7, "n_shop": 3, "n_cust": 5}]
    assert compare_months(frame, reference)["matched"]
    frame.loc[0, "n_cust"] = 4
    assert not compare_months(frame, reference)["matched"]


def test_extra_month_is_not_exact_match():
    frame = pd.DataFrame({"ym": [202306, 202307], "n": [7, 5], "n_shop": [3, 3], "n_cust": [5, 5]})
    reference = [{"ym": "2023-06", "n": 7, "n_shop": 3, "n_cust": 5}]
    assert not compare_months(frame, reference)["matched"]


def test_night_mask_with_known_total_preserves_domain():
    # SYNTHETIC literal counts, not an estimate of suppressed reference data.
    frame = pd.DataFrame({"dow": list(range(7)), "hour_bucket": ["23-05"] * 7,
                          "n": [2, 2, 2, 2, 1, 1, 1], "n_shop": [1]*7, "n_cust": [1]*7})
    out, report = suppress(frame, ["dow", "hour_bucket"], known_totals={((), ()): 11})
    assert not report["unresolved"]
    assert out.n.isna().all() and out.status.eq("suppressed").all()
