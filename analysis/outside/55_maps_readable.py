"""센터 밖 분석 5-b — 기획서용 지도 3종 (읽기 쉬운 판).

50_map_moran.py의 산출물(out/*)을 읽어 그림만 다시 그린다. 계산은 바꾸지 않는다.
공표 규칙: 방학 칸이 억제 기준을 통과한 동만 색칠, 나머지는 '자료 부족' 빗금(D-017).
색: dataviz 기준 팔레트. 발산 = 빨강(#b8312f·#ec8f86) ↔ 회색(#f0efec) ↔ 파랑(#86b6ef·#1c5cab),
순차 = 파랑 5단(#cde2fb→#0d366b, 지도는 흰 경계선으로 최저 단계도 구분). 각 팔 validate_palette.js --ordinal 통과.
"""
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["hatch.color"] = "#9a9a9a"
ROOT = Path(__file__).resolve().parents[2]
BD = ROOT / "data_external" / "boundary"
OUT = Path(__file__).resolve().parent / "out"
FIG = Path(__file__).resolve().parent / "fig"

INK, INK2, GU_LINE, DONG_LINE, NODATA = "#1a1a1a", "#52514e", "#1a1a1a", "#7a7a7a", "#e3e3e3"
GU_NAME = {"27110": "중구", "27140": "동구", "27170": "서구", "27200": "남구",
           "27230": "북구", "27260": "수성구", "27290": "달서구", "27710": "달성군"}
HALO = [pe.withStroke(linewidth=3, foreground="white")]

# ---- 경계 ---------------------------------------------------------------------
umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"], ri["code"] = umd.EMD_CD + "00", ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
br = pd.read_csv(OUT / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("법정동코드")
geo = geo.merge(br[["법정동코드", "bkey", "unit_id"]], left_on="code", right_on="법정동코드")
geo = geo.dissolve(by="bkey", aggfunc="first").reset_index()
gu = umd[umd.COL_ADM_SE != "27720"].dissolve(by="COL_ADM_SE").reset_index()
gu["name"] = gu.COL_ADM_SE.map(GU_NAME)

b = pd.read_csv(OUT / "bdong_types_INTERNAL.csv").set_index("dong")
rc = pd.read_csv(OUT / "m4_dong_regime_resuppressed.csv")
pub = set(rc[(rc.R == "방학") & rc.n.notna()].dong)
chk = pd.read_csv(OUT / "u2_denominator_check_INTERNAL.csv").set_index("dong")
lisa = pd.read_csv(OUT / "lisa_lq_vac_INTERNAL.csv").set_index("bkey")
g = geo.merge(b, left_on="bkey", right_index=True, how="left")
g["pub"] = g.bkey.isin(pub)
g["prio"] = g.bkey.map(chk.robust.map(lambda s: 1 if s.startswith("견고") else 2))
g["lisa"] = g.bkey.map(lisa.lisa)

# 도심 확대 범위: 중구 경계 + 여유
zx0, zy0, zx1, zy1 = gu[gu.name == "중구"].total_bounds
cx, cy, half = (zx0 + zx1) / 2, (zy0 + zy1) / 2, max(zx1 - zx0, zy1 - zy0) / 2 + 150
ZOOM = (cx - half * 1.04, cy - half, cx + half * 1.04, cy + half)   # 확대 패널 가로:세로 ≈ 1.04
GU_OFFSET = {"서구": (-1800, -1600), "북구": (2600, -900), "남구": (0, -1600)}


def short(k):
    return k.split("|")[1]


def frame(ax, zoom=False):
    ax.set_axis_off()
    g.boundary.plot(ax=ax, color=DONG_LINE, linewidth=0.35 if not zoom else 0.6, zorder=3)
    gu.boundary.plot(ax=ax, color=GU_LINE, linewidth=1.8 if not zoom else 2.4, zorder=6)
    if zoom:
        ax.set_xlim(ZOOM[0], ZOOM[2])
        ax.set_ylim(ZOOM[1], ZOOM[3])
        ax.set_aspect("equal", adjustable="box")
        for s in ax.spines.values():
            s.set_visible(True)
        ax.set_frame_on(True)
        for s in ax.spines.values():
            s.set_edgecolor(INK2)
            s.set_linewidth(1.2)
    else:
        for _, r in gu.iterrows():
            p = r.geometry.representative_point()
            if r["name"] == "중구":
                continue
            dx, dy = GU_OFFSET.get(r["name"], (0, 0))
            ax.text(p.x + dx, p.y + dy, r["name"], ha="center", va="center", fontsize=13, fontweight="bold",
                    color=INK, path_effects=HALO, zorder=9)
        ax.add_patch(Rectangle((ZOOM[0], ZOOM[1]), ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1],
                               fill=False, edgecolor=INK2, linewidth=1.2, linestyle="--", zorder=8))
        ax.text(ZOOM[0], ZOOM[3] + 300, "중구 (오른쪽 확대)", ha="left", va="bottom", fontsize=9.5,
                fontweight="bold", color=INK, path_effects=HALO, zorder=9)


