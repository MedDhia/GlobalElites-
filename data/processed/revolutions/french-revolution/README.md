# French Revolution, 1789-1799

The abolition of the orders, the confiscation of church property and the reconstruction of the administration.

Countries whose political order was at stake: France.

## The cohort

12,685 elites, of whom 5,715 (45%) span two sectors. Birth years 1699 to 1779; median age when the window opened, 34. Death year is imputed as birth plus 80 for 3% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 962 |
| 20-35 | 4,456 |
| 36-55 | 4,909 |
| 56+ | 2,358 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 51.6% |
| Learning & Culture | 30.1% |
| Military | 26.0% |
| Administration & Law | 9.5% |
| Nobility & Kinship | 7.4% |
| Religion | 7.0% |
| Business | 6.9% |

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
