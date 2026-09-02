"""Shared estimator for pairwise association between categories that co-occur
inside the same unit.

Used by the 13-sector layer (scripts/02) and the 4-domain layer (scripts/05).

The reference model is quasi-independence on the symmetric category-by-category
table, with the diagonal excluded by design (a person cannot pair a category with
itself). Expected counts E_ij = a_i * a_j are fitted by iterative proportional
fitting so that every category's row total is reproduced exactly.

Quasi-independence is used over a plain 2x2 odds ratio because every unit that
appears in the table occupies exactly two slots, which makes the category
indicators negatively dependent by construction; plain independence would read
that arithmetic as substantive behaviour.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy import stats

DEFAULT_BOOT = 2000


def bh(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values, NaN-safe."""
    p = np.asarray(pvals, dtype=float)
    ok = np.isfinite(p)
    q = np.full(p.shape, np.nan)
    if not ok.any():
        return q
    ranked_source = p[ok]
    order = np.argsort(ranked_source)
    ranked = ranked_source[order]
    n = ranked.size
    adj = ranked * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(adj, 0, 1)
    q[ok] = out
    return q


def quasi_independence(obs: np.ndarray, iters: int = 400, tol: float = 1e-10) -> np.ndarray:
    """Expected counts under quasi-independence, diagonal excluded by design."""
    rows = obs.sum(axis=1)
    live = rows > 0
    a = np.where(live, np.sqrt(np.maximum(rows, 1e-12)), 0.0)
    for _ in range(iters):
        exp = np.outer(a, a)
        np.fill_diagonal(exp, 0.0)
        s = exp.sum(axis=1)
        ratio = np.ones_like(a)
        np.divide(rows, s, out=ratio, where=(s > 0) & live)
        a = a * np.sqrt(ratio)          # symmetric Sinkhorn step; a plain ratio diverges
        if np.nanmax(np.abs(ratio[live] - 1.0)) < tol:
            break
    exp = np.outer(a, a)
    np.fill_diagonal(exp, 0.0)
    return exp


def quasi_independence_batch(obs: np.ndarray, iters: int = 200, tol: float = 1e-9) -> np.ndarray:
    """Vectorised quasi-independence fit for a stack of tables, shape (B, k, k)."""
    rows = obs.sum(axis=2)
    live = rows > 0
    a = np.where(live, np.sqrt(np.maximum(rows, 1e-12)), 0.0)
    eye = np.eye(obs.shape[1], dtype=bool)
    for _ in range(iters):
        exp = a[:, :, None] * a[:, None, :]
        exp[:, eye] = 0.0
        s = exp.sum(axis=2)
        ratio = np.ones_like(a)
        np.divide(rows, s, out=ratio, where=(s > 0) & live)
        a = a * np.sqrt(ratio)
        if np.max(np.abs(ratio[live] - 1.0)) < tol:
            break
    exp = a[:, :, None] * a[:, None, :]
    exp[:, eye] = 0.0
    return exp


def cooccurrence_matrix(frame: pd.DataFrame, categories, main_col: str,
                        second_col: str) -> np.ndarray:
    """Symmetric count of units holding each unordered pair of categories."""
    idx = {c: k for k, c in enumerate(categories)}
    k = len(categories)
    both = frame[frame[main_col].notna() & frame[second_col].notna()
                 & (frame[second_col] != frame[main_col])]
    a = both[main_col].map(idx).to_numpy()
    b = both[second_col].map(idx).to_numpy()
    obs = np.zeros((k, k))
    np.add.at(obs, (np.minimum(a, b), np.maximum(a, b)), 1.0)
    obs = obs + obs.T
    np.fill_diagonal(obs, 0.0)
    return obs


