"""센터 밖 분석 5 — 법정동 LQ 지도, 결합 단위 아동 1천 명당 지도, Moran's I·LISA.

경계: 국가공간정보 LSMD_ADM_SECT_UMD/RI_27_202609 (EPSG:5186). 구 지역은 읍면동(법정동), 달성군은 리.
주 지표: 방학 LQ(D-016). 민감도: 25개월 LQ.
공표 규칙: 지도에 칠하는 동 값은 방학 레짐 칸이 억제 기준(건수<5, 가맹점<3, 고객<5)을 통과한 동만.
"""
from pathlib import Path

import esda
import geopandas as gpd
import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
ROOT = Path(__file__).resolve().parents[2]
BD = ROOT / "data_external" / "boundary"
OUT = Path(__file__).resolve().parent / "out"
FIG = Path(__file__).resolve().parent / "fig"
FIG.mkdir(exist_ok=True)
log = open(OUT / "50_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


# ---- 경계 → 법정동 키 -------------------------------------------------------
umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"] = umd.EMD_CD + "00"
ri["code"] = ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
br = pd.read_csv(OUT / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("법정동코드")
geo = geo.merge(br[["법정동코드", "bkey", "unit_id"]], left_on="code", right_on="법정동코드", how="left")
P("경계 폴리곤", len(geo), "| 대응표 키 붙음", int(geo.bkey.notna().sum()),
  "| 못 붙은 코드", geo.loc[geo.bkey.isna(), "code"].tolist())
geo = geo.dropna(subset=["bkey"]).dissolve(by="bkey", aggfunc="first").reset_index()

# ---- 지표 ------------------------------------------------------------------
b = pd.read_csv(OUT / "bdong_types_INTERNAL.csv").set_index("dong")
rc = pd.read_csv(OUT / "m4_dong_regime_resuppressed.csv")
pub_vac = set(rc[(rc.R == "방학") & rc.n.notna()].dong)   # 방학 칸이 억제 통과한 동
g = geo.merge(b, left_on="bkey", right_index=True, how="left")
miss = sorted(set(b.index) - set(g.bkey))
P("지표 있는 법정동 중 경계 없음:", miss)
g["pub"] = g.bkey.isin(pub_vac)
P("지도 법정동", len(g), "| 공표 가능(방학 칸 통과)", int(g.pub.sum()))

# ---- 지도 1: 방학 LQ ---------------------------------------------------------
gu = umd.assign(gu=umd.COL_ADM_SE).dissolve(by="gu")
gu = gu[gu.index != "27720"]


def base(ax):
    ax.set_axis_off()
    gu.boundary.plot(ax=ax, color="#333", linewidth=0.8, zorder=4)


bins = [0, 0.5, 0.8, 1.25, 2.0, np.inf]
labs = ["< 0.5", "0.5–0.8", "0.8–1.25", "1.25–2.0", "≥ 2.0"]
cols = ["#b2182b", "#ef8a62", "#f7f7f7", "#67a9cf", "#2166ac"]
fig, ax = plt.subplots(figsize=(9, 10))
base(ax)
g[~g.pub].plot(ax=ax, color="#d9d9d9", edgecolor="white", linewidth=0.2, hatch="///")
sh = g[g.pub].copy()
sh["cls"] = pd.cut(sh.lq_vac, bins, labels=False, right=False)
for i, c in enumerate(cols):
    sh[sh.cls == i].plot(ax=ax, color=c, edgecolor="white", linewidth=0.2)
g[g.type_vac == "U2"].boundary.plot(ax=ax, color="black", linewidth=1.2, zorder=5)
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(cols, labs)]
          + [Patch(facecolor="#d9d9d9", hatch="///", label="억제·값 없음"),
             Patch(facecolor="none", edgecolor="black", label="U2 (등록 대비 이용 미관측)")],
          loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=9, title="방학 급식 LQ (일반 배달 대비)")
