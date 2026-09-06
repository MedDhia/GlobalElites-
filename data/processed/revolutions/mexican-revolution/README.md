# Mexican Revolution, 1910-1920

The fall of the Porfiriato and a decade of civil war ending in the 1917 constitution.

Countries whose political order was at stake: Mexico.

## The cohort

1,923 elites, of whom 1,213 (63%) span two sectors. Birth years 1820 to 1900; median age when the window opened, 26. Death year is imputed as birth plus 80 for 5% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 294 |
| 20-35 | 854 |
| 36-55 | 494 |
| 56+ | 281 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Learning & Culture | 43.3% |
| Military | 34.2% |
| Politics | 33.3% |
| Administration & Law | 13.7% |
| Business | 8.4% |
| Religion | 8.3% |
| Nobility & Kinship | 7.1% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1760 to 1999, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
