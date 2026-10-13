"""Literal cells in one namespace; only paths/chunksize are substituted."""
import argparse
import contextlib
import ctypes
import gc
import io
import json
import os
import threading
import time
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from extract_cells import HERE, ORDER, ROOT

OUT = ROOT / "synthetic/visit3/out_SYNTHETIC"
DEPENDENCIES = {"S1": [], "P1": ["S1"], "P1b": ["P1"], "P2": ["P1"], "P3": ["S1"],
                "M1": ["S1"], "M2": ["M1"], "M3": ["M1"], "M4": ["M2"],
                "M5": ["M1", "M3", "M4"], "M6": ["M1", "M2", "M3"],
                "A1": ["S1"], "A2": ["A1"], "A3": ["A1"], "A4": ["A1"]}


def selected(cell):
    needed = set()
    def visit(c):
        for dep in DEPENDENCIES[c]:
            visit(dep)
        needed.add(c)
    visit(cell)
    return [c for c in ORDER if c in needed]


def canonical(value):
    if isinstance(value, pd.DataFrame):
        value = value.sort_index()
        return {"index": [canonical(x) for x in value.index.tolist()],
                "columns": [canonical(x) for x in value.columns.tolist()],
                "values": [[canonical(x) for x in row] for row in value.to_numpy().tolist()]}
    if isinstance(value, pd.Series):
        return canonical(value.to_frame())
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted(canonical(v) for v in value)
    if isinstance(value, np.generic):
        return canonical(value.item())
    if isinstance(value, float):
        if np.isnan(value):
            return None
        if np.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return round(value, 10)
    return value


