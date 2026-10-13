"""센터 밖 분석 3 — 법정동(가맹점) ↔ 행정동(인구) 대응표와 결합 단위.

공식 대응표: 행정안전부 KIKmix.20260916(말소코드포함) — 2025-06-30 시점 유효 행만 사용.
결합 단위(unit) = 행정동–법정동 이분 그래프의 연결 성분. 인구·결제를 성분 단위로 합산(면적 배분 없음).
출력: out/bridge_bdong_hdong.csv, out/bridge_units.csv, out/30_summary.txt
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"
AT = "20250630"
log = open(OUT / "30_summary.txt", "w", encoding="utf-8")


def P(*x):
    print(*x, file=log)


k = pd.read_excel(ROOT / "data_external/admin_code/KIKmix.20260916(말소코드포함).xlsx", dtype=str)
k = k[(k.시도명 == "대구광역시") & k.읍면동명.notna() & (k.생성일자 <= AT)
      & (k.말소일자.isna() | (k.말소일자 > AT))]
k = k[k.시군구명 != "군위군"]
# 읍·면 자체 법정코드(끝 2자리 00, 리 아님) 중 같은 읍면에 리가 있으면 제외
is_ri = k.법정동코드.str[8:] != "00"
eup_with_ri = set(k.loc[is_ri, "법정동코드"].str[:8])
k = k[is_ri | ~k.법정동코드.str[:8].isin(eup_with_ri) | (k.법정동코드.str[5:8] < "250")]
names = dict(zip(k.법정동코드, k.동리명))
eup = pd.read_excel(ROOT / "data_external/admin_code/KIKmix.20260916(말소코드포함).xlsx", dtype=str)
eup = eup[eup.법정동코드.str.endswith("00") & eup.법정동코드.str.startswith("27")]
eupname = dict(zip(eup.법정동코드, eup.동리명))
k["bname"] = [f"{eupname.get(c[:8] + '00', '')} {n}" if c[8:] != "00" else n
              for c, n in zip(k.법정동코드, k.동리명)]
k["bkey"] = k.시군구명 + "|" + k.bname.str.strip()
# 출장소가 법정동 대신 군 코드에만 대응된 경우(다사읍서재출장소) → 소속 읍의 단위에 합친다
for i in k.index[k.법정동코드.str[5:] == "00000"]:
    parent_eup = next((e for e in k.읍면동명.unique() if e != k.at[i, "읍면동명"]
                       and k.at[i, "읍면동명"].startswith(e)), None)
    if parent_eup:
        k.at[i, "bkey"] = k.loc[(k.읍면동명 == parent_eup) & (k.법정동코드.str[5:] != "00000"), "bkey"].iloc[0]
P("2025-06-30 유효 대구 행정동", k.행정동코드.nunique(), "법정동(리)", k.bkey.nunique(), "대응 행", len(k))

# 인구 코드와 대조
pop = pd.read_csv(OUT / "pop_hdong_month_6_18.csv", dtype={"hcode": str, "ym": str})
ph, kh = set(pop.hcode), set(k.행정동코드)
P("인구 행정동 144 중 대응표에 있음:", len(ph & kh), "| 인구에 없는 대응표 행정동:", sorted(kh - ph),
  "| 대응표에 없는 인구 행정동:", sorted(ph - kh))

# 가맹점 법정동 키와 대조
dt = pd.read_csv(ROOT / "10_2_데이터분석결과물/EXPORT_m4_dong_total.csv")
r = pd.read_csv(ROOT / "10_2_데이터분석결과물/EXPORT_m4_dong_regime.csv")
keys = set(dt.dong) | set(r.dong)
miss = sorted(x for x in keys if x not in set(k.bkey))
P("가맹점 법정동 키", len(keys), "| 대응표에 없는 키", len(miss), ":", miss)
meal_by = r.groupby("dong").n.sum()
P("  대응 안 되는 키의 급식 결제:", int(meal_by.reindex(miss).fillna(0).sum()), "/", int(meal_by.sum()))

# 연결 성분
parent = {}


def f(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for h, b in zip(k.행정동코드, k.bkey):
    parent[f("H" + h)] = f("B" + b)
k["unit"] = [f("B" + b) for b in k.bkey]
hn = pop.drop_duplicates("hcode").set_index("hcode").hdong
units = (k.groupby("unit").agg(gu=("시군구명", "first"),
                              hdongs=("행정동코드", lambda s: ",".join(sorted({hn.get(c, c) for c in s}))),
                              bdongs=("bname", lambda s: ",".join(sorted(set(s)))),
                              n_h=("행정동코드", "nunique"), n_b=("bkey", "nunique")))
order = units.sort_values(["gu", "hdongs"]).index
units["unit_id"] = pd.Series(range(1, len(units) + 1), index=order).map(lambda i: f"U{i:03d}")
k["unit_id"] = k.unit.map(units.unit_id)
units = units.set_index("unit_id").sort_index()
P("\n결합 단위", len(units), "| 행정동 1개짜리", int((units.n_h == 1).sum()),
  "| 행정동 수 분포", units.n_h.value_counts().sort_index().to_dict())
P("행정동이 가장 많이 묶인 단위:\n", units.sort_values("n_h", ascending=False).head(8)
  [["gu", "n_h", "n_b", "hdongs"]].to_string())

# 가맹점 키 → 단위. 달성군 표기 흔들림 보정: 공백 제거 / 읍면만 적힌 키는 읍면 자체 코드의 행정동 /
# 리만 적힌 키는 달성군 안에서 이름이 유일할 때만
norm = {b.replace(" ", ""): u for b, u in zip(k.bkey, k.unit_id)}
self_eup = pd.read_excel(ROOT / "data_external/admin_code/KIKmix.20260916(말소코드포함).xlsx", dtype=str)
self_eup = self_eup[(self_eup.시군구명 == "달성군") & self_eup.읍면동명.notna()
                    & (self_eup.법정동코드.str[5:] == self_eup.행정동코드.str[5:]) & (self_eup.생성일자 <= AT)
                    & (self_eup.말소일자.isna() | (self_eup.말소일자 > AT))]
for c, n in zip(self_eup.행정동코드, self_eup.동리명):
    u = k.loc[k.행정동코드 == c, "unit_id"]
    if len(u):
        norm.setdefault("달성군|" + n, u.iloc[0])
ri = k[k.시군구명 == "달성군"].assign(ri=lambda d: d.bname.str.split().str[-1])
uniq = ri.groupby("ri").unit_id.agg(lambda s: s.iloc[0] if s.nunique() == 1 else None).dropna()
for n, u in uniq.items():
    norm.setdefault("달성군|" + n, u)
kmap = pd.Series({x: norm.get(x.replace(" ", "")) for x in keys}, name="unit_id")
kmap.index.name = "dong"
un = kmap[kmap.isna()].index.tolist()
P("\n보정 후 단위를 못 찾은 키:", un, "| 급식 결제", int(meal_by.reindex(un).fillna(0).sum()))
P("보정으로 붙은 키:", {x: kmap[x] for x in miss if x not in un})
kmap.to_csv(OUT / "bridge_shopkey_unit.csv", encoding="utf-8-sig")

k[["시군구명", "행정동코드", "읍면동명", "법정동코드", "bkey", "unit_id"]].to_csv(
    OUT / "bridge_bdong_hdong.csv", index=False, encoding="utf-8-sig")
units.to_csv(OUT / "bridge_units.csv", encoding="utf-8-sig")
log.close()
