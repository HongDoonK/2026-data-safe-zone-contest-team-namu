"""M4 fixed publication ladder; geography means shop location."""
import numpy as np
import pandas as pd

from .m2 import _selected
from .m3 import clean_shops, join_shops, read_shops
from .manifest import write_json
from .pipeline import Aggregate, emit, population, read_pay
from .suppress import exposure_ranges, frame_digest, suppress

ORDER = ("L1", "L2", "L4", "L3", "L5")
LEVEL_KEYS = {"L1": ["dong", "R", "hour3"], "L2": ["dong", "R"], "L3": ["dong"],
              "L4": ["gungu", "R", "hour3"], "L5": ["gungu", "R"]}


def spatial_keys(frame):
    out = frame.copy()
    out["dong"] = out.gungu.astype(str) + "|" + out.dong.astype(str)
    return out


def select_level(shares, threshold):
    return next((level for level in ORDER if shares.get(level, float("nan")) >= threshold), "none")


def publishability(frame, region, thresholds=None):
    limits = thresholds or {"n_min": 5, "shop_min": 3, "cust_min": 5}
    cells = frame.loc[frame.n.gt(0)]
    passed = cells.n.ge(limits["n_min"]) & cells.n_shop.ge(limits["shop_min"]) & cells.n_cust.ge(limits["cust_min"])
    total = cells.n.sum()
    missing = cells[region].astype(str).str.contains("<NOT_IN_TABLE>|<EMPTY>", regex=True)
    return {"cells_total": len(cells), "cells_pass": int(passed.sum()),
            "cell_pass_share": float(passed.mean()) if len(cells) else np.nan,
            "count_pass_share": float(cells.loc[passed, "n"].sum() / total) if total else np.nan,
            "not_in_table_share": float(cells.loc[missing, "n"].sum() / total) if total else np.nan}


def add_lq(frame, keys):
    region = "dong" if "dong" in keys else "gungu"
    conditions = [key for key in keys if key != region]
    counts = frame.pivot(index=keys, columns="G", values="n").reindex(columns=["meal", "general"], fill_value=0).apply(pd.to_numeric).fillna(0).reset_index()
    counts["all"] = counts.meal + counts.general
    counts["share_meal"] = counts.meal / counts["all"].replace(0, np.nan)
    eligible = ~counts[region].astype(str).str.contains("<NOT_IN_TABLE>|<EMPTY>", regex=True)
    if conditions:
        totals = counts.loc[eligible].groupby(conditions)[["meal", "all"]].sum()
        totals["total_share"] = totals.meal / totals["all"].replace(0, np.nan)
        counts = counts.merge(totals[["total_share"]], on=conditions, how="left")
    else:
        denominator = counts.loc[eligible, "all"].sum()
        counts["total_share"] = counts.loc[eligible, "meal"].sum() / denominator if denominator else np.nan
    counts["lq"] = counts.share_meal / counts.total_share.replace(0, np.nan)
    return frame.merge(counts[keys + ["share_meal", "lq"]], on=keys, how="left", validate="many_to_one")


def _meta(ctx, keys, kind="mixed"):
    return {"keys": keys, "metrics": ["n", "n_shop", "n_cust"], "population": population(ctx.cfg, kind),
            "population_kind": kind, "zero_policy": "mask", "time_only": False,
            "night_bucket_applied": False, "coverage_complete": True,
            "fixed_keys": {"G": kind} if kind in ("meal", "general") else {}}


