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
