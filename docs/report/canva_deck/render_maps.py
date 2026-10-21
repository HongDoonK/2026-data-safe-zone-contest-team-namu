"""기획서 덱(캔바용) 지도 이미지 — 대시보드 지도 자료(out_dashboard/geo.json)를 덱 색으로 다시 그린다.

글자(구 이름, 1순위 번호)는 이미지에 넣지 않고 위치만 maps_labels.json에 적는다.
덱 빌더가 그 위치에 텍스트 상자를 올려 글꼴을 덱과 맞추고 캔바에서 고칠 수 있게 한다.
공표 규칙(G8): 동 단위는 유형·번호만 쓴다. 지표 값은 그리지 않는다.
"""
import ast
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[3]
GEO = ROOT / "analysis" / "outside" / "out_dashboard" / "geo.json"
OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck_lib import AMBER, BG, NAVY, TEAL, UNDEC, mix  # noqa: E402  (덱과 같은 팔레트)

BASE, EDGE = mix(NAVY, 0.08, BG), "#FFFFFF"
KIND = {"confirmed": AMBER, "undecided": UNDEC, "exclude_nb": TEAL, "exclude_need": mix(TEAL, 0.5)}

rows = json.load(open(GEO, encoding="utf-8"))
for r in rows:
    g = r["geometry"]
    r["geometry"] = shape(ast.literal_eval(g) if isinstance(g, str) else g)
gdf = gpd.GeoDataFrame(rows, geometry="geometry")
dong = gdf[gdf.layer == "dong"].copy()
gu = gdf[gdf.layer == "gu"].copy()
x0, y0, x1, y1 = dong.total_bounds
pad = (x1 - x0) * 0.01
x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
W_IN = 8.0
H_IN = W_IN * (y1 - y0) / (x1 - x0)


def norm(x, y):
    return round((x - x0) / (x1 - x0), 4), round((y1 - y) / (y1 - y0), 4)


def draw(name, color_of):
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    dong.plot(ax=ax, color=[color_of(r) for r in dong.itertuples()], edgecolor=EDGE, linewidth=0.35)
    gu.boundary.plot(ax=ax, color=NAVY, linewidth=0.9, alpha=0.55)
    fig.savefig(OUT / f"{name}.png", transparent=True)
    plt.close(fig)


draw("map_targets", lambda r: AMBER if r.kind else BASE)
draw("map_types", lambda r: KIND.get(r.kind, BASE))

labels = {
    "aspect": round((y1 - y0) / (x1 - x0), 4),
    "gu": [dict(name=r.name, pos=norm(*r.geometry.representative_point().coords[0])) for r in gu.itertuples()],
    "targets": [dict(no=int(r.no), name=r.name, gu=r.gu, kind=r.kind, pos=norm(*r.geometry.representative_point().coords[0]))
                for r in dong[dong.kind != ""].itertuples()],
}
json.dump(labels, open(OUT / "maps_labels.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("maps:", OUT, "| aspect", labels["aspect"], "| targets", len(labels["targets"]))
