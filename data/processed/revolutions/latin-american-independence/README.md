# Latin American independence, 1810-1825

The Spanish American wars of independence and the Brazilian separation, grouped as one wave.

Countries whose political order was at stake: Argentina, Mexico, Colombia, Venezuela, Chile, Peru, Bolivia, Ecuador, Uruguay, Paraguay, Brazil.

## The cohort

2,976 elites, of whom 2,108 (71%) span two sectors. Birth years 1723 to 1805; median age when the window opened, 24. Death year is imputed as birth plus 80 for 2% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 542 |
| 20-35 | 1,195 |
| 36-55 | 923 |
| 56+ | 316 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 63.6% |
| Military | 36.5% |
| Learning & Culture | 18.0% |
| Administration & Law | 15.1% |
| Nobility & Kinship | 12.9% |
| Business | 10.3% |
| Religion | 9.1% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1720 to 1959, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
