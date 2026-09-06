"""Cohorts of elites who lived through a major revolution.

What this builds
----------------
One folder per revolution, holding the elites who were adults in a country whose
political order was at stake while the revolution ran, plus the derived tables
that describe them: who they were, which sectors they held, how the fields of
power associated among them, and how that association compares with the birth
cohorts before and after.

Membership rule
---------------
A person belongs to a revolution's cohort when

    their coded country is one of the countries where the political order was at
    stake, and they were at least 20 years old at some point inside the window,
    and they were still alive when the window opened.

Death is missing for more than half the rows, so a missing death year is imputed
as birth + 80 for the alive test only. That imputation is generous: it keeps
people in who may have died earlier, so cohorts are upper bounds on membership.
The `death_imputed` column marks every row where it was used.

Countries are scoped tightly. A revolution's countries are the ones whose own
political order was at stake, not every country that took an interest. France is
not in the Haitian cohort and the United Kingdom is not in the Irish cohort,
though both intervened, because including the metropole would swamp the cohort
with elites whose regime was never in question.

Size rule
---------
A revolution is kept when its cohort holds at least 500 elites and at least 200
who span two sectors, which is the floor the pair estimator needs. Every
revolution considered is listed in `revolutions_index.csv` with its counts and
whether it was kept, so the exclusions are visible.

What this is not
----------------
Nothing here is a causal estimate. These are descriptive cohorts. Living through
a revolution is not an assignment, the windows are conventional dates, and the
birth-cohort series in each folder is a comparison, not a control. The event
study in `scripts/14` is where the causal question is put.

Outputs (data/processed/revolutions/):
    README.md                       the rule, the layout, the counts
    revolutions_index.csv           every revolution considered, kept or not
    cohort_summary.csv              one row per kept revolution
    cohort_composition.csv          sector and group shares, stacked
    cohort_group_pairs.csv          the 21 group-pair scores, stacked
    <slug>/README.md                what the revolution was, what the folder holds
    <slug>/elites.csv.gz            the cohort, person by person
    <slug>/summary.csv              counts and coverage
    <slug>/sector_composition.csv   share of the cohort holding each sector
    <slug>/group_pairs.csv          group-pair association inside the cohort
    <slug>/group_pairs_by_age_band.csv   the same, split by age at the midpoint
    <slug>/birth_cohort_pairs.csv   the same countries by 40-year birth cohort
"""

import pathlib

import numpy as np
import pandas as pd

from assoc_core import pair_statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "revolutions"

GROUP = {
    "Politics": "Politics", "Administration & Law": "Administration & Law",
    "Military": "Military", "Big business": "Business", "Small business": "Business",
    "Nobility": "Nobility & Kinship", "Kinship": "Nobility & Kinship",
    "Religion": "Religion", "Academia": "Learning & Culture",
    "Exploration & Invention": "Learning & Culture",
    "Culture (core)": "Learning & Culture", "Culture (periphery)": "Learning & Culture",
}
GROUP_ORDER = ["Politics", "Administration & Law", "Military", "Business",
               "Nobility & Kinship", "Religion", "Learning & Culture"]
SECTOR_ORDER = ["Politics", "Administration & Law", "Military", "Religion", "Nobility",
                "Kinship", "Big business", "Small business", "Academia",
                "Exploration & Invention", "Culture (core)", "Culture (periphery)",
                "Sport & Games"]

MIN_ELITES = 500
MIN_TWO_SECTOR = 200
MIN_PAIRS = 200          # the floor the pair estimator needs inside a cell
MIN_PAIRS_SPLIT = 100    # the floor for age bands and birth cohorts
SPARSE_CELL = 10         # below this many elites in a pair, assoc_log2 is floor-driven
ADULT = 20
IMPUTED_LIFESPAN = 80
MAX_AGE = 90
COHORT_WIDTH = 40        # birth-cohort blocks in the comparison series
COHORT_SPAN = 120        # years either side of the window covered by that series
RNG = np.random.default_rng(20260906)

