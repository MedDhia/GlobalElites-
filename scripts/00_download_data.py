"""Download the BHHT cross-verified database of notable people (Scientific Data, 2022).

Source
------
Laouenan, M., Bhargava, P., Eymeoud, J.-B., Gergaud, O., Plique, G. & Wasmer, E.
"A cross-verified database of notable people, 3500BC-2018AD."
Scientific Data 9, 290 (2022). https://doi.org/10.1038/s41597-022-01369-4

Data are distributed through the Sciences Po Dataverse:
  doi:10.21410/7E4/RDAG3O  (file: cross-verified-database.csv.gz, ~250 MB)

The archive is too large to version in git, so it is written to data/raw/ which
is git-ignored. Run this script once before the rest of the pipeline.
"""

import hashlib
import pathlib
import sys
import urllib.request

DATAVERSE_FILE_ID = 4432
URL = f"https://data.sciencespo.fr/api/access/datafile/{DATAVERSE_FILE_ID}"
DEST = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw" / "cross-verified-database.csv.gz"
EXPECTED_BYTES = 261_545_417


def main() -> int:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists() and DEST.stat().st_size == EXPECTED_BYTES:
        print(f"already present: {DEST}")
        return 0

    print(f"downloading {URL}\n  -> {DEST}")
    with urllib.request.urlopen(URL) as resp, open(DEST, "wb") as out:
        total = 0
        digest = hashlib.sha256()
        while chunk := resp.read(1 << 20):
            out.write(chunk)
            digest.update(chunk)
            total += len(chunk)
            print(f"\r  {total / 1e6:8.1f} MB", end="", file=sys.stderr)
    print(f"\ndone: {total} bytes, sha256={digest.hexdigest()}")
    if total != EXPECTED_BYTES:
        print(f"WARNING: expected {EXPECTED_BYTES} bytes; the upstream file may have been revised.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
