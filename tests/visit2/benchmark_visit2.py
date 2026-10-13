"""SYNTHETIC subprocess timing / peak resident memory, using stdlib only."""
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def peak_memory(process):
    if os.name != "nt":
        return None
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage",
                "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]

    data = Counters()
    data.cb = ctypes.sizeof(data)
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    get_info.restype = wintypes.BOOL
    if get_info(wintypes.HANDLE(int(process._handle)), ctypes.byref(data), data.cb):
        return int(data.PeakWorkingSetSize)
    return None


def benchmark(command, destination):
    destination = Path(destination).resolve()
    fixture_root = Path(__file__).resolve().parent / "fixtures"
    if fixture_root not in destination.parents or not destination.name.startswith("SYNTHETIC"):
        raise ValueError("benchmark logs must use a SYNTHETIC name inside fixtures")
    destination.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    started = time.perf_counter()
    maximum = None
    with destination.with_suffix(".stdout.txt").open("w", encoding="utf-8") as out:
        with destination.with_suffix(".stderr.txt").open("w", encoding="utf-8") as err:
            process = subprocess.Popen(command, stdout=out, stderr=err, env=env)
            while True:
                current = peak_memory(process)
                if current is not None:
                    maximum = current if maximum is None else max(maximum, current)
                result = process.poll()
                if result is not None:
                    break
                time.sleep(0.05)
    record = {"label": "SYNTHETIC", "command": command, "exit_code": result,
              "seconds": round(time.perf_counter() - started, 3),
              "peak_resident_bytes": maximum, "over_10_minutes": time.perf_counter() - started > 600}
    destination.with_suffix(".json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a subprocess command is required")
    sys.exit(benchmark(command, args.log))
