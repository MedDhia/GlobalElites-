"""Figures for the positional and break-point analysis.

Reads data/processed/network_structure/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy.cluster.hierarchy import dendrogram

from netstruct import blocks_from, profile_correlations, to_matrix
from plotstyle import CMAP, GREY, RED, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
NS = DATA / "network_structure"

SECTOR_ORDER = [
    "Politics", "Administration & Law", "Military", "Religion", "Nobility",
    "Kinship", "Big business", "Small business", "Academia",
    "Exploration & Invention", "Culture (core)", "Culture (periphery)",
    "Sport & Games",
]
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]
BLOCK_COLOUR = {"Politics block": "#4477AA", "Military block": "#EE6677",
                "Academia block": "#228833", "Big business block": "#CCBB44"}
BLOCK_GLOSS = {
    "Politics block": "Politics, Administration & Law",
    "Military block": "Military, Religion, Nobility, Kinship",
    "Academia block": "Academia, Culture (core), Culture (periphery)",
    "Big business block": "Big business, Small business, Exploration & Invention, Sport & Games",
}
VLIM = 3.0
PAIR_COLOUR = {
    "Political + Security": "#b2182b", "Ideational + Economic": "#ef8a62",
    "Political + Ideational": "#4d9221", "Political + Economic": "#67a9cf",
    "Ideational + Security": "#2166ac", "Economic + Security": "#053061",
}


def pooled_positions():
    overall = pd.read_csv(DATA / "sector_pair_association_overall.csv")
    mat = to_matrix(overall, SECTOR_ORDER, "sector_a", "sector_b")
    corr = profile_correlations(mat)
    labels, link, _ = blocks_from(corr, 4, SECTOR_ORDER)
    return mat, corr, labels, link


# --------------------------------------------------------------------------- #
def figS01(mat, corr, labels, link):
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 6.4),
                             gridspec_kw={"width_ratios": [1, 1.5]})

    ax = axes[0]
    dend = dendrogram(link, labels=SECTOR_ORDER, orientation="left", ax=ax,
                      color_threshold=0, above_threshold_color=GREY,
                      leaf_font_size=8.6)
    order = dend["ivl"][::-1]     # ivl runs bottom-to-top for a left-facing dendrogram
    for tick in ax.get_yticklabels():
        tick.set_color(BLOCK_COLOUR.get(labels[tick.get_text()], GREY))
    ax.set_xlabel("1 - correlation between association profiles")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("Sectors grouped by the company they keep", fontsize=10.5,
                 loc="left", pad=10)

    ax = axes[1]
    m = mat.loc[order, order]
    data = m.to_numpy(dtype=float)
    im = ax.imshow(np.ma.masked_invalid(data), cmap=CMAP.with_extremes(bad="#f2f2f2"),
                   vmin=-VLIM, vmax=VLIM)
    n = len(order)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(order, rotation=45, ha="right", fontsize=7.4)
    ax.set_yticklabels(order, fontsize=7.4)
    for tick, side in ((ax.get_xticklabels(), None), (ax.get_yticklabels(), None)):
        for t in tick:
            t.set_color(BLOCK_COLOUR.get(labels[t.get_text()], GREY))
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(n):
        ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, facecolor="white",
                                   edgecolor="white", zorder=3))
        for j in range(n):
            if i == j or not np.isfinite(data[i, j]):
                continue
            ax.text(j, i, f"{data[i, j]:+.1f}", ha="center", va="center", fontsize=5.8,
                    zorder=5, color="white" if abs(data[i, j]) / VLIM > 0.62 else "#1a1a1a")
    cuts = [k for k in range(1, n) if labels[order[k]] != labels[order[k - 1]]]
    for c in cuts:
        ax.axhline(c - 0.5, color="#111111", lw=1.8, zorder=6)
        ax.axvline(c - 0.5, color="#111111", lw=1.8, zorder=6)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.set_title("The association matrix reordered by block", fontsize=10.5,
                 loc="left", pad=10)

    handles = [Patch(color=c, label=f"{k}: {BLOCK_GLOSS[k]}") for k, c in BLOCK_COLOUR.items()]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=7.8,
               bbox_to_anchor=(0.5, -0.16))
    fig.suptitle("Four positions in the network of elite power",
                 fontsize=12.5, x=0.04, ha="left", y=1.03)
    fig.text(0.04, -0.05,
             "Two sectors occupy the same position when they combine with the same partners, whether or not they "
             "combine with each other. Distance is one minus\nthe correlation between their rows of the association "
             "matrix, computed with the two sectors' own cells left out; linkage is average. Four blocks are used for "
             "comparability\nwith the four-domain scheme: the silhouette curve is close to flat across two to six "
             "blocks (0.29 to 0.34), so the number is a choice and not a finding. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figS01_positions_and_blocks")


def figS02(blocks, image):
    periods = ["all"] + ERA_ORDER
    grid = (blocks[blocks["layer"] == "sector"]
            .pivot(index="node", columns="period", values="block")
            .reindex(SECTOR_ORDER)[periods])

    fig = plt.figure(figsize=(15.4, 8.6))
    gs = fig.add_gridspec(2, 6, height_ratios=[1.35, 1], hspace=0.42, wspace=0.16)

    ax = fig.add_subplot(gs[0, :])
    codes = {b: k for k, b in enumerate(BLOCK_COLOUR)}
    arr = grid.apply(lambda col: col.map(codes)).to_numpy(dtype=float)
    cmap = plt.matplotlib.colors.ListedColormap(list(BLOCK_COLOUR.values()))
    ax.imshow(np.ma.masked_invalid(arr), cmap=cmap, vmin=-0.5, vmax=3.5, aspect="auto")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(["Pooled"] + ERA_ORDER, fontsize=8.4)
    ax.set_yticks(range(len(SECTOR_ORDER)))
    ax.set_yticklabels(SECTOR_ORDER, fontsize=8)
    ax.set_xticks(np.arange(-0.5, len(periods), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(SECTOR_ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.6)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    ax.axvline(0.5, color="#111111", lw=2.0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Which block each sector sits in, era by era",
                 fontsize=10.5, loc="left", pad=8)

    vmax = 2.0
    first_order = [b for b in BLOCK_COLOUR if b in set(grid[ERA_ORDER[0]].dropna())]
    for k, era in enumerate(ERA_ORDER):
        axk = fig.add_subplot(gs[1, k])
        sub = image[(image["layer"] == "sector") & (image["period"] == era)]
        present = set(grid[era].dropna())
        order = [b for b in BLOCK_COLOUR if b in present]
        m = (sub.pivot(index="block_a", columns="block_b", values="mean_assoc")
             .reindex(index=order, columns=order))
        d = m.to_numpy(dtype=float)
        axk.imshow(np.ma.masked_invalid(d), cmap=CMAP.with_extremes(bad="#f2f2f2"),
                   vmin=-vmax, vmax=vmax)
        axk.set_xticks(range(len(order)))
        axk.set_yticks(range(len(order)))
        short = [b.replace(" block", "") for b in order]
        axk.set_xticklabels(short, rotation=45, ha="right", fontsize=6.4)
        # Label the rows wherever this era's block set differs from the first panel's,
        # so a reader never has to assume the rows line up.
        show_y = (k == 0) or (order != first_order)
        axk.set_yticklabels(short if show_y else [""] * len(order), fontsize=6.4)
        for t, b in zip(axk.get_xticklabels(), order):
            t.set_color(BLOCK_COLOUR[b])
        if show_y:
            for t, b in zip(axk.get_yticklabels(), order):
                t.set_color(BLOCK_COLOUR[b])
        axk.tick_params(length=0)
        for spine in axk.spines.values():
            spine.set_visible(False)
        for i in range(len(order)):
            for j in range(len(order)):
                if not np.isfinite(d[i, j]):
                    continue
                axk.text(j, i, f"{d[i, j]:+.1f}", ha="center", va="center", fontsize=6.2,
                         color="white" if abs(d[i, j]) / vmax > 0.6 else "#1a1a1a")
        axk.set_title(f"{era}  ({len(order)} blocks)", fontsize=8.4, loc="left", pad=5)

    fig.suptitle("Positions hold at the edges and churn in the middle",
                 fontsize=12.5, x=0.045, ha="left", y=0.985)
    fig.text(0.045, 0.02,
             "Top: blocks are refitted inside each era and matched to the pooled solution by overlap, so a colour means "
             "the same position throughout. Academia and both\nculture sectors never leave their block and kinship never "
             "leaves the military one; sport and the business sectors move repeatedly. The 1900-2020 cut yields three "
             "blocks,\nnot four. Bottom: mean association within and between blocks. Within beats between in every era, "
             "by 1.64 pooled and by as little as 0.24 in 1600-1799, which is what\nmakes these blocks worth drawing; it "
             "is not uniform, and the business block's own diagonal turns negative in three eras. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    save(fig, "figS02_blocks_over_time")


def figS03(indices):
    sec = indices[indices["layer"] == "sector"].set_index("period").reindex(ERA_ORDER)
    dom = indices[indices["layer"] == "domain"].set_index("period").reindex(ERA_ORDER)
    x = np.arange(len(ERA_ORDER))

    panels = [
        ("Composition of the matrix", None),
        ("Spread of the scores", "sd_assoc"),
        ("Degree centralization", "degree_centralization"),
        ("Transitivity of the positive ties", "transitivity"),
        ("Modularity", "modularity"),
        ("Core-periphery fit", "core_periphery_fit"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(14.2, 7.0))
    for ax, (title, col) in zip(axes.ravel(), panels):
        if col is None:
            ax.stackplot(x, sec["share_associated"], sec["share_dissociated"],
                         sec["share_indistinguishable"],
                         labels=["associated", "dissociated", "not distinguishable"],
                         colors=["#b2182b", "#2166ac", "#dcdcdc"], edgecolor="white",
                         linewidth=0.5)
            ax.set_ylim(0, 1)
            ax.legend(fontsize=7, loc="lower left")
            ax.set_ylabel("share of the 78 pairs")
        else:
            ax.plot(x, sec[col], color=RED, lw=2.0, marker="o", ms=4.2,
                    label="13 sectors")
            if col in ("sd_assoc", "core_periphery_fit"):
                ax.plot(x, dom[col], color="#2166ac", lw=1.6, marker="s", ms=3.6,
                        ls=(0, (4, 2)), label="4 domains")
                ax.legend(fontsize=7, loc="best")
            ax.set_ylim(bottom=0)
        ax.set_title(title, fontsize=9.8, loc="left")
        ax.set_xticks(x)
        ax.set_xticklabels(ERA_ORDER, rotation=45, ha="right", fontsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("The shape of the network, not only its cells",
                 fontsize=12.5, x=0.045, ha="left", y=1.0)
    fig.text(0.045, -0.075,
             "As the record thickens the matrix resolves: the share of pairs indistinguishable from the reference model "
             "falls from 44% before 1000 to under 3% after 1800.\nWhat does not happen is concentration. Centralization "
             "ends at 0.28 against 0.33 before 1000 and modularity at 0.31 against 0.30, and across the thirteen sectors "
             "the core-periphery\nfit stays between 0.39 and 0.65, never high enough to say the positive ties form one "
             "core with a periphery around it. The near-perfect fit on the four domains is a\nstatement about a network "
             "with six cells, not about concentration. Transitivity, modularity and centralization use the significant "
             "positive ties only. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figS03_network_indices")


def figS04(coreness):
    sec = coreness[coreness["layer"] == "sector"]
    periods = ["all"] + ERA_ORDER
    mat = sec.pivot(index="node", columns="period", values="coreness").reindex(SECTOR_ORDER)[periods]
    fit = (sec.drop_duplicates("period").set_index("period")["cp_fit"].reindex(periods))

    fig, ax = plt.subplots(figsize=(9.4, 6.0))
    im = ax.imshow(mat.to_numpy(dtype=float), cmap="magma_r", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels([f"Pooled\nfit {fit['all']:.2f}"]
                       + [f"{e}\nfit {fit[e]:.2f}" for e in ERA_ORDER], fontsize=7.6)
    ax.set_yticks(range(len(SECTOR_ORDER)))
    ax.set_yticklabels(SECTOR_ORDER, fontsize=8)
    ax.set_xticks(np.arange(-0.5, len(periods), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(SECTOR_ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    ax.axvline(0.5, color="#111111", lw=2.0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    d = mat.to_numpy(dtype=float)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            if np.isfinite(d[i, j]):
                ax.text(j, i, f"{d[i, j]:.2f}", ha="center", va="center", fontsize=6.6,
                        color="white" if d[i, j] > 0.62 else "#1a1a1a")
    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("coreness", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.set_title("Who sits at the centre of the positive ties",
                 fontsize=11.5, loc="left", pad=10)
    fig.text(0.0, -0.10,
             "Coreness is the leading eigenvector of the positive part of the association matrix, its best rank-one "
             "approximation, rescaled so the largest score is one.\nIt reads as membership of the tightest positive "
             "cluster and not as importance. The centre changes hands: culture and the academy hold it before 1400, "
             "nobility,\nkinship and the military after 1800. The fit printed under each column says how well one core "
             "with a periphery around it describes that era at all, and it\nnever exceeds 0.65 in any era. "
             + SOURCE, fontsize=7.4, color=GREY, ha="left")
    save(fig, "figS04_coreness")


def figS05(common, sec_breaks, dom_breaks):
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 7.4))
    layers = [("sector centuries", "13 sectors, century cohorts 800-1900"),
              ("sector half-centuries", "13 sectors, half-century cohorts 1400-1949"),
              ("domain half-centuries", "4 domains, half-century cohorts 1400-1949")]
    for ax, (layer, title) in zip(axes.ravel(), layers):
        g = common[common["layer"] == layer].sort_values("date")
        ax.plot(g["date"], g["sum_wald"], color=GREY, lw=1.8, marker="o", ms=4.5)
        best = g[g["is_best"]].iloc[0]
        ax.scatter([best["date"]], [best["sum_wald"]], s=110, color=RED, zorder=4)
        ax.annotate(f"{int(best['date'])}\np = {best['p_value_best']:.4f}",
                    (best["date"], best["sum_wald"]), textcoords="offset points",
                    xytext=(0, -34), ha="center", fontsize=8, color=RED)
        ax.set_title(title, fontsize=9.6, loc="left")
        ax.set_xlabel("candidate date of the shift")
        ax.set_ylabel("sum of Wald statistics")
        ax.set_ylim(bottom=0)
        ax.spines[["top", "right"]].set_visible(False)

    ax = axes.ravel()[3]
    sec_h = sec_breaks[sec_breaks["layer"] == "sector half-centuries"]
    bins = np.arange(1475, 1826, 50)
    ax.hist(sec_h["break_date"], bins=bins, color="#c6c6c6", edgecolor="white",
            label="all 78 sector pairs")
    ax.hist(sec_h[sec_h["has_break"]]["break_date"], bins=bins, color=RED,
            edgecolor="white", label="shift at q < 0.05")
    for _, r in dom_breaks[dom_breaks["has_break"]].iterrows():
        ax.axvline(r["break_date"], color=PAIR_COLOUR.get(r["pair"], "#2166ac"),
                   lw=2.0, ls=(0, (3, 2)))
    ax.set_title("Where each pair puts its own shift, 1400-1949", fontsize=9.6, loc="left")
    ax.set_xlabel("best-fitting date of the shift")
    ax.set_ylabel("sector pairs")
    ax.legend(fontsize=7.4, loc="upper left")
    ax.text(0.99, 0.96, "dashed lines: the five domain crossings\nwith a shift at q < 0.05",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.2, color=GREY)
    ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("A linear trend cannot see a step. Scanning for one.",
                 fontsize=12.5, x=0.045, ha="left", y=1.0)
    fig.text(0.045, -0.085,
             "Each pair is fitted with a common slope plus one level shift at an unknown date; the largest Wald statistic "
             "over all admissible dates is the test statistic, and\nits null distribution is simulated 2,000 times under "
             "a no-shift model using each cohort's own bootstrap standard error. The pooled panels sum that statistic "
             "over\nevery pair, so they ask whether one date fits the whole system. Read the 1100 result in the first "
             "panel with care: it rests on cohorts of a few thousand people.\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figS05_break_scan")


def figS06(dom_half, dom_breaks):
    order = ["Political + Security", "Ideational + Economic", "Political + Ideational",
             "Political + Economic", "Ideational + Security", "Economic + Security"]
    tr = dom_breaks.set_index("pair")
    fig, axes = plt.subplots(2, 3, figsize=(13.8, 6.8), sharex=True, sharey=True)
    for ax, pair in zip(axes.ravel(), order):
        g = dom_half[dom_half["pair"] == pair].sort_values("period")
        x = g["period"].to_numpy(dtype=float)
        colour = PAIR_COLOUR[pair]
        r = tr.loc[pair]
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        ax.fill_between(x, g["assoc_ci_low"], g["assoc_ci_high"], color=colour,
                        alpha=0.18, linewidth=0)
        ax.plot(x, g["assoc_log2"], color=colour, lw=1.4, marker="o", ms=3.4, alpha=0.85)

        no_break = r["level_no_break"] + r["slope_no_break_per_century"] * (x - r["centre"]) / 100
        ax.plot(x, no_break, color=GREY, lw=1.3, ls=(0, (5, 3)), label="no shift")
        step = (r["level_at_centre"] + r["slope_per_century"] * (x - r["centre"]) / 100
                + r["shift"] * (x > r["break_date"]))
        ax.plot(x, step, color="#111111", lw=2.0, label="one level shift")
        ax.axvline(r["break_date"], color="#111111", lw=0.9, ls=(0, (2, 2)), alpha=0.6)

        ax.set_title(pair.replace(" + ", "  +  "), fontsize=9.4, loc="left")
        verdict = (f"shift {r['shift']:+.2f} at {int(r['break_date'])}, q = {r['q_value']:.3f}"
                   if r["has_break"] else
                   f"no shift distinguishable (q = {r['q_value']:.2f})")
        ax.text(0.03, 0.06, verdict, transform=ax.transAxes, fontsize=7.0,
                color="#111111" if r["has_break"] else GREY)
        ax.tick_params(labelsize=7.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend(fontsize=7.2, loc="upper right")
    for ax in axes[-1]:
        ax.set_xlabel("Birth half-century")
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)")
    fig.suptitle("The domain structure does not drift. It steps.",
                 fontsize=12.5, x=0.05, ha="left", y=1.0)
    fig.text(0.05, -0.10,
             "The same six series carried no linear trend distinguishable from flat. Five of the six carry a level shift: "
             "three dated at 1750, two at 1550, and the pooled\nscan puts one common date at 1750. The two results are "
             "not in tension: a structure that holds a level and then moves to another has no trend to find. The vertical "
             "line\nmarks the best-fitting date even where the shift is not distinguishable. Grey dashed is the no-shift "
             "fit, black the fitted step. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figS06_domain_steps")


def main():
    mat, corr, labels, link = pooled_positions()
    blocks = pd.read_csv(NS / "sector_blocks_by_era.csv")
    image = pd.read_csv(NS / "blockmodel_image_by_era.csv")
    indices = pd.read_csv(NS / "network_indices_by_era.csv")
    coreness = pd.read_csv(NS / "coreness_by_era.csv")
    common = pd.read_csv(NS / "breakpoint_common_date.csv")
    sec_breaks = pd.read_csv(NS / "breakpoints_sector_pairs.csv")
    dom_breaks = pd.read_csv(NS / "breakpoints_domain_pairs.csv")
    dom_half = pd.read_csv(DATA / "domain_pair_association_by_halfcentury.csv")

    print("writing network-structure figures")
    figS01(mat, corr, labels, link)
    figS02(blocks, image)
    figS03(indices)
    figS04(coreness)
    figS05(common, sec_breaks, dom_breaks)
    figS06(dom_half, dom_breaks)


if __name__ == "__main__":
    main()
