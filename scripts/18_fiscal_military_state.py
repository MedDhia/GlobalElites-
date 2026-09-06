"""Testing Brewer's fiscal-military state, 1688-1783.

The thesis
----------
Brewer, "The Sinews of Power" (1989): after 1688 the English state built a fiscal
and administrative apparatus without European precedent. A salaried, meritocratic
Excise in place of tax farming and venal office; public credit and a national debt
underwritten by Parliament; an army and navy paid for by taxation and borrowing.
The comparison is explicit and is with France, where office stayed venal and
patrimonial.

Why this is testable where the military revolution was not. Brewer's claim is
country-specific, dated, and names its counterfactual, so there is a treated unit
and a donor pool instead of a Europe-wide period with no untreated units.

Design
------
One treated unit with a long pre-period, so the decision tree points at the
synthetic control family. Four donors and five pre-cohorts is too few for a
synthetic control to mean anything, since the fit would be mechanical, so the
estimator is a plain difference in differences with two placebo distributions:

  in space  each donor is treated in turn and Britain's effect is ranked among
            the five. With four donors the smallest p this can return is 0.20,
            which is a limit of the panel and is reported as one.
  in pairs  Britain's effect on the six predicted pairs is ranked against its
            effect on the fifteen the thesis says nothing about.

Sectors are coarsened to seven groups so that a country and cohort cell has enough
cases to fit the model. The coarsening is chosen to preserve what is particular to
Brewer's predictions: politics and administration stay separate, since their fusion is the
claim, and business stays separate from everything, since public credit is what
distinguishes this thesis from the military revolution.

Exposure. A cohort born in b has its main career in [b+25, b+65]. PRE is a career
closed before 1688 (cohorts to 1600), EXPOSED is a career falling entirely inside
1688-1783 (cohorts 1675 and 1700), POST is a career opening after 1783 (cohorts
from 1775). Everything else is transition and is held out.

Outputs (data/processed/fiscal_military/):
    predictions.csv                 the pre-specified predictions
    country_pairs_by_cohort.csv     the series everything is computed from
    phase_contrasts.csv             each unit's PRE to EXPOSED and EXPOSED to POST change
    did_results.csv                 Britain against the donor pool, per pair
    placebo_in_space.csv            each donor treated in turn
    placebo_in_pairs.csv            predicted against non-predicted pairs
    britain_vs_france.csv           the head-to-head Brewer actually draws
    placebo_in_time.csv             the same design on a window 200 years earlier
    composition_placebo.csv         what the recorded population does across the phases
"""

import math
import pathlib

import numpy as np
import pandas as pd

from assoc_core import pair_statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "fiscal_military"

# Seven groups. Politics and administration are kept apart because their fusion is
# the claim; business is kept apart because public credit is what separates this
# thesis from the military revolution. Sport is dropped as negligible before 1800.
GROUP = {
    "Politics": "Politics",
    "Administration & Law": "Administration & Law",
    "Military": "Military",
    "Big business": "Business",
    "Small business": "Business",
    "Nobility": "Nobility & Kinship",
    "Kinship": "Nobility & Kinship",
    "Religion": "Religion",
    "Academia": "Learning & Culture",
    "Exploration & Invention": "Learning & Culture",
    "Culture (core)": "Learning & Culture",
    "Culture (periphery)": "Learning & Culture",
}
GROUP_ORDER = ["Politics", "Administration & Law", "Military", "Business",
               "Nobility & Kinship", "Religion", "Learning & Culture"]

WINDOW = (1688, 1783)
CAREER = (25, 65)
COHORT = 25
MIN_PAIRS = 120
TREATED = "United Kingdom"
DONORS = ["France", "Germany", "Spain", "Italy"]
N_PERM = 100_000
RNG = np.random.default_rng(20260902)

