"""Testing Tilly's coercion and capital paths.

The thesis
----------
Tilly, "Coercion, Capital, and European States, AD 990-1992" (1990): rulers had to
extract the means of war from whoever held them, and what they held determined the
state that resulted. Where capital was concentrated in cities and merchants, rulers
bargained and built negotiated, contractual structures. Where capital was thin,
they coerced directly, absorbed landlords into the officer corps and built large
coercive apparatuses. Between the two lies capitalized coercion, the combination
that produced the national state.

Why this suits the data. The claim is typological and cross-sectional, so there is
no dating problem and no exposure lag. What it predicts is an ordering of countries,
which is what this repository measures country by country.

What this is and is not. Countries are not assigned their endowment of cities and
capital at random; that endowment is Tilly's explanatory variable and it is
inherited from centuries of geography and trade. So nothing here identifies a
causal effect. What can be tested is whether the ordering Tilly predicts is the
ordering the record shows, against a null in which the path labels are shuffled
across countries.

Design
------
Sectors are coarsened to the same seven groups used for the fiscal-military test,
and association scores are refitted inside each country and era. The main era is
1600-1799, where the panel is balanced at five countries per path. Ordering is
tested with a Jonckheere-Terpstra statistic against a permutation null over the
path labels, which is the right null when there are five countries per cell.

Outputs (data/processed/tilly/):
    path_coding.csv             the coded paths, with the alternative coding
    country_era_pairs.csv       the series everything is computed from
    predictions.csv             the pre-specified orderings
    ordering_tests.csv          Jonckheere-Terpstra and its permutation p, per era
    group_means.csv             each path's mean on each predicted quantity
    coercion_index.csv          the composite index, country by country and era
    leave_one_out.csv           the composite test dropping each country
    alternative_coding.csv      the same tests under the alternative coding
    manipulation_check.csv      whether the coded paths differ in sector composition
"""

import itertools
import pathlib

import numpy as np
import pandas as pd

from assoc_core import bh, pair_statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "tilly"

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

PATHS = ["capital-intensive", "capitalized coercion", "coercion-intensive"]
ERAS = ["1400-1599", "1600-1799", "1800-1899", "1900-2020"]
MAIN_ERA = "1600-1799"
MIN_PAIRS = 150
N_PERM = 100_000
RNG = np.random.default_rng(20260902)

# ---------------------------------------------------------------------------
# Tilly's own examples, mapped onto the modern states the source codes. The
# mapping is lossy and the lossiest case is Italy, which merges Venice and Genoa,
# his capital-intensive exemplars, with the papal and southern states. Debatable
# cases are moved in the alternative coding and each country is dropped in turn.
# ---------------------------------------------------------------------------
CODING = {
    "Netherlands": "capital-intensive",      # the Dutch Republic, his central case
    "Italy": "capital-intensive",            # Venice and Genoa; see the caveat above
    "Switzerland": "capital-intensive",
    "Belgium": "capital-intensive",          # the Flemish and Brabant city belt
    "Portugal": "capital-intensive",         # a commercial seaboard state
    "France": "capitalized coercion",        # his exemplar of the combination
    "United Kingdom": "capitalized coercion",
    "Germany": "capitalized coercion",       # Brandenburg-Prussia, coercive early and combined later
    "Spain": "capitalized coercion",
    "Denmark": "capitalized coercion",
    "Russia": "coercion-intensive",          # his exemplar of coercion
    "Poland": "coercion-intensive",
    "Hungary": "coercion-intensive",
    "Sweden": "coercion-intensive",          # thinly urbanised, large army
    "Austria": "coercion-intensive",
    "Romania": "coercion-intensive",
    "Turkey": "coercion-intensive",
}
# Denmark and Sweden are the two Tilly is least explicit about, and Germany changes
# path across his period. The alternative coding moves all three.
ALTERNATIVE = dict(CODING)
ALTERNATIVE.update({"Denmark": "capital-intensive", "Sweden": "capitalized coercion",
                    "Germany": "coercion-intensive"})

# ---------------------------------------------------------------------------
# Written before the series was computed. `order` runs from the path predicted to
# be lowest to the path predicted to be highest.
# ---------------------------------------------------------------------------
PREDICTIONS = [
    ("Politics + Military", ["capital-intensive", "capitalized coercion", "coercion-intensive"],
     "Direct rule through armed force where capital is thin"),
    ("Politics + Business", ["coercion-intensive", "capitalized coercion", "capital-intensive"],
     "Rulers bargain with, and are drawn from, merchant oligarchies where capital is thick"),
    ("Military + Nobility & Kinship", ["capital-intensive", "capitalized coercion", "coercion-intensive"],
     "Coercion-intensive rulers coopt landlords into the officer corps"),
    ("Administration & Law + Business", ["coercion-intensive", "capitalized coercion", "capital-intensive"],
     "Negotiated, contractual, city-based administration"),
]
COMPOSITE = ("coercion index",
             ["capital-intensive", "capitalized coercion", "coercion-intensive"],
             "assoc(Politics + Military) minus assoc(Politics + Business): Tilly's "
             "axis in one number")


