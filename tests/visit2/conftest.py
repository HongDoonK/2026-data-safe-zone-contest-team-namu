"""Local fixtures only; no real input is written by tests."""
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis" / "visit2"))


@pytest.fixture
def case_dir():
    path = Path(__file__).parent / "fixtures" / ("SYNTHETIC_" + uuid.uuid4().hex)
    path.mkdir(parents=True)
    return path