# ---------------------------------------------------------------------------
# Written before the series was computed.
# ---------------------------------------------------------------------------
PREDICTIONS = [
    ("Politics + Administration & Law", +1,
     "Office-holding becomes the substance of rule: the Excise as a salaried, "
     "examined service", "Brewer 1989 ch. 3"),
    ("Administration & Law + Military", +1,
     "The fiscal apparatus exists to fund war; revenue and command are one system",
     "Brewer 1989 ch. 2"),
    ("Politics + Business", +1,
     "Public credit ties Parliament to the moneyed interest", "Brewer 1989 ch. 4"),
    ("Administration & Law + Business", +1,
     "The Treasury and the Bank: debt management becomes an administrative craft",
     "Brewer 1989 ch. 4; Dickson 1967"),
    ("Military + Business", +1,
     "Contracting, victualling and naval supply", "Brewer 1989 ch. 2; Baugh 1965"),
    ("Administration & Law + Nobility & Kinship", -1,
     "Salaried merit replaces venal and patrimonial office, the sharpest contrast "
     "Brewer draws with France", "Brewer 1989 ch. 3"),
]
CONTESTED = [("Politics + Nobility & Kinship",
              "Brewer has the apparatus growing underneath an aristocratic "
              "political order, so the tie could hold or loosen")]


def canonical(pair):
    a, b = pair.split(" + ")
    order = {s: k for k, s in enumerate(GROUP_ORDER)}
    lo, hi = sorted([a, b], key=lambda s: order[s])
    return f"{lo} + {hi}"


def phase(cohort, window=WINDOW):
    if cohort + CAREER[1] < window[0]:
        return "pre"
    if cohort + CAREER[0] >= window[0] and cohort + CAREER[1] <= window[1]:
        return "exposed"
    if cohort + CAREER[0] > window[1]:
        return "post"
    return "transition"


def weighted_mean(values, se):
    se = np.asarray(se, dtype=float)
    w = np.divide(1.0, se ** 2, out=np.zeros_like(se), where=se > 0)
    ok = np.isfinite(values) & (w > 0)
    if ok.sum() == 0:
        return np.nan
    return float(np.average(np.asarray(values)[ok], weights=w[ok]))


def phase_change(series, a, b):
    """Change in a pair's association between two phases."""
    x = series[series["phase"] == a]
    y = series[series["phase"] == b]
    if x.empty or y.empty:
        return np.nan
    return weighted_mean(y["assoc_log2"], y["assoc_boot_se"]) - \
        weighted_mean(x["assoc_log2"], x["assoc_boot_se"])


def build(df, window=WINDOW, min_pairs=MIN_PAIRS):
    frames = []
    for country in [TREATED] + DONORS:
        sub = df[df["country"] == country]
        for cohort in sorted(sub["cohort"].unique()):
            cell = sub[sub["cohort"] == cohort]
            got = pair_statistics(cell, GROUP_ORDER, "group_main", "group_second",
                                  "cell", f"{country}|{cohort}",
                                  min_units=min_pairs, rng=RNG)
            if not got.empty:
                got["country"] = country
                got["cohort"] = cohort
                frames.append(got.rename(columns={"cat_a": "group_a", "cat_b": "group_b"}))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not out.empty:
        out = out.drop(columns=["period_type", "period"])
        out["phase"] = out["cohort"].map(lambda c: phase(c, window))
    return out


def contrasts(series, a="pre", b="exposed"):
    rows = []
    for (country, pair), grp in series.groupby(["country", "pair"]):
        rows.append({"country": country, "pair": pair,
                     "change": phase_change(grp, a, b),
                     f"n_{a}": int((grp["phase"] == a).sum()),
                     f"n_{b}": int((grp["phase"] == b).sum())})
    return pd.DataFrame(rows)


