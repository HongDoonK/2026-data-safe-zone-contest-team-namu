"""M2 chunked comparisons and paired shop-block bootstrap."""
import calendar
import time

import numpy as np
import pandas as pd

from .distinct import CountAccumulator, DistinctAccumulator
from .filters import meal_flag, period_mask, status_mask
from .pipeline import Aggregate, emit, read_pay
from .stats import cramers_v, share_diff_bootstrap
from .timeparse import DOW_LABELS, assign_regime, hour_to_bucket


def complete_grid(frame, dimensions):
    keys = list(dimensions)
    index = pd.MultiIndex.from_product(list(dimensions.values()), names=keys)
    return frame.set_index(keys).reindex(index, fill_value=0).reset_index()


def both_shops(frame):
    positive = frame.loc[frame.n.gt(0)].dropna(subset=["shop_id"])
    return set(positive.groupby("shop_id").G.nunique().loc[lambda values: values == 2].index)


def public_ci(frame, published_hours):
    out = frame.copy()
    out["note"] = ""
    out["status"] = "published"
    small = out.n_shops_used.lt(30)
    out.loc[small, ["ci_low", "ci_high"]] = np.nan
    out.loc[small, "note"] = "가맹점 수 부족"
    hidden = ~out.hour3.isin(published_hours)
    out.loc[hidden, ["diff", "ci_low", "ci_high"]] = np.nan
    out.loc[hidden, "status"] = "suppressed"
    return out


def _selected(frame, cfg):
    result = frame.loc[~frame.time_invalid & period_mask(frame, cfg["period"]) & status_mask(frame, cfg["status_filter"])].copy()
    result["G"] = np.where(meal_flag(result, cfg["meal_pay_values"]), "meal", "general")
    result["R"] = assign_regime(result, cfg["regime"])
    result["daytype"] = np.where(result.dow.ge(5), "weekend", "weekday")
    result["hour_bucket"] = result.hour.map(lambda h: hour_to_bucket(h, cfg["export"]["night_bucket"]))
    return result


