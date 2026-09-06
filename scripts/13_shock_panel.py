"""Build the country by birth-cohort panel and the shock list the event study needs.

Panel
-----
Association scores for the six domain crossings, refitted inside every country
and 25-year birth cohort with at least MIN_CROSSINGS elites crossing two domains.
Alongside it, two placebo outcomes that any coverage artefact would move:
the share of classified elites in each domain, and the log count of recorded
elites. If a shock moves the placebos as much as it moves the association
scores, the association result is about the record and not about power.

Shocks
------
Hand-coded, and the coding rule is written down here. A shock enters
only if it is (a) dated to a single year, (b) a rupture in who holds power
and not a change of government within a settled order, and (c) inside the
window where the panel has cohorts on both sides of it.

Exposure
--------
The panel is birth cohorts, not calendar years. A cohort born in [b, b+25) has
careers running roughly [b+25, b+90). A shock in year T is taken to fall on the
first cohort with b >= T - EXPOSURE_LAG, so that most of that cohort's career
comes after the shock. EXPOSURE_LAG is 50 years in the main specification and
30 and 70 are written out as alternatives.

Outputs (data/processed/shocks/):
    shock_panel_pairs.csv        country x cohort x pair association scores
    shock_panel_placebo.csv      country x cohort composition and volume
    shock_list.csv               the coded shocks
    shock_panel_coverage.csv     which cells survive and why
"""

import pathlib

import numpy as np
import pandas as pd

from assoc_core import pair_statistics
from domainmap import SPECS, derive

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "shocks"

SPEC = SPECS["main"]
DOMAIN_ORDER = SPEC["domains"]
COHORT = 25
BIRTH_MIN, BIRTH_MAX = 1500, 1950
MIN_CROSSINGS = 120        # per country and cohort, to fit the six-pair model
MIN_CELLS = 6              # a country needs this many usable cohorts to enter
EXPOSURE_LAGS = {"main": 50, "short": 30, "long": 70}
RNG = np.random.default_rng(20260902)

