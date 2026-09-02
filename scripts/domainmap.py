"""Sector-to-domain mappings and the person-level derivation they drive.

The assignment of sectors to domains is a reading, not a measurement, so every
mapping the analysis uses lives here as a named specification. `main` is the one
reported in the README; the others exist so the reader can see how much of each
conclusion survives a different reading of where cultural production belongs.

Sectors left out of a specification are unclassified for that specification: they
do not create a domain, and an elite holding only unclassified sectors drops out
of that specification's universe.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CULTURE = ["Culture (core)", "Culture (periphery)"]

_POLITICAL = {"Politics": "Political", "Administration & Law": "Political"}
_SECURITY = {"Military": "Security"}
_ECONOMIC_WITH_INVENTION = {"Big business": "Economic", "Small business": "Economic",
                            "Exploration & Invention": "Economic"}
_ECONOMIC_PLAIN = {"Big business": "Economic", "Small business": "Economic"}
_CREDENTIAL = {"Religion": "Ideational", "Academia": "Ideational"}
_CULTURE_IDEATIONAL = {"Culture (core)": "Ideational", "Culture (periphery)": "Ideational"}
_CULTURE_OWN = {"Culture (core)": "Cultural", "Culture (periphery)": "Cultural"}

FOUR = ["Political", "Ideational", "Economic", "Security"]
FIVE = ["Political", "Ideational", "Cultural", "Economic", "Security"]


SPECS: dict[str, dict] = {
    "main": {
        "label": "Main: Culture inside the ideational domain",
        "short": "main",
        "domains": FOUR,
        "mapping": {**_POLITICAL, **_CREDENTIAL, **_CULTURE_IDEATIONAL,
                    **_ECONOMIC_WITH_INVENTION, **_SECURITY},
        "note": "Ideational power read broadly as meaning-making: the church, the "
                "academy and cultural production together.",
    },
    "culture_out": {
        "label": "Culture dropped: ideational = religion and the academy",
        "short": "culture out",
        "domains": FOUR,
        "mapping": {**_POLITICAL, **_CREDENTIAL,
                    **_ECONOMIC_WITH_INVENTION, **_SECURITY},
        "note": "Ideational power read narrowly as clerical and credentialled "
                "authority. Writers, performers and journalists leave the universe.",
    },
    "culture_own": {
        "label": "Culture as a fifth domain of its own",
        "short": "culture own",
        "domains": FIVE,
        "mapping": {**_POLITICAL, **_CREDENTIAL, **_CULTURE_OWN,
                    **_ECONOMIC_WITH_INVENTION, **_SECURITY},
        "note": "Cultural production separated from clerical and credentialled "
                "authority, so a writer who is also an academic now crosses a boundary.",
    },
    "culture_core_only": {
        "label": "Only Culture (core) counts as ideational",
        "short": "core only",
        "domains": FOUR,
        "mapping": {**_POLITICAL, **_CREDENTIAL, "Culture (core)": "Ideational",
                    **_ECONOMIC_WITH_INVENTION, **_SECURITY},
        "note": "Writers and composers produce ideas; performers, journalists and "
                "designers are dropped.",
    },
    "invention_ideational": {
        "label": "Exploration & Invention moved to the ideational domain",
        "short": "invention ideational",
        "domains": FOUR,
        "mapping": {**_POLITICAL, **_CREDENTIAL, **_CULTURE_IDEATIONAL,
                    "Exploration & Invention": "Ideational",
                    **_ECONOMIC_PLAIN, **_SECURITY},
        "note": "Inventors and explorers read as knowledge producers instead of "
                "creators of productive assets. Everything else as in the main "
                "specification.",
    },
}

CORE_PAIRS = ["Political + Ideational", "Political + Economic", "Political + Security",
              "Ideational + Economic", "Ideational + Security", "Economic + Security"]


def derive(df: pd.DataFrame, spec: dict) -> pd.DataFrame:
    """Attach domain columns for one specification. Does not mutate `df`."""
    mapping = spec["mapping"]
    order = spec["domains"]
    rank = {d: k for k, d in enumerate(order)}

    out = df.copy()
    out["domain_main"] = out["sector_main"].map(mapping)
    out["domain_second"] = out["sector_second"].map(mapping)

    has_main = out["domain_main"].notna()
    has_second = out["domain_second"].notna()
    same = has_main & has_second & (out["domain_main"] == out["domain_second"])
    out["n_domains"] = has_main.astype(int) + has_second.astype(int) - same.astype(int)
    out["crosses_domains"] = out["n_domains"] == 2

    only = out["domain_main"].where(has_main, out["domain_second"])
    a = out["domain_main"].map(rank)
    b = out["domain_second"].map(rank)
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    pair_label = [f"{order[int(x)]} + {order[int(y)]}" if np.isfinite(x) and np.isfinite(y)
                  else "" for x, y in zip(lo, hi)]
    out["portfolio"] = np.where(
        out["n_domains"] == 0, "Unclassified",
        np.where(out["n_domains"] == 1, only.fillna("") + " only",
                 pd.Series(pair_label, index=out.index)))

    out["sector_span"] = np.select(
        [out["sector_second"].isna(),
         out["n_domains"] == 2,
         has_main & has_second & same,
         out["n_domains"] == 1],
        ["one sector", "two sectors, two domains", "two sectors, one domain",
         "two sectors, one classified"],
        default="two sectors, none classified")
    return out
