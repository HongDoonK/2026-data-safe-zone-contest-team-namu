"""M1 discovery and literal preregistered gate calculations."""
from itertools import permutations

import numpy as np
import pandas as pd

from .config import meal_values_configured
from .filters import meal_flag, status_mask
from .pipeline import Aggregate, emit, read_pay
from .manifest import write_json
from .suppress import suppress, frame_digest


def band(value):
    if value < 50:
        return "<50"
    if value < 100:
        return "50-99"
    if value < 500:
        return "100-499"
    return None


def month_disclosure_plan(a, b, cfg):
    """Try exact A totals, then band A, then exclude unresolved B values."""
    options = dict(cfg["suppression"], zero_policy="show")
    totals = a.groupby("pay_gbn").n.sum()
    known = {(("pay_gbn",), (key,)): int(value) for key, value in totals.items()}
    _, first = suppress(b, ["ym", "pay_gbn"], margin_groups=[["pay_gbn"], ["ym"]], known_totals=known, **options)
    trace = [{"step": "exact_totals", "unresolved": bool(first["unresolved"])}]
    if not first["unresolved"]:
        return a.copy(), b.copy(), set(), trace
    excluded, banded = set(), set()
    for value, part in b.groupby("pay_gbn"):
        _, initial = suppress(part, ["ym", "pay_gbn"], margin_groups=[["pay_gbn"], ["ym"]],
                              known_totals={(("pay_gbn",), (value,)): int(totals[value])}, **options)
        if not initial["unresolved"]:
            continue
        banded.add(value)
        # The exact A total is no longer offered. The common suppress contract
        # still audits margins and can refuse; do not override that refusal.
        _, retry = suppress(part, ["ym", "pay_gbn"], margin_groups=[["pay_gbn"], ["ym"]], **options)
        trace.append({"step": "band_A_retry_B", "value": value, "unresolved": bool(retry["unresolved"])})
        if retry["unresolved"]:
            excluded.add(value)
    proposed = a.copy()
    proposed["note"] = ""
    proposed.loc[proposed.pay_gbn.isin(excluded), "note"] = "월별 표 제외(노출)"
    trace.append({"step": "exclude_unresolved_B", "values": sorted(excluded)})
    return proposed, b.loc[~b.pay_gbn.isin(excluded)].copy(), banded, trace


def export_values(ctx, a, banded):
    """Only weaken checked disclosure; independently check each partition."""
    if not banded:
        return emit(ctx, a, "m1_paygbn_values", ["pay_gbn", "card_pay_gbn"], "diagnostic")
    keys = ["pay_gbn", "card_pay_gbn"]
    small = a.loc[a.pay_gbn.isin(banded)].copy()
    large = a.loc[~a.pay_gbn.isin(banded)].copy()
    if any(band(value) is None for col in ("n", "n_shop", "n_cust") for value in small[col]):
        ctx.rejected_tables.append("m1_paygbn_values")
        return None
    note = small["note"].copy()
    for col in small:
        if col in ("n", "n_shop", "n_cust"):
            small[col] = small[col].map(band)
        elif col not in keys:
            small[col] = np.nan
    small["note"] = note
    small["status"] = "banded"
    safe_small, small_report = suppress(small, keys, n_col=None, shop_col=None, cust_col=None)
    safe_large, report = suppress(large, keys, **ctx.cfg["suppression"])
    if report["unresolved"]:
        ctx.rejected_tables.append("m1_paygbn_values")
        return None
    combined = pd.concat([safe_large, safe_small], ignore_index=True)
    report["frame_digest"] = frame_digest(combined)
    report["banded_partition"] = small_report
    from .pipeline import population
    meta = {"keys": keys, "metrics": [c for c in combined if c not in keys + ["status"]],
            "population": population(ctx.cfg, "diagnostic"), "population_kind": "diagnostic",
            "zero_policy": "mask", "time_only": True, "night_bucket_applied": False}
    # Existing public totals are checked by the writer, including band refusal.
    ctx.write_export(combined, "m1_paygbn_values", report, meta)
    return combined