def pair_statistics(frame: pd.DataFrame, categories, main_col: str, second_col: str,
                    period_type: str, period, min_units: int = 300,
                    n_boot: int = DEFAULT_BOOT, rng=None) -> pd.DataFrame:
    """Association statistics for every unordered pair of categories in one period.

    Returns one row per pair with, among other columns:
      n_pair        units holding both categories
      expected_qi   expected count under quasi-independence
      assoc_log2    log2((n_pair + 0.5) / (expected_qi + 0.5))
      assoc_ci_*    95% percentile interval from a parametric bootstrap that
                    resamples the pair counts and refits the model each draw
      p_value       two-sided bootstrap p-value
      log_or_uncond secondary statistic: log odds ratio of holding both
                    categories, over every unit of the period
    """
    rng = np.random.default_rng() if rng is None else rng
    k = len(categories)
    pairs = list(itertools.combinations(range(k), 2))
    ii = np.array([i for i, _ in pairs])
    jj = np.array([j for _, j in pairs])

    n_all = len(frame)
    obs = cooccurrence_matrix(frame, categories, main_col, second_col)
    m = int(obs.sum() / 2)
    if m < min_units:
        return pd.DataFrame()

    exp = quasi_independence(obs)
    o_vec = obs[ii, jj]
    e_vec = exp[ii, jj]
    assoc = np.log2((o_vec + 0.5) / (e_vec + 0.5))

    p_hat = np.clip(o_vec, 0, None)
    p_hat = p_hat / p_hat.sum() if p_hat.sum() > 0 else np.full(len(pairs), 1 / len(pairs))
    draws = rng.multinomial(m, p_hat, size=n_boot).astype(float)
    tables = np.zeros((n_boot, k, k))
    tables[:, ii, jj] = draws
    tables[:, jj, ii] = draws
    exp_b = quasi_independence_batch(tables)
    boot = np.log2((draws + 0.5) / (exp_b[:, ii, jj] + 0.5))

    ci_low, ci_high = np.percentile(boot, [2.5, 97.5], axis=0)
    boot_sd = boot.std(axis=0, ddof=1)
    centred = boot - assoc
    p_boot = (np.sum(np.abs(centred) >= np.abs(assoc)[None, :], axis=0) + 1) / (n_boot + 1)

    n_cat = (frame[main_col].value_counts().reindex(categories).fillna(0)
             + frame[second_col].value_counts().reindex(categories).fillna(0)).to_numpy()

    rows = []
    for pos, (i, j) in enumerate(pairs):
        o = o_vec[pos]
        aa, bb = o, n_cat[i] - o
        cc, dd = n_cat[j] - o, n_all - o - (n_cat[i] - o) - (n_cat[j] - o)
        a2, b2, c2, d2 = aa + 0.5, bb + 0.5, cc + 0.5, max(dd, 0) + 0.5
        lor = np.log(a2 * d2 / (b2 * c2))
        se = np.sqrt(1 / a2 + 1 / b2 + 1 / c2 + 1 / d2)
        rows.append({
            "period_type": period_type,
            "period": period,
            "cat_a": categories[i],
            "cat_b": categories[j],
            "pair": f"{categories[i]} + {categories[j]}",
            "n_elites_period": n_all,
            "n_diversified_period": m,
            "n_pair": int(o),
            "expected_qi": e_vec[pos],
            "assoc_log2": assoc[pos],
            "assoc_ci_low": ci_low[pos],
            "assoc_ci_high": ci_high[pos],
            "assoc_boot_se": boot_sd[pos],
            "p_value": p_boot[pos],
            "share_of_diversified": o / m,
            "log_or_uncond": lor,
            "se_uncond": se,
            "ci_low_uncond": lor - 1.96 * se,
            "ci_high_uncond": lor + 1.96 * se,
            "p_value_uncond": 2 * stats.norm.sf(abs(lor / se)),
        })

    out = pd.DataFrame(rows)
    out["q_value"] = bh(out["p_value"].to_numpy())
    out["q_value_uncond"] = bh(out["p_value_uncond"].to_numpy())
    out["direction"] = np.where(out["q_value"] < 0.05,
                                np.where(out["assoc_log2"] > 0, "associated", "dissociated"),
                                "not distinguishable")
    return out


def weighted_trend(frame: pd.DataFrame, x_col: str, y_col: str, se_col: str,
                   x_scale: float = 100.0, min_points: int = 5):
    """Inverse-variance weighted linear fit of y on x. Returns None if too sparse."""
    g = frame[np.isfinite(frame[y_col]) & (frame[se_col] > 0)].sort_values(x_col)
    if len(g) < min_points:
        return None
    x = g[x_col].to_numpy(dtype=float) / x_scale
    y = g[y_col].to_numpy()
    w = 1.0 / g[se_col].to_numpy() ** 2
    X = np.column_stack([np.ones_like(x), x])
    xtwx = X.T @ (X * w[:, None])
    beta = np.linalg.solve(xtwx, X.T @ (y * w))
    resid = y - X @ beta
    dof = max(len(x) - 2, 1)
    scale = float((resid ** 2 * w).sum()) / dof
    cov = np.linalg.inv(xtwx) * scale
    slope, slope_se = float(beta[1]), float(np.sqrt(cov[1, 1]))
    tstat = slope / slope_se if slope_se > 0 else np.nan
    return {
        "n_points": len(g),
        "first_x": int(g[x_col].iloc[0]),
        "last_x": int(g[x_col].iloc[-1]),
        "y_first": float(y[0]),
        "y_last": float(y[-1]),
        "y_mean": float(np.average(y, weights=w)),
        "slope": slope,
        "slope_se": slope_se,
        "slope_ci_low": slope - 1.96 * slope_se,
        "slope_ci_high": slope + 1.96 * slope_se,
        "p_value": 2 * stats.t.sf(abs(tstat), dof) if np.isfinite(tstat) else np.nan,
    }
