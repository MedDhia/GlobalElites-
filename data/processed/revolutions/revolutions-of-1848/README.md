# Revolutions of 1848, 1848-1849

The European wave: constitutional and national risings, defeated almost everywhere within two years.

Countries whose political order was at stake: France, Germany, Austria, Hungary, Italy, Poland, Czech Republic, Romania.

## The cohort

36,998 elites, of whom 17,922 (48%) span two sectors. Birth years 1758 to 1829; median age when the window opened, 39. Death year is imputed as birth plus 80 for 1% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 0 |
| 20-35 | 14,754 |
| 36-55 | 14,727 |
| 56+ | 7,517 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Learning & Culture | 57.4% |
| Politics | 30.6% |
| Business | 12.8% |
| Administration & Law | 12.1% |
| Military | 9.1% |
| Religion | 7.2% |
| Nobility & Kinship | 7.2% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1720 to 1999, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
