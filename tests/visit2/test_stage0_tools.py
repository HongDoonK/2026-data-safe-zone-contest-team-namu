"""SYNTHETIC executable and generation contracts."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_selfcheck_executable():
    path = ROOT / "analysis/visit2/selfcheck.py"
    assert path.exists(), "selfcheck is not implemented"
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_synthetic_generator_both_headers(case_dir):
    path = ROOT / "synthetic/visit2/make_synthetic.py"
    assert path.exists(), "synthetic generator is not implemented"
    result = subprocess.run([sys.executable, str(path), "--rows", "48", "--out", str(case_dir)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    en = pd.read_csv(case_dir / "SYNTHETIC_PAY_en.csv", dtype=str, keep_default_na=False)
    ko = pd.read_csv(case_dir / "SYNTHETIC_PAY_ko.csv", dtype=str, keep_default_na=False)
    assert len(en) == len(ko) == 48
    assert en.values.tolist() == ko.values.tolist()
    assert "SHOP_ID" in en and "가맹점코드" in ko
    assert en.CARD_APP_TIME.str.len().ne(10).any()
    assert en.PAY_GBN.str.strip().nunique() >= 5
    assert en.PAY_GBN.str.startswith(" ").any()
    assert en.PAY_GBN.eq("").any()
    shop = pd.read_csv(case_dir / "SYNTHETIC_SHOP_en.csv", dtype=str)
    assert shop.SHOP_ID.duplicated().sum() == 1
    assert set(en.SHOP_ID.str.strip()) - set(shop.SHOP_ID)


def test_synthetic_generator_rejects_outside_synthetic(case_dir):
    path = ROOT / "synthetic/visit2/make_synthetic.py"
    assert path.exists()
    result = subprocess.run([sys.executable, str(path), "--rows", "48", "--out", str(ROOT / "out")],
                            capture_output=True, text=True)
    assert result.returncode != 0


def test_synthetic_large_fixed_grid(case_dir):
    path = ROOT / "synthetic/visit2/make_synthetic.py"
    result = subprocess.run([sys.executable, str(path), "--rows", "40000", "--out", str(case_dir)],
                            capture_output=True, text=True)
    assert result.returncode == 0
    en = pd.read_csv(case_dir / "SYNTHETIC_PAY_en.csv", dtype=str, keep_default_na=False)
    good = en[en.CARD_APP_TIME.str.fullmatch(r"[0-9]{10}")]
    dates = pd.to_datetime(good.CARD_APP_TIME, format="%Y%m%d%H", errors="coerce")
    assert set(dates.dt.month) >= {1, 7, 9}
    assert set(dates.dt.weekday) == set(range(7))
    assert set(dates.dt.hour) == set(range(24))
    assert good.SHOP_ID.nunique() >= 36
