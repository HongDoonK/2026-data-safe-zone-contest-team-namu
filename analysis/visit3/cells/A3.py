hm = a.groupby(a[C_TOT] // 500 * 500).agg(n=(C_TOT, "size"), n_cust=(C_CUST, "nunique"))
hg = pd.concat(gh).groupby(level=0).sum().rename("n_general")
hg.index = hg.index * 500
e = hm.join(hg, how="outer")
bad = (e.n < 5) | (e.n_cust < 5)
e.loc[bad, ["n", "n_cust"]] = np.nan
e.index.name = "tot_amt_bin500"
e.to_csv("EXPORT_m5_amount_hist.csv", encoding="utf-8-sig")
print(e.head(30).to_string())
