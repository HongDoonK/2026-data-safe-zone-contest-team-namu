"""MCLP 시나리오 골격 — 가정 층(층 2). 결론 문장에 숫자를 섞지 않는다(T2_integrated_logic.md §0).

질문: 등록만 되고 쉬고 있는 가게를 살리거나(활성화) 새로 모집한다면(모집), 어느 법정동부터 해야
      아이들이 "주변에서 실제로 급식 주문을 받는 가게"를 충분히 갖게 되는가.

  수요 i  = 결합 단위(71). 무게 w_i = 6~18세 아동 수(월평균).
            [4차: × KCB 30·40대 월소득 200만 원 이하 비율 r_i / 아동 가중 평균 r̄ → 무게 합 = 아동 합]
  후보 j  = 법정동(경계 290). 공급 S_j = 방학에 급식 결제를 받은 가게 수.
            [4차: Q1 meal_vac10_live(엄격, 주) / meal_vac_live(민감도)]
  닿음 N(i) = 단위 i의 법정동 + 그와 경계가 맞닿은 법정동.
            [4차: Q3 흐름. 집 동 h의 급식 결제 중 가게 동 j 비중 >= tau 인 j를, 단위 안 집 동들에 걸쳐 합집합.
             tau ∈ {0.05, 0.10(주), 0.20}. 흐름이 없는 단위는 맞닿은 동으로 대체. 맞닿은 동·단위 안은 비교용으로 유지]
  수준 C_i = sum_{j in N(i)} S_j  (+ 경계 없는 가맹점 키의 공급은 소속 단위 안으로)
  커버    = C_i >= T. 탐욕 선택의 목적함수는 부분 커버 sum w_i * min(C_i, T) / T (단조·부분모듈 → (1-1/e) 보장, 모델 안에서만)
  행동    = 활성화: 등록(4차: 등록·영업) - S_j 가 3곳 이상인 동에 +min(D, 쉬는 등록 가게)
            모집:   일반 배달이 있는 동이면 +D
                    [4차 Q1에 nonY_live(등록 Y 아님·영업 중·일반 결제 있음)가 있으면 +min(D, nonY_live): 데려올 수 있는 가게 상한]
격자: T {1(원안 참고), 5, 10, 20} × D {3, 5} × P {5, 10} × 행동 {활성화, 모집}.

입력 교체는 맨 위 SOURCES가 --v4 폴더의 파일 유무에 따라 바뀐다. 폴더·파일이 없으면 그 입력은 지금 방식 그대로.
  --v4 DIR     4차 반출 폴더 (EXPORT_v4_dong_shop_state / meal_flow_home_shop / kcb_hdong_income)
  --cand FILE  90_reason_table.py 의 mclp_candidates.csv. 없으면 --v4 일 때 출력 폴더의 것을 찾는다.
               후보 단위 안 법정동으로 제한하고 단위별 허용 동작만 쓰는 선택(scope=후보)을 추가한다(D-019 §4).
  --tag NAME   출력을 out_NAME/ (그림은 out_NAME/fig/)로. 가짜 자료는 반드시 태그를 붙인다.
  --v4·--cand 가 모두 없으면 10/12 골격과 같은 출력을 낸다(회귀).
억제 빈칸(G4): 두 끝으로 두 번 계산해 범위로 보고한다. fill=lo 는 커버가 가장 낮게, hi 는 가장 높게 나오는 쪽.
  Q1 <3 → lo 0 / hi 2 (meal_vac10_live·meal_vac_live·able_live·nonY_live 모두 같은 쪽으로).  Q3 <5 → lo: 빈칸 흐름 0(그 동은 닿지 않음)·분모의 다른 빈칸 4 / hi: 빈칸 흐름 4·분모의 다른 빈칸 0.
  KCB <5 → 0/4 의 가운데 값을 무게에 쓰고, 두 끝의 차이를 요약에 적는다.
"""
import argparse
import glob
from itertools import product
from pathlib import Path

