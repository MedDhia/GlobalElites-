"""Figures on the association and dissociation of elite power sectors.

Reads the tables written by scripts/02_sector_associations.py and writes both a
PDF and a 300-dpi PNG for every figure into figures/.
"""

import pathlib
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

mpl.use("Agg")

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

SECTOR_ORDER = [
    "Politics", "Administration & Law", "Military", "Religion", "Nobility",
    "Kinship", "Big business", "Small business", "Academia",
    "Exploration & Invention", "Culture (core)", "Culture (periphery)",
    "Sport & Games",
]
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]

SHORT = {
    "Administration & Law": "Admin. & Law",
    "Exploration & Invention": "Exploration\n& Invention",
    "Culture (core)": "Culture\n(core)",
    "Culture (periphery)": "Culture\n(periphery)",
    "Sport & Games": "Sport\n& Games",
    "Big business": "Big business",
    "Small business": "Small business",
}

CMAP = plt.get_cmap("RdBu_r")
VLIM = 3.0
GREY = "#4d4d4d"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "axes.edgecolor": GREY,
    "axes.linewidth": 0.7,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "text.color": "#1a1a1a",
    "axes.labelcolor": "#1a1a1a",
    "figure.dpi": 110,
    "savefig.bbox": "tight",
    "legend.frameon": False,
})

SOURCE = ("Source: BHHT cross-verified database of notable people "
          "(Laouenan et al., Scientific Data 9:290, 2022).")


