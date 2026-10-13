# T2 4차 방문 실행 계획 (2026-10-14 또는 10-15, 팀 확정)

> **작성**: 2026-10-12 / **근거**: 3차 반출 결과 [T2_export_1002_results.md](T2_export_1002_results.md) §6, 결정 [D-015~D-017](../DECISIONS.md)
> **전제**: 코드 반입 불가. 셀은 현장에서 손으로 친다. 셀마다 13줄 이하, 확인 출력을 둔다(3차와 같은 형식).
> **성격**: **마지막 분석 방문.** 반출 심사(약 3일)를 거쳐 10/17~18에 받아야 기획서(마감 10/22 18:00)에 들어간다.
> **3차의 교훈**: M4 셀에서 억제 한 줄(`tt[bad] = np.nan`)이 빠진 채 반출됐다. 이번에는 **모든 저장 셀에 억제 줄을 두고, 반출 전에 셀 X1이 파일을 다시 읽어 자동 점검**한다. X1이 "통과"를 찍지 않은 파일은 반출 신청하지 않는다.
> **총 예상**: 약 4시간 + 반출 신청 30분. 순서를 바꾸지 않는다.

---

## 0. 오늘 얻을 것

| 순위 | 셀 | 질문 | 어디에 쓰나 | 시간 |
|---|---|---|---|---|
| 1 | **Q4·Q1** 동별 가게 상태 | 동마다 등록 가게 중 실제 영업 중인 곳, 방학에 급식 주문을 받은 가게는 몇 곳인가 | 확인표(이유 3), **MCLP 공급** | 25분 |
| 2 | **Q2** KCB 소득 | 행정동별 30·40대 저소득 비율은 어떤가 | 필요도(이유 1), **상호제공 연계 가점** | 40분 |
| 3 | **Q3** 집 동 → 가게 동 흐름 | 아이들은 자기 동네 가게에서 주문하는가, 옆 동네로 가는가 | 확인표(이유 7), **MCLP 커버 범위** | 40분 |
| 4 | **Q6** 신한 배달매출 | 동별 전체 배달 시장에서 대구로 비중은 어느 정도인가 | 확인표(이유 5), 기관 간 연계 | 40분 |
| 5 | **Q5** 하루 결제 합 | 하루 한도(끼니 수 × 단가)가 실제 결제를 막는가 | 확인표(이유 4), H5 | 30분 |
| 6 | Q7 배달 결과 (선택) | 동별 배달 취소율·배달 시간 | 확인표(이유 5) | 시간 남을 때 |
| — | **X1·메모·반출** | 억제 자동 점검, 정의 메모 | 반출 | 30분 |

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
| E | KCB·신한 파일이 **신청한 31종에 들어 있어 작업공간에서 열리는지** 센터에 문의 | Q2·Q6 전제 | 운영 |

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
**확인**: KCB 파일(`TB_KCB_INCOME_STAT_DATASET.csv`, 약 98MB, 이름에 KCB·INCOME), 신한 배달매출 파일(이름에 SHC 또는 배달·DELIVERY), 대구로 배달 파일(`DELI`)의 **경로와 크기를 받아 적는다.**

### 셀 F1 — KCB·신한 첫 줄 보기 (10줄)