def observe(cell, ns):
    if cell == "S1":
        return {"pay_columns": pd.read_csv(ns["PAY"], nrows=0).columns.tolist(),
                "shop_columns": pd.read_csv(ns["SHOP"], nrows=0).columns.tolist()}
    if cell == "P1":
        return {"monthly": ns["a"], "codes": ns["a"].groupby(level=0).sum(),
                "pre": ns["pre"].pivot(index="ym", columns=ns["C_GBN"], values="n_disc").fillna(0)}
    if cell == "P1b":
        return {"monthly_meal": ns["a"].loc["아동급식카드"]}
    if cell == "P2":
        b = ns["b"]
        return {"pivot": b.pivot(index="ym", columns=ns["C_GBN"], values="n").fillna(0),
                "year_vac": b.groupby([ns["C_GBN"], "yr", "vac"]).n.sum().unstack()}
    if cell == "P3":
        return {"overlap": ns["r"].set_index("gbn").sort_index()}
    if cell == "M1":
        return {"reg": ns["reg"], "empty_dong": int((ns["sh"].DONG_NM == "").sum())}
    if cell == "M2":
        m = ns["m"]
        return {"count": len(m), "missing": int(m.dong.isna().sum()), "dongs": m.dong.nunique(),
                "regimes": m.R.value_counts().sort_index(),
                "rows": m.groupby([ns["C_SHOP"], ns["C_CUST"], ns["C_TIME"], "R", "dong"], dropna=False).size()}
    if cell == "M3":
        return {"gp": ns["gp"].sort_index(), "g": ns["g"].sort_index()}
    if cell == "M4":
        return {"t": ns["t"], "tt": ns["tt"], "bad": ns["bad"], "k": ns["k"],
                "regime_order": ns["t"].groupby(level=1).n.sum().index.tolist()}
    if cell == "M5":
        return {"tot": ns["tot"], "bad2": ns["bad2"]}
    if cell == "M6":
        return {"selected_ids": sorted(ns["sel"].index.tolist()), "e2": ns["e2"], "live": len(ns["live"]),
                "cross": ns["sel"].groupby(["STORE_STATUS", "SERVICE_CLOSED"]).size()}
    if cell == "A1":
        return {"count": len(ns["a"]), "describe": ns["a"][ns["NUM"]].describe().round(0)}
    if cell == "A2":
        a, disc, tot, app = ns["a"], ns["C_DISC"], ns["C_TOT"], ns["C_APP"]
        return {"ratios": [round((a[disc] > 0).mean(), 3), round((a[tot]-a[app]-a[disc]).abs().le(1).mean(), 3),
                           round((a[tot]-a[app]).abs().le(1).mean(), 3), round((a[tot]-a[disc]).abs().le(1).mean(), 3)],
                "disc_q": a[disc].quantile([.1, .25, .5, .75, .9, .99]),
                "tot_q": a[tot].quantile([.1, .25, .5, .75, .9, .99]),
                "disc_bins": a.groupby(a[disc] // 500 * 500).size().head(20)}
    if cell == "A3":
        return {"hm": ns["hm"], "hg": ns["hg"], "e": ns["e"], "bad": ns["bad"]}
    if cell == "A4":
        return {"top": ns["top"].set_index("ym")[["bin", "n"]]}
    return {}


def memory_bytes():
    if os.name == "nt":
        class Counters(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [
                (x, ctypes.c_size_t) for x in ["PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                                             "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                                             "PagefileUsage", "PeakPagefileUsage"]]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        handle = kernel.GetCurrentProcess()
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return counters.WorkingSetSize, counters.PeakWorkingSetSize
    import resource
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    return rss, rss


def execute(cell, ns, pay, shop, outdir, chunksize=1000000, variant="original", source_override=None, snapshot=True):
    outdir = Path(outdir).resolve()
    outdir.relative_to(OUT.resolve())
    outdir.mkdir(parents=True, exist_ok=True)
    source_path = HERE / "cells" / (cell + ".py")
    candidate = HERE / ("cells_" + variant) / (cell + ".py")
    if variant != "original" and candidate.is_file():
        source_path = candidate
    source = source_override if source_override is not None else source_path.read_bytes().decode("utf-8")
    source = source.replace('r"결제파일경로.csv"', repr(str(Path(pay).resolve())))
    source = source.replace('r"가맹점파일경로.csv"', repr(str(Path(shop).resolve())))
    source = source.replace("chunksize=1000000", "chunksize=%d" % chunksize)
    stdout = io.StringIO()
    peak = [memory_bytes()[0]]
    stop = threading.Event()
    def sample():
        while not stop.wait(.01):
            peak[0] = max(peak[0], memory_bytes()[0])
    thread = threading.Thread(target=sample, daemon=True)
    old_cwd = Path.cwd()
    os.chdir(str(outdir))
    start = time.perf_counter()
    thread.start()
    exception = None
    try:
        with warnings.catch_warnings(record=True) as captured, contextlib.redirect_stdout(stdout):
            warnings.simplefilter("always")
            try:
                exec(compile(source, str(source_path), "exec"), ns)
            except Exception:
                exception = traceback.format_exc()
    finally:
        elapsed = time.perf_counter() - start
        stop.set()
        thread.join()
        peak[0] = max(peak[0], memory_bytes()[0])
        os.chdir(str(old_cwd))
    exports = []
    for path in outdir.glob("EXPORT_*.csv"):
        if "SYNTHETIC" not in path.name:
            destination = path.with_name(path.stem + "_SYNTHETIC.csv")
            path.replace(destination)
            exports.append(destination.name)
    record = {"label": "SYNTHETIC", "cell": cell, "seconds": elapsed,
              "peak_rss_bytes_sampled": peak[0], "process_peak_rss_bytes": memory_bytes()[1],
              "stdout": stdout.getvalue(), "exception": exception,
              "warnings": [{"category": w.category.__name__, "line": w.lineno,
                            "file": w.filename, "message": str(w.message)} for w in captured],
              "exports": exports}
    if not exception and snapshot:
        record["snapshot"] = canonical(observe(cell, ns))
    (outdir / ("SYNTHETIC_%s_stdout.txt" % cell)).write_text("SYNTHETIC\n" + stdout.getvalue(), encoding="utf-8")
    (outdir / ("SYNTHETIC_%s_record.json" % cell)).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def run(pay, shop, tag="small_original", chunksize=1000000, cells=None, variant="original", snapshot=True):
    ns, records = {}, []
    outdir = OUT / ("SYNTHETIC_" + tag)
    for cell in cells or ORDER:
        record = execute(cell, ns, pay, shop, outdir, chunksize, variant, snapshot=snapshot)
        records.append(record)
        if record["exception"]:
            break
    (outdir / "SYNTHETIC_run.json").write_text(json.dumps({"label": "SYNTHETIC", "records": records,
                        "chunksize": chunksize, "pay": str(pay), "shop": str(shop)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return ns, records, outdir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pay", type=Path, default=ROOT / "synthetic/visit3/data_SYNTHETIC/SYNTHETIC_pay_small.csv")
    parser.add_argument("--shop", type=Path, default=ROOT / "synthetic/visit3/data_SYNTHETIC/SYNTHETIC_shop.csv")
    parser.add_argument("--tag", default="manual")
    parser.add_argument("--chunksize", type=int, default=1000000)
    parser.add_argument("--cell", choices=ORDER)
    parser.add_argument("--variant", choices=["original", "proposed", "optional"], default="original")
    parser.add_argument("--no-snapshot", action="store_true")
    args = parser.parse_args()
    _, records, folder = run(args.pay, args.shop, args.tag, args.chunksize,
                             selected(args.cell) if args.cell else None, args.variant, not args.no_snapshot)
    print("SYNTHETIC logs: " + str(folder))
    for record in records:
        print(record["cell"], "ERROR" if record["exception"] else "OK", round(record["seconds"], 3), "seconds")
    if any(r["exception"] for r in records):
        raise SystemExit(1)