# ---------------------------------------------------------------------------
# The revolutions considered. `countries` names the states whose own political
# order was at stake, coded as the source codes present-day citizenship, which is
# the only country field the database carries. That mapping is anachronistic by
# construction: Germany stands for the German states, Italy for the Italian ones,
# and the successor republics stand for the territory of the Russian empire.
# ---------------------------------------------------------------------------
REVOLUTIONS = [
    ("english-revolution", "English Revolution", 1642, 1651,
     ["United Kingdom", "Ireland"],
     "Civil war, regicide and the Commonwealth. The one case in the set where the "
     "old order was restored within a generation."),
    ("glorious-revolution", "Glorious Revolution", 1688, 1689,
     ["United Kingdom", "Ireland"],
     "The deposition of James II and the settlement that followed, which opened the "
     "fiscal-military state tested in scripts/18."),
    ("american-revolution", "American Revolution", 1775, 1783,
     ["US"],
     "Secession and the founding of a republic without a titled nobility."),
    ("french-revolution", "French Revolution", 1789, 1799,
     ["France"],
     "The abolition of the orders, the confiscation of church property and the "
     "reconstruction of the administration."),
    ("haitian-revolution", "Haitian Revolution", 1791, 1804,
     ["Haiti"],
     "A slave revolution that produced an independent state. Kept in the index for "
     "the record; the database holds too few people to work with."),
    ("latin-american-independence", "Latin American independence", 1810, 1825,
     ["Argentina", "Mexico", "Colombia", "Venezuela", "Chile", "Peru", "Bolivia",
      "Ecuador", "Uruguay", "Paraguay", "Brazil"],
     "The Spanish American wars of independence and the Brazilian separation, "
     "grouped as one wave."),
    ("revolutions-of-1848", "Revolutions of 1848", 1848, 1849,
     ["France", "Germany", "Austria", "Hungary", "Italy", "Poland",
      "Czech Republic", "Romania"],
     "The European wave: constitutional and national risings, defeated almost "
     "everywhere within two years."),
    ("meiji-restoration", "Meiji Restoration", 1868, 1869,
     ["Japan"],
     "The overthrow of the shogunate and the dismantling of the samurai order."),
    ("mexican-revolution", "Mexican Revolution", 1910, 1920,
     ["Mexico"],
     "The fall of the Porfiriato and a decade of civil war ending in the 1917 "
     "constitution."),
    ("xinhai-revolution", "Xinhai Revolution", 1911, 1912,
     ["China"],
     "The end of the Qing dynasty and of the imperial examination elite."),
    ("russian-revolution", "Russian Revolution", 1917, 1923,
     ["Russia", "Ukraine", "Poland", "Finland", "Latvia", "Lithuania", "Estonia",
      "Georgia", "Belarus", "Azerbaijan", "Armenia"],
     "February, October and the civil war, across the territory of the Russian "
     "empire."),
    ("german-revolution", "German Revolution", 1918, 1919,
     ["Germany", "Austria"],
     "The fall of the two central European monarchies and the republics that "
     "replaced them."),
    ("irish-revolution", "Irish revolution", 1916, 1923,
     ["Ireland"],
     "The rising, the war of independence, partition and the civil war."),
    ("turkish-revolution", "Turkish revolution", 1919, 1923,
     ["Turkey"],
     "The war of independence, the end of the sultanate and the caliphate, and the "
     "republic."),
    ("chinese-communist-revolution", "Chinese Communist Revolution", 1946, 1949,
     ["China"],
     "The civil war and the founding of the People's Republic."),
    ("cuban-revolution", "Cuban Revolution", 1953, 1959,
     ["Cuba"],
     "The insurgency against Batista and the state built after it."),
    ("iranian-revolution", "Iranian Revolution", 1978, 1979,
     ["Iran"],
     "The fall of the monarchy and the founding of the Islamic Republic."),
]

AGE_BANDS = [("under 20", -np.inf, 19), ("20-35", 20, 35),
             ("36-55", 36, 55), ("56+", 56, np.inf)]