def _spatial_prior_safe(ctx, checked, meta):
    """Audit gungu margins against composite dong keys before writing."""
    if "dong" not in meta["keys"]:
        return True
    for entry in ctx.totals:
        if entry["population"] != meta["population"] or entry["metric"] != "n":
            continue
        dimensions = dict(zip(entry["keys"], entry["values"]))
        dimensions.update(entry.get("fixed_keys", {}))
        if "gungu" not in dimensions:
            continue
        fixed = meta.get("fixed_keys", {})
        if any(key not in dimensions or dimensions[key] != value for key, value in fixed.items()):
            continue
        mask = pd.Series(True, index=checked.index)
        applicable = True
        for key, value in dimensions.items():
            if key in fixed:
                continue
            if key == "gungu":
                mask &= checked.dong.astype(str).str.split("|", n=1, regex=False).str[0].eq(str(value))
            elif key in checked:
                mask &= checked[key].eq(value)
            else:
                applicable = False
                break
        if not applicable:
            continue
        part = checked.loc[mask]
        hidden = part.status.eq("suppressed")
        residual = int(entry["total"] - pd.to_numeric(part.loc[~hidden, "n"]).sum())
        try:
            bounds = exposure_ranges(residual, int(hidden.sum()), 0, ctx.cfg["suppression"]["n_min"] - 1)
        except ValueError:
            return False
        if any(bound != (0, ctx.cfg["suppression"]["n_min"] - 1) for bound in bounds):
            return False
    return True


def _checked_counts(ctx, frame, keys, kind="mixed", extra_totals=None):
    meta = _meta(ctx, keys, kind)
    known = ctx.known_totals(meta)
    for key, value in (extra_totals or {}).items():
        if key in known and known[key] != value:
            raise ValueError("M4 공개 예정 합계가 기공개 합계와 모순됩니다")
        known[key] = value
    out, report = suppress(frame, keys, known_totals=known, **ctx.cfg["suppression"])
    if not _spatial_prior_safe(ctx, out, meta):
        report["unresolved"].append({"reason": "prior_spatial_total_narrows"})
    return out, report, meta


def export_map_candidate(ctx, level, frames):
    """Derive shares only from entirely public checked count tables."""
    frame = frames[level]
    keys = LEVEL_KEYS[level]
    if level == "L1":
        if not frames["L2"].groupby(LEVEL_KEYS["L2"]).G.nunique().eq(2).all():
            return False, "share_counterpart_missing"
        coarse, coarse_report, coarse_meta = _checked_counts(ctx, frames["L2"], LEVEL_KEYS["L2"] + ["G"])
        if coarse_report["unresolved"] or not coarse.status.eq("published").all():
            return False, "coarse_share_counts_not_fully_public"
        coarse_meal = coarse.loc[coarse.G.eq("meal")]
        known = {(("dong", "R"), (row.dong, row.R)): int(row.n) for row in coarse_meal.itertuples()}
        meal = frame.loc[frame.G.eq("meal")].drop(columns=["G"])
        checked, report, meta = _checked_counts(ctx, meal, keys, "meal", known)
        if report["unresolved"]:
            return False, "L1_count_exposure"
        shared = add_lq(coarse, LEVEL_KEYS["L2"])
        shared = shared.loc[shared.G.eq("meal"), ["dong", "R", "share_meal", "lq"]]
        # Counts have been checked, and all coarse counts are public-safe.
        # L1's hidden cells also passed these exact coarse totals above.
        ctx.write_export(checked, "m4_mapunit_meal", report, meta)
        emit(ctx, shared, "m4_mapunit_share", ["dong", "R"], "diagnostic", n_col=None,
             shop_col=None, cust_col=None, subset="L1_checked_coarse_shares")
        return True, float(pd.to_numeric(checked.n).sum() / meal.n.sum()) if meal.n.sum() else np.nan
    if not frame.groupby(keys).G.nunique().eq(2).all():
        return False, "share_counterpart_missing"
    checked, report, meta = _checked_counts(ctx, frame, keys + ["G"])
    if report["unresolved"] or not checked.status.eq("published").all():
        return False, "share_denominator_not_fully_public"
    # Shares are deterministic functions of the same already checked public
    # n cells. No hidden value or raw denominator enters this derivation.
    output = add_lq(checked, keys)
    report["frame_digest"] = frame_digest(output)
    report["derivation"] = "share_meal/lq from fully published n only"
    meta["metrics"] += ["share_meal", "lq"]
    ctx.write_export(output, "m4_mapunit", report, meta)
    return True, 1.0


