"""Country-comparison figures.

Reads data/processed/countries/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from plotstyle import BLUE, CMAP, GREY, RED, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
CD = ROOT / "data" / "processed" / "countries"

PAIR_ORDER = ["Political + Security", "Ideational + Economic", "Political + Ideational",
              "Political + Economic", "Ideational + Security", "Economic + Security"]
DOMAIN_ORDER = ["Political", "Ideational", "Economic", "Security"]
DOMAIN_COLOUR = {"Political": "#4477AA", "Ideational": "#228833",
                 "Economic": "#CCBB44", "Security": "#EE6677"}
GROUP_COLOUR = {}
VLIM = 1.3

SOURCE = ("Source: BHHT cross-verified database of notable people "
          "(Laouenan et al., Scientific Data 9:290, 2022).")
CAVEAT = ("Country is the cross-verified citizenship of the source, projected onto modern states, so the label is "
          "anachronistic for anyone born before the state existed.\nCoverage is encyclopaedic coverage: how many "
          "elites a country contributes says as much about which Wikipedia editions write about it as about the "
          "country.")


def order_countries(clusters, coverage):
    c = clusters.merge(coverage[["country", "n_crossings"]], on="country",
                       suffixes=("", "_cov"))
    c = c.sort_values(["cluster", "n_crossings"], ascending=[True, False])
    return c


def assign_group_colours(clusters):
    palette = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#AA3377"]
    for k, name in enumerate(sorted(clusters["cluster"].unique())):
        GROUP_COLOUR[name] = palette[k % len(palette)]


# --------------------------------------------------------------------------- #
def figC01(coverage, clusters):
    cov = coverage[coverage["in_domain_panel"]].copy()
    cov = cov.merge(clusters[["country", "cluster"]], on="country", how="left")

    fig, axes = plt.subplots(1, 2, figsize=(13.6, 8.4), sharey=False)

    ax = axes[0]
    c = cov.sort_values("n_crossings")
    y = np.arange(len(c))
    ax.barh(y, c["n_crossings"], color=[GROUP_COLOUR.get(g, GREY) for g in c["cluster"]],
            height=0.72)
    ax.set_yticks(y)
    ax.set_yticklabels(c["country"], fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("elites crossing two domains (log scale)")
    ax.set_title("How much each country contributes", fontsize=10.5, loc="left", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    for yi, (_, r) in zip(y, c.iterrows()):
        ax.text(r["n_crossings"] * 1.08, yi, f"{int(r['n_crossings']):,}", va="center",
                fontsize=6.6, color=GREY)
    ax.set_xlim(700, 120000)

    ax = axes[1]
    c = cov.sort_values("crossing_rate")
    y = np.arange(len(c))
    ax.hlines(y, c["crossing_rate_ci_low"], c["crossing_rate_ci_high"],
              color=[GROUP_COLOUR.get(g, GREY) for g in c["cluster"]], lw=1.6, alpha=0.65)
    ax.scatter(c["crossing_rate"], y, s=34,
               color=[GROUP_COLOUR.get(g, GREY) for g in c["cluster"]], zorder=3)
    overall = coverage["n_crossings"].sum() / coverage["n_classified"].sum()
    ax.axvline(overall, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.text(overall, len(c) - 0.2, f"  all countries {overall:.0%}", fontsize=7.4,
            color=GREY, va="top")
    ax.set_yticks(y)
    ax.set_yticklabels(c["country"], fontsize=8)
    ax.set_xlabel("share of classified elites holding two of the four domains")
    ax.set_title("How often elites cross a domain boundary", fontsize=10.5, loc="left", pad=10)
    ax.spines[["top", "right"]].set_visible(False)

    handles = [Patch(color=col, label=name) for name, col in sorted(GROUP_COLOUR.items())]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8,
               bbox_to_anchor=(0.5, -0.055), title="Group by crossing profile (see figure C3)",
               title_fontsize=8)
    fig.suptitle("Thirty-six countries with at least 1,000 elites crossing two domains",
                 fontsize=12.5, x=0.045, ha="left", y=1.0)
    fig.text(0.045, -0.115,
             "These 36 countries hold 90% of all domain crossings in the database. Bars are 95% Wilson intervals.\n"
             + CAVEAT + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figC01_country_coverage")


def figC02(composition, order):
    wide = (composition.pivot(index="country", columns="domain",
                              values="share_of_classified")
            .reindex(columns=DOMAIN_ORDER))
    wide = wide.loc[wide["Political"].sort_values().index]
    y = np.arange(len(wide))

    fig, axes = plt.subplots(1, 2, figsize=(13.4, 8.2), sharey=True,
                            gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    left = np.zeros(len(wide))
    total = wide.sum(axis=1).to_numpy()
    for domain in DOMAIN_ORDER:
        v = wide[domain].to_numpy() / total
        ax.barh(y, v, left=left, color=DOMAIN_COLOUR[domain], height=0.76,
                edgecolor="white", linewidth=0.5, label=domain)
        left += v
    ax.set_yticks(y)
    ax.set_yticklabels(wide.index, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of domain memberships held")
    ax.set_title("What each country's elite is made of", fontsize=10.5, loc="left", pad=10)
    ax.legend(fontsize=7.6, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.11))
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    reach = (composition.pivot(index="country", columns="domain",
                               values="cross_domain_rate").reindex(wide.index))
    for domain in DOMAIN_ORDER:
        ax.scatter(reach[domain], y, s=30, color=DOMAIN_COLOUR[domain], label=domain,
                   alpha=0.9)
    ax.set_xlabel("share of that domain's holders who also hold another")
    ax.set_xlim(0, 1)
    ax.set_title("How far out of its own domain each reaches", fontsize=10.5,
                 loc="left", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    for yi in y:
        ax.axhspan(yi - 0.42, yi + 0.42, color="#f4f4f4", zorder=0, linewidth=0)

    fig.suptitle("Composition and reach, country by country",
                 fontsize=12.5, x=0.045, ha="left", y=1.0)
    fig.text(0.045, -0.085,
             "Left: memberships, not people, so a crosser counts in two domains and the bar sums to one. Countries are "
             "ordered by the political share.\nSecurity is the smallest domain almost everywhere and the one whose "
             "reach varies most. " + CAVEAT + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figC02_country_composition")


def figC03(dom, order, coverage):
    wide = dom.pivot(index="country", columns="pair", values="assoc_log2")[PAIR_ORDER]
    sig = dom.pivot(index="country", columns="pair", values="q_value")[PAIR_ORDER] < 0.05
    countries = order["country"].tolist()
    wide, sig = wide.loc[countries], sig.loc[countries]

    fig, ax = plt.subplots(figsize=(10.6, 10.4))
    data = wide.to_numpy(dtype=float)
    im = ax.imshow(data, cmap=CMAP, vmin=-VLIM, vmax=VLIM, aspect="auto")
    ax.set_xticks(range(len(PAIR_ORDER)))
    ax.set_xticklabels([p.replace(" + ", "\n+ ") for p in PAIR_ORDER], fontsize=8,
                       linespacing=1.1)
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries, fontsize=8)
    for t, c in zip(ax.get_yticklabels(), countries):
        t.set_color(GROUP_COLOUR[order.set_index("country").loc[c, "cluster"]])
    ax.set_xticks(np.arange(-0.5, len(PAIR_ORDER), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(countries), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isfinite(data[i, j]):
                continue
            ax.text(j, i, f"{data[i, j]:+.2f}", ha="center", va="center", fontsize=6.4,
                    color="white" if abs(data[i, j]) / VLIM > 0.62 else "#1a1a1a")
            if not bool(sig.iloc[i, j]):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="none",
                                           edgecolor="#777777", linewidth=0.0,
                                           hatch="////", zorder=4))
    groups = order["cluster"].tolist()
    cuts = [k for k in range(1, len(groups)) if groups[k] != groups[k - 1]]
    for c in cuts:
        ax.axhline(c - 0.5, color="#111111", lw=2.0)
    for name in sorted(set(groups)):
        idx = [k for k, g in enumerate(groups) if g == name]
        ax.text(-1.35, np.mean(idx), name.replace(" group", "\ngroup"), rotation=90,
                va="center", ha="center", fontsize=8.4, color=GROUP_COLOUR[name])
    cbar = fig.colorbar(im, ax=ax, shrink=0.42, pad=0.02, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.set_title("The six crossings, country by country",
                 fontsize=12.5, loc="left", pad=14)
    fig.text(0.0, -0.055,
             "Each country is fitted on its own, so its scores are net of its own domain sizes and comparable with "
             "another country's. Countries are grouped by\nWard clustering on the six scores and ordered by size "
             "inside each group; hatching marks a cell not distinguishable from the reference model (BH q $\\geq$ 0.05).\n"
             "Political with security is positive in 34 of the 36 countries and distinguishable from the reference "
             "model in 32 of them; Canada and New\nZealand are the two negatives.\n"
             + CAVEAT + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    save(fig, "figC03_country_crossing_matrix")


def figC04(dom, order, coverage):
    wide = dom.pivot(index="country", columns="pair", values="assoc_log2")[PAIR_ORDER]
    grp = order.set_index("country")["cluster"]
    size = coverage.set_index("country")["n_crossings"]

    panels = [("Political + Security", "Political + Economic",
               "Rule with coercion", "Rule with money"),
              ("Ideational + Security", "Economic + Security",
               "Ideas with coercion", "Money with coercion")]
    fig, axes = plt.subplots(1, 2, figsize=(14.4, 7.0))
    for ax, (xcol, ycol, xlab, ylab) in zip(axes, panels):
        x, y = wide[xcol], wide[ycol]
        s = 24 + np.sqrt(size.reindex(wide.index)) * 1.4
        ax.axhline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        for name in sorted(GROUP_COLOUR):
            m = grp.reindex(wide.index) == name
            ax.scatter(x[m], y[m], s=s[m], color=GROUP_COLOUR[name], alpha=0.85,
                       edgecolor="white", linewidth=0.6, label=name, zorder=3)
        for country in wide.index:
            ax.annotate(country, (x[country], y[country]), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=6.6, color="#333333")
        ax.set_xlabel(f"{xlab}   ({xcol})")
        ax.set_ylabel(f"{ylab}   ({ycol})")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=8, loc="lower left", title="Group", title_fontsize=8)
    fig.suptitle("A map of elite power structures",
                 fontsize=12.5, x=0.045, ha="left", y=1.0)
    fig.text(0.045, -0.085,
             "Both axes are log$_2$(observed / expected) inside the country. Point area scales with the number of "
             "crossings behind the country.\nThe same three countries occupy the unusual corner of both panels. Canada, "
             "Australia and New Zealand are the only ones where rule combines with money\nmore often than chance, the "
             "only ones where coercion combines with the ideational domain more often than chance, and two of the three "
             "are the only ones\nwhere rule does not combine with coercion. Everywhere else money is the domain that "
             "keeps its distance from both rule and coercion.\n" + CAVEAT + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figC04_country_map")


def figC05(dom, order):
    grp = order.set_index("country")["cluster"]
    fig, axes = plt.subplots(2, 3, figsize=(15.0, 10.0))
    for ax, pair in zip(axes.ravel(), PAIR_ORDER):
        g = dom[dom["pair"] == pair].sort_values("assoc_log2")
        y = np.arange(len(g))
        colours = [GROUP_COLOUR[grp[c]] for c in g["country"]]
        ax.hlines(y, g["assoc_ci_low"], g["assoc_ci_high"], color=colours, lw=1.3, alpha=0.6)
        ax.scatter(g["assoc_log2"], y, s=24, color=colours, zorder=3)
        ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        ax.set_yticks(y)
        ax.set_yticklabels(g["country"], fontsize=6.4)
        ax.set_title(pair.replace(" + ", "  +  "), fontsize=9.6, loc="left")
        ax.set_xlabel("log$_2$(obs / exp)", fontsize=8)
        ax.tick_params(axis="x", labelsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
    handles = [Patch(color=col, label=name) for name, col in sorted(GROUP_COLOUR.items())]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8,
               bbox_to_anchor=(0.5, -0.015))
    fig.suptitle("Every crossing, every country, ranked",
                 fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.055,
             "Bars are 95% bootstrap intervals. Political with ideational is the crossing on which countries barely "
             "differ, spanning 0.19 from end to end; money with\ncoercion spans 1.97. " + CAVEAT + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    save(fig, "figC05_crossings_ranked")


def figC06(sec, order):
    wide = sec.pivot(index="country", columns="pair", values="assoc_log2")
    counts = sec.pivot(index="country", columns="pair", values="n_pair")
    # Rank by spread across countries, but only among pairs that are estimable
    # everywhere. Without the floor the ranking fills up with small nobility pairs
    # whose spread is sampling noise.
    estimable = counts.min() >= 50
    pairs = wide.loc[:, estimable].std().sort_values(ascending=False).index.tolist()
    countries = [c for c in order["country"] if c in wide.index]
    m = wide.loc[countries, pairs]

    fig, ax = plt.subplots(figsize=(13.4, 7.6))
    data = m.to_numpy(dtype=float)
    lim = 3.0
    im = ax.imshow(data, cmap=CMAP, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(pairs)))
    ax.set_xticklabels([p.replace(" + ", "\n+ ") for p in pairs], fontsize=6.8,
                       rotation=45, ha="right", linespacing=1.1)
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries, fontsize=8)
    for t, c in zip(ax.get_yticklabels(), countries):
        t.set_color(GROUP_COLOUR[order.set_index("country").loc[c, "cluster"]])
    ax.set_xticks(np.arange(-0.5, len(pairs), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(countries), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if np.isfinite(data[i, j]):
                ax.text(j, i, f"{data[i, j]:+.1f}", ha="center", va="center", fontsize=5.8,
                        color="white" if abs(data[i, j]) / lim > 0.62 else "#1a1a1a")
    cbar = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.015, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.set_title("Where countries differ most at the level of sectors",
                 fontsize=12.0, loc="left", pad=12)
    fig.text(0.0, -0.20,
             f"The {len(pairs)} sector pairs combined by at least 50 elites in every one of the {len(countries)} "
             "countries with 5,000 or more elites spanning two sectors, ordered by how\nmuch the score varies across "
             "them. The floor matters: without it the ranking fills up with small nobility pairs whose spread is "
             "sampling noise. Countries keep\nthe grouping from the four-domain analysis, which was not fitted on any "
             "of these numbers. " + CAVEAT + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    save(fig, "figC06_country_sector_pairs")


def figC07(dom_era, order):
    both = (dom_era.groupby(["country", "pair"])["era"].nunique() == 2)
    keep = sorted({c for c, _ in both[both].index})
    if not keep:
        return
    grp = order.set_index("country")["cluster"]
    keep = [c for c in order["country"] if c in keep]

    fig, axes = plt.subplots(2, 3, figsize=(15.0, 9.0), sharey=True)
    for ax, pair in zip(axes.ravel(), PAIR_ORDER):
        g = dom_era[(dom_era["pair"] == pair) & (dom_era["country"].isin(keep))]
        piv = g.pivot(index="country", columns="era", values="assoc_log2").reindex(keep)
        y = np.arange(len(keep))[::-1]
        for yi, country in zip(y, keep):
            a, b = piv.loc[country, "1800-1899"], piv.loc[country, "1900-2020"]
            if not (np.isfinite(a) and np.isfinite(b)):
                continue
            colour = GROUP_COLOUR[grp[country]]
            ax.annotate("", xy=(b, yi), xytext=(a, yi),
                        arrowprops=dict(arrowstyle="-|>", color=colour, lw=1.4,
                                        alpha=0.85, shrinkA=0, shrinkB=0))
            ax.scatter([a], [yi], s=16, color=colour, alpha=0.5, zorder=3)
        ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        ax.set_yticks(y)
        ax.set_yticklabels(keep, fontsize=7)
        ax.set_title(pair.replace(" + ", "  +  "), fontsize=9.6, loc="left")
        ax.set_xlabel("log$_2$(obs / exp)", fontsize=8)
        ax.tick_params(axis="x", labelsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("From the nineteenth century to the twentieth, country by country",
                 fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.055,
             "Each arrow runs from the 1800-1899 birth cohort to the 1900-2020 one, for the 30 countries with at "
             "least 400 crossings in each. A dot with no arrow is a\ncountry that barely moved. Rule with coercion is "
             "the only crossing that moves one way: it rises in 25 of the 30, median +0.38. Money with coercion falls "
             "in 20 of\nthe 30, median -0.34, and the other four split about evenly. " + CAVEAT + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.97])
    save(fig, "figC07_country_change")


def main():
    coverage = pd.read_csv(CD / "country_coverage.csv")
    clusters = pd.read_csv(CD / "country_clusters.csv")
    composition = pd.read_csv(CD / "country_domain_composition.csv")
    dom = pd.read_csv(CD / "country_domain_pairs.csv")
    dom_era = pd.read_csv(CD / "country_domain_pairs_by_era.csv")
    sec = pd.read_csv(CD / "country_sector_pairs.csv")

    assign_group_colours(clusters)
    order = order_countries(clusters, coverage)

    print("writing country figures")
    figC01(coverage, clusters)
    figC02(composition, order)
    figC03(dom, order, coverage)
    figC04(dom, order, coverage)
    figC05(dom, order)
    figC06(sec, order)
    figC07(dom_era, order)


if __name__ == "__main__":
    main()
