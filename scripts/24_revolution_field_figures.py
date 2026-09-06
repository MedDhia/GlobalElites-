"""Descriptive figures: how the fields of power sat together in revolutionary cohorts.

Four views of the same 21 group-pair association scores in
data/processed/revolutions/, drawn as fields, not as rows of a table.

    figW01  the pooled shape, split into what holds together and what stays apart
    figW02  the same graph inside each of the sixteen cohorts
    figW03  the space of power: fields placed by association, and how far each moves
    figW04  the ordering of the 21 pairs inside each cohort, cohort by cohort

Writes PDF plus 300-dpi PNG into figures/.
"""

import itertools
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.linalg import orthogonal_procrustes

from plotstyle import CMAP, GREY, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
RD = ROOT / "data" / "processed" / "revolutions"

# Ring order chosen so that the strongest positive ties fall between neighbours,
# which keeps the long chords in figW01 and figW02 the ones that carry meaning.
RING = ["Politics", "Administration & Law", "Military", "Nobility & Kinship",
        "Business", "Learning & Culture", "Religion"]
SHORT = {"Politics": "Politics", "Administration & Law": "Admin\n& law",
         "Military": "Military", "Nobility & Kinship": "Nobility\n& kin",
         "Business": "Business", "Learning & Culture": "Learning\n& culture",
         "Religion": "Religion"}
NODE_COLOUR = "#3f3f3f"
DASH = {"solid": "-", "dashed": (0, (2.5, 2))}
LIM = 2.2
LABEL_NUDGE = {"Business": (-4, -21), "Nobility & Kinship": (34, 12),
               "Military": (0, -21), "Learning & Culture": (-14, 13)}

NOTE = ("A cohort is the elites who were adults in a country whose political order was at stake while the revolution ran. "
        "Sectors are coarsened to seven fields and association is\nrefitted inside each cohort, so cohorts of very different "
        "size are comparable. A tie is log2(observed / expected under quasi-independence): positive means the two fields "
        "were\nheld by the same people more often than the size of each field implies, negative means less often. Cells "
        "holding fewer than ten people are dropped. These are descriptive\ncohorts, not treatment groups.")


def short(name):
    return (name.replace("Revolutions of ", "").replace(" Revolution", "")
            .replace(" revolution", "").replace("Latin American independence", "Latin America")
            .replace("Chinese Communist", "Chinese CP").replace("Meiji Restoration", "Meiji"))


def ring_positions(radius=1.0, rotate=np.pi / 2):
    ang = rotate + np.linspace(0, 2 * np.pi, len(RING), endpoint=False)
    return {f: (radius * np.cos(a), radius * np.sin(a)) for f, a in zip(RING, ang)}


def matrices(pairs, revolution=None):
    """Association and readability as 7x7 frames; NaN where the cell is sparse."""
    g = pairs if revolution is None else pairs[pairs["revolution"] == revolution]
    val = pd.DataFrame(np.nan, index=RING, columns=RING, dtype=float)
    sig = pd.DataFrame(False, index=RING, columns=RING)
    for _, r in g.iterrows():
        if r["sparse_cell"]:
            continue
        a, b = r["group_a"], r["group_b"]
        val.loc[a, b] = val.loc[b, a] = r["assoc_log2"]
        s = r["direction"] != "not distinguishable"
        sig.loc[a, b] = sig.loc[b, a] = s
    return val, sig


def pooled_matrix(solid):
    """Mean association per pair over the cohorts where the cell is readable."""
    mean = solid.groupby(["group_a", "group_b"])["assoc_log2"].mean()
    out = pd.DataFrame(0.0, index=RING, columns=RING)
    for (a, b), v in mean.items():
        out.loc[a, b] = out.loc[b, a] = v
    return out


