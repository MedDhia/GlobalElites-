"""The four domains of elite power: political/regulatory, ideational/academic,
economic/allocative, security/military.

The 13 sectors of the sector layer are collapsed onto four domains. Three sectors
are left unclassified because they name a mode of transmission or a form of
celebrity instead of a domain of power: Nobility, Kinship and Sport & Games.

    Political / regulatory   Politics, Administration & Law
    Ideational / academic    Religion, Academia, Culture (core), Culture (periphery)
    Economic / allocative    Big business, Small business, Exploration & Invention
    Security / military      Military

Collapsing changes what diversification means. An elite coded Politics plus
Administration & Law spans two sectors but one domain: that is consolidation
inside the political domain, not a second source of power. Only an elite whose
two sectors fall in two different domains crosses a domain boundary, and those
crossings are what the association model is fitted to.

Outputs (data/processed/):
  elites_domain_person_level.csv.gz
  domain_marginals_by_period.csv
  domain_portfolio_by_period.csv
  domain_reach_by_period.csv
  crossing_by_period.csv
  crossing_by_region_period.csv
  consolidation_by_period.csv
  domain_pair_association_overall.csv
  domain_pair_association_by_era.csv
  domain_pair_association_by_century.csv
  domain_pair_association_by_halfcentury.csv
  domain_pair_association_by_era_region.csv
  domain_pair_trends.csv
  domain_pair_summary.csv
"""

import itertools
import pathlib

import numpy as np
import pandas as pd

from assoc_core import bh, pair_statistics, weighted_trend
from domainmap import SPECS, derive

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed"

SPEC = SPECS["main"]
SECTOR_TO_DOMAIN = SPEC["mapping"]      # left unclassified: Nobility, Kinship, Sport & Games
DOMAIN_ORDER = SPEC["domains"]
DOMAIN_LONG = {
    "Political": "Political / regulatory",
    "Ideational": "Ideational / academic",
    "Economic": "Economic / allocative",
    "Security": "Security / military",
}

ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]
CENTURY_MIN, CENTURY_MAX = 800, 1900
HALF_MIN, HALF_MAX = 1400, 1950     # half-century cohorts, where counts allow it
MIN_CROSSINGS = 150
RNG = np.random.default_rng(20260902)

RENAME = {"cat_a": "domain_a", "cat_b": "domain_b"}


