"""Shared figure styling for the sector and domain layers."""

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use("Agg")

FIGS = pathlib.Path(__file__).resolve().parents[1] / "figures"
FIGS.mkdir(exist_ok=True)

CMAP = plt.get_cmap("RdBu_r")
GREY = "#4d4d4d"
RED = "#b2182b"
BLUE = "#2166ac"

SOURCE = ("Source: BHHT cross-verified database of notable people "
          "(Laouenan et al., Scientific Data 9:290, 2022).")

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


def save(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(FIGS / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    print(f"  figures/{name}.pdf / .png")
