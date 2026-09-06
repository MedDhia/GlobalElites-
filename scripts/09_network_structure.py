"""Two readings of the elite-power network beyond pairwise scores.

Part A, position and blocks
    Sectors that combine with the same partners occupy the same position, whether
    or not they combine with each other. Profile correlations over the association
    matrix give a positional similarity, average-linkage clustering turns that into
    blocks, and a blockmodel image says how each block relates to every other.
    Alongside it: a continuous core-periphery fit and a set of whole-network indices
    per era, so the shape of the network can be tracked and not only its cells.

Part B, break points
    The trend fits reported earlier are linear, and a linear trend cannot see a level
    shift. For every pair this fits a common-slope model with one level shift at an
    unknown date, scans every admissible date, and takes the largest Wald statistic.
    The null distribution of that supremum is simulated under a no-break model using
    each period's own bootstrap standard error, so the p-values do not lean on an
    asymptotic approximation that a twelve-point series would not support. A pooled
    version asks whether one date fits the whole system at once.

Outputs (data/processed/network_structure/):
    sector_profile_correlations.csv     positional similarity, pooled and by era
    sector_blocks_by_era.csv            block membership of each sector
    blockmodel_image_by_era.csv         mean association within and between blocks
    coreness_by_era.csv                 continuous core-periphery scores
    network_indices_by_era.csv          whole-network indices, both layers
    breakpoints_sector_pairs.csv        one level shift per sector pair
    breakpoints_domain_pairs.csv        one level shift per domain pair
    breakpoint_common_date.csv          pooled scan for a system-wide date
"""

import itertools
import pathlib

import numpy as np
import pandas as pd

from breaks import bh, break_test, sup_wald, _wls
from netstruct import (blocks_from, choose_k, coreness, network_indices,
                       profile_correlations, to_matrix)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUTDIR = DATA / "network_structure"

SECTOR_ORDER = [
    "Politics", "Administration & Law", "Military", "Religion", "Nobility",
    "Kinship", "Big business", "Small business", "Academia",
    "Exploration & Invention", "Culture (core)", "Culture (periphery)",
    "Sport & Games",
]
DOMAIN_ORDER = ["Political", "Ideational", "Economic", "Security"]
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]

N_BLOCKS = 4          # chosen on the pooled matrix, see choose_k()
N_SIM = 2000
TRIM = 2              # periods held out at each end of a break scan
RNG = np.random.default_rng(20260902)


def run_breaks(table, label, pair_col="pair"):
    rows, series = [], {}
    for pair, grp in table.groupby(pair_col):
        g = grp[np.isfinite(grp["assoc_log2"]) & (grp["assoc_boot_se"] > 0)].sort_values("period")
        if len(g) < 2 * TRIM + 4:
            continue
        x = g["period"].to_numpy(dtype=float)
        y = g["assoc_log2"].to_numpy()
        se = g["assoc_boot_se"].to_numpy()
        candidates = x[TRIM:len(x) - TRIM - 1]
        res = break_test(x, y, se, candidates)
        if res is None:
            continue
        rows.append({"layer": label, "pair": pair, "n_points": len(g),
                     "break_date": res["date"], "shift": res["shift"],
                     "shift_se": res["shift_se"],
                     "shift_ci_low": res["shift"] - 1.96 * res["shift_se"],
                     "shift_ci_high": res["shift"] + 1.96 * res["shift_se"],
                     # fitted value at year t is
                     #   level_at_centre + slope_per_century * (t - centre) / 100
                     #   + shift * 1{t > break_date}
                     "centre": res["centre"],
                     "level_at_centre": res["level_at_centre"],
                     "slope_per_century": res["slope"] * 100,
                     "level_no_break": res["level_no_break"],
                     "slope_no_break_per_century": res["slope_no_break"] * 100,
                     "rmse_no_break": res["rmse_no_break"],
                     "sup_wald": res["stat"], "p_value": res["p_value"],
                     "overdispersion": res["overdispersion"]})
        series[pair] = (x, y, se)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["q_value"] = bh(out["p_value"].to_numpy())
        out["has_break"] = out["q_value"] < 0.05
    return out, series


