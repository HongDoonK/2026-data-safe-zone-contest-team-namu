"""Shop-join primitives with conservative small-group disclosure."""
import math

import numpy as np
import pandas as pd

from .filters import meal_flag, period_mask, status_mask
from .io import detect_encoding, iter_chunks
from .pipeline import Aggregate, emit, read_pay


def clean_shops(frame):
    present = frame.loc[frame.shop_id.notna()].copy()
    duplicate = present.shop_id.duplicated(keep=False)
    return present.loc[~duplicate].copy(), present.loc[duplicate].copy()


def safe_ratio(numerator, denominator):
    if numerator < 3 or denominator < 3:
        return np.nan, np.nan, np.nan
    return numerator / denominator, numerator, denominator


def distribution(counts):
    fields = ["p50", "p75", "p90", "top10pct_share", "n_shops"]
    if len(counts) < 50:
        return dict.fromkeys(fields, np.nan)
    return {"p50": float(counts.quantile(0.5)), "p75": float(counts.quantile(0.75)),
            "p90": float(counts.quantile(0.9)), "n_shops": len(counts),
            "top10pct_share": float(counts.nlargest(math.ceil(len(counts) * 0.1)).sum() / counts.sum())}


def read_shops(cfg):
    mapping = cfg["columns"][cfg["columns"]["active"]]["shop"]
    encoding = detect_encoding(cfg["paths"]["shop"], cfg["encoding_candidates"])
    parts = list(iter_chunks(cfg["paths"]["shop"], list(mapping), mapping, encoding, cfg["chunksize"]))
    if not parts:
        raise ValueError("가맹점 테이블이 비었습니다")
    return pd.concat(parts, ignore_index=True)


def join_shops(frame, clean):
    result = frame.merge(clean, on="shop_id", how="left", validate="many_to_one", indicator=True)
    result["in_shop_table"] = result._merge.eq("both").map({True: "Y", False: "N"})
    for column in ("child_able", "gungu", "dong"):
        result[column] = result[column].fillna("<EMPTY>")
        result.loc[result.in_shop_table.eq("N"), column] = "<NOT_IN_TABLE>"
    return result.drop(columns=["_merge"])


def _shop_emit(ctx, frame, name, keys, n_col="n", margins=None, fixed_keys=None):
    frame = frame.copy()
    for column in frame:
        if column not in list(keys) + [n_col] and pd.api.types.is_numeric_dtype(frame[column]):
            frame.loc[frame[column].lt(3), column] = np.nan
    return emit(ctx, frame, name, keys, "shop", n_col=n_col, shop_col=None, cust_col=None,
                margins=margins, fixed_keys=fixed_keys, thresholds={"n_min": 3}, subset={"profile": name})