def band_of(age):
    out = np.full(len(age), "", dtype=object)
    for name, lo, hi in AGE_BANDS:
        out[(age >= lo) & (age <= hi)] = name
    return out


def cohort_of(rev, df):
    """The people who lived through one revolution, with ages attached."""
    slug, name, y0, y1, countries, _ = rev
    d = df[df["country"].isin(countries) & df["birth"].notna()].copy()
    death = d["death"].fillna(d["birth"] + IMPUTED_LIFESPAN)
    keep = ((d["birth"] + ADULT <= y1) & (death >= y0)
            & (d["birth"] >= y0 - MAX_AGE))
    d = d[keep].copy()
    d["death_imputed"] = d["death"].isna()
    d["revolution"] = name
    d["revolution_slug"] = slug
    d["window_start"] = y0
    d["window_end"] = y1
    d["age_at_start"] = y0 - d["birth"]
    d["age_at_end"] = y1 - d["birth"]
    d["age_at_midpoint"] = ((y0 + y1) / 2 - d["birth"]).round().astype(int)
    d["age_band"] = band_of(d["age_at_midpoint"].to_numpy())
    return d


def composition(frame, categories, main_col, second_col):
    rows = []
    n = len(frame)
    for c in categories:
        holds = (frame[main_col] == c) | (frame[second_col] == c)
        primary = (frame[main_col] == c)
        rows.append({"category": c, "n_holding": int(holds.sum()),
                     "share_holding": float(holds.sum()) / n if n else np.nan,
                     "n_primary": int(primary.sum()),
                     "share_primary": float(primary.sum()) / n if n else np.nan})
    return pd.DataFrame(rows)


def pairs_for(frame, label, min_pairs=MIN_PAIRS):
    got = pair_statistics(frame, GROUP_ORDER, "group_main", "group_second",
                          "cohort", label, min_units=min_pairs, rng=RNG)
    if got.empty:
        return got
    got = got.rename(columns={"cat_a": "group_a", "cat_b": "group_b"}).drop(
        columns=["period_type"])
    # An empty or near-empty cell makes assoc_log2 a function of the 0.5 continuity
    # correction more than of the data. Flagged, not dropped.
    got["sparse_cell"] = got["n_pair"] < SPARSE_CELL
    return got


def birth_cohort_series(rev, df):
    """The same countries by 40-year birth cohort, for context around the window."""
    slug, name, y0, y1, countries, _ = rev
    d = df[df["country"].isin(countries) & df["birth"].notna()].copy()
    lo = int(np.floor((y0 - COHORT_SPAN) / COHORT_WIDTH) * COHORT_WIDTH)
    hi = int(np.ceil((y1 + COHORT_SPAN) / COHORT_WIDTH) * COHORT_WIDTH)
    frames = []
    for start in range(lo, hi, COHORT_WIDTH):
        cell = d[(d["birth"] >= start) & (d["birth"] < start + COHORT_WIDTH)]
        got = pairs_for(cell, start, min_pairs=MIN_PAIRS_SPLIT)
        if got.empty:
            continue
        got["birth_cohort_start"] = start
        got["birth_cohort_end"] = start + COHORT_WIDTH - 1
        got["overlaps_window"] = (start <= y1) and (start + COHORT_WIDTH - 1 >= y0 - MAX_AGE)
        frames.append(got)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


PERSON_COLS = ["wikidata_code", "name", "birth", "death", "death_imputed", "gender",
               "country", "region", "subregion", "era", "birth_century",
               "domain_level1", "sector_main", "sector_second",
               "group_main", "group_second", "occupation_level3", "visibility",
               "diversified", "revolution", "revolution_slug",
               "window_start", "window_end", "age_at_start", "age_at_end",
               "age_at_midpoint", "age_band"]


