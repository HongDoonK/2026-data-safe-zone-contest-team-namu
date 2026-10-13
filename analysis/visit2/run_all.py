"""Sequential offline run; every nonzero module exit stops the chain."""
import argparse
import json
import sys
import time
from pathlib import Path

from lib.config import load_config
from lib.manifest import write_json
from lib.pipeline import open_context
from lib.runtime import execute

HERE = Path(__file__).resolve().parent
STEPS = ["00_headers.py", "20_m1_paygbn.py", "10_m0_reproduce.py", "40_m3_shop.py",
         "30_m2_compare.py", "50_m4_space.py", "export_check.py"]


def run_steps(config, run, steps=None, executor=execute):
    root = Path(run)
    started = time.perf_counter()
    records = []
    failed = None
    exit_code = 0
    for script in steps or STEPS:
        print("[run_all] 실행: " + script, flush=True)
        command = [sys.executable, str(HERE / script), "--config", str(config), "--run", str(root)]
        record = dict(executor(command), module=script)
        records.append(record)
        exit_code = record["exit_code"]
        if not exit_code and script == "10_m0_reproduce.py":
            manifest = json.loads((root / "export/run_manifest.json").read_text(encoding="utf-8"))
            selected = next((entry["extra"].get("selected_mode") for entry in reversed(manifest["modules"])
                             if entry["module"] == "M0"), None)
            if selected and selected != manifest["config"]["status_filter"]["mode"]:
                print("M0 재현 상태 필터와 설정이 다릅니다. 사람이 설정을 확인한 뒤 새 run으로 실행하세요", flush=True)
                exit_code = record["exit_code"] = 2
        timing = {"steps": records, "failed_step": script if exit_code else None,
                  "seconds": round(time.perf_counter() - started, 3)}
        write_json(root / "internal/run_all_timing.json", timing)
        if exit_code:
            failed = script
            print("[run_all] 중단: %s exit=%s; 이후 모듈은 실행하지 않았습니다" % (script, exit_code), flush=True)
            break
    manifest_path = root / "export/run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["run_all"] = {"failed_step": failed, "exit_code": exit_code,
                           "seconds": round(time.perf_counter() - started, 3), "steps": records}
    write_json(manifest_path, manifest)
    print("[run_all] exit=%d; run=%s" % (exit_code, root), flush=True)
    return exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(description="V2 전체 순차 실행")
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    try:
        cfg = load_config(args.config)
        ctx = open_context(cfg)
        ctx.finish("run_all_init", {})
        return run_steps(Path(args.config).resolve(), ctx.root.resolve())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("전체 실행 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
