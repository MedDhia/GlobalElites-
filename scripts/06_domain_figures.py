"""Figures for the four domains of elite power.

Reads the tables written by scripts/05_domain_associations.py and writes both a
PDF and a 300-dpi PNG for every figure into figures/.
"""

import pathlib
import textwrap

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from plotstyle import BLUE, CMAP, GREY, RED, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

DOMAINS = ["Political", "Ideational", "Economic", "Security"]
LONG = {"Political": "Political /\nregulatory", "Ideational": "Ideational /\nacademic",
        "Economic": "Economic /\nallocative", "Security": "Security /\nmilitary"}
ONE_LINE = {"Political": "Political / regulatory", "Ideational": "Ideational / academic",
            "Economic": "Economic / allocative", "Security": "Security / military"}
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]
PAIR_COLOUR = {
    "Political + Security": "#b2182b",
    "Ideational + Economic": "#ef8a62",
    "Political + Ideational": "#4d9221",
    "Political + Economic": "#67a9cf",
    "Ideational + Security": "#2166ac",
    "Economic + Security": "#053061",
}
VLIM = 1.2
# The two diagonals of the square layout cross at the centre; shift their labels
# off the crossing point so they stay readable.
DIAGONAL_OFFSET = {frozenset(("Political", "Economic")): 0.30,
                   frozenset(("Ideational", "Security")): 0.72}
SCOPE = ("Nobility, Kinship and Sport & Games are left unclassified: they name a mode of "
         "transmission or a form of celebrity, not a domain of power.")


def to_matrix(frame, value="assoc_log2"):
    mat = pd.DataFrame(np.nan, index=DOMAINS, columns=DOMAINS, dtype=float)
    for _, r in frame.iterrows():
        mat.loc[r["domain_a"], r["domain_b"]] = r[value]
        mat.loc[r["domain_b"], r["domain_a"]] = r[value]
    return mat


def draw_matrix(ax, mat, sig=None, annotate=True, labels=True, fontsize=8.5):
    data = mat.to_numpy(dtype=float)
    cmap = CMAP.with_extremes(bad="#f2f2f2")
    im = ax.imshow(np.ma.masked_invalid(data), cmap=cmap, vmin=-VLIM, vmax=VLIM)
    n = len(mat)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([LONG[d] for d in mat.columns] if labels else [""] * n,
                       fontsize=7, linespacing=0.95)
    ax.set_yticklabels([LONG[d] for d in mat.index] if labels else [""] * n,
                       fontsize=7, linespacing=0.95)
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(n):
        ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, facecolor="white",
                                   edgecolor="white", zorder=3))
    if sig is not None:
        for i in range(n):
            for j in range(n):
                if i != j and not bool(sig.iloc[i, j]) and np.isfinite(data[i, j]):
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="none",
                                               edgecolor="#777777", linewidth=0.0,
                                               hatch="////", zorder=4))
    if annotate:
        for i in range(n):
            for j in range(n):
                if i == j or not np.isfinite(data[i, j]):
                    continue
                shade = abs(data[i, j]) / VLIM
                ax.text(j, i, f"{data[i, j]:+.2f}", ha="center", va="center",
                        fontsize=fontsize, zorder=5,
                        color="white" if shade > 0.62 else "#1a1a1a")
    return im


