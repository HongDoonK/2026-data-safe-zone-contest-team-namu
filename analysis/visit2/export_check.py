"""Stage-A export audit: static guards and pairwise checks against 0911 references.

``check_run`` and ``check_references`` return a dictionary with ``checks``
(``code``, ``status``, ``message``), ``exposures`` (safe cell indexes and
integer bounds), ``fail_count``, ``warn_count``, ``known_count`` and
``report_path``. No actual suppressed count or raw ID is reported.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

from lib.suppress import exposure_ranges
from lib.timeparse import project_time_key


HERE = Path(__file__).resolve().parent
ALLOWED_STATUS = {"published", "suppressed", "banded", "zero"}
REGION_KEYS = {"dong", "gungu", "dong_id", "gungu_id"}
TIME_KEYS = {"hour", "hour3", "hour_bucket"}


def _result():
    return {"checks": [], "exposures": [], "fail_count": 0, "warn_count": 0,
            "known_count": 0, "report_path": None}


def _add(result, code, status, message):
    result["checks"].append({"code": code, "status": status, "message": message})
    if status == "FAIL":
        result["fail_count"] += 1
    elif status == "WARN":
        result["warn_count"] += 1


def _load_cfg(value):
    if isinstance(value, dict):
        cfg = dict(value)
        path = Path(cfg.get("_config_path", HERE / "config/visit2.json"))
    else:
        path = Path(value)
        cfg = json.loads(path.read_text(encoding="utf-8-sig"))
    for section in ("suppression", "export", "reference_exports", "id_patterns"):
        if section not in cfg:
            raise ValueError("설정 필수 항목 누락: " + section)
    if not isinstance(cfg["suppression"], dict) or not isinstance(cfg["export"], dict):
        raise ValueError("suppression/export는 설정 객체여야 합니다")
    for key in ("n_min", "shop_min", "cust_min"):
        if type(cfg["suppression"].get(key)) is not int or cfg["suppression"][key] < 1:
            raise ValueError("억제 기준 설정 오류")
    export = cfg["export"]
    if type(export.get("max_axes")) is not int or export["max_axes"] < 1:
        raise ValueError("export.max_axes는 양의 정수여야 합니다")
    if type(export.get("time_only_axes_exception")) is not bool:
        raise ValueError("축 예외 설정은 불리언이어야 합니다")
    night = export.get("night_bucket")
    if not isinstance(night, dict) or not isinstance(night.get("hours"), list) or not isinstance(night.get("label"), str):
        raise ValueError("심야 구간 설정 오류")
    if any(type(hour) is not int or hour < 0 or hour > 23 for hour in night["hours"]) or not night["label"]:
        raise ValueError("심야 시각/라벨 설정 오류")
    if cfg["reference_exports"] is None:
        cfg["reference_exports"] = {}
        cfg["_references_unavailable"] = True
    if not isinstance(cfg["reference_exports"], dict) or not isinstance(cfg["id_patterns"], list):
        raise ValueError("reference_exports 또는 id_patterns 설정 오류")
    cfg["_config_path"] = str(path)
    return cfg


def _safe(value, patterns):
    text = str(value)
    for pattern in patterns:
        if not isinstance(pattern, str) or pattern.startswith("<"):
            continue
        try:
            text = re.sub(pattern, "[ID_REDACTED]", text)
        except re.error:
            continue
    return text


def _compile_patterns(cfg, result, reference_only):
    if reference_only:
        _add(result, "C2", "N/A", "참조 전용 모드: 신규 표 ID 검사는 해당 없음")
        return []
    items = cfg["id_patterns"]
    if not items or any(not isinstance(x, str) or not x or x.startswith("<") for x in items):
        _add(result, "C2", "FAIL", "id_patterns 설정이 비었거나 자리표시자입니다")
        return []
    try:
        return [re.compile(x) for x in items]
    except re.error:
        _add(result, "C2", "FAIL", "id_patterns 정규식 오류")
        return []


def _read_csv(path):
    """Strict UTF-8 CSV; rows retain strings so IDs are never rounded."""
    last_error = None
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.reader(handle, strict=True)
                header = next(reader)
                if not header or any(not col for col in header) or len(set(header)) != len(header):
                    raise ValueError("빈 열 이름 또는 중복 열 이름")
                rows = []
                for row in reader:
                    if len(row) != len(header):
                        raise ValueError("CSV 열 수 불일치")
                    rows.append(dict(zip(header, row)))
                return header, rows
        except (UnicodeError, csv.Error, ValueError, StopIteration) as exc:
            last_error = exc
    raise ValueError("CSV 형식 또는 UTF-8 인코딩 오류") from last_error


def _int_or_none(raw):
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        raise ValueError("건수가 불리언입니다")
    value = float(raw)
    if not value.is_integer() or value < 0:
        raise ValueError("건수가 음수 또는 비정수입니다")
    return int(value)


def _ref_path(cfg, value):
    path = Path(value)
    if path.is_absolute():
        return path
    # V2-00 config paths are relative to analysis/visit2, not config/.
    base = Path(cfg["_config_path"]).resolve().parent
    if base.name == "config":
        base = base.parent
    return base / path


def _load_references(cfg, result):
    tables = []
    refs = cfg["reference_exports"]
    if cfg.get("_references_unavailable") or not refs:
        _add(result, "C8", "WARN", "참조 자료가 없어 반출 전 수작업 대조가 필요합니다")
        return tables
    for name, relative in refs.items():
        if relative is None:
            _add(result, "C8", "WARN", "참조 자료 없음: 반출 전 수작업 대조 필요")
            continue
        try:
            ref_path = _ref_path(cfg, relative)
            metas = json.loads(ref_path.with_name("reference_meta.json").read_text(encoding="utf-8-sig"))
            records = json.loads(ref_path.read_text(encoding="utf-8-sig"))
            meta = metas[name]
            if not isinstance(records, list) or not records or not isinstance(meta["keys"], list):
                raise ValueError("참조 형식 오류")
            _range(meta, cfg)
            rows = []
            for record in records:
                row = dict(record)
                row["n"] = _int_or_none(row.get("n"))
                row["status"] = "suppressed" if row["n"] is None else "published"
                rows.append(row)
            tables.append({"name": name, "keys": meta["keys"], "meta": meta,
                           "rows": rows, "reference": True})
        except (OSError, UnicodeError, ValueError, KeyError, TypeError):
            _add(result, "C8", "FAIL", "참조 자료 또는 메타 형식 오류")
    return tables


def _range(meta, cfg):
    policy = meta.get("zero_policy")
    if policy == "mask":
        return 0, cfg["suppression"]["n_min"] - 1
    if policy in ("show", "absent_row"):
        return 1, cfg["suppression"]["n_min"] - 1
    raise ValueError("zero_policy 메타 오류")


def _band_range(raw):
    value = str(raw).strip()
    lower = re.fullmatch(r"<([0-9]+)", value)
    if lower:
        return (0, int(lower.group(1)) - 1)
    span = re.fullmatch(r"([0-9]+)-([0-9]+)", value)
    if span and int(span.group(1)) <= int(span.group(2)):
        return (int(span.group(1)), int(span.group(2)))
    return None


def _row_interval(row, meta, cfg):
    if row["status"] == "banded":
        return row.get("_band_range")
    if row["n"] is None:
        return _range(meta, cfg)
    return row["n"], row["n"]


def _population_match(old, new):
    om = old["meta"]
    nm = new["meta"]
    okind = om.get("population_kind")
    nkind = nm.get("population_kind")
    if om.get("population") == "0911_unknown":
        if nkind in ("general", "shop", "diagnostic"):
            return False
        if "G" in nm.get("keys", []):
            return None  # row-level G split needs an explicit meal slice
        fixed_g = str(nm.get("fixed_keys", {}).get("G", "")).lower()
        if fixed_g and fixed_g not in ("meal", "급식", "child_meal"):
            return False if fixed_g in ("general", "일반") else None
        return True  # unknown kind may be meal; compare conservatively
    if okind and nkind and okind != nkind and "mixed" not in (okind, nkind):
        return False
    if om.get("population") != nm.get("population"):
        return False
    ofix, nfix = om.get("fixed_keys", {}), nm.get("fixed_keys", {})
    if any(key in nfix and nfix[key] != value for key, value in ofix.items()):
        return False
    return True


def _cell_key(row, keys):
    return tuple(_canonical(k, row.get(k)) for k in keys)


def _canonical(key, value):
    text = str(value).strip()
    if key == "ym":
        return text.replace("-", "")
    if key in ("hour", "hour3"):
        return str(int(text))
    if key == "dow" and text in {str(i) for i in range(7)}:
        from lib.timeparse import DOW_LABELS
        return DOW_LABELS[int(text)]
    return text


def _reference_baseline(tables, cfg, result):
    """Known narrowing from complete 0911 month/week-hour tables."""
    bounds = {}
    month = next((t for t in tables if t["keys"] == ["ym"]), None)
    week = next((t for t in tables if t["keys"] == ["dow", "hour"]), None)
    if month is None or week is None:
        _add(result, "C8", "WARN", "1차 두 표의 합계 대조 불가: 수작업 점검 필요")
        return bounds
    if any(row["n"] is None for row in month["rows"]):
        _add(result, "C8", "WARN", "월별 참조 합계에 억제 칸이 있어 대조 불가")
        return bounds
    hidden = [(i, row) for i, row in enumerate(week["rows"]) if row["n"] is None]
    total = sum(row["n"] for row in month["rows"])
    visible = sum(row["n"] for row in week["rows"] if row["n"] is not None)
    lo, hi = _range(week["meta"], cfg)
    try:
        narrowed = exposure_ranges(total - visible, len(hidden), lo, hi)
    except ValueError:
        _add(result, "C8", "FAIL", "과거 두 표 합계와 억제 범위가 서로 맞지 않습니다")
        return bounds
    for (index, row), interval in zip(hidden, narrowed):
        bounds[(week["name"], index)] = interval
        if interval != (lo, hi):
            result["known_count"] += 1
            result["exposures"].append({"status": "KNOWN", "table": week["name"],
                                        "cell_index": index, "range": list(interval),
                                        "original_range": [lo, hi],
                                        "key": {k: row[k] for k in week["keys"]},
                                        "pair": [month["name"], week["name"]]})
    if result["known_count"]:
        _add(result, "C8", "KNOWN", "1차 표 사이에서 이미 알려진 억제 범위가 있습니다")
    return bounds


def _match_rows(old, new, cfg):
    """Return deterministic old/new cell matches; never infer an incomplete total."""
    common = set(old["keys"]) & set(new["keys"])
    old_time = next((k for k in old["keys"] if k in TIME_KEYS), None)
    new_time = next((k for k in new["keys"] if k in TIME_KEYS), None)
    for oi, oldrow in enumerate(old["rows"]):
        for ni, newrow in enumerate(new["rows"]):
            if any(_canonical(k, oldrow.get(k)) != _canonical(k, newrow.get(k)) for k in common):
                continue
            if old_time and new_time and old_time != new_time:
                mapped = project_time_key(old_time, new_time, oldrow[old_time], cfg)
                if mapped is None or str(mapped).lstrip("0") != str(newrow[new_time]).lstrip("0"):
                    continue
            elif old_time != new_time:
                continue
            if set(old["keys"]) != set(new["keys"]):
                # Only identical cell resolution is safe without a complete
                # coverage declaration; time projection to one bucket is not.
                continue
            yield oi, ni


def _project_old_row(old, new, row, cfg):
    values = []
    for key in new["keys"]:
        if key in old["keys"]:
            values.append(_canonical(key, row.get(key)))
            continue
        if key in TIME_KEYS:
            source = next((k for k in old["keys"] if k in TIME_KEYS), None)
            if source is None:
                return None
            mapped = project_time_key(source, key, row[source], cfg)
        elif key == "R" and "ym" in old["keys"]:
            mapped = project_time_key("ym", "R", row["ym"], cfg)
        else:
            return None
        if mapped is None:
            return None
        values.append(_canonical(key, mapped))
    return tuple(values)


def _check_projected_group(old, new, indexes, ni, cfg, baseline, result):
    """Compare one new coarse cell with its old fine cells in both directions."""
    row = new["rows"][ni]
    domains = []
    hidden = []
    for oi in indexes:
        prior = old["rows"][oi]
        if prior["n"] is None:
            domains.append(baseline.get((old["name"], oi), _range(old["meta"], cfg)))
            hidden.append(oi)
        else:
            domains.append((prior["n"], prior["n"]))
    previous = _row_interval(row, new["meta"], cfg)
    low = max(previous[0], sum(bound[0] for bound in domains))
    high = min(previous[1], sum(bound[1] for bound in domains))
    if low > high:
        _add(result, "C8", "FAIL", "시간·레짐 투영 집계가 과거 표와 모순됩니다")
        return
    # Old information may already bound a new hidden cell. That alone is
    # historical knowledge, not an additional disclosure by this run.
    for pos, oi in enumerate(indexes):
        if oi not in hidden:
            continue
        original = domains[pos]
        others_low = sum(bound[0] for j, bound in enumerate(domains) if j != pos)
        others_high = sum(bound[1] for j, bound in enumerate(domains) if j != pos)
        narrowed = (max(original[0], low - others_high),
                    min(original[1], high - others_low))
        if len(hidden) == 1 and low == high:
            # Shared primitive for a fixed sum. Published old cells have
            # point intervals and can be subtracted exactly.
            hidden_sum = low - sum(old["rows"][j]["n"] for j in indexes if j != oi)
            narrowed = exposure_ranges(hidden_sum, 1, original[0], original[1])[0]
        if narrowed != original:
            _add(result, "C8", "FAIL", "신규 집계가 과거 억제 칸의 가능 범위를 좁혔습니다")
            result["exposures"].append({"status": "FAIL", "table": old["name"],
                                        "cell_index": oi, "range": list(narrowed)})


def _check_reverse_complete(old, new, cfg, baseline, result):
    """For a declared complete fine table, compare each old public margin."""
    shared = [key for key in old["keys"] if key in new["keys"]]
    complete = new["meta"].get("coverage_complete") is True
    if set(new["keys"]) == {"dow", "hour_bucket"}:
        from lib.timeparse import DOW_LABELS, hour_to_bucket
        expected = {(str(day), str(hour_to_bucket(hour, cfg["export"]["night_bucket"])))
                    for day in DOW_LABELS for hour in range(24)}
        actual = {(str(row["dow"]), str(row["hour_bucket"])) for row in new["rows"]}
        complete = actual == expected and len(actual) == len(new["rows"])
    if not complete:
        _add(result, "C8", "FAIL", "세부 표의 전체 범위 증명이 없어 과거 합계와 대조할 수 없습니다")
        return
    if "G" in new["keys"] and "G" not in old["keys"]:
        _add(result, "C8", "FAIL", "G 분할의 급식 동일모집단 범위를 확인할 수 없습니다")
        return
    old_groups = {}
    for oi, row in enumerate(old["rows"]):
        old_groups.setdefault(_cell_key(row, shared), []).append(oi)
    new_groups = {}
    for ni, row in enumerate(new["rows"]):
        new_groups.setdefault(_cell_key(row, shared), []).append(ni)
    for group, old_indices in old_groups.items():
        new_indices = new_groups.get(group, [])
        old_intervals = [_row_interval(old["rows"][oi], old["meta"], cfg) for oi in old_indices]
        new_intervals = [_row_interval(new["rows"][ni], new["meta"], cfg) for ni in new_indices]
        if not new_indices:
            # Complete coverage plus no row means zero (absent row).
            new_intervals = []
        low = max(sum(x[0] for x in old_intervals), sum(x[0] for x in new_intervals))
        high = min(sum(x[1] for x in old_intervals), sum(x[1] for x in new_intervals))
        if low > high:
            _add(result, "C8", "FAIL", "전체 세부 집계와 과거 공개 합계가 모순됩니다")
            continue
        for pos, ni in enumerate(new_indices):
            if new["rows"][ni]["status"] != "suppressed":
                continue
            original = new.get("historical_bounds", {}).get(ni, new_intervals[pos])
            narrowed = (max(original[0], low - sum(x[1] for j, x in enumerate(new_intervals) if j != pos)),
                        min(original[1], high - sum(x[0] for j, x in enumerate(new_intervals) if j != pos)))
            if narrowed != original:
                _add(result, "C8", "FAIL", "과거 합계와 신규 공개 칸이 신규 억제 범위를 좁혔습니다")
                result["exposures"].append({"status": "FAIL", "table": new["name"],
                                            "cell_index": ni, "range": list(narrowed)})
        for pos, oi in enumerate(old_indices):
            if old["rows"][oi]["n"] is not None:
                continue
            original = baseline.get((old["name"], oi), old_intervals[pos])
            others_low = sum(x[0] for j, x in enumerate(old_intervals) if j != pos)
            others_high = sum(x[1] for j, x in enumerate(old_intervals) if j != pos)
            narrowed = (max(original[0], low - others_high),
                        min(original[1], high - others_low))
            if narrowed != original:
                _add(result, "C8", "FAIL", "세부 표가 과거 억제 칸의 가능 범위를 좁혔습니다")
                result["exposures"].append({"status": "FAIL", "table": old["name"],
                                            "cell_index": oi, "range": list(narrowed)})


def _check_pair(old, new, cfg, baseline, result):
    compatibility = _population_match(old, new)
    if compatibility is False:
        return
    if compatibility is None:
        _add(result, "C8", "FAIL", "G 분할 또는 모집단이 불명확해 과거 표와 안전하게 대조할 수 없습니다")
        return
    old_bounds = _range(old["meta"], cfg)
    new_bounds = _range(new["meta"], cfg)
    matched = False
    for oi, ni in _match_rows(old, new, cfg):
        matched = True
        a, b = old["rows"][oi], new["rows"][ni]
        old_interval = baseline.get((old["name"], oi), old_bounds) if a["n"] is None else (a["n"], a["n"])
        new_interval = _row_interval(b, new["meta"], cfg)
        overlap = (max(old_interval[0], new_interval[0]), min(old_interval[1], new_interval[1]))
        if overlap[0] > overlap[1]:
            _add(result, "C8", "FAIL", "기존 표와 신규 표의 동일 칸이 서로 모순됩니다")
        elif a["n"] is None and overlap != old_interval:
            _add(result, "C8", "FAIL", "신규 표가 과거 억제 칸의 가능 범위를 좁혔습니다")
            result["exposures"].append({"status": "FAIL", "table": old["name"],
                                        "cell_index": oi, "range": list(overlap)})
        # A new hidden cell can be narrower from the old public cell alone;
        # that is already-public knowledge, unless domains contradict above.
    if set(old["keys"]) != set(new["keys"]):
        projected = {}
        for oi, row in enumerate(old["rows"]):
            key = _project_old_row(old, new, row, cfg)
            if key is not None:
                projected.setdefault(key, []).append(oi)
        for ni, row in enumerate(new["rows"]):
            key = _cell_key(row, new["keys"])
            if key not in projected:
                continue
            matched = True
            try:
                _check_projected_group(old, new, projected[key], ni, cfg, baseline, result)
            except ValueError:
                _add(result, "C8", "FAIL", "투영 집계의 가능 범위 계산 오류")
    if not matched and set(old["keys"]) != set(new["keys"]):
        _check_reverse_complete(old, new, cfg, baseline, result)
        matched = True
    if not matched:
        _add(result, "C8", "FAIL", "참조 표와 새 표의 대응 칸을 확인할 수 없습니다")


def _audit_new_table(path, cfg, regexes, result):
    name = path.stem
    safe_name = _safe(name, cfg["id_patterns"])
    meta_path = path.with_suffix(".meta.json")
    if not meta_path.exists():
        _add(result, "C3", "FAIL", safe_name + ": 메타 사이드카 없음")
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for key in ("population", "keys", "metrics", "time_only", "zero_policy", "night_bucket_applied"):
            if key not in meta:
                raise ValueError("메타 필수 항목 누락")
        if not isinstance(meta["keys"], list) or not isinstance(meta["metrics"], list):
            raise ValueError("메타 키 형식 오류")
        if (not all(isinstance(key, str) for key in meta["keys"] + meta["metrics"])
                or not isinstance(meta.get("fixed_keys", {}), dict)
                or not isinstance(meta["population"], str)
                or type(meta["time_only"]) is not bool
                or type(meta["night_bucket_applied"]) is not bool):
            raise ValueError("메타 필드 자료형 오류")
        _range(meta, cfg)
        header, rows = _read_csv(path)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        _add(result, "C3", "FAIL", safe_name + ": CSV 또는 메타 형식 오류")
        return None
    if "status" not in header or any(k not in header for k in meta["keys"] + meta["metrics"]):
        _add(result, "C3", "FAIL", safe_name + ": 상태 또는 메타 등록 열 누락")
        return None
    if not rows:
        _add(result, "C3", "FAIL", safe_name + ": 빈 CSV")
        return None
    try:
        identities = [_cell_key(row, meta["keys"]) for row in rows]
        if len(set(identities)) != len(rows):
            raise ValueError("중복 키")
    except (ValueError, TypeError):
        _add(result, "C3", "FAIL", safe_name + ": 중복 키 또는 키 형식 오류")
        return None
    if any(row["status"] not in ALLOWED_STATUS or
           (row["status"] == "zero" and meta["zero_policy"] != "show") for row in rows):
        _add(result, "C3", "FAIL", safe_name + ": 허용하지 않는 status")
        return None
    if any(regex.search(str(value)) for regex in regexes
           for value in [path.name] + header + [cell for row in rows for cell in row.values()]):
        _add(result, "C2", "FAIL", safe_name + ": ID 형식 검출")
    if len(meta["keys"]) > cfg["export"]["max_axes"]:
        exception = meta["time_only"] is True and cfg["export"].get("time_only_axes_exception") is True
        if any(k in REGION_KEYS for k in meta["keys"]) or not exception:
            _add(result, "C5", "FAIL", safe_name + ": 축 수 초과")
    is_meal = meta.get("population_kind") not in ("general", "shop", "diagnostic")
    if is_meal:
        for row in rows:
            if row["status"] != "published":
                continue
            try:
                for col, minimum in (("n", "n_min"), ("n_shop", "shop_min"), ("n_cust", "cust_min")):
                    if col in row and _int_or_none(row[col]) is not None and _int_or_none(row[col]) < cfg["suppression"][minimum]:
                        _add(result, "C4", "FAIL", safe_name + ": 공개 건수가 억제 기준 미달")
                        break
            except (ValueError, OverflowError):
                _add(result, "C4", "FAIL", safe_name + ": 공개 건수 형식 오류")
        for key in TIME_KEYS & set(meta["keys"]):
            if key == "hour" and any(str(row[key]).strip().lstrip("0") in {"23", "", "1", "2", "3", "4", "5"} for row in rows):
                _add(result, "C6", "FAIL", safe_name + ": 급식표에 심야 개별 시간 칸 존재")
    if any(col.startswith("share_") for col in header) and "n" in header:
        _add(result, "C7", "WARN", safe_name + ": 비중과 분모 건수의 동시 공개 여부 확인 필요")
    payload = set(header) - set(meta["keys"]) - {"status"}
    if any(row["status"] == "suppressed" and any(row.get(col, "") != "" for col in payload) for row in rows):
        _add(result, "C4", "FAIL", safe_name + ": 억제 칸에 수치가 남아 있습니다")
    if "n" not in meta["metrics"]:
        return None  # Only additive n participates in C8.
    for row in rows:
        if row["status"] == "banded":
            row["_band_range"] = _band_range(row.get("n"))
            if row["_band_range"] is None:
                _add(result, "C8", "WARN", safe_name + ": 미지원 구간 표기, 수작업 점검 필요")
                return None
            row["n"] = None
            continue
        try:
            row["n"] = _int_or_none(row.get("n"))
            if row["status"] == "published" and row["n"] is None:
                raise ValueError("published n 누락")
            if row["status"] == "zero" and row["n"] != 0:
                raise ValueError("zero n 불일치")
        except (ValueError, OverflowError):
            _add(result, "C3", "FAIL", safe_name + ": n 수치 형식 오류")
            return None
    return {"name": name, "keys": meta["keys"], "meta": meta, "rows": rows, "reference": False}


def _check_filter(path, result):
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        _add(result, "C9", "FAIL", "filter_definition.txt 없음 또는 인코딩 오류")
        return
    groups = (("급식", "meal"), ("상태", "status"), ("기간", "period"),
              ("레짐", "regime"), ("지표", "metric"), ("심야", "night"), ("0 처리", "zero"))
    if any(not any(word in text.lower() for word in choices) for choices in groups):
        _add(result, "C9", "FAIL", "filter_definition.txt 필수 정의 누락")


def _finalize(result, run=None, cfg=None):
    if result["fail_count"] == 0:
        _add(result, "SUMMARY", "PASS", "단계 A 점검에서 추가 FAIL 없음")
    if run is not None:
        report = Path(run) / "internal/export_check_report.txt"
        report.parent.mkdir(parents=True, exist_ok=True)
        patterns = cfg["id_patterns"] if cfg else []
        lines = ["V2-07 단계 A 반출 점검", "FAIL=%d WARN=%d KNOWN=%d" %
                 (result["fail_count"], result["warn_count"], result["known_count"])]
        for item in result["checks"]:
            lines.append("%s %s %s" % (item["code"], item["status"], _safe(item["message"], patterns)))
        for item in result["exposures"]:
            lines.append("%s %s cell_index=%d range=%s" %
                         (item["status"], _safe(item["table"], patterns), item["cell_index"], item["range"]))
            lines.append(_safe("  key=%s original_range=%s pair=%s" %
                               (item.get("key"), item.get("original_range"), item.get("pair")), patterns))
        if result["fail_count"]:
            lines.append("제안 조치: 해당 표의 해상도를 낮추거나 이번 반출에서 제외하고 해당 모듈을 재실행하세요.")
            lines.append("합계로 범위가 좁혀지면 같은 그룹의 공개 칸을 추가 억제하세요. show 표는 mask 또는 합계 구간 표기를 검토하세요.")
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result["report_path"] = str(report)
    return result


def check_references(cfg):
    """Audit only approved past references; ID gate is N/A in this mode."""
    result = _result()
    try:
        config = _load_cfg(cfg)
        _compile_patterns(config, result, True)
        refs = _load_references(config, result)
        _reference_baseline(refs, config, result)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        _add(result, "CONFIG", "FAIL", "참조 점검 설정 오류: " + type(exc).__name__)
    return _finalize(result)


def check_run(config_path, run_path, reference_only=False):
    """Audit a run, write an internal report, and return the documented result."""
    result = _result()
    try:
        cfg = _load_cfg(config_path)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        _add(result, "CONFIG", "FAIL", "설정 오류: " + type(exc).__name__)
        return _finalize(result, run_path)
    regexes = _compile_patterns(cfg, result, reference_only)
    refs = _load_references(cfg, result)
    baseline = _reference_baseline(refs, cfg, result)
    if reference_only:
        return _finalize(result, run_path, cfg)
    export = Path(run_path) / "export"
    if not export.is_dir():
        _add(result, "C1", "FAIL", "export 폴더 없음")
        return _finalize(result, run_path, cfg)
    allowed = {"filter_definition.txt", "run_manifest.json"}
    csv_paths = []
    for entry in export.iterdir():
        if entry.is_file() and entry.suffix == ".csv":
            csv_paths.append(entry)
        elif entry.is_file() and entry.name.endswith(".meta.json"):
            if not (export / (entry.name[:-10] + ".csv")).exists():
                _add(result, "C3", "FAIL", "짝이 없는 메타 사이드카")
        elif entry.name not in allowed:
            _add(result, "C1", "FAIL", "export 폴더에 허용하지 않는 파일")
    if not csv_paths:
        _add(result, "C1", "FAIL", "export 폴더에 검사할 CSV가 없습니다")
    if not (export / "run_manifest.json").is_file():
        _add(result, "C1", "FAIL", "run_manifest.json 없음")
    _check_filter(export / "filter_definition.txt", result)
    for path in csv_paths:
        table = _audit_new_table(path, cfg, regexes, result)
        if table is None:
            continue
        # Bounds derivable from old tables alone remain historical knowledge.
        # This is a read-only baseline, never a new/new propagation pass.
        table["historical_bounds"] = {}
        for old in refs:
            if _population_match(old, table) is not True:
                continue
            groups = {}
            projectable = True
            for oi, row in enumerate(old["rows"]):
                key = _project_old_row(old, table, row, cfg)
                if key is None:
                    projectable = False
                    break
                interval = baseline.get((old["name"], oi), _row_interval(row, old["meta"], cfg))
                groups.setdefault(key, []).append(interval)
            if not projectable:
                continue
            for ni, row in enumerate(table["rows"]):
                if row["status"] != "suppressed":
                    continue
                intervals = groups.get(_cell_key(row, table["keys"]), [])
                if not intervals and old["meta"]["zero_policy"] != "absent_row":
                    continue
                initial = table["historical_bounds"].get(ni, _range(table["meta"], cfg))
                bound = (max(initial[0], sum(x[0] for x in intervals)),
                         min(initial[1], sum(x[1] for x in intervals)))
                if bound[0] <= bound[1]:
                    table["historical_bounds"][ni] = bound
        for old in refs:
            first = len(result["exposures"])
            _check_pair(old, table, cfg, baseline, result)
            for item in result["exposures"][first:]:
                source = old if item["table"] == old["name"] else table
                index = item["cell_index"]
                row = source["rows"][index]
                item["key"] = {k: row[k] for k in source["keys"]}
                item["original_range"] = list(baseline.get((source["name"], index), _range(source["meta"], cfg)))
                item["pair"] = [old["name"], table["name"]]
    return _finalize(result, run_path, cfg)


def main(argv=None):
    parser = argparse.ArgumentParser(description="V2-07 단계 A 반출 점검")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--reference-only", action="store_true")
    parser.add_argument("--past", help="단계 B 전용; 현재 지원하지 않음")
    args = parser.parse_args(argv)
    if args.past is not None:
        parser.error("--past는 단계 B에서 구현합니다; 현재 사용할 수 없습니다")
    result = check_run(args.config, args.run, args.reference_only)
    print("단계 A 반출 점검: FAIL=%d WARN=%d KNOWN=%d" %
          (result["fail_count"], result["warn_count"], result["known_count"]))
    if result["report_path"]:
        print("내부 보고서: " + str(result["report_path"]))
    return 1 if result["fail_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
