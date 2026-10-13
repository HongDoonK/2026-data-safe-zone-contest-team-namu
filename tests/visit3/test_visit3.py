"""SYNTHETIC tests: no real-data numeric assertions."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, str(ROOT / relative))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_plan_cells_exact():
    path = ROOT / "analysis/visit3/extract_cells.py"
    assert path.is_file(), "literal-cell extractor is not implemented"
    extractor = module("extractor", "analysis/visit3/extract_cells.py")
    checks = extractor.check()
    assert len(checks) == 15
    assert all(c["synced"] and c["lines"] == c["expected_lines"] for c in checks)


def test_full_validation_evidence():
    import json
    path = ROOT / "synthetic/visit3/out_SYNTHETIC/SYNTHETIC_validation.json"
    assert path.is_file(), "run python analysis/visit3/validate.py first"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    assert evidence["exceptions"] == 0
    assert evidence["oracle_failures"] == []
    assert evidence["chunk_failures"] == []
    assert evidence["large_chunk_failures"] == []
    assert all(evidence["p0_conditions"].values())
    assert all(evidence["export_trap_tests"].values())
    assert evidence["recovery_ok"]
    assert evidence["python38_syntax"]
    assert evidence["protected_hashes_unchanged"]


def test_memory_measurement_is_live():
    import sys
    sys.path.insert(0, str(ROOT / "analysis/visit3"))
    runner = module("runner", "analysis/visit3/run_cells.py")
    current, peak = runner.memory_bytes()
    assert current > 0 and peak >= current


@pytest.fixture(scope="module")
def reference():
    import sys
    sys.path.insert(0, str(ROOT / "analysis/visit3"))
    from oracle import calculate
    return calculate(ROOT / "synthetic/visit3/data_SYNTHETIC/SYNTHETIC_pay_small.csv",
                     ROOT / "synthetic/visit3/data_SYNTHETIC/SYNTHETIC_shop.csv")


@pytest.mark.parametrize("cell", ["S1", "P1", "P1b", "P2", "P3", "M1", "M2", "M3", "M4", "M5", "M6", "A1", "A2", "A3", "A4"])
def test_independent_reference_each_cell(reference, cell):
    import json
    from run_cells import canonical
    output = ROOT / "synthetic/visit3/out_SYNTHETIC/SYNTHETIC_small_original"
    record = json.loads((output / ("SYNTHETIC_" + cell + "_record.json")).read_text(encoding="utf-8"))
    assert record["exception"] is None
    assert record["snapshot"] == canonical(reference[0][cell])


@pytest.mark.parametrize("name", ["EXPORT_m4_dong_regime_SYNTHETIC.csv", "EXPORT_m4_dong_total_SYNTHETIC.csv",
                                  "EXPORT_m4_u2_gungu_status_SYNTHETIC.csv", "EXPORT_m5_amount_hist_SYNTHETIC.csv"])
def test_independent_reference_saved_csv(reference, name):
    from validate import read_exports
    from run_cells import canonical
    output = ROOT / "synthetic/visit3/out_SYNTHETIC/SYNTHETIC_small_original"
    assert canonical(read_exports(output)[name]) == canonical(reference[1][name])


def test_reidentification_traps_are_detected():
    from validate import traps
    assert all(traps({}).values())


def test_dependency_recovery_minimum_cells():
    from run_cells import selected
    assert selected("M5") == ["S1", "M1", "M2", "M3", "M4", "M5"]
    assert selected("P1b") == ["S1", "P1", "P1b"]


def test_all_python38_syntax():
    import ast
    for folder in ["analysis/visit3", "tests/visit3", "synthetic/visit3"]:
        for path in (ROOT / folder).rglob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 8))


def test_B_fixture_is_rare_marker_not_C1():
    import csv
    from collections import Counter
    counts, marked = Counter(), Counter()
    path = ROOT / "synthetic/visit3/data_SYNTHETIC/SYNTHETIC_P0_B.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            ym = row["CARD_APP_TIME"][:6]
            if row["PAY_GBN"].strip() == "행복페이" and "202201" <= ym < "202306":
                counts[ym] += 1
                marked[ym] += float(row["CHILD_DISC_AMT"]) > 0
    assert len(counts) == 17
    assert all(marked[ym] / counts[ym] == .01 for ym in counts)

