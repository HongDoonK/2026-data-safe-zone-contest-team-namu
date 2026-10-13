"""V2-00 suppression. Reports contain internal evidence, never export them.

The task's fixed [lo, n_min-1] domain does not model secondary suppression
or high-n cells hidden for distinct-count reasons. Such tables fail closed.
"""
from itertools import combinations
from numbers import Integral

import numpy as np
import pandas as pd

from .timeparse import hour_to_bucket


def exposure_ranges(S, k, lo, hi):
    """Bounds for k integer cells with a fixed sum and identical domains.

    No feasible assignment is a ValueError, never an empty success.
    An empty group is feasible only with S=0.
    """
    if any(isinstance(x, bool) or not isinstance(x, Integral) for x in (S, k, lo, hi)):
        raise ValueError("S,k,lo,hi는 정수여야 합니다")
    if k < 0 or lo < 0 or hi < lo or S < k * lo or S > k * hi:
        raise ValueError("합계와 억제 칸 범위가 양립하지 않습니다")
    if k == 0:
        return []
    bounds = (max(lo, S - (k - 1) * hi), min(hi, S - (k - 1) * lo))
    return [bounds] * k


def _group_indices(df, keys):
    if not keys:
        return [((), list(range(len(df))))]
    result = []
    grouper = keys[0] if len(keys) == 1 else keys
    for values, part in df.groupby(grouper, dropna=False, sort=False):
        if len(keys) == 1:
            values = (values,)
        result.append((values, part.index.tolist()))
    return result


