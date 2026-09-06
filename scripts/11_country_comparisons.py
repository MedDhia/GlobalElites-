"""Country comparisons on the same quantities as the rest of the analysis.

Everything here is computed inside a country, so a country's scores are net of
its own sector marginals and are comparable with another country's.

Country is the cross-verified citizenship of the source database, projected onto
modern states. Two warnings follow from that and neither can be fixed here. The
label is anachronistic for anyone born before the state existed: a fifteenth-century
Florentine is filed under Italy. And coverage is encyclopaedic coverage, so the
number of elites a country contributes reflects which Wikipedia editions write
about it as much as anything about the country.

Outputs (data/processed/countries/):
    country_coverage.csv                 elites, crossings and rates per country
    country_crossing_by_era.csv          crossing rate per country per era
    country_domain_composition.csv       holders and reach per country per domain
    country_domain_pairs.csv             the six crossings per country
    country_domain_pairs_by_era.csv      the six crossings per country per modern era
    country_sector_pairs.csv             the 78 sector pairs per large country
    country_clusters.csv                 countries grouped by crossing profile
    country_cluster_profile.csv          mean crossing profile of each group
"""

import pathlib

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from assoc_core import pair_statistics
from domainmap import SPECS, derive

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "countries"

SPEC = SPECS["main"]
DOMAIN_ORDER = SPEC["domains"]
SECTOR_ORDER = [
    "Politics", "Administration & Law", "Military", "Religion", "Nobility",
    "Kinship", "Big business", "Small business", "Academia",
    "Exploration & Invention", "Culture (core)", "Culture (periphery)",
    "Sport & Games",
]
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]
MODERN_ERAS = ["1800-1899", "1900-2020"]

MIN_DOMAIN_CROSSINGS = 1000     # per country, for the six-pair model
MIN_SECTOR_PAIRS = 5000         # per country, for the seventy-eight-pair model
MIN_ERA_CROSSINGS = 400         # per country and era
N_CLUSTERS = 4
RNG = np.random.default_rng(20260902)


