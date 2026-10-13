"""JSON schema and discovery-specific configuration loading."""
import json
from pathlib import Path


def meal_values_configured(cfg):
    values = cfg.get("meal_pay_values")
    return isinstance(values, list) and bool(values) and all(
        isinstance(x, str) and x.strip() and not x.strip().startswith("<") for x in values)


def _load(path, discovery):
    path = Path(path).resolve()
    try:
        cfg = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError("설정 JSON을 읽을 수 없습니다: " + type(exc).__name__) from exc
    required = ("paths", "columns", "meal_pay_values", "status_filter", "period", "regime",
                "suppression", "export", "reference_exports", "id_patterns", "bootstrap",
                "publish_rule", "chunksize", "encoding_candidates", "run_label")
    if not isinstance(cfg, dict):
        raise ValueError("설정은 JSON 객체여야 합니다")
    for key in required:
        if key not in cfg:
            raise ValueError("필수 설정 누락: " + key)
    nested = {"paths": ("pay", "shop", "out_root"),
              "suppression": ("n_min", "shop_min", "cust_min", "zero_policy"),
              "export": ("max_axes", "time_only_axes_exception", "split_axis", "night_bucket"),
              "status_filter": ("mode", "complete_values", "cancel_values"),
              "period": ("start_ym", "end_ym"),
              "regime": ("mode", "month_map", "default", "date_ranges"),
              "bootstrap": ("reps", "seed"),
              "publish_rule": ("count_share_thresholds", "primary")}
    for section, keys in nested.items():
        if not isinstance(cfg[section], dict):
            raise ValueError("설정 객체 필요: " + section)
        for key in keys:
            if key not in cfg[section]:
                raise ValueError("필수 설정 누락: " + section + "." + key)
    for section, key in [("suppression", "n_min"), ("suppression", "shop_min"),
                         ("suppression", "cust_min"), ("export", "max_axes"), ("bootstrap", "reps")]:
        if type(cfg[section][key]) is not int or cfg[section][key] < 1:
            raise ValueError("양의 정수 필요: " + section + "." + key)
    if type(cfg["chunksize"]) is not int or cfg["chunksize"] < 1:
        raise ValueError("chunksize는 양의 정수여야 합니다")
    if cfg["suppression"]["zero_policy"] not in ("mask", "show"):
        raise ValueError("suppression.zero_policy 오류")
    if cfg["status_filter"]["mode"] not in ("all", "complete_only", "exclude_cancel"):
        raise ValueError("status_filter.mode 오류")
    if cfg["regime"]["mode"] not in ("month", "date_ranges"):
        raise ValueError("regime.mode 오류")
    try:
        active = cfg["columns"]["active"]
        cfg["cols_pay"] = dict(cfg["columns"][active]["pay"])
        cfg["cols_shop"] = dict(cfg["columns"][active]["shop"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("columns 활성 매핑 오류") from exc
    if not discovery and not meal_values_configured(cfg):
        raise ValueError("meal_pay_values 미설정: M1 값 목록을 보고 사람이 설정해야 합니다")
    cfg["_config_path"] = str(path)
    return cfg


def load_config(path):
    return _load(path, False)


def load_discovery_config(path):
    """M1-only exception; load_config(path) keeps the specified signature."""
    return _load(path, True)