def run(ctx):
    cfg = ctx.cfg
    regimes = sorted(set(cfg["regime"]["month_map"].values()) | {cfg["regime"]["default"]} |
                     {item["label"] for item in cfg["regime"].get("date_ranges", [])})
    daytypes = ["weekday", "weekend"]
    months = Aggregate(["ym", "G"])
    profiles = {"meal": Aggregate(["R", "dow", "hour_bucket"]), "general": Aggregate(["R", "dow", "hour"])}
    edges = {"meal": Aggregate(["hour_bucket", "daytype"]), "general": Aggregate(["hour", "daytype"])}
    days = {"meal": DistinctAccumulator(["hour_bucket", "daytype"]), "general": DistinctAccumulator(["hour", "daytype"])}
    block_keys = ["shop_id", "G", "R", "daytype", "hour3"]
    block = CountAccumulator(block_keys)
    customers = DistinctAccumulator(block_keys)
    all_effect = CountAccumulator(["G", "R", "daytype", "hour3"])
    night = Aggregate(["ym", "G"])
    night_days = DistinctAccumulator(["ym", "G"])
    dates = []
    invalid = empty_pay = total = 0
    for frame in read_pay(cfg):
        invalid += int(frame.time_invalid.sum())
        selected = _selected(frame, cfg)
        total += len(selected)
        empty_pay += int(selected.pay_gbn.isna().sum())
        months.update(selected)
        valid_shop = selected.dropna(subset=["shop_id"])
        block.update(valid_shop)
        customers.update(valid_shop, "cust_id")
        all_effect.update(selected)
        for group in ("meal", "general"):
            part = selected.loc[selected.G.eq(group)]
            profiles[group].update(part)
            edges[group].update(part)
            days[group].update(part, "ymd")
        late = selected.loc[selected.hour.isin(cfg["export"]["night_bucket"]["hours"])]
        night.update(late)
        night_days.update(late, "ymd")
        dates.append(selected.groupby(["G", "ymd"]).hour.agg(["min", "max"]).reset_index())
    if not total:
        raise ValueError("M2 모집단에 행이 없습니다")
    a = months.finalize()
    ctx.write_internal(a, "m2_month_group.csv")
    m0_path = ctx.export / "m0_month.csv"
    if m0_path.exists():
        old = pd.read_csv(m0_path)
        diff = a.loc[a.G.eq("meal"), ["ym", "n"]].merge(old[["ym", "n"]], on="ym", how="outer", suffixes=("_m2", "_m0"))
        diff["difference"] = diff.n_m2 - diff.n_m0
        ctx.write_internal(diff, "m2_m0_month_difference.csv")
    emit(ctx, a, "m2_month_group", ["ym", "G"], "mixed", margins=[["G"], ["ym"]])
    exported_profiles = {}
    buckets = sorted({hour_to_bucket(hour, cfg["export"]["night_bucket"]) for hour in range(24)})
    for group, aggregate in profiles.items():
        time_key = "hour_bucket" if group == "meal" else "hour"
        dims = {"R": regimes, "dow": list(range(7)), time_key: buckets if group == "meal" else list(range(24))}
        table = complete_grid(aggregate.finalize(), dims)
        table["dow"] = table.dow.map(lambda number: DOW_LABELS[int(number)])
        name = "m2_" + group + "_regime_dow_hour"
        ctx.write_internal(table, name + ".csv")
        exported_profiles[group] = emit(ctx, table, name, list(dims), group,
                                        margins=[["R"], ["R", "dow"], ["R", time_key]])
    counts = block.finalize()
    both = both_shops(counts)
    within = counts.loc[counts.shop_id.isin(both)].copy()
    raw_customers = pd.concat(customers.frames, ignore_index=True).drop_duplicates()
    raw_customers = raw_customers.loc[raw_customers.shop_id.isin(both)]
    ctx.write_internal(within, "m2_shop_block_counts.csv")
    exported_within = {}
    for group in ("meal", "general"):
        keys = ["R", "daytype", "hour3"]
        part = within.loc[within.G.eq(group)]
        table = part.groupby(keys).agg(n=("n", "sum"), n_shop=("shop_id", "nunique")).reset_index()
        unique = raw_customers.loc[raw_customers.G.eq(group)].groupby(keys).cust_id.nunique().rename("n_cust").reset_index()
        table = table.merge(unique, on=keys, how="left").fillna({"n_cust": 0})
        table = complete_grid(table, {"R": regimes, "daytype": daytypes, "hour3": list(range(8))})
        ctx.write_internal(table, "m2_within_shop_" + group + ".csv")
        exported_within[group] = emit(ctx, table, "m2_within_shop_" + group, keys, group,
                                      margins=[["R", "daytype"], ["R", "hour3"]], subset="both_shop")
    meal_total = int(within.loc[within.G.eq("meal"), "n"].sum())
    band = "<1,000" if meal_total < 1000 else "1,000-9,999" if meal_total < 10000 else "10,000+"
    meta = pd.DataFrame({"n_shop": [len(both)], "meal_rows_band": [band]})
    emit(ctx, meta, "m2_within_shop_meta", [], "diagnostic", n_col="n_shop", shop_col=None, cust_col=None,
         thresholds={"n_min": 3}, subset="both_shop_meta")
    started = time.perf_counter()
    ci_parts, effects = [], []
    all_counts = all_effect.finalize()
    shop_order = sorted(both)
    for regime in regimes:
        for daytype in daytypes:
            matrices = {}
            for group in ("meal", "general"):
                part = within.loc[within.G.eq(group) & within.R.eq(regime) & within.daytype.eq(daytype)]
                matrices[group] = part.pivot_table(index="shop_id", columns="hour3", values="n", aggfunc="sum").reindex(index=shop_order, columns=range(8), fill_value=0).fillna(0).to_numpy()
            ci = share_diff_bootstrap(matrices["meal"], matrices["general"], cfg["bootstrap"]["reps"], cfg["bootstrap"]["seed"])
            published_hours = set()
            if exported_within["meal"] is not None:
                visible = exported_within["meal"]
                mask = visible.R.eq(regime) & visible.daytype.eq(daytype) & visible.status.eq("published")
                published_hours = set(visible.loc[mask, "hour3"])
            ci = public_ci(ci, published_hours)
            ci["R"], ci["daytype"] = regime, daytype
            ci_parts.append(ci)
            general_within = exported_within["general"]
            general_safe = general_within is not None and general_within.loc[
                general_within.R.eq(regime) & general_within.daytype.eq(daytype), "status"].eq("published").all()
            safe = len(published_hours) == 8 and general_safe and all(value is not None and value.status.eq("published").all() for value in exported_profiles.values())
            effect = {"R": regime, "daytype": daytype, "status": "published" if safe else "suppressed",
                      "cramers_v_all": np.nan, "cramers_v_within": np.nan, "max_abs_diff_hour3": np.nan,
                      "max_abs_diff": np.nan, "ci_low": np.nan, "ci_high": np.nan, "note": "" if safe else "억제 칸 포함"}
            if safe:
                part = all_counts.loc[all_counts.R.eq(regime) & all_counts.daytype.eq(daytype)]
                matrix = part.pivot(index="G", columns="hour3", values="n").reindex(index=["meal", "general"], columns=range(8), fill_value=0).fillna(0).to_numpy()
                effect["cramers_v_all"] = cramers_v(matrix)
                effect["cramers_v_within"] = cramers_v(np.vstack([matrices["meal"].sum(0), matrices["general"].sum(0)]))
                if ci["diff"].notna().any():
                    peak = ci.loc[ci["diff"].abs().idxmax()]
                    effect.update(max_abs_diff_hour3=int(peak.hour3), max_abs_diff=abs(float(peak["diff"])), ci_low=peak.ci_low, ci_high=peak.ci_high)
            effects.append(effect)
    ci = pd.concat(ci_parts, ignore_index=True)
    ctx.write_internal(ci, "m2_within_shop_ci.csv")
    emit(ctx, ci, "m2_within_shop_ci", ["R", "daytype", "hour3"], "diagnostic", n_col=None, shop_col=None, cust_col=None)
    emit(ctx, pd.DataFrame(effects), "m2_effect_summary", ["R", "daytype"], "diagnostic", n_col=None, shop_col=None, cust_col=None)
    bootstrap_seconds = time.perf_counter() - started
    start = pd.Timestamp(str(cfg["period"]["start_ym"]) + "01")
    end = pd.Timestamp(str(cfg["period"]["end_ym"]) + "01") + pd.offsets.MonthEnd(0)
    calendar_days = pd.date_range(start, end, freq="D")
    denominator = {"weekday": int((calendar_days.weekday < 5).sum()), "weekend": int((calendar_days.weekday >= 5).sum())}
    for group in ("meal", "general"):
        key = "hour_bucket" if group == "meal" else "hour"
        table = edges[group].finalize().merge(days[group].finalize().rename(columns={"nunique": "days_with_any"}), on=[key, "daytype"], how="left")
        table = complete_grid(table, {key: buckets if group == "meal" else list(range(24)), "daytype": daytypes})
        table["days_in_period"] = table.daytype.map(denominator)
        ctx.write_internal(table, "m2_hour_edge_" + group + ".csv")
        emit(ctx, table, "m2_hour_edge_" + group, [key, "daytype"], group)
    table = a[["ym", "G"]].merge(night.finalize(), on=["ym", "G"], how="left").fillna(0)
    table = table.merge(night_days.finalize().rename(columns={"nunique": "days_with_23_05"}), on=["ym", "G"], how="left").fillna(0)
    table["days_in_month"] = table.ym.map(lambda ym: calendar.monthrange(int(ym) // 100, int(ym) % 100)[1])
    table = table.rename(columns={"n": "n_23_05"})
    ctx.write_internal(table, "m2_edge_by_month.csv")
    emit(ctx, table, "m2_edge_by_month", ["ym", "G"], "mixed", n_col="n_23_05")
    daily = pd.concat(dates).groupby(["G", "ymd"]).agg(first_hour=("min", "min"), last_hour=("max", "max")).reset_index()
    ctx.write_internal(daily.groupby("G")[["first_hour", "last_hour"]].quantile([0.01, 0.5, 0.99]).reset_index(), "m2_daily_edge_quantiles.csv")
    ctx.finish("M2", {"population_rows": total, "time_invalid": invalid, "empty_pay_gbn": empty_pay,
                      "both_shops": len(both), "bootstrap_seconds": bootstrap_seconds, "rejected_tables": ctx.rejected_tables})
    print("[M2] run=" + str(ctx.root))
    return 0
