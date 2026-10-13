"""센터 밖 분석 6 — 확인 1순위 22곳의 '옆 동네 가게에서 산다' 가능성 점검 (확인표 이유 7).

이웃 = 경계가 맞닿은 법정동(5m 이내 틈 허용, 전체 290개 경계 기준 — 자료 유무와 무관하게 실제 인접).
지표(모두 방학, 억제 전 내부 값으로 계산 / 공표는 판정 라벨만):
  nb_lq   = 이웃 동 전체의 방학 급식 합 ÷ 이웃 동 전체의 일반 결제 합, 대구 평균 대비
  pool_lq = (자기 동 + 이웃) 합산 LQ
판정(2026-10-09, 결과 보기 전 고정):
  '옆 동네가 대신할 가능성 큼' : nb_lq >= 1.0 AND pool_lq >= 0.8
  '주변도 함께 적음'          : nb_lq < 0.8
  '중간'                      : 그 밖
"""
from pathlib import Path

import geopandas as gpd
import libpysal
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BD = ROOT / "data_external" / "boundary"
OUT = Path(__file__).resolve().parent / "out"
log = open(OUT / "70_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"], ri["code"] = umd.EMD_CD + "00", ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
br = pd.read_csv(OUT / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("법정동코드")
geo = geo.merge(br[["법정동코드", "bkey", "unit_id"]], left_on="code", right_on="법정동코드")
geo = geo.dissolve(by="bkey", aggfunc="first").reset_index()
# 맞닿음 판정: 경계 사이 5m 이내 틈은 맞닿은 것으로 본다(지적 경계의 미세한 틈 보정)
w = libpysal.weights.fuzzy_contiguity(geo, buffering=True, buffer=5, silence_warnings=True)
nb = {geo.bkey[i]: [geo.bkey[j] for j in w.neighbors[i]] for i in w.neighbors}

b = pd.read_csv(OUT / "bdong_types_INTERNAL.csv").set_index("dong")
b[["meal_vac", "gen"]] = b[["meal_vac", "gen"]].fillna(0)
base = b.meal_vac.sum() / b.gen.sum()
chk = pd.read_csv(OUT / "u2_denominator_check_INTERNAL.csv").set_index("dong")
top = chk[chk.robust.str.startswith("견고")].sort_values("gen", ascending=False)

rows = []
for d in top.index:
    if d not in nb:
        rows.append(dict(dong=d, n_nb=np.nan, verdict="경계 없음(주소 표기 불완전)"))
        continue
    ns = [x for x in nb[d] if x in b.index]
    s = b.loc[ns]
    nb_lq = (s.meal_vac.sum() / s.gen.sum()) / base if s.gen.sum() > 0 else np.nan
    pool = b.loc[ns + [d]]
    pool_lq = (pool.meal_vac.sum() / pool.gen.sum()) / base
    hi = s[(s.gen > 0) & ((s.meal_vac / s.gen) / base >= 1.25)].index.tolist()   # 이웃 중 '많음' 이상
    if nb_lq >= 1.0 and pool_lq >= 0.8:
        v = "옆 동네가 대신할 가능성 큼"
    elif nb_lq < 0.8:
        v = "주변도 함께 적음"
    else:
        v = "중간"
    rows.append(dict(dong=d, self_lq=b.at[d, "lq_vac"], n_nb=len(ns), nb_lq=nb_lq, pool_lq=pool_lq,
                     nb_high=",".join(x.split("|")[1] for x in hi), verdict=v))
r = pd.DataFrame(rows).set_index("dong")
P("확인 1순위", len(r), "| 대구 방학 기준 비중", round(base, 4))
P(r.verdict.value_counts().to_string())
P("\n" + r.round(2).to_string())
r.to_csv(OUT / "neighbor_check_INTERNAL.csv", encoding="utf-8-sig")
log.close()
