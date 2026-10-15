# T2 4차 방문 실행 계획 (2026-10-14 또는 10-15, 팀 확정)

> **작성**: 2026-10-12 / **근거**: 3차 반출 결과 [T2_export_1002_results.md](T2_export_1002_results.md) §6, 결정 [D-015~D-017](../DECISIONS.md)
> **전제**: 코드 반입 불가. 셀은 현장에서 손으로 친다. 셀마다 13줄 이하, 확인 출력을 둔다(3차와 같은 형식).
> **성격**: **마지막 분석 방문.** 반출은 대개 당일 완료된다(팀 확인). 기획서 마감 10/22 18:00, 제출 목표 10/20~21.
> **3차의 교훈**: M4 셀에서 억제 한 줄(`tt[bad] = np.nan`)이 빠진 채 반출됐다. 이번에는 **모든 저장 셀에 억제 줄을 두고, 반출 전에 셀 X1이 파일을 다시 읽어 자동 점검**한다. X1이 "통과"를 찍지 않은 파일은 반출 신청하지 않는다.
> **총 예상**: 약 4시간 25분 + 반출 신청 30분. 순서를 바꾸지 않는다. (10/15: Q1b `nonY_live`, Q8, Q5c, Q9 추가 · 10/15 밤: 신한 미제공 → Q6 삭제, Q7 배달을 4순위로 올리고 배달팁 추가, Q10 계정 연령대 선택 추가)

---

## 0. 오늘 얻을 것

| 순위 | 셀 | 질문 | 어디에 쓰나 | 시간 |
|---|---|---|---|---|
| 1 | **Q4·Q1** 동별 가게 상태 | 동마다 등록 가게 중 실제 영업 중인 곳, 방학에 급식 주문을 받은 가게는 몇 곳인가 | 확인표(이유 3), **MCLP 공급** | 25분 |
| 2 | **Q2** KCB 소득 | 행정동별 30·40대 저소득 비율은 어떤가 | 필요도(이유 1), **상호제공 연계 가점** | 40분 |
| 3 | **Q3** 집 동 → 가게 동 흐름 | 아이들은 자기 동네 가게에서 주문하는가, 옆 동네로 가는가 | 확인표(이유 7), **MCLP 커버 범위** | 40분 |
| 3-2 | **Q8** 방학 앞·뒤 반기 (10/15 추가) | 1순위 동네가 두 시기(2023-08~2024-02 / 2024-08~2025-02) 모두 낮은가 | **1순위의 재현성**(우연이 아님을 보이는 근거) | 10분 |
| 4 | **Q7** 동별 배달 결과 (10/15 올림) | 동별 배달 취소율·배달 시간·배달팁 | 확인표(이유 5). 신한 배달매출이 제공되지 않아 대신 | 20분 |
| 5 | **Q5** 하루 결제 합 (+Q5c·Q9, 10/15 추가) | 하루 한도(끼니 수 × 단가)가 실제 결제를 막는가. 계정이 방학 내내 1끼 한도 안에서만 쓰는가. **1순위 17곳은 나머지와 다른가** | 확인표(이유 4·6), H5 | 45분 |
| 6 | Q10 급식 계정 명의자 연령대 (선택) | 1순위 대 나머지, 누가 앱을 쓰나(보호자·아동) | 처방의 안내 대상 | 시간 남을 때 |
| — | **X1·메모·반출** | 억제 자동 점검, 정의 메모 | 반출 | 30분 |

**4차 제공 데이터(2026-10-15 확정)**: 대구로 플랫폼 6종(가맹점·결제·고객·리뷰·배달·주문, 상호제공) + 행정동 단위 소득관련 통계정보(KCB, 상호제공). **신한카드 배달매출은 없다.**

Q4는 Q1이 쓰는 `gp`(가맹점별 일반 결제)를 만들기 때문에 Q1보다 먼저 친다.

**중단 규칙**: 퇴실 90분 전(기본 14:00)이 되면 돌던 셀을 끊고 X1 → 메모 → 반출 신청으로 간다.

---

## 1. 방문 전 (10/12~13)

| # | 할 일 | 이유 | 담당 |
|---|---|---|---|
| A | **방문일 확정, 지금까지 실제 방문 일수 확인** | 5일 이상이면 방문 점수 만점. 반출 심사 3일 | 운영 |
| B | **3차 반출 파일 1개(레짐 파일)가 억제 없이 나간 일을 센터에 알릴지 결정** | 팀 결정 사항. 알린다면 방문 때 함께 | 팀 |
| C | 센터 작업공간에 **3차 노트북(2026_10_02.ipynb)이 남아 있는지** 센터에 문의 | 남아 있으면 M1·M2를 다시 칠 필요 없음(15분 절약) | 운영 |
| D | 이 문서 §2~§7 **인쇄** | 화면 전환 없이 타이핑 | 전원 |
| E | KCB 파일이 **작업공간에서 열리는지** 센터에 문의(신한은 이번 제공 목록에 없음) | Q2 전제 | 운영 |

---

## 2. 공통 설정

### 셀 S1 — 상수 (10줄)

