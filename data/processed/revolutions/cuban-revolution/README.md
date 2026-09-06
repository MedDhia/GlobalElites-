# Cuban Revolution, 1953-1959

The insurgency against Batista and the state built after it.

Countries whose political order was at stake: Cuba.

## The cohort

1,260 elites, of whom 490 (39%) span two sectors. Birth years 1867 to 1939; median age when the window opened, 32. Death year is imputed as birth plus 80 for 24% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 116 |
| 20-35 | 539 |
| 36-55 | 400 |
| 56+ | 205 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Learning & Culture | 58.0% |
| Politics | 16.9% |
| Administration & Law | 8.2% |
| Military | 5.7% |
| Business | 5.0% |
| Nobility & Kinship | 4.6% |
| Religion | 2.9% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1840 to 1959, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
