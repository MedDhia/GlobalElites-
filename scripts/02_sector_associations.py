"""Measure how often pairs of the 13 sectors are combined in the same elite
career, relative to what the sector marginals alone would produce, and how that
changes over time.

An elite coded in two distinct level-2 domains is one edge in a network whose
nodes are sectors. Within a period we ask, for every unordered pair (i, j),
whether that edge appears more often (association) or less often (dissociation)
than the marginals imply. The estimator lives in scripts/assoc_core.py.

Outputs (data/processed/):
  sector_marginals_by_period.csv
  diversification_by_period.csv
  diversification_by_region_period.csv
  sector_pair_association_overall.csv
  sector_pair_association_by_era.csv
  sector_pair_association_by_century.csv
  sector_pair_association_by_halfcentury.csv
  sector_pair_association_by_era_region.csv
  sector_pair_trends.csv
"""

import pathlib

import numpy as np
import pandas as pd

from assoc_core import bh, pair_statistics, weighted_trend

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
HALF_MIN, HALF_MAX = 1400, 1950     # half-century cohorts, matching the domain layer
MIN_DIVERSIFIED = 300
RNG = np.random.default_rng(20260902)

RENAME = {"cat_a": "sector_a", "cat_b": "sector_b"}


def sector_pairs(frame, period_type, period):
    got = pair_statistics(frame, SECTOR_ORDER, "sector_main", "sector_second",
                          period_type, period, min_units=MIN_DIVERSIFIED, rng=RNG)
    return got.rename(columns=RENAME)


def build_period_table(df, column, label, keep=None):
    frames = []
    values = keep if keep is not None else sorted(df[column].dropna().unique())
    for value in values:
        got = sector_pairs(df[df[column] == value], label, value)
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
        any_slot = main_only + sub["sector_second"].value_counts().reindex(SECTOR_ORDER).fillna(0)
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
    overall = sector_pairs(df, "all", "3500BC-2020AD")
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

    df["birth_halfcentury"] = (df["birth"] // 50).astype(int) * 50
    halves = list(range(HALF_MIN, HALF_MAX, 50))
    by_half = build_period_table(df, "birth_halfcentury", "halfcentury", keep=halves)
    by_half.to_csv(OUTDIR / "sector_pair_association_by_halfcentury.csv", index=False)
    print(f"half-century rows: {len(by_half)} over {by_half['period'].nunique()} cohorts")


    # ---- trend of each pair across centuries -------------------------------
    trends = []
    for pair, grp in by_century.groupby("pair"):
        fit = weighted_trend(grp, "period", "assoc_log2", "assoc_boot_se")
        if fit is None:
            continue
        trends.append({
            "pair": pair,
            "sector_a": grp["sector_a"].iloc[0],
            "sector_b": grp["sector_b"].iloc[0],
            "n_centuries": fit["n_points"],
            "first_century": fit["first_x"],
            "last_century": fit["last_x"],
            "assoc_first": fit["y_first"],
            "assoc_last": fit["y_last"],
            "assoc_mean": fit["y_mean"],
            "slope_per_century": fit["slope"],
            "slope_se": fit["slope_se"],
            "slope_ci_low": fit["slope_ci_low"],
            "slope_ci_high": fit["slope_ci_high"],
            "p_value": fit["p_value"],
        })
    tr = pd.DataFrame(trends)
    tr["q_value"] = bh(tr["p_value"].to_numpy())
    tr["trend"] = np.where(tr["q_value"] < 0.05,
                           np.where(tr["slope_per_century"] > 0, "converging", "diverging"),
                           "flat")
    tr.sort_values("slope_per_century").to_csv(OUTDIR / "sector_pair_trends.csv", index=False)
    print(f"trend rows: {len(tr)}")


if __name__ == "__main__":
    main()