```python
import pandas as pd, numpy as np, os, glob
PAY = r"import_data/TB_CKNU_INS_DAEGURO_PAY/INS_DAEGURO_PAY.csv"
SHOP = r"import_data/TB_CKNU_INS_DAEGURO_SHOP/INS_DAEGURO_SHOP.csv"
ENC = "utf-8"
C_SHOP, C_CUST, C_GBN, C_STAT = "SHOP_ID", "CUST_ID", "PAY_GBN", "CARD_PAY_GBN"
C_TIME, C_TOT, C_APP, C_DISC = "CARD_APP_TIME", "TOT_AMT", "CARD_APP_AMT", "CHILD_DISC_AMT"
MEAL, DONE = ["아동급식카드"], "완료"
print(pd.read_csv(PAY, nrows=1, encoding=ENC, dtype=str).columns.tolist())
print(pd.read_csv(SHOP, nrows=1, encoding=ENC, dtype=str).columns.tolist())
```
**확인**: 3차와 같은 컬럼 이름이 보인다(경로는 3차 노트북과 같음).

### 셀 F0 — 파일 찾기 (5줄)

```python
for root, _, files in os.walk("import_data"):
    for f in files:
        p = os.path.join(root, f)
        print(round(os.path.getsize(p) / 1e6), "MB", p)
```
**확인**: KCB 파일(`TB_KCB_INCOME_STAT_DATASET.csv`, 약 98MB, 이름에 KCB·INCOME), 대구로 배달 파일(`INS_DAEGURO_DELIVERY.csv` 예상, 약 259MB), 대구로 고객 파일(`INS_DAEGURO_CUST.csv` 예상, 약 11MB)의 **경로와 크기를 받아 적는다.**

### 셀 F1 — KCB·배달·고객 첫 줄 보기 (11줄)

```python
KCB = r"여기에_KCB_경로.csv"
DELI = r"여기에_대구로_배달_경로.csv"
CUST = r"여기에_대구로_고객_경로.csv"
for f in [KCB, DELI, CUST]:
    for enc in ["utf-8", "utf-8-sig", "cp949"]:
        try:
            print(f, enc)
            print(pd.read_csv(f, nrows=3, dtype=str, encoding=enc).to_string())
            break
        except UnicodeDecodeError:
            pass
```
**확인**: 각 파일이 어떤 인코딩에서 읽혔는지, **열 이름 전체**를 받아 적는다. 배달 파일에는 `SHOP_ID DELI_ALLOC_TIME DELI_COMP_TIME DELI_CANCEL_TIME DELI_TIP_AMT`, 고객 파일에는 `CUST_ID BR_DT`가 있어야 한다(정의서 기준). 이름이 다르면 Q7·Q10의 열 이름을 고친다. 배달·고객 파일 인코딩이 `utf-8`이 아니면 Q7·Q10의 `encoding=ENC`를 그 값으로 바꾼다. KCB 인코딩은 K1의 `KENC`에 쓴다.

### 셀 M1 — 가맹점과 동 키 (4줄) · 3차 노트북이 있으면 그 M1 실행

```python
sh = pd.read_csv(SHOP, dtype=str, encoding=ENC, keep_default_na=False).apply(lambda s: s.str.strip())
sh["dong"] = sh.GUNGU_NM + "|" + sh.DONG_NM
d2 = sh.set_index("SHOP_ID").dong
print(len(sh), sh.dong.nunique())
```
**확인**: `22086 205`

### 셀 M2 — 급식 결제 (13줄) · 3차 노트북이 있으면 그 M2 실행

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
**확인**: `341216 동 결측: 0 동 수: 189`

---

## 3. 1순위 — 동별 가게 상태 (Q4 → Q1, 25분)

### 셀 Q4 — 일반 결제: 가맹점 × 레짐 (13줄, 1~2분)

```python
gs = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_GBN, C_STAT, C_TIME], dtype=str, encoding=ENC,
                      chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    ch = ch[(ch[C_STAT] == DONE) & (~ch[C_GBN].isin(MEAL)) & (ch.ym >= "202306") & (ch.ym <= "202506")]
    mm = ch.ym.str[4:6]
    ch["R"] = np.where(mm.isin(["01", "02", "08"]), "방학", np.where(mm.isin(["07", "12"]), "전환", "학기"))
    gs.append(ch.groupby([C_SHOP, "R"]).size())
gsr = pd.concat(gs).groupby(level=[0, 1]).sum()
gp = gsr.groupby(level=0).sum()
print(gsr.sum(), gp.sum())
print(gsr.groupby(level=1).sum().to_string())
```
**확인**: `3612950 3612950`. 레짐별 합(방학·전환·학기)을 받아 적는다.

### 셀 Q4b — 동 × 레짐 일반 결제 저장 (7줄)

```python
gd = gsr.groupby([gsr.index.get_level_values(0).map(d2), gsr.index.get_level_values(1)]).sum().unstack(fill_value=0)
gd.index.name = "dong"
print(gd.shape, int(gd.values.sum()))
gd[gd < 5] = np.nan
gd.loc[gd.isna().any(axis=1)] = np.nan
gd.to_csv("EXPORT_v4_dong_regime_general.csv", encoding="utf-8-sig")
print(int(gd.isna().any(axis=1).sum()), "동 억제")
```
**확인**: 행 수는 205 이하, 합 3,612,950. **5번째 줄**(한 칸이라도 억제되면 그 동 전체 억제)을 빠뜨리지 않는다 — 3차 반출의 동 합계로 역산되는 것을 막는다.

### 셀 Q1 — 동별 가게 상태 (13줄)

