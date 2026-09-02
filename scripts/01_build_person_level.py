"""Build the person-level analysis file from the raw BHHT database.

Each notable person in BHHT carries a *main* and (often) a *second* occupational
domain at level 2 of the taxonomy. Read substantively, those two domains are the
sectors from which an individual drew authority, income or standing: politics,
the military, the church, landed nobility, business, the academy, culture, and so
on. A person coded with two distinct level-2 domains therefore spans two sectors,
and the population of such people is what lets us ask which sectors go together.

Output: data/processed/elites_person_level.csv.gz
"""

import gzip
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cross-verified-database.csv.gz"
OUT = ROOT / "data" / "processed" / "elites_person_level.csv.gz"

# The 13 substantive level-2 domains. "Other" and "Missing" are dropped: they are
# residual codes, not sectors, and treating them as one would create a spurious
# hub in every co-occurrence matrix.
SECTORS = [
    "Politics",
    "Administration/Law",
    "Military",
    "Religious",
    "Nobility",
    "Family",
    "Corporate/Executive/Business (large)",
    "Worker/Business (small)",
    "Academia",
    "Explorer/Inventor/Developer",
    "Culture-core",
    "Culture-periphery",
    "Sports/Games",
]

# Short labels used on figures and in the pair-level tables.
SECTOR_LABEL = {
    "Politics": "Politics",
    "Administration/Law": "Administration & Law",
    "Military": "Military",
    "Religious": "Religion",
    "Nobility": "Nobility",
    "Family": "Kinship",
    "Corporate/Executive/Business (large)": "Big business",
    "Worker/Business (small)": "Small business",
    "Academia": "Academia",
    "Explorer/Inventor/Developer": "Exploration & Invention",
    "Culture-core": "Culture (core)",
    "Culture-periphery": "Culture (periphery)",
    "Sports/Games": "Sport & Games",
}

USECOLS = [
    "wikidata_code",
    "name",
    "birth",
    "death",
    "gender",
    "un_region",
    "un_subregion",
    "level1_main_occ",
    "level2_main_occ",
    "level2_second_occ",
    "level3_main_occ",
    "freq_main_occ",
    "freq_second_occ",
    "sum_visib_ln_5criteria",
]

# Broad eras used for the small-multiple matrices and the sector networks.
ERA_EDGES = [(-4000, 999, "Pre-1000"),
             (1000, 1399, "1000-1399"),
             (1400, 1599, "1400-1599"),
             (1600, 1799, "1600-1799"),
             (1800, 1899, "1800-1899"),
             (1900, 2020, "1900-2020")]


def assign_era(year: float) -> str:
    for lo, hi, name in ERA_EDGES:
        if lo <= year <= hi:
            return name
    return "Out of range"


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"missing {RAW}; run scripts/00_download_data.py first")

    frames = []
    with gzip.open(RAW, "rt", encoding="utf-8", errors="replace") as handle:
        reader = pd.read_csv(handle, usecols=USECOLS, chunksize=250_000,
                             dtype=str, low_memory=False)
        for chunk in reader:
            frames.append(chunk)
    df = pd.concat(frames, ignore_index=True)
    print(f"raw rows: {len(df):,}")

    for col in ("birth", "death", "freq_main_occ", "freq_second_occ", "sum_visib_ln_5criteria"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["birth"].notna()]
    df = df[(df["birth"] >= -4000) & (df["birth"] <= 2020)]
    print(f"with a usable birth year: {len(df):,}")

    df = df[df["level2_main_occ"].isin(SECTORS)].copy()
    print(f"with a substantive main sector: {len(df):,}")

    df["sector_main"] = df["level2_main_occ"].map(SECTOR_LABEL)
    second = df["level2_second_occ"].where(df["level2_second_occ"].isin(SECTORS))
    df["sector_second"] = second.map(SECTOR_LABEL)
    # A second domain identical to the main one carries no cross-sector information.
    df.loc[df["sector_second"] == df["sector_main"], "sector_second"] = pd.NA
    df["diversified"] = df["sector_second"].notna()

    df["birth_century"] = (df["birth"] // 100).astype(int) * 100
    df["era"] = df["birth"].map(assign_era)
    df["region"] = df["un_region"].replace("", pd.NA).fillna("Unknown")
    df["subregion"] = df["un_subregion"].replace("", pd.NA).fillna("Unknown")

    out = df[[
        "wikidata_code", "name", "birth", "death", "gender", "region", "subregion",
        "level1_main_occ", "sector_main", "sector_second", "level3_main_occ",
        "freq_main_occ", "freq_second_occ", "sum_visib_ln_5criteria",
        "birth_century", "era", "diversified",
    ]].rename(columns={"level1_main_occ": "domain_level1",
                       "level3_main_occ": "occupation_level3",
                       "sum_visib_ln_5criteria": "visibility"})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # mtime=0 keeps the archive byte-identical across reruns, so an unchanged
    # extract does not show up as a new 60 MB blob in git.
    out.to_csv(OUT, index=False, compression={"method": "gzip", "mtime": 0})
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB), {len(out):,} rows")
    print(f"  spanning two sectors: {out['diversified'].sum():,} "
          f"({out['diversified'].mean():.1%})")


if __name__ == "__main__":
    main()
