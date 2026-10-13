"""Explicit population filters; no automatic meal-value selection."""
import json

import pandas as pd


def meal_flag(df, meal_values):
    return df.pay_gbn.astype("string").str.strip().isin(meal_values)


def status_mask(df, status_cfg):
    mode = status_cfg["mode"]
    values = df.card_pay_gbn.astype("string").str.strip()
    if mode == "all":
        return pd.Series(True, index=df.index)
    if mode == "complete_only":
        return values.isin(status_cfg["complete_values"])
    if mode == "exclude_cancel":
        return ~values.isin(status_cfg["cancel_values"])
    raise ValueError("알 수 없는 status_filter.mode")


def period_mask(df, period_cfg):
    return df.ym.between(int(period_cfg["start_ym"]), int(period_cfg["end_ym"])).fillna(False)


def describe_filter(cfg):
    parts = [("meal_pay_values", cfg["meal_pay_values"]), ("status_filter", cfg["status_filter"]),
             ("period", cfg["period"]), ("regime", cfg["regime"]),
             ("night_bucket", cfg["export"]["night_bucket"]),
             ("zero_policy", cfg["suppression"]["zero_policy"]), ("columns", cfg["columns"])]
    text = "\n".join(k + "=" + json.dumps(v, ensure_ascii=False, sort_keys=True) for k, v in parts)
    return text + "\nmetrics: n=행 수; n_shop=nunique(shop_id); n_cust=nunique(cust_id)\n" + \
        "daytype: weekday=월~금, weekend=토~일; 공휴일 미반영\n"