def suppress(df, key_cols, n_col="n", shop_col="n_shop", cust_col="n_cust",
             n_min=5, shop_min=3, cust_min=5, zero_policy="mask",
             value_cols=None, margin_groups=None, known_totals=None):
    if zero_policy not in ("mask", "show"):
        raise ValueError("zero_policy는 mask 또는 show여야 합니다")
    if any(type(x) is not int or x < 1 for x in (n_min, shop_min, cust_min)):
        raise ValueError("억제 기준은 양의 정수여야 합니다")
    keys = list(key_cols)
    if any(x not in df for x in keys) or df.duplicated(keys).any() if keys else len(df) > 1:
        raise ValueError("키 누락 또는 중복 집계 칸")
    raw = df.reset_index(drop=True).copy()
    if n_col is None and "n" in raw and pd.to_numeric(raw["n"], errors="coerce").notna().any():
        raise ValueError("n_col=None인 표에 숫자 건수 n을 둘 수 없습니다")
    preserved_status = raw["status"].copy() if n_col is None and "status" in raw else None
    if preserved_status is not None and not preserved_status.isin(["published", "suppressed", "banded", "zero"]).all():
        raise ValueError("n_col=None 표의 status 값 오류")
    hidden = pd.Series(False, index=raw.index)
    for col, threshold in ((n_col, n_min), (shop_col, shop_min), (cust_col, cust_min)):
        if col is None or col not in raw:
            continue
        numeric = pd.to_numeric(raw[col], errors="coerce")
        if numeric.isna().any() or (~np.isfinite(numeric)).any() or (numeric < 0).any() or (numeric % 1 != 0).any():
            raise ValueError("억제 입력 건수에 결측·음수·비정수가 있습니다")
        raw[col] = numeric
        hidden = hidden | numeric.lt(threshold)
    zero = raw[n_col].eq(0) if n_col is not None and n_col in raw else pd.Series(False, index=raw.index)
    if zero_policy == "show":
        hidden = hidden & ~zero
    primary = hidden.copy()
    report = {"primary_cells": int(primary.sum()), "secondary_cells": 0,
              "zero_cells": int(zero.sum()), "unresolved": [], "groups": [],
              "zero_policy": zero_policy, "key_cols": keys, "n_col": n_col,
              "thresholds": {"n_min": n_min, "shop_min": shop_min, "cust_min": cust_min}}
    lo, hi = (0 if zero_policy == "mask" else 1), n_min - 1
    shares = [col for col in raw if col.startswith("share_")]
    constraints = []
    if n_col is not None and n_col in raw:
        report["n_before"] = int(raw[n_col].sum())
        # V2-00 3.6 explicitly includes the complete table and margin_groups.
        for group in [[]] + list(margin_groups or []):
            if any(col not in keys for col in group):
                raise ValueError("margin_groups는 키 열만 사용해야 합니다")
            for vals, indexes in _group_indices(raw, list(group)):
                constraints.append((list(group), vals, indexes, int(raw.loc[indexes, n_col].sum()), "margin"))
        for (group, vals), total in (known_totals or {}).items():
            if len(group) != len(vals):
                raise ValueError("known_totals 키와 값 길이 불일치")
            if any(col not in keys for col in group):
                # Callers must map hour/ym/etc before supplying a constraint.
                report["unresolved"].append({"reason": "unmapped_known_total"})
                continue
            mask = pd.Series(True, index=raw.index)
            for col, val in zip(group, vals):
                mask = mask & raw[col].eq(val).fillna(False)
            if isinstance(total, bool) or not isinstance(total, Integral) or total < 0:
                raise ValueError("known_totals 합계는 음이 아닌 정수여야 합니다")
            constraints.append((list(group), tuple(vals), raw.index[mask].tolist(), int(total), "known"))
        if shares:
            # The share denominator grouping is not specified in the API.
            # Never infer it from possibly rounded values; refuse publication.
            report["unresolved"].append({"reason": "share_denominator_group_unspecified"})
        # Monotone: each iteration hides a cell, or finishes. No silent loop cap.
        while True:
            changed = False
            evidence = []
            final_errors = []
            for group, vals, indexes, total, origin in constraints:
                selected = raw.loc[indexes]
                suppressed = [i for i in indexes if hidden.loc[i]]
                published = [i for i in indexes if not hidden.loc[i]]
                S = total - int(raw.loc[published, n_col].sum())
                try:
                    ranges = exposure_ranges(S, len(suppressed), lo, hi)
                    exposed = any(r != (lo, hi) for r in ranges)
                    reason = "narrowed" if exposed else None
                except ValueError:
                    ranges = []
                    exposed = True
                    reason = "infeasible_bounds"
                evidence.append({"keys": group, "values": list(vals), "origin": origin,
                                 "suppressed_cells": len(suppressed), "ranges": ranges})
                if exposed:
                    candidates = [i for i in published if not (zero_policy == "show" and zero.loc[i])]
                    if candidates:
                        chosen = min(candidates, key=lambda i: (raw.loc[i, n_col], i))
                        hidden.loc[chosen] = True
                        changed = True
                        break
                    final_errors.append({"keys": group, "values": list(vals), "reason": reason})
            if not changed:
                report["groups"] = evidence
                report["unresolved"].extend(final_errors)
                break
        # Reject the false domain even when a feasible sum disguises it.
        if ((raw[n_col] < lo) | (raw[n_col] > hi))[hidden].any():
            report["unresolved"].append({"reason": "hidden_count_outside_specified_domain"})
    output = raw.copy()
    if preserved_status is None:
        output["status"] = "published"
        output.loc[hidden, "status"] = "suppressed"
        if zero_policy == "show":
            output.loc[zero, "status"] = "zero"
    else:
        output["status"] = preserved_status
        hidden = hidden | preserved_status.eq("suppressed")
    # A caller can forget value_cols or omit a metric from meta; every
    # non-key value must therefore be hidden by default.
    fields = [col for col in output if col not in keys and col != "status"]
    for col in fields:
        output[col] = output[col].astype(object)
        output.loc[hidden, col] = np.nan
        if preserved_status is not None and pd.api.types.is_numeric_dtype(raw[col]):
            output.loc[preserved_status.eq("banded"), col] = np.nan
    report["secondary_cells"] = int((hidden & ~primary).sum())
    if n_col is not None and n_col in raw:
        report["n_after"] = int(raw.loc[~hidden, n_col].sum())
    # write_export uses this to reject accidental mutations after checking.
    report["frame_digest"] = frame_digest(output)
    return output, report


def frame_digest(df):
    import hashlib
    return hashlib.sha256(df.to_csv(index=False, lineterminator="\n").encode("utf-8")).hexdigest()


def apply_night_bucket(df, hour_col, cfg):
    if "n_shop" in df or "n_cust" in df:
        raise ValueError("고유 수를 합산할 수 없습니다: 원자료에서 hour_bucket별로 다시 집계하세요")
    if "n" not in df:
        raise ValueError("apply_night_bucket에는 n 열이 필요합니다")
    result = df.copy()
    result["hour_bucket"] = result[hour_col].map(lambda hour: hour_to_bucket(hour, cfg))
    keys = [col for col in result if col not in (hour_col, "n")]
    return result.groupby(keys, dropna=False, as_index=False)["n"].sum()