def canonical(pair):
    a, b = pair.split(" + ")
    order = {s: k for k, s in enumerate(GROUP_ORDER)}
    lo, hi = sorted([a, b], key=lambda s: order[s])
    return f"{lo} + {hi}"


def jonckheere(values, labels, order):
    """Jonckheere-Terpstra statistic for an ordered alternative across groups."""
    groups = [np.asarray([v for v, l in zip(values, labels) if l == g], dtype=float)
              for g in order]
    total = 0.0
    for i, j in itertools.combinations(range(len(groups)), 2):
        a, b = groups[i], groups[j]
        if a.size == 0 or b.size == 0:
            continue
        total += float((b[:, None] > a[None, :]).sum()
                       + 0.5 * (b[:, None] == a[None, :]).sum())
    return total


def ordering_test(frame, value_col, order, n_perm=N_PERM, rng=RNG):
    """Observed Jonckheere-Terpstra and its permutation p over path labels."""
    f = frame.dropna(subset=[value_col])
    if f["path"].nunique() < 2 or len(f) < 6:
        return None
    values = f[value_col].to_numpy()
    labels = f["path"].to_numpy()
    obs = jonckheere(values, labels, order)
    null = np.empty(n_perm)
    for k in range(n_perm):
        null[k] = jonckheere(values, rng.permutation(labels), order)
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    means = f.groupby("path")[value_col].mean()
    ordered = [means.get(g, np.nan) for g in order]
    monotone = all(a <= b for a, b in zip(ordered[:-1], ordered[1:])
                   if np.isfinite(a) and np.isfinite(b))
    return {"jt": obs, "jt_null_mean": float(null.mean()), "p_permutation": p,
            "n_countries": len(f), "means_in_predicted_order": ordered,
            "monotone_as_predicted": bool(monotone)}


def build(df, coding):
    frames = []
    for country in sorted(coding):
        sub = df[df["country"] == country]
        for era in ERAS:
            cell = sub[sub["era"] == era]
            got = pair_statistics(cell, GROUP_ORDER, "group_main", "group_second",
                                  "cell", f"{country}|{era}", min_units=MIN_PAIRS, rng=RNG)
            if not got.empty:
                got["country"] = country
                got["era"] = era
                frames.append(got.rename(columns={"cat_a": "group_a", "cat_b": "group_b"}))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return out.drop(columns=["period_type", "period"]) if not out.empty else out