def draw_edges(ax, pos, val, sig, width=5.5, alpha=0.9, only=None, styles=None):
    for a, b in itertools.combinations(RING, 2):
        v = val.loc[a, b]
        if not np.isfinite(v):
            continue
        if only == "positive" and v <= 0:
            continue
        if only == "negative" and v >= 0:
            continue
        (x0, y0), (x1, y1) = pos[a], pos[b]
        lw = 0.5 + width * min(abs(v) / LIM, 1.0)
        colour = CMAP(0.5 + 0.5 * np.clip(v / LIM, -1, 1))
        style = "-" if styles is None else DASH[styles.loc[a, b]]
        ax.plot([x0, x1], [y0, y1], color=colour, lw=lw, ls=style,
                alpha=alpha if sig.loc[a, b] else 0.35,
                solid_capstyle="round", zorder=2)


def draw_nodes(ax, pos, sizes, labels=True, fontsize=7.6, pad=0.30):
    for f in RING:
        x, y = pos[f]
        ax.scatter([x], [y], s=sizes.get(f, 60), color=NODE_COLOUR, zorder=4,
                   edgecolor="white", lw=1.0)
        if labels:
            r = np.hypot(x, y)
            ax.annotate(SHORT[f], (x * (1 + pad / max(r, 0.4)), y * (1 + pad / max(r, 0.4))),
                        ha="center", va="center", fontsize=fontsize, color="#222222")
    ax.set_aspect("equal")
    ax.axis("off")


# ---------------------------------------------------------------------------


