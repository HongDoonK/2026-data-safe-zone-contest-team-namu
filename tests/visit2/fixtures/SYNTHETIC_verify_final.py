"""Verify persisted SYNTHETIC end-to-end evidence, without pytest."""
import ast
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/visit2"))
from export_check import check_run


def main():
    base = ROOT / "tests/visit2/fixtures"
    evidence = {"label": "SYNTHETIC", "runs": [], "python38_runtime_tested": False}
    pattern = re.compile(r"SYN_(SHOP|CUST)_[0-9]{4}")
    for language in ("en", "ko"):
        log = base / ("SYNTHETIC_e2e_" + language + ".stdout.txt")
        console = log.read_text(encoding="utf-8")
        errors = log.with_name(log.name.replace("stdout", "stderr")).read_text(encoding="utf-8")
        run = Path(console.split("run=")[-1].strip())
        manifest = json.loads((run / "export/run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["run_all"]["exit_code"] == 0
        result = check_run(ROOT / "synthetic/visit2" / ("SYNTHETIC_config_" + language + ".json"), run)
        assert result["fail_count"] == 0
        report = (run / "internal/export_check_report.txt").read_text(encoding="utf-8")
        assert not pattern.search(console + errors + report)
        files = list((run / "export").glob("*.csv"))
        assert {path.name for path in files} == set(manifest["exports"])
        for path in files:
            text = path.read_text(encoding="utf-8-sig")
            assert not pattern.search(text)
            meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
            assert len(meta["keys"]) <= 3
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                header = reader.fieldnames
            assert not {"shop_id", "cust_id", "p99", "maximum", "max", "p_value", "pvalue"} & {name.lower() for name in header}
            for row in rows:
                if row["status"] == "suppressed":
                    assert all(not row[column] for column in header if column not in meta["keys"] + ["status"])
            if path.name.startswith("m2_"):
                assert not any(column.startswith("share_") for column in header)
            if meta.get("population_kind") == "meal" and "hour" in meta["keys"]:
                assert not any(int(row["hour"]) in (23, 0, 1, 2, 3, 4, 5) for row in rows)
        for name, count in (("m2_meal_regime_dow_hour", 378), ("m2_general_regime_dow_hour", 504),
                            ("m2_within_shop_meal", 48), ("m2_within_shop_general", 48)):
            with (run / "export" / (name + ".csv")).open(encoding="utf-8-sig", newline="") as handle:
                assert len(list(csv.DictReader(handle))) == count
        timing = json.loads((run / "internal/run_all_timing.json").read_text(encoding="utf-8"))
        assert all(record["exit_code"] == 0 for record in timing["steps"])
        upper = [record.get("combined_peak_upper_bound_bytes") for record in timing["steps"]]
        rejected = {record["module"]: record["extra"].get("rejected_tables", []) for record in manifest["modules"]
                    if record["extra"].get("rejected_tables")}
        evidence["runs"].append({"language": language, "run": str(run), "csv_files": len(files),
                                  "fail_count": result["fail_count"], "warn_count": result["warn_count"],
                                  "seconds": timing["seconds"], "steps": timing["steps"],
                                  "combined_peak_upper_bound_bytes": max(value for value in upper if value is not None),
                                  "rejected_tables": rejected})
    sources = list((ROOT / "analysis/visit2").rglob("*.py"))
    local = {path.stem for path in sources} | {"lib", "pandas", "numpy"}
    imports = set()
    for path in sources:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), feature_version=(3, 8))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.NamedExpr)
            if isinstance(node, ast.Import):
                imports.update(item.name.split(".")[0] for item in node.names)
            elif isinstance(node, ast.ImportFrom) and not node.level:
                imports.add(node.module.split(".")[0])
            if isinstance(node, ast.Attribute):
                assert node.attr not in {"is_relative_to", "removeprefix", "removesuffix"}
    assert not imports - sys.stdlib_module_names - local
    evidence["python38_ast_files"] = len(sources)
    evidence["unapproved_imports"] = []
    (base / "SYNTHETIC_final_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SYNTHETIC final audit PASS: en/ko, strict suppression, no raw IDs, grids, Python 3.8 syntax, imports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
