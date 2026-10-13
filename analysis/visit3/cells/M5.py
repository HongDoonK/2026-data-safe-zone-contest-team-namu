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
