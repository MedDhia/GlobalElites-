# Russian Revolution, 1917-1923

February, October and the civil war, across the territory of the Russian empire.

Countries whose political order was at stake: Russia, Ukraine, Poland, Finland, Latvia, Lithuania, Estonia, Georgia, Belarus, Azerbaijan, Armenia.

## The cohort

13,925 elites, of whom 6,669 (48%) span two sectors. Birth years 1828 to 1903; median age when the window opened, 31. Death year is imputed as birth plus 80 for 2% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 1,259 |
| 20-35 | 6,057 |
| 36-55 | 4,500 |
| 56+ | 2,109 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Learning & Culture | 64.7% |
| Politics | 22.0% |
| Military | 12.9% |
| Business | 8.4% |
| Nobility & Kinship | 6.7% |
| Administration & Law | 6.0% |
| Religion | 5.9% |

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