def figW01(pairs, comp):
    solid = pairs[~pairs["sparse_cell"]]
    mean = solid.groupby(["group_a", "group_b"])["assoc_log2"].mean()
    readable = solid.groupby(["group_a", "group_b"]).size()
    agree = (solid[solid["direction"] != "not distinguishable"]
             .groupby(["group_a", "group_b"])["direction"].nunique())
    named = (solid[solid["direction"] != "not distinguishable"]
             .groupby(["group_a", "group_b"]).size())

    val = pd.DataFrame(np.nan, index=RING, columns=RING, dtype=float)
    sig = pd.DataFrame(False, index=RING, columns=RING)
    styles = pd.DataFrame("solid", index=RING, columns=RING)
    for (a, b), v in mean.items():
        val.loc[a, b] = val.loc[b, a] = v
        one_way = agree.get((a, b), 0) == 1 and named.get((a, b), 0) >= 3
        sig.loc[a, b] = sig.loc[b, a] = one_way
        styles.loc[a, b] = styles.loc[b, a] = "solid" if one_way else "dashed"

    share = (comp[comp["level"] == "group"].groupby("category")["share_holding"].mean())
    sizes = {f: 60 + 2200 * share.get(f, 0) for f in RING}
    pos = ring_positions()

    fig, axes = plt.subplots(1, 2, figsize=(13.6, 7.4))
    for ax, only, title in zip(axes, ["positive", "negative"],
                               ["What was held together", "What was held apart"]):
        draw_edges(ax, pos, val, sig, width=7.5, only=only, styles=styles)
        draw_nodes(ax, pos, sizes, fontsize=8.4)
        ax.set_xlim(-1.62, 1.62)
        ax.set_ylim(-1.5, 1.62)
        ax.set_title(title, fontsize=11.5, loc="left", x=0.02, y=0.97)

    handles = [Line2D([], [], color=CMAP(0.86), lw=5, label="held together"),
               Line2D([], [], color=CMAP(0.14), lw=5, label="held apart"),
               Line2D([], [], color=GREY, lw=3.4, label="thicker: further from chance"),
               Line2D([], [], color=GREY, lw=3.4, label="solid: every readable cohort agrees"),
               Line2D([], [], color=GREY, lw=3.4, ls=(0, (2.5, 2)),
                      label="dashed: cohorts disagree, or too few call it")]
    axes[1].legend(handles=handles, fontsize=7.8, loc="lower center",
                   bbox_to_anchor=(0.5, 0.02), ncol=2)

    fig.suptitle("The shape of elite power in a revolution, pooled over sixteen of them",
                 fontsize=13, x=0.035, ha="left", y=0.99)
    fig.text(0.035, -0.145,
             "Node size is the mean share of a cohort holding the field. Every one of the 21 ties is drawn, on the left "
             "where the mean runs positive and on the right where it runs\nnegative. The positive side is a chain, not a "
             "clique: administration to politics to the military to the nobility on one arm, and learning to religion and "
             "to business on the\nother. Only one tie joins the two arms, the nobility to learning at 0.26, and the "
             "cohorts disagree about even that one. Two fields are attached to a single partner and "
             "held\napart from all five of the others: administration, which goes with politics alone, and religion, "
             "which goes with learning alone. The strongest tie of either kind is negative,\nadministration with business "
             "at -1.41. Politics with business is dashed because six cohorts call it dissociated and three call it "
             "associated.\n" + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figW01_pooled_field_graph")


def figW02(pairs, comp, index):
    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    pos = ring_positions()
    shares = (comp[comp["level"] == "group"]
              .pivot(index="revolution", columns="category", values="share_holding"))

    fig, axes = plt.subplots(3, 6, figsize=(16.4, 10.0))
    flat = axes.ravel()

    ax = flat[0]
    draw_nodes(ax, pos, {f: 90 for f in RING}, fontsize=6.4, pad=0.52)
    ax.set_xlim(-1.95, 1.95)
    ax.set_ylim(-1.9, 1.95)
    ax.set_title("the seven fields\nin every panel", fontsize=8.6, loc="left",
                 color=GREY, linespacing=1.5)

    for ax, rev in zip(flat[1:], order):
        val, sig = matrices(pairs, rev)
        drawn = val.where(sig)
        draw_edges(ax, pos, drawn, sig, width=5.0, alpha=0.95)
        sz = {f: 26 + 900 * shares.loc[rev].get(f, 0) for f in RING}
        draw_nodes(ax, pos, sz, labels=False)
        ax.set_xlim(-1.32, 1.32)
        ax.set_ylim(-1.32, 1.32)
        n_pos = int((drawn.values[np.triu_indices(len(RING), 1)] > 0).sum())
        n_neg = int((drawn.values[np.triu_indices(len(RING), 1)] < 0).sum())
        y0 = int(index.set_index("revolution").loc[rev, "window_start"])
        ax.set_title(f"{short(rev)}, {y0}\n{n_pos} together, {n_neg} apart",
                     fontsize=8.6, loc="left", linespacing=1.5)
        if n_pos + n_neg == 0:
            ax.annotate("no tie separable\nfrom chance", (0, 0), ha="center",
                        va="center", fontsize=7.4, color=GREY, style="italic")
    for ax in flat[len(order) + 1:]:
        ax.axis("off")

    fig.suptitle("Sixteen revolutions, the same seven fields, only the ties that stand out from chance",
                 fontsize=13, x=0.03, ha="left", y=1.0)
    fig.text(0.03, -0.115,
             "A tie is drawn only where the cohort's own bootstrap separates it from chance after adjustment, so an empty "
             "space between two fields means the cohort had too few\npeople to tell, not that the fields were unrelated. "
             "Node size is that cohort's share holding the field. The recurring motif is the triangle of politics, "
             "administration and the\nmilitary at the top of each ring and the tie from learning to religion and to "
             "business at the bottom; what changes between panels is whether the two arms are joined and\nhow far "
             "administration is pushed out. Count the ties with the cohort size in mind: the German ring resolves all "
             "twenty-one and the 1848 and Russian rings nineteen, while the\nMeiji ring resolves four and the Cuban five. "
             "That is the estimator finding more in a larger cohort, not elites who were more entangled.\n"
             + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.955], h_pad=3.4)
    save(fig, "figW02_field_graphs_by_revolution")


def embed(val, fill):
    """Classical MDS of a 7x7 association matrix, associated fields placed close."""
    m = val.copy()
    for a, b in itertools.combinations(RING, 2):
        if not np.isfinite(m.loc[a, b]):
            m.loc[a, b] = m.loc[b, a] = fill.loc[a, b]
    a = m.to_numpy().astype(float)
    np.fill_diagonal(a, 0.0)
    d = np.nanmax(a) + 0.35 - a     # association to dissimilarity
    np.fill_diagonal(d, 0.0)
    n = len(RING)
    j = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * j @ (d ** 2) @ j
    w, v = np.linalg.eigh(b)
    idx = np.argsort(w)[::-1][:2]
    return v[:, idx] * np.sqrt(np.maximum(w[idx], 0))