def common_date(series, label, n_sim=N_SIM, rng=RNG):
    """Scan for one date that fits every pair at once."""
    grids = {p: v for p, v in series.items()}
    x_any = next(iter(grids.values()))[0]
    candidates = x_any[TRIM:len(x_any) - TRIM - 1]

    def total(at, data):
        s = 0.0
        for pair, (x, y, se) in data.items():
            w = 1.0 / se ** 2
            X = np.column_stack([np.ones_like(x), x - x.mean(), (x > at).astype(float)])
            try:
                beta, cov, _, _ = _wls(X, y, w)
            except np.linalg.LinAlgError:
                continue
            s += (beta[2] / np.sqrt(max(cov[2, 2], 1e-18))) ** 2
        return s

    observed = {c: total(c, grids) for c in candidates}
    best_date = max(observed, key=observed.get)
    best_stat = observed[best_date]

    # Weighted least squares is invariant to a global rescaling of the weights, so
    # simulating with se * phi and weighting by the same se * phi leaves the Wald
    # statistic on the same scale as the observed one.
    null_sets = []
    for pair, (x, y, se) in grids.items():
        X0 = np.column_stack([np.ones_like(x), x - x.mean()])
        beta0, _, _, scale0 = _wls(X0, y, 1.0 / se ** 2)
        phi = max(np.sqrt(scale0), 1.0)
        null_sets.append((pair, x, X0 @ beta0, se * phi))

    null = np.empty(n_sim)
    for b in range(n_sim):
        data = {pair: (x, fitted + rng.normal(size=len(x)) * sd, sd)
                for pair, x, fitted, sd in null_sets}
        null[b] = max(total(c, data) for c in candidates)
    p = (np.sum(null >= best_stat) + 1) / (n_sim + 1)

    return pd.DataFrame([{"layer": label, "date": float(c),
                          "sum_wald": float(observed[c]),
                          "is_best": c == best_date,
                          "p_value_best": float(p) if c == best_date else np.nan}
                         for c in candidates])


