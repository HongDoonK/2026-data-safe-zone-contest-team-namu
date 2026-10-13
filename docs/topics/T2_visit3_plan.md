# T2 3차 방문 실행 계획 (2026-09-29 ~ 10-02)

> **작성**: 2026-09-28 / **근거**: 설계서 [§0.0-6](T2_child_meal_card.md), 2차 반출 결과 [T2_export_0918_results.md](T2_export_0918_results.md), 결정 [D-013·D-014](../DECISIONS.md)
> **전제**: **코드 반입 불가.** 모든 셀을 현장에서 손으로 친다. 2차 방문에서 오타로 세 번 막혔으므로 **셀을 10~13줄로 쪼개고 셀마다 확인 출력**을 둔다.
> **성격**: 3차는 **마지막 본 분석 방문**이다(마감 10-22). 여기서 못 얻으면 기획서에 못 쓴다.
> **총 예상**: 약 4시간 + 반출 신청. 순서를 바꾸지 않는다.

---

## 0. 오늘의 목표 세 개

| 순위 | 모듈 | 질문 | 산출 | 시간 |
|---|---|---|---|---|
| **1** | **P0 기간** | 2023-05 이전에도 급식 결제가 다른 코드로 기록됐는가? | 분석 기간 확정(D-014 규칙) | 30분 |
| **2** | **M4 공간** | 급식 이용·공급이 어느 법정동에서 끊기는가? | 동×레짐 표, 동 LQ, 확인표(U2) | 90분 |
| **3** | **H5 금액** | `CHILD_DISC_AMT`는 무엇이고 금액은 상한에 몰리는가? | 금액 항등식, 500원 히스토그램 | 60분 |
| 4 | H3 결합 | (선택) 결제-주문-배달 결합이 가능한가 | 결합 모호율만 | 시간 남을 때 |

**중단 규칙**: 14시(또는 남은 시간 90분)가 되면 진행 중인 모듈을 끊고 **반출 신청서 작성으로 넘어간다.** 심사가 3일 걸려 신청을 못 하면 그날 작업이 0이 된다.

---

## 1. 방문 전 (오늘 ~ 출발 전)

| # | 할 일 | 이유 | 담당 |
|---|---|---|---|
| A | **센터에 동 이름 반출 가능 여부 확인** | M4 산출물이 여기 걸려 있다. 불가하면 §4의 대체안(군구 + 동 번호)으로 간다 | 운영 |
| B | 대구시 급식카드 **이용시간 규정** 조사 | H1-심야의 "제도" 해석 근거. 규정을 못 찾으면 "23시 이후 관측 없음"까지만 쓴다 | 기획 |
| C | 아동급식 **단가와 적용 단위**(1식/1일/1회 주문) 공고 조사 | H5를 집군 분석으로 올릴 수 있는지의 조건(레드팀 C-6) | 기획 |
| D | 법정동 기준 **6~18세 인구** 확보 | M4 반출물이 오면 바로 붙인다 | 공간 |
| E | 이 문서 §3~§5 **인쇄** | 현장에서 화면 전환 없이 타이핑 | 전원 |

