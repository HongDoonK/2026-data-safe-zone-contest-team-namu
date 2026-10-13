"""Execute the real CLI on approved references and SYNTHETIC attacks."""
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/visit2"))
from lib.filters import describe_filter


def main():
    base = Path(__file__).parent / "SYNTHETIC_stage1_cli"
    base.mkdir(exist_ok=True)
    cfg = json.loads((ROOT / "analysis/visit2/config/visit2.json").read_text(encoding="utf-8"))
    cfg["reference_exports"] = {name: str((ROOT / "analysis/visit2" / path).resolve())
                                for name, path in cfg["reference_exports"].items()}
    cfg["id_patterns"] = [r"SYN_ID_[0-9]+"]
    cfg["export"]["time_only_axes_exception"] = True
    config = base / "SYNTHETIC_config.json"
    config.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    old = json.loads((ROOT / "analysis/visit2/reference/export_0911_week_hour.json").read_text(encoding="utf-8"))
    day = [{"dow": row["dow"], "hour_bucket": "%02d" % row["hour"], "n": row["n"],
            "n_shop": row["n_shop"], "n_cust": row["n_cust"], "status": "published"}
           for row in old if 6 <= row["hour"] <= 22]
    night = [{"dow": dow, "hour_bucket": "23-05", "n": "", "n_shop": "", "n_cust": "", "status": "suppressed"}
             for dow in ("월", "화", "수", "목", "금", "토", "일")]
    cases = {
        "reference": ([], [], 0, None),
        "a_new_known": ([{"dow": "금", "hour": 23, "n": 2, "status": "published"}], ["dow", "hour"], 1, "C8"),
        "b_safe_night": (day + night, ["dow", "hour_bucket"], 0, None),
        "c_id_cell": ([{"g": "SYN_ID_123", "n": 5, "status": "published"}], ["g"], 1, "C2"),
        "c_id_header": ([{"share_SYN_ID_456": "x", "n": 5, "status": "published"}], ["share_SYN_ID_456"], 1, "C2"),
        "d_region_axes": ([{"dong": "SYNTHETIC_D", "a": "a", "b": "b", "c": "c", "n": 5, "status": "published"}], ["dong", "a", "b", "c"], 1, "C5"),
        "e_no_status": ([{"g": "SYNTHETIC", "n": 5}], ["g"], 1, "C3"),
        "e_no_meta": ([{"g": "SYNTHETIC", "n": 5, "status": "published"}], ["g"], 1, "C3"),
        "e_bad_status": ([{"g": "SYNTHETIC", "n": 5, "status": "wrong"}], ["g"], 1, "C3"),
        "f_night_hour": ([{"hour": 23, "n": 5, "status": "published"}], ["hour"], 1, "C6"),
        "g_empty": ([], [], 1, "C1"),
        "g_bad_csv": ([{"g": "SYNTHETIC", "n": 5, "status": "published"}], ["g"], 1, "C3"),
        "g_cp949": ([{"g": "합성", "n": 5, "status": "published"}], ["g"], 1, "C3"),
    }
    results = []
    for name, (rows, keys, exit_code, check) in cases.items():
        run = base / ("SYNTHETIC_" + name)
        export = run / "export"
        export.mkdir(parents=True, exist_ok=True)
        (export / "filter_definition.txt").write_text(describe_filter(cfg), encoding="utf-8")
        (export / "run_manifest.json").write_text("{}", encoding="utf-8")
        if rows:
            path = export / "SYNTHETIC_input.csv"
            with path.open("w", encoding="cp949" if name == "g_cp949" else "utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            meta = {"keys": keys, "metrics": [x for x in ("n", "n_shop", "n_cust") if x in rows[0]],
                    "population": "SYNTHETIC_meal", "population_kind": "meal", "zero_policy": "mask",
                    "time_only": True, "night_bucket_applied": name == "b_safe_night"}
            if name != "e_no_meta":
                path.with_suffix(".meta.json").write_text(json.dumps(meta), encoding="utf-8")
            if name == "g_bad_csv":
                path.write_text("g,n,status\nx,5,published,EXTRA\n", encoding="utf-8")
        command = [sys.executable, str(ROOT / "analysis/visit2/export_check.py"), "--config", str(config), "--run", str(run)]
        if name == "reference":
            command.append("--reference-only")
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=env)
        report = (run / "internal/export_check_report.txt").read_text(encoding="utf-8")
        (run / "SYNTHETIC_console.txt").write_text(process.stdout + process.stderr, encoding="utf-8")
        assert process.returncode == exit_code, (name, process.returncode, process.stdout, process.stderr, report)
        if check:
            assert check + " FAIL" in report, (name, report)
        if name == "reference":
            assert "FAIL=0" in report and report.count("KNOWN export_0911_week_hour") == 10
            assert report.count("range=[1, 2]") == 10
        for private in ("SYN_ID_123", "SYN_ID_456"):
            assert private not in report + process.stdout + process.stderr
        results.append({"case": name, "expected_exit": exit_code, "actual_exit": process.returncode, "check": check, "pass": True})
    (base / "SYNTHETIC_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("SYNTHETIC stage1 CLI: %d scenarios PASS; no raw ID strings in report/console" % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