def write_folder(rev, cohort, df):
    slug, name, y0, y1, countries, blurb = rev
    folder = OUTDIR / slug
    folder.mkdir(parents=True, exist_ok=True)

    cols = [c for c in PERSON_COLS if c in cohort.columns]
    (cohort[cols].sort_values(["birth", "name"])
     .to_csv(folder / "elites.csv.gz", index=False,
             compression={"method": "gzip", "mtime": 0}))

    two_sector = int((cohort["sector_second"].notna()
                      & (cohort["sector_second"] != cohort["sector_main"])).sum())
    two_group = int(cohort["group_second"].notna().sum())
    bands = cohort["age_band"].value_counts()
    summary = {
        "revolution": name, "slug": slug, "window_start": y0, "window_end": y1,
        "countries": "; ".join(countries),
        "n_elites": len(cohort),
        "n_two_sector": two_sector,
        "n_two_group": two_group,
        "share_two_sector": two_sector / len(cohort),
        "n_death_imputed": int(cohort["death_imputed"].sum()),
        "share_death_imputed": float(cohort["death_imputed"].mean()),
        "birth_min": int(cohort["birth"].min()), "birth_max": int(cohort["birth"].max()),
        "median_age_at_start": float(cohort["age_at_start"].median()),
        "share_women": float((cohort["gender"] == "Female").mean()),
        "median_visibility": float(cohort["visibility"].median()),
    }
    for label, _, _ in AGE_BANDS:
        summary[f"n_{label.replace(' ', '_').replace('+', 'plus')}"] = int(bands.get(label, 0))
    top = cohort["country"].value_counts().head(5)
    summary["top_countries"] = "; ".join(f"{c} {n}" for c, n in top.items())
    pd.DataFrame([summary]).to_csv(folder / "summary.csv", index=False)

    sect = composition(cohort, SECTOR_ORDER, "sector_main", "sector_second")
    sect["level"] = "sector"
    grp = composition(cohort, GROUP_ORDER, "group_main", "group_second")
    grp["level"] = "group"
    comp = pd.concat([sect, grp], ignore_index=True)
    comp.insert(0, "revolution", name)
    comp.to_csv(folder / "sector_composition.csv", index=False)

    pairs = pairs_for(cohort, slug)
    if not pairs.empty:
        pairs = pairs.rename(columns={"period": "slug"})
        pairs.insert(0, "revolution", name)
        pairs.to_csv(folder / "group_pairs.csv", index=False)

    band_frames = []
    for label, _, _ in AGE_BANDS:
        cell = cohort[cohort["age_band"] == label]
        got = pairs_for(cell, label, min_pairs=MIN_PAIRS_SPLIT)
        if got.empty:
            continue
        got = got.rename(columns={"period": "age_band"})
        got.insert(0, "revolution", name)
        band_frames.append(got)
    if band_frames:
        pd.concat(band_frames, ignore_index=True).to_csv(
            folder / "group_pairs_by_age_band.csv", index=False)

    series = birth_cohort_series(rev, df)
    if not series.empty:
        series = series.drop(columns=["period"])
        series.insert(0, "revolution", name)
        series.to_csv(folder / "birth_cohort_pairs.csv", index=False)

    (folder / "README.md").write_text(folder_readme(rev, summary, comp, pairs, series))
    return summary, comp, pairs