**2026-10-01 조사 결과 (B·C)** — 외부 공개자료, 사용자 조사. **출처(링크·공고명·날짜) 기록 전**
- **B 이용시간**: **06:00~23:00**, 당일 미사용 금액은 소멸. 2차 반출에서 확인한 "급식 결제만 23시에 끊김"(23~05시 25개월 11건, 06시부터 관측)과 맞는다. 기획서에서 "제도가 정한 경계"로 쓰려면 먼저 ① 출처를 기록하고 ② 데이터 기간(2023-06~2025-06)에도 같은 규정이었는지 확인한다.
- **C 단가·적용 단위**: 1식 **10,000원**, 하루 최대 **30,000원**(2026년 기준). 1식 10,000원은 [대구시 아동급식지원 안내](https://www.daegu.go.kr/woman/index.do?menu_id=00050143)(2026-03-06 수정)로 확인했다. 하루 한도의 출처는 아직 기록하지 못했다.
  - **2023년은 8,000원**이다(2022년 7,000원에서 인상). 출처는 [평화뉴스 2023-10-17](https://www.pn.or.kr/news/articleView.html?idxno=20653)이고, 강득구 의원실 국정감사 자료를 인용했다. 같은 기사에 따르면 보건복지부 권고단가도 2023년에 7,000원에서 8,000원으로 올랐다.
  - **2024·2025년 단가를 직접 밝힌 기사는 찾지 못했다**(2026-10-01 검색). [대구 동구청 결식아동 급식지원 안내](https://dong.daegu.kr/portal/contents.do?mid=0308010400)(최종 수정 2025-08-18)는 1식 8,000원이다. 따라서 **데이터 기간(2023-06~2025-06) 내내 8,000원이었을 가능성이 높다.** 다만 구청 안내문이라 단정하지는 않는다.
  - 그렇다면 기간 안에 단가 변경이 없다. 비교할 개정 시점이 없으므로 **A4는 해당 없음**이다. H5의 이벤트 스터디도 할 수 없고, 집군 진단은 고정 단가 8,000원 기준으로만 한다.
  - 하루 한도는 2026년의 30,000원만 안다(2023~2025년은 미확인).
- **대구로 급식 서비스 외부 자료 (2026-10-01 검색)**
  - **서비스 시작 2023-06-01.** 대구시가 대구로와 협력해 전국 최초로 도입했다([아주경제 2023-10-03](https://www.ajunews.com/view/20231003161847877)). 2022-09 계획 단계에서는 "내년 1월부터"였다([아주경제 2022-09-15](https://www.ajunews.com/view/20220915174155028)). 반출물에서 급식 결제가 2023-06에 시작하는 이유와 맞는다. P0는 계획대로 하되, **B가 나오면 외부 사실과 어긋나므로 이상 신호**로 기록한다.
  - **배달팁 지원.** 2023년에는 사업시행사 자체 예산 3억 원으로 배달팁 **전액**을 지원했다(아주경제 2023-10-03). 2024년에는 "1월~예산 소진 시까지, 최대 4,000원, 초과분 본인 부담"이다([아동급식 정보마당 공지 2024-04-09](https://kidsmeal.daegu.go.kr/view/fjo/ntcpoi/ntcPoiDtl?bbsSn=2), 공지 이미지의 대체텍스트).
  - **`CHILD_DISC_AMT`는 배달팁 지원액일 가능성이 크다** `[INFERRED]`. 2024-03까지 약 11.2만 식에 2.9억 원을 지원했다([뉴데일리 2024-03-27](https://tk.newdaily.co.kr/site/data/html/2024/03/27/2024032700397.html)). 1식 평균 약 2,590원으로, 2차 현장의 `CHILD_DISC_AMT` 평균 2,473원(잠정)과 가깝다. 3차 A2에서 확인한다: `app+disc=tot`이 1에 가까운지, 500원 구간에서 4,000원 구간에 몰리는지.
  - **반출물과 보도 대조.**
    - 2023-06~08 급식 결제: 보도 "약 3만 건" ↔ 2차 반출 31,061건. 일치한다.
    - 같은 기간 전체 주문 중 비중: 보도 4.8% ↔ 반출물 5.6%. 분모가 다르다(보도는 전체 주문, 반출물은 승인시각 있는 완료 결제).
    - 2024-03까지 누적: 보도 "약 11.2만 식" ↔ 2023-06~2024-02 반출물 117,970건. 약 5% 차이로, 집계 시점이나 정의 차이일 수 있다.
  - 대구 동구청 안내에 따르면 학기 중에는 조·중·석식, 토·공휴일과 방학 중에는 중식을 지원한다. 2차 결과의 "방학에 점심 쏠림"과 방향이 맞는다 `[INFERRED]`.
- **조례 확인(2026-10-01)**: [대구광역시 아동급식 지원 조례](https://www.law.go.kr/LSW/ordinInfoP.do?ordinSeq=1755623)(조례 제5878호, 2022-12-12 제정·시행). 연혁은 제정 1건뿐이므로 데이터 기간 내내 같은 조례다. **단가와 이용시간 숫자는 조례에 없다.**
  - 단가는 시장이 매년 세우는 "아동급식 계획"에서 정한다(제4조①2). 보건복지부 급식최저단가 이상이어야 한다(제7조②).
  - 배달앱 급식 지원의 근거는 제7조①3("온라인플랫폼(배달앱 등)을 통한 급식 지원")과 제9조(비대면 주문결제 온라인플랫폼 구축·운영·위탁)다.
  - 국가법령정보센터 자치법규 검색에서 시행규칙은 나오지 않았다. 구·군별 아동급식지원 조례는 따로 있다.
  - 따라서 B·C의 출처는 연도별 아동급식 계획이나 대구시 안내문에서 찾아야 한다. 담당은 대구시 교육청소년과(053-803-5894, 조례 페이지 표기)다.
  - 조례 제정(2022-12) 약 6개월 뒤에 대구로 급식 결제가 처음 관측된다(2023-06). 두 사건의 관계는 `[INFERRED]`이며, **P0 판정 규칙에는 쓰지 않는다.**

---

## 2. 공통 설정 셀 (S1) — 가장 먼저, 약 10줄

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
**확인**: 컬럼 이름이 위 상수와 정확히 같은지 본다. 다르면 상수를 고치고 다음으로 간다.

---

## 3. P0 — 분석 기간 확정 (30분)

### 셀 P1 — `CHILD_DISC_AMT`가 0보다 큰 행의 결제수단 × 연월 (약 11줄)

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

**읽는 법**
- 첫 표: 결제수단별 전체 건수와 그중 `CHILD_DISC_AMT > 0` 건수. **아동급식카드 외에 0보다 큰 값이 많은 코드가 있는지** 본다.
- 둘째 표: **2023-06 이전**에 0보다 큰 행이 있는 연월과 코드. 비어 있으면(빈 표) 판정 **A**로 간다.

### 셀 P1b — 급식 결제의 월별 아동 할인 건수 (1줄, 2026-10-01 추가·사용자 승인)

```python
print(a.loc["아동급식카드"].to_string())
```
**언제**: P1 바로 뒤, **A1보다 먼저** 친다(A1이 `a`를 덮어쓴다).

**읽는 법**: 연월별 급식 결제 건수 `n`(취소 포함, 빈 ym 줄 포함 합 369,750)과 그중 `CHILD_DISC_AMT > 0`인 건수 `n_disc`를 보여 준다.
- **2023-06~12의 `n_disc`가 거의 0이면** 그 시기에는 표지(`CHILD_DISC_AMT`)가 기록되지 않았다는 뜻이다. 그러면 이 표지로는 2023-05 이전 기록 여부를 판단할 수 없으므로 **판정 C**("판단 불가")다.
- `n_disc / n`이 갑자기 0에 가까워지는 달이 있으면 배달팁 지원이 끊긴 달(예산 소진)일 수 있다 `[INFERRED]`. 메모에 적고, 월별 급식 추이를 해석할 때 쓴다.
- 근거: `CHILD_DISC_AMT`가 배달팁 지원액일 가능성(§1 외부 자료).

### 셀 P2 — 행복페이·카드·대구로페이 월별 추이 (약 6줄)

```python
b = a.reset_index()
b = b[b[C_GBN].isin(["행복페이", "카드", "대구로페이"])]
print(b.pivot(index="ym", columns=C_GBN, values="n").fillna(0).to_string())
b["vac"] = b.ym.str[4:6].isin(["01", "02", "08"])
b["yr"] = b.ym.str[:4]
print(b.groupby([C_GBN, "yr", "vac"]).n.sum().unstack().to_string())
```
**읽는 법**: 행복페이의 방학월 비중이 **연도마다 높은지**, 아니면 특정 연도만 높은지 본다. 특정 연도만이면 플랫폼 계절성이지 급식 신호가 아니다.

### 셀 P3 — (P1이 애매할 때만) 계정 겹침 (약 11줄)

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
**읽는 법**: 어떤 코드의 `share`가 유별나게 높으면 그 코드에 급식 계정이 섞였을 수 있다. 다만 단독 증거로 쓰지 않는다(일반 이용자도 겹친다).

### 판정 (D-014, 결과를 보기 전에 고정된 규칙)

| 관측 | 판정 | 조치 |
|---|---|---|
| 2023-05 이전 `CHILD_DISC_AMT > 0`이 **없거나 산발적** | **A. 25개월 확정** | 주 분석 2023-06~2025-06, 2023-06 제외 민감도 병기 |
| **매월 반복 + 방학에 증가** | **B. 확장판 추가** | 주 분석은 25개월 유지, 확장판(2022-01~)은 **기간 민감도**로만 |
| 값 의미 불명 또는 급식 외 코드에 흔함 | **C. 판단 불가** | A로 처리하고 한계에 명시 |

**이 판정을 문서로 적고 번복하지 않는다.**

---

## 4. M4 — 법정동 공간 (90분)

> **동 이름 반출이 불가하면**: 아래 `dong` 키를 `군구 + 번호`로 바꿔 반출하고(내부 매핑표는 현장 노트에만), 동 이름 목록은 별도 승인 요청한다. 지도는 승인 후 4차에 그린다.

### 셀 M1 — 가맹점 테이블과 동 키 (약 8줄)

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
**확인**: 동 개수가 대구 법정동 규모(200개 안팎)인지, 가맹점 합이 22,086인지 본다.

### 셀 M2 — 급식 결제 읽기 (약 12줄, 1~2분)

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
**확인**: `len(m)`이 **341,216**이어야 한다. 다르면 기록하고 계속한다.

### 셀 M3 — 일반 결제의 가맹점별 건수 (약 9줄, 1~2분)

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
**확인**: 합이 **3,612,950**이어야 한다.

### 셀 M4 — 동 × 레짐 표와 억제 (약 12줄)

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
**읽는 법**: 마지막 출력의 레짐별 합이 학기 104,876 / 방학 188,725 / 전환 47,615와 맞는지 본다(2차 반출물 값).

### 셀 M5 — 동 단위 종합표(LQ 포함)와 보완 억제 (약 13줄)

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
**왜 `k == 1`을 함께 막는가**: 한 동에서 레짐 칸 하나만 억제되면, 동 합계에서 빼서 그 값을 되찾을 수 있다. 2차 반출에서 실제로 두 칸이 역산됐다.

### 셀 M6 — 확인표(U2): 등록 Y·영업 중·급식 0 (약 11줄)

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
**읽는 법**: `영업 중·서비스 유지` 수가 **확인표의 진짜 대상**이다. 2차에서 1,412곳으로 계산됐고, 그중 폐업·탈퇴를 뺀 수가 여기서 나온다. 이 수가 기획서 §확인 우선순위표의 모집단이 된다.

---

## 5. H5 — 금액 진단 (60분)

### 셀 A1 — 급식 금액 읽기와 항등식 (약 13줄, 1~2분)

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

### 셀 A2 — 항등식 후보와 분포 (약 8줄)

```python
print("disc>0 비율:", round((a[C_DISC] > 0).mean(), 3))
print("app+disc=tot:", round((a[C_TOT] - a[C_APP] - a[C_DISC]).abs().le(1).mean(), 3))
print("app=tot    :", round((a[C_TOT] - a[C_APP]).abs().le(1).mean(), 3))
print("disc=tot   :", round((a[C_TOT] - a[C_DISC]).abs().le(1).mean(), 3))
print(a[C_DISC].quantile([.1, .25, .5, .75, .9, .99]).to_string())
print(a[C_TOT].quantile([.1, .25, .5, .75, .9, .99]).to_string())
print(a.groupby(a[C_DISC] // 500 * 500).size().head(20).to_string())
```
**읽는 법**
- `disc>0 비율`과 분위수로 **2차 방문의 V2 불일치를 해소**한다(75% 값 재확인).
- 항등식 세 줄 중 **1에 가까운 것**이 `CHILD_DISC_AMT`의 의미를 말해준다. 1에 가까운 게 없으면 "관계 불명"으로 기록하고 H5는 히스토그램까지만 한다(레드팀 C-6).

### 셀 A3 — 500원 히스토그램 반출 (약 9줄)

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
**읽는 법**: 급식과 일반의 봉우리 위치가 **같은지 다른지**만 본다. 같으면 "상한 집군"이 아니라 메뉴 가격 분포일 수 있다.

### 셀 A4 — (단가 공고를 확보한 경우만) 월별 집군점

```python
a["bin"] = a[C_TOT] // 500 * 500
p = a.groupby(["ym", "bin"]).size().rename("n").reset_index()
top = p.sort_values("n").groupby("ym").tail(1)
print(top.to_string())
```
공고로 단가 개정 시점을 알고 있을 때만 의미가 있다. 없으면 건너뛴다.

---

## 6. 반출 패키지

| 파일 | 내용 | 억제 |
|---|---|---|
| `EXPORT_m4_dong_regime.csv` | 동 × 레짐 급식 건수·가맹점·고객 | 건수<5, 가맹점<3, 고객<5 |
| `EXPORT_m4_dong_total.csv` | 동별 가맹점·등록Y·등록비율·일반결제·급식·LQ | 위 + **레짐 칸 1개만 억제된 동은 합계도 억제** + 가맹점<3 |
| `EXPORT_m4_u2_gungu_status.csv` | 확인표 대상(등록Y·영업·급식0)의 군구 × 운영상태 | <3 |
| `EXPORT_m5_amount_hist.csv` | 결제금액 500원 히스토그램(급식·일반) | 건수<5, 고객<5 |
| `filter_definition_v3.txt` | 정의·기간 판정·억제 규칙 메모 | — |

**메모에 반드시 적을 것**: P0 판정(A/B/C)과 근거, 급식 정의(완료·중복 미제거), 기간, 레짐 정의, 동 키가 법정동임, 억제 규칙(보완 억제 포함), 셀별 확인 출력이 기대값과 일치했는지, P1b에서 할인 비율이 0에 가까워진 달(있으면).

**반출 전 점검(사람이 눈으로)**
1. 억제 칸이 하나뿐인 그룹이 없는지 — 셀 M4가 그 개수를 출력한다.
2. 다른 파일의 합계로 억제 칸을 역산할 수 있는지 — 합계 행은 넣지 않는다.
3. 동 이름 반출 승인 여부와 파일 내용이 일치하는지.

---

## 7. 축소 경로 (시간이 부족할 때)

| 남은 시간 | 버리는 것 | 지키는 것 |
|---|---|---|
| 3시간 | H3 결합 진단 | P0 + M4 + H5 |
| 2시간 | H5의 A4, M4의 M6 | P0 + M4(M1~M5) + H5(A1~A3) |
| 1시간 | M4의 동 종합표(M5) | **P0 판정 + 동×레짐 표(M4)** |
| 30분 | 전부 | **P0 판정만.** 이것만 있어도 기간이 확정돼 기획서를 쓸 수 있다 |

---

## 8. 방문 직후 (반출 승인 대기 3일)

1. 로컬에서 `export_check.py`로 **1·2·3차 반출물 누적 역산 점검**
2. 결과 문서 `T2_export_0929_results.md` 작성 — H1-b 판정, 동 LQ 상·하위, 확인표 모집단 확정
3. 설계서 §0.0-4 판정 결과 반영, §0.0-2의 H5 지위 확정
4. 기획서 30p 골격 착수(마감 10-22, W4~W5)

## Status
- 2026-09-28 작성. 방문 전 준비 A~E 미완. 셀은 현장 손타이핑용으로 10~13줄로 분할했다.
- 2026-09-29 당일 체크리스트 작성 → [T2_visit3_checklist.md](T2_visit3_checklist.md) (시간표, 셀별 기대 확인값, P0 판정 기입란, 반출 전 점검). 셀 코드는 바꾸지 않았다.
- 2026-10-01 팀 공유용 쉬운 말 정리(노션 붙여넣기용) → [T2_visit3_notion.md](T2_visit3_notion.md)
- 2026-10-01 방문 전 준비 B·C 결과 기록(§1 표 아래). 출처 미기록. A4 실행 조건은 여전히 미충족.
- 2026-10-01 외부 자료로 데이터 기간 단가가 8,000원으로 일정했을 가능성이 확인됨 → A4 해당 없음. 셀 P1b(1줄) 추가(사용자 승인). P1b 결과가 "2023년 표지 없음"이면 P0는 C.
