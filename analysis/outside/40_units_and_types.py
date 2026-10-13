"""센터 밖 분석 4 — 결합 단위별 아동 인구 대비 급식 이용 + 법정동 진단 유형(U1·U2).

U1/U2 기준(D-015, D-016으로 주 지표 변경):
  U1 등록 없음      : 등록 Y 가게 0 AND 일반 결제 > 0
  U2 등록 대비 미관측: 등록 Y 가게 >= 3 AND 급식 LQ가 '일반 결제 > 0인 법정동' 중 하위 25%
  주 분석 LQ = 방학(1·2·8월) 급식 / 25개월 일반 결제 (D-016). 민감도 = 25개월 급식 / 25개월 일반.
  일반 결제의 동 × 레짐 값은 반출되지 않아 분모는 전 기간이다(일반 결제의 계절성이 동 간에 같다는 가정).
분류는 억제 전 내부 값으로 하고, 공표용 표는 억제 규칙을 따른다.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
E3 = ROOT / "10_2_데이터분석결과물"
OUT = Path(__file__).resolve().parent / "out"
K, Q = 3, 0.25
log = open(OUT / "40_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


r = pd.read_csv(E3 / "EXPORT_m4_dong_regime.csv")
dt = pd.read_csv(E3 / "EXPORT_m4_dong_total.csv").set_index("dong")
km = pd.read_csv(OUT / "bridge_shopkey_unit.csv").set_index("dong").unit_id
units = pd.read_csv(OUT / "bridge_units.csv").set_index("unit_id")
pop = pd.read_csv(OUT / "pop_hdong_month_6_18.csv", dtype={"hcode": str, "ym": str})
br = pd.read_csv(OUT / "bridge_bdong_hdong.csv", dtype={"행정동코드": str}).drop_duplicates("행정동코드")
mm = pop.ym.str[4:6]
pop["R"] = np.where(mm.isin(["01", "02", "08"]), "방학", np.where(mm.isin(["07", "12"]), "전환", "학기"))
pop["unit_id"] = pop.hcode.map(br.set_index("행정동코드").unit_id)
months = pop.drop_duplicates("ym").R.value_counts()

# ---- 1. 결합 단위 ---------------------------------------------------------
meal = r.assign(unit_id=r.dong.map(km)).groupby(["unit_id", "R"]).n.sum().unstack(fill_value=0)
# 단위 아동 수 = 같은 달의 행정동 합 → 레짐(또는 전체) 월평균. (2026-10-12 수정: 이전에는 행정동-월 행의 평균이라 다행정동 단위가 과소)
monthly = pop.groupby(["unit_id", "ym", "R"]).child.sum().reset_index()
child = monthly.groupby(["unit_id", "R"]).child.mean().unstack()
d = dt.assign(unit_id=dt.index.map(km))
u = units[["gu", "hdongs", "n_h", "n_b"]].copy()
u["child"] = monthly.groupby("unit_id").child.mean()
u["meal"] = meal.sum(1)
u["gen"] = d.groupby("unit_id").gen.sum()
u["shops"] = d.groupby("unit_id").shops.sum()
u["able_y"] = d.groupby("unit_id").able_y.sum()
u = u.fillna({"meal": 0})
for R in ["방학", "전환", "학기"]:
    u[f"per1k_{R}"] = meal.get(R, 0).reindex(u.index).fillna(0) / months[R] / child[R] * 1000
u["per1k_all"] = u.meal / 25 / u.child * 1000
u["vac_sem"] = u["per1k_방학"] / u["per1k_학기"].replace(0, np.nan)
u["lq_gen"] = (u.meal / u.gen) / (u.meal.sum() / u.gen.sum())
u["lq_child"] = (u.meal / u.meal.sum()) / (u.child / u.child.sum())
P("결합 단위", len(u), "| 급식 결제 배정", int(u.meal.sum()), "/ 341,216")
P("단위 아동 수 분포:", u.child.describe().round(0).to_dict())
P("spearman lq_gen vs lq_child:", round(u[["lq_gen", "lq_child"]].corr("spearman").iloc[0, 1], 3),
  "| per1k_학기 vs per1k_방학:", round(u[["per1k_학기", "per1k_방학"]].corr("spearman").iloc[0, 1], 3))
cols = ["gu", "hdongs", "child", "meal", "per1k_학기", "per1k_방학", "vac_sem", "lq_child", "lq_gen"]
big = u[u.child >= 1000]
P(f"\n아동 1,000명 이상 단위 {len(big)}개 — 학기 아동 1천 명당 월 급식 하위 12")
P(big.sort_values("per1k_학기")[cols].head(12).round(2).to_string())
P("\n— 상위 8")
P(big.sort_values("per1k_학기")[cols].tail(8).round(2).to_string())
P("\n— 방학/학기 배율 상위 10")
P(big.sort_values("vac_sem", ascending=False)[cols].head(10).round(2).to_string())
u.to_csv(OUT / "units_per_child.csv", encoding="utf-8-sig")

# ---- 2. 법정동 진단 유형 ----------------------------------------------------
b = dt[["shops", "able_y", "gen"]].copy()
b["meal"] = r.groupby("dong").n.sum().reindex(b.index).fillna(0)   # 내부 값(억제 전)
b["meal_vac"] = r[r.R == "방학"].groupby("dong").n.sum().reindex(b.index).fillna(0)
b = b.drop(index=[x for x in b.index if x.endswith("|")])           # 동 이름 없는 키 제외
act = b[b.gen > 0].copy()
unclass = b.gen.isna() | b.able_y.isna()
for tag, col in [("vac", "meal_vac"), ("all", "meal")]:
    lq = (act[col] / act.gen) / (act[col].sum() / act.gen.sum())
    cut = lq.quantile(Q)
    b[f"lq_{tag}"] = lq
    t = pd.Series("U0", index=b.index)
    t[(b.able_y == 0) & (b.gen > 0)] = "U1"
    t[(b.able_y >= K) & (b[f"lq_{tag}"] <= cut)] = "U2"
    t[unclass] = "분류불가(가게<3 억제)"
    b[f"type_{tag}"] = t
    name = "주 분석: 방학" if tag == "vac" else "민감도: 25개월"
    P(f"\n[{name}] 법정동 유형 (k={K}, LQ 하위 {Q:.0%} 컷 = {cut:.3f}, 모집단 {len(act)}개 동)")
    P(t.value_counts().to_string())
    P("군구별 U2:", b[t == "U2"].index.str.split("|").str[0].value_counts().to_dict())
b["unit_id"] = b.index.map(km)
P("\n주 분석 vs 민감도 교차:\n", pd.crosstab(b.type_vac, b.type_all).to_string())
P("\nU1 등록 없음:\n", b[b.type_vac == "U1"][["shops", "gen", "meal"]].to_string())
cols = ["shops", "able_y", "gen", "meal_vac", "lq_vac", "lq_all", "type_all", "unit_id"]
P("\n[주 분석] U2 (일반결제 많은 순):\n",
  b[b.type_vac == "U2"][cols].sort_values("gen", ascending=False).round(3).to_string())
P("\n민감도에서만 U2:\n", b[(b.type_all == "U2") & (b.type_vac != "U2")][cols].round(3).to_string())
P("\nspearman lq_vac vs lq_all:", round(b[["lq_vac", "lq_all"]].corr("spearman").iloc[0, 1], 3))
b.to_csv(OUT / "bdong_types_INTERNAL.csv", encoding="utf-8-sig")
log.close()