```python
u = sh.set_index("SHOP_ID").copy()
u["gen"] = gp
u["meal"] = m.groupby(C_SHOP).size()
u["meal_vac"] = m[m.R == "방학"].groupby(C_SHOP).size()
u = u.fillna({"gen": 0, "meal": 0, "meal_vac": 0})
u["live"] = (u.STORE_STATUS == "01") & (u.SERVICE_CLOSED == "N")
u["Y"] = u.CHILD_ABLE_YN == "Y"
q = pd.DataFrame({"able_live": u.Y & u.live, "meal_vac_shop": u.meal_vac > 0,
                  "meal_vac_live": (u.meal_vac > 0) & u.live, "meal_vac10_live": (u.meal_vac >= 10) & u.live,
                  "u2_live": u.Y & u.live & (u.gen > 0) & (u.meal == 0)})
qd = q.groupby(u.dong).sum()
qd.index.name = "dong"
print(len(qd), qd.sum().to_string())
```
**확인**: `u2_live` 합 **631**(3차 M6과 같아야 한다). `able_live`는 등록 Y 10,781곳 중 영업 중인 수, `meal_vac_shop`은 방학에 급식 결제가 1건 이상 있었던 가게 수, `meal_vac10_live`는 방학 급식 결제 10건 이상이면서 지금 영업 중인 가게 수(**MCLP의 엄격한 공급**) — 받아 적는다.

### 셀 Q1b — 저장 (4줄)

```python
qd["nonY_live"] = (~u.Y & u.live & (u.gen > 0)).groupby(u.dong).sum()
qd[qd < 3] = np.nan
qd.to_csv("EXPORT_v4_dong_shop_state.csv", encoding="utf-8-sig")
print(int(qd.isna().sum().sum()), "칸 억제 /", qd.size)
```
**첫 줄(10/15 추가)**: `nonY_live` = 등록 Y가 아니지만 영업 중이고 일반 결제가 있는 가게 수. MCLP "모집"이 동마다 실제로 데려올 수 있는 가게 수의 상한이다.
**메모에 적을 것**: 이 파일의 `able_live`와 3차 반출의 `able_y`의 차이(= 등록했지만 영업하지 않는 가게 수)가 1~2인 동이 생길 수 있다. 가게 수이고 개인 정보가 아니지만, 센터 심사가 지적하면 그 동의 `able_live`를 지운다.

---

## 4. 2순위 — KCB 소득 (Q2, 40분)

### 셀 K1 — 읽고 값 확인 (8줄)

```python
KENC = "utf-8"
k = pd.read_csv(KCB, dtype=str, encoding=KENC, keep_default_na=False).apply(lambda s: s.str.strip())
print(k.shape, k.columns.tolist())
k = k[k.EMD_CD.str.startswith("27")]
print(len(k), k.EMD_CD.str.len().value_counts().to_dict(), k.EMD_CD.nunique())
print(k.BS_YR_QT.value_counts().sort_index().tail(6).to_string())
print(k.RES_COM_CD.value_counts().to_string())
print(k.AGE_CD.value_counts().to_string())
```
**확인**: `KENC`는 F1에서 읽힌 인코딩. 열 이름이 `BS_YR_QT RES_COM_CD EMD_CD SEX_CD AGE_CD C1_CNT … C22_CNT`인지 본다(정의서 기준). 다르면 아래 셀의 이름을 고친다. 대구 행정동 수는 **약 140~160개**(군위군 포함 여부에 따라). `EMD_CD` 길이(8 또는 10)와 **마지막 분기 값**을 받아 적는다.

### 셀 K2 — 행정동 × 연령대 소득 구간 저장 (11줄)

```python
QT = "여기에_마지막_분기값"
RES = "1"
CC = [f"C{i}_CNT" for i in range(1, 23)]
kk = k[(k.BS_YR_QT == QT) & (k.RES_COM_CD == RES)].copy()
kk[CC] = kk[CC].apply(pd.to_numeric, errors="coerce").fillna(0)
kk["grp"] = np.where(kk.AGE_CD.isin(["30", "40"]), "3040", "기타")
kd = kk.groupby(["EMD_CD", "grp"])[CC].sum()
print(kd.shape, kd.index.get_level_values(0).nunique(), int(kd.values.sum()))
kd[kd < 5] = np.nan
kd.to_csv("EXPORT_v4_kcb_hdong_income.csv", encoding="utf-8-sig")
print(int(kd.isna().sum().sum()), "칸 억제 /", kd.size)
```
**확인**: `QT`는 K1의 마지막 분기(2023년 4분기), `RES`는 K1에서 "1"이 있으면 1(실거주지 기준). 30·40대를 따로 묶는 이유: **아이를 키우는 부모 세대의 소득**이 필요도에 더 가깝다.
**KCB004가 작업공간에 없으면**: 센터 보유 `읍면동소득신용통계정보`를 F1처럼 열어 열 이름을 받아 적고, 반출은 하지 않는다(현장에서 셀을 새로 짜면 오타 위험이 크다). 다음 방문이 없으므로 기획서에는 "연계 설계"로만 쓴다.

---

## 5. 3순위 — 집 동 → 가게 동 흐름 (Q3, 40분)

> **아이디어**: 배달 주소는 자료에 없다. 대신 **일반 배달을 주로 어느 동 가게에서 시키는지**로 그 계정의 집 동을 추정하고, 그 계정의 급식카드 결제가 **어느 동 가게로 가는지** 센다. 확인표 이유 7("옆 동네 가게에서 산다")을 직접 확인하고, MCLP의 커버 범위(급식 주문이 얼마나 먼 동까지 가는가)를 데이터로 정한다.

### 셀 Q3a — 계정 × 동 일반 결제 수 (12줄, 1~2분)

