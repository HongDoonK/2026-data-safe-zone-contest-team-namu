"""Effect sizes and paired shop-block resampling; no p-values."""
import numpy as np
import pandas as pd


def cramers_v(table_2d):
    table = np.asarray(table_2d, dtype=float)
    if table.ndim != 2 or (table < 0).any() or not np.isfinite(table).all():
        raise ValueError("교차표는 유한한 음이 아닌 2차원 배열이어야 합니다")
    table = table[table.sum(axis=1) > 0][:, table.sum(axis=0) > 0]
    total = table.sum()
    if total == 0 or min(table.shape) < 2:
        return np.nan
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / total
    chi2 = ((table - expected) ** 2 / expected).sum()
    return float(np.sqrt(chi2 / (total * (min(table.shape) - 1))))


def share_diff_bootstrap(counts_meal, counts_gen, reps, seed):
    meal, gen = np.asarray(counts_meal, dtype=float), np.asarray(counts_gen, dtype=float)
    if meal.ndim != 2 or meal.shape != gen.shape or (meal < 0).any() or (gen < 0).any():
        raise ValueError("같은 가맹점 순서의 음이 아닌 2차원 행렬이 필요합니다")
    if not np.isfinite(meal).all() or not np.isfinite(gen).all() or type(reps) is not int or reps < 1:
        raise ValueError("유한한 건수와 양의 reps가 필요합니다")
    shops, width = meal.shape

    def diff(m, g):
        if m.sum() == 0 or g.sum() == 0:
            return np.full(width, np.nan)
        return m / m.sum() - g / g.sum()

    observed = diff(meal.sum(0), gen.sum(0))
    rng = np.random.default_rng(seed)
    samples = np.full((reps, width), np.nan)
    if shops:
        for i in range(reps):
            idx = rng.integers(0, shops, size=shops)
            weights = np.bincount(idx, minlength=shops)
            samples[i] = diff((weights[:, None] * meal).sum(0), (weights[:, None] * gen).sum(0))
    valid = np.isfinite(samples).all(axis=1)
    bounds = np.nanpercentile(samples[valid], [2.5, 97.5], axis=0) if valid.any() else np.full((2, width), np.nan)
    # The caller applies M2's n_shops_used<30 publication rule.
    return pd.DataFrame({"hour3": np.arange(width), "diff": observed,
                         "ci_low": bounds[0], "ci_high": bounds[1],
                         "reps_valid": int(valid.sum()), "n_shops_used": shops})