def figW03(pairs, index):
    solid = pairs[~pairs["sparse_cell"]]
    fill = pooled_matrix(solid)
    anchor = embed(fill, fill)

    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    clouds = {}
    for rev in order:
        val, _ = matrices(pairs, rev)
        e = embed(val, fill)
        r, s = orthogonal_procrustes(e - e.mean(0), anchor - anchor.mean(0))
        clouds[rev] = (e - e.mean(0)) @ r + anchor.mean(0)

    travel = pd.Series({f: np.mean([np.hypot(*(clouds[r][i] - anchor[i])) for r in order])
                        for i, f in enumerate(RING)}).sort_values()

    fig, axes = plt.subplots(1, 2, figsize=(14.6, 7.0),
                             gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    for i, f in enumerate(RING):
        pts = np.array([clouds[r][i] for r in order])
        ax.scatter(pts[:, 0], pts[:, 1], s=17, color="#b9b9b9", zorder=2)
        for p in pts:
            ax.plot([anchor[i, 0], p[0]], [anchor[i, 1], p[1]], color="#dcdcdc",
                    lw=0.7, zorder=1)
        ax.scatter([anchor[i, 0]], [anchor[i, 1]], s=130, color=NODE_COLOUR, zorder=4,
                   edgecolor="white", lw=1.2)
        ax.annotate(f, (anchor[i, 0], anchor[i, 1]), textcoords="offset points",
                    xytext=LABEL_NUDGE.get(f, (0, 13)), ha="center", fontsize=9,
                    color="#1a1a1a", zorder=5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Fields placed so that association is closeness", fontsize=11,
                 loc="left", y=0.99)

    ax = axes[1]
    y = np.arange(len(travel))
    ax.barh(y, travel.to_numpy(), color="#8a8a8a", height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels(travel.index, fontsize=8.6)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("mean distance from the pooled position, in units of the map")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("How far each field moves between revolutions", fontsize=11,
                 loc="left", y=1.02)

    fig.suptitle("The space of power, and which fields keep their place in it",
                 fontsize=13, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.12,
             "Left: the seven fields placed by classical scaling of the pooled association matrix, so that fields held by "
             "the same people sit close. Each cohort's own matrix is\nscaled the same way and rotated onto the pooled map, "
             "and its seven positions are the small grey dots. Sparse cells are filled with the pooled value before "
             "scaling, which\npulls a small cohort towards the middle, so a thin cohort contributes short spokes by "
             "construction and the lengths are a floor on the real movement. Right: the mean\ndistance a field travels "
             "from its pooled position. Learning, politics and administration keep their place; business moves furthest, "
             "at more than twice the distance learning\nmoves, with religion behind it. The two fields whose place in the "
             "structure of elite power is least settled across revolutions are the two that are not the state.\n"
             + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figW03_space_of_power")


def figW04(pairs, index):
    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    solid = pairs[~pairs["sparse_cell"]]
    mean = solid.groupby("pair")["assoc_log2"].mean().sort_values(ascending=False)
    # Cohorts differ in how many cells are readable, from 7 to 21, so a raw rank is
    # not comparable across columns. Position is the rank as a share of the cohort's
    # own readable pairs: 0 is the most associated tie it has, 1 the most dissociated.
    rank = (solid.pivot(index="pair", columns="revolution", values="assoc_log2")
            .reindex(index=mean.index, columns=order)
            .rank(ascending=False, axis=0, pct=True))

    named = ["Religion + Learning & Culture", "Business + Learning & Culture",
             "Administration & Law + Business", "Business + Religion",
             "Nobility & Kinship + Learning & Culture", "Politics + Nobility & Kinship"]
    fig, ax = plt.subplots(figsize=(14.4, 8.0))
    x = np.arange(len(order))
    for pair in mean.index:
        v = rank.loc[pair].to_numpy(dtype=float)
        ok = np.isfinite(v)
        if pair in named:
            continue
        ax.plot(x[ok], v[ok], color="#d5d5d5", lw=1.5, zorder=1)
    for pair in named:
        v = rank.loc[pair].to_numpy(dtype=float)
        ok = np.isfinite(v)
        colour = CMAP(0.5 + 0.5 * np.clip(mean[pair] / LIM, -1, 1))
        ax.plot(x[ok], v[ok], color=colour, lw=3.0, alpha=0.95, zorder=3,
                solid_capstyle="round")
        ax.scatter(x[ok], v[ok], s=26, color=colour, zorder=4)
        last = len(ok) - 1 - int(np.argmax(ok[::-1]))
        ax.annotate(f"  {pair}", (x[last], v[last]), ha="left", va="center",
                    fontsize=8, color="#222222", zorder=5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{short(r)}\n{int(index.set_index('revolution').loc[r, 'window_start'])}"
                        for r in order], fontsize=7.6)
    ax.set_xlim(-0.5, len(order) + 5.6)
    ax.set_ylim(1.04, -0.04)
    ax.set_ylabel("position in the cohort's own ordering\n"
                  "0 = its most associated tie, 1 = its most dissociated")
    ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("A settled core, and ties to the nobility that roam",
                 fontsize=13, x=0.035, ha="left", y=0.985)
    fig.text(0.035, -0.175,
             "Each line is one pair of fields, placed by where it sits in that cohort's own ordering; six are drawn out "
             "and the other fifteen left grey. Position is used\ninstead of rank because cohorts resolve between seven "
             "and twenty-one pairs, so fourth of nine and fourth of twenty-one are not the same place. A line breaks "
             "where\nthe cohort's cell holds fewer than ten people. Two ties never leave their end: religion with "
             "learning stays in the top two fifths of all fourteen cohorts that can read it,\nand administration with "
             "business in the bottom quarter of all eight. The lines that cross the panel are ties involving the "
             "nobility and business, the two fields the map in\nfigW03 shows moving most: the nobility with learning "
             "runs from the top seventh of the Cuban ordering to near the bottom of the Meiji one, politics with the "
             "nobility\nfrom a quarter of the way down the Glorious ordering to the very bottom of the Turkish one, and "
             "business with religion from the top of the Mexican ordering to the bottom of the\nGerman one.\n"
             + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figW04_rank_ribbons")


def main():
    index = pd.read_csv(RD / "revolutions_index.csv")
    pairs = pd.read_csv(RD / "cohort_group_pairs.csv")
    comp = pd.read_csv(RD / "cohort_composition.csv")

    solid = pairs[~pairs["sparse_cell"]]
    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    pos = (solid.pivot(index="pair", columns="revolution", values="assoc_log2")
           .reindex(columns=order).rank(ascending=False, axis=0, pct=True))
    spread = pd.DataFrame({"lowest": pos.min(axis=1), "highest": pos.max(axis=1),
                           "at_lowest": pos.idxmin(axis=1), "at_highest": pos.idxmax(axis=1),
                           "cohorts": pos.notna().sum(axis=1)})
    spread["span"] = spread["highest"] - spread["lowest"]
    print("\nhow far each tie moves in the cohort's own ordering")
    print(spread.sort_values("span", ascending=False).round(2).to_string())

    fill = pooled_matrix(solid)
    anchor = embed(fill, fill)
    travel = {}
    for rev in order:
        val, _ = matrices(pairs, rev)
        e = embed(val, fill)
        r, _ = orthogonal_procrustes(e - e.mean(0), anchor - anchor.mean(0))
        aligned = (e - e.mean(0)) @ r + anchor.mean(0)
        for i, f in enumerate(RING):
            travel.setdefault(f, []).append(float(np.hypot(*(aligned[i] - anchor[i]))))
    print("\nmean distance each field travels from its pooled position")
    print(pd.Series({f: np.mean(v) for f, v in travel.items()}).sort_values().round(3).to_string())

    named = solid[solid["direction"] != "not distinguishable"]
    print("\nties drawn per cohort")
    print(named.groupby(["revolution", "direction"]).size().unstack(fill_value=0)
          .assign(total=lambda t: t.sum(axis=1)).sort_values("total", ascending=False)
          .to_string())

    print("\nwriting revolutionary field figures")
    figW01(pairs, comp)
    figW02(pairs, comp, index)
    figW03(pairs, index)
    figW04(pairs, index)


if __name__ == "__main__":
    main()
