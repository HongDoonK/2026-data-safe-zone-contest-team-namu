"""SYNTHETIC — 4차 반출 파일 모양의 가짜 자료. 판정표 코드(analysis/outside/90_reason_table.py) 점검용.

동 이름·행정동·법정동 코드는 실제 키를 쓰고, 값은 전부 난수다. 실데이터 결과가 아니다.
파일 형식은 4차 계획(docs/topics/T2_visit4_plan.md)의 저장 셀(Q4b, Q1b, K2, Q3c, S6b, Q7)과 억제 규칙을 따른다.
  --kcb8            KCB EMD_CD를 8자리로
  --drop a,b        빼고 만들 파일(예: shinhan,delivery,app)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
IN = ROOT / "analysis" / "outside" / "out"
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "v4_exports_SYNTHETIC"))
ap.add_argument("--kcb8", action="store_true")
ap.add_argument("--drop", default="")
ap.add_argument("--seed", type=int, default=7)
A = ap.parse_args()
OUT = Path(A.out)
OUT.mkdir(parents=True, exist_ok=True)
drop = set(filter(None, A.drop.split(",")))
rng = np.random.default_rng(A.seed)
CONTROLS = {"달성군": ["화원읍 구라리", "구지면 창리"], "동구": ["신기동", "봉무동"], "북구": ["연경동", "사수동"],
            "서구": ["중리동", "비산동"], "수성구": ["파동", "욱수동"]}       # T2_reason_rules.md §5

b = pd.read_csv(IN / "bdong_types_INTERNAL.csv").set_index("dong")
br = pd.read_csv(IN / "bridge_bdong_hdong.csv", dtype=str)
chk = pd.read_csv(IN / "u2_denominator_check_INTERNAL.csv")
targets = list(chk[chk.robust.str.startswith("견고")].dong)
act = b[b.gen > 0]
U = lambda lo, hi, n=None: rng.uniform(lo, hi, n if n is not None else len(act))

# Q4b 동 × 레짐 일반 결제 (<5, 한 칸 억제 시 동 전체)
gen = act.gen.values
vac = np.round(gen * U(0.18, 0.30)); tr = np.round(gen * U(0.14, 0.20))
gd = pd.DataFrame({"방학": vac, "전환": tr, "학기": gen - vac - tr}, index=act.index)
gd.index.name = "dong"
gd[gd < 5] = np.nan
gd.loc[gd.isna().any(axis=1)] = np.nan
gd.to_csv(OUT / "EXPORT_v4_dong_regime_general.csv", encoding="utf-8-sig")

# Q1b 동별 가게 상태 (<3)
able = b.able_y.fillna(0).values
q = pd.DataFrame(index=b.index)
q["able_live"] = np.round(able * rng.uniform(0.6, 0.95, len(b)))
q["meal_vac_shop"] = np.round(able * rng.uniform(0.2, 0.7, len(b)))
q["meal_vac_live"] = np.round(q.meal_vac_shop * rng.uniform(0.7, 0.95, len(b)))
q["meal_vac10_live"] = np.round(q.meal_vac_live * rng.uniform(0.15, 0.6, len(b)))
q["u2_live"] = np.round(q.able_live * rng.uniform(0, 0.1, len(b)))
q.index.name = "dong"
q[q < 3] = np.nan
q.to_csv(OUT / "EXPORT_v4_dong_shop_state.csv", encoding="utf-8-sig")

# K2 KCB 행정동 × (3040/기타) × C1~C22 (<5). 행정동 2곳은 일부러 빼서 연결 점검
hc = sorted(br["행정동코드"].unique())
gone = set(rng.choice(hc, 2, replace=False))
hc = [h for h in hc if h not in gone]
rows, k = [], np.arange(1, 23)
for h in hc:
    mu = rng.uniform(3, 9)
    shape = np.exp(-((k - mu) / 4) ** 2)
    for grp, n in [("3040", rng.uniform(300, 5000)), ("기타", rng.uniform(800, 9000))]:
        c = rng.poisson(n * shape / shape.sum()).astype(float)
        rows.append([h[:8] if A.kcb8 else h, grp, *c])
kd = pd.DataFrame(rows, columns=["EMD_CD", "grp"] + [f"C{i}_CNT" for i in k])
cc = [f"C{i}_CNT" for i in k]
kd[cc] = kd[cc].mask(kd[cc] < 5)
kd.to_csv(OUT / "EXPORT_v4_kcb_hdong_income.csv", index=False, encoding="utf-8-sig")

# Q3c 추정 집 동 × 가게 동 급식 결제 (건수<5 또는 계정<5)
fl = []
gu = b.index.str.split("|").str[0]
for h in b.index[b.meal > 0]:
    tot = b.meal[h] * rng.uniform(0.3, 0.6)
    selfs = rng.uniform(0.4, 0.9)
    fl.append((h, h, tot * selfs))
    others = [d for d in b.index[(gu == h.split("|")[0]) & (b.index != h)]]
    for j, w in zip(rng.choice(others, min(3, len(others)), replace=False), rng.dirichlet([1, 1, 1])):
        fl.append((h, j, tot * (1 - selfs) * w))
fl = pd.DataFrame(fl, columns=["home", "dong", "n"]).groupby(["home", "dong"]).n.sum().round().to_frame()
fl["n_cust"] = np.round(fl.n / rng.uniform(4, 12, len(fl)))
bad = (fl.n < 5) | (fl.n_cust < 5)
fl[bad] = np.nan
fl.to_csv(OUT / "EXPORT_v4_meal_flow_home_shop.csv", encoding="utf-8-sig")

# S6b 신한 배달매출 법정동 × 월 (건수<5면 행 억제). 열 이름은 현장에서 정해지므로 가짜 이름
if "shinhan" not in drop:
    bg = br.drop_duplicates("법정동코드").assign(gen=lambda d: d.bkey.map(b.gen)).fillna({"gen": 0})
    yms = [f"{y}{m:02d}" for y in (2023, 2024, 2025) for m in range(1, 13)
           if "202306" <= f"{y}{m:02d}" <= "202506"]
    s = pd.DataFrame([(c, ym, rng.poisson(g / 25 * rng.uniform(1, 4) + 1)) for c, g in zip(bg["법정동코드"], bg.gen)
                      for ym in yms], columns=["umd_cd", "ym", "DLV_CNT"]).astype({"DLV_CNT": float})
    s["DLV_AMT"] = s.DLV_CNT * rng.uniform(18000, 25000, len(s))
    s.loc[s.DLV_CNT < 5, ["DLV_CNT", "DLV_AMT"]] = np.nan
    s.to_csv(OUT / "EXPORT_v4_shinhan_delivery_umd_month.csv", index=False, encoding="utf-8-sig")

# Q7 가게 동별 배달 결과 (<5면 행 억제)
if "delivery" not in drop:
    n = np.round(gen * U(0.8, 1.2))
    dg = pd.DataFrame({"n": n, "n_cancel": np.round(n * U(0.005, 0.05))}, index=act.index)
    dg["mins_n"] = dg.n - dg.n_cancel
    dg["mins_sum"] = dg.mins_n * U(18, 45)
    dg.index.name = "dong"
    dg[dg.n < 5] = np.nan
    dg.to_csv(OUT / "EXPORT_v4_dong_delivery.csv", encoding="utf-8-sig")

# 앱 점검 기록(대상 + 대조)과 지역아동센터 목록
if "app" not in drop:
    rec = []
    keys = [("대상", t) for t in targets] + [("대조", f"{g}|{d}") for g, ds in CONTROLS.items() for d in ds]
    for role, key in keys:
        g, d = key.split("|")
        p = [0.1, 0.1, 0.15, 0.15, 0.2, 0.15, 0.1, 0.05] if role == "대조" else [0.05, 0.05, 0.1, 0.1, 0.2, 0.2, 0.15, 0.15]
        for i in range(int(rng.integers(5, 30))):
            rec.append(dict(역할=role, 구=g, 동=d, 점검일="2026-10-SYN", 가게=f"가짜{i}", 업종="한식",
                            최소주문금액=rng.choice([0, 5000, 8000, 9000, 10000, 12000, 13000, 15000], p=p),
                            배달팁=rng.choice([0, 1000, 2000, 3000, 4000]), 영업중=rng.choice(["Y", "N"], p=[0.85, 0.15])))
    pd.DataFrame(rec).to_csv(OUT / "app_check_SYNTHETIC.csv", index=False, encoding="utf-8-sig")
    ce = pd.DataFrame({"행정동코드": rng.choice(hc, int(len(hc) * 0.6), replace=False)})
    ce["정원"] = rng.choice([19, 29, 39, 49], len(ce))
    ce.to_csv(OUT / "centers_SYNTHETIC.csv", index=False, encoding="utf-8-sig")
print("SYNTHETIC v4 →", OUT, sorted(p.name for p in OUT.iterdir()))
