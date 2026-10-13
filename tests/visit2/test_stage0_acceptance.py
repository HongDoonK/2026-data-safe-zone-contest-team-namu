"""Stage-0 acceptance, including the user's 2026-09-18 refusal decision."""
from pathlib import Path

import pandas as pd

from lib.suppress import suppress


def test_suppress_secondary_group():
    """User accepted unresolved/refusal when fixed bounds cannot fit a peer."""
    path = Path(__file__).parent / "fixtures/SYNTHETIC_secondary_group.csv"
    df = pd.read_csv(path)
    result, report = suppress(df, ["key"], known_totals={((), ()): 10})
    assert report["secondary_cells"] == 1
    assert result.status.eq("suppressed").all()
    assert report["unresolved"]
    assert any(item["reason"] == "hidden_count_outside_specified_domain"
               for item in report["unresolved"])