def run_tests(series, coding, label, n_perm=N_PERM):
    preds = [(canonical(p), o, c) for p, o, c in PREDICTIONS]
    rows, means_rows, comp_rows = [], [], []
    for era in ERAS:
        e = series[series["era"] == era]
        if e.empty:
            continue
        wide = e.pivot(index="country", columns="pair", values="assoc_log2")
        wide["path"] = [coding.get(c) for c in wide.index]
        for pair, order, claim in preds:
            if pair not in wide.columns:
                continue
            res = ordering_test(wide.reset_index()[["country", "path", pair]]
                                .rename(columns={pair: "value"}), "value", order,
                                n_perm=n_perm)
            if res is None:
                continue
            rows.append({"coding": label, "era": era, "quantity": pair,
                         "predicted_order": " < ".join(order), "claim": claim,
                         **{k: v for k, v in res.items()
                            if k != "means_in_predicted_order"},
                         **{f"mean_{g}": v for g, v in
                            zip(order, res["means_in_predicted_order"])}})
            for g, v in zip(order, res["means_in_predicted_order"]):
                means_rows.append({"coding": label, "era": era, "quantity": pair,
                                   "path": g, "mean": v})
        pm, pb = canonical("Politics + Military"), canonical("Politics + Business")
        if pm in wide.columns and pb in wide.columns:
            comp = wide[[pm, pb, "path"]].copy()
            comp["value"] = comp[pm] - comp[pb]
            res = ordering_test(comp.reset_index(), "value", COMPOSITE[1], n_perm=n_perm)
            if res is not None:
                rows.append({"coding": label, "era": era, "quantity": COMPOSITE[0],
                             "predicted_order": " < ".join(COMPOSITE[1]),
                             "claim": COMPOSITE[2],
                             **{k: v for k, v in res.items()
                                if k != "means_in_predicted_order"},
                             **{f"mean_{g}": v for g, v in
                                zip(COMPOSITE[1], res["means_in_predicted_order"])}})
            for country, r in comp.iterrows():
                comp_rows.append({"coding": label, "era": era, "country": country,
                                  "path": r["path"], "politics_military": r[pm],
                                  "politics_business": r[pb], "coercion_index": r["value"]})
    return (pd.DataFrame(rows), pd.DataFrame(means_rows), pd.DataFrame(comp_rows))


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"country": c, "path": p, "alternative_path": ALTERNATIVE[c]}
                  for c, p in CODING.items()]).to_csv(OUTDIR / "path_coding.csv",
                                                      index=False)
    pd.DataFrame([{"quantity": canonical(p), "predicted_order": " < ".join(o),
                   "claim": c} for p, o, c in PREDICTIONS]
                 + [{"quantity": COMPOSITE[0], "predicted_order": " < ".join(COMPOSITE[1]),
                     "claim": COMPOSITE[2]}]).to_csv(OUTDIR / "predictions.csv",
                                                     index=False)

    df = pd.read_csv(IN, compression="gzip", low_memory=False)
    df["group_main"] = df["sector_main"].map(GROUP)
    df["group_second"] = df["sector_second"].map(GROUP)
    df.loc[df["group_second"] == df["group_main"], "group_second"] = np.nan
    df = df[df["group_main"].notna() & df["country"].isin(CODING)]

    series = build(df, CODING)
    series.to_csv(OUTDIR / "country_era_pairs.csv", index=False)
    cov = series.groupby(["era", "country"]).size().unstack().notna().sum(axis=1)
    print("countries with an estimable cell per era")
    print(cov.to_string())

    tests, means, comp = run_tests(series, CODING, "main")
    # The pre-specification names 1600-1799 as the main era, so the family for the
    # adjustment is the five tests inside an era, not all twenty.
    tests["q_within_era"] = (tests.groupby("era")["p_permutation"]
                             .transform(lambda v: bh(v.to_numpy())))
    tests["q_all_tests"] = bh(tests["p_permutation"].to_numpy())
    tests.to_csv(OUTDIR / "ordering_tests.csv", index=False)
    means.to_csv(OUTDIR / "group_means.csv", index=False)
    comp.to_csv(OUTDIR / "coercion_index.csv", index=False)
    print(f"\nordering tests, main coding (predicted order low to high)")
    print(tests[["era", "quantity", "n_countries", "monotone_as_predicted",
                 "p_permutation", "q_within_era"]
                + [c for c in tests.columns if c.startswith("mean_")]]
          .round(3).to_string(index=False))

    # ---- leave one country out on the composite ----------------------------
    rows = []
    e = series[series["era"] == MAIN_ERA]
    wide = e.pivot(index="country", columns="pair", values="assoc_log2")
    pm, pb = canonical("Politics + Military"), canonical("Politics + Business")
    for drop in sorted(CODING):
        w = wide.drop(index=drop, errors="ignore")
        if pm not in w.columns or pb not in w.columns:
            continue
        f = pd.DataFrame({"country": w.index,
                          "path": [CODING[c] for c in w.index],
                          "value": (w[pm] - w[pb]).to_numpy()})
        res = ordering_test(f, "value", COMPOSITE[1], n_perm=10_000)
        if res:
            rows.append({"dropped": drop, "jt": res["jt"],
                         "p_permutation": res["p_permutation"],
                         "monotone": res["monotone_as_predicted"],
                         "n_countries": res["n_countries"]})
    loo = pd.DataFrame(rows)
    loo.to_csv(OUTDIR / "leave_one_out.csv", index=False)
    print(f"\nleave one out on the coercion index, {MAIN_ERA}: "
          f"p ranges {loo['p_permutation'].min():.3f} to {loo['p_permutation'].max():.3f}, "
          f"monotone in {int(loo['monotone'].sum())} of {len(loo)} drops")

    # ---- alternative coding -------------------------------------------------
    alt, _, _ = run_tests(series, ALTERNATIVE, "alternative", n_perm=10_000)
    alt.to_csv(OUTDIR / "alternative_coding.csv", index=False)
    print("\nalternative coding (Denmark to capital, Sweden to capitalized, Germany to coercion)")
    print(alt[alt["era"] == MAIN_ERA][["quantity", "monotone_as_predicted",
                                       "p_permutation"]].round(3).to_string(index=False))

    # ---- manipulation check -------------------------------------------------
    rows = []
    for era in ERAS:
        sub = df[df["era"] == era]
        for country in sorted(CODING):
            s = sub[sub["country"] == country]
            if len(s) < 200:
                continue
            rec = {"era": era, "country": country, "path": CODING[country],
                   "n_elites": len(s)}
            for g in GROUP_ORDER:
                holds = (s["group_main"] == g) | (s["group_second"] == g)
                rec[f"share_{g}"] = float(holds.mean())
            rec["military_minus_business"] = rec["share_Military"] - rec["share_Business"]
            rows.append(rec)
    mc = pd.DataFrame(rows)
    mc.to_csv(OUTDIR / "manipulation_check.csv", index=False)
    m = mc[mc["era"] == MAIN_ERA]
    if not m.empty:
        res = ordering_test(m.rename(columns={"military_minus_business": "value"}),
                            "value", COMPOSITE[1], n_perm=10_000)
        print(f"\nmanipulation check, {MAIN_ERA}: does the coding separate countries on "
              f"the military minus business share of elites?")
        print(m.groupby("path")["military_minus_business"].mean().round(3).to_string())
        if res:
            print(f"  ordered as predicted: {res['monotone_as_predicted']}, "
                  f"permutation p = {res['p_permutation']:.3f}")


if __name__ == "__main__":
    main()
