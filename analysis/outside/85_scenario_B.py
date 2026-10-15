"""시나리오 B(이용 회복) + A(공급 확대, MCLP)와 같은 단위로 비교 — 가정 층(D-018, D-019 §4).

공통 결과 단위: 방학 한 달에 급식카드를 쓰는 계정 증가분(계정 ≠ 아동).

[10/12 골격] --v4·--reason 없이 돌리면 그대로 낸다(회귀).
  A. 공급 확대: 새로 커버되는 아동 × 대구 방학 월 이용률(계정/아동). 새로 커버된 아이가 대구 평균만큼 쓴다는
     가정이라 A에 유리한 상한이다.
  B1. 이용 회복(동): 대상 동의 방학 LQ를 목표 tau까지 올린다. 늘어나는 방학 결제 = max(0, tau·기준비중·일반결제 − 방학 급식)
      → 6개월로 나눠 월 결제 → 대구 방학 "계정당 월 결제"로 나눠 계정.
      대상: 먼저 확인 9곳 / 1순위 17곳 / U2 37곳. tau ∈ {0.8, 1.0}.
  B2. 학기 회복(달성군 남부): 논공·유가·구지·옥포·현풍 단위의 학기 아동 1천 명당 월 결제를 대구 단위 중앙값까지 올린다
      → 학기 월 계정 증가(학기 계정당 월 결제로 환산). 단위가 학기라 A·B1과 따로 표기.

[4차 교체] --v4 DIR 또는 --reason FILE. 80·90을 같은 --tag로 먼저 돌린다.
  A. 80의 주 설정 격자(is_main: 엄격 공급 × 흐름 닿음 tau 0.10 × KCB 무게)에서 행동별 최대 새 커버 무게.
     범위 = 억제 두 끝(fill lo·hi) 각각의 최대. 대구 전체 후보 / D-019 후보 단위(scope=후보) 두 줄. 여전히 A에 유리한 상한.
  B. 판정표(90 reason_table_INTERNAL.csv)의 1순위(target) 동을 유형별로:
       제외(옆 동네·필요 적음) → 0
       처방 확정 중 공급형 포함 → B에서는 0. 효과는 A(후보 단위 MCLP)에서 센다(이중 계산 방지)
       처방 확정(가격형·배달형·배달형(부분)) → 회복 몫 × {0.5, 1.0}
       잔여 추정(안내·신청) → 같은 계산, "추정"으로 따로
       미확정 → 0 ~ 회복 몫 × 1.0, "상한"으로만 따로
     회복 몫 = max(0, 기대 이용 − 실제 이용).
       기대 이용(단위): 결합 단위(아동 300명 이상) 방학 아동 1천 명당 월 급식 결제 y를
         log y ~ log 아동 수 + log 일반 배달(25개월)/아동 + log 주변(단위+맞닿은 동) 등록·영업 가게/아동 1천 (+ KCB 30·40대 저소득 비율)
         으로 맞춘 OLS의 leave-one-out 예측(자기 단위를 빼고 맞춘 값)을 exp로 되돌린 값(기하 평균 쪽, 보수적).
         민감도 1: 같은 설명 변수를 표준화한 공간에서 가장 가까운 10개 단위의 y 중앙값.
         민감도 2: 일반 배달을 뺀 모형(직장 배달이 많은 단위의 기대가 커지는 효과, D-017 우려를 뺀 값).
       A 표에는 "10/12 방식(주 공급의 모든 닿음 중 최대)" 참고 줄을 둔다(그림에는 넣지 않는다).
       동으로 나누기: 동 기대 = 단위 기대 × 아동/1000 × (동 일반 배달 / 단위 일반 배달), 동 부족분 = max(0, 동 기대 − 동 방학 월 급식).
         한 단위 안 1순위 동들의 부족분 합이 단위 부족분 max(0, 단위 기대 − 단위 실제)를 넘으면 비율대로 줄인다.
     계정 환산은 10/12와 같다(늘어난 방학 월 결제 ÷ 방학 계정당 월 결제).
  B2. 달성군 남부 학기 회복. 기준 = 대구 단위 중앙값(10/12) 또는 달성군 북부 읍(화원읍·다사읍) 합산 학기 이용률.
      --b2-ref daegu|north|both (4차 경로 기본 both).
공표: 유형·집합 합계만. 동별 값은 scenario_B_dong_INTERNAL.csv (억제 전 값에서 나온다).
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IN = HERE / "out"
RHO = (0.5, 1.0)                 # 처방 확정·추정의 회복 비율 범위
MIN_CHILD, KNN, VAC_MONTHS = 300, 10, 6
SOUTH, NORTH = "논공읍|유가읍|구지면|옥포읍|현풍읍", "화원읍|다사읍"

ap = argparse.ArgumentParser()
ap.add_argument("--v4")
ap.add_argument("--reason")
ap.add_argument("--tag", default="")
ap.add_argument("--b2-ref", dest="b2_ref", choices=["daegu", "north", "both"])
A_ = ap.parse_args()
OUT = HERE / (f"out_{A_.tag}" if A_.tag else "out")
FIG = (OUT / "fig") if A_.tag else (HERE / "fig")
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SYN = "SYN" in A_.tag.upper() or "SYNTHETIC" in str(A_.v4 or "").upper() or "SYN" in str(A_.reason or "").upper()
REQ = bool(A_.v4 or A_.reason)
reason_path = Path(A_.reason) if A_.reason else (OUT / "reason_table_INTERNAL.csv" if A_.v4 else None)
grid = pd.read_csv(OUT / "mclp_grid_results.csv")
NEWA = "is_main" in grid.columns
NEWB = reason_path is not None and reason_path.exists()
B2REF = A_.b2_ref or ("both" if (REQ or NEWA) else "daegu")
LEGACY = not REQ and not NEWA and B2REF == "daegu"
log = open(OUT / "85_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


# ---- 대구 전체 환산 계수 (2차 month_group + 주민등록 인구) --------------------------------------
mg = pd.read_csv(ROOT / "9_18_데이터분석 결과물/EXPORT_m2_month_group.csv", dtype={"ym": str})
pop = pd.read_csv(IN / "pop_gungu_month_6_18.csv", dtype={"ym": str})
mg = mg.merge(pop[pop.gu == "대구"][["ym", "child", "R"]], on="ym")
k = mg.groupby("R").agg(n=("n", "mean"), cust=("n_cust", "mean"), child=("child", "mean"))
k["pay_per_cust"] = k.n / k.cust             # 계정당 월 결제
k["cust_per_child"] = k.cust / k.child        # 아동 1명당 월 이용 계정
P("[환산 계수] 레짐별 월평균\n", k.round(4).to_string())
vac = k.loc["방학"]

if LEGACY:
    # ==== 10/12 골격 그대로 (회귀) =====================================================
    # ---- A: MCLP 결과를 계정으로 --------------------------------------------------------------
    A = grid
    A = A[A.new_children > 0].copy()
    A["acc_month"] = A.new_children * vac.cust_per_child
    a_best = A.groupby("act").agg(new_children=("new_children", "max"), acc_month=("acc_month", "max"))
    P("\n[A 공급 확대] 포화되지 않은 설정 중 최대 (새로 커버 아동 → 방학 월 계정 상한)\n", a_best.round(1).to_string())

    # ---- B1: 대상 동 방학 이용 회복 ------------------------------------------------------------
    b = pd.read_csv(IN / "bdong_types_INTERNAL.csv").set_index("dong")
    b = b[b.gen > 0]
    base = b.meal_vac.sum() / b.gen.sum()
    chk = pd.read_csv(IN / "u2_denominator_check_INTERNAL.csv").set_index("dong")
    nbr = pd.read_csv(IN / "neighbor_check_INTERNAL.csv").set_index("dong")
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
    u = pd.read_csv(IN / "units_per_child.csv").set_index("unit_id")
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
    raise SystemExit

# ==== 4차 교체 경로 =========================================================================
sem = k.loc["학기"]
u = pd.read_csv(IN / "units_per_child.csv").set_index("unit_id")
b = pd.read_csv(IN / "bdong_types_INTERNAL.csv").set_index("dong")
P(f"\n[입력] 태그 {A_.tag or '(없음 → out/, fig/)'} | 4차 폴더 {A_.v4 or '없음'} | 판정표 {reason_path if NEWB else '없음'}"
  f" | MCLP 격자 {'4차 형식' if NEWA else '10/12 형식'} | B2 기준 {B2REF}")
if REQ and not NEWB:
    P("  ※ 판정표가 없다 → B는 10/12 방식(B1 대구 평균 80·100%)으로만 계산한다. 90_reason_table.py를 같은 --tag로 먼저 돌릴 것")

# ---- A: MCLP 결과를 계정으로 ------------------------------------------------------------------
arows = []
if NEWA:
    bl = pd.read_csv(OUT / "mclp_baseline.csv")
    fills = list(bl.loc[bl.is_main, "fill"].unique())
    scopes = ["대구 전체"] + (["후보"] if (grid.scope == "후보").any() else [])
    main_cfg = bl.loc[bl.is_main, ["supply", "reach", "need"]].drop_duplicates().iloc[0].to_dict()
    P(f"\n[A] 80 주 설정: {main_cfg} | 억제 두 끝: {fills}")
    for scope in scopes:
        for act in ["모집", "활성화"]:
            s = grid[grid.is_main & (grid.scope == scope) & (grid.act == act)]
            mx = s.groupby("fill").new_children.max().reindex(fills).fillna(0.0)
            arows.append(dict(scope=scope, act=act, runs=len(s), new_lo=float(mx.min()), new_hi=float(mx.max())))
    sens = grid[grid.scope == "대구 전체"].groupby(["reach", "fill", "act"]).new_children.max().unstack("act") * vac.cust_per_child
    P("  닿음·억제 끝별 최대 방학 월 계정 (대구 전체, 민감도):\n", sens.round(1).to_string())
    g_all = grid[(grid.scope == "대구 전체") & (grid.supply == main_cfg["supply"])]
    A_old = {act: float(g_all.loc[g_all.act == act, "new_children"].max()) if (g_all.act == act).any() else 0.0
             for act in ["모집", "활성화"]}
    P("  참고(10/12 방식 = 주 공급의 모든 닿음·억제 끝 중 최대) 방학 월 계정:",
      {a: round(float(v * vac.cust_per_child), 1) for a, v in A_old.items()})
else:
    g = grid[grid.new_children > 0]
    for act in ["모집", "활성화"]:
        v = float(g.loc[g.act == act, "new_children"].max()) if (g.act == act).any() else 0.0
        arows.append(dict(scope="대구 전체", act=act, runs=int((grid.act == act).sum()), new_lo=v, new_hi=v))
At = pd.DataFrame(arows)
At["acc_lo"], At["acc_hi"] = At.new_lo * vac.cust_per_child, At.new_hi * vac.cust_per_child
P("\n[A 공급 확대] 새로 커버되는 무게(아동) → 방학 월 계정 상한. 범위 = 억제 두 끝\n", At.round(1).to_string(index=False))

# ---- B: 판정 유형별 이용 회복 -----------------------------------------------------------------
cmp_rows = []
SCOPE_NAME = {"대구 전체": "A 공급 확대(대구 어디서나)", "후보": "A 공급형 처방(D-019 후보 단위)"}
for _, r in At.iterrows():
    cmp_rows.append(dict(수단=f"{SCOPE_NAME[r.scope]}: {'가게 모집' if r.act == '모집' else '쉬는 가게 활성화'}",
                         기간="방학", 지위="A 상한(가정)", n_dong=np.nan, 하한=r.acc_lo, 상한=r.acc_hi))
if NEWA:
    for act, v in A_old.items():
        cmp_rows.append(dict(수단=f"참고: A 10/12 방식(모든 닿음 중 최대): {'가게 모집' if act == '모집' else '쉬는 가게 활성화'}",
                             기간="방학", 지위="참고(A 10/12 방식)", n_dong=np.nan,
                             하한=v * vac.cust_per_child, 상한=v * vac.cust_per_child))
dong_out = None
if NEWB:
    rt = pd.read_csv(reason_path).set_index("dong")
    tg = rt[rt.target.astype(str).str.lower() == "true"].copy()
    uif = OUT / "mclp_unit_inputs_INTERNAL.csv"
    if not uif.exists():
        raise SystemExit(f"{uif} 없음 — 80_mclp_skeleton.py를 같은 --tag(와 --v4 또는 --cand)로 먼저 돌린다")
    ui = pd.read_csv(uif).set_index("unit_id")

    # 기대 이용 모형 (결합 단위, 아동 300명 이상)
    UP = u[u.child >= MIN_CHILD].index
    X = pd.DataFrame(index=u.index)
    X["log_아동"] = np.log(u.child)
    X["log_일반배달_아동당"] = np.log((u.gen.fillna(0) / u.child).clip(lower=1e-3))
    X["log_주변등록영업가게_아동1천당"] = np.log(ui.able_adj_per1k.reindex(u.index).clip(lower=0.1))
    nm = ui.need_mid.reindex(u.index)
    if nm.notna().any():
        rbar = (u.child * nm).sum() / u.child[nm.notna()].sum()
        X["KCB_3040_저소득비율"] = nm.fillna(rbar)
    y = np.log(u["per1k_방학"].clip(lower=1e-3))
    yU = y.loc[UP]

    def fit_loo(cols):
        """OLS(로그 선형)를 맞추고 leave-one-out 예측을 exp로 되돌린다."""
        XU = X.loc[UP, cols]
        Xm = np.column_stack([np.ones(len(XU)), XU.values])
        XtXi = np.linalg.pinv(Xm.T @ Xm)
        beta = XtXi @ Xm.T @ yU.values
        e = yU.values - Xm @ beta
        h = np.einsum("ij,jk,ik->i", Xm, XtXi, Xm)
        loo = yU.values - e / (1 - h)
        se = np.sqrt(np.diag(XtXi) * (e ** 2).sum() / (len(yU) - Xm.shape[1]))
        coef = pd.DataFrame({"계수": beta, "표준오차": se}, index=["절편"] + cols)
        r2 = 1 - (e ** 2).sum() / ((yU - yU.mean()) ** 2).sum()
        return pd.Series(np.exp(loo), index=UP), coef, r2, np.sqrt(np.mean((yU.values - loo) ** 2))

    E_reg, coef, r2, rmse = fit_loo(list(X.columns))
    E_nog, coef_nog, r2_nog, rmse_nog = fit_loo([c for c in X.columns if not c.startswith("log_일반배달")])
    XU = X.loc[UP]
    Z = (XU - XU.mean()) / XU.std(ddof=0).replace(0, 1)
    dist = np.sqrt(((Z.values[:, None, :] - Z.values[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(dist, np.inf)
    nn = np.argsort(dist, axis=1)[:, :KNN]
    E_knn = pd.Series(np.median(np.exp(yU.values)[nn], axis=1), index=UP)
    P(f"\n[기대 이용 모형] 결합 단위 {len(UP)}곳(아동 {MIN_CHILD}명 이상), y = log 방학 아동 1천 명당 월 급식 결제")
    P(coef.round(3).to_string())
    P(f"  R² {r2:.3f} | LOO 오차(로그) RMSE {rmse:.3f} | 실제 < 기대(LOO) 단위 {int((np.exp(yU) < E_reg).sum())}곳")
    P(f"  민감도 1: 가까운 {KNN}개 단위 중앙값 (주 모형과 순위 상관 {E_reg.corr(E_knn, method='spearman'):.2f})")
    P(f"  민감도 2: 일반 배달 뺀 모형 R² {r2_nog:.3f}, LOO RMSE {rmse_nog:.3f} (주 모형과 순위 상관 "
      f"{E_reg.corr(E_nog, method='spearman'):.2f}) — 일반 배달이 많은 단위의 기대가 커지는 효과(D-017 우려)를 뺀 값")

    ugen = b.gen.fillna(0).groupby(b.unit_id).sum()
    uact = b.meal_vac.fillna(0).groupby(b.unit_id).sum() / VAC_MONTHS
    tg["unit_id"] = tg.unit_id.astype(str)
    tg["s"] = b.gen.reindex(tg.index).fillna(0) / tg.unit_id.map(ugen)
    tg["act_m"] = b.meal_vac.reindex(tg.index).fillna(0) / VAC_MONTHS

    def gaps(E):
        exp_u = E * u.child.reindex(E.index) / 1000
        gap_u = (exp_u - uact.reindex(E.index).fillna(0)).clip(lower=0)
        sf = (tg.unit_id.map(exp_u) * tg.s - tg.act_m).clip(lower=0)
        tot = sf.groupby(tg.unit_id).transform("sum")
        f = np.minimum(1.0, tg.unit_id.map(gap_u) / tot.replace(0, np.nan)).fillna(0)
        return (sf * f).fillna(0), tg.unit_id.map(exp_u) * tg.s

    tg["gap"], tg["exp_m"] = gaps(E_reg)
    tg["gap_knn"], _ = gaps(E_knn)
    tg["gap_nogen"], _ = gaps(E_nog)
    P(f"  1순위 {len(tg)}곳 중 단위가 모형 밖(아동 < {MIN_CHILD}): {int((~tg.unit_id.isin(UP)).sum())}곳 → 회복 몫 0")

    def btype(s):
        s = str(s)
        body = s.split(":", 1)[1].strip() if ":" in s else s
        if s.startswith("제외"):
            return "제외", body
        if s.startswith("처방 확정"):
            return ("A로(공급형)", body) if "공급형" in body else ("확정", body)
        if s.startswith("잔여 추정"):
            return "추정", body
        return "상한", "이유 미확정"

    tg[["status", "group"]] = pd.DataFrame([btype(s) for s in tg["유형"]], index=tg.index)
    lo_r = tg.status.map({"확정": RHO[0], "추정": RHO[0]}).fillna(0.0)
    hi_r = tg.status.map({"확정": RHO[1], "추정": RHO[1], "상한": 1.0}).fillna(0.0)
    tg["add_lo"], tg["add_hi"] = tg.gap * lo_r, tg.gap * hi_r
    tg["add_hi_knn"], tg["add_hi_nogen"] = tg.gap_knn * hi_r, tg.gap_nogen * hi_r
    for c in ["add_lo", "add_hi", "add_hi_knn", "add_hi_nogen"]:
        tg[c.replace("add", "acc")] = tg[c] / vac.pay_per_cust
    dong_out = tg[["gu", "unit_id", "유형", "status", "group", "s", "exp_m", "act_m", "gap", "gap_knn", "gap_nogen",
                   "add_lo", "add_hi", "acc_lo", "acc_hi", "acc_hi_knn", "acc_hi_nogen"]]
    dong_out.to_csv(OUT / "scenario_B_dong_INTERNAL.csv", encoding="utf-8-sig")

    agg = tg.groupby(["status", "group"]).agg(n_dong=("gap", "size"), now_vac_month=("act_m", "sum"), gap_month=("gap", "sum"),
                                              acc_lo=("acc_lo", "sum"), acc_hi=("acc_hi", "sum"),
                                              acc_hi_knn=("acc_hi_knn", "sum"), acc_hi_nogen=("acc_hi_nogen", "sum"))
    P(f"\n[B 판정 유형별] 1순위 {len(tg)}곳. 회복 비율 확정·추정 {RHO}, 미확정 0~1.0. 월 결제·월 계정 합계\n", agg.round(1).to_string())
    P("  " + " · ".join(f"{s} {n}곳" for s, n in tg.status.value_counts().items()))
    order = {"확정": 0, "추정": 1, "상한": 2, "A로(공급형)": 3, "제외": 4}
    STAT = {"확정": "B 확정(가정 하)", "추정": "B 추정(가정 하)", "상한": "B 상한(이유 미확정)",
            "A로(공급형)": "A로 보냄(B 0)", "제외": "제외(효과 0)"}
    for (st, grp), r in sorted(agg.iterrows(), key=lambda x: (order[x[0][0]], x[0][1])):
        name = {"확정": f"B 처방 확정: {grp}", "추정": f"B 잔여 추정: {grp}", "상한": "B 미확정(상한)",
                "A로(공급형)": f"B 공급형 → A에서 계산: {grp}", "제외": f"B 제외: {grp}"}[st]
        cmp_rows.append(dict(수단=f"{name} ({int(r.n_dong)}곳)", 기간="방학", 지위=STAT[st], n_dong=r.n_dong,
                             하한=r.acc_lo, 상한=r.acc_hi))
    ref_lo, ref_hi = tg.gap.sum() * RHO[0] / vac.pay_per_cust, tg.gap.sum() * RHO[1] / vac.pay_per_cust
    cmp_rows.append(dict(수단=f"참고: 1순위 {len(tg)}곳 전체, 판정 무시", 기간="방학", 지위="참고", n_dong=len(tg), 하한=ref_lo, 상한=ref_hi))
    P(f"  참고(판정 무시, 1순위 전체): 방학 월 계정 {ref_lo:.1f} ~ {ref_hi:.1f} | 비율 1.0 민감도: 가까운 {KNN}개 중앙값 "
      f"{tg.gap_knn.sum() / vac.pay_per_cust:.1f}, 일반 배달 뺀 모형 {tg.gap_nogen.sum() / vac.pay_per_cust:.1f}")
    # 10/12 방식(대구 평균 80·100%)을 같은 대상에 적용한 값 — 연속성 확인용, 비교표에는 넣지 않는다
    bb = b[b.gen > 0]
    base = bb.meal_vac.sum() / bb.gen.sum()
    s_ = bb.loc[[d for d in tg.index if d in bb.index]]
    old = {tau: np.maximum(tau * base * s_.gen - s_.meal_vac, 0).sum() / 6 / vac.pay_per_cust for tau in (0.8, 1.0)}
    P(f"  참고(10/12 B1 방식, 같은 대상): 평균의 80% {old[0.8]:.1f} / 100% {old[1.0]:.1f}")
    cand = OUT / "mclp_candidates.csv"
    if cand.exists():
        cu = set(pd.read_csv(cand).unit_id)
        both = tg[tg.unit_id.isin(cu) & tg.status.isin(["확정", "추정", "상한"])]
        P(f"  A 후보 단위 안에서 B 효과도 받는 1순위 동 {len(both)}곳 (A·B를 더하지 말 것):",
          both.group.value_counts().to_dict())
else:
    # 판정표가 없을 때: 10/12 B1 (1순위 17곳, 대구 평균 80·100%)
    bb = b[b.gen > 0]
    base = bb.meal_vac.sum() / bb.gen.sum()
    chk = pd.read_csv(IN / "u2_denominator_check_INTERNAL.csv")
    s_ = bb.loc[[d for d in chk[chk.robust.str.startswith("견고")].dong if d in bb.index]]
    old = {tau: np.maximum(tau * base * s_.gen - s_.meal_vac, 0).sum() / 6 / vac.pay_per_cust for tau in (0.8, 1.0)}
    cmp_rows.append(dict(수단=f"B1 이용 회복(10/12 방식): 1순위 {len(s_)}곳 → 평균의 80~100%", 기간="방학", 지위="B 대구 평균(10/12)",
                         n_dong=len(s_), 하한=old[0.8], 상한=old[1.0]))

# ---- B2: 달성군 남부 학기 회복 -----------------------------------------------------------------
south, north = u[u.hdongs.str.contains(SOUTH)], u[u.hdongs.str.contains(NORTH)]
refs = {"daegu": ("대구 단위 중앙값", u.loc[u.child >= MIN_CHILD, "per1k_학기"].median()),
        "north": ("달성군 북부 읍(화원·다사) 합산", (north.per1k_학기 * north.child).sum() / north.child.sum())}
P(f"\n[B2 학기 회복·달성군 남부 {len(south)}개 단위, 아동 {south.child.sum():.0f}] 현재 학기 월 결제 "
  f"{(south.per1k_학기 * south.child / 1000).sum():.1f}")
for key in (["daegu", "north"] if B2REF == "both" else [B2REF]):
    lab, ref = refs[key]
    gap = np.maximum(ref - south.per1k_학기, 0) * south.child / 1000
    acc = float(gap.sum() / sem.pay_per_cust)
    P(f"  기준 {lab} = 학기 아동 1천 명당 월 {ref:.2f} → 늘어나는 학기 월 결제 {gap.sum():.1f}, 월 계정 {acc:.1f}")
    cmp_rows.append(dict(수단=f"B2 학기 회복: 달성군 남부 5개 읍면 → {lab}", 기간="학기", 지위="B2(가정 하)", n_dong=np.nan, 하한=acc, 상한=acc))

# ---- 비교표 --------------------------------------------------------------------------------
cmp = pd.DataFrame(cmp_rows)
cmp["늘어나는_월_계정"] = cmp.상한                       # 10/12 열 이름은 범위의 위쪽 값으로 유지
cmp = cmp[["수단", "기간", "지위", "n_dong", "늘어나는_월_계정", "하한", "상한"]]
P(f"\n[비교] 대구 방학 월평균 이용 계정 {vac.cust:.0f}, 학기 {sem.cust:.0f}. 늘어나는_월_계정 = 범위의 위쪽\n",
  cmp.round(1).to_string(index=False))
cmp.to_csv(OUT / "scenario_AB_compare.csv", index=False, encoding="utf-8-sig")
d18 = OUT / "mclp_d018_check.csv"
if d18.exists():
    dd = pd.read_csv(d18)
    P("\n[D-018 점검 (80에서)] 엄격 공급 + 흐름 닿음 기준선 커버 < 90% 경고 설정 수(닿음별):",
      dd[dd["판정"].astype(str).str.startswith("경고(")].groupby("reach").size().to_dict())

# ---- 그림: 방학 월 계정 증가, 범위 막대 ------------------------------------------------------------
plt.rcParams["font.family"] = "Malgun Gothic"
show = cmp[(cmp.기간 == "방학") & ~cmp.지위.isin(["A로 보냄(B 0)", "제외(효과 0)", "참고(A 10/12 방식)"])].reset_index(drop=True)
PAL = {"A": ("#86b6ef", "#d3e4f8"), "B 확정": ("#1c5cab", "#9bb8df"), "B 추정": ("#4f86c6", "#c3d6ee"),
       "B 상한": ("#8a8883", "#d9d7d2"), "B 대구": ("#1c5cab", "#9bb8df"), "참고": ("#b7b5b0", "#e6e4df")}


def pal(st):
    return next(v for kk, v in PAL.items() if st.startswith(kk))


fh = 0.5 * len(show) + 1.8
fig, ax = plt.subplots(figsize=(10.5, fh), facecolor="white")
yy = np.arange(len(show))[::-1]
xmax = max(float(show.상한.max()), 1.0)
for y_, (_, r) in zip(yy, show.iterrows()):
    dark, light = pal(r.지위)
    ax.barh(y_, r.상한, color=light, height=0.6)
    ax.barh(y_, r.하한, color=dark, height=0.6)
    txt = f"{r.하한:,.0f}" if abs(r.상한 - r.하한) < 0.5 else f"{r.하한:,.0f} ~ {r.상한:,.0f}"
    if r.지위.startswith("A") and r.상한 < 0.5:
        txt = "0 (기준선 포화 또는 새 커버 없음)"
    ax.text(r.상한 + xmax * 0.01, y_, txt, va="center", fontsize=9.5, color="#1a1a1a")
ax.set_yticks(yy, show.수단, fontsize=9.5)
ax.set_xlim(0, xmax * 1.18)
ax.set_xlabel("방학 한 달에 늘어나는 급식카드 이용 계정 (가정 하의 계산, 진한 막대 = 범위 아래, 옅은 막대 = 범위 위)", fontsize=9.5)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
ax.grid(axis="x", color="#e6e6e6")
ax.set_axisbelow(True)
hd = [Patch(color=PAL[k_][0], label=lab) for k_, lab in
      [("A", "A 공급 확대(상한)"), ("B 확정", "B 처방 확정"), ("B 추정", "B 잔여 추정"), ("B 상한", "B 미확정(상한)"),
       ("B 대구", "B1 대구 평균(10/12 방식)"), ("참고", "참고")] if show.지위.str.startswith(k_).any()]
fig.legend(handles=hd, loc="upper left", bbox_to_anchor=(0.01, -0.01), ncol=len(hd), fontsize=8.5, frameon=False)
ttl = "가게를 늘리는 것과 이용을 회복하는 것 — 판정 유형별"
ax.set_title(("[가짜 자료 · 실데이터 아님] " if SYN else "") + ttl, loc="left", fontsize=12.5)
n_ex = int(cmp[cmp.지위 == "제외(효과 0)"].n_dong.sum()) if (cmp.지위 == "제외(효과 0)").any() else 0
n_sup = int(cmp[cmp.지위 == "A로 보냄(B 0)"].n_dong.sum()) if (cmp.지위 == "A로 보냄(B 0)").any() else 0
note = ("A: 새로 커버된 아이가 대구 평균만큼 쓴다고 본 상한(범위 = 억제 빈칸 두 끝). "
        "B: 비슷한 조건 단위의 기대 이용까지 부족분의 50~100% 회복(확정·추정), 미확정은 0~100%(상한).\n"
        f"1순위 중 제외 {n_ex}곳은 효과 0, 공급형 {n_sup}곳은 A에서 계산(이중 계산 없음). A·B 줄을 더하지 않는다. 계정 수는 아이 수와 같지 않다.")
fig.text(0.01, -0.01 - 0.4 / fh, note, fontsize=8.2, color="#52514e", va="top")
fig.savefig(FIG / "v2_fig5_scenario_AB.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
log.close()
print(f"ok → {OUT.name}: A {'4차' if NEWA else '10/12'} · B {'판정 유형별' if NEWB else '10/12 B1'} · B2 {B2REF}")
