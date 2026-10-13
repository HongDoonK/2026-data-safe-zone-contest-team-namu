# 3차 안심구역 방문 — 손타이핑 코드

2026-10-02 예정 방문용. 코드 블록 하나를 주피터 셀 하나로 입력한다. 아래 코드는 2026-10-01 계획서 원본 15개 셀과 동일하다. 검토 대기 중인 선택 수정안은 포함하지 않았다.

## 실행 전

- PAY·SHOP은 현장 파일의 실제 경로로 바꾼다.
- 같은 노트북, 같은 커널에서 순서대로 실행한다. 중간에 커널을 재시작하면 선행 셀도 다시 실행한다.
- CSV는 노트북의 현재 작업 폴더에 저장된다. 이 폴더 위치를 확인해 둔다.
- 동 이름 반출 승인을 확인한다. 불가하면 M1 전에 보고한다. 군구+번호 대체 셀은 원본에 없다.
- 아래 확인 수치는 2차 반출물 기준의 재현 확인값이다. 현장에서 새로 나온 수치는 [잠정 — 반출 전]으로 적는다. 다르면 기록·보고한다.
- 퇴실 90분 전(계획서 기본 14:00)이 되면 분석을 멈추고 반출 신청으로 넘어간다.

실행 순서: **S1 → P1 → P1b → P2 → P3(필요할 때) → M1 → M2 → M3 → M4 → M5 → M6 → A1 → A2 → A3**. **A4는 현재 건너뛴다.**


## S1. 공통 설정 — 가장 먼저

```python
import pandas as pd, numpy as np
PAY = r"결제파일경로.csv"
SHOP = r"가맹점파일경로.csv"
ENC = "utf-8"
C_SHOP, C_CUST, C_GBN, C_STAT = "SHOP_ID", "CUST_ID", "PAY_GBN", "CARD_PAY_GBN"
C_TIME, C_TOT, C_APP, C_DISC = "CARD_APP_TIME", "TOT_AMT", "CARD_APP_AMT", "CHILD_DISC_AMT"
MEAL, DONE = ["아동급식카드"], "완료"
print(pd.read_csv(PAY, nrows=1, encoding=ENC, dtype=str).columns.tolist())
print(pd.read_csv(SHOP, nrows=1, encoding=ENC, dtype=str).columns.tolist())
```

확인: PAY와 SHOP의 자리표시자를 현장 실제 파일 경로로 바꾼다. 출력은 결제 15열·가맹점 8열인지 확인한다. 컬럼 상수와 헤더를 대조한다. A1·M1·M6에는 직접 적힌 컬럼명도 있으므로 함께 대조한다.


첫 헤더에 \ufeff가 남으면 ENC="utf-8-sig", UnicodeDecodeError가 나면 체크리스트대로 ENC="cp949"로 바꿔 다시 확인한다. 상수 밖 직접 컬럼명이 다르면 보고한다.


## P1. 결제수단별 할인 양수 건수 확인

```python
acc = []
for ch in pd.read_csv(PAY, usecols=[C_GBN, C_TIME, C_DISC], dtype=str, encoding=ENC,
                      chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    ch["d"] = pd.to_numeric(ch[C_DISC], errors="coerce").fillna(0) > 0
    acc.append(ch.groupby([C_GBN, "ym"]).d.agg(["size", "sum"]))
a = pd.concat(acc).groupby(level=[0, 1]).sum()
a.columns = ["n", "n_disc"]
print(a.groupby(level=0)[["n", "n_disc"]].sum().to_string())
pre = a.reset_index()
pre = pre[(pre.ym < "202306") & (pre.n_disc > 0)]
print(pre.pivot(index="ym", columns=C_GBN, values="n_disc").fillna(0).to_string())
```

확인: 첫 표는 결제수단 19행이다. 급식 전체 n은 369,750(취소 포함, 2차 반출 기준). 둘째 표의 빈 ym은 승인시각 결측이므로 2023-05 이전 기록으로 세지 않는다.


## P1b. 급식 월별 할인 표지 확인 — P1 바로 뒤

```python
print(a.loc["아동급식카드"].to_string())
```

확인: 26행(빈 ym + 202306~202506), n 합 369,750인지 확인한다. 2023-06~12의 n_disc가 거의 0인지, 특정 달에 비율이 떨어지는지 기록한다. A1보다 먼저 실행한다.


## P2. 행복페이·카드·대구로페이 월별 추이

```python
b = a.reset_index()
b = b[b[C_GBN].isin(["행복페이", "카드", "대구로페이"])]
print(b.pivot(index="ym", columns=C_GBN, values="n").fillna(0).to_string())
b["vac"] = b.ym.str[4:6].isin(["01", "02", "08"])
b["yr"] = b.ym.str[:4]
print(b.groupby([C_GBN, "yr", "vac"]).n.sum().unstack().to_string())
```

