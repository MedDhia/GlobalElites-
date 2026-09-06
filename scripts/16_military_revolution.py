"""Testing the military revolution against the association between fields of power.

The thesis
----------
Roberts (1955) and Parker (1988) date a transformation of European warfare to
roughly 1560-1660: volley fire and drill, the trace italienne, standing armies an
order of magnitude larger than before. Downing (1992), Tilly (1990) and Ertman
(1997) carry it into state formation: paying for those armies built permanent
taxation, a standing bureaucracy and a professional officer corps.

Every one of those claims is a claim about which fields of power get combined in
the same career, which is what this repository measures. So the predictions can be
written down in advance and then tested.

Design
------
This is a period effect. Everyone in Europe lives through the sixteenth and
seventeenth centuries, so there are no untreated units in time. The control group
is instead internal: the 71 sector pairs about which the thesis says nothing. That
controls for anything moving all pairs together, coverage change included, but not
for anything that moves military pairs for a non-military reason. The design is an
interrupted time series with within-sample controls, not an identified experiment,
and it is reported as such.

Exposure. A cohort born in year b has its main career in [b+25, b+65]. A cohort is
PRE if that career closes before the window opens (b + 65 < 1560, so cohorts up to
1475), POST if it opens after the window closes (b + 25 > 1660, so cohorts from
1650), and TRANSITION otherwise. The transition cohorts are held out of the
contrast, not assigned to either side.

Tests
-----
T1  Sign test on the six signed predictions.
T2  Rank of the predicted pairs' signed change among all 78, permutation p.
T3  Timing: does the level-shift scan date each predicted pair inside the window?
T4  Placebo windows: the same contrast centred 200 years earlier and 200 later.
T5  Composition placebo: the same contrast on sector shares and elite counts.
T6  The military sector's mean association and its coreness, cohort by cohort.
T7  Intensity: high against low military-pressure countries, difference in
    differences with permutation inference over which countries sit in which bloc.

Outputs (data/processed/military_revolution/):
    europe_sector_pairs_by_cohort.csv    the series everything is computed from
    predictions.csv                      the pre-specified predictions
    prepost_contrast.csv                 every pair's PRE to POST change
    test_summary.csv                     T1, T2 and the placebo windows
    breaks_predicted_pairs.csv           T3
    composition_placebo.csv              T5
    military_centrality_by_cohort.csv    T6
    bloc_did.csv                         T7
"""

import math
import pathlib

import numpy as np
import pandas as pd

from assoc_core import bh, pair_statistics, quasi_independence
from breaks import break_test
from netstruct import coreness, to_matrix

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "elites_person_level.csv.gz"
OUTDIR = ROOT / "data" / "processed" / "military_revolution"

SECTOR_ORDER = [
    "Politics", "Administration & Law", "Military", "Religion", "Nobility",
    "Kinship", "Big business", "Small business", "Academia",
    "Exploration & Invention", "Culture (core)", "Culture (periphery)",
    "Sport & Games",
]

WINDOW = (1560, 1660)          # Roberts' dating of the military revolution
CAREER = (25, 65)              # a cohort born b has its main career b+25 to b+65
COHORT = 25
COHORT_MIN, COHORT_MAX = 1350, 1849
POST_CAP = 1775                # main specification; 1825 reported as a sensitivity
MIN_PAIRS = 300                # sector-diversified elites needed to fit 78 pairs
N_PERM = 100_000
RNG = np.random.default_rng(20260902)

