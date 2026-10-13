gs = []
for ch in pd.read_csv(PAY, usecols=[C_SHOP, C_GBN, C_STAT, C_TIME], dtype=str, encoding=ENC,
                      chunksize=1000000, keep_default_na=False):
    ch = ch.apply(lambda s: s.str.strip())
    ch["ym"] = ch[C_TIME].str[:6]
    ch = ch[(ch[C_STAT] == DONE) & (~ch[C_GBN].isin(MEAL)) & (ch.ym >= "202306") & (ch.ym <= "202506")]
    gs.append(ch[C_SHOP].value_counts())
gp = pd.concat(gs).groupby(level=0).sum()
g = gp.groupby(gp.index.map(d2)).sum()
print(gp.sum(), g.sum())
