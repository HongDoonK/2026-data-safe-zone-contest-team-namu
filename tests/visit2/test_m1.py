"""SYNTHETIC hand-countable M1 contracts."""
import pandas as pd

from lib.m1 import gate_branches, month_grid, transitions, month_disclosure_plan, export_values
from lib.pipeline import open_context
from test_module_cli import _fixture, _run


def test_gate_gap_is_not_reclassified():
    result = gate_branches(100000, 500, 18)
    assert result["branch_count_true"] == 0
    assert "규칙상 미정" in result["branch_note"]


def test_month_grid_twelve_cells():
    data = pd.DataFrame({"pay_gbn": ["SYN_A", "SYN_B", "SYN_C", "SYN_A"],
                         "ym": [202301, 202302, 202303, 202304],
                         "n": [5]*4, "n_shop": [3]*4, "n_cust": [5]*4})
    result = month_grid(data)
    assert len(result) == 12
    assert result.n.eq(0).sum() == 8


def test_transition_gap_and_overlap():
    values = pd.DataFrame({"pay_gbn": ["SYN_A", "SYN_B"], "n": [6, 6],
                           "first_ym": [202301, 202306], "last_ym": [202305, 202310]})
    customers = {"SYN_A": set(range(6)), "SYN_B": set(range(1, 7))}
    shops = {"SYN_A": set(range(3)), "SYN_B": set(range(3))}
    row = transitions(values, customers, shops).query("a == 'SYN_A' and b == 'SYN_B'").iloc[0]
    assert row.gap_months == 1 and row.cust_overlap == 5 and row.shop_overlap == 3


def test_rare_value_bands_then_excludes_unresolved_months(case_dir):
    cfg, config = _fixture(case_dir)
    a = pd.DataFrame({"pay_gbn": ["SYN_RARE"], "card_pay_gbn": ["SYN_DONE"],
                      "n": [7], "n_shop": [7], "n_cust": [7]})
    b = pd.DataFrame({"ym": [202301, 202302, 202303], "pay_gbn": ["SYN_RARE"]*3,
                      "n": [0, 3, 4], "n_shop": [0, 3, 4], "n_cust": [0, 3, 4]})
    planned, monthly, banded, trace = month_disclosure_plan(a, b, cfg)
    assert [item["step"] for item in trace] == ["exact_totals", "band_A_retry_B", "exclude_unresolved_B"]
    assert monthly.empty and banded == {"SYN_RARE"}
    assert planned.note.iloc[0] == "월별 표 제외(노출)"
    out = export_values(open_context(cfg), planned, banded)
    assert out.n.iloc[0] == "<50" and out.status.iloc[0] == "banded"


def test_m1_unset_meal_runs_discovery(case_dir):
    import json
    cfg, config = _fixture(case_dir)
    cfg["meal_pay_values"] = []
    config.write_text(json.dumps(cfg), encoding="utf-8")
    process, run = _run("20_m1_paygbn.py", config)
    assert process.returncode == 0, process.stderr
    assert "게이트 계산 건너뜀" in process.stdout
    assert not (run / "export/m1_gate.csv").exists()


def test_m1_gate_uses_full_period_distinct_shops(case_dir):
    import csv
    cfg, config = _fixture(case_dir)
    with open(cfg["paths"]["pay"], "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        original = list(reader)[0]
    with open(cfg["paths"]["pay"], "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        for index in range(5, 10):
            row = dict(original, SHOP_ID="SYN_SHOP_%04d" % index, CUST_ID="SYN_CUST_%04d" % index,
                       CARD_APP_TIME="2023070312")
            writer.writerow(row)
    process, run = _run("20_m1_paygbn.py", config)
    assert process.returncode == 0, process.stderr
    gate = pd.read_csv(run / "internal/m1_gate.csv")
    assert gate.loc[gate.status_mode.eq("all"), "N_SHOP"].iloc[0] == 10