def run(ctx):
    cfg = ctx.cfg
    print("[M4] 지역 = 가맹점 소재지 기준")
    raw = read_shops(cfg)
    clean, duplicates = clean_shops(raw)
    accumulators = {level: Aggregate(keys + ["G"]) for level, keys in LEVEL_KEYS.items()}
    gungu = Aggregate(["gungu", "R", "G"])
    for frame in read_pay(cfg):
        joined = spatial_keys(join_shops(_selected(frame, cfg), clean))
        gungu.update(joined)
        for aggregate in accumulators.values():
            aggregate.update(joined)
    frames = {level: aggregate.finalize() for level, aggregate in accumulators.items()}
    records = []
    for level, frame in frames.items():
        ctx.write_internal(frame, "m4_" + level + "_counts.csv")
        region = LEVEL_KEYS[level][0]
        for group in ("meal", "general"):
            records.append(dict(publishability(frame.loc[frame.G.eq(group)], region, cfg["suppression"]), level=level, G=group))
    g1 = pd.DataFrame(records)
    shares = dict(zip(g1.loc[g1.G.eq("meal"), "level"], g1.loc[g1.G.eq("meal"), "count_pass_share"]))
    decisions = []
    for threshold in cfg["publish_rule"]["count_share_thresholds"]:
        level = select_level(shares, threshold)
        decisions.append({"threshold": threshold, "selected_level": level,
                          "count_pass_share": shares.get(level, np.nan)})
    primary = select_level(shares, cfg["publish_rule"]["primary"])
    emit(ctx, gungu.finalize(), "m4_gungu_regime", ["gungu", "R", "G"], "mixed", margins=[["gungu"], ["R", "G"]])
    attempts, actual, after = [], "none", np.nan
    if primary != "none":
        for level in ORDER[ORDER.index(primary):]:
            success, detail = export_map_candidate(ctx, level, frames)
            attempts.append({"level": level, "success": success, "detail": detail})
            if success:
                actual, after = level, detail
                break
    if actual == "none":
        ctx.rejected_tables.append("m4_mapunit")
    for decision in decisions:
        decision["exported_level_after_secondary"] = actual if decision["threshold"] == cfg["publish_rule"]["primary"] else "not_requested"
    g1["count_pass_share_after_secondary"] = np.nan
    if actual != "none":
        g1.loc[g1.level.eq(actual) & g1.G.eq("meal"), "count_pass_share_after_secondary"] = after
    ctx.write_internal(g1, "m4_g1_publishability.csv")
    emit(ctx, g1, "m4_g1_publishability", ["level", "G"], "diagnostic", n_col=None, shop_col=None, cust_col=None)
    emit(ctx, pd.DataFrame(decisions), "m4_map_unit_decision", ["threshold"], "diagnostic", n_col=None, shop_col=None, cust_col=None)
    names = clean[["gungu", "dong"]].fillna("<EMPTY>").drop_duplicates()
    names["len_chars"] = names.dong.str.len()
    ctx.write_internal(names, "m4_dong_names.csv")
    shops = clean.copy()
    shops[["gungu", "dong"]] = shops[["gungu", "dong"]].fillna("<EMPTY>")
    shops["is_y"] = shops.child_able.eq("Y").astype(int)
    c = shops.groupby(["gungu", "dong"]).agg(n_shop_total=("shop_id", "nunique"), n_shop_child_able_y=("is_y", "sum")).reset_index()
    c.loc[c.n_shop_child_able_y.between(1, 2), "n_shop_child_able_y"] = np.nan
    emit(ctx, c, "m4_dong_able", ["gungu", "dong"], "shop", n_col="n_shop_total", shop_col=None, cust_col=None,
         margins=[["gungu"]], thresholds={"n_min": 3})
    with (ctx.export / "filter_definition.txt").open("a", encoding="utf-8") as handle:
        handle.write("\n지역 = 가맹점 소재지 기준. LQ total은 <NOT_IN_TABLE>·<EMPTY> 제외.\n")
    write_json(ctx.internal / "m4_map_attempts.json", attempts)
    ctx.finish("M4", {"primary_level": primary, "exported_level": actual, "rejected_tables": ctx.rejected_tables,
                      "dup_id_excluded_shops": int(duplicates.shop_id.nunique())})
    print("[M4] 주 단위=%s; 반출 단위=%s; run=%s" % (primary, actual, ctx.root))
    return 0
