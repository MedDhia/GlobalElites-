"""Figures for the military revolution test.

Reads data/processed/military_revolution/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from plotstyle import BLUE, GREY, RED, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
MR = ROOT / "data" / "processed" / "military_revolution"

WINDOW = (1560, 1660)
CAREER = (25, 65)
EXPOSED = (WINDOW[0] - CAREER[1], WINDOW[1] - CAREER[0])   # cohorts 1495 to 1635
PRED_COLOUR = {1: "#b2182b", -1: "#2166ac"}
NOTE = ("Europe only, 25-year birth cohorts. A cohort born in year b has its main career in [b+25, b+65], so the "
        "cohorts exposed to a 1560-1660 window are those born\nbetween 1495 and 1635; they are held out of the "
        "before-and-after contrast, not assigned to a side.")


def shade_window(ax):
    ax.axvspan(EXPOSED[0], EXPOSED[1], color="#f2e2c9", alpha=0.75, zorder=0,
               linewidth=0)


def figM01(contrast, preds):
    c = contrast.sort_values("change")
    y = np.arange(len(c))
    pred = c["direction"].notna()
    fig, ax = plt.subplots(figsize=(9.6, 11.6))
    ax.hlines(y[~pred], c.loc[~pred, "change"] - 1.96 * c.loc[~pred, "change_se"],
              c.loc[~pred, "change"] + 1.96 * c.loc[~pred, "change_se"],
              color="#cccccc", lw=1.2)
    ax.scatter(c.loc[~pred, "change"], y[~pred], s=16, color="#aaaaaa", zorder=3,
               label="the 71 pairs the thesis says nothing about")
    for d in (1, -1):
        m = c["direction"] == d
        if not m.any():
            continue
        ax.hlines(y[m.to_numpy()], c.loc[m, "change"] - 1.96 * c.loc[m, "change_se"],
                  c.loc[m, "change"] + 1.96 * c.loc[m, "change_se"],
                  color=PRED_COLOUR[d], lw=2.0)
        ax.scatter(c.loc[m, "change"], y[m.to_numpy()], s=58, color=PRED_COLOUR[d],
                   zorder=4, marker="D" if d > 0 else "v",
                   label=("predicted to tighten" if d > 0 else "predicted to loosen"))
    cont = c["contested"] if "contested" in c else pd.Series(False, index=c.index)
    if cont.any():
        ax.scatter(c.loc[cont, "change"], y[cont.to_numpy()], s=70, facecolor="none",
                   edgecolor="#111111", linewidth=1.4, zorder=5,
                   label="contested prediction")
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    labelled = c[pred | cont]
    ax.set_yticks(y[(pred | cont).to_numpy()])
    ax.set_yticklabels(labelled["pair"], fontsize=8)
    for t, d in zip(ax.get_yticklabels(), labelled["direction"]):
        t.set_color(PRED_COLOUR.get(d, "#111111") if np.isfinite(d) else "#111111")
    ax.set_ylim(-1, len(c))
    ax.set_xlabel("change in log$_2$(observed / expected), cohorts before 1495 to cohorts 1650-1775")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Six predictions, written before the series was computed",
                 fontsize=12.5, loc="left", pad=12)
    fig.text(0.0, -0.035,
             "Every one of the 78 sector pairs is shown; only the predicted ones are labelled. Five of the six move "
             "as the thesis says they should, which a sign test puts at\np = 0.11 and a permutation test on the size "
             "of the moves at p = 0.12. The one that fails is administration and law with the military, which is the "
             "fiscal-military\nstate's central claim. Bars are 95% intervals on the change. " + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    save(fig, "figM01_predictions")


def figM02(series, preds, contested):
    pairs = list(preds["pair"]) + contested
    fig, axes = plt.subplots(2, 4, figsize=(16.0, 7.4), sharex=True)
    direction = dict(zip(preds["pair"], preds["direction"]))
    for ax, pair in zip(axes.ravel(), pairs):
        g = series[series["pair"] == pair].sort_values("cohort")
        shade_window(ax)
        colour = PRED_COLOUR.get(direction.get(pair, 0), "#111111")
        ax.fill_between(g["cohort"], g["assoc_ci_low"], g["assoc_ci_high"],
                        color=colour, alpha=0.18, linewidth=0)
        ax.plot(g["cohort"], g["assoc_log2"], color=colour, lw=1.8, marker="o", ms=3.4)
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        arrow = {1: "  predicted ↑", -1: "  predicted ↓"}.get(direction.get(pair), "  contested")
        ax.set_title(pair.replace(" + ", "  +  ") + arrow, fontsize=8.8, loc="left")
        ax.tick_params(labelsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
    axes.ravel()[-1].axis("off")
    handles = [Patch(color="#f2e2c9", label="cohorts whose careers fall in 1560-1660")]
    axes.ravel()[-1].legend(handles=handles, fontsize=8.4, loc="center")
    for ax in axes[-1]:
        ax.set_xlabel("birth cohort")
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)")
    fig.suptitle("The predicted pairs, cohort by cohort",
                 fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.065,
             "Shaded bands are 95% bootstrap intervals. The moves are real and mostly in the predicted direction, but "
             "look at where they happen. Politics with the military\nand politics with administration both rise "
             "across the shaded cohorts, which fits. The rest do not: the military-engineer tie is made between 1425 "
             "and 1500,\nbefore the window opens, and so is the fall in the military-religion tie; administration "
             "with the military is flat through the window and then falls after 1700,\nagainst the prediction. Most "
             "of this reorganisation is finished before Roberts' window starts. " + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.96])
    save(fig, "figM02_predicted_trajectories")


def figM03(breaks, centrality):
    fig, axes = plt.subplots(1, 2, figsize=(14.4, 6.0),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    b = breaks.sort_values("break_cohort")
    y = np.arange(len(b))
    ax.axvspan(EXPOSED[0], EXPOSED[1], color="#f2e2c9", alpha=0.8, zorder=0, linewidth=0)
    colours = ["#b2182b" if v else "#777777" for v in b["in_window"]]
    ax.scatter(b["break_cohort"], y, s=90, color=colours, zorder=3)
    for yi, (_, r) in zip(y, b.iterrows()):
        ax.annotate(f"{r['shift']:+.2f}", (r["break_cohort"], yi),
                    textcoords="offset points", xytext=(0, 11), ha="center",
                    fontsize=7, color=GREY)
    ax.set_yticks(y)
    ax.set_yticklabels(b["pair"], fontsize=8)
    ax.set_xlabel("birth cohort at which the level shift is dated")
    ax.set_xlim(1350, 1830)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Where the shifts actually date", fontsize=10.5, loc="left", pad=10)
    ax.text(EXPOSED[0] + 5, len(b) - 0.4, "cohorts exposed to 1560-1660",
            fontsize=7.6, color="#8a6d3b", va="top")

    ax = axes[1]
    shade_window(ax)
    ax.plot(centrality["cohort"], centrality["military_mean_assoc"], color=RED,
            lw=2.0, marker="o", ms=4, label="mean association with the other 12 sectors")
    ax.plot(centrality["cohort"], centrality["military_coreness"], color=BLUE,
            lw=1.6, marker="s", ms=3.4, ls=(0, (4, 2)),
            label="coreness among the positive ties")
    ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
    ax.set_xlabel("birth cohort")
    ax.set_ylabel("score")
    ax.legend(fontsize=7.8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("The military sector's position in the network", fontsize=10.5,
                 loc="left", pad=10)

    fig.suptitle("The timing does not fit", fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.10,
             "Left: a common-slope model with one level shift at an unknown date, fitted to each predicted pair. One "
             "of the seven dates inside the exposed cohorts, three date to\n1700 or 1750 and one to 1400. Read it "
             "with care: the model finds the single largest step, so where a series rises early and falls later it "
             "reports the fall. That is\nwhat happens to politics with the military and politics with "
             "administration, both of which do rise across the window and are dated here by their eighteenth-century\n"
             "decline. The safe statement is that no predicted pair has its dominant step inside the window. Right: "
             "the military sector does move toward the centre of the\nnetwork across the exposed cohorts, coreness "
             "rising from about 0.3 to 0.9, and stays there. That is the one piece of timing that fits cleanly.\n"
             + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figM03_timing")


def figM04(summary, did, bloc_series, preds):
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 5.8),
                             gridspec_kw={"width_ratios": [1, 1.2]})

    ax = axes[0]
    s = summary.copy()
    y = np.arange(len(s))[::-1]
    colours = ["#b2182b" if "military revolution" in w else "#999999" for w in s["window"]]
    ax.barh(y, s["mean_signed_change"], color=colours, height=0.6)
    for yi, (_, r) in zip(y, s.iterrows()):
        ax.text(r["mean_signed_change"] + 0.02, yi,
                f"{int(r['n_correct_sign'])}/{int(r['n_predictions'])} correct, "
                f"permutation p = {r['p_permutation']:.2f}",
                va="center", fontsize=7.4, color=GREY)
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels([w.replace("military revolution", "real window") for w in s["window"]],
                       fontsize=8)
    ax.set_xlabel("mean change in the predicted direction")
    ax.set_xlim(right=max(s["mean_signed_change"]) * 2.4)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Real window against placebo windows", fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    d = did.sort_values("did")
    y = np.arange(len(d))
    ax.scatter(d["low"], y, s=52, color="#2166ac", label="low military pressure", zorder=3)
    ax.scatter(d["high"], y, s=52, color="#b2182b", label="high military pressure", zorder=3)
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.plot([r["low"], r["high"]], [yi, yi], color="#bbbbbb", lw=1.4, zorder=2)
        ax.text(1.15, yi, f"p = {r['p_permutation']:.2f}", fontsize=7, color=GREY,
                va="center")
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(d["pair"], fontsize=8)
    ax.set_xlim(-1.6, 1.6)
    ax.set_xlabel("change from before 1495 to 1650-1775, inside the bloc")
    ax.legend(fontsize=7.8, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("No gradient by military pressure", fontsize=10.5, loc="left", pad=10)

    fig.suptitle("Two more tests, and neither helps the thesis",
                 fontsize=12.5, x=0.04, ha="left", y=1.02)
    fig.text(0.04, -0.11,
             "Left: the same six predictions evaluated across windows moved 100 years each way. A window a century "
             "earlier than Roberts' fits better than his own, 6 of 6\ncorrect against 5 of 6 and a larger mean move, "
             "though it rests on only two pre-window cohorts. A window a century later fits worst. The windows "
             "overlap, which\nis all a single 500-year series can offer, but the ordering says the contrast is "
             "medieval against early modern and not sensitive to where in that span the cut\nfalls. Right: high "
             "military pressure is France, Germany, Spain, Austria and Russia; low is the United Kingdom, the "
             "Netherlands, Switzerland and Sweden. If\narmy-building drove the reorganisation the high bloc should "
             "have moved further on the predicted pairs. It did not on any of the seven, the two largest gaps run "
             "the\nwrong way, and the permutation test over which countries sit in which bloc clears 0.28 everywhere. "
             + NOTE + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figM04_placebo_and_intensity")


def main():
    series = pd.read_csv(MR / "europe_sector_pairs_by_cohort.csv")
    contrast = pd.read_csv(MR / "prepost_contrast.csv")
    preds = pd.read_csv(MR / "predictions.csv")
    summary = pd.read_csv(MR / "test_summary.csv")
    breaks = pd.read_csv(MR / "breaks_predicted_pairs.csv")
    centrality = pd.read_csv(MR / "military_centrality_by_cohort.csv")
    did = pd.read_csv(MR / "bloc_did.csv")
    bloc_series = pd.read_csv(MR / "bloc_sector_pairs_by_cohort.csv")
    contested = contrast.loc[contrast["contested"], "pair"].tolist()

    print("writing military-revolution figures")
    figM01(contrast, preds)
    figM02(series, preds, contested)
    figM03(breaks, centrality)
    figM04(summary, did, bloc_series, preds)


if __name__ == "__main__":
    main()
