# Turkish revolution, 1919-1923

The war of independence, the end of the sultanate and the caliphate, and the republic.

Countries whose political order was at stake: Turkey.

## The cohort

722 elites, of whom 449 (62%) span two sectors. Birth years 1832 to 1903; median age when the window opened, 37. Death year is imputed as birth plus 80 for 2% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 47 |
| 20-35 | 256 |
| 36-55 | 320 |
| 56+ | 99 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 45.8% |
| Learning & Culture | 39.5% |
| Military | 30.1% |
| Administration & Law | 11.8% |
| Nobility & Kinship | 7.9% |
| Religion | 6.1% |
| Business | 3.5% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1800 to 1999, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
