"""Event study of dated shocks on the association between fields of elite power.

Design
------
Staggered adoption with heterogeneous timing, so the estimator is a
Callaway-Sant'Anna style group-time average treatment effect. For a group of
countries first exposed at cohort g and an event time e, ATT(g, e) compares the
change in the outcome from the last pre-exposure cohort (e = -1) to cohort
g + e, between those countries and countries not yet exposed at that cohort
plus those never exposed inside the window. Cell-level differences are weighted
by the inverse of their bootstrap variance. ATT(e) aggregates over groups.

Inference
---------
Sixteen countries and four never-treated ones is far too few clusters for
standard errors clustered on country, so inference is randomization inference: the
multiset of shock years is reassigned at random across the panel countries and
the whole estimator is recomputed, N_PERM times. The reported p-value is the
share of draws whose |ATT(e)| reaches the observed one. This tests the sharp
null of no effect for any country and is the only inference this panel supports.

Falsification
-------------
1. Pre-exposure event times. An effect at e = -3 or e = -2 is a failure.
2. Composition placebos. The same estimator on the log number of recorded
   elites, the crossing rate, and each domain's share. A shock that moves these
   as much as it moves the association scores is moving the record, not power.
3. Placebo in time. Every shock shifted 100 years earlier.
4. Leave one country out.

Outputs (data/processed/shocks/):
    event_study_att.csv          ATT(e) per shock type and pair, with RI p-values
    event_study_group_time.csv   the underlying ATT(g, e) and what they rest on
    event_study_placebo.csv      the same estimator on the composition outcomes
    event_study_placebo_time.csv shocks shifted 100 years earlier
    event_study_loo.csv          leave-one-country-out on the headline estimates
"""

import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
SD = ROOT / "data" / "processed" / "shocks"

COHORT = 25
EVENT_TIMES = [-3, -2, 0, 1, 2, 3]      # -1 is the reference
LAG_COL = "first_treated_cohort_main"
N_PERM = 2000
RNG = np.random.default_rng(20260902)


def to_matrices(panel, value="value", weight="w"):
    """Country by cohort matrices, built once so the permutation loop is cheap."""
    countries = sorted(panel["country"].unique())
    cohorts = sorted(panel["cohort"].unique())
    ci = {c: k for k, c in enumerate(countries)}
    ti = {t: k for k, t in enumerate(cohorts)}
    y = np.full((len(countries), len(cohorts)), np.nan)
    w = np.zeros_like(y)
    for c, t, v, ww in zip(panel["country"], panel["cohort"],
                           panel[value], panel[weight]):
        y[ci[c], ti[t]] = v
        w[ci[c], ti[t]] = ww
    return countries, cohorts, ci, ti, y, w