def did_table(cont, preds, treated=TREATED, donors=None):
    donors = donors or DONORS
    piv = cont.pivot(index="pair", columns="country", values="change")
    have = [c for c in donors if c in piv.columns]
    out = pd.DataFrame({
        "pair": piv.index,
        "treated_change": piv[treated].to_numpy() if treated in piv else np.nan,
        "donor_mean_change": piv[have].mean(axis=1).to_numpy(),
        "n_donors": piv[have].notna().sum(axis=1).to_numpy(),
    })
    out["did"] = out["treated_change"] - out["donor_mean_change"]
    out = out.merge(preds[["pair", "direction", "claim", "source"]], on="pair", how="left")
    out["signed_did"] = out["did"] * out["direction"]
    return out


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    preds = pd.DataFrame(PREDICTIONS, columns=["pair", "direction", "claim", "source"])
    preds["pair"] = preds["pair"].map(canonical)
    preds.to_csv(OUTDIR / "predictions.csv", index=False)
    contested = [canonical(p) for p, _ in CONTESTED]

    df = pd.read_csv(IN, compression="gzip", low_memory=False)
    df["group_main"] = df["sector_main"].map(GROUP)
    df["group_second"] = df["sector_second"].map(GROUP)
    df = df[df["group_main"].notna() & df["birth"].between(1400, 1849)].copy()
    df["cohort"] = (df["birth"] // COHORT).astype(int) * COHORT
    # A person whose two sectors land in one group carries no cross-group pair.
    df.loc[df["group_second"] == df["group_main"], "group_second"] = np.nan

    series = build(df)
    series.to_csv(OUTDIR / "country_pairs_by_cohort.csv", index=False)
    cells = series.groupby(["country", "phase"])["cohort"].nunique().unstack().fillna(0)
    print("cohorts per unit and phase")
    print(cells.astype(int).to_string())

    cont = contrasts(series, "pre", "exposed")
    cont_post = contrasts(series, "exposed", "post")
    cont_post = cont_post.rename(columns={"change": "change_exposed_to_post"})
    allc = cont.merge(cont_post[["country", "pair", "change_exposed_to_post"]],
                      on=["country", "pair"], how="left")
    allc.to_csv(OUTDIR / "phase_contrasts.csv", index=False)

    did = did_table(cont, preds)
    did["is_predicted"] = did["direction"].notna()
    did["is_contested"] = did["pair"].isin(contested)
    did = did.sort_values("did", ascending=False)
    did.to_csv(OUTDIR / "did_results.csv", index=False)

    pr = did[did["is_predicted"]]
    n_right = int((np.sign(pr["did"]) == pr["direction"]).sum())
    p_sign = sum(math.comb(len(pr), i) for i in range(n_right, len(pr) + 1)) / 2 ** len(pr)
    obs = float(pr["signed_did"].mean())
    print(f"\nBritain against the donor pool, PRE to EXPOSED: "
          f"{n_right} of {len(pr)} predictions in the right direction, sign test p = {p_sign:.3f}")
    print(did[["pair", "direction", "treated_change", "donor_mean_change", "did"]]
          .round(3).to_string(index=False))

    # ---- placebo in pairs ---------------------------------------------------
    pool = did["did"].dropna().to_numpy()
    draws = RNG.choice(pool, size=(N_PERM, len(pr)), replace=True)
    signs = RNG.choice([-1, 1], size=(N_PERM, len(pr)))
    null = (draws * signs).mean(axis=1)
    p_pairs = float((np.sum(null >= obs) + 1) / (N_PERM + 1))
    pd.DataFrame([{"observed_mean_signed_did": obs, "n_predictions": len(pr),
                   "n_correct_sign": n_right, "p_sign_test": p_sign,
                   "p_permutation_over_pairs": p_pairs,
                   "n_pairs_in_pool": len(pool)}]).to_csv(
        OUTDIR / "placebo_in_pairs.csv", index=False)
    print(f"placebo over pairs: mean signed effect {obs:+.3f}, p = {p_pairs:.3f}")

    # ---- placebo in space ---------------------------------------------------
    rows = []
    units = [TREATED] + DONORS
    for unit in units:
        others = [u for u in units if u != unit]
        d = did_table(cont, preds, treated=unit, donors=others)
        d = d[d["direction"].notna()]
        if d["did"].notna().sum() == 0:
            continue
        rows.append({"unit": unit, "mean_signed_did": float(d["signed_did"].mean()),
                     "n_correct_sign": int((np.sign(d["did"]) == d["direction"]).sum()),
                     "n_predictions": int(d["direction"].notna().sum())})
    space = pd.DataFrame(rows).sort_values("mean_signed_did", ascending=False)
    space["rank"] = np.arange(1, len(space) + 1)
    space["p_in_space"] = space["rank"] / len(space)
    space.to_csv(OUTDIR / "placebo_in_space.csv", index=False)
    print("\nplacebo in space, each unit treated in turn")
    print(space.round(3).to_string(index=False))

    # ---- Britain against France --------------------------------------------
    bf = did_table(cont, preds, treated=TREATED, donors=["France"])
    bf = bf.rename(columns={"donor_mean_change": "france_change",
                            "did": "britain_minus_france"})
    bf["is_contested"] = bf["pair"].isin(contested)
    bf.sort_values("britain_minus_france", ascending=False).to_csv(
        OUTDIR / "britain_vs_france.csv", index=False)
    print("\nBritain against France")
    print(bf[bf["direction"].notna() | bf["is_contested"]]
          [["pair", "direction", "treated_change", "france_change", "britain_minus_france"]]
          .round(3).to_string(index=False))

    # ---- persistence --------------------------------------------------------
    did_post = did_table(cont_post.rename(columns={"change_exposed_to_post": "change"}),
                         preds)
    did_post = did_post[did_post["direction"].notna()]
    print("\npersistence, EXPOSED to POST (a reversal would show as the opposite sign)")
    print(did_post[["pair", "direction", "treated_change", "donor_mean_change", "did"]]
          .round(3).to_string(index=False))
    did_post.to_csv(OUTDIR / "persistence.csv", index=False)

    # ---- placebo in time ----------------------------------------------------
    # A window 200 years earlier needs pre-exposure cohorts born before 1423, and
    # no unit clears the case floor that early, so the test is not estimable and
    # is recorded as such instead of being reported as a null.
    shifted = (WINDOW[0] - 200, WINDOW[1] - 200)
    ser_t = build(df, window=shifted)
    cont_t = contrasts(ser_t, "pre", "exposed") if not ser_t.empty else pd.DataFrame()
    did_t = did_table(cont_t, preds) if not cont_t.empty else pd.DataFrame()
    dt = did_t[did_t["direction"].notna() & did_t["did"].notna()] if not did_t.empty \
        else pd.DataFrame()
    if len(dt):
        n_t = int((np.sign(dt["did"]) == dt["direction"]).sum())
        rec = {"window": f"{shifted[0]}-{shifted[1]}", "estimable": True,
               "n_correct_sign": n_t, "n_predictions": len(dt),
               "mean_signed_did": float(dt["signed_did"].mean()), "note": ""}
        print(f"\nplacebo in time, window {shifted[0]}-{shifted[1]}: "
              f"{n_t} of {len(dt)} correct, mean signed effect "
              f"{dt['signed_did'].mean():+.3f}")
    else:
        with_pre = sorted(ser_t.loc[ser_t["phase"] == "pre", "country"].unique()) \
            if not ser_t.empty else []
        rec = {"window": f"{shifted[0]}-{shifted[1]}", "estimable": False,
               "n_correct_sign": np.nan, "n_predictions": 0,
               "mean_signed_did": np.nan,
               "note": (f"needs cohorts born before 1423. The treated unit has no "
                        f"pre-exposure cell there, since Britain's 1400 cohort holds "
                        f"fewer than the {MIN_PAIRS} cross-group pairs the model needs. "
                        f"Units that do have one: {', '.join(with_pre) or 'none'}")}
        print(f"\nplacebo in time, window {shifted[0]}-{shifted[1]}: not estimable, "
              f"{rec['note']}")
    pd.DataFrame([rec]).to_csv(OUTDIR / "placebo_in_time.csv", index=False)

    # ---- composition placebo ------------------------------------------------
    rows = []
    for country in [TREATED] + DONORS:
        sub = df[df["country"] == country].copy()
        sub["phase"] = sub["cohort"].map(lambda c: phase(c))
        for ph in ("pre", "exposed", "post"):
            s = sub[sub["phase"] == ph]
            if s.empty:
                continue
            rec = {"country": country, "phase": ph, "n_elites": len(s),
                   "log_n_elites": float(np.log(len(s)))}
            for g in GROUP_ORDER:
                holds = (s["group_main"] == g) | (s["group_second"] == g)
                rec[f"share_{g}"] = float(holds.mean())
            rows.append(rec)
    comp = pd.DataFrame(rows)
    comp.to_csv(OUTDIR / "composition_placebo.csv", index=False)
    uk = comp[comp["country"] == TREATED].set_index("phase")
    print("\ncomposition of the British record by phase")
    print(uk[[c for c in uk.columns if c.startswith("share_")] + ["n_elites"]]
          .round(3).to_string())


if __name__ == "__main__":
    main()
