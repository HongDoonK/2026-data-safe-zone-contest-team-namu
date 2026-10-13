t = m.groupby(["dong", "R"]).agg(n=(C_SHOP, "size"), n_shop=(C_SHOP, "nunique"), n_cust=(C_CUST, "nunique"))
bad = (t.n < 5) | (t.n_shop < 3) | (t.n_cust < 5)
print("칸", len(t), "억제", int(bad.sum()))
tt = t.copy()
tt[bad] = np.nan
tt.to_csv("EXPORT_m4_dong_regime.csv", encoding="utf-8-sig")
k = bad.groupby(level=0).sum()
print("억제 칸이 정확히 1개인 동:", int((k == 1).sum()))
print(t.groupby(level=1).n.sum().to_string())
