mr = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_CUST, C_GBN, C_STAT, C_TIME], dtype=str,
                      encoding=ENC, chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    mr.append(ch[(ch[C_GBN].isin(MEAL)) & (ch[C_STAT] == DONE)])
m = pd.concat(mr)
m["ym"] = m[C_TIME].str[:6]
m = m[(m.ym >= "202306") & (m.ym <= "202506")]
mm = m.ym.str[4:6]
m["R"] = np.where(mm.isin(["01", "02", "08"]), "방학",
                  np.where(mm.isin(["07", "12"]), "전환", "학기"))
m["dong"] = m[C_SHOP].map(d2)
print(len(m), "동 결측:", m.dong.isna().sum(), "동 수:", m.dong.nunique())
