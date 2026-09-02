"""Measure how often pairs of sectors are combined in the same elite career,
relative to what the sector marginals alone would produce, and how that changes
over time.

Design
------
An elite coded in two distinct level-2 domains is one edge in a network whose
nodes are sectors. Within a period we ask, for every unordered pair (i, j),
whether that edge appears more often (association) or less often (dissociation)
than the marginals imply.

The reference model is *quasi-independence* on the symmetric sector-by-sector
table with the diagonal excluded by design (self-pairs do not exist). Expected counts E_ij =
a_i * a_j (i != j) are fitted by iterative proportional fitting so that every
sector's row total is reproduced exactly. This is the standard reference model
for square tables in mobility research, and it is the right one here: because
every diversified elite contributes exactly two sector slots, plain independence
or a 2x2 odds ratio builds in a negative dependence between sectors that has
nothing to do with elite behaviour.

Headline statistic
  assoc = log2(observed / expected)      > 0 association, < 0 dissociation
Uncertainty
  Parametric bootstrap over the multinomial distribution of pair counts, refitting
  quasi-independence in each draw. Reported as a percentile interval, a bootstrap
  two-sided p-value, and a Benjamini-Hochberg q-value within period.
Secondary statistic
  log odds ratio from the 2x2 co-occurrence table over all elites of the period
  (sector held in either slot), retained for readers who want the unconditional
  quantity.

Outputs (data/processed/):
  sector_marginals_by_period.csv
  diversification_by_period.csv
  diversification_by_region_period.csv
  sector_pair_association_overall.csv
  sector_pair_association_by_era.csv
  sector_pair_association_by_century.csv
  sector_pair_association_by_era_region.csv
  sector_pair_trends.csv
"""

import itertools
import pathlib

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed"

SECTOR_ORDER = [
    "Politics", "Administration & Law", "Military", "Religion", "Nobility",
    "Kinship", "Big business", "Small business", "Academia",
    "Exploration & Invention", "Culture (core)", "Culture (periphery)",
    "Sport & Games",
]

ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]

CENTURY_MIN, CENTURY_MAX = 800, 1900
MIN_DIVERSIFIED = 300          # a period needs this many two-sector elites
N_BOOT = 2000
RNG = np.random.default_rng(20260902)