def wilson(k, n, z=1.96):
    """Wilson interval for a proportion."""
    if n == 0:
        return np.nan, np.nan
    p = k / n
    denom = 1 + z ** 2 / n
    centre = (p + z ** 2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return centre - half, centre + half


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = derive(pd.read_csv(IN, compression="gzip", low_memory=False), SPEC)
    df = df[df["country"] != "Unknown"]
    df["diversified"] = df["diversified"].astype(bool)
    print(f"persons with a country: {len(df):,} across {df['country'].nunique()} countries")

    # ---- coverage -----------------------------------------------------------
    cov = (df.groupby("country")
           .agg(n_elites=("crosses_domains", "size"),
                n_classified=("n_domains", lambda s: int((s >= 1).sum())),
                n_crossings=("crosses_domains", "sum"),
                n_sector_diversified=("diversified", "sum"),
                median_birth=("birth", "median"))
           .reset_index())
    cov["crossing_rate"] = cov["n_crossings"] / cov["n_classified"]
    lo, hi = zip(*[wilson(k, n) for k, n in zip(cov["n_crossings"], cov["n_classified"])])
    cov["crossing_rate_ci_low"], cov["crossing_rate_ci_high"] = lo, hi
    cov["share_of_all_elites"] = cov["n_elites"] / len(df)
    cov["in_domain_panel"] = cov["n_crossings"] >= MIN_DOMAIN_CROSSINGS
    cov["in_sector_panel"] = cov["n_sector_diversified"] >= MIN_SECTOR_PAIRS
    cov = cov.sort_values("n_crossings", ascending=False)
    cov.to_csv(OUTDIR / "country_coverage.csv", index=False)

    panel = cov.loc[cov["in_domain_panel"], "country"].tolist()
    sector_panel = cov.loc[cov["in_sector_panel"], "country"].tolist()
    print(f"domain panel: {len(panel)} countries, "
          f"{cov.loc[cov['in_domain_panel'], 'n_crossings'].sum() / cov['n_crossings'].sum():.1%} "
          f"of crossings; sector panel: {len(sector_panel)} countries")

    # ---- crossing rate by era ----------------------------------------------
    rows = []
    for (country, era), grp in df[df["country"].isin(panel)].groupby(["country", "era"]):
        cl = grp[grp["n_domains"] >= 1]
        if len(cl) < 200:
            continue
        k = int(cl["crosses_domains"].sum())
        low, high = wilson(k, len(cl))
        rows.append({"country": country, "era": era, "n_classified": len(cl),
                     "n_crossings": k, "crossing_rate": k / len(cl),
                     "ci_low": low, "ci_high": high})
    pd.DataFrame(rows).to_csv(OUTDIR / "country_crossing_by_era.csv", index=False)

    # ---- domain composition -------------------------------------------------
    rows = []
    for country, grp in df[df["country"].isin(panel)].groupby("country"):
        cl = grp[grp["n_domains"] >= 1]
        for domain in DOMAIN_ORDER:
            holds = (cl["domain_main"] == domain) | (cl["domain_second"] == domain)
            n_hold = int(holds.sum())
            rows.append({"country": country, "domain": domain, "n_holders": n_hold,
                         "share_of_classified": n_hold / len(cl),
                         "cross_domain_rate": (int((holds & cl["crosses_domains"]).sum())
                                               / n_hold) if n_hold else np.nan})
    pd.DataFrame(rows).to_csv(OUTDIR / "country_domain_composition.csv", index=False)

    # ---- the six crossings, per country -------------------------------------
    frames = []
    for country in panel:
        sub = df[(df["country"] == country) & (df["n_domains"] >= 1)]
        got = pair_statistics(sub, DOMAIN_ORDER, "domain_main", "domain_second",
                              "country", country, min_units=MIN_DOMAIN_CROSSINGS, rng=RNG)
        if not got.empty:
            frames.append(got.rename(columns={"cat_a": "domain_a", "cat_b": "domain_b"}))
    dom = pd.concat(frames, ignore_index=True)
    dom = dom.rename(columns={"period": "country"}).drop(columns=["period_type"])
    dom.to_csv(OUTDIR / "country_domain_pairs.csv", index=False)
    print(f"country x crossing rows: {len(dom)}")

    # ---- the six crossings, per country and modern era ----------------------
    frames = []
    for country in panel:
        for era in MODERN_ERAS:
            sub = df[(df["country"] == country) & (df["era"] == era)
                     & (df["n_domains"] >= 1)]
            got = pair_statistics(sub, DOMAIN_ORDER, "domain_main", "domain_second",
                                  "country_era", f"{country} | {era}",
                                  min_units=MIN_ERA_CROSSINGS, rng=RNG)
            if not got.empty:
                frames.append(got.rename(columns={"cat_a": "domain_a", "cat_b": "domain_b"}))
    dom_era = pd.concat(frames, ignore_index=True)
    dom_era[["country", "era"]] = dom_era["period"].str.split(" | ", regex=False, expand=True)
    dom_era.drop(columns=["period_type", "period"]).to_csv(
        OUTDIR / "country_domain_pairs_by_era.csv", index=False)
    print(f"country x era x crossing rows: {len(dom_era)}")

    # ---- the 78 sector pairs, per large country -----------------------------
    frames = []
    for country in sector_panel:
        sub = df[df["country"] == country]
        got = pair_statistics(sub, SECTOR_ORDER, "sector_main", "sector_second",
                              "country", country, min_units=MIN_SECTOR_PAIRS, rng=RNG)
        if not got.empty:
            frames.append(got.rename(columns={"cat_a": "sector_a", "cat_b": "sector_b"}))
    sec = pd.concat(frames, ignore_index=True)
    sec = sec.rename(columns={"period": "country"}).drop(columns=["period_type"])
    sec.to_csv(OUTDIR / "country_sector_pairs.csv", index=False)
    print(f"country x sector-pair rows: {len(sec)}")

    # ---- group countries by their crossing profile --------------------------
    wide = dom.pivot(index="country", columns="pair", values="assoc_log2").dropna()
    dist = np.sqrt(((wide.to_numpy()[:, None, :] - wide.to_numpy()[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(dist, 0.0)
    link = linkage(squareform((dist + dist.T) / 2, checks=False), method="ward")
    labels = fcluster(link, N_CLUSTERS, criterion="maxclust")
    groups = pd.DataFrame({"country": wide.index, "cluster_id": labels})
    # Name each group after its largest member, so the label survives a rerun.
    size = cov.set_index("country")["n_crossings"]
    names = {g: f"{size.reindex(grp['country']).idxmax()} group"
             for g, grp in groups.groupby("cluster_id")}
    groups["cluster"] = groups["cluster_id"].map(names)
    groups = groups.merge(cov[["country", "n_crossings", "crossing_rate"]], on="country")
    groups.sort_values(["cluster", "n_crossings"], ascending=[True, False]).to_csv(
        OUTDIR / "country_clusters.csv", index=False)

    prof = (wide.join(groups.set_index("country")["cluster"])
            .groupby("cluster").agg(["mean", "size"]))
    prof.columns = [f"{a}__{b}" for a, b in prof.columns]
    prof.reset_index().to_csv(OUTDIR / "country_cluster_profile.csv", index=False)
    print("\ncountry groups")
    for name, grp in groups.groupby("cluster"):
        members = grp.sort_values("n_crossings", ascending=False)["country"].tolist()
        print(f"  {name} ({len(members)}): {', '.join(members)}")


if __name__ == "__main__":
    main()
