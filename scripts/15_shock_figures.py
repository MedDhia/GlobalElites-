"""Figures for the shock event study.

Reads data/processed/shocks/ and writes PDF plus 300-dpi PNG into figures/.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from plotstyle import BLUE, GREY, RED, save

ROOT = pathlib.Path(__file__).resolve().parents[1]
SD = ROOT / "data" / "processed" / "shocks"

PAIR_ORDER = ["Political + Security", "Ideational + Economic", "Political + Ideational",
              "Political + Economic", "Ideational + Security", "Economic + Security"]
TYPE_COLOUR = {"revolutionary rupture": "#b2182b", "state creation": "#2166ac"}
SOURCE = ("Source: BHHT cross-verified database of notable people "
          "(Laouenan et al., Scientific Data 9:290, 2022). Shocks hand-coded, "
          "see data/processed/shocks/shock_list.csv.")


def figE01(coverage, shocks):
    cov = coverage[coverage["country_in_panel"]].copy()
    countries = sorted(cov["country"].unique())
    cohorts = sorted(cov["cohort"].unique())
    mat = (cov.pivot(index="country", columns="cohort", values="n_crossings")
           .reindex(index=countries, columns=cohorts))
    usable = (cov.pivot(index="country", columns="cohort", values="usable")
              .reindex(index=countries, columns=cohorts).fillna(False))

    fig, ax = plt.subplots(figsize=(13.6, 7.0))
    data = np.log10(mat.to_numpy(dtype=float))
    ax.imshow(np.ma.masked_invalid(np.where(usable.to_numpy(), data, np.nan)),
              cmap="Greens", vmin=2, vmax=4, aspect="auto")
    for i, country in enumerate(countries):
        for j, cohort in enumerate(cohorts):
            v = mat.loc[country, cohort]
            if not np.isfinite(v):
                continue
            if usable.loc[country, cohort]:
                ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=5.8,
                        color="white" if v > 1200 else "#1a1a1a")
            else:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#f0f0f0",
                                           edgecolor="white", zorder=2))
                ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=5.4,
                        color="#999999", zorder=3)
    shock_map = shocks.set_index("country")
    for i, country in enumerate(countries):
        if country not in shock_map.index:
            continue
        g = shock_map.loc[country, "first_treated_cohort_main"]
        if g in cohorts:
            x = cohorts.index(g) - 0.5
            colour = TYPE_COLOUR[shock_map.loc[country, "type"]]
            ax.plot([x, x], [i - 0.5, i + 0.5], color=colour, lw=3.2, zorder=5)
            ax.text(x, i - 0.34, f"{int(shock_map.loc[country, 'year'])}", ha="center",
                    va="center", fontsize=6.0, color=colour, zorder=6,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))
    ax.set_xticks(range(len(cohorts)))
    ax.set_xticklabels(cohorts, rotation=45, ha="right", fontsize=7.4)
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries, fontsize=8)
    ax.set_xticks(np.arange(-0.5, len(cohorts), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(countries), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel("birth cohort")
    handles = [Patch(color=c, label=t) for t, c in TYPE_COLOUR.items()]
    handles.append(Patch(facecolor="#f0f0f0", label="below the 120-crossing floor, cell unusable"))
    ax.legend(handles=handles, fontsize=7.6, loc="upper left", bbox_to_anchor=(0, -0.12), ncol=3)
    ax.set_title("What the panel actually contains",
                 fontsize=12.5, loc="left", pad=12)
    fig.text(0.0, -0.19,
             "Elites crossing two domains in each country and 25-year birth cohort. A cell enters the event study only "
             "above 120 crossings. The vertical bar marks the\nfirst exposed cohort for that country's shock, taken as "
             "50 years before the shock year because a cohort's careers run roughly 25 to 90 years after birth.\n"
             "Read the gaps: Argentina and Brazil have no cohort at all before their shock, so they cannot enter. "
             "Only four countries are never exposed inside the\nwindow, and three of the four rupture cases share a "
             "single event in 1918. " + SOURCE, fontsize=7.4, color=GREY, ha="left")
    save(fig, "figE01_shock_panel")


def figE02(att):
    fig, axes = plt.subplots(2, 6, figsize=(17.4, 7.4), sharex=True)
    for row, shock_type in enumerate(["revolutionary rupture", "state creation"]):
        for col, pair in enumerate(PAIR_ORDER):
            ax = axes[row, col]
            g = att[(att["shock_type"] == shock_type) & (att["outcome"] == pair)]
            g = g.sort_values("event_time")
            if g.empty:
                ax.axis("off")
                continue
            x = g["event_time"].to_numpy(dtype=float)
            ax.fill_between(x, g["null_ci_low"], g["null_ci_high"], color="#d9d9d9",
                            alpha=0.85, linewidth=0, zorder=1,
                            label="95% randomization null")
            ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)), zorder=2)
            ax.axvline(-0.5, color="#111111", lw=1.0, zorder=2)
            pre = x < 0
            ax.plot(x[pre], g["att"].to_numpy()[pre], color=GREY, lw=1.4, marker="o",
                    ms=4, ls=(0, (3, 2)), zorder=3)
            ax.plot(x[~pre], g["att"].to_numpy()[~pre], color=TYPE_COLOUR[shock_type],
                    lw=1.9, marker="o", ms=4.6, zorder=3)
            ax.set_xticks([-3, -2, 0, 1, 2, 3])
            ax.tick_params(labelsize=7)
            ax.spines[["top", "right"]].set_visible(False)
            if row == 0:
                ax.set_title(pair.replace(" + ", "\n+ "), fontsize=8.4, loc="left",
                             linespacing=1.15)
            if col == 0:
                ax.set_ylabel(f"{shock_type}\n\nATT, log$_2$(obs / exp)", fontsize=8)
            if row == 1:
                ax.set_xlabel("event time\n(25-year cohorts)", fontsize=8)
    axes[0, 0].legend(fontsize=6.6, loc="upper left")
    fig.suptitle("No shock shows a persistent effect that the randomization null does not already produce",
                 fontsize=12.5, x=0.035, ha="left", y=1.0)
    fig.text(0.035, -0.075,
             "ATT(e) from a Callaway-Sant'Anna style group-time estimator with not-yet-exposed and never-exposed "
             "countries as controls, cells weighted by the inverse\nof their bootstrap variance. Event time -1 is the "
             "reference; the black line marks exposure. The grey band is the middle 95% of 2,000 draws in which the "
             "shock years\nare reassigned at random across the sixteen panel countries. Five of the 72 estimates fall "
             "outside it, against 3.6 expected by chance, and none survives a\nBenjamini-Hochberg adjustment. Two of "
             "the five are at pre-exposure event times, which is a failure and not a finding. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.96])
    save(fig, "figE02_event_study")


def figE03(att, placebo, placebo_time):
    fig, axes = plt.subplots(1, 3, figsize=(15.4, 5.6))

    ax = axes[0]
    w = att.pivot_table(index=["shock_type", "outcome"], columns="event_time", values="att")
    pre = w[[-3, -2]].abs().max(axis=1)
    post = w[[0, 1, 2, 3]].abs().max(axis=1)
    colours = [TYPE_COLOUR[s] for s, _ in w.index]
    ax.scatter(post, pre, s=52, color=colours, alpha=0.85, zorder=3)
    lim = max(post.max(), pre.max()) * 1.15
    ax.plot([0, lim], [0, lim], color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax.text(lim * 0.62, lim * 0.68, "pre-trend as large\nas the effect", fontsize=7.4,
            color=GREY, rotation=38, ha="center")
    for k, ((s, o), xx, yy) in enumerate(zip(w.index, post, pre)):
        ax.annotate(o.replace(" + ", "+"), (xx, yy), textcoords="offset points",
                    xytext=(0, 8 if k % 2 == 0 else -13), ha="center", fontsize=6.2,
                    color="#333333")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("largest |ATT| after exposure")
    ax.set_ylabel("largest |ATT| before exposure")
    ax.set_title("1. Pre-trends are the size of the effects", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    counts = []
    for label, frame in (("association scores\n(the outcome)", att),
                         ("composition and volume\n(the placebo)", placebo)):
        pre_f = frame[frame["event_time"] < 0]
        post_f = frame[frame["event_time"] >= 0]
        counts.append({"label": label,
                       "pre": int((pre_f["p_value_ri"] < 0.05).sum()),
                       "post": int((post_f["p_value_ri"] < 0.05).sum()),
                       "n_pre": len(pre_f), "n_post": len(post_f)})
    cdf = pd.DataFrame(counts)
    x = np.arange(len(cdf))
    ax.bar(x - 0.18, cdf["pre"], width=0.34, color="#999999",
           label=f"before exposure (of {cdf['n_pre'].iloc[0]})")
    ax.bar(x + 0.18, cdf["post"], width=0.34, color=RED,
           label=f"after exposure (of {cdf['n_post'].iloc[0]})")
    # The two groups hold different numbers of estimates, so the chance level differs.
    for k in x:
        ax.plot([k - 0.35, k - 0.01], [0.05 * cdf["n_pre"].iloc[k]] * 2,
                color=GREY, lw=1.1, ls=(0, (3, 2)))
        ax.plot([k + 0.01, k + 0.35], [0.05 * cdf["n_post"].iloc[k]] * 2,
                color=GREY, lw=1.1, ls=(0, (3, 2)))
    ax.text(1.35, 0.05 * cdf["n_post"].iloc[0] + 0.25, "expected by chance", fontsize=7,
            color=GREY, ha="center")
    ax.set_xticks(x)
    ax.set_xticklabels(cdf["label"], fontsize=8)
    ax.set_ylabel("estimates with randomization p < 0.05")
    ax.set_title("2. The placebo moves more than the outcome", fontsize=10, loc="left")
    ax.legend(fontsize=7.6)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    real = att[att["event_time"] >= 0]["att"].abs()
    fake = placebo_time[placebo_time["event_time"] >= 0]["att"].abs()
    bins = np.linspace(0, max(real.max(), fake.max()) * 1.05, 12)
    # The two sets hold different numbers of estimates, so compare densities.
    ax.hist(real, bins=bins, color=RED, alpha=0.6, density=True,
            label=f"real shock dates (n = {len(real)})")
    ax.hist(fake, bins=bins, color=BLUE, alpha=0.5, density=True,
            label=f"moved 100 years earlier (n = {len(fake)})")
    ax.set_xlabel("|ATT| after exposure")
    ax.set_ylabel("density of estimates")
    ax.set_title("3. Fake dates do about as well", fontsize=10, loc="left")
    ax.legend(fontsize=7.6)
    ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Three tests, and the design fails two of them",
                 fontsize=12.5, x=0.04, ha="left", y=1.02)
    fig.text(0.04, -0.115,
             "Left: for eleven of the twelve shock-type by crossing combinations the largest pre-exposure estimate is "
             "more than a sixth of the largest post-exposure one, and\nfor one it is larger. Parallel trends is not a "
             "close call here. Middle: running the identical estimator on the share of elites in each domain, the "
             "crossing rate and the\nlog number of recorded elites returns more results at p < 0.05 than the "
             "association scores do, and the strongest of them are before exposure. Whatever the\nshock countries are "
             "doing differently, they were doing it first, and it shows up in who gets recorded. Right: the estimator "
             "itself is not manufacturing effects, since\nfake dates produce a similar spread and nothing significant. "
             "The problem is the design, not the arithmetic. " + SOURCE,
             fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout()
    save(fig, "figE03_falsification")


def figE04(panel, shocks, coverage):
    treated = ["France", "Germany", "Russia", "Austria"]
    controls = ["Spain", "Sweden", "Switzerland", "United Kingdom"]
    shock_map = shocks.set_index("country")
    fig, axes = plt.subplots(2, 3, figsize=(15.0, 7.6), sharex=True)
    colours = {"France": "#b2182b", "Germany": "#d6604d", "Russia": "#762a83",
               "Austria": "#e08214"}
    for ax, pair in zip(axes.ravel(), PAIR_ORDER):
        g = panel[panel["pair"] == pair]
        ctrl = (g[g["country"].isin(controls)].groupby("cohort")
                .apply(lambda d: np.average(d["assoc_log2"],
                                            weights=1 / d["assoc_boot_se"] ** 2),
                       include_groups=False))
        ax.plot(ctrl.index, ctrl.to_numpy(), color="#555555", lw=2.4,
                label="never exposed (mean of 4)", zorder=4)
        for country in treated:
            s = g[g["country"] == country].sort_values("cohort")
            if s.empty:
                continue
            ax.plot(s["cohort"], s["assoc_log2"], color=colours[country], lw=1.5,
                    marker="o", ms=3.2, alpha=0.9, label=country)
            gg = shock_map.loc[country, "first_treated_cohort_main"]
            ax.axvline(gg, color=colours[country], lw=1.0, ls=(0, (2, 2)), alpha=0.6)
        ax.axhline(0, color=GREY, lw=0.8, ls=(0, (4, 3)))
        ax.set_title(pair.replace(" + ", "  +  "), fontsize=9.4, loc="left")
        ax.tick_params(labelsize=7.4)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("birth cohort")
    for ax in axes[:, 0]:
        ax.set_ylabel("log$_2$(obs / exp)")
    axes[0, 0].legend(fontsize=6.8, loc="lower left", ncol=2)
    fig.suptitle("The four rupture cases against the countries that had no rupture",
                 fontsize=12.5, x=0.04, ha="left", y=1.0)
    fig.text(0.04, -0.075,
             "Descriptive, not causal. Dashed vertical lines mark each country's first exposed cohort. The series are "
             "noisy, the treated countries are not on a common path\nbefore exposure, and three of the four share the "
             "same 1918 event, which is why the event study above cannot separate a shock from everything else "
             "happening\nto those countries at the time. " + SOURCE, fontsize=7.4, color=GREY, ha="left")
    fig.tight_layout(rect=[0, 0.01, 1, 0.96])
    save(fig, "figE04_rupture_trajectories")


def main():
    coverage = pd.read_csv(SD / "shock_panel_coverage.csv")
    shocks = pd.read_csv(SD / "shock_list.csv")
    panel = pd.read_csv(SD / "shock_panel_pairs.csv")
    att = pd.read_csv(SD / "event_study_att.csv")
    placebo = pd.read_csv(SD / "event_study_placebo.csv")
    placebo_time = pd.read_csv(SD / "event_study_placebo_time.csv")

    print("writing shock figures")
    figE01(coverage, shocks)
    figE02(att)
    figE03(att, placebo, placebo_time)
    figE04(panel, shocks, coverage)


if __name__ == "__main__":
    main()