def _bh(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(pvals, dtype=float)
    ok = np.isfinite(p)
    q = np.full(p.shape, np.nan)
    if not ok.any():
        return q
    sub, order = p[ok], np.argsort(p[ok])
    ranked = p[ok][order]
    n = ranked.size
    adj = ranked * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(adj, 0, 1)
    q[ok] = out
    return q


def quasi_independence(obs: np.ndarray, iters: int = 400, tol: float = 1e-10) -> np.ndarray:
    """Expected counts under quasi-independence, diagonal excluded by design.

    Fits E_ij = a_i a_j for i != j by iterative proportional fitting so that the
    row totals of E equal those of the observed symmetric table.
    """
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
    rows = obs.sum(axis=2)                                   # (B, k)
    live = rows > 0
    a = np.where(live, np.sqrt(np.maximum(rows, 1e-12)), 0.0)
    eye = np.eye(obs.shape[1], dtype=bool)
    for _ in range(iters):
        exp = a[:, :, None] * a[:, None, :]
        exp[:, eye] = 0.0
        s = exp.sum(axis=2)
        ratio = np.ones_like(a)
        np.divide(rows, s, out=ratio, where=(s > 0) & live)
        a = a * np.sqrt(ratio)          # symmetric Sinkhorn step; a plain ratio diverges
        if np.max(np.abs(ratio[live] - 1.0)) < tol:
            break
    exp = a[:, :, None] * a[:, None, :]
    exp[:, eye] = 0.0
    return exp


def _upper(mat: np.ndarray, pairs) -> np.ndarray:
    return np.array([mat[i, j] for i, j in pairs])


def pair_statistics(frame: pd.DataFrame, period_label: str, period_value) -> pd.DataFrame:
    """Association statistics for every sector pair within one period."""
    idx = {s: k for k, s in enumerate(SECTOR_ORDER)}
    k = len(SECTOR_ORDER)
    pairs = list(itertools.combinations(range(k), 2))

    n_all = len(frame)
    div = frame[frame["diversified"]]
    m = len(div)
    if m < MIN_DIVERSIFIED:
        return pd.DataFrame()

    a_idx = div["sector_main"].map(idx).to_numpy()
    b_idx = div["sector_second"].map(idx).to_numpy()
    lo, hi = np.minimum(a_idx, b_idx), np.maximum(a_idx, b_idx)
    obs = np.zeros((k, k))
    np.add.at(obs, (lo, hi), 1.0)
    obs = obs + obs.T
    np.fill_diagonal(obs, 0.0)

    exp = quasi_independence(obs)
    o_vec = _upper(obs, pairs)
    e_vec = _upper(exp, pairs)
    assoc = np.log2((o_vec + 0.5) / (e_vec + 0.5))

    # Parametric bootstrap: resample the 78 pair counts, refit quasi-independence.
    p_hat = np.clip(o_vec, 0, None)
    p_hat = p_hat / p_hat.sum() if p_hat.sum() > 0 else np.full(len(pairs), 1 / len(pairs))
    draws = RNG.multinomial(int(m), p_hat, size=N_BOOT).astype(float)
    ii = np.array([i for i, _ in pairs])
    jj = np.array([j for _, j in pairs])
    tables = np.zeros((N_BOOT, k, k))
    tables[:, ii, jj] = draws
    tables[:, jj, ii] = draws
    exp_b = quasi_independence_batch(tables)
    boot = np.log2((draws + 0.5) / (exp_b[:, ii, jj] + 0.5))

    ci_low, ci_high = np.percentile(boot, [2.5, 97.5], axis=0)
    boot_sd = boot.std(axis=0, ddof=1)
    centred = boot - assoc                       # bootstrap null centred at zero effect
    p_boot = (np.sum(np.abs(centred) >= np.abs(assoc)[None, :], axis=0) + 1) / (N_BOOT + 1)

    # Secondary: unconditional 2x2 odds ratio over every elite of the period.
    n_sector = (frame["sector_main"].value_counts().reindex(SECTOR_ORDER).fillna(0)
                + frame["sector_second"].value_counts().reindex(SECTOR_ORDER).fillna(0)).to_numpy()

    rows = []
    for pos, (i, j) in enumerate(pairs):
        o = o_vec[pos]
        aa, bb = o, n_sector[i] - o
        cc, dd = n_sector[j] - o, n_all - o - (n_sector[i] - o) - (n_sector[j] - o)
        a2, b2, c2, d2 = aa + 0.5, bb + 0.5, cc + 0.5, max(dd, 0) + 0.5
        lor = np.log(a2 * d2 / (b2 * c2))
        se = np.sqrt(1 / a2 + 1 / b2 + 1 / c2 + 1 / d2)
        rows.append({
            "period_type": period_label,
            "period": period_value,
            "sector_a": SECTOR_ORDER[i],
            "sector_b": SECTOR_ORDER[j],
            "pair": f"{SECTOR_ORDER[i]} + {SECTOR_ORDER[j]}",
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
    out["q_value"] = _bh(out["p_value"].to_numpy())
    out["q_value_uncond"] = _bh(out["p_value_uncond"].to_numpy())
    out["direction"] = np.where(out["q_value"] < 0.05,
                                np.where(out["assoc_log2"] > 0, "associated", "dissociated"),
                                "not distinguishable")
    return out


def build_period_table(df: pd.DataFrame, column: str, label: str, keep=None) -> pd.DataFrame:
    frames = []
    values = keep if keep is not None else sorted(df[column].dropna().unique())
    for value in values:
        got = pair_statistics(df[df[column] == value], label, value)
        if not got.empty:
            frames.append(got)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> None:
    df = pd.read_csv(IN, compression="gzip", low_memory=False)
    df["diversified"] = df["diversified"].astype(bool)
    print(f"persons: {len(df):,}; spanning two sectors: {df['diversified'].sum():,}")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # ---- marginals and diversification rates -------------------------------
    marg = []
    def add_marginals(sub, ptype, pvalue):
        if len(sub) == 0:
            return
        main_only = sub["sector_main"].value_counts().reindex(SECTOR_ORDER).fillna(0)
        any_slot = (main_only + sub["sector_second"].value_counts()
                    .reindex(SECTOR_ORDER).fillna(0))
        div_rate = sub.groupby("sector_main")["diversified"].mean().reindex(SECTOR_ORDER)
        for sector in SECTOR_ORDER:
            marg.append({
                "period_type": ptype, "period": pvalue, "sector": sector,
                "n_main": int(main_only[sector]),
                "n_any_slot": int(any_slot[sector]),
                "share_of_elites_main": main_only[sector] / len(sub),
                "diversification_rate": div_rate[sector],
            })

    for era in ERA_ORDER:
        add_marginals(df[df["era"] == era], "era", era)
    for century in range(CENTURY_MIN, CENTURY_MAX + 100, 100):
        add_marginals(df[df["birth_century"] == century], "century", century)
    pd.DataFrame(marg).to_csv(OUTDIR / "sector_marginals_by_period.csv", index=False)

    win = df[df["birth_century"].between(CENTURY_MIN, CENTURY_MAX)]
    for keys, name in ((["birth_century"], "diversification_by_period.csv"),
                       (["birth_century", "region"], "diversification_by_region_period.csv")):
        tab = (win.groupby(keys)
               .agg(n_elites=("diversified", "size"), n_diversified=("diversified", "sum"))
               .reset_index())
        tab["diversification_rate"] = tab["n_diversified"] / tab["n_elites"]
        tab.to_csv(OUTDIR / name, index=False)

    # ---- pairwise association ---------------------------------------------
    overall = pair_statistics(df, "all", "3500BC-2020AD")
    overall.to_csv(OUTDIR / "sector_pair_association_overall.csv", index=False)
    print(f"overall pairs: {len(overall)}")

    by_era = build_period_table(df, "era", "era", keep=ERA_ORDER)
    by_era.to_csv(OUTDIR / "sector_pair_association_by_era.csv", index=False)
    print(f"era rows: {len(by_era)} over {by_era['period'].nunique()} eras")

    centuries = list(range(CENTURY_MIN, CENTURY_MAX + 100, 100))
    by_century = build_period_table(df, "birth_century", "century", keep=centuries)
    by_century.to_csv(OUTDIR / "sector_pair_association_by_century.csv", index=False)
    print(f"century rows: {len(by_century)} over {by_century['period'].nunique()} centuries")

    df["era_region"] = df["era"] + " | " + df["region"]
    keep_er = sorted(v for v, n in df["era_region"].value_counts().items()
                     if n >= 3000 and "Unknown" not in v)
    by_er = build_period_table(df, "era_region", "era_region", keep=keep_er)
    if not by_er.empty:
        by_er[["era", "region"]] = by_er["period"].str.split(" | ", regex=False, expand=True)
    by_er.to_csv(OUTDIR / "sector_pair_association_by_era_region.csv", index=False)
    print(f"era x region rows: {len(by_er)}")

    # ---- trend of each pair across centuries -------------------------------
    trends = []
    for pair, grp in by_century.groupby("pair"):
        g = grp[np.isfinite(grp["assoc_log2"]) & (grp["assoc_boot_se"] > 0)].sort_values("period")
        if len(g) < 5:
            continue
        x = g["period"].to_numpy(dtype=float) / 100.0
        y = g["assoc_log2"].to_numpy()
        w = 1.0 / g["assoc_boot_se"].to_numpy() ** 2
        X = np.column_stack([np.ones_like(x), x])
        xtwx = X.T @ (X * w[:, None])
        beta = np.linalg.solve(xtwx, X.T @ (y * w))
        resid = y - X @ beta
        dof = max(len(x) - 2, 1)
        scale = float((resid ** 2 * w).sum()) / dof
        cov = np.linalg.inv(xtwx) * scale
        slope, slope_se = beta[1], float(np.sqrt(cov[1, 1]))
        tstat = slope / slope_se if slope_se > 0 else np.nan
        trends.append({
            "pair": pair,
            "sector_a": g["sector_a"].iloc[0],
            "sector_b": g["sector_b"].iloc[0],
            "n_centuries": len(g),
            "first_century": int(g["period"].iloc[0]),
            "last_century": int(g["period"].iloc[-1]),
            "assoc_first": y[0],
            "assoc_last": y[-1],
            "assoc_mean": float(np.average(y, weights=w)),
            "slope_per_century": slope,
            "slope_se": slope_se,
            "slope_ci_low": slope - 1.96 * slope_se,
            "slope_ci_high": slope + 1.96 * slope_se,
            "p_value": 2 * stats.t.sf(abs(tstat), dof) if np.isfinite(tstat) else np.nan,
        })
    tr = pd.DataFrame(trends)
    tr["q_value"] = _bh(tr["p_value"].to_numpy())
    tr["trend"] = np.where(tr["q_value"] < 0.05,
                           np.where(tr["slope_per_century"] > 0, "converging", "diverging"),
                           "flat")
    tr.sort_values("slope_per_century").to_csv(OUTDIR / "sector_pair_trends.csv", index=False)
    print(f"trend rows: {len(tr)}")


if __name__ == "__main__":
    main()