def save(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(FIGS / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    print(f"  figures/{name}.pdf / .png")


def to_matrix(frame: pd.DataFrame, value: str = "assoc_log2") -> pd.DataFrame:
    mat = pd.DataFrame(np.nan, index=SECTOR_ORDER, columns=SECTOR_ORDER, dtype=float)
    for _, r in frame.iterrows():
        mat.loc[r["sector_a"], r["sector_b"]] = r[value]
        mat.loc[r["sector_b"], r["sector_a"]] = r[value]
    return mat


def draw_matrix(ax, mat: pd.DataFrame, sig: pd.DataFrame | None = None,
                annotate: bool = False, counts: pd.DataFrame | None = None,
                xlabels: bool = True, ylabels: bool = True):
    data = mat.to_numpy(dtype=float)
    masked = np.ma.masked_invalid(data)
    cmap = CMAP.with_extremes(bad="#f2f2f2")
    im = ax.imshow(masked, cmap=cmap, vmin=-VLIM, vmax=VLIM)
    n = len(mat)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(mat.columns if xlabels else [""] * n, rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels(mat.index if ylabels else [""] * n, fontsize=7)
    ax.tick_params(length=3)
    if not xlabels:
        ax.tick_params(axis="x", length=0)
    if not ylabels:
        ax.tick_params(axis="y", length=0)
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    # the diagonal is excluded by design: a person cannot pair a sector with itself
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
    if annotate and counts is not None:
        for i in range(n):
            for j in range(n):
                if i == j or not np.isfinite(data[i, j]):
                    continue
                shade = abs(data[i, j]) / VLIM
                ax.text(j, i, f"{data[i, j]:+.1f}", ha="center", va="center",
                        fontsize=5.6, zorder=5,
                        color="white" if shade > 0.62 else "#1a1a1a")
    return im


# --------------------------------------------------------------------------- #
def fig01_overall(overall: pd.DataFrame) -> None:
    mat = to_matrix(overall)
    sig = to_matrix(overall.assign(s=(overall["q_value"] < 0.05).astype(float)), "s") == 1
    counts = to_matrix(overall, "n_pair")

    fig, ax = plt.subplots(figsize=(7.4, 6.6))
    im = draw_matrix(ax, mat, sig=sig, annotate=True, counts=counts)
    cbar = fig.colorbar(im, ax=ax, shrink=0.72, pad=0.02, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.text(0.5, 1.04, "combined more", transform=cbar.ax.transAxes, ha="center",
                 fontsize=6.6, color="#b2182b")
    cbar.ax.text(0.5, -0.07, "combined less", transform=cbar.ax.transAxes, ha="center",
                 fontsize=6.6, color="#2166ac")
    cbar.ax.tick_params(labelsize=7)
    ax.set_title("Which sectors of power do elites combine?\n"
                 "Pairwise association under quasi-independence, 3500 BCE to 2020 CE",
                 fontsize=11, pad=12, loc="left")
    fig.text(0.0, -0.045,
             "Cells give log$_2$ of observed over expected co-occurrence among the 723,260 elites coded in two "
             "distinct sectors.\nRed = combined more often than the sector marginals imply; blue = combined less "
             "often. Hatching marks a pair whose\ndeparture from the reference model is not distinguishable from "
             "zero (BH q $\\geq$ 0.05). " + SOURCE,
             fontsize=6.8, color=GREY, ha="left", va="top")
    save(fig, "fig01_association_matrix_overall")


def fig02_by_era(by_era: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(15.6, 9.8))
    fig.subplots_adjust(wspace=0.10, hspace=0.06)
    im = None
    for k, (ax, era) in enumerate(zip(axes.ravel(), ERA_ORDER)):
        sub = by_era[by_era["period"] == era]
        if sub.empty:
            ax.axis("off")
            continue
        mat = to_matrix(sub)
        sig = to_matrix(sub.assign(s=(sub["q_value"] < 0.05).astype(float)), "s") == 1
        im = draw_matrix(ax, mat, sig=sig, xlabels=(k >= 3), ylabels=(k % 3 == 0))
        n = int(sub["n_diversified_period"].iloc[0])
        ax.set_title(f"{era}   (n = {n:,} two-sector elites)", fontsize=9.5, loc="left", pad=6)
    cbar = fig.colorbar(im, ax=axes, shrink=0.45, pad=0.02, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    fig.suptitle("The pairing of power sectors, by birth cohort of the elite",
                 fontsize=13, x=0.06, ha="left", y=0.975)
    fig.text(0.06, 0.045,
             "Each panel refits the quasi-independence model within the cohort, so the colours describe pairing "
             "net of how large each sector is in that period.\nHatching marks pairs not distinguishable from the "
             "reference model (BH q $\\geq$ 0.05). " + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    save(fig, "fig02_association_matrix_by_era")


def fig03_trajectories(by_century: pd.DataFrame, trends: pd.DataFrame) -> None:
    picked = pd.concat([trends.nsmallest(6, "slope_per_century"),
                        trends.nlargest(6, "slope_per_century")])
    picked = picked.sort_values("slope_per_century")

    fig, axes = plt.subplots(3, 4, figsize=(14.2, 8.4), sharex=True)
    for ax, (_, row) in zip(axes.ravel(), picked.iterrows()):
        g = by_century[by_century["pair"] == row["pair"]].sort_values("period")
        x = g["period"].to_numpy()
        y = g["assoc_log2"].to_numpy()
        colour = "#b2182b" if row["slope_per_century"] > 0 else "#2166ac"
        ax.axhline(0, color=GREY, lw=0.7, ls=(0, (4, 3)))
        ax.fill_between(x, g["assoc_ci_low"], g["assoc_ci_high"],
                        color=colour, alpha=0.18, linewidth=0)
        ax.plot(x, y, color=colour, lw=1.6, marker="o", ms=3.2)
        label = "converging" if row["slope_per_century"] > 0 else "diverging"
        ax.set_title(textwrap.fill(row["pair"], 34), fontsize=8.4, loc="left")
        ax.text(0.03, 0.06,
                f"{row['slope_per_century']:+.2f} per century  ({label}, q = {row['q_value']:.3f})",
                transform=ax.transAxes, fontsize=6.8, color=colour)
        ax.tick_params(labelsize=7)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("Birth century", fontsize=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)", fontsize=8)
    fig.suptitle("Sector pairs that moved most: the six that pulled apart and the six that came together",
                 fontsize=12.5, x=0.055, ha="left", y=0.985)
    fig.text(0.055, 0.005,
             "Points are cohort-specific association scores with 95% bootstrap intervals. Slopes come from "
             "inverse-variance weighted regressions of the score on century, 800 to 1900.\n" + SOURCE,
             fontsize=7, color=GREY, ha="left")
    fig.tight_layout(rect=[0.0, 0.03, 1.0, 0.955])
    save(fig, "fig03_pair_trajectories")


def fig04_networks(by_era: pd.DataFrame, marginals: pd.DataFrame) -> None:
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, len(SECTOR_ORDER), endpoint=False)
    pos = {s: (np.cos(a), np.sin(a)) for s, a in zip(SECTOR_ORDER, angles)}

    fig, axes = plt.subplots(2, 3, figsize=(14.6, 9.8))
    for ax, era in zip(axes.ravel(), ERA_ORDER):
        sub = by_era[(by_era["period"] == era) & (by_era["q_value"] < 0.05)]
        shares = (marginals[(marginals["period_type"] == "era") & (marginals["period"] == era)]
                  .set_index("sector")["share_of_elites_main"].reindex(SECTOR_ORDER).fillna(0))
        graph = nx.Graph()
        graph.add_nodes_from(SECTOR_ORDER)
        for _, r in sub.iterrows():
            if r["assoc_log2"] >= 0.5:
                graph.add_edge(r["sector_a"], r["sector_b"], w=r["assoc_log2"])

        pos_edges = sorted(((u, v) for u, v, d in graph.edges(data=True) if d["w"] > 0),
                           key=lambda e: graph[e[0]][e[1]]["w"])
        widths_p = [0.6 + min(graph[u][v]["w"], 3.0) * 1.4 for u, v in pos_edges]
        shades = [CMAP(0.5 + min(graph[u][v]["w"], 3.0) / (2 * VLIM)) for u, v in pos_edges]
        nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=pos_edges, width=widths_p,
                               edge_color=shades, alpha=0.9)
        sizes = 110 + shares.to_numpy() * 1900
        nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=SECTOR_ORDER,
                               node_size=sizes, node_color="white",
                               edgecolors="#333333", linewidths=0.9)
        for s, (x, y) in pos.items():
            ax.text(x * 1.36, y * 1.36, SHORT.get(s, s), ha="center", va="center",
                    fontsize=7.0, color="#1a1a1a")
        n = int(by_era.loc[by_era["period"] == era, "n_diversified_period"].iloc[0])
        ax.set_title(f"{era}   (n = {n:,})", fontsize=10, loc="left")
        ax.set_xlim(-1.9, 1.9)
        ax.set_ylim(-1.62, 1.62)
        ax.axis("off")

    handles = [Line2D([], [], color=CMAP(0.62), lw=1.6, label="log$_2$ obs/exp $\\approx$ +0.7"),
               Line2D([], [], color=CMAP(0.78), lw=3.2, label="$\\approx$ +1.7"),
               Line2D([], [], color=CMAP(0.95), lw=4.8, label="$\\geq$ +2.7"),
               Line2D([], [], marker="o", color="none", markerfacecolor="white",
                      markeredgecolor="#333333", markersize=9,
                      label="node area = share of elites whose main sector it is")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, 0.012))
    fig.suptitle("The architecture of elite power, era by era",
                 fontsize=13, x=0.06, ha="left", y=0.975)
    fig.text(0.06, 0.055,
             "Only associations are drawn: an edge appears where a pair is combined at least 1.4 times more often "
             "than quasi-independence implies (log$_2$ obs/exp $\\geq$ 0.5) at BH q < 0.05.\nWidth and colour scale "
             "with the excess. Dissociations are in Figures 1 and 2.\n" + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    fig.tight_layout(rect=[0.0, 0.07, 1.0, 0.955])
    save(fig, "fig04_sector_networks_by_era")


def fig05_diversification(div: pd.DataFrame, div_region: pd.DataFrame,
                          marginals: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.5))

    ax = axes[0]
    ax.plot(div["birth_century"], div["diversification_rate"], color="#b2182b",
            lw=2.0, marker="o", ms=4)
    ax.set_ylim(0, 0.8)
    ax.set_xlim(740, 1990)
    ax.set_xlabel("Birth century")
    ax.set_ylabel("Share of elites spanning two sectors")
    ax.set_title("All elites", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    for _, r in div.iterrows():
        if r["birth_century"] in (800, 1500, 1900):
            ax.annotate(f"{r['diversification_rate']:.0%}",
                        (r["birth_century"], r["diversification_rate"]),
                        textcoords="offset points", xytext=(0, 10), fontsize=7,
                        ha="center", color="#b2182b")

    ax = axes[1]
    palette = {"Europe": "#b2182b", "America": "#2166ac", "Asia": "#1b7837",
               "Africa": "#e08214", "Oceania": "#762a83"}
    for region, grp in div_region.groupby("region"):
        if region not in palette:
            continue
        grp = grp[grp["n_elites"] >= 150].sort_values("birth_century")
        if len(grp) < 3:
            continue
        ax.plot(grp["birth_century"], grp["diversification_rate"],
                color=palette[region], lw=1.7, marker="o", ms=3.2, label=region)
    ax.set_ylim(0, 0.9)
    ax.set_xlabel("Birth century")
    ax.set_title("By world region", fontsize=10, loc="left")
    ax.legend(fontsize=7.5, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    cent = marginals[marginals["period_type"] == "century"].copy()
    cent["period"] = cent["period"].astype(int)
    mat = (cent.pivot(index="sector", columns="period", values="diversification_rate")
           .reindex(SECTOR_ORDER).sort_index(axis=1))
    cmap = plt.get_cmap("magma_r").with_extremes(bad="#e8e8e8")
    im = ax.imshow(np.ma.masked_invalid(mat.to_numpy(dtype=float)), cmap=cmap,
                   vmin=0.1, vmax=0.9, aspect="auto")
    ax.set_xticks(range(len(mat.columns)))
    ax.set_xticklabels([int(c) for c in mat.columns], rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(mat)))
    ax.set_yticklabels(mat.index, fontsize=7)
    ax.set_title("By main sector", fontsize=10, loc="left")
    ax.set_xlabel("Birth century")
    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("share spanning two sectors", fontsize=7.5, )
    cbar.ax.tick_params(labelsize=7)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.suptitle("How often elites drew on a second sector at all",
                 fontsize=12.5, x=0.055, ha="left", y=1.02)
    fig.text(0.055, -0.09,
             "The long decline is partly behavioural specialisation and partly a source effect: modern "
             "biographies are far more numerous and often shorter, which\ngives the coder less to work with. "
             "Read the level cautiously and the ordering across sectors with more confidence. " + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "fig05_diversification_rates")


def fig06_ranked(overall: pd.DataFrame) -> None:
    top = overall.nlargest(20, "assoc_log2")
    bottom = overall.nsmallest(20, "assoc_log2")
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.4), sharex=True)
    for ax, frame, title, colour in (
        (axes[0], top.sort_values("assoc_log2"), "Combined more often than chance", "#b2182b"),
        (axes[1], bottom.sort_values("assoc_log2", ascending=False),
         "Combined less often than chance", "#2166ac"),
    ):
        y = np.arange(len(frame))
        ax.hlines(y, frame["assoc_ci_low"], frame["assoc_ci_high"], color=colour, lw=1.6, alpha=0.65)
        ax.scatter(frame["assoc_log2"], y, color=colour, s=26, zorder=3)
        ax.axvline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        ax.set_yticks(y)
        ax.set_yticklabels(frame["pair"], fontsize=7.6)
        ax.set_title(title, fontsize=10.5, loc="left")
        ax.set_xlabel("log$_2$(observed / expected)")
        ax.spines[["top", "right"]].set_visible(False)
        for yi, (_, r) in zip(y, frame.iterrows()):
            ax.text(r["assoc_ci_high"] + 0.22 if r["assoc_log2"] > 0 else r["assoc_ci_low"] - 0.22,
                    yi, f"n = {int(r['n_pair']):,}", fontsize=6.4, va="center",
                    ha="left" if r["assoc_log2"] > 0 else "right", color=GREY)
    axes[0].set_xlim(-3.4, 3.9)
    fig.suptitle("The twenty tightest and the twenty most avoided combinations of power sectors",
                 fontsize=12.5, x=0.045, ha="left", y=0.99)
    fig.text(0.045, -0.02,
             "Pooled over the whole record. Bars are 95% bootstrap intervals on the association score. " + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.955])
    save(fig, "fig06_ranked_pairs")