def folder_readme(rev, summary, comp, pairs, series):
    slug, name, y0, y1, countries, blurb = rev
    grp = comp[comp["level"] == "group"].sort_values("share_holding", ascending=False)
    lines = [f"# {name}, {y0}-{y1}", "", blurb, "",
             f"Countries whose political order was at stake: {', '.join(countries)}.", "",
             "## The cohort", "",
             f"{summary['n_elites']:,} elites, of whom {summary['n_two_sector']:,} "
             f"({summary['share_two_sector']:.0%}) span two sectors. Birth years "
             f"{summary['birth_min']} to {summary['birth_max']}; median age when the "
             f"window opened, {summary['median_age_at_start']:.0f}. Death year is "
             f"imputed as birth plus {IMPUTED_LIFESPAN} for "
             f"{summary['share_death_imputed']:.0%} of them, for the alive test only.", "",
             "| Age at the midpoint | Elites |", "|---|---:|"]
    for label, _, _ in AGE_BANDS:
        col = f"n_{label.replace(' ', '_').replace('+', 'plus')}"
        lines.append(f"| {label} | {summary[col]:,} |")
    lines += ["", "## What they held", "",
              "Share of the cohort holding each group of sectors, counting both the "
              "primary and the secondary sector.", "",
              "| Group | Share |", "|---|---:|"]
    for _, r in grp.iterrows():
        lines.append(f"| {r['category']} | {r['share_holding']:.1%} |")
    lines += ["", "## Files", "",
              "| File | Contents |", "|---|---|",
              "| `elites.csv.gz` | the cohort, person by person, with ages |",
              "| `summary.csv` | the counts above in one row |",
              "| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |"]
    if not pairs.empty:
        lines.append("| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |")
    lines.append("| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |")
    if not series.empty:
        lo = int(series["birth_cohort_start"].min())
        hi = int(series["birth_cohort_end"].max())
        lines.append(f"| `birth_cohort_pairs.csv` | the same countries by 40-year birth "
                     f"cohort, {lo} to {hi}, as context either side of the window |")
    lines += ["", "Association is `assoc_log2`, the log2 ratio of the observed count of "
              "elites holding both groups to the count expected under quasi-independence "
              "fitted inside this cohort. Positive is association, negative is "
              "dissociation. `scripts/assoc_core.py` holds the estimator and "
              "`docs/CODEBOOK.md` documents every column.", "",
              "These are descriptive cohorts, not treatment groups. Living through a "
              "revolution is not an assignment.", ""]
    return "\n".join(lines)


