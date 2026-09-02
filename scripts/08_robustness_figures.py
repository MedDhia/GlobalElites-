"""Figures for the culture-placement robustness run.

Reads data/processed/robustness/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from domainmap import CORE_PAIRS, SPECS
from plotstyle import CMAP, GREY, SOURCE, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "robustness"

SPEC_ORDER = ["main", "culture_out", "culture_own", "culture_core_only",
              "invention_ideational"]
SPEC_LABEL = {
    "main": "Main\nCulture is ideational",
    "culture_out": "Culture out\nideational = religion + academy",
    "culture_own": "Culture own\nfifth domain",
    "culture_core_only": "Core only\nCulture (core) is ideational",
    "invention_ideational": "Invention ideational\ninventors leave the economy",
}
SPEC_COLOUR = {
    "main": "#111111",
    "culture_out": "#b2182b",
    "culture_own": "#2166ac",
    "culture_core_only": "#e08214",
    "invention_ideational": "#1b7837",
}
FIVE = ["Political", "Ideational", "Cultural", "Economic", "Security"]
SHORT = {"Political": "Political /\nregulatory", "Ideational": "Ideational /\nacademic",
         "Cultural": "Cultural", "Economic": "Economic /\nallocative",
         "Security": "Security /\nmilitary"}
ERA_ORDER = ["Pre-1000", "1000-1399", "1400-1599", "1600-1799", "1800-1899", "1900-2020"]
VLIM = 1.2


def draw_matrix(ax, mat, sig=None, labels=True, fontsize=8):
    data = mat.to_numpy(dtype=float)
    im = ax.imshow(np.ma.masked_invalid(data),
                   cmap=CMAP.with_extremes(bad="#f2f2f2"), vmin=-VLIM, vmax=VLIM)
    n = len(mat)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([SHORT[d] for d in mat.columns], fontsize=6.8, linespacing=0.95)
    ax.set_yticklabels([SHORT[d] for d in mat.index] if labels else [""] * n,
                       fontsize=6.8, linespacing=0.95)
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
    for i in range(n):
        for j in range(n):
            if i == j or not np.isfinite(data[i, j]):
                continue
            ax.text(j, i, f"{data[i, j]:+.2f}", ha="center", va="center", fontsize=fontsize,
                    zorder=5, color="white" if abs(data[i, j]) / VLIM > 0.62 else "#1a1a1a")
    return im


def to_matrix(frame, domains, value="assoc_log2"):
    mat = pd.DataFrame(np.nan, index=domains, columns=domains, dtype=float)
    for _, r in frame.iterrows():
        if r["domain_a"] in domains and r["domain_b"] in domains:
            mat.loc[r["domain_a"], r["domain_b"]] = r[value]
            mat.loc[r["domain_b"], r["domain_a"]] = r[value]
    return mat


# --------------------------------------------------------------------------- #
def figR01(comp, universe):
    core = comp[comp["is_core_pair"]]
    order = (core[core["spec"] == "main"].sort_values("assoc_log2")["pair"].tolist())

    fig, axes = plt.subplots(1, 2, figsize=(14.2, 6.2),
                             gridspec_kw={"width_ratios": [2.5, 1]})
    ax = axes[0]
    y = np.arange(len(order))
    for k, spec in enumerate(SPEC_ORDER):
        g = core[core["spec"] == spec].set_index("pair").reindex(order)
        offset = (k - (len(SPEC_ORDER) - 1) / 2) * 0.115
        ax.hlines(y + offset, g["assoc_ci_low"], g["assoc_ci_high"],
                  color=SPEC_COLOUR[spec], lw=1.4, alpha=0.65)
        ax.scatter(g["assoc_log2"], y + offset, s=38, color=SPEC_COLOUR[spec],
                   label=SPEC_LABEL[spec].replace("\n", ": "), zorder=3,
                   marker="D" if spec == "main" else "o")
    ax.axvline(0, color=GREY, lw=1.0, ls=(0, (4, 3)))
    for yi in y:
        ax.axhspan(yi - 0.42, yi + 0.42, color="#f2f2f2", zorder=0, linewidth=0)
    ax.set_yticks(y)
    ax.set_yticklabels([p.replace(" + ", "  +  ") for p in order], fontsize=9.5)
    ax.set_xlabel("log$_2$(observed / expected)")
    ax.set_xlim(-1.15, 2.05)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=7.6, loc="center right", ncol=1)
    ax.set_title("The six crossings under five readings of where culture belongs",
                 fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    u = universe.set_index("spec").reindex(SPEC_ORDER)
    yy = np.arange(len(SPEC_ORDER))[::-1]
    ax.barh(yy, u["n_classified"] / 1e6, height=0.34, color="#cfcfcf",
            label="hold at least one domain")
    ax.barh(yy - 0.36, u["n_crossing"] / 1e6, height=0.34,
            color=[SPEC_COLOUR[s] for s in SPEC_ORDER], label="cross two domains")
    for k, spec in enumerate(SPEC_ORDER):
        yk = yy[k]
        ax.text(u.loc[spec, "n_classified"] / 1e6 + 0.03, yk,
                f"{u.loc[spec, 'n_classified'] / 1e6:.2f}M", va="center", fontsize=7, color=GREY)
        ax.text(u.loc[spec, "n_crossing"] / 1e6 + 0.03, yk - 0.36,
                f"{u.loc[spec, 'n_crossing'] / 1e6:.2f}M "
                f"({u.loc[spec, 'crossing_share_of_classified']:.0%})",
                va="center", fontsize=7, color=GREY)
    ax.set_yticks(yy - 0.18)
    ax.set_yticklabels([SPEC_LABEL[s].split("\n")[0] for s in SPEC_ORDER], fontsize=8.4)
    ax.set_xlim(0, 2.3)
    ax.set_xlabel("million elites")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=7.6, loc="lower right")
    ax.set_title("What each reading leaves in", fontsize=10.5, loc="left", pad=10)

    fig.suptitle("Does the placement of cultural production change the answer?",
                 fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.075,
             "Four of the six crossings keep their sign under every reading: political with security stays positive "
             "(+0.33 to +1.07), and political-ideational,\nideational-security and economic-security stay negative. "
             "The two that flip do so only when culture becomes a fifth domain, which changes the\nreference model "
             "itself: with ten cells instead of six, the expected counts are redistributed, so scores are comparable "
             "within a reading and not across.\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figR01_culture_robustness")


def figR02(overall_five):
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 5.8),
                             gridspec_kw={"width_ratios": [1, 1.15]})
    mat = to_matrix(overall_five, FIVE)
    sig = to_matrix(overall_five.assign(s=(overall_five["q_value"] < 0.05).astype(float)),
                    FIVE, "s") == 1
    im = draw_matrix(axes[0], mat, sig=sig)
    cbar = fig.colorbar(im, ax=axes[0], shrink=0.78, pad=0.03, extend="both")
    cbar.set_label("log$_2$(observed / expected)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    axes[0].set_title("Association between five domains", fontsize=10.5, loc="left", pad=10)

    ax = axes[1]
    f = overall_five.sort_values("assoc_log2")
    y = np.arange(len(f))
    colours = ["#b2182b" if v > 0 else "#2166ac" for v in f["assoc_log2"]]
    ax.hlines(y, f["assoc_ci_low"], f["assoc_ci_high"], color=colours, lw=2.2, alpha=0.7)
    ax.scatter(f["assoc_log2"], y, color=colours, s=42, zorder=3)
    ax.axvline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
    ax.set_yticks(y)
    ax.set_yticklabels([p.replace(" + ", "  +  ") for p in f["pair"]], fontsize=8.6)
    ax.set_xlim(-1.15, 1.95)
    ax.set_xlabel("log$_2$(observed / expected)")
    ax.spines[["top", "right"]].set_visible(False)
    for yi, (_, r) in zip(y, f.iterrows()):
        ax.text(1.18, yi, f"n = {int(r['n_pair']):,}   ({r['share_of_diversified']:.0%})",
                fontsize=7.2, va="center", ha="left", color=GREY)
    ax.set_title("The ten crossings, ranked", fontsize=10.5, loc="left", pad=10)

    fig.suptitle("Culture as a domain of its own\n"
                 "374,703 elites crossing two of five domains",
                 fontsize=12.5, x=0.04, ha="left", y=1.06)
    fig.text(0.04, -0.10,
             "Splitting cultural production away from clerical and credentialled authority puts the church and the "
             "academy next to writers and performers\n(+0.47) and both away from politics: political-cultural is "
             "-0.57 and political-ideational -0.18. Culture is the domain furthest from the military\n(-0.89), which "
             "in this reading is fused with politics more tightly than anywhere else in the analysis (+1.07). " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figR02_five_domain_pooled")


def figR03(era_five):
    fig, axes = plt.subplots(1, 6, figsize=(18.0, 4.1))
    im = None
    for k, (ax, era) in enumerate(zip(axes, ERA_ORDER)):
        sub = era_five[era_five["period"] == era]
        if sub.empty:
            ax.axis("off")
            continue
        mat = to_matrix(sub, FIVE)
        sig = to_matrix(sub.assign(s=(sub["q_value"] < 0.05).astype(float)), FIVE, "s") == 1
        im = draw_matrix(ax, mat, sig=sig, labels=(k == 0), fontsize=6.4)
        n = int(sub["n_diversified_period"].iloc[0])
        ax.set_title(f"{era}\nn = {n:,} crossings", fontsize=8.4, loc="left", pad=6)
    cbar = fig.colorbar(im, ax=axes, shrink=0.72, pad=0.012, extend="both")
    cbar.set_label("log$_2$(obs / exp)", fontsize=7.5)
    cbar.ax.tick_params(labelsize=7)
    fig.suptitle("The five-domain matrix, era by era",
                 fontsize=12.5, x=0.04, ha="left", y=1.14)
    fig.text(0.04, -0.14,
             "Hatching marks a cell not distinguishable from the reference model (BH q $\\geq$ 0.05). Political with "
             "security is positive in every era here too;\npolitical with cultural is the pair that moves, from -1.26 "
             "in the earliest cohorts to -0.52 in the latest. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    save(fig, "figR03_five_domain_by_era")


def figR04(core_era):
    order = ["Political + Security", "Ideational + Economic", "Political + Ideational",
             "Political + Economic", "Ideational + Security", "Economic + Security"]
    xpos = {era: k for k, era in enumerate(ERA_ORDER)}
    fig, axes = plt.subplots(2, 3, figsize=(14.0, 7.2), sharex=True, sharey=True)
    for ax, pair in zip(axes.ravel(), order):
        for spec in SPEC_ORDER:
            g = (core_era[(core_era["pair"] == pair) & (core_era["spec"] == spec)]
                 .assign(x=lambda t: t["period"].map(xpos)).sort_values("x"))
            if g.empty:
                continue
            ax.plot(g["x"], g["assoc_log2"], color=SPEC_COLOUR[spec],
                    lw=2.2 if spec == "main" else 1.3,
                    marker="D" if spec == "main" else "o",
                    ms=4.2 if spec == "main" else 3.0,
                    alpha=1.0 if spec == "main" else 0.8,
                    label=SPEC_LABEL[spec].split("\n")[0])
        ax.axhline(0, color=GREY, lw=0.9, ls=(0, (4, 3)))
        ax.set_title(pair.replace(" + ", "  +  "), fontsize=9.5, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=7.5)
    for ax in axes[-1]:
        ax.set_xticks(range(len(ERA_ORDER)))
        ax.set_xticklabels(ERA_ORDER, rotation=45, ha="right", fontsize=7.2)
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=8,
               bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Each core crossing over time, under every reading",
                 fontsize=12.5, x=0.045, ha="left", y=1.0)
    fig.text(0.045, -0.085,
             "The readings move the level of a crossing far more often than its shape. The four readings that keep "
             "four domains are close to indistinguishable;\nthe five-domain reading in blue is the outlier, and it "
             "mostly shifts a path up or down without changing where it rises and falls. The exception is\n"
             "ideational with economic, where separating culture from the academy turns the crossing negative in "
             "every cohort after 1000.\n" + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.035, 1, 0.97])
    save(fig, "figR04_core_pairs_across_readings")


def main():
    comp = pd.read_csv(DATA / "robustness_pair_comparison.csv")
    universe = pd.read_csv(DATA / "robustness_universe.csv")
    core_era = pd.read_csv(DATA / "robustness_core_by_era.csv")
    overall_five = pd.read_csv(DATA / "culture_own_pair_association_overall.csv")
    era_five = pd.read_csv(DATA / "culture_own_pair_association_by_era.csv")

    print("writing robustness figures")
    figR01(comp, universe)
    figR02(overall_five)
    figR03(era_five)
    figR04(core_era)


if __name__ == "__main__":
    main()