def fig07_trends(trends: pd.DataFrame) -> None:
    tr = trends.sort_values("slope_per_century").reset_index(drop=True)
    colours = {"converging": "#b2182b", "diverging": "#2166ac", "flat": "#999999"}
    fig, ax = plt.subplots(figsize=(8.6, 12.4))
    y = np.arange(len(tr))
    for yi, (_, r) in zip(y, tr.iterrows()):
        c = colours[r["trend"]]
        ax.hlines(yi, r["slope_ci_low"], r["slope_ci_high"], color=c, lw=1.5, alpha=0.6)
        ax.scatter(r["slope_per_century"], yi, color=c, s=22, zorder=3)
    ax.axvline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels(tr["pair"], fontsize=6.8)
    ax.set_ylim(-1, len(tr))
    ax.set_xlabel("Change in log$_2$(observed / expected) per century, 800 to 1900")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [Patch(color=colours[k], label=lab) for k, lab in
               (("converging", "converging (q < 0.05)"),
                ("diverging", "pulling apart (q < 0.05)"),
                ("flat", "no detectable trend"))]
    ax.legend(handles=handles, fontsize=8, loc="lower right")
    ax.set_title("Every sector pair, ranked by how its association moved across a millennium",
                 fontsize=11.5, loc="left", pad=12)
    fig.text(0.0, -0.012,
             "Inverse-variance weighted regressions of the cohort association score on birth century. "
             "Bars are 95% intervals. " + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    save(fig, "fig07_pair_trend_slopes")


def fig08_composition(marginals: pd.DataFrame) -> None:
    cent = marginals[marginals["period_type"] == "century"].copy()
    cent["period"] = cent["period"].astype(int)
    wide = (cent.pivot(index="period", columns="sector", values="share_of_elites_main")
            .reindex(columns=SECTOR_ORDER).fillna(0).sort_index())
    colours = plt.get_cmap("tab20")(np.linspace(0, 1, 20))[:len(SECTOR_ORDER)]
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    ax.stackplot(wide.index, wide.to_numpy().T, labels=wide.columns,
                 colors=colours, edgecolor="white", linewidth=0.4)
    ax.set_xlim(wide.index.min(), wide.index.max())
    ax.set_ylim(0, 1)
    ax.set_xlabel("Birth century")
    ax.set_ylabel("Share of elites, by main sector")
    ax.set_title("What the recorded elite is made of, century by century",
                 fontsize=11.5, loc="left", pad=10)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=7.6)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.0, -0.06,
             "Composition reflects both who held power and who ends up in the encyclopaedic record. The surge "
             "of Sport & Games after 1800 is the clearest\ncase where the second reading dominates, which is why "
             "the association scores are computed net of these marginals. " + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    save(fig, "fig08_sector_composition")