import geopandas as gpd
import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IN = HERE / "out"                                  # 밖 분석 내부 산출물(입력)
BD = ROOT / "data_external" / "boundary"
POPDIR = ROOT / "data_external" / "population_dong"
SOURCES = {"supply": "regime_vac_nshop",   # --v4 + Q1  → "v4_meal_vac10_live" (민감도 "v4_meal_vac_live")
           "reach": "adjacency",           # --v4 + Q3  → "v4_flow" (tau ∈ TAUS, 주 TAU_MAIN)
           "need": None}                   # --v4 + KCB → "v4_kcb_3040_low"
K_ACT = 3
GRID = dict(T=[1, 5, 10, 20], D=[3, 5], P=[5, 10], act=["활성화", "모집"])
GRID_T = {"abs": [1, 5, 10, 20, 50], "per1k": [1, 2, 3, 5, 10]}
TAUS, TAU_MAIN = [0.05, 0.10, 0.20], 0.10
FILL = {"Q1": (0, 2), "Q3": (0, 4), "KCB": (0, 4)}   # (가장 불리, 가장 유리) = (0, 억제 문턱 - 1)
FLOW_MIN = 20          # 집 동의 관측 급식 흐름 합이 이보다 적으면 그 집 동은 닿음 계산에서 뺀다(90의 R7_MIN과 같은 값)
SAT, D018_COV = 0.99, 0.90

