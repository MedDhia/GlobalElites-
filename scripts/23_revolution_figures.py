"""Figures comparing the revolutionary cohorts.

Reads data/processed/revolutions/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from plotstyle import BLUE, CMAP, GREY, RED, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
RD = ROOT / "data" / "processed" / "revolutions"

# Red for association and blue for dissociation, matching the heatmaps and the
# network figure in scripts/03, which read off the RdBu_r scale.
DIR_COLOUR = {"associated": RED, "dissociated": BLUE,
              "not distinguishable": "#9e9e9e"}
BAND_ORDER = ["under 20", "20-35", "36-55", "56+"]
BAND_COLOUR = {"under 20": "#c6dbef", "20-35": "#6baed6",
               "36-55": "#2171b5", "56+": "#08306b"}
POLITICS_PAIRS = ["Politics + Administration & Law", "Politics + Military",
                  "Politics + Business", "Politics + Learning & Culture"]
PAIR_COLOUR = {"Politics + Administration & Law": "#1b7837",
               "Politics + Military": RED,
               "Politics + Business": "#d95f02",
               "Politics + Learning & Culture": BLUE}

NOTE = ("A cohort is the elites who were adults in a country whose political order was at stake while the revolution ran. "
        "Sectors are coarsened to seven groups so a cohort\ncell has enough cases, and association is refitted inside each "
        "cohort, which makes cohorts of very different size comparable. Cells holding fewer than ten people are\nflagged "
        "sparse and dropped from every count, since the score there follows the continuity correction more than the data. "
        "These are descriptive cohorts, not treatment groups.")


def short(name):
    return (name.replace("Revolutions of ", "").replace(" Revolution", "")
            .replace(" revolution", "").replace("Latin American independence", "Latin America")
            .replace("Chinese Communist", "Chinese CP").replace("Meiji Restoration", "Meiji"))


def solid(pairs):
    return pairs[~pairs["sparse_cell"]]


def pair_order(pairs):
    return (solid(pairs).groupby("pair")["assoc_log2"].mean()
            .sort_values(ascending=False).index.tolist())


# ---------------------------------------------------------------------------


def figV01(summary, index):
    s = summary.sort_values("window_start")
    y = np.arange(len(s))[::-1]
    fig, axes = plt.subplots(1, 3, figsize=(15.4, 6.4),
                             gridspec_kw={"width_ratios": [1.55, 0.8, 1.05]})

    ax = axes[0]
    for yi, (_, r) in zip(y, s.iterrows()):
        ax.plot([r["birth_min"] + 20, r["birth_max"] + 20], [yi] * 2, color="#d9d9d9",
                lw=5.5, solid_capstyle="butt", zorder=1)
        ax.plot([r["window_start"], max(r["window_end"], r["window_start"] + 1.5)],
                [yi] * 2, color=RED, lw=8.5, solid_capstyle="butt", zorder=3)
        ax.annotate(f"{r['n_elites']:,}", (r["birth_max"] + 26, yi), va="center",
                    fontsize=7, color=GREY)
    ax.set_yticks(y)
    ax.set_yticklabels([short(v) for v in s["revolution"]], fontsize=8)
    ax.set_xlabel("year")
    ax.set_xlim(1610, 2075)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("1. When, and who was alive for it", fontsize=10, loc="left", pad=8)
    ax.legend(handles=[Patch(color=RED, label="the window"),
                       Patch(color="#d9d9d9", label="years in which a member turned 20")],
              fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.11))

    ax = axes[1]
    for yi, (_, r) in zip(y, s.iterrows()):
        ax.plot([r["n_two_sector"], r["n_elites"]], [yi] * 2, color="#c6c6c6", lw=1.6,
                zorder=1)
    ax.scatter(s["n_elites"], y, s=34, color="#9e9e9e", zorder=3)
    ax.scatter(s["n_two_sector"], y, s=34, color="#252525", zorder=3)
    ax.set_xscale("log")
    ax.set_xlim(300, 120_000)
    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("elites in the cohort (log scale)")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("2. Size", fontsize=10, loc="left", pad=8)
    ax.legend(handles=[Patch(color="#9e9e9e", label="all"),
                       Patch(color="#252525", label="spanning two sectors")],
              fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.11))

    ax = axes[2]
    cols = {"under 20": "n_under_20", "20-35": "n_20-35", "36-55": "n_36-55",
            "56+": "n_56plus"}
    shares = s[[cols[b] for b in BAND_ORDER]].to_numpy(dtype=float)
    shares = shares / shares.sum(axis=1, keepdims=True)
    left = np.zeros(len(s))
    for k, band in enumerate(BAND_ORDER):
        ax.barh(y, shares[:, k], left=left, color=BAND_COLOUR[band], height=0.66,
                label=band)
        left = left + shares[:, k]
    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of the cohort, by age at the window midpoint")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("3. Generations inside a cohort", fontsize=10, loc="left", pad=8)
    ax.legend(fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.11))

    fig.suptitle("Sixteen revolutions, 144,178 elites who lived through one",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.11,
             "Seventeen revolutions were considered and sixteen clear the floor of 500 elites with 200 spanning two "
             "sectors. Only the Haitian Revolution falls out, at 39\nelites, which is a fact about what encyclopaedic "
             "sources record. Cohorts run from 518 people (the Meiji Restoration) to 54,018 (the German Revolution), a "
             "hundredfold\nspread that follows the coverage of the database far more than the size of the revolution, so "
             "cohort sizes are not comparable across the set. Age composition is\nsteadier: the 20-35 band is the largest "
             "in ten of the sixteen and the 36-55 band in the other six. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    save(fig, "figV01_cohorts")


def figV02(pairs, index):
    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    rows = pair_order(pairs)
    val = pairs.pivot(index="pair", columns="revolution",
                      values="assoc_log2").loc[rows, order]
    spa = pairs.pivot(index="pair", columns="revolution",
                      values="sparse_cell").loc[rows, order]

    fig, ax = plt.subplots(figsize=(14.2, 8.6))
    lim = 2.2
    im = ax.imshow(val.to_numpy(), cmap=CMAP, vmin=-lim, vmax=lim, aspect="auto")
    for i in range(val.shape[0]):
        for j in range(val.shape[1]):
            v = val.iat[i, j]
            if spa.iat[i, j]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="white",
                                           edgecolor="#bdbdbd", lw=0.5, hatch="////",
                                           zorder=2))
                continue
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=6.4,
                    color="white" if abs(v) > 1.25 else "#333333", zorder=3)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([short(v) for v in order], rotation=45, ha="right", fontsize=7.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    ax.set_xticks(np.arange(-0.5, len(order), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.0)
    ax.tick_params(which="minor", length=0)
    ax.spines[:].set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.015)
    cb.set_label("log$_2$(observed / expected) inside the cohort", fontsize=8)
    cb.ax.tick_params(labelsize=7.5)

    fig.suptitle("The same shape in sixteen revolutions, three centuries apart",
                 fontsize=12.5, x=0.035, ha="left", y=0.985)
    ax.set_title("revolutions left to right by date; pairs top to bottom by mean association. "
                 "Hatched cells hold fewer than ten people.",
                 fontsize=8.4, loc="left", color=GREY, pad=8)
    fig.text(0.035, -0.105,
             "The row order barely disturbs the columns. Ranking each cohort's readable pairs against the pooled "
             "ordering gives a Spearman correlation of 0.77 at the median,\nfrom 0.35 in the Mexican Revolution to 0.92 "
             "in 1848, and no cohort inverts it. Religion with learning and business with learning hold the top of the "
             "column and\nadministration with business and administration with religion hold the bottom, in the English "
             "Revolution and again in the Iranian one. 85 of these 336 cells hold\nfewer than ten people and are hatched; "
             "they concentrate in the small cohorts, fourteen of the Cuban cohort's twenty-one and none of the German, "
             "Russian or 1848\nones.\n" + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figV02_pair_heatmap")


def figV03(pairs):
    rows = pair_order(pairs)
    counts = (solid(pairs).groupby(["pair", "direction"]).size()
              .unstack(fill_value=0)
              .reindex(columns=["associated", "dissociated", "not distinguishable"],
                       fill_value=0))
    fig, ax = plt.subplots(figsize=(12.6, 8.2))
    for yi, pair in enumerate(rows):
        if yi % 2 == 0:
            ax.axhspan(yi - 0.45, yi + 0.45, color="#f4f4f4", zorder=0)
        g = pairs[pairs["pair"] == pair]
        sp = g[g["sparse_cell"]]
        so = g[~g["sparse_cell"]]
        ax.scatter(sp["assoc_log2"], np.full(len(sp), yi), s=22, facecolor="none",
                   edgecolor="#c6c6c6", lw=0.8, zorder=2)
        ax.scatter(so["assoc_log2"], np.full(len(so), yi), s=34, zorder=3, alpha=0.9,
                   color=[DIR_COLOUR[d] for d in so["direction"]])
        m = so["assoc_log2"].mean()
        ax.plot([m, m], [yi - 0.34, yi + 0.34], color="#111111", lw=2.2, zorder=4)
        c = counts.loc[pair]
        ax.annotate(f"{c['associated']}  /  {c['dissociated']}  /  "
                    f"{c['not distinguishable']}", (5.35, yi), va="center",
                    ha="right", fontsize=7.4, color=GREY)
    ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=8.4)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlim(-5.6, 5.6)
    ax.set_xlabel("log$_2$(observed / expected) inside the cohort")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.annotate("associated / dissociated /\nnot distinguishable", (5.35, -1.15),
                ha="right", fontsize=7.4, color=GREY, annotation_clip=False)
    handles = [Patch(color=RED, label="associated"), Patch(color=BLUE, label="dissociated"),
               Patch(color="#9e9e9e", label="not distinguishable"),
               Patch(facecolor="white", edgecolor="#c6c6c6", label="sparse cell, excluded")]
    ax.legend(handles=handles, fontsize=7.6, ncol=4, loc="upper center",
              bbox_to_anchor=(0.5, -0.075))

    fig.suptitle("What repeats across revolutions, and what does not",
                 fontsize=12.5, x=0.045, ha="left", y=0.985)
    fig.text(0.045, -0.145,
             "One point per revolution, the bar is the mean over the readable cells. Four results hold almost everywhere. "
             "Politics with administration is associated in\nfifteen cohorts and dissociated in none; politics with the "
             "military in thirteen and dissociated in none; politics with learning or culture is dissociated in fourteen "
             "and\nassociated in none; administration with business is dissociated in all eight cohorts large enough to "
             "read. The people who ran the state and the people who wrote and\ntaught were separate populations in the "
             "English Revolution and in the Iranian one alike. The pairs that divide the set sit in the middle of the "
             "column: politics with\nbusiness and politics with nobility both run in both directions.\n" + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figV03_what_repeats")


def figV04(pairs, index):
    pb, pm = "Politics + Business", "Politics + Military"
    g = pairs[pairs["pair"] == pb].sort_values("assoc_log2")
    fig, axes = plt.subplots(1, 2, figsize=(14.8, 6.4),
                             gridspec_kw={"width_ratios": [1.05, 1]})

    ax = axes[0]
    y = np.arange(len(g))
    for yi, (_, r) in zip(y, g.iterrows()):
        col = "#c6c6c6" if r["sparse_cell"] else DIR_COLOUR[r["direction"]]
        ax.plot([r["assoc_ci_low"], r["assoc_ci_high"]], [yi] * 2, color=col, lw=1.6,
                alpha=0.75, zorder=2)
        ax.scatter(r["assoc_log2"], yi, s=46, color=col, zorder=3)
    ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels([short(v) for v in g["revolution"]], fontsize=8)
    ax.set_xlabel("Politics + Business,  log$_2$(observed / expected)")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("The pair that divides the set", fontsize=10.5, loc="left", pad=10)
    ax.legend(handles=[Patch(color=RED, label="associated"),
                       Patch(color=BLUE, label="dissociated"),
                       Patch(color="#9e9e9e", label="not distinguishable")],
              fontsize=7.4, loc="lower right")

    ax = axes[1]
    w = pairs[pairs["pair"].isin([pb, pm])].pivot(index="revolution", columns="pair",
                                                  values="assoc_log2")
    sp = pairs[pairs["pair"].isin([pb, pm])].pivot(index="revolution", columns="pair",
                                                   values="sparse_cell")
    year = index.set_index("revolution")["window_start"]
    ok = ~(sp[pb] | sp[pm])
    sc = ax.scatter(w.loc[ok, pb], w.loc[ok, pm], s=74, c=year[ok.index][ok],
                    cmap="viridis", zorder=3, edgecolor="white", lw=0.6)
    offsets = {"American Revolution": (0, 10), "Latin American independence": (0, -15),
               "German Revolution": (-16, -3), "Russian Revolution": (0, 10)}
    for rev in w.index[ok]:
        ax.annotate(short(rev), (w.loc[rev, pb], w.loc[rev, pm]),
                    textcoords="offset points", xytext=offsets.get(rev, (0, 9)),
                    ha="center", fontsize=6.8, color="#333333")
    ax.axhline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
    ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
    ax.set_xlabel("Politics + Business")
    ax.set_ylabel("Politics + Military")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Money and arms, cohort by cohort", fontsize=10.5, loc="left", pad=10)
    cb = fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("year the window opens", fontsize=8)
    cb.ax.tick_params(labelsize=7.5)

    fig.suptitle("Politics and the military everywhere; politics and business only sometimes",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.155,
             "Left: politics with business is associated in the Irish, Russian and German cohorts and dissociated in the "
             "American, French, Latin American, Xinhai, Chinese\nCommunist and Iranian ones, a spread of 1.5 log points "
             "from the Iranian cohort to the Irish one. Right: all fourteen cohorts with both cells readable sit above the "
             "horizontal\nline, so an elite that held office also held a commission almost everywhere, while the "
             "horizontal position moves freely. The Meiji Restoration, the one cohort whose\npolitics-military score is "
             "negative, is absent here because its business cell is sparse. The colour shows this is not a matter of date: "
             "the cohorts left of the vertical line\nopen between 1775 and 1978, those right of it between 1642 and 1918.\n"
             + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figV04_politics_business")


def figV05(bands, index):
    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    fig, axes = plt.subplots(1, 4, figsize=(16.2, 6.6), sharey=True)
    for ax, pair in zip(axes, POLITICS_PAIRS):
        g = bands[bands["pair"] == pair]
        val = g.pivot(index="revolution", columns="age_band", values="assoc_log2")
        spa = g.pivot(index="revolution", columns="age_band", values="sparse_cell")
        keep = [r for r in order if r in val.index]
        y = np.arange(len(keep))[::-1]
        for yi, rev in zip(y, keep):
            pts = [(b, val.loc[rev, b]) for b in ["20-35", "36-55", "56+"]
                   if b in val.columns and np.isfinite(val.loc[rev, b])
                   and not spa.loc[rev, b]]
            if len(pts) > 1:
                ax.plot([v for _, v in pts], [yi] * len(pts), color="#d0d0d0", lw=1.6,
                        zorder=1)
            for b, v in pts:
                ax.scatter(v, yi, s=40, color=BAND_COLOUR[b], zorder=3)
        ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        ax.set_yticks(y)
        ax.set_yticklabels([short(r) for r in keep], fontsize=7.8)
        ax.tick_params(axis="y", length=0)
        ax.set_title(pair, fontsize=9, loc="left")
        ax.set_xlabel("log$_2$(observed / expected)")
        ax.spines[["top", "right", "left"]].set_visible(False)
    axes[0].legend(handles=[Patch(color=BAND_COLOUR[b], label=b)
                            for b in ["20-35", "36-55", "56+"]],
                   fontsize=7.4, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))

    fig.suptitle("Inside a cohort, no consistent divide between the young and the old",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.155,
             "Association refitted inside each age band, banded on age at the midpoint of the window. If a revolution "
             "recruited a differently structured elite, the youngest\nband should sit apart from the oldest in a "
             "consistent direction. Individual cohorts do separate, by more than a log point in the Russian cohort on "
             "politics with the military and on\npolitics with business, but never the same way twice. Across the cohorts where both ends are readable, the 20-35 band "
             "differs from the 56+ band by a median of -0.11 on politics with administration,\n-0.18 on politics with "
             "business, -0.04 on politics with the military and +0.15 on politics with learning, and the sign flips from "
             "revolution to revolution in every\none of the four. Bands below the hundred-pair floor are absent, which "
             "is why the small cohorts show one or two points. The under-20 band, whose members reached\nadulthood inside the window, is left out because it is not the same age range in a two-year "
             "revolution and a fifteen-year one.\n" + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    save(fig, "figV05_age_bands")


def figV06(series, index):
    order = index[index["kept"]].sort_values("window_start")["revolution"].tolist()
    idx = index.set_index("revolution")
    fig, axes = plt.subplots(4, 4, figsize=(15.6, 12.0), sharey=True)
    for ax, rev in zip(axes.ravel(), order):
        g = series[(series["revolution"] == rev) & (~series["sparse_cell"])]
        y0, y1 = int(idx.loc[rev, "window_start"]), int(idx.loc[rev, "window_end"])
        ax.axvspan(y0 - 90, y1 - 20, color="#ededed", zorder=0)
        ax.axvline(y0, color=RED, lw=1.4, zorder=1)
        for pair in POLITICS_PAIRS:
            h = g[g["pair"] == pair].sort_values("birth_cohort_start")
            if h.empty:
                continue
            x = h["birth_cohort_start"] + 20
            ax.plot(x, h["assoc_log2"], marker="o", ms=3.4, lw=1.4,
                    color=PAIR_COLOUR[pair], label=pair)
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        ax.set_title(f"{short(rev)}, {y0}-{y1}", fontsize=9, loc="left")
        ax.tick_params(labelsize=7.2)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes.ravel()[len(order):]:
        ax.axis("off")
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)", fontsize=8)
    for ax in axes[-1, :]:
        ax.set_xlabel("birth cohort, midpoint", fontsize=8)
    handles = [plt.Line2D([], [], color=PAIR_COLOUR[p], marker="o", ms=4, lw=1.6,
                          label=p) for p in POLITICS_PAIRS]
    handles.append(Patch(color="#ededed", label="birth years that make a person eligible"))
    handles.append(plt.Line2D([], [], color=RED, lw=1.6, label="the window opens"))
    axes[0, 0].legend(handles=handles, fontsize=7.6, ncol=3, loc="upper center",
                      bbox_to_anchor=(2.2, 1.42))

    fig.suptitle("Before, during and after: what politics was joined to, by birth cohort",
                 fontsize=12.5, x=0.035, ha="left", y=1.005)
    fig.text(0.035, -0.045,
             "The same countries split into 40-year birth cohorts, from 120 years before the window to 120 years after, "
             "with association refitted inside each block. The shaded band\nmarks the birth years that put a person in "
             "the revolutionary cohort. The three results that repeat across cohorts repeat across the centuries inside "
             "them: politics with\nadministration is positive in 86 of 87 readable blocks, politics with the military in "
             "72 of 83, and politics with learning is negative in 82 of 85, before the revolution as\nmuch as after. "
             "Politics with business is the exception again, positive in 31 of 80. Only six of the sixteen have readable "
             "blocks entirely on both sides of the shaded band,\nand their contrasts do not point one way: politics with "
             "the military falls by 1.12 across the American Revolution and rises by 0.55 across the German one. Blocks "
             "below\nthe hundred-pair floor are absent, so the series are not balanced.\n" + NOTE + "\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.015, 1, 0.955], h_pad=4.2)
    save(fig, "figV06_birth_cohorts")


def main():
    index = pd.read_csv(RD / "revolutions_index.csv")
    summary = pd.read_csv(RD / "cohort_summary.csv")
    pairs = pd.read_csv(RD / "cohort_group_pairs.csv")
    bands = pd.concat([pd.read_csv(p) for p in
                       sorted(RD.glob("*/group_pairs_by_age_band.csv"))],
                      ignore_index=True)
    series = pd.concat([pd.read_csv(p) for p in
                        sorted(RD.glob("*/birth_cohort_pairs.csv"))],
                       ignore_index=True)

    print("writing revolution figures")
    figV01(summary, index)
    figV02(pairs, index)
    figV03(pairs)
    figV04(pairs, index)
    figV05(bands, index)
    figV06(series, index)


if __name__ == "__main__":
    main()