# ---------------------------------------------------------------------------
# Written before the series was computed. Direction is the sign the thesis
# predicts for the change in log2(observed / expected) from PRE to POST.
# ---------------------------------------------------------------------------
PREDICTIONS = [
    ("Military + Politics", +1,
     "Standing armies are fused to rule; command becomes a route into government",
     "Roberts 1955; Downing 1992"),
    ("Administration & Law + Military", +1,
     "The fiscal-military state: paying for the army builds the office-holding bureaucracy",
     "Parker 1988; Tilly 1990; Ertman 1997"),
    ("Politics + Administration & Law", +1,
     "Permanent taxation turns rule into administration",
     "Tilly 1990; Ertman 1997"),
    ("Military + Exploration & Invention", +1,
     "The trace italienne, ballistics and siegecraft make the military engineer",
     "Parker 1988"),
    ("Military + Big business", +1,
     "Military entrepreneurs, contractors and war finance",
     "Redlich 1964; Parrott 2012"),
    ("Military + Religion", -1,
     "Command secularises as the confessional wars close",
     "Parker 1988; Downing 1992"),
]
# Reported separately and not counted in the sign test, because the literature
# splits on it: professionalisation should loosen the tie between arms and birth
# (Roberts), while absorption of the nobility into the officer corps should
# tighten it (Downing, Ertman).
CONTESTED = [("Military + Nobility",
              "Professionalisation loosens it; absorption of the nobility into the "
              "officer corps tightens it")]

HIGH_PRESSURE = ["France", "Germany", "Spain", "Austria", "Russia"]
LOW_PRESSURE = ["United Kingdom", "Netherlands", "Switzerland", "Sweden"]


def canonical(pair: str) -> str:
    a, b = pair.split(" + ")
    order = {s: k for k, s in enumerate(SECTOR_ORDER)}
    lo, hi = sorted([a, b], key=lambda s: order[s])
    return f"{lo} + {hi}"


def phase(cohort: int) -> str:
    """PRE, POST or TRANSITION, from when the cohort's career sits."""
    if cohort + CAREER[1] < WINDOW[0]:
        return "pre"
    if cohort + CAREER[0] > WINDOW[1]:
        return "post"
    return "transition"


def weighted_mean(values, se):
    se = np.asarray(se, dtype=float)
    w = np.divide(1.0, se ** 2, out=np.zeros_like(se), where=se > 0)
    ok = np.isfinite(values) & np.isfinite(w) & (w > 0)
    if ok.sum() == 0:
        return np.nan, np.nan
    v = np.asarray(values)[ok]
    w = w[ok]
    mean = float(np.average(v, weights=w))
    return mean, float(np.sqrt(1.0 / w.sum()))


def contrast(series, pre_cohorts, post_cohorts):
    """PRE to POST change in a pair's association, with a standard error."""
    pre = series[series["cohort"].isin(pre_cohorts)]
    post = series[series["cohort"].isin(post_cohorts)]
    if pre.empty or post.empty:
        return np.nan, np.nan, 0, 0
    m0, s0 = weighted_mean(pre["assoc_log2"], pre["assoc_boot_se"])
    m1, s1 = weighted_mean(post["assoc_log2"], post["assoc_boot_se"])
    return m1 - m0, float(np.hypot(s0, s1)), len(pre), len(post)


