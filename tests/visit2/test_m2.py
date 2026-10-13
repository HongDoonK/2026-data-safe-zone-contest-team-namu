"""SYNTHETIC M2 fixed-grid and within-shop contracts."""
import pandas as pd
from lib.m2 import complete_grid, both_shops, public_ci
from lib.stats import share_diff_bootstrap


def test_profile_grid_shapes():
    empty = pd.DataFrame(columns=["R", "dow", "hour_bucket", "n", "n_shop", "n_cust"])
    assert len(complete_grid(empty, {"R": ["a", "b", "c"], "dow": list(range(7)), "hour_bucket": list(range(18))})) == 378
    empty = empty.rename(columns={"hour_bucket": "hour"})
    assert len(complete_grid(empty, {"R": ["a", "b", "c"], "dow": list(range(7)), "hour": list(range(24))})) == 504


def test_both_shop_excludes_meal_only():
    frame = pd.DataFrame({"shop_id": ["SYN_A", "SYN_A", "SYN_B", "SYN_B", "SYN_C"],
                          "G": ["meal", "general", "meal", "general", "meal"], "n": [5]*5})
    assert both_shops(frame) == {"SYN_A", "SYN_B"}


def test_small_shop_ci_hidden():
    ci = share_diff_bootstrap([[5]*8], [[5]*8], 200, 1)
    assert (ci.ci_high - ci.ci_low).eq(0).all()
    out = public_ci(ci, set(range(8)))
    assert out.ci_low.isna().all() and out.ci_high.isna().all()


def test_small_cli_grids_edge_zero_and_200_reps(case_dir):
    import json
    from test_module_cli import _fixture, _run
    from export_check import check_run
    cfg, config = _fixture(case_dir)
    cfg["bootstrap"]["reps"] = 200
    config.write_text(json.dumps(cfg), encoding="utf-8")
    process, run = _run("30_m2_compare.py", config)
    assert process.returncode == 0, process.stderr
    for name, expected in [("m2_meal_regime_dow_hour", 378), ("m2_general_regime_dow_hour", 504),
                            ("m2_within_shop_meal", 48), ("m2_within_shop_general", 48)]:
        assert len(pd.read_csv(run / "internal" / (name + ".csv"))) == expected
    meal = pd.read_csv(run / "internal/m2_hour_edge_meal.csv")
    general = pd.read_csv(run / "internal/m2_hour_edge_general.csv")
    assert meal.loc[meal.hour_bucket.eq("23-05"), "days_with_any"].eq(0).all()
    assert general.loc[general.hour.isin(range(1, 6)), "days_with_any"].eq(0).all()
    for path in (run / "export").glob("*.csv"):
        table = pd.read_csv(path)
        assert not any(col.startswith("share_") for col in table)
        meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
        assert len(meta["keys"]) <= 3
    assert check_run(config, run)["fail_count"] == 0


def test_general_only_night_rows_are_counted(case_dir):
    import csv
    from test_module_cli import _fixture, _run
    cfg, config = _fixture(case_dir)
    with open(cfg["paths"]["pay"], encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        row = next(reader)
    with open(cfg["paths"]["pay"], "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writerow(dict(row, PAY_GBN="SYN_GENERAL", CARD_APP_TIME="2023060503"))
    process, run = _run("30_m2_compare.py", config)
    assert process.returncode == 0, process.stderr
    edge = pd.read_csv(run / "internal/m2_hour_edge_general.csv")
    assert edge.loc[edge.hour.eq(3) & edge.daytype.eq("weekday"), "days_with_any"].iloc[0] == 1


def test_m0_population_difference_is_recorded(case_dir):
    import json
    import subprocess
    import sys
    from lib.config import load_config
    from lib.pipeline import open_context
    from test_module_cli import _fixture, ROOT
    cfg, config = _fixture(case_dir)
    ctx = open_context(load_config(config))
    ctx.finish("SYNTHETIC_prior", {})
    pd.DataFrame({"ym": [202306], "n": [99], "n_shop": [5], "n_cust": [5], "status": ["published"]}).to_csv(ctx.export / "m0_month.csv", index=False)
    previous = {"keys": ["ym"], "metrics": ["n", "n_shop", "n_cust"], "population": "SYNTHETIC_DIFFERENT",
                "population_kind": "meal", "time_only": True, "zero_policy": "mask", "night_bucket_applied": False}
    (ctx.export / "m0_month.meta.json").write_text(json.dumps(previous), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "analysis/visit2/30_m2_compare.py"),
                             "--config", str(config), "--run", str(ctx.root)], capture_output=True)
    assert result.returncode == 0, result.stderr
    difference = pd.read_csv(ctx.internal / "m2_m0_month_difference.csv")
    assert difference.difference.iloc[0] == -84
    current = json.loads((ctx.export / "m2_month_group.meta.json").read_text(encoding="utf-8"))
    assert current["population"] != previous["population"]
