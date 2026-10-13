import pandas as pd, numpy as np
PAY = r"결제파일경로.csv"
SHOP = r"가맹점파일경로.csv"
ENC = "utf-8"
C_SHOP, C_CUST, C_GBN, C_STAT = "SHOP_ID", "CUST_ID", "PAY_GBN", "CARD_PAY_GBN"
C_TIME, C_TOT, C_APP, C_DISC = "CARD_APP_TIME", "TOT_AMT", "CARD_APP_AMT", "CHILD_DISC_AMT"
MEAL, DONE = ["아동급식카드"], "완료"
print(pd.read_csv(PAY, nrows=1, encoding=ENC, dtype=str).columns.tolist())
print(pd.read_csv(SHOP, nrows=1, encoding=ENC, dtype=str).columns.tolist())
print("pandas:", pd.__version__)