ax.set_title("대구 법정동 방학 급식카드 결제 위치몫(LQ), 2023-06~2025-06", fontsize=12)
fig.savefig(FIG / "map_lq_vac.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---- 지도 2: 결합 단위 방학 아동 1천 명당 ----------------------------------------
u = pd.read_csv(OUT / "units_per_child.csv").set_index("unit_id")
ug = geo.dissolve(by="unit_id").join(u[["per1k_방학", "per1k_학기", "child", "meal"]])
ug["pub"] = ug.meal >= 5
fig, axs = plt.subplots(1, 2, figsize=(16, 9))
for ax, col, t in zip(axs, ["per1k_방학", "per1k_학기"], ["방학", "학기"]):
    base(ax)
    q = ug[ug.pub]
    q.plot(ax=ax, column=col, cmap="YlGnBu", scheme="quantiles", k=5, edgecolor="white", linewidth=0.3,
           legend=True, legend_kwds={"loc": "upper left", "bbox_to_anchor": (1.0, 1.0), "fontsize": 8, "title": "건/월/아동 1천 명"})
    ug[~ug.pub].plot(ax=ax, color="#d9d9d9", hatch="///")
    ax.set_title(f"{t}: 아동(6~18세) 1천 명당 월 급식 결제 (가맹점 소재 단위)", fontsize=11)
fig.savefig(FIG / "map_unit_per_child.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---- Moran's I / LISA (법정동, 일반 결제 > 0) -------------------------------------
m = g[g.gen > 0].reset_index(drop=True)
# 주 가중치: KNN k=6 (리·동 크기 차이가 크고, 일반 결제 0인 동을 빼면 인접 그래프가 끊긴다)
# 확인용: Queen 인접(고립 폴리곤은 자기 lag 0)
pts = m.geometry.representative_point()
w = libpysal.weights.KNN.from_dataframe(gpd.GeoDataFrame(geometry=pts), k=6, use_index=False)
wq = libpysal.weights.Queen.from_dataframe(m, use_index=False, silence_warnings=True)
P("\nMoran 대상 법정동", len(m), "| Queen 고립", len(wq.islands), "연결성분", wq.n_components)
w.transform = "r"
wq.transform = "r"
res = {}
for col in ["lq_vac", "lq_all"]:
    y = np.log(m[col].clip(lower=0.01))   # LQ는 비율 → 로그
    mi = esda.Moran(y, w, permutations=9999)
    res[col] = mi
    mq = esda.Moran(y, wq, permutations=9999)
    P(f"Moran's I log({col}) KNN6 = {mi.I:.3f} (z {mi.z_sim:.2f}, p {mi.p_sim:.4f}) | Queen = {mq.I:.3f} (p {mq.p_sim:.4f})")
uu = ug[ug.child >= 300].reset_index()
wu = libpysal.weights.Queen.from_dataframe(uu, use_index=False, silence_warnings=True)
wu.transform = "r"
for col in ["per1k_방학", "per1k_학기"]:
    mi = esda.Moran(np.log1p(uu[col]), wu, permutations=9999)
    P(f"Moran's I (결합 단위 {len(uu)}개) log1p({col}) = {mi.I:.3f}, p(perm) = {mi.p_sim:.4f}")

y = np.log(m.lq_vac.clip(lower=0.01))
lisa = esda.Moran_Local(y, w, permutations=9999, seed=1)
lab = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}
m["lisa"] = np.where(lisa.p_sim < 0.05, pd.Series(lisa.q).map(lab), "ns")
P("\nLISA (방학 LQ, p<0.05):", m.lisa.value_counts().to_dict())
for k in ["LL", "HH"]:
    P(f"{k}:", sorted(m.loc[m.lisa == k, "bkey"]))
P("LL ∩ U2:", sorted(m.loc[(m.lisa == "LL") & (m.type_vac == "U2"), "bkey"]))
m[["bkey", "lq_vac", "lisa", "type_vac"]].to_csv(OUT / "lisa_lq_vac_INTERNAL.csv", index=False, encoding="utf-8-sig")

# 공표 그림: 방학 칸이 억제된 동은 군집 라벨을 지우고 빗금(계산에는 포함, D-017)
mp = m[m.bkey.isin(pub_vac)]
P("LISA 라벨 공표 동", int((mp.lisa != "ns").sum()), "/ 라벨 삭제(억제 동)", int(((m.lisa != "ns") & ~m.bkey.isin(pub_vac)).sum()))
fig, ax = plt.subplots(figsize=(9, 10))
base(ax)
g[g.pub].plot(ax=ax, color="#eeeeee", edgecolor="white", linewidth=0.2)
g[~g.pub].plot(ax=ax, color="#d9d9d9", edgecolor="white", linewidth=0.2, hatch="///")
lc = {"HH": "#2166ac", "LL": "#b2182b", "LH": "#f4a582", "HL": "#92c5de"}
for k, c in lc.items():
    mp[mp.lisa == k].plot(ax=ax, color=c, edgecolor="white", linewidth=0.2)
ax.legend(handles=[Patch(color=c, label=k) for k, c in lc.items()] + [Patch(color="#eeeeee", label="유의하지 않음"),
          Patch(facecolor="#d9d9d9", hatch="///", label="억제·값 없음")],
          loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=9, title="LISA, 방학 LQ (p<0.05)")
ax.set_title(f"방학 급식 LQ 공간 군집 — Moran's I = {res['lq_vac'].I:.2f} (p = {res['lq_vac'].p_sim:.4f})", fontsize=12)
fig.savefig(FIG / "map_lisa_lq_vac.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---- 분모 교차 점검: U2 동이 속한 결합 단위의 아동 1천 명당 방학 결제 ------------------------
# 일반 배달 분모는 직장·산업단지 수요가 크면 LQ를 낮춘다. 아동 기준으로도 낮아야 U2를 '견고'로 본다.
med = u.loc[u.child >= 300, "per1k_방학"].median()
c = b[b.type_vac == "U2"][["gen", "lq_vac", "type_all", "unit_id"]].copy()
c["unit_per1k_vac"] = c.unit_id.map(u["per1k_방학"])
c["unit_child"] = c.unit_id.map(u.child)
c["robust"] = np.where(c.unit_child < 300, "단위 아동<300",
                       np.where(c.unit_per1k_vac < med, "견고(아동 기준도 중앙값 미만)", "분모 의존(아동 기준은 중앙값 이상)"))
P(f"\nU2 분모 교차 점검 (결합 단위 방학 아동 1천 명당 중앙값 {med:.1f})")
P(c.robust.value_counts().to_string())
P(c.sort_values("gen", ascending=False).round(2).to_string())
c.to_csv(OUT / "u2_denominator_check_INTERNAL.csv", encoding="utf-8-sig")
log.close()
