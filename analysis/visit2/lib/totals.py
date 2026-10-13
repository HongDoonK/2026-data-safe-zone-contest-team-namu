"""Exact published-total constraints for later tables.

No time-axis projection is performed here. A total is usable only when its
population and every fixed/key dimension match the target exactly.
"""
import json
from itertools import combinations
from pathlib import Path

import pandas as pd
from .timeparse import DOW_LABELS, hour_to_bucket, project_time_key


def _reference_frames(frame, info, cfg):
    """Static folds of one old table; no cross-table propagation."""
    keys = list(info["keys"])
    if "ym" in keys:
        frame["ym"] = frame.ym.astype(str).str.replace("-", "", regex=False).astype(int)
    if set(keys) == {"dow", "hour"} and info.get("zero_policy") == "absent_row":
        index = pd.MultiIndex.from_product([DOW_LABELS, range(24)], names=["dow", "hour"])
        frame = frame.set_index(["dow", "hour"]).reindex(index, fill_value=0).reset_index()
    yield frame, keys
    if "hour" in keys:
        for target in ("hour3", "hour_bucket"):
            if target == "hour_bucket" and "export" not in cfg:
                continue
            transformed = frame.copy()
            transformed[target] = transformed.hour.map(lambda h: int(h) // 3 if target == "hour3" else hour_to_bucket(h, cfg["export"]["night_bucket"]))
            new_keys = [target if key == "hour" else key for key in keys]
            # min_count preserves a hidden constituent as a hidden coarse cell.
            grouped = transformed.groupby(new_keys, dropna=False).n.agg(lambda values: values.sum() if values.notna().all() else float("nan")).reset_index()
            yield grouped, new_keys
    if "ym" in keys and cfg.get("regime", {}).get("mode") == "month":
        transformed = frame.copy()
        transformed["R"] = transformed.ym.map(lambda ym: project_time_key("ym", "R", ym, cfg))
        new_keys = ["R" if key == "ym" else key for key in keys]
        grouped = transformed.groupby(new_keys, dropna=False).n.agg(lambda values: values.sum() if values.notna().all() else float("nan")).reset_index()
        yield grouped, new_keys


def _complete_entries(frame, keys, info, name):
    entries = []
    for width in range(len(keys) + 1):
        for subset in combinations(keys, width):
            groups = frame.groupby(subset[0] if width == 1 else list(subset), dropna=False, sort=False) if subset else [((), frame)]
            for values, part in groups:
                if part.n.isna().any():
                    continue
                values = (values,) if width == 1 else () if width == 0 else values
                total = part.n.sum()
                if total < 0 or total % 1:
                    raise ValueError("참조 n이 음수 또는 비정수")
                entries.append({"population": info["population"], "keys": list(subset), "values": list(values),
                                "fixed_keys": info.get("fixed_keys", {}), "total": int(total), "metric": "n", "source": name})
    return entries


def reference_totals(cfg):
    """Read complete n groups from configured reference JSON tables.

    Reference paths are relative to the visit2 directory containing config/.
    A null reference is unavailable; a configured but unreadable one fails.
    """
    config_path = cfg.get("_config_path")
    base = Path(config_path).resolve().parent if config_path else Path(__file__).resolve().parents[1]
    if base.name == "config":
        base = base.parent
    refs = cfg.get("reference_exports", {})
    if not refs or not any(relative is not None for relative in refs.values()):
        return []
    entries = []
    for name, relative in refs.items():
        if relative is None:
            continue
        ref_path = base / relative
        metadata = json.loads(ref_path.with_name("reference_meta.json").read_text(encoding="utf-8-sig"))
        info = dict(metadata[name])
        if name in ("export_0911_month", "export_0911_week_hour"):
            info["fixed_keys"] = dict(info.get("fixed_keys", {}), G="meal")
        if "n" not in info["metrics"]:
            continue
        rows = json.loads((base / relative).read_text(encoding="utf-8-sig"))
        frame = pd.DataFrame(rows)
        keys = list(info["keys"])
        if any(key not in frame for key in keys) or "n" not in frame:
            raise ValueError("참조 표의 키 또는 n 열 누락: " + name)
        frame["n"] = pd.to_numeric(frame["n"], errors="coerce")
        for transformed, transformed_keys in _reference_frames(frame, info, cfg):
            entries.extend(_complete_entries(transformed, transformed_keys, info, name))
    return entries


def known_totals_for(meta, entries):
    """Map exact same-population totals to suppress's (keys, values) API.

    Prior dimensions must exist as target keys or target fixed keys. Every
    target fixed key must also have been represented in the prior total.
    """
    result = {}
    target_keys = list(meta["keys"])
    target_fixed = meta.get("fixed_keys", {})
    for entry in entries:
        if entry.get("metric") != "n" or entry.get("population") != meta["population"]:
            continue
        old_keys = entry["keys"]
        old_values = entry["values"]
        old_fixed = entry.get("fixed_keys", {})
        if len(old_keys) != len(old_values):
            raise ValueError("공개 합계의 키와 값 길이가 다릅니다")
        dimensions = dict(zip(old_keys, old_values))
        if any(key in dimensions and dimensions[key] != value for key, value in old_fixed.items()):
            raise ValueError("공개 합계의 고정 키가 모순됩니다")
        dimensions.update(old_fixed)
        if any(key not in dimensions or dimensions[key] != value for key, value in target_fixed.items()):
            continue
        if any(key not in target_keys and key not in target_fixed for key in dimensions):
            continue  # In particular, do not guess ym -> R or hour -> hour3.
        group = tuple(key for key in target_keys if key in dimensions)
        values = tuple(dimensions[key] for key in group)
        pair = (group, values)
        total = entry["total"]
        if pair in result and result[pair] != total:
            raise ValueError("기공개 합계가 서로 모순됩니다")
        result[pair] = total
    return result
