"""M0 exact reference reproduction without automatic filter selection."""
import json
from pathlib import Path

import pandas as pd

from .filters import meal_flag, status_mask
from .pipeline import Aggregate, emit, read_pay
from .timeparse import DOW_LABELS, hour_to_bucket


def compare_months(frame, records):
    reference = pd.DataFrame(records).copy()
    reference["ym"] = reference.ym.astype(str).str.replace("-", "", regex=False).astype(int)
    actual = frame.copy()
    actual["ym"] = actual.ym.astype(int)
    joined = reference.merge(actual, on="ym", how="outer", suffixes=("_reference", "_actual"), indicator=True)
    result = {"reference_months": len(reference), "actual_months": len(actual)}
    for metric in ("n", "n_shop", "n_cust"):
        equal = joined[metric + "_reference"].eq(joined[metric + "_actual"])
        result[metric + "_months_equal"] = int(equal.sum())
    result["total_diff"] = int(actual.n.sum() - reference.n.sum())
    result["matched"] = bool(joined._merge.eq("both").all() and all(result[m + "_months_equal"] == len(reference) for m in ("n", "n_shop", "n_cust")))
    return result


def _references(cfg):
    refs = cfg.get("reference_exports") or {}
    config_base = Path(cfg["_config_path"]).resolve().parent
    if config_base.name == "config":
        config_base = config_base.parent
    result = {}
    for name, value in refs.items():
        if value is not None:
            result[name] = json.loads((config_base / value).read_text(encoding="utf-8-sig"))
    return result


def run(ctx):
    cfg = ctx.cfg
    modes = ("all", "complete_only", "exclude_cancel")
    groups = {mode: {"month": Aggregate(["ym"]), "hour": Aggregate(["dow", "hour"]),
                     "night": Aggregate(["dow", "hour_bucket"])} for mode in modes}
    invalid = meal_invalid = 0
    distributions = []
    for frame in read_pay(cfg, ["shop_id", "cust_id", "pay_gbn", "card_pay_gbn", "dest_pay_gbn", "app_time"]):
        meal = meal_flag(frame, cfg["meal_pay_values"])
        invalid += int(frame.time_invalid.sum())
        meal_invalid += int((meal & frame.time_invalid).sum())
        for col in ("card_pay_gbn", "dest_pay_gbn"):
            counts = frame.loc[meal, col].fillna("<EMPTY>").value_counts().rename("n").rename_axis("value").reset_index()
            counts["column"] = col
            distributions.append(counts)
        valid = frame.loc[meal & ~frame.time_invalid].copy()
        valid["hour_bucket"] = valid.hour.map(lambda h: hour_to_bucket(h, cfg["export"]["night_bucket"]))
        for mode in modes:
            selected = valid.loc[status_mask(valid, dict(cfg["status_filter"], mode=mode))]
            for aggregate in groups[mode].values():
                aggregate.update(selected)
    references = _references(cfg)
    month_ref = references.get("export_0911_month")
    week_ref = references.get("export_0911_week_hour")
    comparisons = []
    tables = {}
    for mode in modes:
        tables[mode] = {key: agg.finalize() for key, agg in groups[mode].items()}
        for key in ("hour", "night"):
            tables[mode][key]["dow"] = tables[mode][key].dow.map(lambda n: DOW_LABELS[int(n)])
        ctx.write_internal(tables[mode]["month"], "m0_month_" + mode + ".csv")
        ctx.write_internal(tables[mode]["hour"], "m0_dow_hour_" + mode + ".csv")
        if month_ref is not None:
            comparison = compare_months(tables[mode]["month"], month_ref)
            comparison["status_mode"] = mode
            if week_ref is not None:
                # Compare only originally public cells; hidden actuals stay internal.
                published = pd.DataFrame(week_ref).dropna(subset=["n"])
                joined = published.merge(tables[mode]["hour"], on=["dow", "hour"], how="left", suffixes=("_reference", "_actual"))
                comparison["week_public_match"] = bool(joined.n_reference.eq(joined.n_actual).all())
                comparison["week_hidden_sum_diff"] = int(tables[mode]["month"].n.sum() - joined.n_actual.sum())
                comparison["matched"] = comparison["matched"] and comparison["week_public_match"]
            comparisons.append(comparison)
            print("status=%s 월 일치 %s/%s 총합 차 %s" % (mode, comparison["n_months_equal"], comparison["reference_months"], comparison["total_diff"]))
    ctx.write_internal(pd.DataFrame(comparisons), "m0_reproduce_compare.csv")
    if distributions:
        ctx.write_internal(pd.concat(distributions).groupby(["column", "value"], as_index=False).n.sum(), "m0_meal_values.csv")
    matches = [item["status_mode"] for item in comparisons if item["matched"]]
    if month_ref is not None and len(matches) != 1:
        print("재현 실패" if not matches else "재현 조합 불확정")
        ctx.finish("M0", {"matches": matches, "time_invalid": invalid, "meal_time_invalid": meal_invalid, "exit_code": 2})
        return 2
    selected = matches[0] if matches else cfg["status_filter"]["mode"]
    if month_ref is None:
        print("reference 없음: 비교 생략, 설정한 상태 필터로 표 생성")
    subset = {"period": "all", "status_mode": selected}
    observed_months = tables[selected]["month"].ym
    if selected == cfg["status_filter"]["mode"] and observed_months.between(int(cfg["period"]["start_ym"]), int(cfg["period"]["end_ym"])).all():
        subset = None  # Proved identical row population, not a guessed alias.
    emit(ctx, tables[selected]["month"], "m0_month", ["ym"], subset=subset)
    night = tables[selected]["night"]
    buckets = sorted({hour_to_bucket(h, cfg["export"]["night_bucket"]) for h in range(24)})
    index = pd.MultiIndex.from_product([DOW_LABELS, buckets], names=["dow", "hour_bucket"])
    night = night.set_index(["dow", "hour_bucket"]).reindex(index, fill_value=0).reset_index()
    ctx.write_internal(night, "m0_dow_hour_night.csv")
    emit(ctx, night, "m0_dow_hour_night", ["dow", "hour_bucket"], subset=subset)
    with (ctx.export / "filter_definition.txt").open("a", encoding="utf-8") as handle:
        handle.write("\n1차 반출 재현 조합: %s; reference_available=%s; M0 period=all\n" % (selected, month_ref is not None))
    ctx.finish("M0", {"matches": matches, "selected_mode": selected, "time_invalid": invalid,
                      "meal_time_invalid": meal_invalid, "rejected_tables": ctx.rejected_tables})
    print("[M0] run=" + str(ctx.root))
    return 0