def lock_zoom(ax):
    ax.set_xlim(ZOOM[0], ZOOM[2])
    ax.set_ylim(ZOOM[1], ZOOM[3])
    ax.set_aspect("equal", adjustable="box")


def nodata(ax):
    g[~g.pub].plot(ax=ax, color=NODATA, hatch="////", edgecolor="none", zorder=1)


def two_panel(title, subtitle):
    fig = plt.figure(figsize=(16, 11.5), facecolor="white")
    ax = fig.add_axes([0.0, 0.08, 0.60, 0.80])
    az = fig.add_axes([0.62, 0.40, 0.36, 0.48])
    fig.text(0.02, 0.965, title, fontsize=19, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.925, subtitle, fontsize=11.5, color=INK2, va="top")
    return fig, ax, az


# =========================== 그림 1: 방학 이용 수준 + 확인 우선 동 ===========================
bins = [0, 0.5, 0.8, 1.25, 2.0, np.inf]
cols = ["#b8312f", "#ec8f86", "#f0efec", "#86b6ef", "#1c5cab"]
labs = ["매우 적음 (대구 평균의 절반 미만)", "적음 (평균의 0.5~0.8배)", "평균 수준 (0.8~1.25배)",
        "많음 (1.25~2배)", "매우 많음 (2배 이상)"]
fig, ax, az = two_panel("방학에 아동급식카드를 얼마나 쓰는가 — 동네별 비교",
                        "같은 동네 일반 배달 주문 대비 급식카드 결제 비중을 대구 전체 평균과 비교 (2023-06~2025-06 방학: 1·2·8월)")
s = g[g.pub].copy()
s["cls"] = pd.cut(s.lq_vac, bins, labels=False, right=False)
p1 = g[g.prio == 1].sort_values("gen", ascending=False).reset_index(drop=True)
p1["no"] = range(1, len(p1) + 1)
for a, zoom in [(ax, False), (az, True)]:
    nodata(a)
    for i, c in enumerate(cols):
        s[s.cls == i].plot(ax=a, color=c, edgecolor="none", zorder=2)
    frame(a, zoom)
    g[g.prio == 2].boundary.plot(ax=a, color=INK, linewidth=1.3, linestyle=(0, (2, 1.5)), zorder=7)
    p1.boundary.plot(ax=a, color=INK, linewidth=2.6 if zoom else 2.0, zorder=7)
    for _, r in p1.iterrows():
        pt = r.geometry.representative_point()
        inside = ZOOM[0] < pt.x < ZOOM[2] and ZOOM[1] < pt.y < ZOOM[3]
        if zoom == inside or (not zoom and not inside):
            a.text(pt.x, pt.y, str(r.no), ha="center", va="center", fontsize=10 if zoom else 9,
                   fontweight="bold", color="white", zorder=10,
                   bbox=dict(boxstyle="circle,pad=0.25", fc=INK, ec="white", lw=1))
lock_zoom(az)
az.set_title("중구 확대 (작은 동이 많은 도심)", fontsize=12, color=INK, loc="left")
h = [Patch(facecolor=c, edgecolor=DONG_LINE, label=l) for c, l in zip(cols, labs)]
h += [Patch(facecolor=NODATA, hatch="////", edgecolor=DONG_LINE, label="자료 부족 (결제가 적어 공개 제한)"),
      Line2D([], [], color=INK, lw=2.6,
             label="현장 확인 1순위: 굵은 테두리 (등록 가게 대비 이용이 적고, 아동 수 기준으로도 적음 · 번호는 오른쪽 목록)"),
      Line2D([], [], color=INK, lw=1.4, ls=(0, (2, 1.5)), label="현장 확인 2순위 (일반 배달이 많아 적게 보일 수 있음)")]
fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.02, 0.0), ncol=2, fontsize=10.5, frameon=False,
           title="방학 급식카드 이용 수준", title_fontsize=11.5, alignment="left")
nomap = chk[chk.robust.str.startswith("견고") & ~chk.index.isin(p1.bkey)].index.tolist()
lst = "\n".join([f"{r.no:>2}. {r.bkey.split('|')[0]} {short(r.bkey)}" for _, r in p1.iterrows()]
                + [f"  · {k.split('|')[0]} {short(k)} (지도 표시 불가)" for k in nomap])
fig.text(0.63, 0.37, "현장 확인 1순위 동 (일반 배달 많은 순)", fontsize=11.5, fontweight="bold", color=INK, va="top")
half = (len(p1) + 1) // 2
rows = lst.split("\n")
fig.text(0.63, 0.34, "\n".join(rows[:half]), fontsize=10, color=INK, va="top", linespacing=1.45)
fig.text(0.80, 0.34, "\n".join(rows[half:]), fontsize=10, color=INK, va="top", linespacing=1.45)
fig.savefig(FIG / "v2_map1_vacation_use.png", dpi=200, facecolor="white")
plt.close(fig)