# Revolutionary rupture: a violent or constitutional overthrow that removed the
# standing of the previous ruling stratum, not a change of government inside a
# settled order. Dated to the year the old order fell.
SHOCKS = [
    {"country": "France", "year": 1789, "type": "revolutionary rupture",
     "event": "Revolution and abolition of noble privilege"},
    {"country": "Russia", "year": 1917, "type": "revolutionary rupture",
     "event": "October Revolution"},
    {"country": "Germany", "year": 1918, "type": "revolutionary rupture",
     "event": "Fall of the empire, abolition of nobility as a legal order"},
    {"country": "Austria", "year": 1918, "type": "revolutionary rupture",
     "event": "Fall of the Habsburg monarchy, Adelsaufhebungsgesetz 1919"},
    # State creation: a new state where none stood, or independence from an
    # imperial centre. Kept separate because the theoretical prior differs.
    {"country": "US", "year": 1776, "type": "state creation",
     "event": "Declaration of Independence"},
    {"country": "Argentina", "year": 1816, "type": "state creation",
     "event": "Independence from Spain"},
    {"country": "Brazil", "year": 1822, "type": "state creation",
     "event": "Independence from Portugal"},
    {"country": "Italy", "year": 1861, "type": "state creation",
     "event": "Unification"},
    {"country": "Canada", "year": 1867, "type": "state creation",
     "event": "Confederation"},
    {"country": "Norway", "year": 1905, "type": "state creation",
     "event": "Dissolution of the union with Sweden"},
    {"country": "Australia", "year": 1901, "type": "state creation",
     "event": "Federation"},
    {"country": "New Zealand", "year": 1907, "type": "state creation",
     "event": "Dominion status"},
]
# Countries with neither kind of rupture inside the window, which is what makes
# them usable as controls: United Kingdom, Sweden, Spain, Switzerland.


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = derive(pd.read_csv(IN, compression="gzip", low_memory=False), SPEC)
    df = df[(df["country"] != "Unknown") & df["birth"].between(BIRTH_MIN, BIRTH_MAX - 1)]
    df["cohort"] = (df["birth"] // COHORT).astype(int) * COHORT
    classified = df[df["n_domains"] >= 1]

    cells = (classified.groupby(["country", "cohort"])["crosses_domains"]
             .agg(n_classified="size", n_crossings="sum").reset_index())
    cells["usable"] = cells["n_crossings"] >= MIN_CROSSINGS
    per_country = cells[cells["usable"]].groupby("country").size()
    panel_countries = sorted(per_country[per_country >= MIN_CELLS].index)
    cells["country_in_panel"] = cells["country"].isin(panel_countries)
    cells.to_csv(OUTDIR / "shock_panel_coverage.csv", index=False)
    print(f"{len(panel_countries)} countries in the panel: {', '.join(panel_countries)}")

    # ---- association scores per cell ---------------------------------------
    frames = []
    for country in panel_countries:
        for cohort in sorted(cells.loc[(cells["country"] == country) & cells["usable"],
                                       "cohort"]):
            sub = classified[(classified["country"] == country)
                             & (classified["cohort"] == cohort)]
            got = pair_statistics(sub, DOMAIN_ORDER, "domain_main", "domain_second",
                                  "country_cohort", f"{country}|{cohort}",
                                  min_units=MIN_CROSSINGS, rng=RNG)
            if not got.empty:
                frames.append(got.rename(columns={"cat_a": "domain_a", "cat_b": "domain_b"}))
    panel = pd.concat(frames, ignore_index=True)
    panel[["country", "cohort"]] = panel["period"].str.split("|", expand=True)
    panel["cohort"] = panel["cohort"].astype(int)
    panel = panel.drop(columns=["period_type", "period"])
    panel.to_csv(OUTDIR / "shock_panel_pairs.csv", index=False)
    print(f"panel: {len(panel):,} rows, "
          f"{panel.groupby(['country', 'cohort']).ngroups} country-cohort cells")

    # ---- placebo outcomes ---------------------------------------------------
    rows = []
    for (country, cohort), grp in classified.groupby(["country", "cohort"]):
        if country not in panel_countries:
            continue
        rec = {"country": country, "cohort": cohort, "n_classified": len(grp),
               "log_n_classified": float(np.log(len(grp))),
               "crossing_rate": float(grp["crosses_domains"].mean())}
        for domain in DOMAIN_ORDER:
            holds = (grp["domain_main"] == domain) | (grp["domain_second"] == domain)
            rec[f"share_{domain.lower()}"] = float(holds.mean())
        rows.append(rec)
    placebo = pd.DataFrame(rows)
    placebo = placebo.merge(cells[["country", "cohort", "n_crossings", "usable"]],
                            on=["country", "cohort"], how="left")
    placebo.to_csv(OUTDIR / "shock_panel_placebo.csv", index=False)

    # ---- shock list ---------------------------------------------------------
    shocks = pd.DataFrame(SHOCKS)
    shocks["in_panel"] = shocks["country"].isin(panel_countries)
    for name, lag in EXPOSURE_LAGS.items():
        shocks[f"first_treated_cohort_{name}"] = (
            np.ceil((shocks["year"] - lag) / COHORT) * COHORT).astype(int)
    obs = panel.groupby("country")["cohort"].agg(["min", "max", "nunique"])
    shocks = shocks.merge(obs.rename(columns={"min": "first_cohort", "max": "last_cohort",
                                              "nunique": "n_cohorts"}),
                          left_on="country", right_index=True, how="left")
    for name in EXPOSURE_LAGS:
        g = shocks[f"first_treated_cohort_{name}"]
        shocks[f"n_pre_{name}"] = [
            int(((panel[panel["country"] == c]["cohort"].unique()) < gg).sum())
            if c in panel_countries else 0
            for c, gg in zip(shocks["country"], g)]
        shocks[f"n_post_{name}"] = [
            int(((panel[panel["country"] == c]["cohort"].unique()) >= gg).sum())
            if c in panel_countries else 0
            for c, gg in zip(shocks["country"], g)]
    shocks.to_csv(OUTDIR / "shock_list.csv", index=False)

    print("\nshocks and the cohorts available around them (main lag = 50 years)")
    print(shocks[shocks["in_panel"]][
        ["country", "year", "type", "first_treated_cohort_main",
         "first_cohort", "last_cohort", "n_pre_main", "n_post_main"]].to_string(index=False))
    controls = [c for c in panel_countries if c not in set(shocks["country"])]
    print(f"\nnever treated inside the window: {', '.join(controls) or 'none'}")


if __name__ == "__main__":
    main()
