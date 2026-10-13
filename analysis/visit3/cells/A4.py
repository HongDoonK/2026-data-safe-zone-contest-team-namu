a["bin"] = a[C_TOT] // 500 * 500
p = a.groupby(["ym", "bin"]).size().rename("n").reset_index()
top = p.sort_values("n").groupby("ym").tail(1)
print(top.to_string())