# =========================== 그림 2: 아동 1천 명당 (방학 vs 학기, 같은 눈금) ===========================
u = pd.read_csv(OUT / "units_per_child.csv").set_index("unit_id")
ug = geo.dissolve(by="unit_id").join(u[["per1k_방학", "per1k_학기", "child", "meal"]])
ug["ok"] = (ug.meal >= 5) & (ug.child >= 300)
sb = [0, 25, 75, 150, 300, np.inf]
sc = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
sl = ["25건 미만", "25~75건", "75~150건", "150~300건", "300건 이상"]
fig = plt.figure(figsize=(16, 9.5), facecolor="white")
fig.text(0.02, 0.965, "방학과 학기, 아동 1천 명당 한 달 급식카드 결제 건수", fontsize=19, fontweight="bold", color=INK, va="top")
fig.text(0.02, 0.92, "두 지도는 같은 눈금. 결제는 가게 위치 기준이며 아동 수는 그 지역 주민등록 6~18세 (2023-06~2025-06)",
         fontsize=11.5, color=INK2, va="top")
for i, (col, t) in enumerate([("per1k_방학", "방학 (1·2·8월)"), ("per1k_학기", "학기 (3~6·9~11월)")]):
    a = fig.add_axes([0.01 + i * 0.49, 0.10, 0.47, 0.76])
    a.set_axis_off()
    ug[~ug.ok].plot(ax=a, color=NODATA, hatch="////", edgecolor="none")
    q = ug[ug.ok].copy()
    q["cls"] = pd.cut(q[col], sb, labels=False, right=False)
    for j, c in enumerate(sc):
        q[q.cls == j].plot(ax=a, color=c, edgecolor="none")
    ug.boundary.plot(ax=a, color="white", linewidth=0.7)
    gu.boundary.plot(ax=a, color=GU_LINE, linewidth=1.8)
    for _, r in gu.iterrows():
        p = r.geometry.representative_point()
        if r["name"] != "중구":
            a.text(p.x, p.y, r["name"], ha="center", va="center", fontsize=11, fontweight="bold", color=INK,
                   path_effects=HALO)
    med = u.loc[u.child >= 300, col].median()
    a.set_title(f"{t}  ·  지역 중앙값 {med:.0f}건", fontsize=14, color=INK, loc="left")
h = [Patch(facecolor=c, label=l) for c, l in zip(sc, sl)] + [Patch(facecolor=NODATA, hatch="////", label="자료 부족")]
fig.legend(handles=h, loc="lower center", ncol=6, fontsize=11, frameon=False,
           title="아동 1천 명당 한 달 결제 건수", title_fontsize=11.5)
fig.savefig(FIG / "v2_map2_per_child.png", dpi=200, facecolor="white")
plt.close(fig)

# =========================== 그림 3: 이용이 뭉치는 곳 (LISA) ===========================
lc = {"HH": ("#1c5cab", "많이 쓰는 동네끼리 모여 있음"), "LL": ("#b8312f", "적게 쓰는 동네끼리 모여 있음"),
      "HL": ("#86b6ef", "주변보다 혼자 많이 씀"), "LH": ("#ec8f86", "주변보다 혼자 적게 씀")}
fig, ax, az = two_panel("방학 급식카드 이용이 '뭉쳐' 나타나는 곳",
                        "이웃 동네와 비교해 통계적으로 의미 있는 묶음만 색칠 (p < 0.05, 이웃 = 가까운 6개 동)")
for a, zoom in [(ax, False), (az, True)]:
    nodata(a)
    g[g.pub].plot(ax=a, color="#f6f6f4", edgecolor="none", zorder=1)
    for k, (c, _) in lc.items():
        g[g.pub & (g.lisa == k)].plot(ax=a, color=c, edgecolor="none", zorder=2)
    frame(a, zoom)
lock_zoom(az)
az.set_title("중구 확대 (작은 동이 많은 도심)", fontsize=12, color=INK, loc="left")
h = [Patch(facecolor=c, edgecolor=DONG_LINE, label=l) for c, l in lc.values()]
h += [Patch(facecolor="#f6f6f4", edgecolor=DONG_LINE, label="뚜렷한 묶음 없음"),
      Patch(facecolor=NODATA, hatch="////", edgecolor=DONG_LINE, label="자료 부족 (공개 제한)")]
fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.02, 0.0), ncol=3, fontsize=10.5, frameon=False,
           title="방학 급식카드 이용 수준의 공간 묶음", title_fontsize=11.5, alignment="left")
fig.text(0.63, 0.36,
         "읽는 법\n"
         "· 빨간 묶음 = 주변 동네까지 함께 이용이 적은 곳\n"
         "· 파란 묶음 = 주변 동네까지 함께 이용이 많은 곳\n\n"
         "주의\n"
         "· 달서구 서부(성서산업단지 주변)의 빨간 묶음은\n"
         "  직장인 배달 주문이 많아 비중이 낮게 보이는 효과가 크다.\n"
         "  아동 수 기준으로는 오히려 이용이 많은 편이다.\n"
         "· 결제는 가게 위치 기준이며 아동의 거주지가 아니다.",
         fontsize=10.5, color=INK, va="top", linespacing=1.5)
fig.savefig(FIG / "v2_map3_clusters.png", dpi=200, facecolor="white")
plt.close(fig)
print("ok")
