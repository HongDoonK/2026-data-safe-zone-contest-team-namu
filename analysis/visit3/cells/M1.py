sh = pd.read_csv(SHOP, dtype=str, encoding=ENC, keep_default_na=False).apply(lambda s: s.str.strip())
sh["dong"] = sh.GUNGU_NM + "|" + sh.DONG_NM
d2 = sh.set_index("SHOP_ID").dong
reg = sh.groupby("dong").agg(shops=("SHOP_ID", "size"),
                             able_y=("CHILD_ABLE_YN", lambda s: (s == "Y").sum()))
print(len(reg), reg.shops.sum())
print(reg.sort_values("shops", ascending=False).head(10).to_string())
print("빈 동 이름:", (sh.DONG_NM == "").sum())
