"""Figures for the Tilly path test.

Reads data/processed/tilly/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from plotstyle import GREY, RED, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
TD = ROOT / "data" / "processed" / "tilly"

PATHS = ["capital-intensive", "capitalized coercion", "coercion-intensive"]
PATH_COLOUR = {"capital-intensive": "#2166ac", "capitalized coercion": "#7f7f7f",
               "coercion-intensive": "#b2182b"}
MAIN_ERA = "1600-1799"
ERAS = ["1400-1599", "1600-1799", "1800-1899", "1900-2020"]
NOTE = ("Sectors are coarsened to seven groups so a country and era cell has enough cases. Paths are coded from "
        "Tilly's own examples onto the modern states the source\nuses; the lossiest case is Italy, which merges "
        "Venice and Genoa with the papal and southern states. Inference permutes the path labels across countries.")


def figT01(series, tests, coding):
    order = ["Politics + Business", "Politics + Military",
             "Military + Nobility & Kinship", "Administration & Law + Business"]
    e = series[series["era"] == MAIN_ERA]
    wide = e.pivot(index="country", columns="pair", values="assoc_log2")
    path = coding.set_index("country")["path"]
    t = tests[(tests["era"] == MAIN_ERA) & (tests["coding"] == "main")].set_index("quantity")

    fig, axes = plt.subplots(1, 4, figsize=(16.0, 6.2), sharey=False)
    for ax, pair in zip(axes, order):
        if pair not in wide.columns:
            ax.axis("off")
            continue
        for k, p in enumerate(PATHS):
            members = [c for c in wide.index if path.get(c) == p]
            vals = wide.loc[members, pair].dropna()
            x = np.full(len(vals), k) + np.linspace(-0.16, 0.16, len(vals))
            ax.scatter(x, vals, s=46, color=PATH_COLOUR[p], zorder=3, alpha=0.9)
            for xi, (c, v) in zip(x, vals.items()):
                ax.annotate(c, (xi, v), textcoords="offset points", xytext=(0, 7),
                            ha="center", fontsize=5.8, color="#444444")
            if len(vals):
                ax.plot([k - 0.28, k + 0.28], [vals.mean()] * 2, color=PATH_COLOUR[p],
                        lw=2.6, zorder=4)
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        ax.set_xticks(range(3))
        ax.set_xticklabels(["capital", "capitalized", "coercion"], fontsize=8)
        row = t.loc[pair] if pair in t.index else None
        tag = ""
        if row is not None:
            tag = (f"\nordered as predicted, q = {row['q_within_era']:.3f}"
                   if row["monotone_as_predicted"]
                   else f"\nnot ordered as predicted, p = {row['p_permutation']:.2f}")
        ax.set_title(pair + tag, fontsize=8.6, loc="left")
        ax.tick_params(labelsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
        pred = t.loc[pair, "predicted_order"] if row is not None else ""
        ax.set_xlabel("predicted low to high:\n" + pred.replace("-intensive", "")
                      .replace("capitalized coercion", "capitalized"), fontsize=6.8)
    axes[0].set_ylabel("log$_2$(observed / expected), 1600-1799 cohorts")
    fig.suptitle("Tilly's capital side holds. His coercion side does not.",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.12,
             "Each point is a country, the bar is the path's mean. Politics with business runs exactly as Tilly says, "
             "from +0.14 among the capital-intensive states to -0.71\namong the coercion-intensive ones, monotone "
             "across all three paths and surviving the adjustment for the five tests in this era. The three coercion-"
             "side predictions\ndo not hold: politics with the military is highest among the capital-intensive states, "
             "and administration with business is highest among the coercion-intensive\nones, both the reverse of the "
             "prediction. " + NOTE + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    save(fig, "figT01_paths_main_era")


def figT02(series, coding, tests):
    e = series[series["era"] == MAIN_ERA]
    wide = e.pivot(index="country", columns="pair", values="assoc_log2")
    path = coding.set_index("country")["path"]
    pm, pb = "Politics + Military", "Politics + Business"

    fig, axes = plt.subplots(1, 2, figsize=(14.6, 6.0),
                             gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
    for p in PATHS:
        members = [c for c in wide.index if path.get(c) == p]
        sub = wide.loc[members, [pm, pb]].dropna()
        ax.scatter(sub[pb], sub[pm], s=70, color=PATH_COLOUR[p], label=p, zorder=3,
                   alpha=0.9)
        for c, r in sub.iterrows():
            ax.annotate(c, (r[pb], r[pm]), textcoords="offset points", xytext=(0, 9),
                        ha="center", fontsize=6.6, color="#333333")
    ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
    ax.axvline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
    ax.set_xlabel("Politics + Business   (Tilly's capital axis)")
    ax.set_ylabel("Politics + Military   (Tilly's coercion axis)")
    ax.legend(fontsize=8, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"The two axes, {MAIN_ERA} cohorts", fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    t = tests[tests["coding"] == "main"]
    quantities = ["Politics + Business", "Politics + Military",
                  "Military + Nobility & Kinship", "coercion index"]
    x = np.arange(len(ERAS))
    for k, q in enumerate(quantities):
        g = t[t["quantity"] == q].set_index("era").reindex(ERAS)
        ax.plot(x, g["p_permutation"], marker="o", ms=5, lw=1.6, label=q)
    ax.axhline(0.05, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.text(3.05, 0.055, "0.05", fontsize=7.4, color=GREY, ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels(ERAS, fontsize=8)
    ax.set_ylabel("permutation p on the predicted ordering")
    ax.set_ylim(0, 1.02)
    ax.legend(fontsize=7.4, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("When each prediction holds", fontsize=10.5, loc="left", pad=10)

    fig.suptitle("Where the paths separate, and when",
                 fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.115,
             "Left: on the capital axis the three paths separate cleanly, with every coercion-intensive state left of "
             "zero except Austria. On the coercion axis they do not\nseparate at all. Right: the capital-side "
             "prediction holds only in 1600-1799, Tilly's formative period, and is gone afterwards. The coercion-side "
             "predictions come\nclosest in 1800-1899, a century after the period the thesis is about, and never reach "
             "0.05. " + NOTE + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figT02_axes_and_timing")


def figT03(mc, loo, alt):
    fig, axes = plt.subplots(1, 3, figsize=(15.4, 5.2))

    ax = axes[0]
    m = mc[mc["era"] == MAIN_ERA]
    for k, p in enumerate(PATHS):
        vals = m.loc[m["path"] == p, "military_minus_business"]
        x = np.full(len(vals), k) + np.linspace(-0.14, 0.14, len(vals))
        ax.scatter(x, vals, s=46, color=PATH_COLOUR[p], zorder=3)
        if len(vals):
            ax.plot([k - 0.26, k + 0.26], [vals.mean()] * 2, color=PATH_COLOUR[p], lw=2.6)
    ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
    ax.set_xticks(range(3))
    ax.set_xticklabels(["capital", "capitalized", "coercion"], fontsize=8)
    ax.set_ylabel("military share minus business share of elites")
    ax.set_title("1. The coding is not arbitrary", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    l = loo.sort_values("p_permutation")
    y = np.arange(len(l))
    ax.barh(y, l["p_permutation"],
            color=[RED if not mo else "#1b7837" for mo in l["monotone"]], height=0.66)
    ax.axvline(0.05, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(l["dropped"], fontsize=7.4)
    ax.set_xlabel("permutation p on the coercion index, dropping that country")
    ax.set_title("2. The composite is fragile", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [Patch(color="#1b7837", label="means still ordered as predicted"),
               Patch(color=RED, label="not ordered")]
    ax.legend(handles=handles, fontsize=7, loc="lower right")

    ax = axes[2]
    a = alt[alt["era"] == MAIN_ERA].set_index("quantity")
    quantities = [q for q in ["Politics + Business", "Politics + Military",
                              "Military + Nobility & Kinship",
                              "Administration & Law + Business", "coercion index"]
                  if q in a.index]
    y = np.arange(len(quantities))
    ax.barh(y, [a.loc[q, "p_permutation"] for q in quantities], color="#777777",
            height=0.6)
    ax.axvline(0.05, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(quantities, fontsize=7.6)
    ax.set_xlabel("permutation p under the alternative coding")
    ax.set_title("3. Recoding the debatable cases", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Three checks on the coding", fontsize=12.5, x=0.035, ha="left", y=1.02)
    fig.text(0.035, -0.14,
             "Left: the coded paths do separate countries on the raw mix of military and business elites, ordered as "
             "Tilly's typology says and at p = 0.008. So the\ncoercion-side nulls are not a failure of the coding. "
             "Those states really do produce more soldiers and fewer merchants; what they do not produce is a tighter "
             "bond\nbetween politics and the military once that difference in size is netted out. Middle: dropping "
             "one country at a time, the composite index keeps a p below 0.18\nthroughout but the means are ordered as "
             "predicted in only one of seventeen drops. Right: moving Denmark, Sweden and Germany leaves the "
             "capital-side result\nintact at p = 0.013 and changes nothing else. " + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figT03_coding_checks")


def main():
    series = pd.read_csv(TD / "country_era_pairs.csv")
    tests = pd.read_csv(TD / "ordering_tests.csv")
    coding = pd.read_csv(TD / "path_coding.csv")
    mc = pd.read_csv(TD / "manipulation_check.csv")
    loo = pd.read_csv(TD / "leave_one_out.csv")
    alt = pd.read_csv(TD / "alternative_coding.csv")

    print("writing Tilly figures")
    figT01(series, tests, coding)
    figT02(series, coding, tests)
    figT03(mc, loo, alt)


if __name__ == "__main__":
    main()