```python
gc = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_CUST, C_GBN, C_STAT, C_TIME], dtype=str,
                      encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    ch = ch[(ch[C_STAT] == DONE) & (ch.ym >= "202306") & (ch.ym <= "202506")]
    ch = ch[~ch[C_GBN].isin(MEAL)]
    ch["dong"] = ch[C_SHOP].map(d2)
    gc.append(ch.groupby([C_CUST, "dong"]).size())
gcnt = pd.concat(gc).groupby(level=[0, 1]).sum()
print(len(gcnt), int(gcnt.sum()))
```
**확인**: 둘째 수 **3,612,950**.

### 셀 Q3b — 집 동 추정 (8줄)

```python
g2 = gcnt.rename("k").reset_index()
g2["tot"] = g2.groupby(C_CUST).k.transform("sum")
top = g2.sort_values("k").groupby(C_CUST).tail(1)
top = top[(top.tot >= 3) & (top.k / top.tot >= 0.5)]
home = top.set_index(C_CUST).dong
mc = pd.Series(m[C_CUST].unique())
print("집 동 추정 계정", len(home), "| 급식 계정", len(mc), "| 그중 추정 가능", int(mc.isin(home.index).sum()))
```
**확인**: 집 동 추정 기준 = 일반 결제 3건 이상, 가장 많이 쓴 동의 비중 50% 이상. **급식 계정 중 추정 가능 비율**을 받아 적는다. 30% 미만이면 Q3c는 하되 메모에 "대표성 낮음"을 적는다.

### 셀 Q3c — 흐름표 저장 (9줄)

```python
f = m.assign(home=m[C_CUST].map(home)).dropna(subset=["home"])
print(len(f), "건 /", len(m), "| 집 동 = 가게 동 비율", round((f.home == f.dong).mean(), 3))
print("방학만:", round((f[f.R == "방학"].home == f[f.R == "방학"].dong).mean(), 3))
fl = f.groupby(["home", "dong"]).agg(n=(C_SHOP, "size"), n_cust=(C_CUST, "nunique"))
bad = (fl.n < 5) | (fl.n_cust < 5)
print("쌍", len(fl), "| 억제", int(bad.sum()))
fl[bad] = np.nan
fl.to_csv("EXPORT_v4_meal_flow_home_shop.csv", encoding="utf-8-sig")
```
**확인**: "집 동 = 가게 동 비율"을 받아 적는다. **8번째 줄 전에 7번째 줄(`fl[bad] = np.nan`)이 있는지** 인쇄본과 대조한다.

---

## 5-2. 3-2순위 — 방학 앞·뒤 반기 (Q8, 10분) · 10/15 추가

> **왜**: 1순위는 25개월 방학 6개월을 합친 값이다. 심사에서 "한 시기의 우연 아닌가"를 물으면 답할 자료가 없다. 방학 6개월을 앞 3개월과 뒤 3개월로 나눠 두 시기 모두 낮은지 본다(밖에서 반기별 LQ·순위 상관 계산). 결제 파일을 한 번 더 읽는다(1~2분).

### 셀 Q8 — 동 × 반기 × 급식/일반 건수 (13줄, 1~2분)

```python
VH = {"202308": "앞", "202401": "앞", "202402": "앞", "202408": "뒤", "202501": "뒤", "202502": "뒤"}
hh = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_GBN, C_STAT, C_TIME], dtype=str, encoding=ENC,
                      chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch = ch.assign(H=ch[C_TIME].str[:6].map(VH), K=np.where(ch[C_GBN].isin(MEAL), "meal", "gen"))
    ch = ch[(ch[C_STAT] == DONE) & ch.H.notna()]
    hh.append(ch.groupby([ch[C_SHOP].map(d2), "H", "K"]).size())
hv = pd.concat(hh).groupby(level=[0, 1, 2]).sum().unstack([1, 2], fill_value=0)
hv.columns = [f"{h}_{k}" for h, k in hv.columns]
hv.index.name = "dong"
print(hv.shape, hv.sum().to_string())
print("방학 급식 합:", int(hv["앞_meal"].sum() + hv["뒤_meal"].sum()), "/ M2 방학:", int((m.R == "방학").sum()))
```
**확인**: 방학 급식 합 = M2 방학 = **188725**(3차 레짐 파일 방학 합과 같음). 앞·뒤 일반 합은 Q4의 방학 합과 같아야 한다.

### 셀 Q8b — 저장 (4줄)

```python
hv[hv < 5] = np.nan
hv.loc[hv.isna().any(axis=1)] = np.nan
hv.to_csv("EXPORT_v4_dong_vac_half.csv", encoding="utf-8-sig")
print(int(hv.isna().any(axis=1).sum()), "동 억제 /", len(hv))
```
**확인**: 2번째 줄(한 칸이라도 억제되면 그 동 전체 억제)을 빠뜨리지 않는다. 반기 합이 3차 방학 합과 Q4b 방학 일반과 같으므로, 한 반기만 비면 다른 반기가 역산된다.

---

## 6. 4순위 — 동별 배달 결과 (Q7, 20분) · 10/15 올림

> **왜**: 신한 배달매출이 이번 제공 목록에 없다. 이유 5(배달 여건)는 대구로 배달 정보로 본다: 가게 동별 배달 취소율, 배차→완료 시간, 배달팁. 배달 파일에는 결제수단이 없어 급식·일반을 나누지 못한다 — 동 전체의 배달 여건으로 쓴다.

### 셀 Q7 — 가게 동별 배달 취소·소요 시간·배달팁 (12줄, 1~3분)

