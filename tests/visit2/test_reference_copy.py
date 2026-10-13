"""Reference values must be literal copies of approved exported CSVs."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_reference_copy():
    aliases = {"월": "ym", "요일": "dow", "시": "hour", "건수": "n", "가게수": "n_shop", "손님수": "n_cust"}
    for source, target in [("t_month.csv", "export_0911_month.json"), ("t_week_hour.csv", "export_0911_week_hour.json")]:
        path = ROOT / "analysis/visit2/reference" / target
        assert path.exists(), "reference implementation missing"
        copied = json.loads(path.read_text(encoding="utf-8"))
        with (ROOT / "9_11_데이터분석결과물" / source).open(encoding="utf-8-sig", newline="") as handle:
            original = list(csv.DictReader(handle))
        assert len(copied) == len(original)
        for actual, row in zip(copied, original):
            assert set(actual) == {aliases[col] for col in row}
            for col, raw in row.items():
                value = actual[aliases[col]]
                if raw == "":
                    assert value is None
                elif col == "요일":
                    assert value == ("화" if raw == "와" else raw)
                elif col == "월":
                    assert value == raw
                else:
                    assert value == json.loads(raw)


def test_reference_meta_exact():
    path = ROOT / "analysis/visit2/reference/reference_meta.json"
    assert path.exists()
    actual = json.loads(path.read_text(encoding="utf-8"))
    for name, keys in [("export_0911_month", ["ym"]), ("export_0911_week_hour", ["dow", "hour"])]:
        assert actual[name] == {"keys": keys, "metrics": ["n", "n_shop", "n_cust"],
                                "population": "0911_unknown", "zero_policy": "absent_row",
                                "time_only": True, "night_bucket_applied": False}


def test_reference_selfcheck():
    import selfcheck
    assert hasattr(selfcheck, "test_0911_known")
    selfcheck.test_0911_known()
