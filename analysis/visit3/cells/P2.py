b = a.reset_index()
b = b[b[C_GBN].isin(["행복페이", "카드", "대구로페이"])]
print(b.pivot(index="ym", columns=C_GBN, values="n").fillna(0).to_string())
b["vac"] = b.ym.str[4:6].isin(["01", "02", "08"])
b["yr"] = b.ym.str[:4]
print(b.groupby([C_GBN, "yr", "vac"]).n.sum().unstack().to_string())
