# Chinese Communist Revolution, 1946-1949

The civil war and the founding of the People's Republic.

Countries whose political order was at stake: China.

## The cohort

2,698 elites, of whom 1,336 (50%) span two sectors. Birth years 1856 to 1929; median age when the window opened, 36. Death year is imputed as birth plus 80 for 9% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 70 |
| 20-35 | 1,083 |
| 36-55 | 1,122 |
| 56+ | 423 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Learning & Culture | 50.6% |
| Politics | 39.9% |
| Military | 13.5% |
| Business | 10.4% |
| Administration & Law | 8.4% |
| Religion | 7.4% |
| Nobility & Kinship | 6.0% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1840 to 1999, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
