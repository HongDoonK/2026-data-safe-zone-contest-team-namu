"""MCLP 시나리오 골격 — 가정 층(층 2). 결론 문장에 숫자를 섞지 않는다(T2_integrated_logic.md §0).

질문: 등록만 되고 쉬고 있는 가게를 살리거나(활성화) 새로 모집한다면(모집), 어느 법정동부터 해야
      아이들이 "주변에서 실제로 급식 주문을 받는 가게"를 충분히 갖게 되는가.

  수요 i  = 결합 단위(71). 무게 w_i = 6~18세 아동 수(월평균). [4차 후: × KCB 필요도]
  후보 j  = 법정동(경계 290). 공급 S_j = 방학에 급식 결제를 받은 가게 수. [4차 후: Q1 meal_vac_live]
  닿음 N(i) = 단위 i의 법정동 + 그와 경계가 맞닿은 법정동.            [4차 후: Q3 흐름, 비중 >= tau]
  수준 C_i = sum_{j in N(i)} S_j  (+ 경계 없는 가맹점 키의 공급은 소속 단위 안으로)
  커버    = C_i >= T. 탐욕 선택의 목적함수는 부분 커버 sum w_i * min(C_i, T) / T (단조·부분모듈 → (1-1/e) 보장, 모델 안에서만)
  행동    = 활성화: 등록 Y - S_j 가 3곳 이상인 동에 +min(D, 쉬는 등록 가게)
            모집:   일반 배달이 있는 동이면 +D
격자: T {1(원안 참고), 5, 10, 20} × D {3, 5} × P {5, 10} × 행동 {활성화, 모집}.
입력 교체는 맨 위 SOURCES만 바꾼다.
"""
from itertools import product
from pathlib import Path

import geopandas as gpd
import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"
FIG = Path(__file__).resolve().parent / "fig"
BD = ROOT / "data_external" / "boundary"
SOURCES = {"supply": "regime_vac_nshop",   # → "v4_meal_vac_live"
           "reach": "adjacency",           # → "v4_flow"
           "need": None}                   # → "v4_kcb_3040_low"
