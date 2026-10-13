"""SYNTHETIC offline CLI checks with literal hand-counted fixtures."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from export_check import check_run

ROOT = Path(__file__).resolve().parents[2]


def _fixture(case_dir, reference_count=None, modes=None):
    cfg = json.loads((ROOT / "analysis/visit2/config/visit2.json").read_text(encoding="utf-8"))
    cfg["run_label"] = "SYNTHETIC"
    cfg["meal_pay_values"] = ["SYN_MEAL_A", "SYN_MEAL_B"]
    cfg["id_patterns"] = [r"SYN_(SHOP|CUST)_[0-9]{4}"]
    shop = case_dir / "SYNTHETIC_shop.csv"
    shop_map = cfg["columns"]["en"]["shop"]
    with shop.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(shop_map.values()))
        writer.writeheader()
        for i in list(range(6)) + [0]:
            row = {"shop_id": "SYN_SHOP_%04d" % i, "gungu": "SYN_G", "dong": "SYN_D",
                   "child_able": "Y" if i % 2 == 0 else "N", "good_able": "N",
                   "store_status": "SYN_OPEN", "closed_at": "", "service_closed": "SYN_ACTIVE"}
            writer.writerow({shop_map[k]: v for k, v in row.items()})
    cfg["paths"]["shop"] = str(shop)
    pay = case_dir / "SYNTHETIC_pay.csv"
    header = list(cfg["columns"]["en"]["pay"].values())
    mapping = cfg["columns"]["en"]["pay"]
    with pay.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        for status in (modes or ["완료", "대기", "취소"]):
            for i in range(5):
                row = {"shop_id": "SYN_SHOP_%04d" % i, "cust_id": "SYN_CUST_%04d" % i,
                       "pay_gbn": "SYN_MEAL_A", "card_pay_gbn": status,
                       "dest_pay_gbn": "SYN_DEST", "app_time": "2023060512", "tot_amt": "5", "app_amt": "5"}
                writer.writerow({mapping[k]: v for k, v in row.items()})
    cfg["paths"]["pay"] = str(pay)
    cfg["paths"]["out_root"] = str(case_dir / "SYNTHETIC_out")
    cfg["chunksize"] = 3
    cfg["reference_exports"] = None
    if reference_count is not None:
        ref = case_dir / "SYNTHETIC_reference.json"
        ref.write_text(json.dumps([{"ym": "2023-06", "n": reference_count, "n_shop": 5, "n_cust": 5}]), encoding="utf-8")
        meta = {"export_0911_month": {"keys": ["ym"], "metrics": ["n", "n_shop", "n_cust"],
                                     "population": "0911_unknown", "zero_policy": "absent_row"}}
        (case_dir / "reference_meta.json").write_text(json.dumps(meta), encoding="utf-8")
        cfg["reference_exports"] = {"export_0911_month": str(ref)}
    config = case_dir / "SYNTHETIC_config.json"
    config.write_text(json.dumps(cfg), encoding="utf-8")
    return cfg, config


def _run(script, config):
    process = subprocess.run([sys.executable, str(ROOT / "analysis/visit2" / script), "--config", str(config)],
                             capture_output=True, text=True, encoding="utf-8",
                             env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    cfg = json.loads(config.read_text(encoding="utf-8"))
    run = next(Path(cfg["paths"]["out_root"]).iterdir())
    return process, run


def test_m0_unique_match_and_no_hour_export(case_dir):
    cfg, config = _fixture(case_dir, 5)
    process, run = _run("10_m0_reproduce.py", config)
    assert process.returncode == 0, process.stderr
    manifest = json.loads((run / "export/run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["modules"][-1]["extra"]["selected_mode"] == "complete_only"
    assert not list((run / "export").glob("m0_dow_hour_all.csv"))
    assert (run / "export/m0_month.csv").exists()


def test_m0_no_match_refuses_exports(case_dir):
    cfg, config = _fixture(case_dir, 99)
    process, run = _run("10_m0_reproduce.py", config)
    assert process.returncode == 2
    assert not list((run / "export").glob("*.csv"))


def test_m0_multiple_match_refuses_exports(case_dir):
    cfg, config = _fixture(case_dir, 5, ["완료"])
    process, run = _run("10_m0_reproduce.py", config)
    assert process.returncode == 2
    assert not list((run / "export").glob("*.csv"))


def test_m0_no_reference_runs_and_checks(case_dir):
    cfg, config = _fixture(case_dir)
    process, run = _run("10_m0_reproduce.py", config)
    assert process.returncode == 0, process.stderr
    assert check_run(config, run)["fail_count"] == 0


def test_m0_exactly_two_matches_refuses_exports(case_dir):
    cfg, config = _fixture(case_dir, 10, ["완료", "대기"])
    process, run = _run("10_m0_reproduce.py", config)
    assert process.returncode == 2
    manifest = json.loads((run / "export/run_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["modules"][-1]["extra"]["matches"]) == 2
    assert not list((run / "export").glob("*.csv"))