# --------------------------------------------------------------------------- #
def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    sec_overall = pd.read_csv(DATA / "sector_pair_association_overall.csv")
    sec_era = pd.read_csv(DATA / "sector_pair_association_by_era.csv")
    sec_cent = pd.read_csv(DATA / "sector_pair_association_by_century.csv")
    sec_half = pd.read_csv(DATA / "sector_pair_association_by_halfcentury.csv")
    dom_overall = pd.read_csv(DATA / "domain_pair_association_overall.csv")
    dom_era = pd.read_csv(DATA / "domain_pair_association_by_era.csv")
    dom_half = pd.read_csv(DATA / "domain_pair_association_by_halfcentury.csv")

    # ---- Part A ------------------------------------------------------------
    pooled = to_matrix(sec_overall, SECTOR_ORDER, "sector_a", "sector_b")
    corr_pooled = profile_correlations(pooled)
    _, link_pooled, dist_pooled = blocks_from(corr_pooled, N_BLOCKS, SECTOR_ORDER)
    ks = choose_k(dist_pooled, link_pooled)
    print("silhouette by number of blocks (pooled)")
    print(ks.round(3).to_string(index=False))

    # The silhouette curve is close to flat, so the number of blocks is fixed at
    # four for comparability with the domain scheme instead of being read off the curve.
    # The two- and six-block partitions are written out so that choice stays visible.
    alt_rows = []
    for k in (2, 6):
        labels, _, _ = blocks_from(corr_pooled, k, SECTOR_ORDER)
        for node in SECTOR_ORDER:
            alt_rows.append({"k": k, "node": node, "block": labels[node]})
    pd.DataFrame(alt_rows).to_csv(OUTDIR / "block_alternatives_pooled.csv", index=False)

    reference, _, _ = blocks_from(corr_pooled, N_BLOCKS, SECTOR_ORDER)

    corr_rows, block_rows, image_rows, core_rows, index_rows = [], [], [], [], []

    def add_positions(frame, order, a_col, b_col, layer, period, reference=None):
        mat = to_matrix(frame, order, a_col, b_col)
        corr = profile_correlations(mat)
        for i, j in itertools.combinations(range(len(order)), 2):
            corr_rows.append({"layer": layer, "period": period,
                              "node_a": order[i], "node_b": order[j],
                              "profile_correlation": corr.iloc[i, j]})
        labels, _, _ = blocks_from(corr, N_BLOCKS if len(order) > 5 else 2, order,
                                   reference=reference)
        core, fit = coreness(mat)
        for node in order:
            block_rows.append({"layer": layer, "period": period, "node": node,
                               "block": labels[node]})
            core_rows.append({"layer": layer, "period": period, "node": node,
                              "coreness": core[node], "cp_fit": fit})
        blocks = sorted(labels.unique())
        for ba in blocks:
            for bb in blocks:
                members_a = [n for n in order if labels[n] == ba]
                members_b = [n for n in order if labels[n] == bb]
                cells = mat.loc[members_a, members_b].to_numpy(dtype=float)
                if ba == bb:
                    cells = cells[~np.eye(len(members_a), dtype=bool)]
                image_rows.append({"layer": layer, "period": period,
                                   "block_a": ba, "block_b": bb,
                                   "n_cells": int(np.isfinite(cells).sum()),
                                   "mean_assoc": float(np.nanmean(cells))
                                   if np.isfinite(cells).any() else np.nan})
        index_rows.append(network_indices(frame, mat, layer, period))

    add_positions(sec_overall, SECTOR_ORDER, "sector_a", "sector_b", "sector", "all",
                  reference=reference)
    for era in ERA_ORDER:
        sub = sec_era[sec_era["period"] == era]
        if not sub.empty:
            add_positions(sub, SECTOR_ORDER, "sector_a", "sector_b", "sector", era,
                          reference=reference)
    add_positions(dom_overall, DOMAIN_ORDER, "domain_a", "domain_b", "domain", "all")
    for era in ERA_ORDER:
        sub = dom_era[dom_era["period"] == era]
        if not sub.empty:
            add_positions(sub, DOMAIN_ORDER, "domain_a", "domain_b", "domain", era)

    pd.DataFrame(corr_rows).to_csv(OUTDIR / "sector_profile_correlations.csv", index=False)
    pd.DataFrame(block_rows).to_csv(OUTDIR / "sector_blocks_by_era.csv", index=False)
    pd.DataFrame(image_rows).to_csv(OUTDIR / "blockmodel_image_by_era.csv", index=False)
    pd.DataFrame(core_rows).to_csv(OUTDIR / "coreness_by_era.csv", index=False)
    pd.DataFrame(index_rows).to_csv(OUTDIR / "network_indices_by_era.csv", index=False)
    ks.assign(layer="sector", period="all").to_csv(OUTDIR / "block_count_silhouette.csv",
                                                   index=False)

    blocks = pd.DataFrame(block_rows)
    pooled_blocks = blocks[(blocks["layer"] == "sector") & (blocks["period"] == "all")]
    print("\npooled blocks")
    for name, grp in pooled_blocks.groupby("block"):
        print(f"  {name}: {', '.join(grp['node'])}")

    # ---- Part B ------------------------------------------------------------
    print("\nscanning for level shifts")
    # Two windows for the sector layer. The century grid covers the whole record but
    # leans on pre-1100 cohorts of a few thousand people; the half-century grid runs
    # over the same 1400 to 1949 window as the domain layer, where the counts are
    # large. Read the second as the comparable one.
    sec_breaks_c, sec_series_c = run_breaks(sec_cent, "sector centuries")
    sec_breaks_h, sec_series_h = run_breaks(sec_half, "sector half-centuries")
    sec_breaks = pd.concat([sec_breaks_c, sec_breaks_h], ignore_index=True)
    sec_breaks.to_csv(OUTDIR / "breakpoints_sector_pairs.csv", index=False)
    for label, frame in (("centuries", sec_breaks_c), ("half-centuries", sec_breaks_h)):
        print(f"  sector pairs with a shift at q < 0.05, {label}: "
              f"{int(frame['has_break'].sum())} of {len(frame)}")

    dom_breaks, dom_series = run_breaks(dom_half, "domain half-centuries")
    dom_breaks.to_csv(OUTDIR / "breakpoints_domain_pairs.csv", index=False)
    print(f"  domain pairs with a shift at q < 0.05: "
          f"{int(dom_breaks['has_break'].sum())} of {len(dom_breaks)}")

    common = pd.concat([common_date(sec_series_c, "sector centuries"),
                        common_date(sec_series_h, "sector half-centuries"),
                        common_date(dom_series, "domain half-centuries")],
                       ignore_index=True)
    common.to_csv(OUTDIR / "breakpoint_common_date.csv", index=False)
    for layer, grp in common.groupby("layer"):
        best = grp[grp["is_best"]].iloc[0]
        print(f"  common date, {layer}: {int(best['date'])} "
              f"(sum Wald {best['sum_wald']:.0f}, p = {best['p_value_best']:.4f})")


if __name__ == "__main__":
    main()
