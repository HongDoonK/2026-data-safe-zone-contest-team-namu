"""Shared offline module runner and publication boundary."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .distinct import CountAccumulator, DistinctAccumulator
from .io import detect_encoding, iter_chunks, read_header
from .manifest import RunContext, write_json
from .suppress import suppress
from .timeparse import add_time_fields


class Aggregate:
    def __init__(self, keys):
        self.keys = list(keys)
        self.count = CountAccumulator(keys)
        self.shop = DistinctAccumulator(keys)
        self.cust = DistinctAccumulator(keys)

    def update(self, frame):
        self.count.update(frame)
        self.shop.update(frame, "shop_id")
        self.cust.update(frame, "cust_id")

    def finalize(self):
        result = self.count.finalize()
        for accumulator, name in ((self.shop, "n_shop"), (self.cust, "n_cust")):
            part = accumulator.finalize().rename(columns={"nunique": name})
            if self.keys:
                result = result.merge(part, on=self.keys, how="left")
            else:
                result[name] = int(part[name].iloc[0]) if len(part) else 0
            result[name] = result[name].fillna(0).astype("int64")
        return result


def read_pay(cfg, usecols=None):
    mapping = cfg["columns"][cfg["columns"]["active"]]["pay"]
    columns = usecols or ["shop_id", "cust_id", "pay_gbn", "card_pay_gbn", "app_time"]
    encoding = detect_encoding(cfg["paths"]["pay"], cfg["encoding_candidates"])
    print("실제 결제 헤더: " + str(read_header(cfg["paths"]["pay"], encoding)))
    for frame in iter_chunks(cfg["paths"]["pay"], columns, mapping, encoding, cfg["chunksize"]):
        yield add_time_fields(frame)


def open_context(cfg, run_path=None):
    if run_path is None:
        ctx = RunContext(cfg)
    else:
        root = Path(run_path)
        manifest = json.loads((root / "export/run_manifest.json").read_text(encoding="utf-8"))
        expected = {k: v for k, v in cfg.items() if not k.startswith("_")}
        if manifest["config"] != expected:
            raise ValueError("이어 실행할 run과 설정이 다릅니다. 새 run을 사용하세요")
        ctx = RunContext.__new__(RunContext)
        ctx.cfg, ctx.root, ctx.run_id = cfg, root, manifest["run_id"]
        ctx.export, ctx.internal = root / "export", root / "internal"
        ctx.started = datetime.now().isoformat()
        ctx.modules, ctx.exports = manifest["modules"], manifest["exports"]
        ctx.manual_actions = manifest.get("manual_actions", [])
        totals = ctx.internal / "published_totals.json"
        ctx.totals = json.loads(totals.read_text(encoding="utf-8")) if totals.exists() else []
        ctx._reference_totals = None
    ctx.rejected_tables = []
    return ctx


def population(cfg, kind, subset=None):
    fields = {k: cfg[k] for k in ("meal_pay_values", "status_filter", "period")}
    fields.update(kind="payments" if kind in ("meal", "general", "mixed") else kind, subset=subset)
    return hashlib.sha256(json.dumps(fields, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def emit(ctx, frame, name, keys, kind="meal", zero_policy=None, margins=None,
         n_col="n", shop_col="n_shop", cust_col="n_cust", subset=None, fixed_keys=None, thresholds=None):
    if (ctx.export / (name + ".csv")).exists():
        raise ValueError("기존 표를 덮어쓸 수 없습니다: " + name)
    policy = zero_policy or ctx.cfg["suppression"]["zero_policy"]
    meta = {"keys": list(keys), "metrics": [c for c in frame if c not in keys and c != "status"],
            "population": population(ctx.cfg, kind, subset), "population_kind": kind,
            "zero_policy": policy, "time_only": not bool(set(keys) & {"dong", "gungu"}),
            "night_bucket_applied": "hour_bucket" in keys,
            "fixed_keys": dict(fixed_keys or {}), "coverage_complete": True}
    if kind in ("meal", "general") and "G" not in keys:
        meta["fixed_keys"]["G"] = kind
    options = dict(ctx.cfg["suppression"])
    options["zero_policy"] = policy
    options.update(thresholds or {})
    out, report = suppress(frame, keys, n_col=n_col, shop_col=shop_col, cust_col=cust_col,
                           margin_groups=margins, known_totals=ctx.known_totals(meta), **options)
    write_json(ctx.internal / (name + "_suppression.json"), report)
    if report["unresolved"]:
        ctx.rejected_tables.append(name)
        print("반출 거부(unresolved): " + name)
        return None
    ctx.write_export(out, name, report, meta)
    return out
