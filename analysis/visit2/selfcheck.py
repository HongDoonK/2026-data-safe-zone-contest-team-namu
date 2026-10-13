"""Offline checks. No pytest or input files required at stage 0."""
import sys
from pathlib import Path

import pandas as pd

from lib.distinct import DistinctAccumulator
from lib.suppress import exposure_ranges, suppress
from lib.timeparse import add_time_fields, label_dow


def test_0911_known():
    from export_check import check_references
    result = check_references(Path(__file__).resolve().parent / "config/visit2.json")
    assert result["fail_count"] == 0
    assert result["known_count"] == 10
    known = [item for item in result["exposures"] if item["status"] == "KNOWN"]
    assert len(known) == 10 and all(item["range"] == [1, 2] for item in known)


def main():
    assert exposure_ranges(11, 10, 1, 4) == [(1, 2)] * 10
    assert exposure_ranges(11, 10, 0, 4) == [(0, 4)] * 10
    assert exposure_ranges(11, 3, 0, 4) == [(3, 4)] * 3
    df = pd.DataFrame({"app_time": ["202409%02d12" % day for day in range(16, 23)]})
    assert [label_dow(x) for x in add_time_fields(df).dow] == ["월", "화", "수", "목", "금", "토", "일"]
    acc = DistinctAccumulator(["key"])
    chunk = pd.DataFrame({"key": ["SYNTHETIC"], "cust_id": ["SYNTHETIC_C1"]})
    acc.update(chunk, "cust_id")
    acc.update(chunk, "cust_id")
    assert acc.finalize()["nunique"].tolist() == [1]
    out, report = suppress(pd.DataFrame({"key": ["SYNTHETIC_A", "SYNTHETIC_B"], "n": [5, 7]}),
                           ["key"], shop_col=None, cust_col=None)
    assert not report["unresolved"] and out.status.eq("published").all()
    test_0911_known()
    print("selfcheck PASS: SYNTHETIC boundaries/dow/distinct; 0911 references KNOWN=10")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, ValueError) as exc:
        print("FAIL selfcheck: " + type(exc).__name__, file=sys.stderr)
        sys.exit(1)