```python
dl = []
for ch in pd.read_csv(DELI, usecols=["SHOP_ID", "DELI_ALLOC_TIME", "DELI_COMP_TIME", "DELI_CANCEL_TIME", "DELI_TIP_AMT"],
                      dtype=str, encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch = ch[(ch.DELI_ALLOC_TIME.str[:6] >= "202306") & (ch.DELI_ALLOC_TIME.str[:6] <= "202506")]
    t0 = pd.to_datetime(ch.DELI_ALLOC_TIME, format="%Y%m%d%H%M", errors="coerce")
    t1 = pd.to_datetime(ch.DELI_COMP_TIME, format="%Y%m%d%H%M", errors="coerce")
    ch = ch.assign(dong=ch.SHOP_ID.map(d2), cancel=ch.DELI_CANCEL_TIME != "", mins=(t1 - t0).dt.total_seconds() / 60,
                   tip=pd.to_numeric(ch.DELI_TIP_AMT, errors="coerce"))
    dl.append(ch.groupby("dong").agg(n=("cancel", "size"), n_cancel=("cancel", "sum"), mins_sum=("mins", "sum"),
                                     mins_n=("mins", "count"), tip_sum=("tip", "sum"), tip_n=("tip", "count")))
print(len(dl), "덩어리")
```
**확인**: 덩어리 수가 1 이상(파일 크기 ÷ 약 35MB). 배달 파일 경로 `DELI`는 F1에서 정했다.

### 셀 Q7b — 저장 (5줄)

```python
dg = pd.concat(dl).groupby(level=0).sum()
print(dg.shape, int(dg.n.sum()), round(dg.n_cancel.sum() / dg.n.sum(), 4), round(dg.tip_sum.sum() / dg.tip_n.sum()))
dg[dg.n < 5] = np.nan
dg.to_csv("EXPORT_v4_dong_delivery.csv", encoding="utf-8-sig")
print(int(dg.n.isna().sum()), "동 억제 /", len(dg))
```
**확인**: 배달 건수 합이 수백만 건 수준, 대구 전체 취소율과 평균 배달팁을 받아 적는다. 3번째 줄(건수 5 미만 동은 행 전체 가림)을 빠뜨리지 않는다.
---

## 7. 5순위 — 하루 결제 합 (Q5, 30분)

### 셀 Q5 — 급식 결제 금액 읽기 (13줄, 1~2분)

```python
ar = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_CUST, C_GBN, C_STAT, C_TIME, C_APP], dtype=str,
                      encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ar.append(ch[(ch[C_STAT] == DONE) & ch[C_GBN].isin(MEAL)])
a = pd.concat(ar)
a["ym"], a["day"] = a[C_TIME].str[:6], a[C_TIME].str[:8]
a = a[(a.ym >= "202306") & (a.ym <= "202506")]
a["app"] = pd.to_numeric(a[C_APP], errors="coerce").fillna(0)
a["gu"] = a[C_SHOP].map(sh.set_index("SHOP_ID").GUNGU_NM)
print(len(a), int(a.app.sum()))
```
**확인**: `341216`.

### 셀 Q5b — 계정·하루 합계 분포 저장 (12줄)

```python
dd = a.groupby([C_CUST, "day"]).agg(app=("app", "sum"), k=("app", "size"), gu=("gu", "first")).reset_index()
dd["yr"] = dd.day.str[:4]
dd["dal"] = np.where(dd.gu == "달성군", "달성군", "그외")
dd["bin"] = dd.app // 1000 * 1000
print(len(dd), dd.k.value_counts().head(4).to_dict())
print(dd.groupby(["yr", "dal"]).app.apply(lambda s: round((s > 24000).mean(), 4)).to_string())
h = dd.groupby(["yr", "dal", "bin"]).agg(n=("app", "size"), n_cust=(C_CUST, "nunique"))
bad = (h.n < 5) | (h.n_cust < 5)
h[bad] = np.nan
h.to_csv("EXPORT_v4_daily_app_hist.csv", encoding="utf-8-sig")
print(len(h), "칸 /", int(bad.sum()), "억제")
```
**확인**: 하루 결제 횟수 분포(1회·2회·3회…)와 **하루 합이 24,000원을 넘는 비율**(연도 × 달성군/그외)을 받아 적는다. 달성군은 2024-01부터 한도 27,000원이므로 2024·2025년에 24,000원 초과 비율이 그외보다 높으면 단가 인상 효과다 `[INFERRED]`.
**하지 않는 것**: 최댓값·99% 분위수는 출력하지 않는다(노트북째 반출된다).

### 셀 Q5c — 계정별 방학 하루 최대 결제 × 구 (8줄) · 10/15 추가

```python
v = dd[dd.day.str[4:6].isin(["01", "02", "08"])]
mx = v.groupby(C_CUST).agg(mx=("app", "max"), gu=("gu", lambda s: s.value_counts().index[0]))
mx["b"] = pd.cut(mx.mx, [-1, 8000, 9000, 10000, 16000, 18000, 20000, 24000, 27000, 30000, 1e12],
                 labels=["~8천", "~9천", "~1만", "~1.6만", "~1.8만", "~2만", "~2.4만", "~2.7만", "~3만", "3만~"])
t5 = mx.groupby(["gu", "b"], observed=False).size().unstack(fill_value=0)
print(len(mx), t5.sum().to_string())
t5[t5 < 5] = np.nan
t5.to_csv("EXPORT_v4_acct_vac_maxday_gu.csv", encoding="utf-8-sig")
```
**확인**: 첫 수(방학에 결제한 계정 수)와 구간별 합을 받아 적는다. 구는 그 계정이 가장 많이 결제한 가게의 구다. 계정 단위라 최댓값 자체는 출력하지 않는다.
**왜**: 결제는 하루 한도(신청 끼니 수 × 단가)로만 막힌다(동구청 확인). 계정이 방학 내내 하루 최대 결제가 1끼 단가 이하라면 1끼만 신청했을 가능성이 크다. 구별 비중은 이유 6(신청 끼니)과 이유 4(1끼 한도로는 최소주문금액을 못 맞춤)의 근거가 된다.

