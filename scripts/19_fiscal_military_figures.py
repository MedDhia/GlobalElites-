"""Figures for the fiscal-military state test.

Reads data/processed/fiscal_military/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from plotstyle import BLUE, GREY, RED, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
FM = ROOT / "data" / "processed" / "fiscal_military"

WINDOW = (1688, 1783)
CAREER = (25, 65)
EXPOSED = (WINDOW[0] - CAREER[1], WINDOW[1] - CAREER[0])   # cohorts 1623 to 1758
TREATED = "United Kingdom"
UNIT_COLOUR = {"United Kingdom": "#b2182b", "France": "#2166ac", "Germany": "#1b7837",
               "Spain": "#e08214", "Italy": "#762a83"}
NOTE = ("Sectors are coarsened to seven groups so a country and cohort cell has enough cases; politics and "
        "administration stay apart because their fusion is the claim, and\nbusiness stays apart because public "
        "credit is what separates this thesis from the military revolution. A cohort born in b works in [b+25, b+65], "
        "so the cohorts whose\nwhole career falls inside 1688-1783 are those born 1663 to 1718.")


def figF01(did, space, pairs_placebo):
    pr = did[did["is_predicted"]].sort_values("did")
    fig, axes = plt.subplots(1, 2, figsize=(15.0, 6.0),
                             gridspec_kw={"width_ratios": [1.45, 1]})

    ax = axes[0]
    y = np.arange(len(pr))
    for yi, (_, r) in zip(y, pr.iterrows()):
        ax.plot([r["donor_mean_change"], r["treated_change"]], [yi, yi],
                color="#cccccc", lw=1.6, zorder=2)
        ok = np.sign(r["did"]) == r["direction"]
        ax.scatter([r["donor_mean_change"]], [yi], s=52, color="#777777", zorder=3)
        ax.scatter([r["treated_change"]], [yi], s=62, color=RED if not ok else "#1b7837",
                   zorder=4)
        ax.text(1.95, yi, ("→ predicted to tighten" if r["direction"] > 0
                           else "→ predicted to loosen"), fontsize=7, color=GREY,
                va="center", ha="right")
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(pr["pair"], fontsize=8.4)
    ax.set_xlim(-2.0, 2.0)
    ax.set_xlabel("change in log$_2$(observed / expected), pre-1688 cohorts to the 1688-1783 cohorts")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [Patch(color="#777777", label="mean of France, Germany, Spain, Italy"),
               Patch(color="#1b7837", label="Britain, moves as predicted relative to them"),
               Patch(color=RED, label="Britain, does not")]
    ax.legend(handles=handles, fontsize=7.6, loc="lower left")
    ax.set_title("Britain against the donor pool on the six predictions",
                 fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    s = space.sort_values("mean_signed_did")
    y = np.arange(len(s))
    colours = [UNIT_COLOUR.get(u, GREY) for u in s["unit"]]
    ax.barh(y, s["mean_signed_did"], color=colours, height=0.62)
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(s["unit"], fontsize=9)
    for t, u in zip(ax.get_yticklabels(), s["unit"]):
        t.set_color(UNIT_COLOUR.get(u, GREY))
    for yi, (_, r) in zip(y, s.iterrows()):
        ax.text(r["mean_signed_did"] + (0.02 if r["mean_signed_did"] > 0 else -0.02), yi,
                f"{int(r['n_correct_sign'])}/{int(r['n_predictions'])}", fontsize=7.4,
                va="center", ha="left" if r["mean_signed_did"] > 0 else "right", color=GREY)
    ax.set_xlabel("mean effect in the predicted direction")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Each unit treated in turn", fontsize=10.5, loc="left", pad=10)

    p_pairs = float(pairs_placebo["p_permutation_over_pairs"].iloc[0])
    n_right = int(pairs_placebo["n_correct_sign"].iloc[0])
    fig.suptitle("Brewer's predictions do not separate Britain from the continent",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.20,
             f"Left: Britain moves in the predicted direction in level on four of the six, but the donor pool moves "
             f"further on the state-building pairs, so the difference in\ndifferences favours the thesis on only "
             f"{n_right}. The two that go sharply the wrong way, public credit and war contracting, are the ones that "
             f"distinguish this thesis from the\nmilitary revolution. Right: treating each unit in turn, Britain "
             f"ranks last of the five. With four donors the smallest rank test this design can return is 0.20 and "
             f"Britain\nsits at 1.00. A second null, permuting over the fifteen pairs the thesis says nothing about, "
             f"gives p = {p_pairs:.2f}. " + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    save(fig, "figF01_britain_vs_donors")


def figF02(series, preds):
    pairs = list(preds["pair"])
    fig, axes = plt.subplots(2, 3, figsize=(15.0, 7.4), sharex=True)
    for ax, pair in zip(axes.ravel(), pairs):
        ax.axvspan(EXPOSED[0], EXPOSED[1], color="#f2e2c9", alpha=0.75, zorder=0,
                   linewidth=0)
        for unit in [TREATED, "France", "Germany", "Spain", "Italy"]:
            g = series[(series["pair"] == pair) & (series["country"] == unit)]
            g = g.sort_values("cohort")
            if g.empty:
                continue
            main = unit == TREATED
            ax.plot(g["cohort"], g["assoc_log2"], color=UNIT_COLOUR[unit],
                    lw=2.4 if main else 1.1, marker="o" if main else None,
                    ms=3.6, alpha=1.0 if main else 0.75, label=unit, zorder=4 if main else 3)
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        d = preds.set_index("pair").loc[pair, "direction"]
        ax.set_title(pair + ("  predicted ↑" if d > 0 else "  predicted ↓"),
                     fontsize=8.6, loc="left")
        ax.tick_params(labelsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend(fontsize=7, loc="lower left", ncol=2)
    for ax in axes[-1]:
        ax.set_xlabel("birth cohort")
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)")
    fig.suptitle("The six predictions, cohort by cohort",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.075,
             "The shaded band is the cohorts whose whole career falls inside 1688-1783. Britain is the heavy red "
             "line. On the two administration pairs Britain and the\ncontinent move together; on the two business "
             "pairs Britain moves against the prediction while France moves with it. " + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.96])
    save(fig, "figF02_predicted_trajectories")


def figF03(bf, persistence):
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 5.6))

    ax = axes[0]
    b = bf[bf["direction"].notna() | bf["is_contested"]].sort_values("britain_minus_france")
    y = np.arange(len(b))
    for yi, (_, r) in zip(y, b.iterrows()):
        ax.plot([r["france_change"], r["treated_change"]], [yi, yi], color="#cccccc",
                lw=1.6, zorder=2)
        ax.scatter([r["france_change"]], [yi], s=54, color=UNIT_COLOUR["France"], zorder=3)
        ax.scatter([r["treated_change"]], [yi], s=60, color=UNIT_COLOUR[TREATED], zorder=4)
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels([p + ("  (contested)" if c else "") for p, c
                        in zip(b["pair"], b["is_contested"])], fontsize=8)
    ax.set_xlabel("change from the pre-1688 cohorts to the 1688-1783 cohorts")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [Patch(color=UNIT_COLOUR[TREATED], label="Britain"),
               Patch(color=UNIT_COLOUR["France"], label="France")]
    ax.legend(handles=handles, fontsize=8, loc="lower right")
    ax.set_title("The head-to-head Brewer actually draws", fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    p = persistence.sort_values("did")
    y = np.arange(len(p))
    colours = [("#1b7837" if np.sign(r["did"]) == r["direction"] else RED)
               for _, r in p.iterrows()]
    ax.barh(y, p["did"], color=colours, height=0.6)
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(p["pair"], fontsize=8)
    ax.set_xlabel("Britain minus the donor pool, 1688-1783 cohorts to the post-1783 cohorts")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("What happens after the window closes", fontsize=10.5, loc="left", pad=10)

    fig.suptitle("Two readings that complicate the verdict",
                 fontsize=12.5, x=0.04, ha="left", y=1.02)
    fig.text(0.04, -0.11,
             "Left: on the sharpest contrast Brewer draws, the tie between office and birth, Britain falls by 0.26 "
             "and France by 0.22. A dead heat. The largest gap between\nthem runs the other way: the tie between arms "
             "and money collapses in Britain and tightens in France. Right: after 1783 Britain does pull away from the "
             "donor\npool on five of the six, which is the pattern the thesis predicts, a century after the window it "
             "predicts it in. " + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figF03_france_and_persistence")


def main():
    did = pd.read_csv(FM / "did_results.csv")
    space = pd.read_csv(FM / "placebo_in_space.csv")
    pairs_placebo = pd.read_csv(FM / "placebo_in_pairs.csv")
    series = pd.read_csv(FM / "country_pairs_by_cohort.csv")
    preds = pd.read_csv(FM / "predictions.csv")
    bf = pd.read_csv(FM / "britain_vs_france.csv")
    persistence = pd.read_csv(FM / "persistence.csv")

    print("writing fiscal-military figures")
    figF01(did, space, pairs_placebo)
    figF02(series, preds)
    figF03(bf, persistence)


if __name__ == "__main__":
    main()
