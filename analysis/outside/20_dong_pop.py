"""센터 밖 분석 2 — 대구 행정동 × 월 6~18세 인구 정리.

입력: data_external/population_dong/*.csv (주민등록 연령별 인구, 전국 행정동, 월별 파일)
출력: out/pop_hdong_month_6_18.csv, out/20_summary.txt
"""
import glob
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data_external" / "population_dong"
OUT = Path(__file__).resolve().parent / "out"
log = open(OUT / "20_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


rows = []
for f in sorted(glob.glob(str(SRC / "*.csv"))):
    d = pd.read_csv(f, encoding="cp949", thousands=",")
    d = d[d["행정구역"].str.startswith("대구광역시")]
    col = [c for c in d.columns if c.endswith("_계_연령구간인구수")][0]
    ym = re.match(r"(\d{4})년(\d{2})월", col)
    ym = ym[1] + ym[2]
    ages = [c for c in d.columns if re.search(r"_계_\d+세$", c)]
    assert (d[ages].sum(1) == d[col]).all(), f
    m = d["행정구역"].str.extract(r"대구광역시\s*(\S*)\s*(\S*)\s*\((\d{10})\)")
    m.columns = ["gu", "hdong", "hcode"]
    m["ym"], m["child"] = ym, d[col].values
    rows.append(m)
p = pd.concat(rows)
p = p[(p.hdong != "") & (p.gu != "군위군")]
P("월 수:", p.ym.nunique(), "| 행정동 코드 수(전체 기간):", p.hcode.nunique())
cnt = p.groupby("hcode").ym.nunique()
P("25개월 모두 있는 코드:", int((cnt == 25).sum()), "| 일부 월만:", p[p.hcode.isin(cnt[cnt < 25].index)]
  .groupby(["hcode", "gu", "hdong"]).ym.agg(["min", "max", "size"]).to_string())
zero = p.groupby("hcode").child.sum()
P("25개월 합 0인 코드:", p[p.hcode.isin(zero[zero == 0].index)][["gu", "hdong"]].drop_duplicates().values.tolist())
gu = p.groupby(["ym", "gu"]).child.sum().unstack()
P("\n군구 합(2023-06 / 2025-06):\n", gu.loc[["202306", "202506"]].T.to_string())
p.to_csv(OUT / "pop_hdong_month_6_18.csv", index=False, encoding="utf-8-sig")
log.close()