### 셀 Q9 — 1순위 17곳 목록 손으로 입력 (5줄) · 10/15 추가

```python
T17 = ["달성군|구지면 화산리", "달성군|논공읍 금포리", "달성군|다사읍 매곡리", "달성군|다사읍 서재리",
       "달성군|다사읍 죽곡리", "달성군|옥포읍 본리리", "달성군|화원읍 명곡리", "달성군|화원읍 본리리",
       "달성군|화원읍 설화리", "동구|지묘동", "북구|검단동", "북구|칠성동2가", "북구|침산동",
       "북구|학정동", "서구|원대동1가", "서구|이현동", "수성구|노변동"]
print(len(T17), "오타(가맹점 동 키에 없음):", sorted(set(T17) - set(sh.dong)))
```
**확인**: `17 오타(가맹점 동 키에 없음): []`. 빈 목록이 아니면 찍힌 이름을 인쇄본과 대조해 고친다(띄어쓰기, `|` 앞뒤 공백 없음).

### 셀 Q9b — 1순위 대 나머지: 하루 최대 결제 구간·시간대 (11줄)

```python
mv = m[m.R == "방학"]
md = mv.groupby(C_CUST).dong.agg(lambda s: s.value_counts().index[0])
mx["g"] = np.where(md.reindex(mx.index).isin(T17), "1순위", "나머지")
g9 = mx.groupby(["g", "b"], observed=False).size().unstack(fill_value=0)
h9 = mv.assign(g=np.where(mv.dong.isin(T17), "1순위", "나머지"), hr=mv[C_TIME].str[8:10])
h9 = h9.groupby(["g", "hr"]).size().unstack(fill_value=0)
print(g9.to_string(), "\n", h9.to_string())
for t, f in [(g9, "EXPORT_v4_top_vac_maxday.csv"), (h9, "EXPORT_v4_top_vac_hour.csv")]:
    t = t.astype(float)
    t.loc[:, (t < 5).any()] = np.nan
    t.to_csv(f, encoding="utf-8-sig")
```
**확인**: `g9` 두 줄의 합 = Q5c 첫 수(방학 결제 계정). 계정의 그룹은 방학 급식 결제를 가장 많이 한 가게의 동으로 정한다.
**억제**: 한 열에서 한 칸이라도 5 미만이면 그 열을 두 줄 모두 지운다(10번째 줄). 대구 전체에서 빼서 역산되는 것을 막기 위해서다.
**왜**: 판정 R6(안내·신청)은 동별 자료가 없다. 1순위 17곳 아이들이 나머지보다 "방학 내내 1끼 한도(1만 원) 안에서만 쓰는" 비율이 높은지, 점심·저녁 중 어디가 빠지는지를 **1순위 묶음 단위**로 직접 본다. 반출 후 1순위가 바뀌어도(D-016 분모 교체) 지금 17곳 기준의 결과로 쓰고 그 사실을 적는다.

---

## 8. 선택 — 급식 계정 명의자 연령대 (Q10, 시간이 남을 때만) · 10/15 추가

### 셀 Q10 — 1순위 대 나머지 × 명의자 연령대 (7줄)

```python
cu = pd.read_csv(CUST, usecols=["CUST_ID", "BR_DT"], dtype=str, encoding=ENC, keep_default_na=False)
cu = cu.apply(lambda s: s.str.strip()).drop_duplicates("CUST_ID").set_index("CUST_ID").BR_DT
ag = cu.reindex(md.index).replace("", "없음").fillna("없음")
g10 = pd.crosstab(np.where(md.isin(T17), "1순위", "나머지"), ag.values).astype(float)
print(len(md), g10.to_string())
g10.loc[:, (g10 < 5).any()] = np.nan
g10.to_csv("EXPORT_v4_top_vac_custage.csv", encoding="utf-8-sig")
```
**확인**: 첫 수 = 방학 급식 계정 수(Q9b의 `md`), 연령대 열은 10·20·…·80과 "없음". Q9b를 먼저 실행해야 한다(`md`, `T17` 사용).
**억제**: 한 열에 5 미만이 있으면 그 열을 두 줄 모두 지운다(6번째 줄).
**왜**: 계정 명의자 연령대(정의서: 계정 명의자 기준)로 누가 앱을 쓰는지 본다. 30·40대가 대부분이면 보호자가 주문하는 것이고, 안내(이유 6) 처방의 대상은 보호자다. 1순위가 나머지와 다르면 표적 안내의 근거가 된다.
---

## 9. 반출 전 자동 점검과 메모 (30분)

### 셀 X1 — 저장한 파일을 다시 읽어 억제 확인 (13줄) · **반출 신청 전에 반드시**

