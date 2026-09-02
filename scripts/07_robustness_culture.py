"""Robustness of the domain results to where cultural production is placed.

The main specification puts Culture (core) and Culture (periphery) inside the
ideational domain, which makes that domain the largest of the four and gives it a
hand in every score it enters. This script reruns the whole domain analysis under
five readings and writes them side by side:

  main                  Culture inside the ideational domain
  culture_out           Culture dropped; ideational = religion and the academy
  culture_own           Culture promoted to a fifth domain of its own
  culture_core_only     only Culture (core) counts as ideational
  invention_ideational  Exploration & Invention moved to the ideational domain

The mappings live in scripts/domainmap.py. Everything else, estimator included,
is held constant.

Outputs (data/processed/robustness/):
  <spec>_pair_association_overall.csv
  <spec>_pair_association_by_era.csv
  <spec>_pair_association_by_halfcentury.csv
  <spec>_crossing_by_period.csv
  <spec>_pair_trends.csv
  robustness_universe.csv          how each reading changes the universe
  robustness_pair_comparison.csv   every pair under every reading, pooled
  robustness_core_by_era.csv       the six core pairs under every reading, by era
"""

import pathlib

import numpy as np
import pandas as pd

from assoc_core import bh, pair_statistics, weighted_trend
from domainmap import CORE_PAIRS, SPECS, derive

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "robustness"

ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]
CENTURY_MIN, CENTURY_MAX = 800, 1900
HALF_MIN, HALF_MAX = 1400, 1950
MIN_CROSSINGS = 150


def run_spec(base: pd.DataFrame, name: str, spec: dict, rng) -> dict:
    df = derive(base, spec)
    df["birth_halfcentury"] = (df["birth"] // 50).astype(int) * 50
    domains = spec["domains"]
    classified = df[df["n_domains"] >= 1]

    def pairs(frame, period_type, period):
        sub = frame[frame["n_domains"] >= 1]
        got = pair_statistics(sub, domains, "domain_main", "domain_second",
                              period_type, period, min_units=MIN_CROSSINGS, rng=rng)
        return got.rename(columns={"cat_a": "domain_a", "cat_b": "domain_b"})

    def by(column, label, keep):
        frames = [pairs(df[df[column] == v], label, v) for v in keep]
        frames = [f for f in frames if not f.empty]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    overall = pairs(df, "all", "3500BC-2020AD")
    by_era = by("era", "era", ERA_ORDER)
    by_half = by("birth_halfcentury", "halfcentury", list(range(HALF_MIN, HALF_MAX, 50)))

    win = classified[classified["birth_century"].between(CENTURY_MIN, CENTURY_MAX)]
    crossing = (win.groupby("birth_century")
                .agg(n_classified=("crosses_domains", "size"),
                     n_crossing=("crosses_domains", "sum"))
                .reset_index())
    crossing["crossing_rate"] = crossing["n_crossing"] / crossing["n_classified"]

    trends = []
    for pair, grp in by_half.groupby("pair"):
        fit = weighted_trend(grp, "period", "assoc_log2", "assoc_boot_se")
        if fit is None:
            continue
        trends.append({
            "pair": pair, "n_points": fit["n_points"],
            "assoc_first": fit["y_first"], "assoc_last": fit["y_last"],
            "slope_per_century": fit["slope"], "slope_se": fit["slope_se"],
            "slope_ci_low": fit["slope_ci_low"], "slope_ci_high": fit["slope_ci_high"],
            "p_value": fit["p_value"],
        })
    tr = pd.DataFrame(trends)
    if not tr.empty:
        tr["q_value"] = bh(tr["p_value"].to_numpy())
        tr["trend"] = np.where(tr["q_value"] < 0.05,
                               np.where(tr["slope_per_century"] > 0, "converging", "diverging"),
                               "flat")

    for frame, suffix in ((overall, "pair_association_overall"),
                          (by_era, "pair_association_by_era"),
                          (by_half, "pair_association_by_halfcentury"),
                          (crossing, "crossing_by_period"),
                          (tr, "pair_trends")):
        frame.to_csv(OUTDIR / f"{name}_{suffix}.csv", index=False)

    universe = {
        "spec": name,
        "label": spec["label"],
        "n_domains_in_spec": len(domains),
        "sectors_classified": len(spec["mapping"]),
        "n_persons": len(df),
        "n_classified": len(classified),
        "share_classified": len(classified) / len(df),
        "n_crossing": int(df["crosses_domains"].sum()),
        "crossing_share_of_classified": df["crosses_domains"].sum() / len(classified),
        "n_two_sectors_one_domain": int((df["sector_span"] == "two sectors, one domain").sum()),
        "n_pairs": len(overall),
        "note": spec["note"],
    }
    return {"universe": universe, "overall": overall, "by_era": by_era,
            "by_half": by_half, "trends": tr}


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(IN, compression="gzip", low_memory=False)
    print(f"loaded {len(base):,} persons")

    universe, comparison, core_era = [], [], []
    for name, spec in SPECS.items():
        # A fresh generator per specification, so a run does not depend on the
        # order the specifications happen to be listed in.
        rng = np.random.default_rng(20260902)
        res = run_spec(base, name, spec, rng)
        universe.append(res["universe"])
        print(f"{name:22s} classified {res['universe']['n_classified']:>9,}  "
              f"crossings {res['universe']['n_crossing']:>8,}  "
              f"pairs {res['universe']['n_pairs']:>2d}")

        got = res["overall"].assign(spec=name, spec_label=spec["label"],
                                    spec_short=spec["short"])
        got["is_core_pair"] = got["pair"].isin(CORE_PAIRS)
        comparison.append(got[["spec", "spec_short", "spec_label", "pair", "domain_a",
                               "domain_b", "is_core_pair", "n_pair", "expected_qi",
                               "assoc_log2", "assoc_ci_low", "assoc_ci_high",
                               "q_value", "direction", "share_of_diversified"]])

        era = res["by_era"][res["by_era"]["pair"].isin(CORE_PAIRS)].assign(
            spec=name, spec_short=spec["short"])
        core_era.append(era[["spec", "spec_short", "period", "pair", "n_pair",
                             "assoc_log2", "assoc_ci_low", "assoc_ci_high", "q_value"]])

    pd.DataFrame(universe).to_csv(OUTDIR / "robustness_universe.csv", index=False)
    comp = pd.concat(comparison, ignore_index=True)
    comp.to_csv(OUTDIR / "robustness_pair_comparison.csv", index=False)
    pd.concat(core_era, ignore_index=True).to_csv(
        OUTDIR / "robustness_core_by_era.csv", index=False)

    core = comp[comp["is_core_pair"]]
    spread = (core.groupby("pair")["assoc_log2"]
              .agg(min="min", max="max", spread=lambda s: s.max() - s.min())
              .sort_values("spread", ascending=False))
    print("\nspread of the six core pairs across the five readings")
    print(spread.round(3).to_string())
    signs = core.groupby("pair")["assoc_log2"].apply(lambda s: len(set(np.sign(s))) == 1)
    print(f"\ncore pairs keeping the same sign in all five readings: "
          f"{int(signs.sum())} of {len(signs)}")


if __name__ == "__main__":
    main()