def fig09_profiles(by_era: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14.4, 8.2), sharex=True, sharey=True)
    for ax, era in zip(axes.ravel(), ERA_ORDER):
        sub = by_era[by_era["period"] == era]
        mat = to_matrix(sub, "n_pair")
        prof = mat.div(mat.sum(axis=1).replace(0, np.nan), axis=0)
        im = ax.imshow(prof.to_numpy(dtype=float), cmap="magma_r", vmin=0, vmax=0.6, aspect="auto")
        ax.set_xticks(range(len(SECTOR_ORDER)))
        ax.set_xticklabels(SECTOR_ORDER, rotation=45, ha="right", fontsize=6.2)
        ax.set_yticks(range(len(SECTOR_ORDER)))
        ax.set_yticklabels(SECTOR_ORDER, fontsize=6.2)
        ax.set_title(era, fontsize=9.5, loc="left")
        for spine in ax.spines.values():
            spine.set_visible(False)
    cbar = fig.colorbar(im, ax=axes, shrink=0.55, pad=0.015)
    cbar.set_label("share of a sector's two-sector elites", fontsize=7.5)
    cbar.ax.tick_params(labelsize=7)
    fig.suptitle("Where each sector's diversifiers actually went\n"
                 "Rows sum to one: the destination profile of every sector, era by era",
                 fontsize=12.5, x=0.055, ha="left", y=0.99)
    fig.text(0.055, -0.035,
             "Unlike the association matrices, these are raw shares, so they are dominated by the largest "
             "sectors of the period. Read them alongside Figure 2.\n" + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    fig.subplots_adjust(hspace=0.42, bottom=0.13, top=0.9)
    save(fig, "fig09_destination_profiles")


def fig10_regions(by_er: pd.DataFrame) -> None:
    modern = by_er[by_er["era"].isin(["1800-1899", "1900-2020"])]
    regions = [r for r in ["Europe", "America", "Asia", "Africa", "Oceania"]
               if r in set(modern["region"])]
    pairs_of_interest = (modern.groupby("pair")["assoc_log2"].std()
                         .sort_values(ascending=False).head(14).index.tolist())
    order = (modern[modern["pair"].isin(pairs_of_interest)]
             .groupby("pair")["assoc_log2"].mean().sort_values().index.tolist())

    palette = {"Europe": "#b2182b", "America": "#2166ac", "Asia": "#1b7837",
               "Africa": "#e08214", "Oceania": "#762a83"}
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 6.6), sharey=True)
    for ax, era in zip(axes, ["1800-1899", "1900-2020"]):
        sub = modern[modern["era"] == era]
        y = np.arange(len(order))
        for k, region in enumerate(regions):
            g = sub[sub["region"] == region].set_index("pair").reindex(order)
            offset = (k - (len(regions) - 1) / 2) * 0.13
            ax.scatter(g["assoc_log2"], y + offset, s=22, color=palette[region],
                       label=region if era == "1800-1899" else None, zorder=3)
        ax.axvline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        for yi in y:
            ax.axhline(yi, color="#f0f0f0", lw=13, zorder=0)
        ax.set_yticks(y)
        ax.set_yticklabels(order, fontsize=7.4)
        ax.set_title(era, fontsize=10.5, loc="left")
        ax.set_xlabel("log$_2$(observed / expected)")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=8, loc="lower right", title="Region", title_fontsize=8)
    fig.suptitle("The same pair, different continents: regional variation in how power is combined",
                 fontsize=12.5, x=0.045, ha="left", y=0.98)
    fig.text(0.045, -0.02,
             "The fourteen pairs whose association varies most across regions in the modern eras. Region is the "
             "UN region of the elite's area of attachment.\n" + SOURCE,
             fontsize=7.2, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.945])
    save(fig, "fig10_regional_variation")


def main() -> None:
    overall = pd.read_csv(DATA / "sector_pair_association_overall.csv")
    by_era = pd.read_csv(DATA / "sector_pair_association_by_era.csv")
    by_century = pd.read_csv(DATA / "sector_pair_association_by_century.csv")
    by_er = pd.read_csv(DATA / "sector_pair_association_by_era_region.csv")
    trends = pd.read_csv(DATA / "sector_pair_trends.csv")
    marginals = pd.read_csv(DATA / "sector_marginals_by_period.csv")
    div = pd.read_csv(DATA / "diversification_by_period.csv")
    div_region = pd.read_csv(DATA / "diversification_by_region_period.csv")

    print("writing figures")
    fig01_overall(overall)
    fig02_by_era(by_era)
    fig03_trajectories(by_century, trends)
    fig04_networks(by_era, marginals)
    fig05_diversification(div, div_region, marginals)
    fig06_ranked(overall)
    fig07_trends(trends)
    fig08_composition(marginals)
    fig09_profiles(by_era)
    fig10_regions(by_er)


if __name__ == "__main__":
    main()
