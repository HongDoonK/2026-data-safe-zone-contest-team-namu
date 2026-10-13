"""Independent reference: csv row iteration, dictionaries, sets and NumPy.

No exec, no imports of cell code, no pandas chunk/groupby aggregation.
Pandas only constructs result tables; invalid amounts are parsed by float().
"""
import csv
import math
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

NUM = "TOT_AMT ETC_AMT DISC_AMT MILEAGE_AMT CARD_APP_AMT PACK_DISC_AMT SHOP_DISC_AMT GOOD_DISC_AMT CHILD_DISC_AMT".split()


def number(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return float("nan")


def table(mapping, columns, multi=False):
    keys = sorted(mapping)
    index = pd.MultiIndex.from_tuples(keys) if multi and keys else (pd.MultiIndex.from_arrays([[], []]) if multi else pd.Index(keys))
    return pd.DataFrame([mapping[k] for k in keys], index=index, columns=columns)


def series(mapping, name=None, multi=False):
    return table({k: [v] for k, v in mapping.items()}, [name], multi).iloc[:, 0]


def calculate(pay, shop):
    with open(str(shop), encoding="utf-8", newline="") as stream:
        shop_cols = next(csv.reader(stream))
    with open(str(pay), encoding="utf-8", newline="") as stream:
        pay_cols = next(csv.reader(stream))
    with open(str(shop), encoding="utf-8", newline="") as stream:
        shops = [{k: v.strip() for k, v in r.items()} for r in csv.DictReader(stream)]
    dongs = {r["SHOP_ID"]: r["GUNGU_NM"] + "|" + r["DONG_NM"] for r in shops}
    reg_counts = defaultdict(lambda: [0, 0])
    for r in shops:
        key = dongs[r["SHOP_ID"]]
        reg_counts[key][0] += 1
        reg_counts[key][1] += int(r["CHILD_ABLE_YN"] == "Y")
    monthly = defaultdict(lambda: [0, 0])
    meal_cust, pre_cust = set(), defaultdict(set)
    meal_rows, regime_counts = Counter(), Counter()
    group_n, group_shops, group_custs = Counter(), defaultdict(set), defaultdict(set)
    dong_n, dong_shops, dong_custs = Counter(), defaultdict(set), defaultdict(set)
    shop_general, dong_general, shop_meal = Counter(), Counter(), Counter()
    numeric, tot_custs, tot_bins, disc_bins, general_bins = [], defaultdict(set), Counter(), Counter(), Counter()
    month_bins = Counter()
    missing, meal_count = 0, 0
    with open(str(pay), encoding="utf-8", newline="") as stream:
        for raw in csv.DictReader(stream):
            r = {k: v.strip() for k, v in raw.items()}
            code, ym, sid, cid = r["PAY_GBN"], r["CARD_APP_TIME"][:6], r["SHOP_ID"], r["CUST_ID"]
            discount = number(r["CHILD_DISC_AMT"])
            monthly[code, ym][0] += 1
            monthly[code, ym][1] += int(discount > 0)
            if code == "아동급식카드":
                meal_cust.add(cid)
            if ym < "202306":
                pre_cust[code].add(cid)
            if not (r["CARD_PAY_GBN"] == "완료" and "202306" <= ym <= "202506"):
                continue
            dong = dongs.get(sid)
            if code != "아동급식카드":
                shop_general[sid] += 1
                if dong is not None:
                    dong_general[dong] += 1
                total = number(r["TOT_AMT"])
                if not math.isnan(total):
                    general_bins[math.floor(total / 500) * 500] += 1
                continue
            meal_count += 1
            shop_meal[sid] += 1
            regime = {"01": "방학", "02": "방학", "08": "방학", "07": "전환", "12": "전환"}.get(ym[4:6], "학기")
            regime_counts[regime] += 1
            meal_rows[sid, cid, r["CARD_APP_TIME"], regime, dong] += 1
            if dong is None:
                missing += 1
            else:
                key = dong, regime
                group_n[key] += 1
                group_shops[key].add(sid)
                group_custs[key].add(cid)
                dong_n[dong] += 1
                dong_shops[dong].add(sid)
                dong_custs[dong].add(cid)
            nums = [number(r[col]) for col in NUM]
            nums = [0.0 if math.isnan(v) else v for v in nums]
            numeric.append(nums)
            tbin = math.floor(nums[0] / 500) * 500
            dbin = math.floor(nums[-1] / 500) * 500
            tot_bins[tbin] += 1
            disc_bins[dbin] += 1
            tot_custs[tbin].add(cid)
            month_bins[ym, tbin] += 1
    # P0 tables are built from independent dictionary accumulators.
    code_totals = defaultdict(lambda: [0, 0])
    pre_dict = {}
    pre_months, pre_codes = set(), set()
    for (code, ym), vals in monthly.items():
        code_totals[code][0] += vals[0]
        code_totals[code][1] += vals[1]
        if ym < "202306" and vals[1] > 0:
            pre_dict[ym, code] = vals[1]
            pre_months.add(ym)
            pre_codes.add(code)
    pre = pd.DataFrame([[pre_dict.get((ym, code), 0) for code in sorted(pre_codes)] for ym in sorted(pre_months)],
                       index=sorted(pre_months), columns=sorted(pre_codes))
    p2_counts, year_counts = {}, defaultdict(Counter)
    codes2 = ["대구로페이", "카드", "행복페이"]
    for (code, ym), vals in monthly.items():
        if code in codes2:
            p2_counts[ym, code] = vals[0]
            year_counts[code, ym[:4]][ym[4:6] in ["01", "02", "08"]] += vals[0]
    p2_months = sorted({ym for ym, code in p2_counts})
    p2 = pd.DataFrame([[p2_counts.get((ym, code), 0) for code in codes2] for ym in p2_months], index=p2_months, columns=codes2)
    years = table({k: [v.get(False, np.nan), v.get(True, np.nan)] for k, v in year_counts.items()}, [False, True], True)
    overlap = table({code: [len(custs), len(custs & meal_cust), round(len(custs & meal_cust)/len(custs), 3)]
                     for code, custs in pre_cust.items()}, ["pre_cust", "also_meal", "share"])
    reg = table(reg_counts, ["shops", "able_y"])
    t = table({key: [n, len(group_shops[key]), len(group_custs[key])] for key, n in group_n.items()}, ["n", "n_shop", "n_cust"], True)
    bad_values = {key: n < 5 or len(group_shops[key]) < 3 or len(group_custs[key]) < 5 for key, n in group_n.items()}
    tt = table({key: [np.nan]*3 if bad_values[key] else vals for key, vals in
                {key: [n, len(group_shops[key]), len(group_custs[key])] for key, n in group_n.items()}.items()}, ["n", "n_shop", "n_cust"], True)
    k = Counter()
    for (dong, regime), flag in bad_values.items():
        k[dong] += int(flag)
    global_ratio = sum(dong_n.values()) / sum(dong_general.values())
    total_rows, bad2 = {}, {}
    for dong, (nshops, able_y) in reg_counts.items():
        n, ns, nc = dong_n[dong], len(dong_shops[dong]), len(dong_custs[dong])
        gen = dong_general.get(dong, np.nan)
        lq = round(n / gen / global_ratio, 3) if gen else (float("inf") if n else np.nan)
        flag = n < 5 or ns < 3 or nc < 5 or k[dong] == 1
        bad2[dong] = flag
        vals = [nshops, able_y, n, ns, nc, gen, round(able_y/nshops, 3), lq]
        if flag:
            for i in [2, 3, 4, 7]:
                vals[i] = np.nan
        if nshops < 3:
            for i in [0, 1, 5, 6]:
                vals[i] = np.nan
        total_rows[dong] = vals
    tot = table(total_rows, ["shops", "able_y", "n", "n_shop", "n_cust", "gen", "able_share", "lq"])
    selected = [r for r in shops if r["CHILD_ABLE_YN"] == "Y" and shop_general[r["SHOP_ID"]] > 0 and shop_meal[r["SHOP_ID"]] == 0]
    cross = Counter((r["STORE_STATUS"], r["SERVICE_CLOSED"]) for r in selected)
    u2_counts = Counter((r["GUNGU_NM"], r["STORE_STATUS"]) for r in selected)
    u2_gu, u2_status = sorted({x[0] for x in u2_counts}), sorted({x[1] for x in u2_counts})
    e2 = pd.DataFrame([[u2_counts[g, s] if u2_counts[g, s] >= 3 else np.nan for s in u2_status] for g in u2_gu], index=u2_gu, columns=u2_status)
    data = np.array(numeric, dtype=float)
    describe = pd.DataFrame(np.vstack([np.full(len(NUM), len(data)), data.mean(axis=0), data.std(axis=0, ddof=1),
                                       data.min(axis=0), np.quantile(data, .25, axis=0), np.quantile(data, .5, axis=0),
                                       np.quantile(data, .75, axis=0), data.max(axis=0)]).round(0),
                            index=["count", "mean", "std", "min", "25%", "50%", "75%", "max"], columns=NUM)
    dt, da, dd = data[:, 0], data[:, 4], data[:, -1]
    hm_values = {key: [n, len(tot_custs[key])] for key, n in tot_bins.items()}
    amount_bad, hist = {}, {}
    for key in sorted(set(tot_bins) | set(general_bins)):
        n, nc = tot_bins.get(key, np.nan), len(tot_custs[key]) if key in tot_bins else np.nan
        flag = n < 5 or nc < 5
        amount_bad[key] = flag
        hist[key] = [np.nan if flag else n, np.nan if flag else nc, general_bins.get(key, np.nan)]
    top = {}
    for ym in sorted({k[0] for k in month_bins}):
        candidates = [(n, b) for (month, b), n in month_bins.items() if month == ym]
        max_n = max(n for n, b in candidates)
        winners = [b for n, b in candidates if n == max_n]
        if len(winners) != 1:
            raise ValueError("SYNTHETIC A4 fixture must have one modal bin per month")
        top[ym] = [winners[0], max_n]
    snapshots = {
        "S1": {"pay_columns": pay_cols, "shop_columns": shop_cols},
        "P1": {"monthly": table(monthly, ["n", "n_disc"], True), "codes": table(code_totals, ["n", "n_disc"]), "pre": pre},
        "P1b": {"monthly_meal": table({ym: vals for (code, ym), vals in monthly.items() if code == "아동급식카드"}, ["n", "n_disc"])},
        "P2": {"pivot": p2, "year_vac": years}, "P3": {"overlap": overlap},
        "M1": {"reg": reg, "empty_dong": sum(r["DONG_NM"] == "" for r in shops)},
        "M2": {"count": meal_count, "missing": missing, "dongs": len(dong_n),
               "regimes": series(regime_counts, "count"), "rows": series(meal_rows, multi=True)},
        "M3": {"gp": series(shop_general, "count"), "g": series(dong_general, "count")},
        "M4": {"t": t, "tt": tt, "bad": series(bad_values), "k": series(dict(k)), "regime_order": sorted(regime_counts)},
        "M5": {"tot": tot, "bad2": series(bad2)},
        "M6": {"selected_ids": sorted(r["SHOP_ID"] for r in selected), "e2": e2,
               "live": sum(r["STORE_STATUS"] == "01" and r["SERVICE_CLOSED"] == "N" for r in selected), "cross": series(cross, multi=True)},
        "A1": {"count": meal_count, "describe": describe},
        "A2": {"ratios": [round(np.mean(dd > 0), 3), round(np.mean(np.abs(dt-da-dd) <= 1), 3),
                          round(np.mean(np.abs(dt-da) <= 1), 3), round(np.mean(np.abs(dt-dd) <= 1), 3)],
               "disc_q": series(dict(zip([.1, .25, .5, .75, .9, .99], np.quantile(dd, [.1, .25, .5, .75, .9, .99]))), "CHILD_DISC_AMT"),
               "tot_q": series(dict(zip([.1, .25, .5, .75, .9, .99], np.quantile(dt, [.1, .25, .5, .75, .9, .99]))), "TOT_AMT"),
               "disc_bins": series(dict(sorted(disc_bins.items())[:20]))},
        "A3": {"hm": table(hm_values, ["n", "n_cust"]), "hg": series(general_bins, "n_general"),
               "e": table(hist, ["n", "n_cust", "n_general"]), "bad": series(amount_bad)},
        "A4": {"top": table(top, ["bin", "n"])}
    }
    exports = {"EXPORT_m4_dong_regime_SYNTHETIC.csv": tt, "EXPORT_m4_dong_total_SYNTHETIC.csv": tot,
               "EXPORT_m4_u2_gungu_status_SYNTHETIC.csv": e2, "EXPORT_m5_amount_hist_SYNTHETIC.csv": snapshots["A3"]["e"]}
    return snapshots, exports