확인: 대구로페이의 첫 관측 월을 적는다. 연도별 방학 비중은 True / (False + True)로 읽는다. 빈 ym·빈 yr 줄은 기간 판정에서 제외한다.


## P3. 계정 겹침 — P1·P1b·P2만으로 애매할 때

```python
meal_c, pre_c = set(), {}
for ch in pd.read_csv(PAY, usecols=[C_CUST, C_GBN, C_TIME], dtype=str, encoding=ENC,
                      chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    meal_c |= set(ch.loc[ch[C_GBN].isin(MEAL), C_CUST])
    for gname, sub in ch[ch.ym < "202306"].groupby(C_GBN):
        pre_c[gname] = pre_c.get(gname, set()) | set(sub[C_CUST])
rows = [(k, len(v), len(v & meal_c)) for k, v in pre_c.items()]
r = pd.DataFrame(rows, columns=["gbn", "pre_cust", "also_meal"])
r["share"] = (r.also_meal / r.pre_cust).round(3)
print(r.sort_values("pre_cust", ascending=False).to_string())
```

확인: 승인시각 결측이 섞이는 현금·모바일상품권·결제수단없음·아동급식카드 행은 체크리스트대로 무시한다. share만으로 판정하지 않는다.


### P0 판정 기록 — 사람이 체크리스트 순서대로 판단

급식 외 코드에 할인 양수 값이 흔하거나, 2023-06~12 급식의 할인 표지가 거의 0이면 **C가 우선**이다. 둘 다 아니면 날짜가 있는 이전 기간의 반복·방학 증가 여부를 본다.

- A: 이전 표지가 없거나 산발적 → 주 분석 25개월 유지.
- B: 매월 반복하고 방학에 증가 → 주 분석은 25개월 유지, 확장판은 기간 민감도로만 사용.
- C: 판단 불가 → A와 같은 기간으로 처리하고 한계를 기록.

판정 ___ / 근거 ___ / 할인 비율이 갑자기 떨어진 달 ___


## M1. 가맹점 읽기와 법정동 키 만들기

```python
sh = pd.read_csv(SHOP, dtype=str, encoding=ENC, keep_default_na=False).apply(lambda s: s.str.strip())
sh["dong"] = sh.GUNGU_NM + "|" + sh.DONG_NM
d2 = sh.set_index("SHOP_ID").dong
reg = sh.groupby("dong").agg(shops=("SHOP_ID", "size"),
                             able_y=("CHILD_ABLE_YN", lambda s: (s == "Y").sum()))
print(len(reg), reg.shops.sum())
print(reg.sort_values("shops", ascending=False).head(10).to_string())
print("빈 동 이름:", (sh.DONG_NM == "").sum())
```

확인: 가맹점 합 22,086, 동 수 203~220(체크리스트 기준)과 빈 동 이름 수를 확인한다. 군구가 다른 같은 동 이름은 군구|동 키로 구분한다.


## M2. 급식 완료 결제 읽기

```python
mr = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_CUST, C_GBN, C_STAT, C_TIME], dtype=str,
                      encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    mr.append(ch[(ch[C_GBN].isin(MEAL)) & (ch[C_STAT] == DONE)])
m = pd.concat(mr)
m["ym"] = m[C_TIME].str[:6]
m = m[(m.ym >= "202306") & (m.ym <= "202506")]
mm = m.ym.str[4:6]
m["R"] = np.where(mm.isin(["01", "02", "08"]), "방학",
                  np.where(mm.isin(["07", "12"]), "전환", "학기"))
m["dong"] = m[C_SHOP].map(d2)
print(len(m), "동 결측:", m.dong.isna().sum(), "동 수:", m.dong.nunique())
```

확인: 급식 341,216행, 동 결측 0인지 확인한다. 동 수를 적어 둔다. 방학 1·2·8월, 전환 7·12월, 나머지는 학기다.


## M3. 일반 완료 결제 집계

```python
gs = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_GBN, C_STAT, C_TIME], dtype=str, encoding=ENC,
                      chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    ch = ch[(ch[C_STAT] == DONE) & (~ch[C_GBN].isin(MEAL)) & (ch.ym >= "202306") & (ch.ym <= "202506")]
    gs.append(ch[C_SHOP].value_counts())
gp = pd.concat(gs).groupby(level=0).sum()
g = gp.groupby(gp.index.map(d2)).sum()
print(gp.sum(), g.sum())
```

확인: 두 출력이 모두 3,612,950인지 확인한다. 일반 결제는 승인시각이 있고 급식이 아닌 완료 결제다. ~ 기호를 빠뜨리지 않는다.


## M4. 동 × 기간 구분 표와 억제