```python
KCB = r"여기에_KCB_경로.csv"
SHD = r"여기에_신한_배달매출_경로.csv"
for f in [KCB, SHD]:
    for enc in ["utf-8", "utf-8-sig", "cp949"]:
        try:
            print(f, enc)
            print(pd.read_csv(f, nrows=3, dtype=str, encoding=enc).to_string())
            break
        except UnicodeDecodeError:
            pass
```
**확인**: 각 파일이 어떤 인코딩에서 읽혔는지, **열 이름 전체**를 받아 적는다. 신한 파일은 지역코드 열(법정동 10자리), 연월 열, 건수 열, 금액 열 이름을 찾아 Q6 상수에 쓴다. 신한 파일이 **20GB를 넘으면 Q6은 건너뛴다**(읽기만 30분 이상).

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
qd[qd < 3] = np.nan
qd.to_csv("EXPORT_v4_dong_shop_state.csv", encoding="utf-8-sig")
print(int(qd.isna().sum().sum()), "칸 억제 /", qd.size)
```
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

## 6. 4순위 — 신한 배달매출 (Q6, 40분) · F1에서 20GB 초과면 건너뜀

### 셀 S6 — 대구 × 법정동 × 월 합계 (13줄, 파일 크기에 따라 5~20분)

```python
SENC = "utf-8"
S_YM, S_REG, S_CNT, S_AMT = "STD_YM", "UMD_CD", "여기에_건수열", "여기에_금액열"
sd = []
for ch in pd.read_csv(SHD, usecols=[S_YM, S_REG, S_CNT, S_AMT], dtype=str, encoding=SENC,
                      chunksize=2000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ym = ch[S_YM].str[:6]
    ch = ch[ch[S_REG].str.startswith("27") & (ym >= "202306") & (ym <= "202506")]
    ch[[S_CNT, S_AMT]] = ch[[S_CNT, S_AMT]].apply(pd.to_numeric, errors="coerce").fillna(0)
    sd.append(ch.groupby([S_REG, ch[S_YM].str[:6]])[[S_CNT, S_AMT]].sum())
s6 = pd.concat(sd).groupby(level=[0, 1]).sum()
print(s6.shape, s6.index.get_level_values(0).nunique(), s6.sum().to_string())
```
**확인**: 상수 4개는 F1에서 본 열 이름으로 고친다(연월·지역코드 이름도 다를 수 있다). 법정동 수는 **200개 안팎**, 월 수는 데이터 기간에 따라 최대 25. 지역코드가 법정동 10자리가 아니면(시군구 단위 등) 받아 적고 그대로 저장한다.

### 셀 S6b — 저장 (4줄)

```python
s6.index.names = ["umd_cd", "ym"]
s6[s6[S_CNT] < 5] = np.nan
s6.to_csv("EXPORT_v4_shinhan_delivery_umd_month.csv", encoding="utf-8-sig")
print(int(s6[S_CNT].isna().sum()), "칸 억제 /", len(s6))
```
**쓰는 곳**: 밖에서 "동별 대구로 일반 결제 ÷ 신한 배달 결제" = 대구로 점유율. 점유율이 낮은 동은 급식카드로 시킬 대구로 가게 자체가 적다(이유 5).

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

---

## 8. 선택 — 동별 배달 결과 (Q7, 시간이 남을 때만)

### 셀 Q7 — 가게 동별 배달 취소·소요 시간 (13줄)

```python
DELI = r"여기에_대구로_배달_경로.csv"
dl = []
for ch in pd.read_csv(DELI, usecols=["SHOP_ID", "DELI_ALLOC_TIME", "DELI_COMP_TIME", "DELI_CANCEL_TIME"],
                      dtype=str, encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch = ch[(ch.DELI_ALLOC_TIME.str[:6] >= "202306") & (ch.DELI_ALLOC_TIME.str[:6] <= "202506")]
    t0 = pd.to_datetime(ch.DELI_ALLOC_TIME, format="%Y%m%d%H%M", errors="coerce")
    t1 = pd.to_datetime(ch.DELI_COMP_TIME, format="%Y%m%d%H%M", errors="coerce")
    ch = ch.assign(dong=ch.SHOP_ID.map(d2), cancel=ch.DELI_CANCEL_TIME != "", mins=(t1 - t0).dt.total_seconds() / 60)
    dl.append(ch.groupby("dong").agg(n=("cancel", "size"), n_cancel=("cancel", "sum"), mins_sum=("mins", "sum"), mins_n=("mins", "count")))
dg = pd.concat(dl).groupby(level=0).sum()
dg[dg.n < 5] = np.nan
dg.to_csv("EXPORT_v4_dong_delivery.csv", encoding="utf-8-sig")
```
**확인**: `dg.n.sum()`이 수백만 건 수준인지만 본다. 배달 결과는 급식·일반을 구분하지 못한다(배달 파일에 결제수단이 없다) — 동 전체의 배달 여건으로만 쓴다.

---

## 9. 반출 전 자동 점검과 메모 (30분)

### 셀 X1 — 저장한 파일을 다시 읽어 억제 확인 (12줄) · **반출 신청 전에 반드시**

```python
CHK = {"dong_regime_general": (["방학", "전환", "학기"], 5),
       "dong_shop_state": (["able_live", "meal_vac_shop", "meal_vac_live", "meal_vac10_live", "u2_live"], 3),
       "kcb_hdong_income": ([f"C{i}_CNT" for i in range(1, 23)], 5),
       "meal_flow_home_shop": (["n", "n_cust"], 5), "daily_app_hist": (["n", "n_cust"], 5),
       "shinhan_delivery": ([S_CNT], 5), "dong_delivery": (["n"], 5)}
for f in sorted(glob.glob("EXPORT_v4_*.csv")):
    e = pd.read_csv(f, encoding="utf-8-sig")
    cols, lim = [v for key, v in CHK.items() if key in f][0]
    low = int((e[cols] < lim).sum().sum())
    print("통과" if low == 0 else "※ 억제 누락", low, f, e.shape)
```
**판정**: 모든 줄이 **"통과"**여야 한다. "※ 억제 누락"이 찍힌 파일은 해당 저장 셀을 다시 실행하고 X1을 다시 돌린다. 그래도 안 되면 그 파일은 반출 신청하지 않는다. (`S_CNT`가 없다는 오류가 나면 Q6을 건너뛴 것이다 — 6번째 줄의 `[S_CNT]`를 `["x"]`로 바꾼다.)

### 셀 X2 — 정의 메모 저장 (12줄) · 밑줄 칸은 현장에서 채운다

```python
memo = """T2 4차 반출 메모 (2026-10-__)
급식 정의: PAY_GBN=아동급식카드, CARD_PAY_GBN=완료, 중복 제거 안 함. 기간 2023-06~2025-06(25개월).
레짐: 방학 1·2·8월 / 전환 7·12월 / 학기 나머지. 동 키: 가맹점 GUNGU_NM|DONG_NM(법정동).
억제: 결제 건수<5, 고객<5, 가맹점<3은 빈칸. 동x레짐 일반 결제는 한 칸이라도 억제되면 그 동 전체 억제.
가게 상태: 영업 = STORE_STATUS 01 그리고 SERVICE_CLOSED N (현재 스냅샷).
집 동 추정: 비급식 완료 결제 3건 이상, 최다 동 비중 0.5 이상. 급식 계정 중 추정 가능 ___%.
KCB: 파일 ___, BS_YR_QT=___, RES_COM_CD=1, 30·40대와 기타로 합산. EMD_CD 길이 ___.
신한: 파일 ___, 열 ___, 기간 ___. 건수<5 억제.
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
| `EXPORT_v4_shinhan_delivery_umd_month.csv` | 법정동 × 월 신한 배달 결제 건수·금액 | 건수<5 |
| `EXPORT_v4_daily_app_hist.csv` | 연도 × 달성군/그외 × 계정·하루 승인액 1천 원 구간 | 건수<5, 계정<5 |
| `EXPORT_v4_dong_delivery.csv` (선택) | 가게 동별 배달 건수·취소·소요 시간 합 | 건수<5 |
| `filter_definition_v4.txt` | 정의·억제·현장 확인값 | — |
| 노트북 | 반출 시 함께 나간다. 최댓값·상위 분위수·개별 계정 출력이 없는지 눈으로 확인 | — |

---

## 10. 축소 경로

| 남은 시간 | 버리는 것 | 지키는 것 |
|---|---|---|
| 3시간 | Q7 | Q4·Q1, Q2, Q3, Q6, Q5 |
| 2시간 | Q5, Q6 | **Q4·Q1, Q2, Q3** |
| 1시간 | Q3 | **Q4·Q1, Q2** |
| 30분 | 전부 | **Q2(KCB)만** — M1·M2 없이 돌아가고, 상호제공 연계 가점이 걸려 있다 |

모든 경우 X1·X2는 한다.

---

## 11. 셀별 기대 확인값 (인쇄용 요약)

| 셀 | 기대값 | 현장 값 |
|---|---|---|
| S1 | 결제 15열, 가맹점 8열 (3차와 같음) | |
| F0 | KCB·신한·배달 파일 경로와 크기 | |
| M1 | `22086 205` | |
| M2 | `341216 / 0 / 189` | |
| Q4 | `3612950 3612950`, 레짐별 합 ___ | |
| Q4b | 행 ≤ 205, 합 3,612,950, 억제 동 ___ | |
| Q1 | `u2_live` **631**, able_live ___, meal_vac_shop ___ | |
| K1 | 대구 행정동 140~160개, EMD_CD 길이 ___, 마지막 분기 ___ | |
| K2 | 행정동 수 = K1과 같음, 인원 합 ___ | |
| Q3a | 둘째 수 3,612,950 | |
| Q3b | 급식 계정 중 추정 가능 ___ / ___ | |
| Q3c | 집 동 = 가게 동 비율 ___ (방학 ___) | |
| S6 | 법정동 약 200개, 월 ≤ 25 | |
| Q5 | `341216` | |
| Q5b | 하루 결제 횟수 분포 ___, 24,000원 초과 비율 ___ | |
| X1 | 전부 "통과" | |

---

## 12. 방문 직후 (반출 대기 3일 동안 밖에서)

1. MCLP 골격을 지금 있는 자료(아동 수, 경계 거리)로 먼저 짠다. 반출이 오면 공급(Q1 `meal_vac_live`)·수요(KCB 보정)·커버 범위(Q3 흐름)를 갈아 끼운다.
2. 반출물 도착 시 `T2_export_10xx_results.md` 작성, 판정표(1순위 × 이유 7개)를 [T2_reason_rules.md](T2_reason_rules.md)(D-019) 규칙대로 채우기. 규칙은 반출물을 보기 전에 고정했으므로 바꾸지 않는다.
3. 기획서 30쪽 작성(W4~W5).

## Status
- 2026-10-12 작성. 방문일 미확정(10/14 또는 10/15). 방문 전 준비 A~E 미완. 셀은 손타이핑용으로 13줄 이하, 모든 저장 셀에 억제 줄, 반출 전 자동 점검 X1 추가.
- 2026-10-12 Q1에 `meal_vac10_live`(방학 급식 10건 이상·영업 중) 추가 — MCLP 골격이 느슨한 공급 정의(1건 이상)에서 포화돼 엄격한 공급이 필요해졌다. SYNTHETIC 재점검 통과.
- 2026-10-12 SYNTHETIC 점검: 가짜 결제·가맹점·KCB·신한·배달 파일로 S1~X2 전 셀을 순서대로 실행해 오류 없음. X1이 억제 누락 파일을 "※ 억제 누락"으로 잡는 것도 확인. 실데이터 결과가 아니다. KCB·신한 열 이름은 정의서 기준 가정이라 현장 F1에서 확인해야 한다.
