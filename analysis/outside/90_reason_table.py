"""판정표 자동 생성 — "덜 쓰는 이유" 7가지 (D-019, docs/topics/T2_reason_rules.md).

입력(없는 파일은 그 이유만 '?자료'로 둔다):
  --v4 DIR       4차 반출 폴더. EXPORT_v4_{dong_regime_general, dong_shop_state, kcb_hdong_income,
                 meal_flow_home_shop, shinhan_delivery_umd_month, dong_delivery}.csv
  --app FILE     대구로 앱 점검 기록: 역할(대상/대조), 구, 동, 점검일, 가게, 업종, 최소주문금액, 배달팁, 영업중
  --centers FILE 지역아동센터: 행정동코드, 정원(없으면 개소 수로 센다)
  --tag NAME     출력 폴더를 out_NAME으로 (가짜 자료 점검용)
출력: reason_table_INTERNAL.csv (전 법정동, 지표·판정·사유), reason_table_PUBLIC.csv/.md (판정 대상, 기호·유형만),
      mclp_candidates.csv, 90_summary.txt
기호: ● 해당 / ○ 아님 / △ 가능성(R2) / ?자료 · ?억제 · ?경계 · ?범위 · ?단가 (공표본은 ?만, G8)
"""
import argparse
import glob
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IN = HERE / "out"                                   # 밖 분석 내부 산출물(입력)
BD = ROOT / "data_external" / "boundary"
POPDIR = ROOT / "data_external" / "population_dong"
Q, K, MIN_CHILD = 0.25, 3, 300                      # G2·G3, D-015
PRICE = {}                                          # R4 1끼 단가(구별 예외). 기록표 '단가' 시트 값이 우선
PRICE_DEFAULT = (10000,)                            # 2026년 대구 공통 1만 원(대구시청 복지과 문의 2026-10-15) — 앱 화면과 같은 시점
REACH_P = 0.7                                       # R3: 같은 단위 가게로 간 급식 비율 >= 0.7 이면 '단위 안'
R4_HIT, R4_OK, R4_MIN, R4_TOP = 0.20, 0.05, 3, 10
R7_MIN = 20
OUTER = {"하빈면", "가창면", "검단동", "안심2동", "공산동", "파동"}   # D-018 외곽 6단위
SH_CNT = None                                       # 신한 건수 열 이름(현장 F1 확인 후). None이면 CNT·건수가 든 첫 열
RS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
STRENGTH = {"R1": "간접", "R2": "보조", "R3": "직접", "R4": "현재 시점", "R5": "간접", "R6": "-", "R7": "간접"}

ap = argparse.ArgumentParser()
ap.add_argument("--v4")
ap.add_argument("--app")
ap.add_argument("--centers")
ap.add_argument("--shops")                           # 가게별 급식카드 최소주문 면제 표(가게, 급식카드_최소주문_면제 Y/N/모름)
ap.add_argument("--tag", default="")
ap.add_argument("--selftest", action="store_true")
A = ap.parse_args()


# ---- 판정 도구 (G3·G4) -------------------------------------------------------------
def judge_one(x, hit, ok, bad):
    """bad='low': 값이 hit 이하면 ●, ok 이상이면 ○. bad='high'는 반대."""
    if pd.isna(x):
        return "?자료"
    if bad == "low":
        return "●" if x <= hit else ("○" if x >= ok else "?경계")
    return "●" if x >= hit else ("○" if x <= ok else "?경계")


def merge2(a, b, conflict="?억제"):
    """두 판정이 같을 때만 확정(G4)."""
    if a == b:
        return a
    if "?자료" in (a, b):
        return "?자료"
    return conflict


def judge(lo, hi, popn, bad="low"):
    """문턱은 모집단 popn의 중간값(lo+hi)/2 분포로 정하고, 억제 두 끝 lo·hi를 각각 판정한다."""
    mid = ((lo + hi) / 2).reindex(popn).dropna()
    hit, ok = mid.quantile(Q if bad == "low" else 1 - Q), mid.median()
    v = pd.Series({k: merge2(judge_one(lo[k], hit, ok, bad), judge_one(hi[k], hit, ok, bad)) for k in lo.index})
    return v, (round(hit, 4), round(ok, 4), len(mid))


def rho_range(s, o, i):
    """ρ = (자기+나간)/(자기+들어온). 각 변수에 단조라 범위 꼭짓점에서 최소·최대가 나온다."""
    v = [(a + c) / (a + e) for a in set(s) for c in set(o) for e in set(i) if a + e > 0]
    return (min(v), max(v)) if v else (np.nan, np.nan)