def index_readme(index):
    lines = ["# Elites who lived through a major revolution", "",
             "One folder per revolution, holding the elites who were adults in a "
             "country whose political order was at stake while the revolution ran.",
             "", "## Membership", "",
             "A person is in a cohort when their coded country is one of the countries "
             "where the political order was at stake, they were at least "
             f"{ADULT} years old at some point inside the window, and they were alive "
             "when the window opened. Death is missing for more than half the rows, so "
             f"a missing death year is imputed as birth plus {IMPUTED_LIFESPAN} for the "
             "alive test only; `death_imputed` marks every row where that was used. The "
             "imputation is generous, so the cohorts are upper bounds.", "",
             "Countries are scoped to the states whose own order was in question, not "
             "every state that took an interest. France is not in the Haitian cohort and "
             "the United Kingdom is not in the Irish cohort, though both intervened: "
             "including the metropole would swamp the cohort with elites whose regime was "
             "never at stake.", "",
             "Country is coded as present-day citizenship, which is the only country "
             "field the database carries. That is anachronistic by construction. Germany "
             "stands for the German states, Italy for the Italian ones, and the successor "
             "republics stand for the territory of the Russian empire.", "",
             "## Which revolutions are here", "",
             f"A revolution is kept when its cohort holds at least {MIN_ELITES} elites "
             f"and at least {MIN_TWO_SECTOR} who span two sectors, which is the floor "
             "the pair estimator needs. Every revolution considered is listed, kept or "
             "not.", "",
             "| Revolution | Years | Elites | Two sectors | Kept |",
             "|---|---|---:|---:|---|"]
    for _, r in index.iterrows():
        lines.append(f"| {r['revolution']} | {r['window_start']}-{r['window_end']} | "
                     f"{r['n_elites']:,} | {r['n_two_sector']:,} | "
                     f"{'yes' if r['kept'] else 'no, ' + r['reason']} |")
    lines += ["", "## Top-level files", "",
              "| File | Contents |", "|---|---|",
              "| `revolutions_index.csv` | the table above, with the full country lists |",
              "| `cohort_summary.csv` | one row per kept revolution: counts, coverage, age bands |",
              "| `cohort_composition.csv` | sector and group shares, every cohort stacked |",
              "| `cohort_group_pairs.csv` | the 21 group-pair scores, every cohort stacked |",
              "", "## Caveats", "",
              "These are descriptive cohorts. Living through a revolution is not an "
              "assignment, the windows are conventional dates, and the birth-cohort "
              "series inside each folder is a comparison, not a control. Cohorts also "
              "overlap where windows are close in the same countries: the Xinhai and "
              "Chinese Communist cohorts share people, as do the Russian and German ones "
              "through Poland and Austria. `scripts/14_shock_event_study.py` is where the "
              "causal question is put.", "",
              "Coverage of the database rises steeply with time, so the modern cohorts "
              "are larger than the early modern ones by a wide margin and the two are "
              "not comparable in size. Association scores are refitted inside each "
              "cohort, which makes them comparable in a way the raw counts are not.", ""]
    return "\n".join(lines)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN, compression="gzip", low_memory=False)
    df["group_main"] = df["sector_main"].map(GROUP)
    df["group_second"] = df["sector_second"].map(GROUP)
    df.loc[df["group_second"] == df["group_main"], "group_second"] = np.nan

    named = set()
    for _, _, _, _, countries, _ in REVOLUTIONS:
        named.update(countries)
    missing = sorted(c for c in named if c not in set(df["country"].dropna()))
    if missing:
        print(f"country labels not present in the source: {missing}")

    index_rows, summaries, comps, pair_frames = [], [], [], []
    for rev in REVOLUTIONS:
        slug, name, y0, y1, countries, _ = rev
        cohort = cohort_of(rev, df)
        two_sector = int((cohort["sector_second"].notna()
                          & (cohort["sector_second"] != cohort["sector_main"])).sum())
        kept = len(cohort) >= MIN_ELITES and two_sector >= MIN_TWO_SECTOR
        reason = ""
        if not kept:
            reason = (f"only {len(cohort):,} elites" if len(cohort) < MIN_ELITES
                      else f"only {two_sector:,} spanning two sectors")
        index_rows.append({"revolution": name, "slug": slug, "window_start": y0,
                           "window_end": y1, "countries": "; ".join(countries),
                           "n_countries": len(countries), "n_elites": len(cohort),
                           "n_two_sector": two_sector, "kept": kept, "reason": reason})
        if not kept:
            print(f"dropped {name}: {reason}")
            continue
        summary, comp, pairs = write_folder(rev, cohort, df)
        summaries.append(summary)
        comps.append(comp)
        if not pairs.empty:
            pair_frames.append(pairs)
        print(f"{name}: {len(cohort):,} elites, {two_sector:,} spanning two sectors")

    index = pd.DataFrame(index_rows).sort_values("n_elites", ascending=False)
    index.to_csv(OUTDIR / "revolutions_index.csv", index=False)
    pd.DataFrame(summaries).to_csv(OUTDIR / "cohort_summary.csv", index=False)
    pd.concat(comps, ignore_index=True).to_csv(OUTDIR / "cohort_composition.csv",
                                               index=False)
    allpairs = pd.concat(pair_frames, ignore_index=True)
    allpairs.to_csv(OUTDIR / "cohort_group_pairs.csv", index=False)
    (OUTDIR / "README.md").write_text(index_readme(index))

    print(f"\n{len(summaries)} of {len(REVOLUTIONS)} revolutions kept, "
          f"{index.loc[index['kept'], 'n_elites'].sum():,} elites in total")
    sparse = int(allpairs["sparse_cell"].sum())
    print(f"{sparse} of {len(allpairs)} cells hold fewer than {SPARSE_CELL} elites "
          f"and are flagged sparse; the counts below drop them")
    print("\nhow each pair reads across the kept cohorts")
    solid = allpairs[~allpairs["sparse_cell"]]
    tab = (solid.groupby("pair")["direction"].value_counts().unstack(fill_value=0)
           .reindex(columns=["associated", "dissociated", "not distinguishable"],
                    fill_value=0))
    tab["cohorts"] = tab.sum(axis=1)
    tab["mean_assoc"] = solid.groupby("pair")["assoc_log2"].mean().round(2)
    print(tab.sort_values("mean_assoc", ascending=False).to_string())


if __name__ == "__main__":
    main()
