# American Revolution, 1775-1783

Secession and the founding of a republic without a titled nobility.

Countries whose political order was at stake: US.

## The cohort

2,925 elites, of whom 2,076 (71%) span two sectors. Birth years 1687 to 1763; median age when the window opened, 29. Death year is imputed as birth plus 80 for 1% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 381 |
| 20-35 | 1,240 |
| 36-55 | 1,019 |
| 56+ | 285 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 66.9% |
| Military | 25.4% |
| Administration & Law | 24.8% |
| Learning & Culture | 20.6% |
| Business | 15.7% |
| Nobility & Kinship | 7.9% |
| Religion | 6.5% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1640 to 1919, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