if A.selftest:
    assert judge_one(0.1, 0.2, 0.5, "low") == "●" and judge_one(0.6, 0.2, 0.5, "low") == "○"
    assert judge_one(0.3, 0.2, 0.5, "low") == "?경계" and judge_one(np.nan, 0.2, 0.5, "low") == "?자료"
    assert judge_one(0.9, 0.8, 0.5, "high") == "●" and judge_one(0.4, 0.8, 0.5, "high") == "○"
    assert merge2("●", "●") == "●" and merge2("●", "?경계") == "?억제" and merge2("●", "?자료") == "?자료"
    assert rho_range((10, 10), (0, 4), (0, 0)) == (1.0, 1.4)
    assert rho_range((0, 4), (0, 0), (0, 0)) == (1.0, 1.0)
    print("selftest ok")
    raise SystemExit

OUT = HERE / (f"out_{A.tag}" if A.tag else "out")
OUT.mkdir(exist_ok=True)
log = open(OUT / "90_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


def v4(name):
    f = Path(A.v4) / f"EXPORT_v4_{name}.csv" if A.v4 else None
    return pd.read_csv(f, encoding="utf-8-sig") if f is not None and f.exists() else None


def code10(s):
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()


# ---- 기본 입력 ------------------------------------------------------------------------
b = pd.read_csv(IN / "bdong_types_INTERNAL.csv").set_index("dong")
u = pd.read_csv(IN / "units_per_child.csv").set_index("unit_id")
km = pd.read_csv(IN / "bridge_shopkey_unit.csv").set_index("dong").unit_id
br = pd.read_csv(IN / "bridge_bdong_hdong.csv", dtype=str)
h2u = br.drop_duplicates("행정동코드").set_index("행정동코드").unit_id
b2u = br.drop_duplicates("bkey").set_index("bkey").unit_id
nb_old = pd.read_csv(IN / "neighbor_check_INTERNAL.csv").set_index("dong").verdict
chk = pd.read_csv(IN / "u2_denominator_check_INTERNAL.csv")
old17 = set(chk[chk.robust.str.startswith("견고")].dong)
UP = u[u.child >= MIN_CHILD].index                                 # 단위 모집단(G2)
DP = b[(b.gen > 0) & (b.able_y >= K)].index                        # 법정동 모집단(G2)
b["gu"] = b.index.str.split("|").str[0]
files = {n: v4(n) for n in ["dong_regime_general", "dong_shop_state", "kcb_hdong_income",
                            "meal_flow_home_shop", "shinhan_delivery_umd_month", "dong_delivery"]}
P("[자료] 4차 폴더:", A.v4 or "없음")
for n, d in files.items():
    P(f"  {n}: {'있음 ' + str(d.shape) if d is not None else '없음'}")
P("  앱 점검:", A.app or "없음", "| 지역아동센터:", A.centers or "없음")

# ---- G1 판정 대상: 4차 동×레짐 분모가 있으면 LQ를 다시 계산해 1순위를 다시 뽑는다 ---------------------
gd = files["dong_regime_general"]
if gd is not None:
    gd = gd.set_index("dong")
    ok = gd.dropna()
    share = ok["방학"].sum() / ok[["방학", "전환", "학기"]].sum().sum()
    b["gen_vac"] = gd["방학"].reindex(b.index)
    b["gen_vac_src"] = np.where(b.gen_vac.notna(), "v4", "대체(25개월×방학 비중)")
    b["gen_vac"] = b.gen_vac.fillna(b.gen * share).replace(0, np.nan)
    act = b[b.gen > 0]
    b["lq"] = (act.meal_vac / act.gen_vac) / (act.meal_vac.sum() / act.gen_vac.sum())
    lq_src = f"4차 동×레짐 일반 결제(D-016 교체), 억제 동은 25개월×방학 비중 {share:.3f}로 대체"
else:
    b["lq"] = b.lq_vac
    lq_src = "25개월 일반 결제(3차, D-016 원안)"
cut = b.loc[b.gen > 0, "lq"].quantile(Q)
unclass = b.type_vac.astype(str).str.startswith("분류불가")
b["U2"] = (b.able_y >= K) & (b.lq <= cut) & ~unclass
med1k = u.loc[UP, "per1k_방학"].median()
b["robust"] = (b.unit_id.map(u["per1k_방학"]) < med1k) & (b.unit_id.map(u.child) >= MIN_CHILD)
b["target"] = b.U2 & b.robust
T = list(b[b.target].index)
P(f"\n[G1] LQ 분모: {lq_src}\n  U2 컷 {cut:.4f} | U2 {int(b.U2.sum())}곳 | 1순위 {len(T)}곳")
P("  지금(D-017) 17곳 대비 새로 들어옴:", sorted(set(T) - old17), "| 빠짐:", sorted(old17 - set(T)))

# ---- 단위 총인구 (R1 연결 점검, R5a 분모) ---------------------------------------------------
prow = []
for f in sorted(glob.glob(str(POPDIR / "*.csv"))):
    d = pd.read_csv(f, encoding="cp949", thousands=",")
    d = d[d["행정구역"].str.startswith("대구광역시")]
    col = [c for c in d.columns if c.endswith("_계_총인구수")][0]
    prow.append(pd.DataFrame({"hcode": d["행정구역"].str.extract(r"\((\d{10})\)")[0].values,
                              "ym": col[:8], "pop": d[col].values}))
pt = pd.concat(prow)
pt["unit_id"] = pt.hcode.map(h2u)
pt = pt.dropna(subset=["unit_id"])
hpop = pt.groupby("hcode")["pop"].mean()
upop = pt.groupby(["unit_id", "ym"])["pop"].sum().groupby(level=0).mean()
R = pd.DataFrame(index=b.index)
R["unit_id"], R["gu"], R["target"], R["old17"], R["lq"] = b.unit_id, b.gu, b.target, b.index.isin(old17), b.lq
thr = {}


def to_dong(unit_verdict):
    return b.unit_id.map(unit_verdict).fillna("?자료")


# ---- R1 필요 적음: KCB 30·40대 월소득 200만 원 이하 비율 (단위) ---------------------------------------
kc = files["kcb_hdong_income"]
if kc is not None:
    C = [f"C{i}_CNT" for i in range(1, 23)]
    kc["EMD_CD"] = code10(kc.EMD_CD)
    k3 = kc[kc.grp.astype(str) == "3040"].copy()
    L = int(k3.EMD_CD.str.len().mode()[0])
    k3["hcode"] = k3.EMD_CD.map({h[:8]: h for h in h2u.index} if L == 8 else {h: h for h in h2u.index})
    k3["unit_id"] = k3.hcode.map(h2u)
    P(f"\n[R1] KCB EMD_CD {L}자리, 30·40대 행 {len(k3)} 중 단위 연결 {int(k3.unit_id.notna().sum())}")
    k3 = k3.dropna(subset=["unit_id"])
    a0, a4 = k3[C].fillna(0), k3[C].fillna(4)
    num_lo, num_hi = a0[C[:3]].sum(axis=1).groupby(k3.unit_id).sum(), a4[C[:3]].sum(axis=1).groupby(k3.unit_id).sum()
    rst_lo, rst_hi = a0[C[3:]].sum(axis=1).groupby(k3.unit_id).sum(), a4[C[3:]].sum(axis=1).groupby(k3.unit_id).sum()
    n1_lo = (num_lo / (num_lo + rst_hi)).reindex(u.index)
    n1_hi = (num_hi / (num_hi + rst_lo)).reindex(u.index)
    unm = (hpop[~hpop.index.isin(set(k3.hcode))].groupby(h2u).sum() / hpop.groupby(h2u).sum()).reindex(u.index).fillna(0)
    n1_lo[unm >= 0.2], n1_hi[unm >= 0.2] = np.nan, np.nan
    v, thr["R1"] = judge(n1_lo, n1_hi, UP, "low")
    R["R1"], R["R1_val"] = to_dong(v), b.unit_id.map((n1_lo + n1_hi) / 2)
    P("  연결 안 된 행정동이 인구 20% 이상인 단위:", list(unm[unm >= 0.2].index))
else:
    R["R1"] = "?자료"

# ---- R2 다른 경로: 지역아동센터 정원 ÷ 아동 (단위, 보조) ------------------------------------------
if A.centers:
    ce = pd.read_csv(A.centers, dtype={"행정동코드": str})
    cap = ce["정원"] if "정원" in ce else pd.Series(1, index=ce.index)
    c2 = (cap.groupby(ce["행정동코드"].map(h2u)).sum().reindex(u.index).fillna(0) / u.child * 1000)
    v, thr["R2"] = judge(c2, c2, UP, "high")
    R["R2"], R["R2_val"] = to_dong(v.replace("●", "△")), b.unit_id.map(c2)
else:
    R["R2"] = "?자료"

# ---- 경계와 이웃 (R3 닿는 범위, R7 대체 판정) — 70·80과 같은 방식 --------------------------------------
import geopandas as gpd
import libpysal

umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"], ri["code"] = umd.EMD_CD + "00", ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
geo = geo.merge(br.drop_duplicates("법정동코드")[["법정동코드", "bkey"]], left_on="code", right_on="법정동코드")
geo = geo.dissolve(by="bkey", aggfunc="first").reset_index()
wq = libpysal.weights.fuzzy_contiguity(geo, buffering=True, buffer=5, silence_warnings=True)
nbr = {geo.bkey[i]: {geo.bkey[j] for j in wq.neighbors[i]} for i in wq.neighbors}

# 이웃 점검(§6-7 규칙)을 G1과 같은 분모로 전 법정동에 다시 계산한다. 판정 대상이 바뀌어도 대체 판정이 비지 않게.
den = b.gen_vac if "gen_vac" in b else b.gen
mv, dn = b.meal_vac.fillna(0), den.fillna(0)
base_nb = mv.sum() / dn.sum()                                    # 70과 같은 기준 비중


def nb_verdict(d):
    if d not in nbr:
        return "경계 없음"
    ns = [x for x in nbr[d] if x in b.index]
    if dn[ns].sum() <= 0:
        return "경계 없음"
    nb_lq = mv[ns].sum() / dn[ns].sum() / base_nb
    pool_lq = mv[ns + [d]].sum() / dn[ns + [d]].sum() / base_nb
    return "옆 동네가 대신할 가능성 큼" if nb_lq >= 1.0 and pool_lq >= 0.8 else ("주변도 함께 적음" if nb_lq < 0.8 else "중간")


nb_new = pd.Series({d: nb_verdict(d) for d in b.index})
diff = [d for d in nb_old.index if d in nb_new.index and nb_old[d] != nb_new[d]]
P(f"\n[이웃 점검 재계산] 기존 파일(17곳)과 다른 동: {diff}" + (" (분모가 바뀌어 달라질 수 있음)" if gd is not None else ""))

# ---- Q3 흐름: R7과 R3 범위 결정에 함께 쓴다 ---------------------------------------------------
fl = files["meal_flow_home_shop"]
reach_used = None
if fl is not None:
    f = fl.assign(n_lo=fl.n.fillna(0), n_hi=fl.n.fillna(4), hu=fl.home.map(km), su=fl.dong.map(km))
    same = f.hu == f.su
    p_lo = f.n_lo[same].sum() / (f.n_lo[same].sum() + f.n_hi[~same].sum())
    p_hi = f.n_hi[same].sum() / (f.n_hi[same].sum() + f.n_lo[~same].sum())
    reach_used = "inside" if p_lo >= REACH_P else ("adjacency" if p_hi < REACH_P else None)
    P(f"\n[Q3] 같은 결합 단위 가게로 간 급식 비율 {p_lo:.3f}~{p_hi:.3f} → R3 닿는 범위: {reach_used or '미정(두 범위 일치 규칙)'}")

# ---- R3 주문받는 가게 적음: 닿는 범위 meal_vac10_live ÷ 아동 (단위) ----------------------------------
qs = files["dong_shop_state"]
if qs is not None:
    qs = qs.set_index("dong")
    keys_in = {x: set(km[km == x].index) | set(b2u[b2u == x].index) for x in u.index}
    REACH = {"inside": keys_in,
             "adjacency": {x: keys_in[x].union(*[nbr.get(j, set()) for j in keys_in[x]]) for x in u.index}}

    def per_child(col, fill, rc):
        s = qs[col].fillna(fill)
        return pd.Series({x: s.reindex(list(rc[x])).fillna(0).sum() for x in u.index}) / u.child * 1000

    vr, sub = {}, {}
    for name, rc in REACH.items():
        lo, hi = per_child("meal_vac10_live", 0, rc), per_child("meal_vac10_live", 2, rc)
        vr[name], thr[f"R3_{name}"] = judge(lo, hi, UP, "low")
        al, ah = per_child("able_live", 0, rc), per_child("able_live", 2, rc)
        am = ((al + ah) / 2).reindex(UP).median()
        sub[name] = pd.Series(np.where(al >= am, "활성화", np.where(ah < am, "모집", "미정")), index=u.index)
        R[f"R3_{name}_val"] = b.unit_id.map((lo + hi) / 2)
    if reach_used:
        v3, s3 = vr[reach_used], sub[reach_used]
    else:
        v3 = pd.Series({x: merge2(vr["inside"][x], vr["adjacency"][x], "?범위") for x in u.index})
        s3 = sub["inside"].where(sub["inside"] == sub["adjacency"], "미정")
    R["R3"], R["R3_sub"] = to_dong(v3), b.unit_id.map(s3)
else:
    R["R3"], R["R3_sub"] = "?자료", ""

# ---- R4 한도 안에서 시킬 게 없음: 앱 점검, 같은 구 대조 동과 비교 (법정동) ---------------------------------
R["R4"], R["R4_tip"], R["R4_list"], R["R4_n_open"], R["R4_note"] = "?자료", "?자료", "?자료", np.nan, ""
if A.app:
    # 기록표(95_app_check_sheet.py의 xlsx: '기록'·'단가' 시트) 또는 같은 열의 CSV
    xl = A.app.lower().endswith(".xlsx")
    ap_ = pd.read_excel(A.app, sheet_name="기록") if xl else pd.read_csv(A.app)
    if xl:
        pr = pd.read_excel(A.app, sheet_name="단가").dropna(subset=["1끼 단가(원)"])
        PRICE.update({g.strip(): (int(p),) for g, p in zip(pr["구"], pr["1끼 단가(원)"])})
    ap_ = ap_[ap_["역할"].isin(["대상", "대조"])].copy()                 # 예시 줄 제외
    for c in ["최소주문금액", "배달팁"]:
        ap_[c] = pd.to_numeric(ap_[c], errors="coerce")
    filled = ap_["가게"].notna() | ap_["최소주문금액"].notna()            # 미리 깔린 빈 줄 제외
    half = filled & ap_["최소주문금액"].isna()
    P(f"\n[R4] 앱 점검 {A.app}: 기록 {int(filled.sum())}줄, 최소주문금액 빠진 줄 {int(half.sum())}(제외), "
      f"단가 {dict((g, PRICE.get(g, PRICE_DEFAULT)) for g in sorted(ap_['구'].str.strip().unique()))}")
    ap_ = ap_[filled & ~half]
    # 점검 방식(2026-10-15): 1인분 목록에서 '아동급식' 표시가 확인된 가게만, 목록 위에서부터 R4_TOP곳
    if "급식카드 표시" in ap_:
        card = ap_["급식카드 표시"].astype(str).str.strip().str.upper()
        P(f"  급식카드 표시 N {int((card == 'N').sum())}줄·모름 {int((card == '모름').sum())}줄 제외")
        ap_ = ap_[~card.isin(["N", "모름"])]
    if "순서" in ap_:
        ap_ = ap_.sort_values(["구", "동", "순서"]).groupby(["구", "동"]).head(R4_TOP)
    ap_["key"] = ap_["구"].str.strip() + "|" + ap_["동"].str.strip()
    ap_ = ap_[ap_["영업중"].astype(str).str.strip().str.upper().isin(["Y", "예", "O", "1", "TRUE"])]
    # 급식카드 결제 시 최소주문금액을 면제하는 가게가 있다(팀 앱 점검 중 확인, 2026-10-15).
    # 기준 = 급식카드 결제 기준 최소주문(면제 가게는 0). 면제 여부를 모르는 가게는 면제/아님 두 경우로 판정해 같을 때만 확정(G4 방식).
    # 가게 상세 화면: "최소주문금액 11,000원 (아동급식카드로 주문 시 미적용)". 면제여도 메뉴 하나는 사야 하므로
    # 급식카드로 시킬 수 있는 최소 금액 = 면제면 대표메뉴 최저가, 아니면 max(최소주문, 대표메뉴 최저가).
    WAIVE, MENU = {}, {}
    if A.shops:
        ws = pd.read_csv(A.shops)
        nm = ws["가게"].astype(str).str.strip()
        WAIVE = dict(zip(nm, ws["급식카드_최소주문_면제"].astype(str).str.strip().str.upper()))
        if "대표메뉴_최저가" in ws:
            MENU = dict(zip(nm, pd.to_numeric(ws["대표메뉴_최저가"], errors="coerce")))
        P(f"  가게 표: {len(WAIVE)}곳 중 면제 Y {sum(v == 'Y' for v in WAIVE.values())}, N {sum(v == 'N' for v in WAIVE.values())}, "
          f"대표메뉴 최저가 확인 {sum(pd.notna(v) for v in MENU.values())}")

    def eff_min(df, scen):
        """scen 'N' = 가장 불리한 끝(모르는 칸을 불리하게), 'Y' = 가장 유리한 끝, 'LIST' = 목록 금액 그대로(개정 전)."""
        mo = df["최소주문금액"]
        if scen == "LIST":
            return mo
        nm = df["가게"].astype(str).str.strip()
        w, menu = nm.map(WAIVE).fillna("모름"), nm.map(MENU).astype(float)
        hi = np.where(w == "Y", menu.fillna(mo), np.maximum(mo, menu.fillna(0)))
        lo = np.where(w == "N", np.maximum(mo, menu.fillna(0)), menu.fillna(0))
        return pd.Series(hi if scen == "N" else lo, index=df.index)

    def r4_one(g, c, price, tip, scen):
        gm = eff_min(g, scen) + (g["배달팁"].fillna(0) if tip else 0)
        a4, p4 = int((gm <= price).sum()), int((gm <= price).sum()) / len(g)
        cm = ((eff_min(c, scen) + (c["배달팁"].fillna(0) if tip else 0)) <= price).groupby(c["key"]).mean().mean() if len(c) else np.nan
        if pd.isna(cm):
            return "●" if a4 < R4_MIN else "?자료"
        return "●" if (p4 <= cm - R4_HIT or a4 < R4_MIN) else ("○" if (p4 >= cm - R4_OK and a4 >= R4_MIN) else "?경계")

    def r4(g, c, gu, tip, scens):
        vs = []
        for price in PRICE.get(gu, PRICE_DEFAULT):
            v = [r4_one(g, c, price, tip, sc) for sc in scens]
            vs.append(v[0] if len(v) == 1 else merge2(v[0], v[1], "?면제"))
        return vs[0] if len(vs) == 1 else merge2(vs[0], vs[1], "?단가")

    for key, g in ap_.groupby("key"):
        if not (g["역할"] == "대상").any() or key not in R.index:
            continue
        gu = key.split("|")[0]
        c = ap_[(ap_["역할"] == "대조") & (ap_["구"].str.strip() == gu)]
        R.loc[key, "R4"] = r4(g, c, gu, False, ["N", "Y"])
        R.loc[key, "R4_tip"] = r4(g, c, gu, True, ["N", "Y"])
        R.loc[key, "R4_list"] = r4(g, c, gu, False, ["LIST"])          # 목록 표시 최소주문 그대로(개정 전 방식, 참고)
        R.loc[key, "R4_n_open"] = len(g)
        # 해석 주석(판정은 바꾸지 않음): 같은 구 대조 동 중 하나라도 대상 동만큼(또는 더) 1끼 가능 가게가 적으면,
        # 평균 이상 쓰는 동네도 같은 장벽을 가진 것 → 대상 동이 덜 쓰는 이유로는 약하다 → 지역 공통 장벽으로 표시
        # (2026-10-15 일반화: 처음엔 'A4 < 3'일 때만 표시. 면제 반영 후 화원 대상·구라리가 같은 목록 3곳으로 같아져 넓힘)
        p0 = PRICE.get(gu, PRICE_DEFAULT)[0]
        c_p4 = (eff_min(c, "N") <= p0).groupby(c["key"]).mean()
        t_p4 = float((eff_min(g, "N") <= p0).mean())
        if str(R.loc[key, "R4"]) in ("●", "?면제", "?경계") and (c_p4 <= t_p4 + R4_OK).any():
            R.loc[key, "R4_note"] = "같은 구 대조 동도 1끼 가능 가게가 대상만큼 적음 — 지역 공통 장벽"

# ---- R5 배달 여건: 5a 배달 시장 ÷ 총인구 (단위), 5c 취소율·배달 시간·배달팁 (법정동) -------------------------
# 2026-10-15 개정(4차 전): 4차에 신한 배달매출이 제공되지 않는다 → 5a는 대구로 일반 배달 결제(25개월)로 대신한다(대리).
sh, parts = files["shinhan_delivery_umd_month"], {}
if sh is not None:
    cnt = SH_CNT or next(c for c in sh.columns if re.search("CNT|건수|COUNT", c, re.I))
    code = code10(sh.umd_cd)
    exact = br.drop_duplicates("법정동코드").set_index("법정동코드").unit_id
    pref = br.assign(p=br["법정동코드"].str[:8]).groupby("p").unit_id.agg(lambda s: s.iloc[0] if s.nunique() == 1 else None)
    sh["unit_id"] = code.map(exact).fillna(code.str[:8].map(pref))
    matched = sh.loc[sh.unit_id.notna(), cnt].fillna(0).sum() / max(sh[cnt].fillna(0).sum(), 1)
    P(f"\n[R5a] 신한 건수 열 '{cnt}', 지역코드 길이 {code.str.len().mode()[0]}, 단위 연결 건수 비율 {matched:.3f}")
    if matched >= 0.5:
        lo = sh[cnt].fillna(0).groupby(sh.unit_id).sum().reindex(u.index) / upop * 1000
        hi = sh[cnt].fillna(4).groupby(sh.unit_id).sum().reindex(u.index) / upop * 1000
        v, thr["R5a"] = judge(lo, hi, UP, "low")
        parts["5a"] = to_dong(v)
        R["R5a_val"] = b.unit_id.map((lo + hi) / 2)
        r5b = (u.gen / ((lo + hi) / 2 * upop / 1000)).reindex(u.index)
        weak = r5b.reindex(UP).quantile(Q)
        R["R3_note"] = b.unit_id.map(r5b <= weak).map({True: "대구로 약세", False: ""})
else:
    a5 = (u.gen / upop * 1000).reindex(u.index)                     # 대구로 일반 배달 결제 ÷ 총인구 1천 명(25개월 합)
    v, thr["R5a"] = judge(a5, a5, UP, "low")
    parts["5a"] = to_dong(v)
    R["R5a_val"] = b.unit_id.map(a5)
    P("\n[R5a] 신한 자료 없음 → 대구로 일반 배달 결제 ÷ 총인구(대리)로 판정")
dg = files["dong_delivery"]
if dg is not None:
    dg = dg.set_index("dong")
    canc, mins = (dg.n_cancel / dg.n).reindex(b.index), (dg.mins_sum / dg.mins_n).reindex(b.index)
    vc, thr["R5c_cancel"] = judge(canc, canc, DP, "high")
    vm, thr["R5c_mins"] = judge(mins, mins, DP, "high")
    vs5 = [vc, vm]
    if "tip_sum" in dg:                                               # 배달팁 평균(4차 Q7에 추가, 2026-10-15)
        tip = (dg.tip_sum / dg.tip_n).reindex(b.index)
        vt5, thr["R5c_tip"] = judge(tip, tip, DP, "high")
        vs5.append(vt5)
    parts["5c"] = pd.Series({k: "●" if "●" in [v_[k] for v_ in vs5] else
                             ("○" if all(v_[k] == "○" for v_ in vs5) else next(v_[k] for v_ in vs5 if v_[k] != "○"))
                             for k in b.index})


def r5(k):
    ps = [p[k] for p in parts.values()]
    if "●" in ps:
        return "●"
    have = [p for p in ps if p != "?자료"]
    if not have:
        return "?자료"
    return "○" if all(p == "○" for p in have) else next(p for p in have if p != "○")


R["R5"] = [r5(k) for k in R.index]
for name, p in parts.items():
    R[f"R5_{name}"] = p
R["R6"] = "?자료"                                                     # 동별 자료 없음(규칙 R6)

# ---- R7 옆 동네: 거주 기준으로 다시 센 LQ가 U2 컷을 넘는가 (법정동) ------------------------------------------
NBMAP = {"옆 동네가 대신할 가능성 큼": "●", "주변도 함께 적음": "○", "중간": "?경계"}
R["R7_src"], R["R7_rho"] = "이웃(약)", np.nan
R["R7"] = [NBMAP.get(nb_new.get(k), "?자료") for k in R.index]
R["R7_nb"] = R.R7
if fl is not None:
    f = fl.assign(n_lo=fl.n.fillna(0), n_hi=fl.n.fillna(4))
    sm = f[f.home == f.dong].set_index("home")
    om = f[f.home != f.dong].groupby("home")[["n_lo", "n_hi"]].sum()
    im = f[f.home != f.dong].groupby("dong")[["n_lo", "n_hi"]].sum()
    for k in R.index:
        s = (sm.n_lo[k], sm.n_hi[k]) if k in sm.index else (0, 0)
        o = (om.n_lo[k], om.n_hi[k]) if k in om.index else (0, 0)
        i = (im.n_lo[k], im.n_hi[k]) if k in im.index else (0, 0)
        if s[0] + i[0] < R7_MIN or pd.isna(R.lq[k]):
            R.loc[k, ["R7", "R7_src"]] = ["?자료", "Q3"]
            continue
        rl, rh = rho_range(s, o, i)
        R.loc[k, ["R7", "R7_src", "R7_rho"]] = [merge2("●" if R.lq[k] * rl >= cut else "○",
                                                       "●" if R.lq[k] * rh >= cut else "○"), "Q3", (rl + rh) / 2]


# ---- 묶기 (규칙 §3) -------------------------------------------------------------------------
WHO = {"공급형(활성화)": "운영사", "공급형(모집)": "시·운영사", "공급형(미정)": "시·운영사",
       "가격형": "시·운영사·가게", "배달형": "운영사", "배달형(부분)": "운영사"}


def classify(r):
    hits = [x for x in ["R1", "R3", "R4", "R5", "R7"] if r[x] == "●"]
    if r.R7 == "●":
        return "제외: 옆 동네 이용", "-", ",".join(hits)
    if r.R1 == "●":
        return "제외: 필요 적음", "-", ",".join(hits)
    rx = []
    if r.R3 == "●":
        rx.append(f"공급형({r.R3_sub if isinstance(r.R3_sub, str) and r.R3_sub else '미정'})")
    if r.R4 == "●":
        rx.append("가격형(지역 공통)" if r.R4_note else "가격형")
    if r.R5 == "●":
        rx.append("배달형" if rx else "배달형(부분)")
    if rx:
        return "처방 확정: " + "·".join(rx), "·".join(dict.fromkeys(w for x in rx for w in WHO.get(x, WHO.get(x.split("(")[0], "")).split("·"))), ",".join(hits)
    if all(r[x] == "○" for x in ["R1", "R3", "R4", "R5", "R7"]):
        return "잔여 추정: 안내·신청" + (" · 다른 경로 가능성" if r.R2 == "△" else ""), "구청", ""
    miss = [x for x in ["R1", "R3", "R4", "R5", "R7"] if str(r[x]).startswith("?")]
    return "미확정: " + ",".join(miss) + " 미판정", "-", ""


R[["유형", "처방 주체", "걸린 이유"]] = pd.DataFrame([classify(r) for _, r in R.iterrows()], index=R.index)
R.to_csv(OUT / "reason_table_INTERNAL.csv", encoding="utf-8-sig")

# ---- 공표본: 판정 대상, 기호와 유형만 (G8) ----------------------------------------------------------
pub = R.loc[T, RS + ["유형"]].copy()
for x in RS:
    pub[x] = pub[x].astype(str).str.replace(r"^\?.*", "?", regex=True)
pub.insert(0, "동", [k.split("|")[1] for k in pub.index])
pub.insert(0, "구", [k.split("|")[0] for k in pub.index])
order = {"처방 확정": 0, "잔여 추정": 1, "미확정": 2, "제외": 3}
pub = pub.assign(_o=pub["유형"].str.split(":").str[0].map(order)).sort_values(["_o", "유형", "구", "동"]).drop(columns="_o")
pub.to_csv(OUT / "reason_table_PUBLIC.csv", index=False, encoding="utf-8-sig")
md = ["| " + " | ".join(pub.columns) + " |", "|" + "---|" * len(pub.columns)]
md += ["| " + " | ".join(map(str, r)) + " |" for r in pub.itertuples(index=False)]
(OUT / "reason_table_PUBLIC.md").write_text("\n".join(md) + "\n\n● 해당 / ○ 아님 / △ 가능성 / ? 판단 불가\n", encoding="utf-8")

# ---- MCLP 후보 (규칙 §4) -----------------------------------------------------------------------
tt = R.loc[T]
mc = tt[(tt.R3 == "●") & tt["유형"].str.startswith("처방 확정")].groupby("unit_id").R3_sub.agg(lambda s: "·".join(sorted(set(s))))
outer = u[u.hdongs.str.split(",").apply(lambda xs: bool(OUTER & {x.strip() for x in xs}))].index
cand = pd.DataFrame({"unit_id": sorted(set(mc.index) | set(outer))})
cand["이유"] = ["R3 해당" + (" + 외곽" if x in outer else "") if x in mc.index else "외곽(D-018)" for x in cand.unit_id]
cand["허용 동작"] = [{"활성화": "활성화", "모집": "모집"}.get(mc.get(x), "활성화·모집") for x in cand.unit_id]
cand["hdongs"] = cand.unit_id.map(u.hdongs)
cand.to_csv(OUT / "mclp_candidates.csv", index=False, encoding="utf-8-sig")

# ---- 요약 ------------------------------------------------------------------------------------
P("\n[문턱] (해당 쪽 25%, 중앙값, 모집단 수):", thr)
t = R.loc[T]
P(f"\n[판정 대상 {len(T)}곳] 이유별 판정 수")
P(pd.DataFrame({x: t[x].value_counts() for x in RS}).fillna(0).astype(int).to_string())
grp = t["유형"].str.split(":").str[0].value_counts()
P("\n[결론 문장용] " + " · ".join(f"{k} {v}곳" for k, v in grp.items()))
P(t["유형"].value_counts().to_string())
if fl is not None:
    both = t[t.R7_nb.isin(["●", "○"]) & t.R7.isin(["●", "○"])]
    P(f"\n[R7] Q3 판정과 이웃 점검(약)이 다른 동: {list(both[both.R7 != both.R7_nb].index)}")
P(f"\n[MCLP 후보] {len(cand)}개 단위\n", cand.to_string(index=False))
P("\n[판정표 · 내부]\n", t[["unit_id"] + RS + ["R3_sub", "유형", "처방 주체"]].to_string())
log.close()
print(f"ok → {OUT.name}: 판정 대상 {len(T)}곳 | " + " · ".join(f"{k} {v}" for k, v in grp.items()))
