"""Run artifacts and the only permitted path to export tables."""
import hashlib
import json
import platform
import re
import subprocess
import uuid
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .filters import describe_filter
from .suppress import exposure_ranges, frame_digest
from .totals import known_totals_for, reference_totals


def _json_value(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError("JSON으로 저장할 수 없는 값")


def write_json(path, data):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=_json_value, allow_nan=False), encoding="utf-8")
    temp.replace(path)


class RunContext:
    def __init__(self, cfg):
        self.cfg = cfg
        label = cfg["run_label"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", label):
            raise ValueError("run_label은 영문·숫자·밑줄·하이픈만 허용합니다")
        self.started = datetime.now().isoformat()
        self.run_id = label + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.root = Path(cfg["paths"]["out_root"]) / self.run_id
        if self.root.exists():
            self.run_id += "_" + uuid.uuid4().hex[:8]
            self.root = Path(cfg["paths"]["out_root"]) / self.run_id
        self.export = self.root / "export"
        self.internal = self.root / "internal"
        self.export.mkdir(parents=True)
        self.internal.mkdir()
        self.totals = []
        self._reference_totals = None
        self.modules = []
        self.exports = []
        self.manual_actions = []
        (self.export / "filter_definition.txt").write_text(describe_filter(cfg), encoding="utf-8")

    def _name(self, name):
        if not name or Path(name).name != name or "/" in name or "\\" in name or ":" in name or name in (".", ".."):
            raise ValueError("출력 파일명에는 경로를 사용할 수 없습니다")
        return name

    def write_internal(self, df_or_text, name):
        path = self.internal / self._name(name)
        if isinstance(df_or_text, pd.DataFrame):
            df_or_text.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            path.write_text(str(df_or_text), encoding="utf-8")
        return path

    def known_totals(self, meta):
        """Exact same-population prior and reference n totals for suppress().

        Call suppress(..., known_totals=ctx.known_totals(meta)) before export.
        Time-key conversion is deliberately unsupported in this common layer.
        """
        if self._reference_totals is None:
            self._reference_totals = reference_totals(self.cfg)
        references = []
        for entry in self._reference_totals:
            copied = dict(entry)
            if entry["population"] == "0911_unknown" and meta.get("population_kind") in ("meal", "mixed"):
                copied["population"] = meta["population"]
                copied["fixed_keys"] = dict(entry.get("fixed_keys", {}), G="meal")
            references.append(copied)
        return known_totals_for(meta, self.totals + references)

    def _check_existing_totals(self, df, meta, report):
        if "n" not in df:
            return
        lo = 0 if report["zero_policy"] == "mask" else 1
        hi = report["thresholds"]["n_min"] - 1
        for (keys, values), total in self.known_totals(meta).items():
            selected = pd.Series(True, index=df.index)
            for key, value in zip(keys, values):
                selected &= df[key].eq(value).fillna(False)
            part = df.loc[selected]
            if part.status.eq("banded").any():
                raise ValueError("기공개 합계와 banded 행은 함께 노출 점검할 수 없습니다")
            visible = part.status.isin(["published", "zero"])
            numeric = pd.to_numeric(part.loc[visible, "n"], errors="coerce")
            if numeric.isna().any():
                raise ValueError("공개 n이 숫자가 아닙니다")
            hidden_count = int(part.status.eq("suppressed").sum())
            try:
                ranges = exposure_ranges(int(total - numeric.sum()), hidden_count, lo, hi)
            except ValueError as exc:
                raise ValueError("기공개 합계와 새 표가 양립하지 않습니다") from exc
            if any(interval != (lo, hi) for interval in ranges):
                raise ValueError("기공개 합계로 억제 칸 노출: export 거부")

    def write_export(self, df, name, report, meta):
        name = self._name(name)
        if name.endswith(".csv"):
            name = name[:-4]
        if "status" not in df:
            raise ValueError("status 열 없음: suppress 통과가 필요합니다")
        if not isinstance(report, dict) or "unresolved" not in report or report["unresolved"]:
            raise ValueError("unresolved 노출: export 거부")
        if report.get("frame_digest") != frame_digest(df):
            raise ValueError("suppress 결과가 아니거나 점검 뒤 표가 바뀌었습니다")
        for field in ("population", "keys", "metrics", "time_only", "zero_policy", "night_bucket_applied"):
            if field not in meta:
                raise ValueError("메타 필수 항목 누락: " + field)
        if meta["zero_policy"] != report["zero_policy"] or meta["keys"] != report["key_cols"]:
            raise ValueError("메타와 억제 점검 조건 불일치")
        allowed = {"published", "suppressed", "banded"}
        if meta["zero_policy"] == "show":
            allowed.add("zero")
        if not df.status.isin(allowed).all():
            raise ValueError("허용하지 않는 status 값")
        if any(col not in df for col in meta["keys"] + meta["metrics"]):
            raise ValueError("메타에 등록된 열이 표에 없습니다")
        hidden = df.status.eq("suppressed")
        public_values = [col for col in df if col not in meta["keys"] and col != "status"]
        if df.loc[hidden, public_values].notna().any().any():
            raise ValueError("억제 칸에 값이 남아 있습니다")
        if report.get("n_col") is None and "n" in df and pd.to_numeric(df.n, errors="coerce").notna().any():
            raise ValueError("n_col=None 표에 숫자 n을 반출할 수 없습니다")
        forbidden = {"shop_id", "cust_id", "p99", "max", "maximum", "p_value", "pvalue"}
        if any(str(col).lower() in forbidden for col in df):
            raise ValueError("반출 금지 열")
        for pattern in self.cfg["id_patterns"]:
            if pattern.startswith("<"):
                continue  # export_check is responsible for the final configured-ID gate.
            regex = re.compile(pattern)
            if any(regex.search(str(x)) for x in list(df.columns) + df.astype(str).values.ravel().tolist()):
                raise ValueError("가명 ID 형식 검출: 반출 거부")
        keys = meta["keys"]
        self._check_existing_totals(df, meta, report)
        region = any(k in ("dong", "gungu", "dong_id") for k in keys)
        exception = meta["time_only"] is True and self.cfg["export"]["time_only_axes_exception"] is True and not region
        limit = self.cfg["export"]["max_axes"]
        pieces = []
        if len(keys) > limit and not exception:
            axis = self.cfg["export"]["split_axis"]
            if axis not in keys or len(keys) - 1 > limit:
                raise ValueError("split_axis로 3축 이하로 분할할 수 없습니다")
            for index, (value, part) in enumerate(df.groupby(axis, dropna=False, sort=False)):
                details = dict(meta)
                details["keys"] = [k for k in keys if k != axis]
                details["fixed_keys"] = dict(meta.get("fixed_keys", {}))
                details["fixed_keys"][axis] = value
                pieces.append((name + "__" + axis + "-" + str(index), part.drop(columns=[axis]), details))
        else:
            pieces.append((name, df.copy(), dict(meta)))
        paths = []
        for stem, part, details in pieces:
            path = self.export / (stem + ".csv")
            if path.exists() or path.with_suffix(".meta.json").exists():
                raise ValueError("같은 실행의 기존 반출물을 덮어쓸 수 없습니다")
            for col in details["metrics"]:
                numeric = pd.to_numeric(part[col], errors="coerce")
                if not (part[col].notna() & numeric.isna()).any() and (numeric.dropna() % 1 == 0).all():
                    part[col] = numeric.astype("Int64")
            details["suppressed_cells"] = int(part.status.eq("suppressed").sum())
            part.to_csv(path, index=False, encoding="utf-8-sig")
            write_json(path.with_suffix(".meta.json"), details)
            self._register(part, details, path.name)
            paths.append(path)
        write_json(self.internal / "published_totals.json", self.totals)
        self.exports.extend(str(p.name) for p in paths)
        return paths

    def _register(self, df, meta, source):
        # Only n is additive. An incompletely public group has no public total.
        if "n" not in meta["metrics"]:
            return
        keys = meta["keys"]
        for width in range(len(keys) + 1):
            for subset in combinations(keys, width):
                if not subset:
                    groups = [((), df)]
                else:
                    grouper = subset[0] if len(subset) == 1 else list(subset)
                    groups = df.groupby(grouper, dropna=False, sort=False)
                for values, group in groups:
                    if subset and len(subset) == 1:
                        values = (values,)
                    if not group.status.isin(["published", "zero"]).all():
                        continue
                    numeric = pd.to_numeric(group.n, errors="coerce")
                    if numeric.isna().any():
                        continue
                    self.totals.append({"population": meta["population"], "metric": "n",
                                        "keys": list(subset), "values": list(values),
                                        "fixed_keys": meta.get("fixed_keys", {}),
                                        "total": int(numeric.sum()), "source": source})

    def finish(self, module, extra):
        record = {"module": module, "started": self.started, "ended": datetime.now().isoformat(), "extra": extra}
        self.modules.append(record)
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                    timeout=5, check=True).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            commit = "unknown"
        inputs = []
        for key in ("pay", "shop"):
            path = Path(self.cfg["paths"][key])
            if path.exists():
                stat = path.stat()
                inputs.append({"kind": key, "path": str(path), "size": stat.st_size, "mtime": stat.st_mtime})
        data = {"run_id": self.run_id, "modules": self.modules, "inputs": inputs,
                "config": {k: v for k, v in self.cfg.items() if not k.startswith("_")},
                "filter_definition": describe_filter(self.cfg), "git_commit": commit,
                "python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__,
                "exports": self.exports, "manual_actions": getattr(self, "manual_actions", [])}
        write_json(self.export / "run_manifest.json", data)


def start_run(cfg):
    return RunContext(cfg)