def run(ctx):
    cfg = ctx.cfg
    raw = read_shops(cfg)
    clean, duplicates = clean_shops(raw)
    ctx.write_internal(duplicates, "m3_duplicate_shop_rows.csv")
    ctx.write_internal(raw[["gungu", "dong"]].drop_duplicates(), "m3_dong_names.csv")
    profile = {"rows": len(raw), "unique_shop_id": raw.shop_id.nunique(),
               "dup_shop_id_count": duplicates.shop_id.nunique(), "empty_shop_id": int(raw.shop_id.isna().sum())}
    ctx.write_internal(pd.DataFrame([profile]), "m3_shop_keys.csv")
    public_profile = {key: value if value >= 3 else np.nan for key, value in profile.items()}
    emit(ctx, pd.DataFrame([public_profile]), "m3_shop_keys", [], "shop", n_col=None, shop_col=None, cust_col=None)
    normalized = raw.copy()
    for column in normalized:
        if column != "shop_id":
            normalized[column] = normalized[column].fillna("<EMPTY>")
    values = []
    for column in ("child_able", "good_able", "store_status", "service_closed"):
        table = normalized[column].value_counts().rename("n").rename_axis("value").reset_index()
        table["column"] = column
        values.append(table)
    _shop_emit(ctx, pd.concat(values, ignore_index=True), "m3_shop_values", ["column", "value"])
    keys = ["child_able", "store_status", "service_closed"]
    cross = normalized.groupby(keys).size().rename("n").reset_index()
    _shop_emit(ctx, cross, "m3_shop_status_cross", keys)
    normalized["closed_year"] = normalized.closed_at.where(normalized.closed_at.str.fullmatch(r"[0-9]{4}(0[1-9]|1[0-2])"), "<INVALID>").map(lambda x: x[:4] if x != "<INVALID>" else x)
    closed = normalized.groupby(["closed_year", "store_status"]).size().rename("n").reset_index()
    _shop_emit(ctx, closed, "m3_shop_closed_year", ["closed_year", "store_status"])
    locations = []
    lengths = []
    for gungu, group in normalized.groupby("gungu"):
        n_y = int(group.child_able.eq("Y").sum())
        locations.append({"gungu": gungu, "n_shop": group.shop_id.nunique(),
                          "n_dong_unique": group.dong.nunique(), "n_child_able_y": n_y if n_y >= 3 else np.nan})
        for length, part in group.groupby(group.dong.str.len()):
            names = part.dong.drop_duplicates()
            lengths.append({"gungu": gungu, "len_chars": length, "n_shop": part.shop_id.nunique(),
                            "n_dong_unique": len(names), "ends_with_digit_dong": int(names.str.contains(r"[0-9]동$").sum())})
    _shop_emit(ctx, pd.DataFrame(locations), "m3_gungu", ["gungu"], "n_shop")
    _shop_emit(ctx, pd.DataFrame(lengths), "m3_dong_name_length", ["gungu", "len_chars"], "n_shop")
    print("[M3] 군위군 등장: " + ("예" if normalized.gungu.str.contains("군위").any() else "아니오"))
    parts_all, parts_meal = [], []
    monthly = Aggregate(["ym", "child_able"])
    total_rows = total_meal_rows = referenced_rows = referenced_meal_rows = 0
    for frame in read_pay(cfg):
        selected = frame.loc[~frame.time_invalid & period_mask(frame, cfg["period"]) & status_mask(frame, cfg["status_filter"])].copy()
        joined = join_shops(selected, clean)
        meal = meal_flag(joined, cfg["meal_pay_values"])
        total_rows += len(joined)
        total_meal_rows += int(meal.sum())
        referenced_rows += int(joined.in_shop_table.eq("Y").sum())
        referenced_meal_rows += int((meal & joined.in_shop_table.eq("Y")).sum())
        monthly.update(joined.loc[meal])
        for part, collection in ((joined, parts_all), (joined.loc[meal], parts_meal)):
            collection.append(part.groupby("shop_id").agg(n=("ym", "size"), first_ym=("ym", "min"), last_ym=("ym", "max")).reset_index())
    def reduce_parts(parts, label):
        data = pd.concat(parts, ignore_index=True)
        grouped = data.groupby("shop_id", as_index=False).agg(n=("n", "sum"), first_ym=("first_ym", "min"), last_ym=("last_ym", "max"))
        return grouped.rename(columns={"n": "pay_n_" + label, "first_ym": "first_ym_" + label, "last_ym": "last_ym_" + label})
    pay = reduce_parts(parts_all, "all").merge(reduce_parts(parts_meal, "meal"), on="shop_id", how="outer")
    pay[["pay_n_all", "pay_n_meal"]] = pay[["pay_n_all", "pay_n_meal"]].fillna(0).astype("int64")
    ctx.write_internal(pay, "m3_shop_pay_summary.csv")
    union = pd.DataFrame({"shop_id": pd.concat([raw.shop_id, pay.shop_id]).dropna().drop_duplicates()})
    union = join_shops(union, clean).merge(pay, on="shop_id", how="left", validate="one_to_one")
    union[["pay_n_all", "pay_n_meal"]] = union[["pay_n_all", "pay_n_meal"]].fillna(0)
    union["has_pay"], union["has_meal_pay"] = union.pay_n_all.gt(0), union.pay_n_meal.gt(0)
    keys = ["in_shop_table", "child_able", "has_pay", "has_meal_pay"]
    cross = union.groupby(keys).size().rename("n_shop").reset_index()
    ctx.write_internal(cross, "m3_shop_meal_x_able.csv")
    # Split one explicit key into fixed metadata; no four-axis export.
    for index, (value, part) in enumerate(cross.groupby("in_shop_table")):
        _shop_emit(ctx, part.drop(columns=["in_shop_table"]), "m3_shop_meal_x_able_%d" % index,
                   keys[1:], "n_shop", [["child_able"], ["has_pay", "has_meal_pay"]], {"in_shop_table": value})
    in_table, has_pay, has_meal = union.in_shop_table.eq("Y"), union.has_pay, union.has_meal_pay
    yes = union.child_able.eq("Y")
    rates = {"dup_id_excluded_shops": duplicates.shop_id.nunique() if duplicates.shop_id.nunique() >= 3 else np.nan}
    items = {"ref_rate_rows": (referenced_rows, total_rows),
             "ref_rate_shops": (int((in_table & has_pay).sum()), int(has_pay.sum())),
             "ref_rate_meal_rows": (referenced_meal_rows, total_meal_rows),
             "match_rate_y_given_meal": (int((yes & has_meal).sum()), int((in_table & has_meal).sum())),
             "active_rate_meal_given_y": (int((yes & has_meal).sum()), int(yes.sum())),
             "active_rate_any_given_y": (int((yes & has_pay).sum()), int(yes.sum()))}
    for key, (num, den) in items.items():
        rates[key], rates[key + "_num"], rates[key + "_den"] = safe_ratio(num, den)
    emit(ctx, pd.DataFrame([rates]), "m3_join_rates", [], "shop", n_col=None, shop_col=None, cust_col=None)
    dist = [dict(distribution(union.loc[has_meal, "pay_n_meal"]), child_able="ALL")]
    for value, part in union.loc[has_meal].groupby("child_able"):
        dist.append(dict(distribution(part.pay_n_meal), child_able=value))
    emit(ctx, pd.DataFrame(dist), "m3_meal_shop_distribution", ["child_able"], "shop", n_col=None, shop_col=None, cust_col=None)
    by_month = monthly.finalize()
    ctx.write_internal(by_month, "m3_meal_ym_by_able.csv")
    emit(ctx, by_month, "m3_meal_ym_by_able", ["ym", "child_able"], margins=[["ym"], ["child_able"]])
    ctx.finish("M3", {"dup_id_excluded_shops": int(duplicates.shop_id.nunique()), "rejected_tables": ctx.rejected_tables,
                      "split_axis_T3_b": "in_shop_table"})
    print("[M3] run=" + str(ctx.root))
    return 0