# --------------------------------------------------------------------------- #
def figD01(overall):
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.4),
                             gridspec_kw={"width_ratios": [1, 1.25]})
    mat = to_matrix(overall)
    sig = to_matrix(overall.assign(s=(overall["q_value"] < 0.05).astype(float)), "s") == 1
    im = draw_matrix(axes[0], mat, sig=sig)
    cbar = fig.colorbar(im, ax=axes[0], shrink=0.78, pad=0.03, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    axes[0].set_title("Association between domains", fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    f = overall.sort_values("assoc_log2")
    y = np.arange(len(f))
    colours = [RED if v > 0 else BLUE for v in f["assoc_log2"]]
    ax.hlines(y, f["assoc_ci_low"], f["assoc_ci_high"], color=colours, lw=2.2, alpha=0.7)
    ax.scatter(f["assoc_log2"], y, color=colours, s=45, zorder=3)
    ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels([p.replace(" + ", "  +  ") for p in f["pair"]], fontsize=9)
    ax.set_xlim(-0.75, 1.55)
    ax.set_xlabel("log$_2$(observed / expected)")
    ax.spines[["top", "right"]].set_visible(False)
    for yi, (_, r) in zip(y, f.iterrows()):
        ax.text(0.78, yi, f"n = {int(r['n_pair']):,}   ({r['share_of_diversified']:.0%} of crossings)",
                fontsize=7.2, va="center", ha="left", color=GREY)
    ax.set_title("The six crossings, ranked", fontsize=10.5, loc="left", pad=10)

    fig.suptitle("Which domains of power do elites combine?\n"
                 "280,761 elites whose two coded sectors fall in two different domains",
                 fontsize=12.5, x=0.045, ha="left", y=1.06)
    fig.text(0.045, -0.10,
             "Expected counts come from a quasi-independence model refitted on the four domains, so the scores are net of "
             "how many elites each domain holds.\nIntervals are 95% percentile bootstrap, 2,000 draws. " + SCOPE
             + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figD01_domain_association_overall")


def figD02(by_half, trends):
    tr = trends[trends["grid"] == "halfcentury"].set_index("pair")
    order = ["Political + Security", "Ideational + Economic", "Political + Ideational",
             "Political + Economic", "Ideational + Security", "Economic + Security"]
    fig, axes = plt.subplots(2, 3, figsize=(13.6, 6.8), sharex=True, sharey=True)
    for ax, pair in zip(axes.ravel(), order):
        g = by_half[by_half["pair"] == pair].sort_values("period")
        colour = PAIR_COLOUR[pair]
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        ax.fill_between(g["period"], g["assoc_ci_low"], g["assoc_ci_high"],
                        color=colour, alpha=0.2, linewidth=0)
        ax.plot(g["period"], g["assoc_log2"], color=colour, lw=1.9, marker="o", ms=3.6)
        row = tr.loc[pair]
        ax.set_title(pair.replace(" + ", "  +  "), fontsize=9.5, loc="left")
        ax.text(0.03, 0.06,
                f"{row['slope_per_century']:+.2f} per century "
                f"[{row['slope_ci_low']:+.2f}, {row['slope_ci_high']:+.2f}], q = {row['q_value']:.2f}",
                transform=ax.transAxes, fontsize=6.9, color=GREY)
        ax.tick_params(labelsize=7.5)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("Birth half-century")
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)")
    fig.suptitle("Each crossing across the modern period, 1400 to 1949",
                 fontsize=12.5, x=0.05, ha="left", y=1.0)
    fig.text(0.05, -0.12,
             "Half-century birth cohorts with 95% bootstrap intervals. No pair carries a trend distinguishable from flat "
             "once the six tests are adjusted:\nat this level of aggregation the association structure is close to "
             "stationary, and the movement visible in the 13-sector layer is largely\nreorganisation inside domains "
             "not across them. The one visible break is around 1800, when four of the six move toward zero.\n"
             + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    save(fig, "figD02_crossing_trajectories")


def figD03(by_era):
    fig, axes = plt.subplots(1, 6, figsize=(17.0, 3.9))
    im = None
    for k, (ax, era) in enumerate(zip(axes, ERA_ORDER)):
        sub = by_era[by_era["period"] == era]
        if sub.empty:
            ax.axis("off")
            continue
        mat = to_matrix(sub)
        sig = to_matrix(sub.assign(s=(sub["q_value"] < 0.05).astype(float)), "s") == 1
        im = draw_matrix(ax, mat, sig=sig, labels=(k == 0), fontsize=7)
        n = int(sub["n_diversified_period"].iloc[0])
        ax.set_title(f"{era}\nn = {n:,} crossings", fontsize=8.6, loc="left", pad=6)
    cbar = fig.colorbar(im, ax=axes, shrink=0.72, pad=0.012, extend="both")
    cbar.set_label("log$_2$(obs / exp)", fontsize=7.5)
    cbar.ax.tick_params(labelsize=7)
    fig.suptitle("The four-domain association matrix, era by era",
                 fontsize=12.5, x=0.045, ha="left", y=1.14)
    fig.text(0.045, -0.14,
             "Each panel refits the model within the cohort. Hatching marks a cell not distinguishable from the "
             "reference model (BH q $\\geq$ 0.05).\nThe political-security cell is the only one positive in every era. "
             + SOURCE, fontsize=7.4, color=GREY, ha="left")
    save(fig, "figD03_domain_matrix_by_era")


def figD04(by_era, marginals):
    pos = {"Political": (-1, 1), "Ideational": (1, 1),
           "Economic": (1, -1), "Security": (-1, -1)}
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.6))
    for ax, era in zip(axes.ravel(), ERA_ORDER):
        sub = by_era[by_era["period"] == era]
        shares = (marginals[(marginals["period_type"] == "era") & (marginals["period"] == era)]
                  .set_index("domain")["share_of_classified"].reindex(DOMAINS).fillna(0))
        graph = nx.Graph()
        graph.add_nodes_from(DOMAINS)
        for _, r in sub.iterrows():
            if r["q_value"] < 0.05:
                graph.add_edge(r["domain_a"], r["domain_b"], w=r["assoc_log2"])
        edges = list(graph.edges())
        widths = [0.8 + min(abs(graph[u][v]["w"]), VLIM) * 4.0 for u, v in edges]
        colours = [CMAP(0.5 + np.clip(graph[u][v]["w"], -VLIM, VLIM) / (2 * VLIM))
                   for u, v in edges]
        styles = ["-" if graph[u][v]["w"] > 0 else (0, (3, 2)) for u, v in edges]
        for (u, v), w, c, st in zip(edges, widths, colours, styles):
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                    lw=w, color=c, ls=st, zorder=1, solid_capstyle="round")
            t = DIAGONAL_OFFSET.get(frozenset((u, v)), 0.5)
            mx = pos[u][0] + t * (pos[v][0] - pos[u][0])
            my = pos[u][1] + t * (pos[v][1] - pos[u][1])
            ax.text(mx, my, f"{graph[u][v]['w']:+.2f}", fontsize=7, ha="center", va="center",
                    zorder=4, bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none",
                                        alpha=0.88))
        for d in DOMAINS:
            x, y = pos[d]
            ax.scatter([x], [y], s=200 + shares[d] * 2600, facecolor="white",
                       edgecolor="#333333", linewidth=1.0, zorder=3)
            ax.text(x * 1.42, y * 1.42, f"{LONG[d]}\n{shares[d]:.0%}", ha="center",
                    va="center", fontsize=7.4, linespacing=1.15)
        n = int(sub["n_diversified_period"].iloc[0])
        ax.set_title(f"{era}   (n = {n:,})", fontsize=10, loc="left")
        ax.set_xlim(-2.0, 2.0)
        ax.set_ylim(-1.85, 1.85)
        ax.axis("off")
    handles = [Line2D([], [], color=RED, lw=3.0, label="association (combined more than expected)"),
               Line2D([], [], color=BLUE, lw=3.0, ls=(0, (3, 2)),
                      label="dissociation (combined less than expected)"),
               Line2D([], [], marker="o", color="none", markerfacecolor="white",
                      markeredgecolor="#333333", markersize=10,
                      label="node area and % = share of classified elites holding the domain")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.2,
               bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("The four domains as a network, era by era",
                 fontsize=12.5, x=0.05, ha="left", y=0.985)
    fig.text(0.05, 0.055,
             "Every edge shown passes BH q < 0.05; width and colour scale with the association score, printed on the edge. "
             + SCOPE + "\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.075, 1, 0.955])
    save(fig, "figD04_domain_networks_by_era")


def figD05(crossing, crossing_region, consolidation, marginals):
    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.6))

    ax = axes[0]
    ax.plot(crossing["birth_century"], crossing["crossing_rate"], color=RED, lw=2.0,
            marker="o", ms=4.2, label="crosses two domains")
    ax.plot(consolidation["birth_century"], consolidation["share_within_domain"],
            color=BLUE, lw=1.8, marker="s", ms=3.8, ls=(0, (4, 2)),
            label="of two-sector elites,\nboth sectors in one domain")
    ax.set_ylim(0, 0.88)
    ax.set_xlim(760, 1950)
    ax.set_xlabel("Birth century")
    ax.set_ylabel("Share")
    ax.set_title("Crossing and consolidation", fontsize=10, loc="left")
    ax.legend(fontsize=7.4, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    palette = {"Europe": RED, "America": BLUE, "Asia": "#1b7837",
               "Africa": "#e08214", "Oceania": "#762a83"}
    for region, grp in crossing_region.groupby("region"):
        if region not in palette:
            continue
        grp = grp[grp["n_classified"] >= 150].sort_values("birth_century")
        if len(grp) < 3:
            continue
        ax.plot(grp["birth_century"], grp["crossing_rate"], color=palette[region],
                lw=1.7, marker="o", ms=3.2, label=region)
    ax.set_ylim(0, 0.45)
    ax.set_xlabel("Birth century")
    ax.set_title("Crossing rate by world region", fontsize=10, loc="left")
    ax.legend(fontsize=7.4, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    cent = marginals[marginals["period_type"] == "century"].copy()
    cent["period"] = cent["period"].astype(int)
    for domain in DOMAINS:
        g = cent[cent["domain"] == domain].sort_values("period")
        g = g[g["n_holders"] >= 100]
        ax.plot(g["period"], g["cross_domain_rate"], lw=1.8, marker="o", ms=3.4,
                label=ONE_LINE[domain])
    ax.set_ylim(0, 0.85)
    ax.set_xlabel("Birth century")
    ax.set_title("Reach out of each domain", fontsize=10, loc="left")
    ax.legend(fontsize=7.4, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("How often elites held power in two of the four domains",
                 fontsize=12.5, x=0.05, ha="left", y=1.04)
    fig.text(0.05, -0.11,
             "Left: the share of classified elites crossing a domain boundary rises to a peak in the 1700s and falls "
             "afterwards, while roughly half of all two-sector\nelites in every century combine sectors inside one "
             "domain. Right: economic and security elites are the most likely to hold a second domain, ideational "
             "elites\nthe least. Modern levels are pulled down by shorter biographies, so read the ordering across "
             "domains ahead of the level. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figD05_crossing_rates")


def figD06(reach):
    fig, axes = plt.subplots(1, 6, figsize=(17.0, 3.9))
    im = None
    for k, (ax, era) in enumerate(zip(axes, ERA_ORDER)):
        sub = reach[(reach["period_type"] == "era") & (reach["period"] == era)]
        if sub.empty:
            ax.axis("off")
            continue
        mat = (sub.pivot(index="from_domain", columns="to_domain", values="reach")
               .reindex(index=DOMAINS, columns=DOMAINS))
        im = ax.imshow(np.ma.masked_invalid(mat.to_numpy(dtype=float)),
                       cmap="magma_r", vmin=0, vmax=0.5)
        n = len(DOMAINS)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels([LONG[d] for d in DOMAINS], fontsize=6.6, linespacing=0.95)
        ax.set_yticklabels([LONG[d] for d in DOMAINS] if k == 0 else [""] * n,
                           fontsize=6.6, linespacing=0.95)
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        for i in range(n):
            ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, facecolor="white",
                                       edgecolor="white", zorder=3))
            for j in range(n):
                if i == j or not np.isfinite(mat.to_numpy()[i, j]):
                    continue
                v = mat.to_numpy()[i, j]
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=7,
                        color="white" if v > 0.32 else "#1a1a1a", zorder=5)
        ax.set_title(era, fontsize=9, loc="left", pad=6)
    cbar = fig.colorbar(im, ax=axes, shrink=0.72, pad=0.012)
    cbar.set_label("share reaching into the column domain", fontsize=7.2)
    cbar.ax.tick_params(labelsize=7)
    fig.suptitle("Reach: of the elites holding the row domain, what share also hold the column domain",
                 fontsize=12.0, x=0.045, ha="left", y=1.16)
    fig.text(0.045, -0.16,
             "Directional and unnormalised, so large domains attract high reach from everywhere. Read alongside the "
             "association matrices, which remove that size effect.\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    save(fig, "figD06_domain_reach_by_era")


def figD07(portfolio):
    cent = portfolio[portfolio["period_type"] == "century"].copy()
    cent["period"] = cent["period"].astype(int)
    order = [f"{d} only" for d in DOMAINS] + [
        "Political + Ideational", "Political + Economic", "Political + Security",
        "Ideational + Economic", "Ideational + Security", "Economic + Security"]
    wide = (cent.pivot(index="period", columns="portfolio", values="share_of_classified")
            .reindex(columns=order).fillna(0).sort_index())
    singles = plt.get_cmap("Greys")(np.linspace(0.10, 0.66, 4))
    crosses = [PAIR_COLOUR[p] for p in order[4:]]
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    ax.stackplot(wide.index, wide.to_numpy().T, labels=wide.columns,
                 colors=list(singles) + crosses, edgecolor="white", linewidth=0.4)
    ax.set_xlim(wide.index.min(), wide.index.max())
    ax.set_ylim(0, 1)
    ax.set_xlabel("Birth century")
    ax.set_ylabel("Share of classified elites")
    ax.set_title("Portfolios of power, century by century",
                 fontsize=11.5, loc="left", pad=10)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc="center left", bbox_to_anchor=(1.01, 0.5),
              fontsize=7.8, title="Domains held", title_fontsize=8.2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.0, -0.06,
             "Greys are elites confined to one domain, colours the six crossings. The ideational domain dominates the "
             "single-domain block throughout, which\nis as much a fact about who gets written about as about who held "
             "power. " + SCOPE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    save(fig, "figD07_portfolio_composition")


def figD08(by_er):
    modern = by_er[by_er["era"].isin(["1800-1899", "1900-2020"])]
    regions = [r for r in ["Europe", "America", "Asia", "Africa", "Oceania"]
               if r in set(modern["region"])]
    order = (modern.groupby("pair")["assoc_log2"].mean().sort_values().index.tolist())
    palette = {"Europe": RED, "America": BLUE, "Asia": "#1b7837",
               "Africa": "#e08214", "Oceania": "#762a83"}
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.8), sharey=True)
    for ax, era in zip(axes, ["1800-1899", "1900-2020"]):
        sub = modern[modern["era"] == era]
        y = np.arange(len(order))
        for k, region in enumerate(regions):
            g = sub[sub["region"] == region].set_index("pair").reindex(order)
            offset = (k - (len(regions) - 1) / 2) * 0.13
            ax.scatter(g["assoc_log2"], y + offset, s=34, color=palette[region],
                       label=region if era == "1800-1899" else None, zorder=3)
        ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        for yi in y:
            ax.axhline(yi, color="#f0f0f0", lw=22, zorder=0)
        ax.set_yticks(y)
        ax.set_yticklabels([p.replace(" + ", "  +  ") for p in order], fontsize=8.4)
        ax.set_title(era, fontsize=10.5, loc="left")
        ax.set_xlabel("log$_2$(observed / expected)")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=8, loc="lower right", title="Region", title_fontsize=8)
    fig.suptitle("The same crossing, different continents",
                 fontsize=12.5, x=0.045, ha="left", y=1.02)
    fig.text(0.045, -0.10,
             "Region is the UN region of the elite's area of attachment. A region enters an era once it has 3,000 "
             "elites in it.\n" + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figD08_regional_variation")


def main():
    overall = pd.read_csv(DATA / "domain_pair_association_overall.csv")
    by_era = pd.read_csv(DATA / "domain_pair_association_by_era.csv")
    by_half = pd.read_csv(DATA / "domain_pair_association_by_halfcentury.csv")
    by_er = pd.read_csv(DATA / "domain_pair_association_by_era_region.csv")
    trends = pd.read_csv(DATA / "domain_pair_trends.csv")
    marginals = pd.read_csv(DATA / "domain_marginals_by_period.csv")
    portfolio = pd.read_csv(DATA / "domain_portfolio_by_period.csv")
    reach = pd.read_csv(DATA / "domain_reach_by_period.csv")
    crossing = pd.read_csv(DATA / "crossing_by_period.csv")
    crossing_region = pd.read_csv(DATA / "crossing_by_region_period.csv")
    consolidation = pd.read_csv(DATA / "consolidation_by_period.csv")

    print("writing domain figures")
    figD01(overall)
    figD02(by_half, trends)
    figD03(by_era)
    figD04(by_era, marginals)
    figD05(crossing, crossing_region, consolidation, marginals)
    figD06(reach)
    figD07(portfolio)
    figD08(by_er)


if __name__ == "__main__":
    main()
