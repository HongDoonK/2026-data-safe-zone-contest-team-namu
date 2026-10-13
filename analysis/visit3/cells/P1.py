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
