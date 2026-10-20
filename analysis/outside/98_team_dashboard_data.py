"""팀 공유 대시보드용 데이터 묶음 — 반출 결과와 밖 분석 출력만 모은다(새 계산 없음, 집계 수준만).

입력: 2차 반출(9_18), 4차 반출(10_16) 일부, analysis/outside/out·out_V4FBK 출력, 결과 문서의 확인값.
출력: analysis/outside/out_dashboard/*.json (대시보드 Artifact에 첨부)
공표 규칙: 동 단위는 유형·기호만, 지표 값은 대구·구·묶음 수준만 쓴다(G8). 억제 전 값은 쓰지 않는다.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "out_dashboard"
OUT.mkdir(exist_ok=True)
FB = HERE / "out_V4FBK"
E2 = ROOT / "9_18_데이터분석 결과물"
BD = ROOT / "data_external" / "boundary"


def save(name, rows):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{name:12s} {len(rows):4d}행 {p.stat().st_size / 1024:7.1f} KB")


# ---- facts: 본문·카드에 쓰는 낱개 수치 (값은 화면에 보이는 대로 반올림) ------------------------
mg = pd.read_csv(E2 / "EXPORT_m2_month_group.csv", encoding="utf-8-sig", dtype={"ym": str})
mg = mg[(mg.ym >= "202306") & (mg.ym <= "202506")]
mm = mg.ym.str[4:6]
mg["regime"] = np.where(mm.isin(["01", "02", "08"]), "방학", np.where(mm.isin(["07", "12"]), "전환", "학기"))
meal_n, gen_n = int(mg.n.sum()), int(mg.n_general.sum())
vac = mg[mg.regime == "방학"]
sem = mg[mg.regime == "학기"]
s85 = (FB / "85_summary.txt").read_text(encoding="utf-8")
ab = pd.read_csv(FB / "scenario_AB_compare.csv")
sb = pd.read_csv(FB / "scenario_B_dong_INTERNAL.csv").set_index("dong")
rt = pd.read_csv(FB / "reason_table_INTERNAL.csv").set_index("dong")
tg = rt[rt.target].copy()


def kind(t):
    t = str(t)
    return ("confirmed" if t.startswith("처방 확정") else "exclude_nb" if t.startswith("제외: 옆 동네")
            else "exclude_need" if t.startswith("제외: 필요") else "undecided")


tg["k"] = tg["유형"].map(kind)
gap = sb.gap.groupby(sb.index.map(tg.k)).sum()
excl = gap.reindex(["exclude_nb", "exclude_need"]).sum()
cnt = tg.k.value_counts()


def ab_row(prefix):
    r = ab[ab["수단"].str.startswith(prefix)].iloc[0]
    return float(r["하한"]), float(r["상한"])


b_lo, b_hi = ab_row("B 처방 확정")
u_lo, u_hi = ab_row("B 미확정")
n_lo, n_hi = ab_row("참고: 1순위 17곳 전체")
a_ref = ab_row("참고: A 10/12 방식")[1]
conf = sb[sb.index.map(tg.k) == "confirmed"]
act_c, gap_c = conf.act_m.sum(), conf.gap.sum()

F = [
    # key, 이름, 값, 단위, 표시, 출처
    ("meal_n", "급식카드 결제(결제 완료)", meal_n, "건", "int", "2차 반출 월별 표, 2023-06~2025-06"),
    ("gen_n", "같은 기간 일반 결제", gen_n, "건", "int", "2차 반출 월별 표"),
    ("months", "분석 기간", 25, "개월", "int", "3차 반출 기간 판정(2023-06~2025-06)"),
    ("vac_share", "방학(1·2·8월) 결제 비중", round(vac.n.sum() / meal_n * 100, 1), "%", "pct", "2차 반출 월별 표"),
    ("vac_acc", "방학 월평균 이용 계정", round(vac.n_cust.mean()), "계정", "int", "2차 반출 월별 표"),
    ("sem_acc", "학기 월평균 이용 계정", round(sem.n_cust.mean()), "계정", "int", "2차 반출 월별 표"),
    ("acc_ratio", "방학 이용 계정 ÷ 학기", round(vac.n_cust.mean() / sem.n_cust.mean(), 1), "배", "x", "2차 반출 월별 표"),
    ("st_sem", "학기 급식 비중(급식 ÷ 전체 결제)", 4.65, "%", "pct", "2차 반출 결과 R1"),
    ("st_vac", "방학 급식 비중", 18.38, "%", "pct", "2차 반출 결과 R1"),
    ("night_meal", "23~05시 급식 결제(25개월 합)", 11, "건", "int", "2차 반출 시간 파일"),
    ("lunch_sem", "학기 평일 11시 급식 ÷ 일반 비중", 0.65, "", "dec2", "2차 반출 시간 파일(3차 문서 §6-4 계산)"),
    ("shops", "대구로 가맹점", 22086, "곳", "int", "2차 반출 가맹점 분류"),
    ("able_y", "급식카드 등록 가맹점", 10781, "곳", "int", "2차 반출 가맹점 분류"),
    ("u2_shops", "등록·영업 중인데 급식 결제가 없는 가게", 631, "곳", "int", "3차 반출(영업·서비스 유지)"),
    ("avg_pay", "급식 결제 1건 평균 승인액", 18626, "원", "won", "4차 반출(승인액 합 ÷ 건수)"),
    ("day_once", "하루 1회만 결제한 날의 비중", round(235512 / 284110 * 100, 1), "%", "pct", "4차 반출 노트북 출력(계정-일 284,110)"),
    ("acct_vac", "방학에 결제한 계정", 6223, "계정", "int", "4차 반출 노트북 출력"),
    ("acct_le10k", "방학 하루 최대 결제가 1만 원 이하인 계정", 31, "계정", "int", "4차 반출 노트북 출력"),
    ("acct_le10k_pct", "그 비중", round(31 / 6223 * 100, 1), "%", "pct", "4차 반출 노트북 출력"),
    ("price_2026", "2026년 1끼 단가(대구 공통)", 10000, "원", "won", "대구광역시청 복지과 문의(2026-10-15)"),
    ("child_2023", "대구 6~18세(2023-06)", 270525, "명", "int", "주민등록 연령별 인구"),
    ("child_2025", "대구 6~18세(2025-06)", 262225, "명", "int", "주민등록 연령별 인구"),
    ("units", "동네 묶음(결합 단위)", 71, "개", "int", "행정동–법정동 대응표"),
    ("u2", "덜 쓰는 동네 후보(U2)", 37, "곳", "int", "4차 동×시기 분모로 재계산(out_V4FBK)"),
    ("top", "1순위 동네", len(tg), "곳", "int", "out_V4FBK 판정표"),
    ("excl", "점검 후 사각지대 아님", int(cnt.get("exclude_nb", 0) + cnt.get("exclude_need", 0)), "곳", "int", "out_V4FBK 판정표"),
    ("excl_nb", "옆 동네 가게 이용", int(cnt.get("exclude_nb", 0)), "곳", "int", "out_V4FBK 판정표"),
    ("excl_need", "도움이 필요한 집이 적음", int(cnt.get("exclude_need", 0)), "곳", "int", "out_V4FBK 판정표"),
    ("conf", "처방이 필요한 곳", int(cnt.get("confirmed", 0)), "곳", "int", "out_V4FBK 판정표"),
    ("und", "확인이 더 필요한 곳", int(cnt.get("undecided", 0)), "곳", "int", "out_V4FBK 판정표"),
    ("persist_both", "1순위 중 두 방학 반기 모두 하위 25%", 13, "곳", "int", "4차 방학 반기 파일(97 요약)"),
    ("rank_corr", "두 반기 동 순위 상관", 0.785, "", "dec3", "4차 방학 반기 파일, 156개 동"),
    ("gap_total", "1순위 겉보기 부족분(방학 월 결제)", round(gap.sum()), "건", "int", "out_V4FBK 시나리오 B"),
    ("gap_excl", "그중 사각지대 아닌 곳의 몫", round(excl), "건", "int", "out_V4FBK 시나리오 B"),
    ("gap_excl_pct", "겉보기 부족분 중 사각지대 아닌 곳 비중", round(excl / gap.sum() * 100), "%", "pct0", "out_V4FBK 시나리오 B"),
    ("cover", "급식 가게가 닿는 아이 비율(필요 가중)", 99.9, "%", "pct", "out_V4FBK MCLP 기준선(맞닿은 동)"),
    ("a_main", "가게 모집·활성화로 늘어나는 방학 월 계정", 0, "계정", "int", "out_V4FBK 시나리오 A"),
    ("a_ref", "가장 후한 가정에서 가게 모집 효과", round(a_ref), "계정", "int", "out_V4FBK 시나리오 A(참고)"),
    ("b_lo", "처방 확정 동 이용 회복(하한)", round(b_lo, 1), "계정", "dec1", "out_V4FBK 시나리오 B"),
    ("b_hi", "처방 확정 동 이용 회복(상한)", round(b_hi, 1), "계정", "dec1", "out_V4FBK 시나리오 B"),
    ("b_pct_lo", "처방 확정 동 자체 증가율(하한)", round(gap_c / 2 / act_c * 100), "%", "pct0", "out_V4FBK 시나리오 B"),
    ("b_pct_hi", "처방 확정 동 자체 증가율(상한)", round(gap_c / act_c * 100), "%", "pct0", "out_V4FBK 시나리오 B"),
    ("u_hi", "확인 필요 동 이용 회복(상한)", round(u_hi, 1), "계정", "dec1", "out_V4FBK 시나리오 B"),
    ("naive_lo", "판정 없이 17곳 전체(하한)", round(n_lo, 1), "계정", "dec1", "out_V4FBK 시나리오 B(참고)"),
    ("naive_hi", "판정 없이 17곳 전체(상한)", round(n_hi, 1), "계정", "dec1", "out_V4FBK 시나리오 B(참고)"),
    ("tip_avg", "대구로 배달 평균 배달팁", 1920, "원", "won", "4차 반출 배달 파일(1~20일 표본)"),
    ("mins_med", "동 평균 배달 시간의 중앙값", 8.9, "분", "dec1", "4차 반출 배달 파일(1~20일 표본)"),
    ("support_n", "대구로 급식 배달비 지원 아동(누적)", 6000, "명", "int", "매일신문 2024-02-29 보도(약)"),
    ("support_won", "대구로 급식 배달비 지원액(누적)", 2.7, "억 원", "dec1", "매일신문 2024-02-29 보도"),
    ("partial", "4차 급식 추출에 담긴 비율", 11, "%", "pct0", "4차 반출 노트북(38,854 ÷ 341,216)"),
    ("mde_a1", "시범 A 1년 판정으로 구별되는 최소 증가", 75, "%", "pct0", "4차 방학 반기 자연 변동"),
    ("mde_a2", "시범 A 2년 판정", 49, "%", "pct0", "4차 방학 반기 자연 변동"),
    ("exp_a_lo", "시범 A 기대 증가(하한)", 47, "%", "pct0", "out_V4FBK 시나리오 B"),
    ("exp_a_hi", "시범 A 기대 증가(상한)", 95, "%", "pct0", "out_V4FBK 시나리오 B"),
    ("app_target", "앱 점검한 1순위 동네", 13, "곳", "int", "앱 점검 기록(2026-10-15)"),
    ("app_ctrl", "앱 점검한 비교 동네", 3, "곳", "int", "앱 점검 기록(2026-10-15)"),
    ("kcb_hdong", "KCB 대구 행정동", 150, "개", "int", "4차 반출 KCB 표"),
]
facts = [dict(key=k, label=l, value=v, unit=u, fmt=f, source=s) for k, l, v, u, f, s in F]
save("facts", facts)

# ---- 월별 / 시간대 / 구 ------------------------------------------------------------------
save("monthly", [dict(month=f"{r.ym[:4]}-{r.ym[4:]}", regime=r.regime, meal=int(r.n), general=int(r.n_general))
                 for r in mg.itertuples()])
hm = pd.read_csv(E2 / "EXPORT_m2_hour_edge_meal.csv", encoding="utf-8-sig", dtype={"hb": str}).groupby("hb").n.sum()
hg = pd.read_csv(E2 / "EXPORT_m2_general_regime_dow_hour.csv", encoding="utf-8-sig")
hg["hb"] = np.where((hg.hour >= 23) | (hg.hour <= 5), "23-05", hg.hour.map(lambda h: f"{h:02d}"))
hg = hg.groupby("hb").n.sum()
hrs = [f"{h:02d}" for h in range(6, 23)] + ["23-05"]
save("hourly", [dict(hour=h if h != "23-05" else "23~05", meal=int(hm.get(h, 0)), general=int(hg[h]),
                     meal_pct=round(hm.get(h, 0) / hm.sum() * 100, 2), general_pct=round(hg[h] / hg.sum() * 100, 2))
                for h in hrs])
gu = pd.read_csv(HERE / "out" / "gungu_per_child.csv")
save("gu", [dict(gu=r.gu, vacation=round(r["방학"], 1), semester=round(r["학기"], 1), ratio=round(r["방학/학기"], 1))
            for _, r in gu.sort_values("방학").iterrows()])

# ---- 과정: 방문·자료·결함·깔때기 ----------------------------------------------------------
save("visits", [
    dict(step="1차 방문", date="2026-09-11", did="급식카드 결제가 언제 있나", got="월별·요일×시간 집계",
         found="방학이 결제의 절반 이상, 방학 이용 계정은 학기의 약 5배"),
    dict(step="2차 방문", date="2026-09-18", did="급식 정의 확정, 일반 결제와 비교", got="월별·시간대·가맹점 표 10개",
         found="급식은 점심·오후가 두껍고 저녁 피크가 얇다. 23시에 끊긴다"),
    dict(step="3차 방문", date="2026-09-29 ~ 10-02", did="동네(법정동) 단위로 나누기", got="동×시기 결제, 금액 분포",
         found="방학에 덜 쓰는 동네 37곳, 아이 수로 봐도 적은 1순위 17곳"),
    dict(step="현장 확인", date="2026-10-08 ~ 10-15", did="구청·시청 문의, 대구로 앱 점검", got="신청 방식, 2026년 단가, 1인분 목록",
         found="결제는 하루 한도로만 막힌다. 2026년 1끼 1만 원. 최소주문 면제 가게가 있으나 목록에 안 보인다"),
    dict(step="4차 방문", date="2026-10-16", did="가게 상태·소득·이동·배달·결제 금액", got="집계표 11개(6개는 일부 결함)",
         found="이유 판정: 사각지대 아님 10 · 처방 4 · 확인 필요 3"),
])
save("sources", [
    dict(data="대구로 결제", kind="미개방 상호제공", provider="경북대 첨단정보통신융합산업기술원", period="2023-06~2025-06",
         unit="결제 1건 → 가게 법정동", use="급식·일반 결제 집계, 시간대, 금액"),
    dict(data="대구로 가맹점", kind="미개방 상호제공", provider="경북대 첨단정보통신융합산업기술원", period="현재 상태",
         unit="가게", use="급식카드 등록·영업 상태, 가게 주소(법정동)"),
    dict(data="대구로 배달·고객", kind="미개방 상호제공", provider="경북대 첨단정보통신융합산업기술원", period="2023-06~",
         unit="배달 1건, 계정", use="배달 시간·배달팁, 계정 명의자 연령대"),
    dict(data="KCB 행정동 소득", kind="미개방 상호제공", provider="한국데이터산업진흥원(KCB)", period="2023년 4분기",
         unit="행정동 × 연령대", use="부모 세대(30·40대) 저소득 비율 = 필요의 대리 지표"),
    dict(data="주민등록 연령별 인구", kind="공개", provider="행정안전부", period="2023-06~2025-06 월별",
         unit="행정동", use="6~18세 아이 수"),
    dict(data="행정동–법정동 대응표", kind="공개", provider="행정안전부", period="2025-06-30 기준",
         unit="대응 관계", use="인구(행정동)와 가게(법정동)를 잇는 동네 묶음"),
    dict(data="법정동·리 경계", kind="공개", provider="국가공간정보포털", period="2026-09",
         unit="법정동·리", use="지도, 이웃 동네"),
    dict(data="현장 확인", kind="현장", provider="동구청·대구시청 복지과·대구로 앱", period="2026-10",
         unit="대구, 법정동", use="신청 방식, 2026년 단가, 1끼로 시킬 수 있는 가게"),
])
save("defects", [
    dict(item="급식 결제 추출", what="반복문 안에 들어가야 할 한 줄이 밖으로 나가 마지막 덩어리만 담김",
         hit="동네 가게 현황의 급식 칸, 집→가게 이동표, 1순위 대 나머지 비교", handled="가게 이유(R3)는 판단 불가로, 옆 동네 이유(R7)는 이웃 동네 비교로 대신(미리 정한 규칙)"),
    dict(item="배달 여건", what="날짜 조건과 취소 조건 오타", hit="취소율을 쓸 수 없음, 매달 1~20일만 집계",
         handled="배달 시간·배달팁만 사용"),
    dict(item="KCB 소득 연결", what="KCB가 출장소 2곳(논공 공단, 다사 서재)을 본 읍에 합쳐 냄",
         hit="논공·다사 동네 묶음의 필요 판정이 비었음", handled="출장소를 본 읍에 연결(인구로 확인). 규칙 자체는 그대로"),
])
save("funnel", [
    dict(stage="대구로 가게가 있는 동네(법정동)", n=198),
    dict(stage="일반 결제가 있어 비교할 수 있는 동네", n=181),
    dict(stage="방학 급식 비중 하위 25% + 등록 가게 3곳 이상", n=37),
    dict(stage="아이 수로 봐도 적은 곳 = 1순위", n=len(tg)),
    dict(stage="점검 후 남은 곳(처방 + 확인 필요)", n=int(cnt.get("confirmed", 0) + cnt.get("undecided", 0))),
    dict(stage="점검 후 처방이 필요한 곳", n=int(cnt.get("confirmed", 0))),
])

# ---- 이유·판정표 ------------------------------------------------------------------------
R = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
SYM = {"●": "해당", "○": "아님"}
rs = [
    ("R1", "도움이 필요한 집이 원래 적다", "KCB: 부모 세대(30·40대) 월소득 200만 원 이하 비율", "동별 급식카드 대상 아동 수"),
    ("R2", "다른 방법으로 먹는다(지역아동센터 등)", "자료 없음", "지역아동센터 정원"),
    ("R3", "급식 주문을 받는 가게가 적다", "동네 가게 현황(4차 결함으로 이번엔 판단 불가)", "운영사 가게 자료"),
    ("R4", "1끼 값으로 시킬 수 있는 가게가 적다", "앱 점검: 1인분 목록 위 10곳 중 1만 원 이하로 시킬 수 있는 가게", "운영사 메뉴·최소주문 자료로 전 동 자동 계산"),
    ("R5", "배달이 적거나 오래 걸린다", "대구로 일반 배달 ÷ 인구, 배달 시간, 배달팁", "같음(취소율 추가)"),
    ("R6", "몰라서 못 쓰거나 신청한 끼니가 안 맞는다", "동별 자료 없음", "구청 신청 유형(학기·방학 × 끼니)"),
    ("R7", "옆 동네 가게에서 사 먹는다", "이웃 동네 비교(이동표는 일부만 반출)", "배달 주소 기준 이동표"),
]
reasons = []
for code, name, now, ops in rs:
    v = tg[code].astype(str)
    reasons.append(dict(code=code, name=name, data_now=now, data_ops=ops, hit=int((v == "●").sum()),
                        no=int((v == "○").sum()), unknown=int(v.str.startswith("?").sum())))
save("reasons", reasons)

persist = {}
for line in (FB / "97_summary.txt").read_text(encoding="utf-8").splitlines():
    for d in tg.index:
        if line.startswith(d + " ") or line.startswith(d):
            if "두 방학 모두 낮음" in line:
                persist[d] = "두 방학 모두 낮음"
            elif "한 방학만 낮음" in line:
                persist[d] = "한 방학만 낮음"
EASY = {"confirmed": "처방 필요(배달)", "undecided": "확인 필요", "exclude_nb": "사각지대 아님: 옆 동네 가게 이용",
        "exclude_need": "사각지대 아님: 도움 필요 가구 적음"}
OWN = {"confirmed": "운영사", "undecided": "구청(현장 확인)", "exclude_nb": "—", "exclude_need": "—"}
RN = {"R1": "필요", "R2": "다른 경로", "R3": "가게", "R4": "1끼 값", "R5": "배달", "R6": "안내·신청", "R7": "옆 동네"}
order = {"confirmed": 0, "undecided": 1, "exclude_nb": 2, "exclude_need": 3}
tg = tg.assign(o=tg.k.map(order)).sort_values(["o", "gu"])
targets = []
for i, (d, r) in enumerate(tg.iterrows(), 1):
    g_, n_ = d.split("|")
    hit = [RN[c] for c in R if str(r[c]) == "●"]
    unk = [RN[c] for c in ["R1", "R3", "R4", "R5", "R7"] if str(r[c]).startswith("?")]
    row = dict(no=i, gu=g_, dong=n_, type=EASY[r.k], kind=r.k, hit=" · ".join(hit) or "—",
               unknown=" · ".join(unk) or "—", owner=OWN[r.k], persist=persist.get(d, "자료 부족"))
    row.update({c: ("●" if str(r[c]) == "●" else "○" if str(r[c]) == "○" else "?") for c in R})
    targets.append(row)
save("targets", targets)

# ---- 기대효과 ------------------------------------------------------------------------------
save("gap", [dict(group="사각지대 아님: 도움 필요 가구 적음", kind="exclude_need", gap=round(gap.get("exclude_need", 0), 1)),
             dict(group="사각지대 아님: 옆 동네 가게 이용", kind="exclude_nb", gap=round(gap.get("exclude_nb", 0), 1)),
             dict(group="확인 필요", kind="undecided", gap=round(gap.get("undecided", 0), 1)),
             dict(group="처방 필요(배달)", kind="confirmed", gap=round(gap.get("confirmed", 0), 1))])
save("scenario", [
    dict(option="가게 더 모집하기(대구 어디서나)", group="A 가게 늘리기", lo=0.0, hi=0.0),
    dict(option="쉬는 등록 가게 다시 살리기", group="A 가게 늘리기", lo=0.0, hi=0.0),
    dict(option="참고: 가게 모집, 가장 후한 가정", group="A 가게 늘리기(참고)", lo=round(a_ref, 1), hi=round(a_ref, 1)),
    dict(option="처방 필요 4곳 이용 회복", group="B 이용 회복", lo=round(b_lo, 1), hi=round(b_hi, 1)),
    dict(option="확인 필요 3곳(최대)", group="B 이용 회복(상한)", lo=round(u_lo, 1), hi=round(u_hi, 1)),
    dict(option="참고: 판정 없이 17곳 전체", group="B 이용 회복(참고)", lo=round(n_lo, 1), hi=round(n_hi, 1)),
])
save("daycount", [dict(times="1회", n=235512), dict(times="2회", n=41914), dict(times="3회", n=5528),
                  dict(times="4회", n=941), dict(times="5회 이상", n=284110 - 235512 - 41914 - 5528 - 941)])
mx = [("~8천", 11), ("~9천", 7), ("~1만", 13), ("~1.6만", 108), ("~1.8만", 79), ("~2만", 134),
      ("~2.4만", 960), ("~2.7만", 1539), ("~3만", 1112), ("3만~", 2260)]
save("maxday", [dict(bin=b_, accounts=n) for b_, n in mx])

# ---- 시범·처방·용어 ----------------------------------------------------------------------
save("variation", [dict(size="50건 이하", dongs=48, sd=0.588), dict(size="50~150건", dongs=29, sd=0.468),
                   dict(size="150~400건", dongs=26, sd=0.200), dict(size="400~1,000건", dongs=33, sd=0.172),
                   dict(size="1,000건 초과", dongs=31, sd=0.129)])
save("mde", [dict(arm="시범 A: 배달형", where="북구 학정동·검단동, 논공 금포리", size=238, sd=0.200, one_year=75, two_year=49,
                  expect="+47~95%(시나리오 B)"),
             dict(arm="시범 B: 가격형(탐색)", where="달성군 화원읍 전체", size=832, sd=0.172, one_year=62, two_year=41,
                  expect="탐색(기대값 없음)")])
save("pilot", [
    dict(when="2026-11 말", what="새 운영사 협약에 점검표 제출·시범 협조 조항. 2026년 여름방학 동 단위 집계 인계"),
    dict(when="2027-01·02", what="겨울방학: 시범 전 기준 측정"),
    dict(when="2027-03", what="1회차 점검표, 시범 대상 확정, 확인 필요 3곳 현장 확인"),
    dict(when="2027-04~07", what="준비: 방학 정기 배달편, 화원읍 면제·1인 메뉴 가게 모집, 앱 목록에 면제 표시"),
    dict(when="2027-08~2028-02", what="시범 1년차(여름·겨울방학)"),
    dict(when="2028-03", what="중간 판정(미리 정한 규칙)"),
    dict(when="2028-08~2029-02", what="시범 2년차(중간 판정이 '불확실'일 때)"),
    dict(when="2029-03", what="최종 판정, 다음 운영사 공모 조건에 반영"),
])
save("solutions", [
    dict(type="처방 필요: 배달", reason="배달(R5)", owner="운영사", action="방학 정기 배달편(점심·저녁 묶음 배달), 배달 가능 가게 우선 노출. 배달비는 이미 지원 중", check="방학 결제, 배달 시간"),
    dict(type="가격 장벽(구 단위)", reason="1끼 값(R4)", owner="대구시·구 + 운영사", action="최소주문 면제 가게와 1만 원 이하 1인 메뉴 늘리기, 앱 목록에 면제 표시", check="1끼 가능 가게 수, 새로 쓰기 시작한 계정"),
    dict(type="가게 부족", reason="가게(R3)", owner="운영사", action="쉬는 등록 가게 다시 살리기, 가맹점 모집(공급 점검 순서)", check="주문받는 가게 수"),
    dict(type="안내·신청", reason="안내·신청(R6)", owner="구청", action="방학 전 보호자와 아이 모두에게 안내, 신청 끼니 점검", check="신청 유형"),
    dict(type="확인 필요", reason="판단 불가 남음", owner="구청", action="현장 확인 질문지 → 다음 회차 판정", check="다음 회차 유형"),
    dict(type="사각지대 아님", reason="옆 동네(R7)·필요(R1)", owner="—", action="처방하지 않고 다음 회차에 관찰", check="이동표, 대상 아동 수"),
])
save("glossary", [
    dict(term="급식카드 결제", easy="급식 결제", code="M2", meaning="대구로 앱에서 아동급식카드로 결제하고 '결제 완료'된 건. 취소는 뺀다"),
    dict(term="일반 결제", easy="비교 기준", code="Q4", meaning="같은 앱의 급식카드 아닌 결제. 그 동네 배달 이용 규모를 재는 잣대"),
    dict(term="방학 · 전환 · 학기", easy="시기", code="레짐", meaning="방학=1·2·8월, 전환=7·12월(방학이 달 중간에 시작), 학기=나머지 달"),
    dict(term="LQ", easy="급식 비중 지수", code="LQ", meaning="그 동네 일반 결제 대비 급식 결제 비중을 대구 평균으로 나눈 값. 1보다 작으면 평균보다 덜 쓴다"),
    dict(term="아동 1천 명당 결제", easy="아이 수 기준 이용", code="per1k", meaning="동네 묶음의 6~18세 1천 명당 한 달 급식 결제 수. 결제는 가게 위치 기준이라 아이 집과 다를 수 있다"),
    dict(term="결합 단위", easy="동네 묶음", code="unit", meaning="인구(행정동)와 가게 주소(법정동)를 공식 대응표로 묶은 단위 71개"),
    dict(term="U2", easy="덜 쓰는 동네 후보", code="U2", meaning="방학 급식 비중 지수 하위 25%이고 급식카드 등록 가게가 3곳 이상인 동"),
    dict(term="1순위", easy="우선 점검 동네", code="D-017", meaning="U2 중 아이 수로 봐도 이용이 중앙값보다 낮은 곳"),
    dict(term="R1~R7", easy="이유 7가지", code="D-019", meaning="필요·다른 경로·가게·1끼 값·배달·안내·옆 동네. 결과를 보기 전에 판정 규칙을 고정했다"),
    dict(term="●  ○  ?", easy="판정 기호", code="", meaning="해당 / 아님 / 판단 불가(자료 없음, 경계값, 작은 숫자 가림)"),
    dict(term="억제", easy="작은 숫자 가리기", code="", meaning="개인이 드러나지 않게 5건 미만 같은 작은 칸을 빈칸으로 만드는 것"),
    dict(term="반출", easy="결과 가져오기", code="", meaning="안심구역 안에서 만든 집계표를 심사받아 밖으로 가져오는 것"),
    dict(term="데이터안심구역", easy="안심구역", code="", meaning="미개방 데이터를 지정된 센터 안에서만 분석하게 하는 곳"),
    dict(term="상호제공 데이터", easy="", code="", meaning="대회를 위해 기관들이 제공한 미개방 데이터(대구로, KCB)"),
    dict(term="Q1", easy="동네 가게 현황표", code="Q1", meaning="동별 급식카드 등록·영업 가게 수, 방학에 급식 주문을 받은 가게 수"),
    dict(term="K1 · K2", easy="소득 분포표", code="K1·K2", meaning="KCB 행정동 × 연령대 월소득 구간별 인원"),
    dict(term="Q3", easy="집→가게 이동표", code="Q3", meaning="계정의 '집 동네'(일반 결제를 가장 많이 한 동)와 급식을 주문한 가게 동의 짝"),
    dict(term="Q5", easy="하루 결제 금액표", code="Q5", meaning="계정이 하루에 쓴 급식 금액, 방학 중 하루 최대 금액"),
    dict(term="Q7", easy="배달 여건표", code="Q7", meaning="가게 동별 배달 건수·배달 시간·배달팁"),
    dict(term="Q8", easy="방학 반기 비교표", code="Q8", meaning="앞 반기(2023-08·2024-01·02)와 뒤 반기(2024-08·2025-01·02) 동별 결제"),
    dict(term="Q9 · Q10", easy="1순위 대 나머지 비교", code="Q9·Q10", meaning="하루 최대 결제 구간, 결제 시간대, 계정 명의자 연령대"),
    dict(term="X1", easy="반출 전 자동 검사", code="X1", meaning="저장한 표를 다시 읽어 5 미만 칸이 남았는지 검사"),
    dict(term="MCLP", easy="공급 점검", code="80", meaning="가게 위치로 아이들이 닿는 범위를 계산해, 가게를 어디에 더하면 닿는 아이가 늘어나는지 보는 최적화"),
    dict(term="시나리오 A · B", easy="두 가지 가정", code="D-018", meaning="A=가게를 늘리면, B=덜 쓰는 동네의 이용이 회복되면 늘어나는 방학 이용 계정"),
    dict(term="기대 이용", easy="", code="85", meaning="아이 수·배달 규모·가게 수가 비슷한 동네라면 이만큼 쓸 것이라는 값"),
    dict(term="겉보기 부족분", easy="", code="", meaning="1순위 동네의 기대 이용 − 실제 이용을 모두 더한 값"),
    dict(term="계정", easy="", code="", meaning="앱 가입 계정. 아이 한 명과 같지 않다(형제 카드, 보호자 명의)"),
    dict(term="법정동 · 행정동", easy="", code="", meaning="법정동=주소의 동(가게 위치), 행정동=주민센터 관할(인구 통계)"),
    dict(term="0회차", easy="첫 기준선", code="", meaning="이 분석. 방학 급식 사각지대 점검표의 첫 회"),
    dict(term="자연 변동", easy="", code="", meaning="아무것도 안 해도 방학마다 생기는 동네 이용의 오르내림"),
    dict(term="구별 가능한 최소 변화", easy="", code="", meaning="자연 변동보다 확실히 크다고 말할 수 있는 가장 작은 증가 폭"),
    dict(term="D-0xx", easy="결정 기록 번호", code="", meaning="분석 규칙을 정한 기록. 예: D-019 = 이유 판정 규칙"),
])

# ---- 지도: 법정동(·리) 경계 + 구 경계, EPSG:5186 그대로 단순화 --------------------------------------
umd = gpd.read_file(BD / "LSMD_ADM_SECT_UMD_27_202609.shp", encoding="cp949")
ri = gpd.read_file(BD / "LSMD_ADM_SECT_RI_27_202609.shp", encoding="cp949")
umd["code"], ri["code"] = umd.EMD_CD + "00", ri.RI_CD
geo = pd.concat([umd[~umd.COL_ADM_SE.isin(["27710", "27720"])][["code", "geometry"]],
                 ri[ri.COL_ADM_SE == "27710"][["code", "geometry"]]], ignore_index=True)
br = pd.read_csv(HERE / "out" / "bridge_bdong_hdong.csv", dtype=str).drop_duplicates("법정동코드")
geo = geo.merge(br[["법정동코드", "bkey"]], left_on="code", right_on="법정동코드")
geo = gpd.GeoDataFrame(geo, geometry="geometry", crs=umd.crs).dissolve(by="bkey").reset_index()
GU = {"27110": "중구", "27140": "동구", "27170": "서구", "27200": "남구", "27230": "북구", "27260": "수성구",
      "27290": "달서구", "27710": "달성군"}
gub = umd[umd.COL_ADM_SE.isin(GU)].dissolve(by="COL_ADM_SE").reset_index()
tk = {f"{t['gu']}|{t['dong']}": t for t in targets}


def gj(g, tol):
    s = g.simplify(tol, preserve_topology=True)
    d = json.loads(gpd.GeoSeries([s]).to_json())["features"][0]["geometry"]

    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], list) else [int(round(c[0])), int(round(c[1]))]
    d["coordinates"] = rnd(d["coordinates"])
    return d


rows = [dict(key=f"구|{GU[r.COL_ADM_SE]}", layer="gu", gu=GU[r.COL_ADM_SE], name=GU[r.COL_ADM_SE], kind="", no=None,
             type="", geometry=gj(r.geometry, 40)) for r in gub.itertuples()]
for r in geo.itertuples():
    t = tk.get(r.bkey)
    g_, n_ = r.bkey.split("|")
    rows.append(dict(key=r.bkey, layer="dong", gu=g_, name=n_, kind=t["kind"] if t else "", no=t["no"] if t else None,
                     type=t["type"] if t else "", geometry=gj(r.geometry, 25)))
print("지도 1순위 연결:", sum(1 for x in rows if x["no"]), "/", len(targets))
save("geo", rows)
