"""Scanning a series for one level shift at an unknown date.

A linear trend cannot see a step. These functions fit a common slope plus one
level shift at every admissible date, take the largest Wald statistic on the
shift, and simulate the null distribution of that supremum under a no-shift
model using each period's own standard error, inflated by the overdispersion
the no-shift fit leaves behind.

Shared by the network-structure script and the military-revolution test.
"""

import numpy as np

N_SIM = 2000
TRIM = 2              # periods held out at each end of a break scan
RNG = np.random.default_rng(20260902)


def _wls(X, y, w):
    xtwx = X.T @ (X * w[:, None])
    beta = np.linalg.solve(xtwx, X.T @ (y * w))
    resid = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    scale = float((resid ** 2 * w).sum()) / dof
    cov = np.linalg.inv(xtwx) * scale
    return beta, cov, resid, scale


def sup_wald(x, y, w, candidates, centre=0.0):
    """Largest Wald statistic for a level shift, over every candidate date.

    The time predictor is centred, which leaves the shift estimate and its Wald
    statistic unchanged and keeps the normal equations well conditioned when the
    dates are calendar years.
    """
    best = {"stat": -np.inf}
    xc = x - centre
    for c in candidates:
        X = np.column_stack([np.ones_like(x), xc, (x > c).astype(float)])
        try:
            beta, cov, _, _ = _wls(X, y, w)
        except np.linalg.LinAlgError:
            continue
        se = np.sqrt(max(cov[2, 2], 1e-18))
        stat = (beta[2] / se) ** 2
        if stat > best["stat"]:
            best = {"stat": float(stat), "date": float(c), "shift": float(beta[2]),
                    "shift_se": float(se), "slope": float(beta[1]),
                    "level_at_centre": float(beta[0]), "n_post": int((x > c).sum())}
    return best


def break_test(x, y, se, candidates, n_sim=N_SIM, rng=RNG):
    """Fit one level shift and simulate the null distribution of the supremum.

    Under the null the series is a common slope with no shift. Each simulated
    series uses the period's own bootstrap standard error, inflated by the
    overdispersion the null model leaves behind, so period-to-period variation
    beyond sampling error is carried into the null.
    """
    w = 1.0 / se ** 2
    centre = float(np.mean(x))
    X0 = np.column_stack([np.ones_like(x), x - centre])
    beta0, _, resid0, scale0 = _wls(X0, y, w)
    phi = max(np.sqrt(scale0), 1.0)          # never claim less noise than the bootstrap
    observed = sup_wald(x, y, w, candidates, centre=centre)
    if not np.isfinite(observed.get("stat", np.nan)):
        return None

    fitted = X0 @ beta0
    draws = rng.normal(size=(n_sim, len(x))) * (se * phi)[None, :]
    null = np.empty(n_sim)
    for b in range(n_sim):
        null[b] = sup_wald(x, fitted + draws[b], w, candidates, centre=centre)["stat"]
    p = (np.sum(null >= observed["stat"]) + 1) / (n_sim + 1)
    observed.update({"p_value": float(p), "overdispersion": float(phi),
                     "centre": centre,
                     "level_no_break": float(beta0[0]),
                     "slope_no_break": float(beta0[1]),
                     "rmse_no_break": float(np.sqrt(np.mean(resid0 ** 2)))})
    return observed


def bh(p):
    p = np.asarray(p, dtype=float)
    ok = np.isfinite(p)
    q = np.full(p.shape, np.nan)
    if not ok.any():
        return q
    order = np.argsort(p[ok])
    ranked = p[ok][order]
    n = ranked.size
    adj = np.minimum.accumulate((ranked * n / np.arange(1, n + 1))[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(adj, 0, 1)
    q[ok] = out
    return q