def att_by_event(mats, groups, controls_never, collect=False):
    """ATT(g, e) and its aggregate over an already-built matrix panel.

    `groups` maps country -> first treated cohort; countries absent from it are
    never treated inside the window.
    """
    countries, cohorts, ci, ti, y, w = mats
    rows = []
    for g in sorted(set(groups.values())):
        ref = g - COHORT
        if ref not in ti:
            continue
        r = ti[ref]
        treated = [c for c, gg in groups.items()
                   if gg == g and c in ci and np.isfinite(y[ci[c], r])]
        if not treated:
            continue
        for e in EVENT_TIMES:
            t = g + e * COHORT
            if t not in ti:
                continue
            k = ti[t]
            tr = [c for c in treated if np.isfinite(y[ci[c], k])]
            ct = [c for c in countries
                  if (c in controls_never or groups.get(c, np.inf) > t)
                  and c not in treated
                  and np.isfinite(y[ci[c], r]) and np.isfinite(y[ci[c], k])]
            if not tr or len(ct) < 2:
                continue

            def delta(units):
                idx = [ci[u] for u in units]
                d = y[idx, k] - y[idx, r]
                # The variance of a within-country difference is the sum of the
                # two cell variances, so the weight combines them harmonically.
                inv = np.divide(1.0, w[idx, k], out=np.full(len(idx), np.inf),
                                where=w[idx, k] > 0)
                inv = inv + np.divide(1.0, w[idx, r],
                                      out=np.full(len(idx), np.inf),
                                      where=w[idx, r] > 0)
                ww = np.divide(1.0, inv, out=np.zeros(len(idx)),
                               where=np.isfinite(inv) & (inv > 0))
                return (float(np.average(d, weights=ww)) if ww.sum() > 0
                        else float(np.mean(d)))

            rec = {"group": g, "event_time": e, "cohort": t,
                   "n_treated": len(tr), "n_control": len(ct),
                   "att": delta(tr) - delta(ct), "weight": len(tr)}
            if collect:
                rec["treated_countries"] = ",".join(sorted(tr))
            rows.append(rec)
    if not rows:
        return pd.DataFrame(), pd.DataFrame()
    gt = pd.DataFrame(rows)
    agg = (gt.groupby("event_time")
           .apply(lambda d: pd.Series({
               "att": float(np.average(d["att"], weights=d["weight"])),
               "n_groups": len(d),
               "n_treated_cells": int(d["n_treated"].sum()),
               "min_controls": int(d["n_control"].min())}),
                  include_groups=False)
           .reset_index())
    return gt, agg


def randomization_p(mats, groups, observed, n_perm=N_PERM, rng=RNG):
    """Share of random reassignments of the shock years reaching |observed|."""
    countries = mats[0]
    years = list(groups.values())
    draws = {e: [] for e in observed["event_time"]}
    for _ in range(n_perm):
        picked = list(rng.choice(countries, size=len(years), replace=False))
        fake = dict(zip(picked, rng.permutation(years)))
        never = set(countries) - set(picked)
        _, agg = att_by_event(mats, fake, never)
        if agg.empty:
            continue
        got = dict(zip(agg["event_time"], agg["att"]))
        for e in draws:
            if e in got:
                draws[e].append(got[e])
    out = []
    for _, r in observed.iterrows():
        d = np.array(draws[r["event_time"]])
        p = ((np.sum(np.abs(d) >= abs(r["att"])) + 1) / (len(d) + 1)
             if len(d) else np.nan)
        lo, hi = (np.percentile(d, [2.5, 97.5]) if len(d) else (np.nan, np.nan))
        out.append({"event_time": r["event_time"], "p_value_ri": p,
                    "null_sd": float(np.std(d)) if len(d) else np.nan,
                    "null_ci_low": lo, "null_ci_high": hi, "n_draws": len(d)})
    return observed.merge(pd.DataFrame(out), on="event_time")


def build_groups(shocks, shock_type, panel_countries, offset=0):
    sub = shocks[(shocks["type"] == shock_type) & shocks["in_panel"]]
    groups = {}
    for _, r in sub.iterrows():
        if r["country"] not in panel_countries:
            continue
        groups[r["country"]] = int(r[LAG_COL]) + offset
    never = set(panel_countries) - set(shocks.loc[shocks["in_panel"], "country"])
    return groups, never


def run(panel_long, shocks, panel_countries, label, offset=0, do_ri=True):
    results, group_times = [], []
    for shock_type in sorted(shocks.loc[shocks["in_panel"], "type"].unique()):
        groups, never = build_groups(shocks, shock_type, panel_countries, offset)
        if len(groups) < 2:
            continue
        for outcome, mats in panel_long.items():
            gt, agg = att_by_event(mats, groups, never, collect=True)
            if agg.empty:
                continue
            if do_ri:
                agg = randomization_p(mats, groups, agg)
            agg.insert(0, "outcome", outcome)
            agg.insert(0, "shock_type", shock_type)
            agg.insert(0, "spec", label)
            results.append(agg)
            gt.insert(0, "outcome", outcome)
            gt.insert(0, "shock_type", shock_type)
            gt.insert(0, "spec", label)
            group_times.append(gt)
    res = pd.concat(results, ignore_index=True) if results else pd.DataFrame()
    gts = pd.concat(group_times, ignore_index=True) if group_times else pd.DataFrame()
    return res, gts


