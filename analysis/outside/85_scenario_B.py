"""시나리오 B(이용 회복) 골격 + A(공급 확대, MCLP)와 같은 단위로 비교 — 가정 층(D-018).

공통 결과 단위: 방학 한 달에 급식카드를 쓰는 계정 증가분(계정 ≠ 아동).
  A. 공급 확대: 새로 커버되는 아동 × 대구 방학 월 이용률(계정/아동). 새로 커버된 아이가 대구 평균만큼 쓴다는
     가정이라 A에 유리한 상한이다.
  B1. 이용 회복(동): 대상 동의 방학 LQ를 목표 tau까지 올린다. 늘어나는 방학 결제 = max(0, tau·기준비중·일반결제 − 방학 급식)
      → 6개월로 나눠 월 결제 → 대구 방학 "계정당 월 결제"로 나눠 계정.
      대상: 먼저 확인 9곳 / 1순위 17곳 / U2 37곳. tau ∈ {0.8, 1.0}.
  B2. 학기 회복(달성군 남부): 논공·유가·구지·옥포·현풍 단위의 학기 아동 1천 명당 월 결제를 대구 단위 중앙값까지 올린다
      → 학기 월 계정 증가(학기 계정당 월 결제로 환산). 단위가 학기라 A·B1과 따로 표기.
공표: 대상 집합 합계만. 동별 증가분은 억제 전 값에서 나오므로 내부용.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"
FIG = Path(__file__).resolve().parent / "fig"
log = open(OUT / "85_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


# ---- 대구 전체 환산 계수 (2차 month_group + 주민등록 인구) --------------------------------------
mg = pd.read_csv(ROOT / "9_18_데이터분석 결과물/EXPORT_m2_month_group.csv", dtype={"ym": str})
pop = pd.read_csv(OUT / "pop_gungu_month_6_18.csv", dtype={"ym": str})
mg = mg.merge(pop[pop.gu == "대구"][["ym", "child", "R"]], on="ym")
k = mg.groupby("R").agg(n=("n", "mean"), cust=("n_cust", "mean"), child=("child", "mean"))
k["pay_per_cust"] = k.n / k.cust             # 계정당 월 결제
k["cust_per_child"] = k.cust / k.child        # 아동 1명당 월 이용 계정
P("[환산 계수] 레짐별 월평균\n", k.round(4).to_string())
vac = k.loc["방학"]

# ---- A: MCLP 결과를 계정으로 --------------------------------------------------------------
A = pd.read_csv(OUT / "mclp_grid_results.csv")
A = A[A.new_children > 0].copy()
A["acc_month"] = A.new_children * vac.cust_per_child
a_best = A.groupby("act").agg(new_children=("new_children", "max"), acc_month=("acc_month", "max"))
P("\n[A 공급 확대] 포화되지 않은 설정 중 최대 (새로 커버 아동 → 방학 월 계정 상한)\n", a_best.round(1).to_string())

# ---- B1: 대상 동 방학 이용 회복 ------------------------------------------------------------
b = pd.read_csv(OUT / "bdong_types_INTERNAL.csv").set_index("dong")
b = b[b.gen > 0]
base = b.meal_vac.sum() / b.gen.sum()
chk = pd.read_csv(OUT / "u2_denominator_check_INTERNAL.csv").set_index("dong")
nbr = pd.read_csv(OUT / "neighbor_check_INTERNAL.csv").set_index("dong")
SETS = {"먼저 확인 9곳": list(nbr[nbr.verdict == "주변도 함께 적음"].index),
        "1순위 17곳": list(chk[chk.robust.str.startswith("견고")].index),
        "U2 37곳": list(b[b.type_vac == "U2"].index)}
rows = []
for name, ds in SETS.items():
    s = b.loc[[d for d in ds if d in b.index]]
    for tau in [0.8, 1.0]:
        add6 = np.maximum(tau * base * s.gen - s.meal_vac, 0).sum()      # 방학 6개월 동안 늘어나는 결제
        pay_m = add6 / 6
        rows.append(dict(scenario="B1 이용 회복", target=name, n_dong=len(s), tau=tau,
                         now_vac_month=s.meal_vac.sum() / 6, add_pay_month=pay_m,
                         acc_month=pay_m / vac.pay_per_cust))
B1 = pd.DataFrame(rows)
P(f"\n[B1 이용 회복] 대구 방학 기준 비중 {base:.4f}\n", B1.round(1).to_string(index=False))

# ---- B2: 달성군 남부 학기 회복 ---------------------------------------------------------------
u = pd.read_csv(OUT / "units_per_child.csv").set_index("unit_id")
sem = k.loc["학기"]
med_sem = u.loc[u.child >= 300, "per1k_학기"].median()
south = u[u.hdongs.str.contains("논공읍|유가읍|구지면|옥포읍|현풍읍")]
gap = np.maximum(med_sem - south.per1k_학기, 0) * south.child / 1000      # 학기 월 결제 증가
B2 = dict(units=len(south), child=int(south.child.sum()), med_sem=med_sem,
          now_sem_month=float((south.per1k_학기 * south.child / 1000).sum()),
          add_pay_month=float(gap.sum()), acc_month=float(gap.sum() / sem.pay_per_cust))
P(f"\n[B2 학기 회복·달성군 남부] {pd.Series(B2).round(1).to_dict()}")
P(south[["hdongs", "child", "per1k_학기", "per1k_방학"]].round(2).to_string())

# ---- 비교표 --------------------------------------------------------------------------------
cmp_rows = [dict(수단="A 공급 확대: 가게 모집 (5~10개 동)", 기간="방학", 늘어나는_월_계정=a_best.loc["모집", "acc_month"]),
            dict(수단="A 공급 확대: 쉬는 가게 활성화 (5~10개 동)", 기간="방학", 늘어나는_월_계정=a_best.loc["활성화", "acc_month"])]
for _, r in B1.iterrows():
    cmp_rows.append(dict(수단=f"B1 이용 회복: {r.target} → 평균의 {r.tau:.0%}", 기간="방학", 늘어나는_월_계정=r.acc_month))
cmp_rows.append(dict(수단="B2 학기 회복: 달성군 남부 5개 읍면 → 대구 중앙값", 기간="학기", 늘어나는_월_계정=B2["acc_month"]))
cmp = pd.DataFrame(cmp_rows)
P(f"\n[비교] 대구 방학 월평균 이용 계정 {vac.cust:.0f}, 학기 {sem.cust:.0f}\n", cmp.round(1).to_string(index=False))
cmp.to_csv(OUT / "scenario_AB_compare.csv", index=False, encoding="utf-8-sig")
B1.to_csv(OUT / "scenario_B1.csv", index=False, encoding="utf-8-sig")

# ---- 그림: 방학 월 계정 증가 비교 (가로 막대) ------------------------------------------------------
plt.rcParams["font.family"] = "Malgun Gothic"
show = cmp[cmp.기간 == "방학"].copy()
show = show[~show.수단.str.contains("U2 37곳")]
colors = ["#86b6ef" if s.startswith("A") else "#1c5cab" for s in show.수단]
fig, ax = plt.subplots(figsize=(10, 4.6), facecolor="white")
y = np.arange(len(show))[::-1]
ax.barh(y, show.늘어나는_월_계정, color=colors, height=0.6)
for yy, v in zip(y, show.늘어나는_월_계정):
    ax.text(v + 3, yy, f"{v:,.0f}", va="center", fontsize=10, color="#1a1a1a")
ax.set_yticks(y, show.수단, fontsize=10)
ax.set_xlabel("방학 한 달에 늘어나는 급식카드 이용 계정 (가정 하의 계산)", fontsize=10)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
ax.grid(axis="x", color="#e6e6e6")
ax.set_axisbelow(True)
ax.set_title("가게를 늘리는 것과 이용을 회복하는 것, 어느 쪽이 이용을 더 늘리나", loc="left", fontsize=12.5)
fig.text(0.01, -0.04, "A는 새로 커버된 아이가 대구 평균만큼 쓴다고 가정한 상한. B1은 대상 동의 방학 이용 비중을 대구 평균의 80%·100%로 올린 경우. "
         "계정 수는 아이 수와 같지 않다.", fontsize=8.5, color="#52514e")
fig.savefig(FIG / "v2_fig5_scenario_AB.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
log.close()
print("ok")