```python
t = m.groupby(["dong", "R"]).agg(n=(C_SHOP, "size"), n_shop=(C_SHOP, "nunique"), n_cust=(C_CUST, "nunique"))
bad = (t.n < 5) | (t.n_shop < 3) | (t.n_cust < 5)
print("칸", len(t), "억제", int(bad.sum()))
tt = t.copy()
tt[bad] = np.nan
tt.to_csv("EXPORT_m4_dong_regime.csv", encoding="utf-8-sig")
k = bad.groupby(level=0).sum()
print("억제 칸이 정확히 1개인 동:", int((k == 1).sum()))
print(t.groupby(level=1).n.sum().to_string())
```

확인: 칸 수·억제 수·억제 1칸인 동 수를 기록한다. 마지막 출력 순서와 합계는 방학 188,725 / 전환 47,615 / 학기 104,876이다. 레짐은 방학·전환·학기라는 기간 구분을 뜻한다.


## M5. 동별 종합표와 LQ

```python
agg = m.groupby("dong").agg(n=(C_SHOP, "size"), n_shop=(C_SHOP, "nunique"), n_cust=(C_CUST, "nunique"))
tot = reg.join(agg)
tot[["n", "n_shop", "n_cust"]] = tot[["n", "n_shop", "n_cust"]].fillna(0)
tot["gen"] = g
tot["able_share"] = (tot.able_y / tot.shops).round(3)
tot["lq"] = ((tot.n / tot.gen) / (tot.n.sum() / tot.gen.sum())).round(3)
bad2 = (tot.n < 5) | (tot.n_shop < 3) | (tot.n_cust < 5) | tot.index.isin(k[k == 1].index)
tot.loc[bad2, ["n", "n_shop", "n_cust", "lq"]] = np.nan
tot.loc[tot.shops < 3, ["shops", "able_y", "able_share", "gen"]] = np.nan
tot.to_csv("EXPORT_m4_dong_total.csv", encoding="utf-8-sig")
print(int(bad2.sum()), "동 억제 /", len(tot))
print(tot.dropna(subset=["lq"]).sort_values("lq", ascending=False).head(10).to_string())
print(tot.dropna(subset=["lq"]).sort_values("lq").head(10).to_string())
```

확인: 동 수는 M1과 같아야 한다. 유효 억제 = M5 억제 동 수 − (M1 동 수 − M2 동 수)를 손으로 계산한다. 1이면 이 파일은 반출 보류 후 보고한다. LQ는 급식/일반 비율을 전체 급식/일반 비율과 비교한 값이다.


## M6. 등록 Y·일반 결제 있음·급식 0 확인표

```python
u = sh.set_index("SHOP_ID").copy()
u["gen"] = gp
u["meal"] = m.groupby(C_SHOP).size()
u[["gen", "meal"]] = u[["gen", "meal"]].fillna(0)
sel = u[(u.CHILD_ABLE_YN == "Y") & (u.gen > 0) & (u.meal == 0)]
print("U2 대상:", len(sel))
print(sel.groupby(["STORE_STATUS", "SERVICE_CLOSED"]).size().to_string())
e2 = sel.groupby(["GUNGU_NM", "STORE_STATUS"]).size().unstack(fill_value=0)
e2[e2 < 3] = np.nan
e2.to_csv("EXPORT_m4_u2_gungu_status.csv", encoding="utf-8-sig")
live = sel[(sel.STORE_STATUS == "01") & (sel.SERVICE_CLOSED == "N")]
print("영업 중·서비스 유지:", len(live), "/", len(sel))
```

확인: U2 대상 1,412, 상태 교차표 합이 대상 수와 같은지 확인한다. 영업 중·서비스 유지 수를 메모한다. 01은 숫자 1이 아닌 문자열이며 N도 정확히 친다.


## A1. 금액 읽기와 숫자 변환 — 15줄 그대로

```python
NUM = [C_TOT, "ETC_AMT", "DISC_AMT", "MILEAGE_AMT", C_APP,
       "PACK_DISC_AMT", "SHOP_DISC_AMT", "GOOD_DISC_AMT", C_DISC]
ar, gh = [], []
for ch in pd.read_csv(PAY, usecols=[C_GBN, C_STAT, C_TIME, C_CUST] + NUM, dtype=str,
                      encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    ch = ch[(ch[C_STAT] == DONE) & (ch.ym >= "202306") & (ch.ym <= "202506")]
    ch["meal"] = ch[C_GBN].isin(MEAL)
    ar.append(ch[ch.meal])
    gh.append((pd.to_numeric(ch.loc[~ch.meal, C_TOT], errors="coerce") // 500).value_counts())
a = pd.concat(ar)
for c in NUM:
    a[c] = pd.to_numeric(a[c], errors="coerce").fillna(0)
print(len(a), a[NUM].describe().round(0).to_string())
```

확인: 341,216행인지 확인한다. 이 셀은 P1의 a를 덮어쓴다. 이후 P1b·P2를 다시 볼 때는 P1부터 다시 실행해야 한다.


