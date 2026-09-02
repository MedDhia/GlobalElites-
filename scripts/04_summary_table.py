"""One-stop summary: every sector pair, its pooled association, its value in each
era, and how it moved across the centuries.

Output: data/processed/sector_pair_summary.csv
"""

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]


def main() -> None:
    overall = pd.read_csv(DATA / "sector_pair_association_overall.csv")
    by_era = pd.read_csv(DATA / "sector_pair_association_by_era.csv")
    trends = pd.read_csv(DATA / "sector_pair_trends.csv")

    base = overall[["pair", "sector_a", "sector_b", "n_pair", "expected_qi",
                    "assoc_log2", "assoc_ci_low", "assoc_ci_high", "q_value",
                    "direction", "share_of_diversified", "log_or_uncond"]].copy()
    base = base.rename(columns={
        "n_pair": "n_pair_total",
        "expected_qi": "expected_total",
        "assoc_log2": "assoc_pooled",
        "assoc_ci_low": "assoc_pooled_ci_low",
        "assoc_ci_high": "assoc_pooled_ci_high",
        "q_value": "q_pooled",
        "direction": "direction_pooled",
    })

    era_wide = by_era.pivot(index="pair", columns="period", values="assoc_log2")
    era_wide = era_wide.reindex(columns=[e for e in ERA_ORDER if e in era_wide.columns])
    era_wide.columns = [f"assoc_{c.replace('-', '_')}" for c in era_wide.columns]

    era_n = by_era.pivot(index="pair", columns="period", values="n_pair")
    era_n = era_n.reindex(columns=[e for e in ERA_ORDER if e in era_n.columns])
    era_n.columns = [f"n_{c.replace('-', '_')}" for c in era_n.columns]

    tr = trends[["pair", "slope_per_century", "slope_ci_low", "slope_ci_high",
                 "q_value", "trend", "assoc_first", "assoc_last", "n_centuries"]]
    tr = tr.rename(columns={"q_value": "q_slope"})

    out = (base.merge(era_wide, on="pair", how="left")
                .merge(era_n, on="pair", how="left")
                .merge(tr, on="pair", how="left")
                .sort_values("assoc_pooled", ascending=False))
    out.to_csv(DATA / "sector_pair_summary.csv", index=False)
    print(f"wrote {DATA / 'sector_pair_summary.csv'} with {len(out)} pairs "
          f"and {out.shape[1]} columns")


if __name__ == "__main__":
    main()