```python
CHK = {"dong_regime_general": (["방학", "전환", "학기"], 5),
       "dong_shop_state": (["able_live", "meal_vac_shop", "meal_vac_live", "meal_vac10_live", "u2_live", "nonY_live"], 3),
       "kcb_hdong_income": ([f"C{i}_CNT" for i in range(1, 23)], 5),
       "meal_flow_home_shop": (["n", "n_cust"], 5), "daily_app_hist": (["n", "n_cust"], 5),
       "dong_vac_half": (["앞_meal", "앞_gen", "뒤_meal", "뒤_gen"], 5),
       "acct_vac_maxday": (["~8천", "~9천", "~1만", "~1.6만", "~1.8만", "~2만", "~2.4만", "~2.7만", "~3만", "3만~"], 5),
       "top_vac_maxday": (None, 5), "top_vac_hour": (None, 5), "top_vac_custage": (None, 5),
       "dong_delivery": (["n"], 5)}
for f in sorted(glob.glob("EXPORT_v4_*.csv")):
    e = pd.read_csv(f, encoding="utf-8-sig")
    cols, lim = [v for key, v in CHK.items() if key in f][0]
    low = int((e[cols or list(e.columns[1:])] < lim).sum().sum())
    print("통과" if low == 0 else "※ 억제 누락", low, f, e.shape)
```
**판정**: 모든 줄이 **"통과"**여야 한다. "※ 억제 누락"이 찍힌 파일은 해당 저장 셀을 다시 실행하고 X1을 다시 돌린다. 그래도 안 되면 그 파일은 반출 신청하지 않는다. (Q7·Q10을 건너뛰어 파일이 없으면 그 줄은 찍히지 않는다.)

### 셀 X2 — 정의 메모 저장 (12줄) · 밑줄 칸은 현장에서 채운다

```python
memo = """T2 4차 반출 메모 (2026-10-__)
급식 정의: PAY_GBN=아동급식카드, CARD_PAY_GBN=완료, 중복 제거 안 함. 기간 2023-06~2025-06(25개월).
레짐: 방학 1·2·8월 / 전환 7·12월 / 학기 나머지. 동 키: 가맹점 GUNGU_NM|DONG_NM(법정동).
억제: 결제 건수<5, 고객<5, 가맹점<3은 빈칸. 동x레짐 일반 결제는 한 칸이라도 억제되면 그 동 전체 억제.
가게 상태: 영업 = STORE_STATUS 01 그리고 SERVICE_CLOSED N (현재 스냅샷).
집 동 추정: 비급식 완료 결제 3건 이상, 최다 동 비중 0.5 이상. 급식 계정 중 추정 가능 ___%.
KCB: 파일 ___, BS_YR_QT=___, RES_COM_CD=1, 30·40대와 기타로 합산. EMD_CD 길이 ___.
배달: 파일 ___, 동별 취소·소요시간·배달팁 합, 건수<5 동 억제. Q10 계정 명의자 연령대(선택). Q8 방학 앞(2023-08·2024-01·02)/뒤(2024-08·2025-01·02), Q5c 계정별 방학 하루 최대 승인액 × 최다 결제 구. Q9 1순위 17곳(D-017) 대 나머지.
X1 결과: 전 파일 통과 / 예외 ___.
"""
open("filter_definition_v4.txt", "w", encoding="utf-8").write(memo)
```

### 반출 패키지

| 파일 | 내용 | 억제 |
|---|---|---|
| `EXPORT_v4_dong_regime_general.csv` | 동 × 레짐 일반 결제 | <5, 한 칸 억제 시 동 전체 |
| `EXPORT_v4_dong_shop_state.csv` | 동별 영업 중 등록 가게, 방학 급식 가게, 확인표 대상 가게 | <3 |
| `EXPORT_v4_kcb_hdong_income.csv` | 행정동 × (30·40대/기타) × 월소득 22구간 인원 | <5 |
| `EXPORT_v4_meal_flow_home_shop.csv` | 추정 집 동 × 가게 동 급식 결제 | 건수<5, 계정<5 |
| `EXPORT_v4_daily_app_hist.csv` | 연도 × 달성군/그외 × 계정·하루 승인액 1천 원 구간 | 건수<5, 계정<5 |
| `EXPORT_v4_dong_vac_half.csv` (10/15) | 동 × 방학 앞·뒤 반기 × 급식/일반 건수 | <5, 한 칸 억제 시 동 전체 |
| `EXPORT_v4_top_vac_maxday.csv`, `EXPORT_v4_top_vac_hour.csv` (10/15) | 1순위 17곳 대 나머지 × 계정 하루 최대 결제 구간 / 방학 급식 결제 시간대 | 열에 5 미만이 있으면 그 열 전체 |
| `EXPORT_v4_acct_vac_maxday_gu.csv` (10/15) | 구 × 계정별 방학 하루 최대 승인액 구간(단가 8천·9천·1만 원 × 1·2·3끼 한도 경계) 계정 수 | <5 |
| `EXPORT_v4_dong_delivery.csv` (4순위) | 가게 동별 배달 건수·취소·소요 시간·배달팁 합 | 건수<5면 행 전체 |
| `EXPORT_v4_top_vac_custage.csv` (선택) | 1순위 대 나머지 × 급식 계정 명의자 연령대 | 열에 5 미만이 있으면 그 열 전체 |
| `filter_definition_v4.txt` | 정의·억제·현장 확인값 | — |
| 노트북 | 반출 시 함께 나간다. 최댓값·상위 분위수·개별 계정 출력이 없는지 눈으로 확인 | — |

---

## 10. 축소 경로