def build_person_level() -> pd.DataFrame:
    df = derive(pd.read_csv(IN, compression="gzip", low_memory=False), SPEC)
    df["birth_halfcentury"] = (df["birth"] // 50).astype(int) * 50
    return df


def domain_pairs(frame, period_type, period):
    sub = frame[frame["n_domains"] >= 1]
    got = pair_statistics(sub, DOMAIN_ORDER, "domain_main", "domain_second",
                          period_type, period, min_units=MIN_CROSSINGS, rng=RNG)
    return got.rename(columns=RENAME)


def build_period_table(df, column, label, keep=None):
    frames = []
    values = keep if keep is not None else sorted(df[column].dropna().unique())
    for value in values:
        got = domain_pairs(df[df[column] == value], label, value)
        if not got.empty:
            frames.append(got)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> None:
    df = build_person_level()
    classified = df[df["n_domains"] >= 1]
    print(f"persons: {len(df):,}")
    print(f"  with at least one of the four domains: {len(classified):,} "
          f"({len(classified) / len(df):.1%})")
    print(f"  crossing two domains: {df['crosses_domains'].sum():,} "
          f"({df['crosses_domains'].sum() / len(classified):.1%} of classified)")
    print(df["sector_span"].value_counts().to_string())

    keep_cols = ["wikidata_code", "name", "birth", "death", "gender", "region", "subregion",
                 "sector_main", "sector_second", "domain_main", "domain_second",
                 "n_domains", "crosses_domains", "portfolio", "sector_span",
                 "birth_century", "birth_halfcentury", "era"]
    df[keep_cols].to_csv(OUTDIR / "elites_domain_person_level.csv.gz", index=False,
                         compression={"method": "gzip", "mtime": 0})

    # ---- marginals, portfolios, reach --------------------------------------
    marg, portfolio, reach = [], [], []

    def add_period(sub, ptype, pvalue):
        if len(sub) == 0:
            return
        cl = sub[sub["n_domains"] >= 1]
        if len(cl) == 0:
            return
        for domain in DOMAIN_ORDER:
            holds = ((cl["domain_main"] == domain) | (cl["domain_second"] == domain))
            n_hold = int(holds.sum())
            if n_hold == 0:
                continue
            crossers = int((holds & cl["crosses_domains"]).sum())
            marg.append({
                "period_type": ptype, "period": pvalue, "domain": domain,
                "n_holders": n_hold,
                "share_of_classified": n_hold / len(cl),
                "cross_domain_rate": crossers / n_hold,
            })
            for other in DOMAIN_ORDER:
                if other == domain:
                    continue
                both = int((holds & ((cl["domain_main"] == other)
                                     | (cl["domain_second"] == other))).sum())
                reach.append({
                    "period_type": ptype, "period": pvalue,
                    "from_domain": domain, "to_domain": other,
                    "n_from": n_hold, "n_both": both, "reach": both / n_hold,
                })
        counts = cl["portfolio"].value_counts()
        for label, n in counts.items():
            portfolio.append({
                "period_type": ptype, "period": pvalue, "portfolio": label,
                "n": int(n), "share_of_classified": n / len(cl),
                "kind": "cross-domain" if " + " in label else "single domain",
            })

    for era in ERA_ORDER:
        add_period(df[df["era"] == era], "era", era)
    for century in range(CENTURY_MIN, CENTURY_MAX + 100, 100):
        add_period(df[df["birth_century"] == century], "century", century)
    add_period(df, "all", "3500BC-2020AD")

    pd.DataFrame(marg).to_csv(OUTDIR / "domain_marginals_by_period.csv", index=False)
    pd.DataFrame(portfolio).to_csv(OUTDIR / "domain_portfolio_by_period.csv", index=False)
    pd.DataFrame(reach).to_csv(OUTDIR / "domain_reach_by_period.csv", index=False)

    win = classified[classified["birth_century"].between(CENTURY_MIN, CENTURY_MAX)]
    for keys, name in ((["birth_century"], "crossing_by_period.csv"),
                       (["birth_century", "region"], "crossing_by_region_period.csv")):
        tab = (win.groupby(keys)
               .agg(n_classified=("crosses_domains", "size"),
                    n_crossing=("crosses_domains", "sum"))
               .reset_index())
        tab["crossing_rate"] = tab["n_crossing"] / tab["n_classified"]
        tab.to_csv(OUTDIR / name, index=False)

    # Among two-sector elites whose sectors are both classified: did the second
    # sector stay inside the same domain (consolidation) or cross into another?
    two = df[df["sector_span"].isin(["two sectors, one domain", "two sectors, two domains"])]
    cons = (two[two["birth_century"].between(CENTURY_MIN, CENTURY_MAX)]
            .assign(within=lambda t: t["sector_span"] == "two sectors, one domain")
            .groupby("birth_century")
            .agg(n_two_sector=("within", "size"), n_within_domain=("within", "sum"))
            .reset_index())
    cons["n_cross_domain"] = cons["n_two_sector"] - cons["n_within_domain"]
    cons["share_within_domain"] = cons["n_within_domain"] / cons["n_two_sector"]
    cons.to_csv(OUTDIR / "consolidation_by_period.csv", index=False)

    # ---- pairwise association ---------------------------------------------
    overall = domain_pairs(df, "all", "3500BC-2020AD")
    overall.to_csv(OUTDIR / "domain_pair_association_overall.csv", index=False)

    by_era = build_period_table(df, "era", "era", keep=ERA_ORDER)
    by_era.to_csv(OUTDIR / "domain_pair_association_by_era.csv", index=False)

    centuries = list(range(CENTURY_MIN, CENTURY_MAX + 100, 100))
    by_century = build_period_table(df, "birth_century", "century", keep=centuries)
    by_century.to_csv(OUTDIR / "domain_pair_association_by_century.csv", index=False)

    halves = list(range(HALF_MIN, HALF_MAX, 50))
    by_half = build_period_table(df, "birth_halfcentury", "halfcentury", keep=halves)
    by_half.to_csv(OUTDIR / "domain_pair_association_by_halfcentury.csv", index=False)

    df["era_region"] = df["era"] + " | " + df["region"]
    keep_er = sorted(v for v, n in df["era_region"].value_counts().items()
                     if n >= 3000 and "Unknown" not in v)
    by_er = build_period_table(df, "era_region", "era_region", keep=keep_er)
    if not by_er.empty:
        by_er[["era", "region"]] = by_er["period"].str.split(" | ", regex=False, expand=True)
    by_er.to_csv(OUTDIR / "domain_pair_association_by_era_region.csv", index=False)
    print(f"pairs: overall {len(overall)}, era {len(by_era)}, "
          f"century {len(by_century)} over {by_century['period'].nunique()}, "
          f"half-century {len(by_half)} over {by_half['period'].nunique()}, "
          f"era x region {len(by_er)}")

    # ---- trends ------------------------------------------------------------
    # Two grids: centuries for comparability with the sector layer, half-centuries
    # from 1400 for the extra points where the counts support them.
    rows = []
    for grid_name, table in (("century", by_century), ("halfcentury", by_half)):
        for pair, grp in table.groupby("pair"):
            fit = weighted_trend(grp, "period", "assoc_log2", "assoc_boot_se")
            if fit is None:
                continue
            rows.append({
                "grid": grid_name,
                "pair": pair,
                "domain_a": grp["domain_a"].iloc[0],
                "domain_b": grp["domain_b"].iloc[0],
                "n_points": fit["n_points"],
                "first_period": fit["first_x"],
                "last_period": fit["last_x"],
                "assoc_first": fit["y_first"],
                "assoc_last": fit["y_last"],
                "assoc_mean": fit["y_mean"],
                "slope_per_century": fit["slope"],
                "slope_se": fit["slope_se"],
                "slope_ci_low": fit["slope_ci_low"],
                "slope_ci_high": fit["slope_ci_high"],
                "p_value": fit["p_value"],
            })
    tr = pd.DataFrame(rows)
    tr["q_value"] = tr.groupby("grid")["p_value"].transform(lambda p: bh(p.to_numpy()))
    tr["trend"] = np.where(tr["q_value"] < 0.05,
                           np.where(tr["slope_per_century"] > 0, "converging", "diverging"),
                           "flat")
    tr.sort_values(["grid", "slope_per_century"]).to_csv(
        OUTDIR / "domain_pair_trends.csv", index=False)

    # ---- one-row-per-pair summary -----------------------------------------
    base = overall[["pair", "domain_a", "domain_b", "n_pair", "expected_qi", "assoc_log2",
                    "assoc_ci_low", "assoc_ci_high", "q_value", "direction",
                    "share_of_diversified", "log_or_uncond"]].rename(columns={
        "n_pair": "n_pair_total", "expected_qi": "expected_total",
        "assoc_log2": "assoc_pooled", "assoc_ci_low": "assoc_pooled_ci_low",
        "assoc_ci_high": "assoc_pooled_ci_high", "q_value": "q_pooled",
        "direction": "direction_pooled"})
    era_wide = by_era.pivot(index="pair", columns="period", values="assoc_log2")
    era_wide = era_wide.reindex(columns=[e for e in ERA_ORDER if e in era_wide.columns])
    era_wide.columns = [f"assoc_{c.replace('-', '_')}" for c in era_wide.columns]
    era_n = by_era.pivot(index="pair", columns="period", values="n_pair")
    era_n = era_n.reindex(columns=[e for e in ERA_ORDER if e in era_n.columns])
    era_n.columns = [f"n_{c.replace('-', '_')}" for c in era_n.columns]
    summary = (base.merge(era_wide, on="pair", how="left")
                   .merge(era_n, on="pair", how="left")
                   .merge(tr[tr["grid"] == "halfcentury"]
                          [["pair", "slope_per_century", "slope_ci_low", "slope_ci_high",
                            "q_value", "trend", "assoc_first", "assoc_last"]]
                          .rename(columns={"q_value": "q_slope"}), on="pair", how="left")
                   .sort_values("assoc_pooled", ascending=False))
    summary.to_csv(OUTDIR / "domain_pair_summary.csv", index=False)
    print(f"trends: {len(tr)}; summary columns: {summary.shape[1]}")


if __name__ == "__main__":
    main()