## A2. 금액 관계와 분위수 확인

```python
print("disc>0 비율:", round((a[C_DISC] > 0).mean(), 3))
print("app+disc=tot:", round((a[C_TOT] - a[C_APP] - a[C_DISC]).abs().le(1).mean(), 3))
print("app=tot    :", round((a[C_TOT] - a[C_APP]).abs().le(1).mean(), 3))
print("disc=tot   :", round((a[C_TOT] - a[C_DISC]).abs().le(1).mean(), 3))
print(a[C_DISC].quantile([.1, .25, .5, .75, .9, .99]).to_string())
print(a[C_TOT].quantile([.1, .25, .5, .75, .9, .99]).to_string())
print(a.groupby(a[C_DISC] // 500 * 500).size().head(20).to_string())
```

확인: disc>0 비율, 세 항등식 비율, 할인·총액 분위수를 기록한다. 어느 관계도 뚜렷하지 않으면 관계 불명으로 적는다. 이 출력은 CSV에 저장되지 않으므로 반출 메모에 포함한다.


## A3. 500원 구간 금액표 저장

```python
hm = a.groupby(a[C_TOT] // 500 * 500).agg(n=(C_TOT, "size"), n_cust=(C_CUST, "nunique"))
hg = pd.concat(gh).groupby(level=0).sum().rename("n_general")
hg.index = hg.index * 500
e = hm.join(hg, how="outer")
bad = (e.n < 5) | (e.n_cust < 5)
e.loc[bad, ["n", "n_cust"]] = np.nan
e.index.name = "tot_amt_bin500"
e.to_csv("EXPORT_m5_amount_hist.csv", encoding="utf-8-sig")
print(e.head(30).to_string())
```

확인: n·n_cust·n_general 열을 확인한다. 음수 구간이 있으면 기록한다. 원본은 일반 n_general의 5 미만 값을 가리지 않는다. 해당 값이 남으면 반출 전 담당자에게 보고한다. 일반 건수 억제 선택판은 아직 반영하지 않았다.


## A4. 참고용 — 현재 계획에서는 건너뛰기

```python
a["bin"] = a[C_TOT] // 500 * 500
p = a.groupby(["ym", "bin"]).size().rename("n").reset_index()
top = p.sort_values("n").groupby("ym").tail(1)
print(top.to_string())
```

확인: 원본 체크리스트에서 현재 해당 없음으로 정한 셀이다. 기간 중 공식 단가 개정 시점을 확인해 실행하기로 한 경우에만 사용한다.


## 반출 신청 전

신청 파일:

- EXPORT_m4_dong_regime.csv
- EXPORT_m4_dong_total.csv
- EXPORT_m4_u2_gungu_status.csv
- EXPORT_m5_amount_hist.csv
- filter_definition_v3.txt — 셀에서 자동 생성되지 않으므로 별도로 작성한다.

확인할 항목:

- 합계 행과 SHOP_ID·CUST_ID 등 원자료 ID가 없는지.
- 레짐 1칸만 억제된 동의 합계가 total에서도 공란인지.
- 레짐별 공란 수가 방학·전환·학기 중 어느 것도 1이 아닌지. M4의 '억제 1칸인 동 수'와 다른 점검이다.
- total의 유효 억제 수 및 shops 공란 수가 각각 1이 아닌지.
- u2의 공란 수와 amount의 급식 n 공란 수가 각각 1이 아닌지.
- A3 일반 n_general에 5 미만 값이 남는지. 원본에는 이 열 억제가 없다.
- 동 이름 반출 승인과 파일 내용이 일치하는지.

점검에 걸리면 해당 파일을 보류하고 보고한다.

메모에 적을 것: P0 판정과 근거, 급식 정의(아동급식카드+완료·중복 미제거), 기간(2023-06~2025-06), 기간 구분, 법정동 키, 억제 규칙, 셀별 확인값, M6의 영업 중·서비스 유지 수, A2의 비율·분위수. 메모의 5건 미만 수치는 '5 미만'으로 적고 최솟값·최댓값은 적지 않는다. 메모도 반출 신청에 포함한다.

## 오류가 나면

셀 이름·오류 마지막 줄·발생 줄 번호를 기록한다. 실패한 셀은 오타를 고친 뒤 전체를 다시 실행한다.

- A1 뒤 P1b·P2가 실패함: P1 → P1b → P2 순서로 복구.
- 커널 재시작 뒤 M5만 필요함: S1 → M1 → M2 → M3 → M4 → M5.
- uniquely valued Index: SHOP_ID 중복 가능성. 임의로 제거하지 말고 보고.
- MEAL·완료·방학·전환·학기·Y·01·N 오타는 예외 없이 결과만 바뀔 수 있으므로 인쇄본과 대조.