| 남은 시간 | 버리는 것 | 지키는 것 |
|---|---|---|
| 3시간 | Q10 | Q4·Q1, Q2, Q3, Q8, Q7, Q5(+Q5c·Q9) |
| 2시간 | Q5, Q7, Q10 | **Q4·Q1, Q2, Q3, Q8** |
| 1시간 | Q3 | **Q4·Q1, Q2** |
| 30분 | 전부 | **Q2(KCB)만** — M1·M2 없이 돌아가고, 상호제공 연계 가점이 걸려 있다 |

모든 경우 X1·X2는 한다.

---

## 11. 셀별 기대 확인값 (인쇄용 요약)

| 셀 | 기대값 | 현장 값 |
|---|---|---|
| S1 | 결제 15열, 가맹점 8열 (3차와 같음) | |
| F0 | KCB·배달·고객 파일 경로와 크기 | |
| M1 | `22086 205` | |
| M2 | `341216 / 0 / 189` | |
| Q4 | `3612950 3612950`, 레짐별 합 ___ | |
| Q4b | 행 ≤ 205, 합 3,612,950, 억제 동 ___ | |
| Q1 | `u2_live` **631**, able_live ___, meal_vac_shop ___ | |
| Q1b | 억제 칸 ___ (nonY_live 포함) | |
| K1 | 대구 행정동 140~160개, EMD_CD 길이 ___, 마지막 분기 ___ | |
| K2 | 행정동 수 = K1과 같음, 인원 합 ___ | |
| Q3a | 둘째 수 3,612,950 | |
| Q3b | 급식 계정 중 추정 가능 ___ / ___ | |
| Q3c | 집 동 = 가게 동 비율 ___ (방학 ___) | |
| Q8 | 방학 급식 합 **188725** = M2 방학, 앞·뒤 일반 합 = Q4 방학 | |
| Q8b | 억제 동 ___ / ___ | |
| Q7b | 배달 건수 수백만, 취소율 ___, 평균 배달팁 ___ | |
| Q5 | `341216` | |
| Q5b | 하루 결제 횟수 분포 ___, 24,000원 초과 비율 ___ | |
| Q5c | 방학 결제 계정 ___, 구간별 합 ___ | |
| Q9 | `17 오타(가맹점 동 키에 없음): []` | |
| Q9b | g9 합 = Q5c 첫 수, 1순위 1만 원 이하 비율 ___ / 나머지 ___ | |
| Q10 | 연령대 분포(1순위 / 나머지) ___ | |
| X1 | 전부 "통과" | |

---

## 12. 방문 직후 (반출 대기 3일 동안 밖에서)

1. MCLP 골격을 지금 있는 자료(아동 수, 경계 거리)로 먼저 짠다. 반출이 오면 공급(Q1 `meal_vac_live`)·수요(KCB 보정)·커버 범위(Q3 흐름)를 갈아 끼운다.
2. 반출물 도착 시 `T2_export_10xx_results.md` 작성, 판정표(1순위 × 이유 7개)를 [T2_reason_rules.md](T2_reason_rules.md)(D-019) 규칙대로 채우기. 규칙은 반출물을 보기 전에 고정했으므로 바꾸지 않는다. 실행은 `python -X utf8 analysis/outside/90_reason_table.py --v4 <반출 폴더> --app <앱 점검.csv>`(§8).
3. 기획서 30쪽 작성(W4~W5).

## Status
- 2026-10-15 밤 **4차 제공 목록 확정**(대구로 6종 + KCB, 신한 없음): Q6(S6·S6b) 삭제, Q7을 4순위로 올리고 배달팁 열 추가(Q7b 분리), F1을 KCB·배달·고객으로, Q10(계정 명의자 연령대, 선택) 추가, X1·X2·패키지·축소·기대값 갱신. 판정 R5a는 대구로 일반 배달 결제 ÷ 인구로 대신(D-019 개정).
- 2026-10-15 Q9(1순위 17곳 목록 손입력 → 1순위 대 나머지 하루 최대 결제·시간대) 추가. R4 단가 1만 원(대구광역시청 복지과, 대구 공통) 반영해 Q5c 구간에 1만·2만·3만 경계 추가.
- 2026-10-15 **추가 3개**(방문 전날): Q1b `nonY_live`(MCLP 모집 상한), Q8 방학 앞·뒤 반기(1순위 재현성), Q5c 계정별 방학 하루 최대 결제 × 구(이유 4·6). X1·X2·반출 패키지·축소 경로·기대값 갱신. SYNTHETIC 재점검은 아래 줄.
- 2026-10-12 작성. 방문일 미확정(10/14 또는 10/15). 방문 전 준비 A~E 미완. 셀은 손타이핑용으로 13줄 이하, 모든 저장 셀에 억제 줄, 반출 전 자동 점검 X1 추가.
- 2026-10-12 Q1에 `meal_vac10_live`(방학 급식 10건 이상·영업 중) 추가 — MCLP 골격이 느슨한 공급 정의(1건 이상)에서 포화돼 엄격한 공급이 필요해졌다. SYNTHETIC 재점검 통과.
- 2026-10-12 SYNTHETIC 점검: 가짜 결제·가맹점·KCB·신한·배달 파일로 S1~X2 전 셀을 순서대로 실행해 오류 없음. X1이 억제 누락 파일을 "※ 억제 누락"으로 잡는 것도 확인. 실데이터 결과가 아니다. KCB·신한 열 이름은 정의서 기준 가정이라 현장 F1에서 확인해야 한다.
