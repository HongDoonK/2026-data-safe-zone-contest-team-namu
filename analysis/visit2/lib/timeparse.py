"""Calendar fields without locale-dependent weekday labels."""
import pandas as pd

DOW_LABELS = ("월", "화", "수", "목", "금", "토", "일")
HOUR3_LABELS = ("00-02", "03-05", "06-08", "09-11", "12-14", "15-17", "18-20", "21-23")


def label_dow(value):
    day = int(value)
    if day != value or not 0 <= day <= 6:
        raise ValueError("dow는 0~6 정수여야 합니다")
    return DOW_LABELS[day]


def hour_to_hour3(hour):
    hour = _hour(hour)
    return hour // 3


def _hour(hour):
    value = int(hour)
    if str(hour).strip() not in (str(value), "%02d" % value) or not 0 <= value <= 23:
        raise ValueError("hour는 0~23 정수여야 합니다")
    return value


def hour_to_bucket(hour, cfg):
    value = _hour(hour)
    if cfg.get("enabled", True) and value in cfg["hours"]:
        return cfg["label"]
    return "%02d" % value


def project_time_key(source, target, value, cfg):
    """Project a time key only when every source instant has one target value.

    None means the projection is ambiguous; hour3=7 straddles the night bucket.
    """
    if source == target:
        return value
    if source == "hour" and target == "hour3":
        return hour_to_hour3(value)
    if source == "hour" and target == "hour_bucket":
        return hour_to_bucket(value, cfg["export"]["night_bucket"])
    if source == "hour3" and target == "hour_bucket":
        start = int(value) * 3
        values = {hour_to_bucket(h, cfg["export"]["night_bucket"]) for h in range(start, start + 3)}
        return next(iter(values)) if len(values) == 1 else None
    if source == "ym" and target == "R" and cfg.get("regime", {}).get("mode") == "month":
        ym = str(value).replace("-", "")
        if len(ym) != 6 or not ym.isdigit():
            return None
        month = int(ym[-2:])
        regime = cfg["regime"]
        return regime["month_map"].get(str(month), regime["default"])
    return None


def add_time_fields(df, col="app_time"):
    result = df.copy()
    text = df[col].astype("string").str.strip()
    valid_shape = text.str.fullmatch(r"[0-9]{10}", na=False)
    dates = pd.to_datetime(text.where(valid_shape), format="%Y%m%d%H", errors="coerce")
    result["time_invalid"] = dates.isna()
    result["ym"] = (dates.dt.year * 100 + dates.dt.month).astype("Int64")
    result["month"] = dates.dt.month.astype("Int64")
    result["ymd"] = (dates.dt.year * 10000 + dates.dt.month * 100 + dates.dt.day).astype("Int64")
    result["hour"] = dates.dt.hour.astype("Int64")
    result["dow"] = dates.dt.weekday.astype("Int64")
    result["is_weekend"] = result.dow.ge(5).astype("boolean")
    result["hour3"] = result.hour // 3
    return result


def assign_regime(df, regime_cfg):
    result = pd.Series(regime_cfg["default"], index=df.index, dtype=object)
    mode = regime_cfg["mode"]
    if mode == "month":
        mapping = {int(k): v for k, v in regime_cfg["month_map"].items()}
        return df.month.map(mapping).fillna(regime_cfg["default"])
    if mode != "date_ranges":
        raise ValueError("알 수 없는 regime.mode")
    claimed = pd.Series(False, index=df.index)
    for item in regime_cfg["date_ranges"]:
        start, end = int(item["start"]), int(item["end"])
        if start > end:
            raise ValueError("레짐 날짜 범위가 역순입니다")
        mask = df.ymd.between(start, end).fillna(False)
        if (claimed & mask).any():
            raise ValueError("레짐 날짜 범위가 겹칩니다")
        result.loc[mask] = item["label"]
        claimed = claimed | mask
    return result
