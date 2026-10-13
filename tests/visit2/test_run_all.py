"""SYNTHETIC fail-fast orchestration contracts."""
import json
from pathlib import Path
from run_all import run_steps
from lib.pipeline import open_context
from test_module_cli import _fixture


def test_failed_middle_step_stops_later_steps(case_dir):
    cfg, config = _fixture(case_dir)
    ctx = open_context(cfg)
    ctx.finish("init", {})
    calls = []
    def execute(command):
        calls.append(Path(command[1]).stem)
        return {"exit_code": 7 if len(calls) == 2 else 0, "seconds": 0.01, "peak_resident_bytes": 10}
    result = run_steps(config, ctx.root, ["SYNTHETIC_a.py", "SYNTHETIC_b.py", "SYNTHETIC_c.py"], execute)
    assert result == 7 and calls == ["SYNTHETIC_a", "SYNTHETIC_b"]
    evidence = json.loads((ctx.internal / "run_all_timing.json").read_text(encoding="utf-8"))
    assert evidence["failed_step"] == "SYNTHETIC_b.py"


def test_actual_cli_stops_before_m4_on_regime_error(case_dir):
    from test_module_cli import _run
    cfg, config = _fixture(case_dir)
    cfg["regime"]["mode"] = "date_ranges"
    cfg["regime"]["date_ranges"] = [{"start": "20230601", "end": "20230630", "label": label}
                                     for label in ["SYN_A", "SYN_B"]]
    config.write_text(json.dumps(cfg), encoding="utf-8")
    process, run = _run("run_all.py", config)
    assert process.returncode == 1
    timing = json.loads((run / "internal/run_all_timing.json").read_text(encoding="utf-8"))
    assert timing["failed_step"] == "30_m2_compare.py"
    assert "50_m4_space.py" not in [row["module"] for row in timing["steps"]]
    assert not list((run / "export").glob("m4_*.csv"))


def test_small_end_to_end_all_modules_and_export_check(case_dir):
    from test_module_cli import _run
    cfg, config = _fixture(case_dir)
    process, run = _run("run_all.py", config)
    assert process.returncode == 0, process.stderr
    manifest = json.loads((run / "export/run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_all"]["exit_code"] == 0
    assert [row["module"] for row in manifest["run_all"]["steps"]] == [
        "00_headers.py", "20_m1_paygbn.py", "10_m0_reproduce.py", "40_m3_shop.py",
        "30_m2_compare.py", "50_m4_space.py", "export_check.py"]
    assert "FAIL=0" in (run / "internal/export_check_report.txt").read_text(encoding="utf-8")
