"""방학 급식 사각지대 점검표 — 0회차 지도와 요약 (해결책 4번, docs/topics/T2_checkup_tool.md).

90(판정표)·85(시나리오)를 같은 태그로 돌린 출력과 4차 반출의 방학 반기 파일을 읽어 그림 1장과 요약을 만든다.
판정·시나리오 계산은 바꾸지 않는다. 새로 계산하는 것은 지속성(방학 앞·뒤 반기 모두 낮은가) 하나다.
  --tag V4FBK   읽을 폴더 out_V4FBK
  --v4  DIR     EXPORT_v4_dong_vac_half.csv 가 있는 4차 반출 폴더
출력: out_TAG/fig/v2_map5_checkup.png, out_TAG/97_summary.txt
공표 규칙(G8): 그림에는 유형과 곳 수만 쓴다. 지표 값은 요약 파일(내부)에만 둔다.
"""
import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BD = ROOT / "data_external" / "boundary"
IN = HERE / "out"
Q = 0.25

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="V4FBK")
ap.add_argument("--v4", default=str(ROOT / "10_16_데이터분석결과물"))
A = ap.parse_args()
OUT = HERE / f"out_{A.tag}"
FIG = OUT / "fig"
FIG.mkdir(parents=True, exist_ok=True)
log = open(OUT / "97_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


INK, INK2, GU_LINE, DONG_LINE, BASE = "#1a1a1a", "#52514e", "#1a1a1a", "#9a9a9a", "#f6f6f4"
GU_NAME = {"27110": "중구", "27140": "동구", "27170": "서구", "27200": "남구",
           "27230": "북구", "27260": "수성구", "27290": "달서구", "27710": "달성군"}
GU_OFFSET = {"서구": (-1800, -1600), "북구": (2600, -900), "남구": (0, -1600)}
HALO = [pe.withStroke(linewidth=3, foreground="white")]
# 유형 → (그림 이름, 색). 처방이 필요한 쪽을 진하게, 제외는 옅게.
KIND = [("확정", "처방 확정 (배달형)", "#b8312f"), ("미확정", "확인 필요 (이유 미확정)", "#e9a23b"),
        ("옆동네", "제외: 옆 동네 가게 이용", "#86b6ef"), ("필요", "제외: 지원 필요 가구 적음", "#c4c3be")]
COL = {k: c for k, _, c in KIND}
NAME = {k: n for k, n, _ in KIND}


def kind(t):
    t = str(t)
    if t.startswith("처방 확정"):
        return "확정"
    if t.startswith("제외: 옆 동네"):
        return "옆동네"
    if t.startswith("제외: 필요"):
        return "필요"
    return "미확정"


# ---- 판정표·시나리오 --------------------------------------------------------------
r = pd.read_csv(OUT / "reason_table_INTERNAL.csv").set_index("dong")
t = r[r.target].copy()
t["k"] = t["유형"].map(kind)
order = {k: i for i, (k, _, _) in enumerate(KIND)}
t = t.assign(o=t.k.map(order)).sort_values(["o", "gu"])
t["no"] = range(1, len(t) + 1)
cnt = t.k.value_counts().reindex(order).fillna(0).astype(int)
P(f"[판정] 1순위 {len(t)}곳:", ", ".join(f"{NAME[k]} {cnt[k]}" for k in order))

sb = pd.read_csv(OUT / "scenario_B_dong_INTERNAL.csv").set_index("dong")
gap = sb.gap.groupby(sb.index.map(t.k)).sum()
excl = gap.reindex(["옆동네", "필요"]).fillna(0).sum()
P(f"[겉보기 부족분] 1순위 기대 − 실제 방학 월 결제 합 {gap.sum():.1f}건 중 제외 {excl:.1f}건 ({excl / gap.sum():.1%})")
P("  유형별:", gap.round(1).to_dict())
ab = pd.read_csv(OUT / "scenario_AB_compare.csv")
P("[시나리오 비교] 늘어나는 방학 월 계정 (하한~상한)")
for _, x in ab.iterrows():
    P(f"  {x['수단']}: {x['하한']:.1f} ~ {x['상한']:.1f}")

# ---- 지속성: 방학 앞(2023-08·2024-01·02)·뒤(2024-08·2025-01·02) 반기 모두 하위 25%인가 -----------------
b = pd.read_csv(IN / "bdong_types_INTERNAL.csv").set_index("dong")
hv = pd.read_csv(Path(A.v4) / "EXPORT_v4_dong_vac_half.csv", encoding="utf-8-sig").set_index("dong").dropna()
hv = hv[(hv["앞_gen"] > 0) & (hv["뒤_gen"] > 0) & hv.index.isin(b[b.able_y >= 3].index)]
for h in ["앞", "뒤"]:
    hv[f"lq_{h}"] = (hv[f"{h}_meal"] / hv[f"{h}_gen"]) / (hv[f"{h}_meal"].sum() / hv[f"{h}_gen"].sum())
    hv[f"low_{h}"] = hv[f"lq_{h}"] <= hv[f"lq_{h}"].quantile(Q)
rho = hv[["lq_앞", "lq_뒤"]].corr(method="spearman").iloc[0, 1]
P(f"\n[지속성] 두 반기 자료가 있는 동(등록 3곳 이상) {len(hv)}곳 | 앞·뒤 방학 LQ 순위 상관 {rho:.3f}")
both = (hv.low_앞 & hv.low_뒤).sum()
P(f"  어느 반기든 하위 25%인 동 {int((hv.low_앞 | hv.low_뒤).sum())}곳 중 두 반기 모두 {int(both)}곳")
t["persist"] = [("두 방학 모두 낮음" if hv.low_앞[d] and hv.low_뒤[d] else "한 방학만 낮음" if hv.low_앞[d] or hv.low_뒤[d]
                 else "두 방학 모두 낮지 않음") if d in hv.index else "자료 부족(억제)" for d in t.index]
P("  1순위 17곳:", t.persist.value_counts().to_dict())
P(t[["gu", "유형", "persist"]].to_string())

# ---- 경계 (55와 같은 방식) ------------------------------------------------------------
umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"], ri["code"] = umd.EMD_CD + "00", ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
br = pd.read_csv(IN / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("법정동코드")
geo = geo.merge(br[["법정동코드", "bkey"]], left_on="code", right_on="법정동코드")
geo = geo.dissolve(by="bkey", aggfunc="first").reset_index()
gu = umd[umd.COL_ADM_SE != "27720"].dissolve(by="COL_ADM_SE").reset_index()
gu["name"] = gu.COL_ADM_SE.map(GU_NAME)
g = geo.merge(t[["k", "no"]], left_on="bkey", right_index=True, how="left")
miss = sorted(set(t.index) - set(g.bkey))
P("\n[지도] 경계가 없는 1순위 동:", miss or "없음")

# 도심 확대: 중구 중심 4km 안의 1순위 동을 모두 담는다
jx0, jy0, jx1, jy1 = gu[gu.name == "중구"].total_bounds
cx, cy = (jx0 + jx1) / 2, (jy0 + jy1) / 2
tg = g[g.k.notna()].copy()
tg["pt"] = tg.geometry.representative_point()
near = tg[np.hypot(tg.pt.x - cx, tg.pt.y - cy) < 4000]
x0, y0, x1, y1 = near.total_bounds if len(near) else (jx0, jy0, jx1, jy1)
x0, y0, x1, y1 = min(x0, jx0) - 500, min(y0, jy0) - 500, max(x1, jx1) + 500, max(y1, jy1) + 500
w, h = x1 - x0, y1 - y0
if w / h < 1.0:
    x0, x1 = (x0 + x1) / 2 - h / 2, (x0 + x1) / 2 + h / 2
else:
    y0, y1 = (y0 + y1) / 2 - w / 2, (y0 + y1) / 2 + w / 2
ZOOM = (x0, y0, x1, y1)


def inside(p):
    return ZOOM[0] < p.x < ZOOM[2] and ZOOM[1] < p.y < ZOOM[3]


def draw(ax, zoom):
    ax.set_axis_off()
    g[g.k.isna()].plot(ax=ax, color=BASE, edgecolor="none", zorder=1)
    for k in order:
        s = g[g.k == k]
        if len(s):
            s.plot(ax=ax, color=COL[k], edgecolor="none", zorder=2)
    g.boundary.plot(ax=ax, color=DONG_LINE, linewidth=0.6 if zoom else 0.3, zorder=3)
    g[g.k.notna()].boundary.plot(ax=ax, color=INK, linewidth=2.0 if zoom else 1.4, zorder=5)
    gu.boundary.plot(ax=ax, color=GU_LINE, linewidth=2.2 if zoom else 1.6, zorder=6)
    for _, x in tg.iterrows():
        if inside(x.pt) == zoom or (not zoom and not inside(x.pt)):
            ax.text(x.pt.x, x.pt.y, str(int(x.no)), ha="center", va="center", fontsize=10 if zoom else 8.5,
                    fontweight="bold", color="white", zorder=10,
                    bbox=dict(boxstyle="circle,pad=0.22", fc=INK, ec="white", lw=1))
    if zoom:
        ax.set_xlim(ZOOM[0], ZOOM[2])
        ax.set_ylim(ZOOM[1], ZOOM[3])
        ax.set_aspect("equal", adjustable="box")
        ax.set_frame_on(True)
        for s in ax.spines.values():
            s.set_visible(True)
            s.set_edgecolor(INK2)
            s.set_linewidth(1.2)
        for _, x in gu.iterrows():
            p = x.geometry.representative_point()
            if inside(p):
                ax.text(p.x, p.y, x["name"], ha="center", va="center", fontsize=11, color=INK2,
                        path_effects=HALO, zorder=9)
    else:
        for _, x in gu.iterrows():
            if x["name"] == "중구":
                continue
            p = x.geometry.representative_point()
            dx, dy = GU_OFFSET.get(x["name"], (0, 0))
            ax.text(p.x + dx, p.y + dy, x["name"], ha="center", va="center", fontsize=12.5, fontweight="bold",
                    color=INK, path_effects=HALO, zorder=9)
        ax.add_patch(Rectangle((ZOOM[0], ZOOM[1]), ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1], fill=False,
                               edgecolor=INK2, linewidth=1.2, linestyle="--", zorder=8))
        ax.text(ZOOM[0], ZOOM[1] - 300, "도심 확대 →", ha="left", va="top", fontsize=9.5,
                fontweight="bold", color=INK, path_effects=HALO, zorder=9)


def nm(d):
    g_, n_ = d.split("|")
    return n_ if g_ == "달성군" else f"{g_} {n_}"


SHORT = {"확정": "처방 확정", "미확정": "확인 필요", "옆동네": "제외·옆 동네", "필요": "제외·필요 적음"}
fig = plt.figure(figsize=(16, 10.5), facecolor="white")
fig.text(0.02, 0.965, "방학 급식 사각지대 점검표 — 0회차 (2023-06~2025-06 대구로 결제)", fontsize=19,
         fontweight="bold", color=INK, va="top")
fig.text(0.02, 0.925, f"방학에 덜 쓰는 1순위 {len(t)}곳을, 결과를 보기 전에 정한 7가지 이유로 점검했다",
         fontsize=12, color=INK2, va="top")
ax = fig.add_axes([0.0, 0.19, 0.57, 0.71])
az = fig.add_axes([0.60, 0.50, 0.37, 0.37])
draw(ax, False)
draw(az, True)
az.set_title("도심 확대", fontsize=12, color=INK, loc="left")

# 점검 흐름: 17 → (제외 10 | 남은 7)
fx = fig.add_axes([0.60, 0.22, 0.38, 0.24])
n17 = len(t)
fx.set_xlim(0, n17)
fx.set_ylim(0, 3)
fx.set_axis_off()
fx.add_patch(Rectangle((0, 2.05), n17, 0.65, color=INK2))
fx.text(n17 / 2, 2.375, f"점검 전 · 방학에 덜 쓰는 1순위 {n17}곳", ha="center", va="center", fontsize=11.5,
        color="white", fontweight="bold")
fx.text(0, 1.8, "점검 후", fontsize=10.5, color=INK2, va="center")
x = 0
for k, lab in [("옆동네", "옆 동네"), ("필요", "필요 적음"), ("확정", "처방"), ("미확정", "확인")]:
    n = cnt[k]
    if n:
        fx.add_patch(Rectangle((x, 0.95), n, 0.65, color=COL[k], ec="white", lw=1.5))
        fx.text(x + n / 2, 1.275, f"{lab} {n}", ha="center", va="center", fontsize=10.5, fontweight="bold",
                color="white" if k == "확정" else INK)
    x += n
ne = cnt["옆동네"] + cnt["필요"]
for x0_, x1_, txt in [(0, ne, f"사각지대 아님 {ne}곳\n겉보기 부족분의 {excl / gap.sum():.0%}"),
                      (ne, n17, f"남은 {n17 - ne}곳")]:
    fx.plot([x0_ + 0.1, x0_ + 0.1, x1_ - 0.1, x1_ - 0.1], [0.82, 0.72, 0.72, 0.82], color=INK, lw=1.2)
    fx.text((x0_ + x1_) / 2, 0.6, txt, ha="center", va="top", fontsize=10.5, color=INK, linespacing=1.35)

persist = t[t.k == "확정"].persist.eq("두 방학 모두 낮음").sum()
notes = [(f"· 처방 확정 {cnt['확정']}곳은 모두" if persist == cnt["확정"] else f"· 처방 확정 {cnt['확정']}곳 중 {persist}곳은")
         + " 방학 앞·뒤 반기 연속 하위 25% (일시적 저조가 아님)",
         "· 이유 7가지: 필요(KCB 소득) · 다른 경로 · 주문받는 가게 · 1끼 가능 가게(앱 점검) ·",
         "  배달 여건 · 안내·신청 · 옆 동네 가게",
         "· 주문받는 가게(공급)는 4차 반출 결함으로 이번 회차 판단 불가"]
fig.text(0.60, 0.175, "\n".join(notes), fontsize=9.5, color=INK2, va="top", linespacing=1.5)

# 범례와 동 목록
h = [Patch(facecolor=c, edgecolor=INK, label=f"{n} ({cnt[k]}곳)") for k, n, c in KIND]
h += [Patch(facecolor=BASE, edgecolor=DONG_LINE, label="1순위 아님")]
fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.02, 0.105), ncol=3, fontsize=10.5, frameon=False,
           title="점검 결과 (굵은 테두리 = 1순위, 번호는 아래 목록)", title_fontsize=11, alignment="left")
lines = [f"{SHORT[k]} — " + " · ".join(f"{int(n)} {nm(d)}" for d, n in zip(t[t.k == k].index, t[t.k == k].no))
         for k in order if (t.k == k).any()]
fig.text(0.02, 0.095, "\n".join(lines), fontsize=9.5, color=INK, va="top", linespacing=1.6)
fig.savefig(FIG / "v2_map5_checkup.png", dpi=200, facecolor="white")
plt.close(fig)
P(f"\n그림: {FIG / 'v2_map5_checkup.png'}")
print("ok →", OUT.name, "|", dict(cnt))
