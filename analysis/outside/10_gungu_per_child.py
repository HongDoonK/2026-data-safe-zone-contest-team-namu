"""센터 밖 분석 1 — 군구 아동 인구(6~18세) 대비 급식 이용, 반출물 재억제.

입력: 반출물(9_18, 10_2) + data_external/population (주민등록 연령별 인구, 군구·월)
출력: analysis/outside/out/*.csv, 요약은 out/10_summary.txt
"""
import glob
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
E2 = ROOT / "9_18_데이터분석 결과물"
E3 = ROOT / "10_2_데이터분석결과물"
POP = ROOT / "data_external" / "population"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
log = open(OUT / "10_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


def regime(mm):
    return np.where(mm.isin(["01", "02", "08"]), "방학", np.where(mm.isin(["07", "12"]), "전환", "학기"))


# 1. 인구: 군구 × 월, 6~18세 ------------------------------------------------
rows = []
for f in sorted(glob.glob(str(POP / "*.csv"))):
    d = pd.read_csv(f, encoding="cp949", thousands=",")
    d["gu"] = d["행정구역"].str.extract(r"대구광역시\s*(\S*)\s*\(")[0].replace("", "대구")
    for c in d.columns:
        m = re.match(r"(\d{4})년(\d{2})월_계_(.+)", c)
        if m:
            for gu, v in zip(d.gu, d[c]):
                rows.append((m[1] + m[2], gu, m[3], v))
pop = pd.DataFrame(rows, columns=["ym", "gu", "k", "v"]).pivot_table(index=["ym", "gu"], columns="k", values="v")
ages = [f"{a}세" for a in range(6, 19)]
chk = (pop[ages].sum(1) - pop["연령구간인구수"]).abs().max()
P("인구 월 수:", pop.index.get_level_values(0).nunique(), "| 6~18 합 = 연령구간인구수 최대 오차:", chk)
pop = pop["연령구간인구수"].rename("child").reset_index()
pop = pop[pop.gu != "군위군"]  # 2023-07 대구 편입, 대구로 가맹점 없음
pop["R"] = regime(pop.ym.str[4:6])
P("대구 6~18세: 2023-06", int(pop.query("ym=='202306' & gu=='대구'").child.iloc[0]),
  "→ 2025-06", int(pop.query("ym=='202506' & gu=='대구'").child.iloc[0]))
pop.to_csv(OUT / "pop_gungu_month_6_18.csv", index=False, encoding="utf-8-sig")

# 2. 3차 레짐 파일 재억제 (반출 시 누락된 억제 복구) ---------------------------
r = pd.read_csv(E3 / "EXPORT_m4_dong_regime.csv")
bad = (r.n < 5) | (r.n_shop < 3) | (r.n_cust < 5)
rc = r.copy()
rc.loc[bad, ["n", "n_shop", "n_cust"]] = np.nan
k1 = bad.groupby(r.dong).sum()
P("레짐 재억제:", int(bad.sum()), "칸 / 억제 1칸뿐인 동", int((k1 == 1).sum()), "(공표 시 동 합계도 억제)")
rc.to_csv(OUT / "m4_dong_regime_resuppressed.csv", index=False, encoding="utf-8-sig")

# 3. 군구 × 레짐: 아동 1천 명당 월평균 급식 결제 ------------------------------
r["gu"] = r.dong.str.split("|").str[0]
meal = r.groupby(["gu", "R"]).n.sum()
months = pop[pop.gu == "대구"].groupby("R").ym.nunique()
child = pop.groupby(["gu", "R"]).child.mean()
t = pd.DataFrame({"meal": meal}).join(child)
t["months"] = t.index.get_level_values(1).map(months)
t["per1k_month"] = t.meal / t.months / t.child * 1000
w = t.per1k_month.unstack()
w["방학/학기"] = w["방학"] / w["학기"]
tot = t.groupby(level=0)[["meal"]].sum().join(pop[pop.gu != "대구"].groupby("gu").child.mean())
tot["per1k_month"] = tot.meal / 25 / tot.child * 1000
tot["child_share"] = tot.child / tot.child.sum()
tot["meal_share"] = tot.meal / tot.meal.sum()
# 일반 결제 LQ (3차 반출 dong_total, gen 억제 동 제외 — 작은 동 몇 곳 누락)
dt = pd.read_csv(E3 / "EXPORT_m4_dong_total.csv")
dt["gu"] = dt.dong.str.split("|").str[0]
gen = dt.groupby("gu").gen.sum()
tot["gen"] = gen
tot["lq_general"] = (tot.meal / tot.gen) / (tot.meal.sum() / tot.gen.sum())
tot["ratio_child"] = tot.meal_share / tot.child_share  # 아동 인구 기준 LQ
tot = tot.join(w)
P("\n레짐별 개월 수:", months.to_dict())
P("\n군구별 (25개월, 아동 1천 명당 월평균 급식 결제, 일반결제 LQ vs 아동인구 LQ)")
P(tot.round(3).sort_values("ratio_child").to_string())
P("\n순위 상관(spearman) lq_general vs ratio_child:",
  round(tot[["lq_general", "ratio_child"]].corr("spearman").iloc[0, 1], 3))
tot.to_csv(OUT / "gungu_per_child.csv", encoding="utf-8-sig")

# 4. 대구 전체 월별: 아동 1천 명당 급식 이용 계정·결제 (2차 m2_month_group) ------
mg = pd.read_csv(E2 / "EXPORT_m2_month_group.csv", dtype={"ym": str})
mg = mg.merge(pop[pop.gu == "대구"][["ym", "child", "R"]], on="ym", how="left")
mg["cust_per1k"] = mg.n_cust / mg.child * 1000
mg["meal_per1k"] = mg.n / mg.child * 1000
P("\n대구 월별 아동 1천 명당 급식 이용 계정(계정≠아동)")
P(mg[["ym", "R", "n", "n_cust", "child", "cust_per1k", "meal_per1k"]].round(2).to_string(index=False))
P("\n레짐별 평균 cust_per1k:", mg.groupby("R").cust_per1k.mean().round(2).to_dict())
yoy = mg.set_index("ym")
for a, b in [("202401", "202501"), ("202402", "202502"), ("202308", "202408")]:
    P(f"전년 동월 {a}→{b}: 계정/1천명 {yoy.cust_per1k[a]:.2f}→{yoy.cust_per1k[b]:.2f}, "
      f"아동 {int(yoy.child[a])}→{int(yoy.child[b])}")
mg.to_csv(OUT / "daegu_month_per_child.csv", index=False, encoding="utf-8-sig")
log.close()
