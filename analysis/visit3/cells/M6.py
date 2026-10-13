u = sh.set_index("SHOP_ID").copy()
u["gen"] = gp
u["meal"] = m.groupby(C_SHOP).size()
u[["gen", "meal"]] = u[["gen", "meal"]].fillna(0)
sel = u[(u.CHILD_ABLE_YN == "Y") & (u.gen > 0) & (u.meal == 0)]
print("U2 대상:", len(sel))
print(sel.groupby(["STORE_STATUS", "SERVICE_CLOSED"]).size().to_string())
e2 = sel.groupby(["GUNGU_NM", "STORE_STATUS"]).size().unstack(fill_value=0)
e2[e2 < 3] = np.nan
e2.to_csv("EXPORT_m4_u2_gungu_status.csv", encoding="utf-8-sig")
live = sel[(sel.STORE_STATUS == "01") & (sel.SERVICE_CLOSED == "N")]
print("영업 중·서비스 유지:", len(live), "/", len(sel))