K_ACT = 3
GRID = dict(T=[1, 5, 10, 20], D=[3, 5], P=[5, 10], act=["활성화", "모집"])
log = open(OUT / "80_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


# ---- 입력 -------------------------------------------------------------------------
units = pd.read_csv(OUT / "units_per_child.csv").set_index("unit_id")
w = units.child.copy()
br = pd.read_csv(OUT / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("bkey")
b2u = br.set_index("bkey").unit_id
km = pd.read_csv(OUT / "bridge_shopkey_unit.csv").set_index("dong").unit_id
reg = pd.read_csv(ROOT / "10_2_데이터분석결과물/EXPORT_m4_dong_regime.csv")      # 억제 전 내부 값
tot = pd.read_csv(ROOT / "10_2_데이터분석결과물/EXPORT_m4_dong_total.csv").set_index("dong")
S0 = reg[reg.R == "방학"].set_index("dong").n_shop.astype(float)
able = tot.able_y.fillna(0)
gen = tot.gen.fillna(0)

umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"], ri["code"] = umd.EMD_CD + "00", ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
geo = geo.merge(br[["법정동코드", "bkey"]], left_on="code", right_on="법정동코드")
geo = geo.dissolve(by="bkey", aggfunc="first").reset_index()
wq = libpysal.weights.fuzzy_contiguity(geo, buffering=True, buffer=5, silence_warnings=True)
nbr = {geo.bkey[i]: {geo.bkey[j] for j in wq.neighbors[i]} for i in wq.neighbors}
J = list(geo.bkey)

# 닿음 N(i): 단위 안 법정동 + 맞닿은 법정동
inside = {u: set(b2u[b2u == u].index) & set(J) for u in units.index}
REACH = {"adjacency": {u: set().union(inside[u], *[nbr[j] for j in inside[u]]) for u in units.index},
         "inside": inside}
reach = REACH["adjacency"]
# 경계 없는 가맹점 키(빈 동·표기 흔들림)의 공급은 소속 단위 안에만 더한다
extra = S0[[k for k in S0.index if k not in J and k in km.index]].groupby(km).sum()
P("수요 단위", len(w), "| 아동 합", int(w.sum()), "| 후보 법정동", len(J),
  "| 공급 합(경계 있음)", int(S0.reindex(J).fillna(0).sum()), "| 경계 없는 키 공급", int(extra.sum()))
P("단위당 닿는 법정동 수:", pd.Series({u: len(r) for u, r in reach.items()}).describe().round(1).to_dict())


def level(S, rc=None):
    rc = rc or reach
    return pd.Series({u: sum(S.get(j, 0) for j in rc[u]) + extra.get(u, 0) for u in units.index})


def thr(kind, t):
    """단위별 커버 문턱: 절대(가게 t곳) 또는 아동 1천 명당 t곳."""
    return pd.Series(float(t), index=units.index) if kind == "abs" else w * t / 1000


def greedy(T, D, Pn, act, rc=None):
    """T는 단위별 문턱 Series. 목적: sum w * min(C, T) / T."""
    rc = rc or reach
    S = S0.reindex(J).fillna(0).to_dict()
    room = {j: (max(able.get(j, 0) - S[j], 0) if act == "활성화" else (D if gen.get(j, 0) > 0 else 0)) for j in J}
    cand = [j for j in J if (room[j] >= K_ACT if act == "활성화" else room[j] > 0)]
    C, picks = level(S, rc), []
    for _ in range(Pn):
        best, gain = None, 0.0
        for j in cand:
            if j in picks:
                continue
            add = min(D, room[j])
            hit = [u for u in units.index if j in rc[u]]
            g = float((w[hit] * (np.minimum(C[hit] + add, T) - np.minimum(C[hit], T)) / T).sum())
            if g > gain:
                best, gain = j, g
        if best is None:
            break
        add = min(D, room[best])
        S[best] += add
        for u in units.index:
            if best in rc[u]:
                C[u] += add
        picks.append(best)
    return picks, C


# ---- 기준선: 닿음 2종 × 문턱 2종 -----------------------------------------------------
GRID_T = {"abs": [1, 5, 10, 20, 50], "per1k": [1, 2, 3, 5, 10]}
base = []
for rname, rc in REACH.items():
    C = level(S0.to_dict(), rc)
    P(f"\n[기준선·{rname}] 닿는 범위 안 방학 급식 가게 수 C: {C.describe().round(0).to_dict()}")
    P(f"  아동 1천 명당 C: {(C / w * 1000).describe().round(1).to_dict()}")
    for kind, ts in GRID_T.items():
        for t in ts:
            Tu = thr(kind, t)
            base.append(dict(reach=rname, kind=kind, t=t, cov=w[C >= Tu].sum() / w.sum(), below=int((C < Tu).sum())))
base = pd.DataFrame(base)
P("\n[기준선 커버 아동 비율]\n", base.round(3).to_string(index=False))
C_in = level(S0.to_dict(), REACH["inside"])
low = units.assign(C_in=C_in, per1k=(C_in / w * 1000)).sort_values("per1k")
P("\n단위 안에서만 셀 때, 아동 1천 명당 급식 가게가 적은 단위 10:\n",
  low[["gu", "hdongs", "child", "C_in", "per1k"]].head(10).round(1).to_string())

# ---- 격자 실행: 포화되지 않은 설정만 (커버 < 0.99) -------------------------------------------
rows = []
live = base[base["cov"] < 0.99]
P("\n포화되지 않은 설정 수:", len(live), "/", len(base))
for (_, b), D, Pn, act in product(live.iterrows(), GRID["D"], GRID["P"], GRID["act"]):
    rc, Tu = REACH[b["reach"]], thr(b["kind"], b["t"])
    C0 = level(S0.to_dict(), rc)
    picks, C = greedy(Tu, D, Pn, act, rc)
    rows.append(dict(reach=b["reach"], kind=b["kind"], t=b["t"], D=D, P=Pn, act=act,
                     cov0=w[C0 >= Tu].sum() / w.sum(), cov1=w[C >= Tu].sum() / w.sum(),
                     new_children=int(w[(C >= Tu) & (C0 < Tu)].sum()), picks="; ".join(picks)))
res = pd.DataFrame(rows)
if len(res):
    P("\n[격자 결과]\n", res.drop(columns="picks").round(3).to_string(index=False))
res.to_csv(OUT / "mclp_grid_results.csv", index=False, encoding="utf-8-sig")
base.to_csv(OUT / "mclp_baseline.csv", index=False, encoding="utf-8-sig")

main = res
freq = pd.Series([p for s in main.picks for p in s.split("; ") if p]).value_counts() if len(main) else pd.Series(dtype=int)
sets = [set(s.split("; ")) - {""} for s in main.picks] if len(main) else []
jac = [len(a & b) / len(a | b) for i, a in enumerate(sets) for b in sets[i + 1:] if a | b]
top17 = set(pd.read_csv(OUT / "u2_denominator_check_INTERNAL.csv").query("robust.str.startswith('견고')", engine="python").dong)
u2 = set(pd.read_csv(OUT / "bdong_types_INTERNAL.csv").query("type_vac == 'U2'").dong)
fr = pd.DataFrame({"times": freq, "share": (freq / max(len(main), 1)).round(2)})
fr["확인1순위"] = fr.index.isin(top17)
fr["U2"] = fr.index.isin(u2)
if jac:
    P(f"\n[안정성] 격자 {len(main)}회, 선택 집합 Jaccard 평균 {np.mean(jac):.2f} (최소 {np.min(jac):.2f})")
P("자주 선택된 법정동 (상위 15):\n", fr.head(15).to_string())
P("절반 이상 선택된 동:", fr[fr.share >= 0.5].index.tolist())
fr.to_csv(OUT / "mclp_pick_frequency.csv", encoding="utf-8-sig")
C0 = level(S0.to_dict(), REACH["inside"])

# ---- 그림: 미커버 단위(T=10) + 선택 빈도 -------------------------------------------------
plt.rcParams["font.family"] = "Malgun Gothic"
ug = geo.assign(unit_id=geo.bkey.map(b2u)).dissolve(by="unit_id")
ug["C0"] = C0 / w * 1000
gu = umd[umd.COL_ADM_SE != "27720"].dissolve(by="COL_ADM_SE")
fig, ax = plt.subplots(figsize=(10, 11), facecolor="white")
ax.set_axis_off()
ug[ug.C0 >= 3].plot(ax=ax, color="#f0efec", edgecolor="white", linewidth=0.6)
ug[ug.C0 < 3].plot(ax=ax, color="#ec8f86", edgecolor="white", linewidth=0.6)
g = geo.assign(share=geo.bkey.map(fr.share)).dropna(subset=["share"])
g[g.share >= 0.5].plot(ax=ax, color="#1c5cab", edgecolor="white", linewidth=0.4)
g[g.share < 0.5].plot(ax=ax, color="#86b6ef", edgecolor="white", linewidth=0.4)
gu.boundary.plot(ax=ax, color="#1a1a1a", linewidth=1.6)
ax.legend(handles=[Patch(color="#ec8f86", label="단위 안 급식 주문받는 가게가 아동 1천 명당 3곳 미만"),
                   Patch(color="#1c5cab", label="시나리오 절반 이상에서 선택된 동"),
                   Patch(color="#86b6ef", label="일부 시나리오에서 선택된 동")],
          loc="upper left", bbox_to_anchor=(0, -0.01), fontsize=10, frameon=False)
ax.set_title("시나리오(가정): 어느 동에서 가게를 살리거나 모집하면 아이들이 더 많이 커버되나", fontsize=12.5, loc="left")
fig.savefig(FIG / "v2_map4_mclp_scenario.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
log.close()
print("ok")
