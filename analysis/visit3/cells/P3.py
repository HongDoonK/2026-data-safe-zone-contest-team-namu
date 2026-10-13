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
