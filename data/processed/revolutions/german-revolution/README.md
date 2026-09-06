# German Revolution, 1918-1919

The fall of the two central European monarchies and the republics that replaced them.

Countries whose political order was at stake: Germany, Austria.

## The cohort

54,018 elites, of whom 22,942 (42%) span two sectors. Birth years 1828 to 1899; median age when the window opened, 38. Death year is imputed as birth plus 80 for 2% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 0 |
| 20-35 | 22,938 |
| 36-55 | 19,818 |
| 56+ | 11,262 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Learning & Culture | 61.4% |
| Politics | 26.4% |
| Business | 12.8% |
| Administration & Law | 10.8% |
| Military | 8.3% |
| Religion | 4.2% |
| Nobility & Kinship | 2.8% |

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