ap = argparse.ArgumentParser()
ap.add_argument("--v4")
ap.add_argument("--cand")
ap.add_argument("--tag", default="")
A = ap.parse_args()
OUT = HERE / (f"out_{A.tag}" if A.tag else "out")
FIG = (OUT / "fig") if A.tag else (HERE / "fig")
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
NEW = bool(A.v4 or A.cand)
SYN = "SYN" in A.tag.upper() or "SYNTHETIC" in str(A.v4 or "").upper()
log = open(OUT / "80_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


def v4(name):
    f = Path(A.v4) / f"EXPORT_v4_{name}.csv" if A.v4 else None
    return pd.read_csv(f, encoding="utf-8-sig") if f is not None and f.exists() else None


q1, q3, kc = v4("dong_shop_state"), v4("meal_flow_home_shop"), v4("kcb_hdong_income")
if q1 is not None:
    SOURCES["supply"] = "v4_meal_vac10_live"
if q3 is not None:
    SOURCES["reach"] = "v4_flow"
if kc is not None:
    SOURCES["need"] = "v4_kcb_3040_low"

# ---- 입력 -------------------------------------------------------------------------
units = pd.read_csv(IN / "units_per_child.csv").set_index("unit_id")
child = units.child.copy()
w = child.copy()                                   # 수요 무게(4차 KCB가 있으면 아래에서 교체)
br = pd.read_csv(IN / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("bkey")
b2u = br.set_index("bkey").unit_id
km = pd.read_csv(IN / "bridge_shopkey_unit.csv").set_index("dong").unit_id
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
JSET = set(J)

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


def level(S, rc=None, ex=None):
    rc = rc or reach
    ex = extra if ex is None else ex
    return pd.Series({u: sum(S.get(j, 0) for j in rc[u]) + ex.get(u, 0) for u in units.index})


def thr(kind, t):
    """단위별 커버 문턱: 절대(가게 t곳) 또는 아동 1천 명당 t곳(무게가 아니라 아동 수 기준)."""
    return pd.Series(float(t), index=units.index) if kind == "abs" else child * t / 1000


def greedy(T, D, Pn, act, rc=None, S=None, ab=None, ex=None, wt=None, allow=None, rec=None):
    """T는 단위별 문턱 Series. 목적: sum w * min(C, T) / T. 후보별 이득을 한 번에 계산한다(10/12판과 같은 합산 순서).
    S: 공급 dict(키 = 가맹점 동 키), ab: 활성화 여유 계산용 등록 가게 dict, allow: 후보 법정동 제한(set),
    rec: 모집 상한 dict(4차 nonY_live). None이면 일반 배달이 있는 동에 +D."""
    rc = rc or reach
    S = S0.reindex(J).fillna(0).to_dict() if S is None else dict(S)
    ab = able if ab is None else ab
    wt = w if wt is None else wt
    Sj = {j: (0.0 if pd.isna(S.get(j, 0)) else S.get(j, 0)) for j in J}
    if act == "활성화":
        room = {j: max(ab.get(j, 0) - Sj[j], 0) for j in J}
    elif rec is None:
        room = {j: (D if gen.get(j, 0) > 0 else 0) for j in J}
    else:
        room = {j: rec.get(j, 0) for j in J}
    cand = [j for j in J if (room[j] >= K_ACT if act == "활성화" else room[j] > 0) and (allow is None or j in allow)]
    C = level(S, rc, ex).astype(float)
    if not cand:
        return [], C
    pos = {u: i for i, u in enumerate(units.index)}
    M = np.zeros((len(cand), len(units)), dtype=bool)          # 후보 × 단위: 후보 동이 그 단위의 닿음 안에 있는가
    col = {j: k for k, j in enumerate(cand)}
    for u, r in rc.items():
        for j in r:
            if j in col:
                M[col[j], pos[u]] = True
    c, Tv, W = C.values.copy(), T.reindex(units.index).values.astype(float), wt.reindex(units.index).values.astype(float)
    add = np.array([min(D, room[j]) for j in cand], dtype=float)
    picked, picks = np.zeros(len(cand), dtype=bool), []
    for _ in range(Pn):
        cur = np.minimum(c, Tv)
        val = W[None, :] * (np.minimum(c[None, :] + add[:, None], Tv[None, :]) - cur[None, :]) / Tv[None, :]
        g = np.where(M, val, 0.0).sum(axis=1)
        g = np.where(np.isnan(g) | picked, -np.inf, g)
        k = int(np.argmax(g))
        if not g[k] > 0:
            break
        picked[k] = True
        c = c + add[k] * M[k]
        picks.append(cand[k])
    return picks, pd.Series(c, index=units.index)


plt.rcParams["font.family"] = "Malgun Gothic"


def draw_map(C0, fr, note=""):
    ug = geo.assign(unit_id=geo.bkey.map(b2u)).dissolve(by="unit_id")
    ug["C0"] = C0 / child * 1000
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
    ax.set_title(note + "시나리오(가정): 어느 동에서 가게를 살리거나 모집하면 아이들이 더 많이 커버되나", fontsize=12.5, loc="left")
    fig.savefig(FIG / "v2_map4_mclp_scenario.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def pick_freq(picks_col, n):
    freq = pd.Series([p for s in picks_col for p in str(s).split("; ") if p and p != "nan"]).value_counts() \
        if n else pd.Series(dtype=int)
    return pd.DataFrame({"times": freq, "share": (freq / max(n, 1)).round(2)})


if not NEW:
    # ==== 10/12 골격 그대로 (회귀) =====================================================
    # ---- 기준선: 닿음 2종 × 문턱 2종 -----------------------------------------------------
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
    live = base[base["cov"] < SAT]
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
    top17 = set(pd.read_csv(IN / "u2_denominator_check_INTERNAL.csv").query("robust.str.startswith('견고')", engine="python").dong)
    u2 = set(pd.read_csv(IN / "bdong_types_INTERNAL.csv").query("type_vac == 'U2'").dong)
    fr = pd.DataFrame({"times": freq, "share": (freq / max(len(main), 1)).round(2)})
    fr["확인1순위"] = fr.index.isin(top17)
    fr["U2"] = fr.index.isin(u2)
    if jac:
        P(f"\n[안정성] 격자 {len(main)}회, 선택 집합 Jaccard 평균 {np.mean(jac):.2f} (최소 {np.min(jac):.2f})")
    P("자주 선택된 법정동 (상위 15):\n", fr.head(15).to_string())
    P("절반 이상 선택된 동:", fr[fr.share >= 0.5].index.tolist())
    fr.to_csv(OUT / "mclp_pick_frequency.csv", encoding="utf-8-sig")
    C0 = level(S0.to_dict(), REACH["inside"])
    draw_map(C0, fr)
    log.close()
    print("ok")
    raise SystemExit

# ==== 4차 교체 경로 (--v4 / --cand) ======================================================
P("\n[SOURCES]", SOURCES, "| 4차 폴더:", A.v4 or "없음", "| 태그:", A.tag or "(없음 → out/, fig/)")
if A.v4 and not Path(A.v4).exists():
    P("  ※ 4차 폴더가 없다 → 전 입력 지금 방식")
for n, d in [("dong_shop_state(Q1)", q1), ("meal_flow_home_shop(Q3)", q3), ("kcb_hdong_income(KCB)", kc)]:
    P(f"  {n}: {'있음 ' + str(d.shape) if d is not None else '없음 → 지금 방식'}")


def extra_of(S):
    """경계 없는 가맹점 키의 값을 소속 단위로 모은다(위 extra와 같은 규칙)."""
    s = pd.Series({k: v for k, v in S.items() if k not in JSET and k in km.index}, dtype=float)
    return s.groupby(km.reindex(s.index).values).sum() if len(s) else pd.Series(dtype=float)


# ---- 공급: {이름: {fill: (공급 dict, 활성화용 등록 dict, 모집 상한 dict 또는 None)}} ----------------------------
SUP = {"regime_vac_nshop": {s: (S0.fillna(0).to_dict(), able.to_dict(), None) for s in ("lo", "hi")}}
REC = "일반 배달이 있는 동에 +D (3차 방식)"
if q1 is not None:
    qs = q1.set_index("dong")
    P("  Q1 억제 칸(<3):", qs.isna().sum().to_dict(), "| 가맹점 키 중 단위 연결 안 됨:", int((~qs.index.isin(km.index)).sum()))
    has_ny = "nonY_live" in qs.columns
    for col in ["meal_vac10_live", "meal_vac_live"]:
        SUP[f"v4_{col}"] = {s: (qs[col].fillna(f).to_dict(), qs.able_live.fillna(f).to_dict(),
                                qs.nonY_live.fillna(f).to_dict() if has_ny else None)
                            for s, f in zip(("lo", "hi"), FILL["Q1"])}
    for col in ["meal_vac10_live", "meal_vac_live", "able_live"] + (["nonY_live"] if has_ny else []):
        P(f"  {col} 합 lo~hi: {qs[col].fillna(FILL['Q1'][0]).sum():.0f} ~ {qs[col].fillna(FILL['Q1'][1]).sum():.0f}")
    P(f"  참고: 3차 방학 급식 가게(n_shop) 합 {S0.sum():.0f}, 등록 Y 합 {able.sum():.0f}")
    if has_ny:
        REC = "+min(D, nonY_live) (등록 Y 아님·영업·일반 결제 있는 가게 수, 억제 0/2)"
    else:
        P("  nonY_live 열 없음 → 모집은 일반 배달이 있는 동에 +D (3차 방식)")
P("  모집 상한:", REC)
MAIN_SUP = "v4_meal_vac10_live" if q1 is not None else "regime_vac_nshop"

# ---- 수요 무게: KCB 30·40대 저소득 비율 (90_reason_table.py R1과 같은 연결) ---------------------------
need = pd.DataFrame(index=units.index, columns=["need_lo", "need_hi", "need_mid"], dtype=float)
NEED = "child"
if kc is not None:
    h2u = pd.read_csv(IN / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("행정동코드").set_index("행정동코드").unit_id
    prow = []
    for f in sorted(glob.glob(str(POPDIR / "*.csv"))):
        d = pd.read_csv(f, encoding="cp949", thousands=",")
        d = d[d["행정구역"].str.startswith("대구광역시")]
        pc = [c for c in d.columns if c.endswith("_계_총인구수")][0]
        prow.append(pd.DataFrame({"hcode": d["행정구역"].str.extract(r"\((\d{10})\)")[0].values, "pop": d[pc].values}))
    hpop = pd.concat(prow).groupby("hcode")["pop"].mean()
    hpop = hpop[hpop.index.isin(h2u.index)]
    CC = [f"C{i}_CNT" for i in range(1, 23)]
    kc["EMD_CD"] = kc.EMD_CD.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    k3 = kc[kc.grp.astype(str) == "3040"].copy()
    L = int(k3.EMD_CD.str.len().mode()[0])
    k3["hcode"] = k3.EMD_CD.map({h[:8]: h for h in h2u.index} if L == 8 else {h: h for h in h2u.index})
    k3["unit_id"] = k3.hcode.map(h2u)
    P(f"  KCB EMD_CD {L}자리, 30·40대 행 {len(k3)} 중 단위 연결 {int(k3.unit_id.notna().sum())}")
    k3 = k3.dropna(subset=["unit_id"])
    lo_f, hi_f = FILL["KCB"]
    a0, a4 = k3[CC].fillna(lo_f), k3[CC].fillna(hi_f)
    num_lo, num_hi = a0[CC[:3]].sum(axis=1).groupby(k3.unit_id).sum(), a4[CC[:3]].sum(axis=1).groupby(k3.unit_id).sum()
    rst_lo, rst_hi = a0[CC[3:]].sum(axis=1).groupby(k3.unit_id).sum(), a4[CC[3:]].sum(axis=1).groupby(k3.unit_id).sum()
    n_lo = (num_lo / (num_lo + rst_hi)).reindex(units.index)
    n_hi = (num_hi / (num_hi + rst_lo)).reindex(units.index)
    unm = (hpop[~hpop.index.isin(set(k3.hcode))].groupby(h2u).sum() / hpop.groupby(h2u).sum()).reindex(units.index).fillna(0)
    n_lo[unm >= 0.2], n_hi[unm >= 0.2] = np.nan, np.nan
    need["need_lo"], need["need_hi"], need["need_mid"] = n_lo, n_hi, (n_lo + n_hi) / 2
    mid = need.need_mid
    rbar = (child * mid).sum() / child[mid.notna()].sum()
    w = child * mid.fillna(rbar) / rbar
    NEED = "kcb_3040_low"
    P(f"  KCB 비율 아동 가중 평균 r̄ {rbar:.4f} | 비율 없는 단위(연결 20% 미만·자료 없음 → r̄, 무게 = 아동) {mid.isna().sum()}곳:",
      list(mid[mid.isna()].index))
    P(f"  억제 두 끝(0/4)의 비율 차이 최대 {(n_hi - n_lo).abs().max() * 100:.2f}%p → 무게는 가운데 값")
    P(f"  무게/아동 범위 {(w / child).min():.2f} ~ {(w / child).max():.2f}, 무게 합 {w.sum():.0f} = 아동 합 {child.sum():.0f}")

# ---- 닿음: Q3 흐름 ----------------------------------------------------------------------------
FLOWS = {}
if q3 is not None:
    f = q3.copy()
    f["sup"], f["n0"] = f.n.isna(), f.n.fillna(0)
    obs = f.groupby("home").n0.transform("sum")
    nsup = f.groupby("home").sup.transform("sum")
    hv = FILL["Q3"][1]
    P(f"  Q3 쌍 {len(f)} 중 억제 {int(f.sup.sum())} | 집 동 {f.home.nunique()} 중 관측 흐름 >= {FLOW_MIN}건: "
      f"{f.loc[obs >= FLOW_MIN, 'home'].nunique()} | 집 동 = 가게 동 비율(관측) {f.n0[f.home == f.dong].sum() / f.n0.sum():.3f}")
    share = {"lo": pd.Series(np.where(f.sup, 0.0, f.n0 / (obs + hv * nsup)), index=f.index),
             "hi": pd.Series(np.where(f.sup, hv / (obs + hv), f.n0 / obs.replace(0, np.nan)), index=f.index)}
    for tau in TAUS:
        for side in ("lo", "hi"):
            g = f[(obs >= FLOW_MIN) & (share[side] >= tau)].assign(hu=lambda d: d.home.map(km)).dropna(subset=["hu"])
            sets = g.groupby("hu").dong.agg(set).to_dict()
            fb = [x for x in units.index if x not in sets]
            rc = {x: (sets[x] if x in sets else REACH["adjacency"][x]) for x in units.index}
            FLOWS[(tau, side)] = (rc, fb)
        rl, fb = FLOWS[(tau, "lo")]
        rh, _ = FLOWS[(tau, "hi")]
        P(f"  흐름 닿음 tau={tau:.2f}: 단위당 닿는 동 수 lo 중앙 {np.median([len(rl[x]) for x in units.index if x not in fb]):.0f}"
          f" / hi 중앙 {np.median([len(rh[x]) for x in units.index if x not in fb]):.0f}"
          f" | 흐름 없어 맞닿은 동으로 대체한 단위 {len(fb)}곳: {fb}")
RNAMES = ([f"flow_{t:.2f}" for t in TAUS] if q3 is not None else []) + ["adjacency", "inside"]
MAIN_REACH = f"flow_{TAU_MAIN:.2f}" if q3 is not None else "adjacency"
P(f"  주 설정: 공급 {MAIN_SUP}, 닿음 {MAIN_REACH}, 무게 {NEED}")

# ---- 설정 목록: 공급 × 닿음 × fill(억제 두 끝) ---------------------------------------------------------
cfgs = []
for sname in SUP:
    for rname in RNAMES:
        sides = ("lo", "hi") if (sname.startswith("v4") or rname.startswith("flow")) else ("-",)
        for side in sides:
            sd = "lo" if side == "-" else side
            S, ab, rec = SUP[sname][sd]
            if rname.startswith("flow"):
                rc, fb = FLOWS[(float(rname[5:]), sd)]
                ex = extra_of(S).reindex(fb).dropna()
            else:
                rc, fb, ex = REACH[rname], [], extra_of(S)
            cfgs.append(dict(supply=sname, fill=side, reach=rname, S=S, ab=ab, rec=rec, rc=rc, ex=ex, fb=fb,
                             main=(sname == MAIN_SUP and rname == MAIN_REACH)))

# ---- 기준선 ------------------------------------------------------------------------------------
base = []
for c in cfgs:
    c["C"] = C = level(c["S"], c["rc"], c["ex"])
    for kind, ts in GRID_T.items():
        for t in ts:
            ok = C >= thr(kind, t)
            base.append(dict(supply=c["supply"], fill=c["fill"], need=NEED, reach=c["reach"], kind=kind, t=t,
                             cov=w[ok].sum() / w.sum(), cov_child=child[ok].sum() / child.sum(),
                             below=int((~ok).sum()), is_main=c["main"]))
base = pd.DataFrame(base)
base.to_csv(OUT / "mclp_baseline.csv", index=False, encoding="utf-8-sig")
pv = base.assign(col=base.supply.str.replace("v4_", "") + "·" + base.fill).pivot_table(
    index=["reach", "kind", "t"], columns="col", values="cov", sort=False)
pv = pv.reindex(pd.MultiIndex.from_tuples(list(dict.fromkeys(zip(base.reach, base.kind, base.t))), names=["reach", "kind", "t"]))
P("\n[기준선 커버 비율(무게 기준)] 열 = 공급·fill (lo 가장 낮게 / hi 가장 높게)\n", pv.round(3).to_string())
for c in cfgs:
    if c["main"]:
        P(f"\n[주 설정 {c['fill']}] 닿는 범위 안 공급 C: {c['C'].describe().round(0).to_dict()}")
        P(f"  아동 1천 명당 C: {(c['C'] / child * 1000).describe().round(1).to_dict()}")
cin = next(c for c in cfgs if c["supply"] == MAIN_SUP and c["reach"] == "inside" and c["fill"] in ("lo", "-"))
low = units.assign(C_in=cin["C"], per1k=(cin["C"] / child * 1000)).sort_values("per1k")
P(f"\n단위 안에서만 셀 때({MAIN_SUP}·{cin['fill']}), 아동 1천 명당 급식 가게가 적은 단위 10:\n",
  low[["gu", "hdongs", "child", "C_in", "per1k"]].head(10).round(1).to_string())

# ---- D-018 뒤집을 조건: 엄격 공급 + 실제 닿음(Q3)에서 기준선 커버 < 90% ----------------------------------
if q1 is not None and q3 is not None:
    m = base[(base.supply == "v4_meal_vac10_live") & base.reach.str.startswith("flow")]
    d18 = m.pivot_table(index=["reach", "kind", "t"], columns="fill", values=["cov", "cov_child"]).reset_index()
    d18.columns = ["_".join(x for x in c if x) for c in d18.columns]
    d18["판정"] = np.where(d18.cov_hi < D018_COV, "경고(억제 범위 전체 90% 미만)",
                         np.where(d18.cov_lo < D018_COV, "경고 가능(억제 범위에 따라)", "-"))
    d18.to_csv(OUT / "mclp_d018_check.csv", index=False, encoding="utf-8-sig")
    mm = d18[d18.reach == MAIN_REACH]
    n_w, n_p = int(mm["판정"].str.startswith("경고(").sum()), int(mm["판정"].str.startswith("경고 가능").sum())
    P(f"\n[D-018 점검] 엄격 공급(meal_vac10_live) + 흐름 닿음, 기준선 커버 < {D018_COV:.0%} 이면 경고\n", d18.round(3).to_string(index=False))
    P(f"  ▶ 주 tau {TAU_MAIN:.2f}: 문턱 설정 {len(mm)}개 중 경고 {n_w} · 경고 가능 {n_p}"
      + (" → ※ D-018 뒤집을 조건 해당: A를 '모집 최적화'로 다시 비중 있게 다룰지 사용자 결정 필요" if n_w else
         (" → 억제 범위에 따라 해당할 수 있음. 원값 확인 불가이므로 범위로 보고" if n_p else " → 해당 없음(공급 포화 유지)")))
else:
    P("\n[D-018 점검] 엄격 공급(Q1)과 흐름(Q3)이 모두 있어야 판정한다 → 판단 불가(자료)")

# ---- 후보 단위 (D-019 §4) ------------------------------------------------------------------------
cand_path = Path(A.cand) if A.cand else (OUT / "mclp_candidates.csv")
ALLOW = None
if cand_path.exists():
    cd = pd.read_csv(cand_path)
    au = {a: set(cd[cd["허용 동작"].astype(str).str.contains(a)].unit_id) for a in GRID["act"]}
    ALLOW = {a: {j for j in J if b2u.get(j) in au[a]} for a in GRID["act"]}
    P(f"\n[후보] {cand_path} : {len(cd)}개 단위 ({', '.join(cd.unit_id + '=' + cd.hdongs.astype(str))})")
    P("  허용 동작별 후보 법정동 수:", {a: len(ALLOW[a]) for a in ALLOW},
      "| 이유:", cd["이유"].value_counts().to_dict())
else:
    P(f"\n[후보] {cand_path} 없음 → 대구 전체 선택만 (90_reason_table.py를 같은 --tag로 먼저 돌린다)")
SCOPES = [("대구 전체", None)] + ([("후보", "ALLOW")] if ALLOW is not None else [])

# ---- 격자 실행: 주 공급, 포화되지 않은 설정만 ------------------------------------------------------------
rows = []
for c in [c for c in cfgs if c["supply"] == MAIN_SUP]:
    live = base[(base.supply == c["supply"]) & (base.fill == c["fill"]) & (base.reach == c["reach"]) & (base["cov"] < SAT)]
    for (_, bb), D, Pn, act in product(live.iterrows(), GRID["D"], GRID["P"], GRID["act"]):
        Tu, C0 = thr(bb["kind"], bb["t"]), c["C"]
        for scope, al in SCOPES:
            allow = ALLOW[act] if al else None
            picks, C = greedy(Tu, D, Pn, act, rc=c["rc"], S=c["S"], ab=c["ab"], ex=c["ex"], wt=w, allow=allow, rec=c["rec"])
            new = (C >= Tu) & (C0 < Tu)
            rows.append(dict(supply=c["supply"], fill=c["fill"], need=NEED, reach=c["reach"], scope=scope,
                             kind=bb["kind"], t=bb["t"], D=D, P=Pn, act=act,
                             cov0=w[C0 >= Tu].sum() / w.sum(), cov1=w[C >= Tu].sum() / w.sum(),
                             new_children=round(float(w[new].sum()), 1), new_children_raw=round(float(child[new].sum()), 1),
                             picks="; ".join(picks), is_main=c["main"]))
res = pd.DataFrame(rows, columns=["supply", "fill", "need", "reach", "scope", "kind", "t", "D", "P", "act", "cov0", "cov1",
                                  "new_children", "new_children_raw", "picks", "is_main"])
res.to_csv(OUT / "mclp_grid_results.csv", index=False, encoding="utf-8-sig")
P(f"\n포화되지 않은 설정(주 공급, 커버 < {SAT}):",
  base[(base.supply == MAIN_SUP) & (base["cov"] < SAT)].groupby(["reach", "fill"]).size().to_dict())
if len(res):
    smry = res.groupby(["reach", "fill", "scope", "act"]).agg(runs=("t", "size"), new_max=("new_children", "max"),
                                                              new_raw_max=("new_children_raw", "max"), cov0_min=("cov0", "min"))
    P("\n[격자 결과 요약] 설정·D·P 중 최대로 새로 커버되는 무게(아동)\n", smry.round(3).to_string())
    mr = res[res.is_main]
    if len(mr):
        P("\n[주 설정 격자]\n", mr.drop(columns=["supply", "need", "reach", "picks", "is_main"]).round(3).to_string(index=False))

# ---- 선택 빈도 (주 설정, 대구 전체) ----------------------------------------------------------------
main = res[res.is_main & (res.scope == "대구 전체")] if len(res) else res
fr = pick_freq(main.picks, len(main))
top17 = set(pd.read_csv(IN / "u2_denominator_check_INTERNAL.csv").query("robust.str.startswith('견고')", engine="python").dong)
u2 = set(pd.read_csv(IN / "bdong_types_INTERNAL.csv").query("type_vac == 'U2'").dong)
fr["확인1순위(D-017)"] = fr.index.isin(top17)
fr["U2"] = fr.index.isin(u2)
sets = [set(str(s).split("; ")) - {"", "nan"} for s in main.picks]
jac = [len(a & b) / len(a | b) for i, a in enumerate(sets) for b in sets[i + 1:] if a | b]
if jac:
    P(f"\n[안정성·주 설정] 격자 {len(main)}회, 선택 집합 Jaccard 평균 {np.mean(jac):.2f} (최소 {np.min(jac):.2f})")
P("자주 선택된 법정동 (주 설정, 상위 15):\n", fr.head(15).to_string())
if ALLOW is not None and len(res):
    mc = res[res.is_main & (res.scope == "후보")]
    P("후보 제한 실행에서 자주 선택된 법정동:\n", pick_freq(mc.picks, len(mc)).head(10).to_string())
fr.to_csv(OUT / "mclp_pick_frequency.csv", encoding="utf-8-sig")

# ---- 85(시나리오 B)로 넘기는 단위 입력 (내부) --------------------------------------------------------
cm = {c["fill"]: c for c in cfgs if c["main"]}
lo_c, hi_c = cm.get("lo", cm.get("-")), cm.get("hi", cm.get("-"))
ab_mid = {k: (SUP[MAIN_SUP]["lo"][1].get(k, 0) + SUP[MAIN_SUP]["hi"][1].get(k, 0)) / 2
          for k in set(SUP[MAIN_SUP]["lo"][1]) | set(SUP[MAIN_SUP]["hi"][1])}
able_adj = level(ab_mid, REACH["adjacency"], extra_of(ab_mid))
ui = pd.DataFrame({"child": child, "w": w, **{c: need[c] for c in need.columns},
                   "C_main_lo": lo_c["C"], "C_main_hi": hi_c["C"],
                   "able_adj_per1k": able_adj / child * 1000, "gen_per_child": units.gen / child,
                   "flow_fallback": units.index.isin(lo_c["fb"])}, index=units.index)
ui.index.name = "unit_id"
ui["src_supply"], ui["src_reach"], ui["src_need"] = MAIN_SUP, MAIN_REACH, NEED
ui.to_csv(OUT / "mclp_unit_inputs_INTERNAL.csv", encoding="utf-8-sig")

draw_map(cin["C"], fr, "[가짜 자료 · 실데이터 아님] " if SYN else "")
log.close()
print(f"ok → {OUT.name}: 공급 {MAIN_SUP} · 닿음 {MAIN_REACH} · 무게 {NEED} · 격자 {len(res)}회")