def main() -> None:
    pairs = pd.read_csv(SD / "shock_panel_pairs.csv")
    placebo = pd.read_csv(SD / "shock_panel_placebo.csv")
    shocks = pd.read_csv(SD / "shock_list.csv")
    panel_countries = sorted(pairs["country"].unique())

    # Countries with no pre-exposure cohort cannot enter an event study at all.
    dropped = shocks[shocks["in_panel"] & (shocks["n_pre_main"] == 0)]["country"].tolist()
    print(f"countries with a shock but no pre-exposure cohort, so unusable: "
          f"{', '.join(dropped) or 'none'}")

    pair_long, pair_frames = {}, {}
    for pair, grp in pairs.groupby("pair"):
        f = grp[["country", "cohort", "assoc_log2", "assoc_boot_se"]].copy()
        f["value"] = f["assoc_log2"]
        f["w"] = 1.0 / f["assoc_boot_se"] ** 2
        pair_frames[pair] = f[["country", "cohort", "value", "w"]]
        pair_long[pair] = to_matrices(pair_frames[pair])

    print("\nmain event study")
    res, gts = run(pair_long, shocks, panel_countries, "main")
    res.to_csv(SD / "event_study_att.csv", index=False)
    gts.to_csv(SD / "event_study_group_time.csv", index=False)
    print(res[["shock_type", "outcome", "event_time", "att", "n_treated_cells",
               "min_controls", "p_value_ri"]].round(3).to_string(index=False))

    print("\ncomposition placebos")
    pl = placebo[placebo["usable"]].copy()
    placebo_long = {}
    for col in ["log_n_classified", "crossing_rate", "share_political",
                "share_ideational", "share_economic", "share_security"]:
        f = pl[["country", "cohort", col]].rename(columns={col: "value"}).copy()
        # No sampling variance is carried for these, so every cell is equal weight.
        f["w"] = 1.0
        placebo_long[col] = to_matrices(f)
    pres, _ = run(placebo_long, shocks, panel_countries, "placebo_outcome")
    pres.to_csv(SD / "event_study_placebo.csv", index=False)
    print(pres[["shock_type", "outcome", "event_time", "att", "p_value_ri"]]
          .round(3).to_string(index=False))

    print("\nplacebo in time: every shock moved 100 years earlier")
    tres, _ = run(pair_long, shocks, panel_countries, "placebo_time", offset=-100)
    tres.to_csv(SD / "event_study_placebo_time.csv", index=False)
    print(tres[["shock_type", "outcome", "event_time", "att", "p_value_ri"]]
          .round(3).to_string(index=False))

    print("\nleave one country out")
    loo = []
    for shock_type in sorted(shocks.loc[shocks["in_panel"], "type"].unique()):
        groups, never = build_groups(shocks, shock_type, panel_countries)
        for drop in panel_countries:
            g2 = {k: v for k, v in groups.items() if k != drop}
            n2 = {c for c in never if c != drop}
            if len(g2) < 2:
                continue
            for outcome, pair in pair_frames.items():
                f2 = pair[pair["country"] != drop]
                _, agg = att_by_event(to_matrices(f2), g2, n2)
                if agg.empty:
                    continue
                agg.insert(0, "dropped", drop)
                agg.insert(0, "outcome", outcome)
                agg.insert(0, "shock_type", shock_type)
                loo.append(agg)
    pd.concat(loo, ignore_index=True).to_csv(SD / "event_study_loo.csv", index=False)
    print(f"leave-one-out rows: {sum(len(x) for x in loo)}")


if __name__ == "__main__":
    main()