def build_series(frame, cohort_col, label, min_pairs=MIN_PAIRS):
    frames = []
    for cohort in sorted(frame[cohort_col].unique()):
        sub = frame[frame[cohort_col] == cohort]
        got = pair_statistics(sub, SECTOR_ORDER, "sector_main", "sector_second",
                              label, cohort, min_units=min_pairs, rng=RNG)
        if not got.empty:
            frames.append(got.rename(columns={"cat_a": "sector_a", "cat_b": "sector_b"}))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not out.empty:
        out = out.rename(columns={"period": "cohort"}).drop(columns=["period_type"])
    return out


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN, compression="gzip", low_memory=False)
    df["diversified"] = df["diversified"].astype(bool)
    eu = df[(df["region"] == "Europe")
            & df["birth"].between(COHORT_MIN, COHORT_MAX)].copy()
    eu["cohort"] = (eu["birth"] // COHORT).astype(int) * COHORT

    preds = pd.DataFrame(PREDICTIONS, columns=["pair", "direction", "claim", "source"])
    preds["pair"] = preds["pair"].map(canonical)
    preds.to_csv(OUTDIR / "predictions.csv", index=False)
    contested = [canonical(p) for p, _ in CONTESTED]

    print(f"Europe, {COHORT}-year cohorts {COHORT_MIN}-{COHORT_MAX}: {len(eu):,} elites, "
          f"{int(eu['diversified'].sum()):,} spanning two sectors")
    series = build_series(eu, "cohort", "europe_cohort")
    series["phase"] = series["cohort"].map(phase)
    series.to_csv(OUTDIR / "europe_sector_pairs_by_cohort.csv", index=False)
    cohorts = sorted(series["cohort"].unique())
    pre_cohorts = [c for c in cohorts if phase(c) == "pre"]
    post_main = [c for c in cohorts if phase(c) == "post" and c <= POST_CAP]
    post_long = [c for c in cohorts if phase(c) == "post"]
    print(f"cohorts: {cohorts}")
    print(f"  pre  {pre_cohorts}\n  post {post_main} (long: {post_long})")

    # ---- T1 and T2 ----------------------------------------------------------
    rows = []
    for pair, grp in series.groupby("pair"):
        d, se, npre, npost = contrast(grp, pre_cohorts, post_main)
        d_long, _, _, _ = contrast(grp, pre_cohorts, post_long)
        rows.append({"pair": pair, "change": d, "change_se": se,
                     "change_long_post": d_long,
                     "n_pre_cohorts": npre, "n_post_cohorts": npost,
                     "predicted": pair in set(preds["pair"]),
                     "contested": pair in contested})
    cont = pd.DataFrame(rows).dropna(subset=["change"])
    cont = cont.merge(preds[["pair", "direction", "claim", "source"]], on="pair", how="left")
    cont["signed_change"] = cont["change"] * cont["direction"]
    cont["rank_of_change"] = cont["change"].rank()
    cont["z"] = cont["change"] / cont["change_se"]
    cont = cont.sort_values("change", ascending=False)
    cont.to_csv(OUTDIR / "prepost_contrast.csv", index=False)

    def evaluate(frame, pre_c, post_c, label):
        rows = []
        for pair, grp in series.groupby("pair"):
            d, se, _, _ = contrast(grp, pre_c, post_c)
            rows.append({"pair": pair, "change": d, "change_se": se})
        c = pd.DataFrame(rows).dropna(subset=["change"])
        c = c.merge(preds[["pair", "direction"]], on="pair", how="left")
        pr = c[c["direction"].notna()]
        if pr.empty:
            return None
        correct = int((np.sign(pr["change"]) == pr["direction"]).sum())
        # T1: sign test.
        k, n = correct, len(pr)
        p_sign = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
        # T2: mean signed rank of the predicted pairs against random six-pair sets.
        c["signed_rank"] = (c["change"] * np.where(c["direction"].notna(),
                                                   c["direction"], 1)).rank()
        obs = float((c.loc[c["direction"].notna(), "change"]
                     * pr["direction"].to_numpy()).mean())
        pool = c["change"].to_numpy()
        draws = RNG.choice(pool, size=(N_PERM, n), replace=True)
        signs = RNG.choice([-1, 1], size=(N_PERM, n))
        null = (draws * signs).mean(axis=1)
        p_rank = float((np.sum(null >= obs) + 1) / (N_PERM + 1))
        return {"window": label, "n_predictions": n, "n_correct_sign": correct,
                "p_sign_test": float(p_sign),
                "mean_signed_change": obs, "p_permutation": p_rank,
                "pre_cohorts": ",".join(map(str, pre_c)),
                "post_cohorts": ",".join(map(str, post_c))}

    summary = [evaluate(series, pre_cohorts, post_main, "military revolution 1560-1660")]
    summary.append(evaluate(series, pre_cohorts, post_long,
                            "military revolution, post to 1825"))
    # T4: the same contrast shape moved 100 years each way. A wider shift leaves
    # the series with no cohorts on one side, so 100 years is what the record
    # allows; the placebo windows do overlap the real one, which weakens them.
    for shift in (-100, 100):
        lo, hi = WINDOW[0] + shift, WINDOW[1] + shift
        pre_c = [c for c in cohorts if c + CAREER[1] < lo]
        post_c = [c for c in cohorts if c + CAREER[0] > hi][:len(post_main)]
        if len(pre_c) >= 2 and len(post_c) >= 2:
            summary.append(evaluate(series, pre_c, post_c,
                                    f"placebo window {lo}-{hi}"))
        else:
            print(f"placebo window {lo}-{hi}: not estimable "
                  f"({len(pre_c)} pre, {len(post_c)} post cohorts)")
    summary = pd.DataFrame([s for s in summary if s])
    summary.to_csv(OUTDIR / "test_summary.csv", index=False)
    print("\nT1 and T2, with placebo windows")
    print(summary.round(4).to_string(index=False))

    # ---- T3 timing ----------------------------------------------------------
    rows = []
    for pair in list(preds["pair"]) + contested:
        g = series[series["pair"] == pair].sort_values("cohort")
        g = g[np.isfinite(g["assoc_log2"]) & (g["assoc_boot_se"] > 0)]
        if len(g) < 8:
            continue
        x = g["cohort"].to_numpy(dtype=float)
        cands = x[2:len(x) - 3]
        res = break_test(x, g["assoc_log2"].to_numpy(), g["assoc_boot_se"].to_numpy(), cands)
        if res is None:
            continue
        rows.append({"pair": pair, "break_cohort": res["date"], "shift": res["shift"],
                     "shift_se": res["shift_se"], "p_value": res["p_value"],
                     "in_window": bool(WINDOW[0] - CAREER[1] <= res["date"]
                                       <= WINDOW[1] - CAREER[0]),
                     "window_low": WINDOW[0] - CAREER[1],
                     "window_high": WINDOW[1] - CAREER[0]})
    tim = pd.DataFrame(rows)
    if not tim.empty:
        tim["q_value"] = bh(tim["p_value"].to_numpy())
    tim.to_csv(OUTDIR / "breaks_predicted_pairs.csv", index=False)
    print("\nT3, where the level shift is dated (exposed cohorts "
          f"{WINDOW[0] - CAREER[1]} to {WINDOW[1] - CAREER[0]})")
    print(tim.round(3).to_string(index=False))

    # ---- T5 composition placebo --------------------------------------------
    rows = []
    for cohort in cohorts:
        sub = eu[eu["cohort"] == cohort]
        rec = {"cohort": cohort, "n_elites": len(sub),
               "log_n_elites": float(np.log(len(sub))),
               "diversification_rate": float(sub["diversified"].mean())}
        for sector in SECTOR_ORDER:
            holds = (sub["sector_main"] == sector) | (sub["sector_second"] == sector)
            rec[f"share_{sector}"] = float(holds.mean())
        rows.append(rec)
    comp = pd.DataFrame(rows)
    comp["phase"] = comp["cohort"].map(phase)
    placebo_rows = []
    for col in [c for c in comp.columns if c.startswith("share_")] + \
               ["log_n_elites", "diversification_rate"]:
        pre_v = comp[comp["cohort"].isin(pre_cohorts)][col].mean()
        post_v = comp[comp["cohort"].isin(post_main)][col].mean()
        placebo_rows.append({"outcome": col, "pre": pre_v, "post": post_v,
                             "change": post_v - pre_v})
    pd.DataFrame(placebo_rows).to_csv(OUTDIR / "composition_placebo.csv", index=False)
    comp.to_csv(OUTDIR / "europe_composition_by_cohort.csv", index=False)

    # ---- T6 the military sector's position ---------------------------------
    rows = []
    for cohort in cohorts:
        g = series[series["cohort"] == cohort]
        mat = to_matrix(g, SECTOR_ORDER, "sector_a", "sector_b")
        core, fit = coreness(mat)
        mil = mat.loc["Military"].drop("Military")
        rows.append({"cohort": cohort, "phase": phase(cohort),
                     "military_mean_assoc": float(np.nanmean(mil)),
                     "military_max_assoc": float(np.nanmax(mil)),
                     "military_coreness": float(core["Military"]),
                     "n_positive_ties": int((g["assoc_log2"] > 0).sum()),
                     "cp_fit": fit})
    cen = pd.DataFrame(rows)
    cen.to_csv(OUTDIR / "military_centrality_by_cohort.csv", index=False)
    print("\nT6, the military sector cohort by cohort")
    print(cen.round(3).to_string(index=False))

    # ---- T7 intensity -------------------------------------------------------
    blocs = df[df["country"].isin(HIGH_PRESSURE + LOW_PRESSURE)
               & df["birth"].between(COHORT_MIN, COHORT_MAX)].copy()
    blocs["cohort"] = (blocs["birth"] // 50).astype(int) * 50
    blocs["bloc"] = np.where(blocs["country"].isin(HIGH_PRESSURE),
                             "high pressure", "low pressure")

    def bloc_series(frame):
        out = []
        for bloc, sub in frame.groupby("bloc"):
            s = build_series(sub, "cohort", "bloc", min_pairs=250)
            if not s.empty:
                s["bloc"] = bloc
                out.append(s)
        return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

    bs = bloc_series(blocs)
    pre_b = sorted({c for c in bs["cohort"].unique() if phase(c) == "pre"})
    post_b = sorted({c for c in bs["cohort"].unique()
                     if phase(c) == "post" and c <= POST_CAP})
    rows = []
    for pair in list(preds["pair"]) + contested:
        vals = {}
        for bloc in ("high pressure", "low pressure"):
            g = bs[(bs["pair"] == pair) & (bs["bloc"] == bloc)]
            vals[bloc], _, _, _ = contrast(g, pre_b, post_b)
        rows.append({"pair": pair, "high": vals["high pressure"],
                     "low": vals["low pressure"],
                     "did": vals["high pressure"] - vals["low pressure"]})
    did = pd.DataFrame(rows)

    # Two blocs is two clusters, so inference permutes which countries sit where.
    countries = HIGH_PRESSURE + LOW_PRESSURE
    null = {r["pair"]: [] for _, r in did.iterrows()}
    for _ in range(300):
        pick = set(RNG.choice(countries, size=len(HIGH_PRESSURE), replace=False))
        tmp = blocs.copy()
        tmp["bloc"] = np.where(tmp["country"].isin(pick), "high pressure", "low pressure")
        fake = bloc_series(tmp)
        if fake.empty:
            continue
        for pair in null:
            v = {}
            for bloc in ("high pressure", "low pressure"):
                g = fake[(fake["pair"] == pair) & (fake["bloc"] == bloc)]
                v[bloc], _, _, _ = contrast(g, pre_b, post_b)
            if np.isfinite(v["high pressure"]) and np.isfinite(v["low pressure"]):
                null[pair].append(v["high pressure"] - v["low pressure"])
    did["p_permutation"] = [
        (np.sum(np.abs(null[r["pair"]]) >= abs(r["did"])) + 1) / (len(null[r["pair"]]) + 1)
        if null[r["pair"]] else np.nan for _, r in did.iterrows()]
    did["n_draws"] = [len(null[p]) for p in did["pair"]]
    did["pre_cohorts"] = ",".join(map(str, pre_b))
    did["post_cohorts"] = ",".join(map(str, post_b))
    did.to_csv(OUTDIR / "bloc_did.csv", index=False)
    bs.to_csv(OUTDIR / "bloc_sector_pairs_by_cohort.csv", index=False)
    print("\nT7, high against low military pressure")
    print(did.round(3).to_string(index=False))

    print("\n--- the six predictions, PRE to POST ---")
    show = cont[cont["predicted"]][["pair", "direction", "change", "change_se", "z",
                                    "rank_of_change"]]
    print(show.round(3).to_string(index=False))
    print("\ncontested:")
    print(cont[cont["contested"]][["pair", "change", "change_se", "z"]].round(3)
          .to_string(index=False))


if __name__ == "__main__":
    main()
