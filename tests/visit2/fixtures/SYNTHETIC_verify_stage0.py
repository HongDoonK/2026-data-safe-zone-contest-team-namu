"""SYNTHETIC evidence: user accepted fail-closed secondary suppression."""
import ast
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/visit2"))
from lib.config import load_config
from lib.distinct import CountAccumulator, DistinctAccumulator
from lib.io import detect_encoding, iter_chunks
from lib.manifest import start_run
from lib.suppress import exposure_ranges, suppress
from lib.timeparse import add_time_fields


def main():
    base = Path(__file__).resolve().parent
    evidence = {"label": "SYNTHETIC", "small_input": {}, "boundaries": [], "source_audit": {}}
    for lang in ("en", "ko"):
        cfg = load_config(base / ("SYNTHETIC_stage0/SYNTHETIC_config_%s.json" % lang))
        enc = detect_encoding(cfg["paths"]["pay"], cfg["encoding_candidates"])
        counts = CountAccumulator([])
        distinct = DistinctAccumulator([])
        invalid = 0
        chunks = 0
        for df in iter_chunks(cfg["paths"]["pay"], list(cfg["cols_pay"]), cfg["cols_pay"], enc, 3):
            counts.update(df)
            distinct.update(df, "cust_id")
            invalid += int(add_time_fields(df).time_invalid.sum())
            chunks += 1
        actual = {"rows": int(counts.finalize().n.iloc[0]), "customers": int(distinct.finalize()["nunique"].iloc[0]),
                  "invalid_time_rows": invalid, "chunks": chunks}
        assert actual == {"rows": 48, "customers": 12, "invalid_time_rows": 2, "chunks": 16}
        evidence["small_input"][lang] = actual
    for args, expected in [((11, 10, 1, 4), (1, 2)), ((11, 10, 0, 4), (0, 4)),
                           ((11, 3, 0, 4), (3, 4)), ((0, 3, 0, 4), (0, 0)),
                           ((12, 3, 0, 4), (4, 4)), ((3, 1, 0, 4), (3, 3))]:
        ranges = exposure_ranges(*args)
        assert ranges == [expected] * args[1]
        evidence["boundaries"].append({"args": args, "range": expected, "pass": True})
    source_files = sorted((ROOT / "analysis/visit2").rglob("*.py")) + [ROOT / "synthetic/visit2/make_synthetic.py"]
    dependencies = set()
    for path in source_files:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, feature_version=(3, 8))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and not node.level:
                dependencies.add(node.module.split(".")[0])
            assert not isinstance(node, ast.NamedExpr)
    local_modules = {path.stem for path in (ROOT / "analysis/visit2").glob("*.py")}
    external = dependencies - sys.stdlib_module_names - {"lib", "pandas", "numpy"} - local_modules
    assert not external, external
    evidence["source_audit"] = {"python38_parse_files": len(source_files), "unapproved_imports": sorted(external),
                                "runtime_python": sys.version.split()[0], "python38_runtime_tested": False}
    df = pd.read_csv(base / "SYNTHETIC_secondary_group.csv")
    out, report = suppress(df, ["key"], known_totals={((), ()): 10})
    meta = {"keys": ["key"], "metrics": ["n", "n_shop", "n_cust"], "population": "SYNTHETIC_meal",
            "time_only": False, "zero_policy": "mask", "night_bucket_applied": False}
    cfg["paths"]["out_root"] = str(base / "SYNTHETIC_gate_output")
    ctx = start_run(cfg)
    try:
        ctx.write_export(out, "SYNTHETIC_secondary", report, meta)
    except ValueError as exc:
        evidence["secondary_gate"] = {"result": "PASS_EXPECTED_REFUSAL", "write_export": "REFUSED",
                                       "reason": str(exc), "unresolved_reasons": [x["reason"] for x in report["unresolved"]]}
    else:
        raise AssertionError("unsafe fixed-domain secondary table was exported")
    assert not list(ctx.export.glob("*.csv"))
    (base / "SYNTHETIC_stage0_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SYNTHETIC stage-0: small en/ko PASS; boundaries PASS; source audit PASS; expected refusal PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