def gate_branches(N, N_SHOP, MONTHS):
    # T2_child_meal_card.md section 4.2. Do not repair gaps/overlaps.
    result = {"branch_full": N >= 100000 and N_SHOP >= 500 and MONTHS >= 24,
              "branch_reduced": 20000 <= N < 100000 or (N >= 100000 and N_SHOP < 500),
              "branch_fb1": 2000 <= N < 20000 or MONTHS < 12,
              "branch_fb2": N < 2000 or N_SHOP < 50 or N == 0}
    result["branch_count_true"] = sum(result.values())
    result["branch_note"] = "" if result["branch_count_true"] == 1 else "규칙상 미정 — 사람 판단"
    return result


def month_grid(data):
    months = sorted(data.ym.dropna().unique())
    values = sorted(data.pay_gbn.unique())
    index = pd.MultiIndex.from_product([months, values], names=["ym", "pay_gbn"])
    return data.set_index(["ym", "pay_gbn"]).reindex(index, fill_value=0).reset_index()


def _month_index(value):
    value = int(value)
    return (value // 100) * 12 + value % 100


def transitions(values, customers, shops):
    top = values.groupby("pay_gbn", as_index=False).agg(n=("n", "sum"),
            first_ym=("first_ym", "min"), last_ym=("last_ym", "max")).nlargest(15, "n")
    rows = []
    for a, b in permutations(top.to_dict("records"), 2):
        av, bv = a["pay_gbn"], b["pay_gbn"]
        if pd.isna(a["last_ym"]) or pd.isna(b["first_ym"]):
            continue
        ac, bc = customers.get(av, set()), customers.get(bv, set())
        ash, bsh = shops.get(av, set()), shops.get(bv, set())
        nc, ns = len(ac & bc), len(ash & bsh)
        safe = nc >= 5 and ns >= 3
        rows.append({"a": av, "b": bv, "a_last_ym": a["last_ym"], "b_first_ym": b["first_ym"],
                     "gap_months": _month_index(b["first_ym"]) - _month_index(a["last_ym"]),
                     "cust_overlap": nc if safe else np.nan, "shop_overlap": ns if safe else np.nan,
                     "cust_overlap_share_a": nc / len(ac) if safe else np.nan,
                     "shop_overlap_share_a": ns / len(ash) if safe else np.nan})
    return pd.DataFrame(rows, columns=["a", "b", "a_last_ym", "b_first_ym", "gap_months",
                                      "cust_overlap", "shop_overlap", "cust_overlap_share_a", "shop_overlap_share_a"])


def run(ctx):
    cfg = ctx.cfg
    values = Aggregate(["pay_gbn", "card_pay_gbn"])
    monthly = Aggregate(["ym", "pay_gbn"])
    detail = []
    gates = {mode: Aggregate([]) for mode in ("all", "complete_only", "exclude_cancel")}
    gate_months = {mode: set() for mode in gates}
    denominators = {mode: 0 for mode in gates}
    rows_read = invalid = 0
    configured = meal_values_configured(cfg)
    for frame in read_pay(cfg):
        rows_read += len(frame)
        invalid += int(frame.time_invalid.sum())
        frame[["pay_gbn", "card_pay_gbn"]] = frame[["pay_gbn", "card_pay_gbn"]].fillna("<EMPTY>")
        values.update(frame)
        valid = frame.loc[~frame.time_invalid]
        monthly.update(valid)
        detail.append(valid.groupby(["pay_gbn", "card_pay_gbn", "ym", "month"], dropna=False).size().rename("n").reset_index())
        if configured:
            meal = meal_flag(frame, cfg["meal_pay_values"])
            for mode in gates:
                selected = status_mask(frame, dict(cfg["status_filter"], mode=mode))
                denominators[mode] += int(selected.sum())
                subset = frame.loc[selected & meal]
                gates[mode].update(subset)
                gate_months[mode].update(subset.ym.dropna().tolist())
    if not rows_read:
        raise ValueError("M1 결제 파일에 행이 없습니다")
    a = values.finalize().sort_values("n", ascending=False)
    facts = pd.concat(detail, ignore_index=True)
    for column in ("first_ym", "last_ym", "months_observed", "vacation_share"):
        a[column] = np.nan
    for index, row in a.iterrows():
        part = facts.loc[facts.pay_gbn.eq(row.pay_gbn) & facts.card_pay_gbn.eq(row.card_pay_gbn)]
        a.loc[index, "first_ym"] = part.ym.min()
        a.loc[index, "last_ym"] = part.ym.max()
        a.loc[index, "months_observed"] = part.ym.nunique()
        a.loc[index, "vacation_share"] = part.loc[part.month.isin([1, 2, 8]), "n"].sum() / row.n
    a["len_chars"] = a.pay_gbn.str.len()
    b = month_grid(monthly.finalize())
    ctx.write_internal(a, "m1_paygbn_values.csv")
    ctx.write_internal(b, "m1_paygbn_month.csv")
    # A is not finalized before B. Fixed-domain conflicts are recorded as
    # approved refusal, never relabelled as a successful export.
    a, candidate_b, banded, trace = month_disclosure_plan(a, b, cfg)
    write_json(ctx.internal / "m1_disclosure_plan.json", trace)
    published_b = None
    if len(candidate_b):
        published_b = emit(ctx, candidate_b, "m1_paygbn_month", ["ym", "pay_gbn"], "diagnostic",
                           zero_policy="show", margins=[["pay_gbn"], ["ym"]],
                           subset={"included_values": sorted(candidate_b.pay_gbn.unique().tolist())})
    else:
        ctx.rejected_tables.append("m1_paygbn_month")
    if published_b is not None:
        wide = published_b.pivot(index="ym", columns="pay_gbn", values="n").reset_index()
        # Every numeric cell comes verbatim from the checked long table.
        emit(ctx, wide, "m1_paygbn_month_wide", ["ym"], "diagnostic", n_col=None,
             shop_col=None, cust_col=None, subset="checked_month_wide")
    export_values(ctx, a, banded)
    # Reuse exact de-duplicated sets already accumulated; only top 15 survive.
    top = set(a.groupby("pay_gbn").n.sum().nlargest(15).index)
    def sets(accumulator, column):
        combined = pd.concat(accumulator.frames, ignore_index=True)
        combined = combined.loc[combined.pay_gbn.isin(top), ["pay_gbn", column]].drop_duplicates()
        return {key: set(group[column]) for key, group in combined.groupby("pay_gbn")}
    c = transitions(a, sets(values.cust, "cust_id"), sets(values.shop, "shop_id"))
    ctx.write_internal(c, "m1_value_transitions.csv")
    candidates = c.loc[c.gap_months.between(-1, 2)].copy()
    if len(candidates):
        emit(ctx, candidates, "m1_value_transitions", ["a", "b"], "diagnostic", n_col=None,
             shop_col=None, cust_col=None, subset="transition_candidates")
    gate_rows = []
    if configured:
        for mode, aggregate in gates.items():
            numbers = aggregate.finalize().iloc[0]
            months = gate_months[mode]
            item = {"status_mode": mode, "N": int(numbers.n), "N_SHOP": int(numbers.n_shop),
                    "MONTHS": len(months), "FIRST_YM": min(months) if months else np.nan,
                    "LAST_YM": max(months) if months else np.nan,
                    "share_of_all_rows": numbers.n / denominators[mode] if denominators[mode] else np.nan}
            item.update(gate_branches(item["N"], item["N_SHOP"], item["MONTHS"]))
            gate_rows.append(item)
        gate = pd.DataFrame(gate_rows)
        ctx.write_internal(gate, "m1_gate.csv")
        # Small synthetic or rare populations must not bypass suppression via
        # uppercase metric names. Share is internal as requested.
        export_gate = gate.drop(columns=["share_of_all_rows"])
        emit(ctx, export_gate, "m1_gate", ["status_mode"], "diagnostic", n_col="N",
             shop_col="N_SHOP", cust_col=None, subset="gate")
    else:
        print("meal_pay_values: 미설정 → 게이트 계산 건너뜀")
    extra = {"rows_read": rows_read, "time_invalid": invalid, "values": int(a.pay_gbn.nunique()),
             "gate_skipped": not configured, "rejected_tables": ctx.rejected_tables,
             "incomplete": []}
    ctx.finish("M1", extra)
    print("[M1] 지급구분 값 %d종; run=%s" % (extra["values"], ctx.root))
    return extra
