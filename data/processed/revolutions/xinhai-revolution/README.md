# Xinhai Revolution, 1911-1912

The end of the Qing dynasty and of the imperial examination elite.

Countries whose political order was at stake: China.

## The cohort

831 elites, of whom 514 (62%) span two sectors. Birth years 1823 to 1892; median age when the window opened, 31. Death year is imputed as birth plus 80 for 4% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 0 |
| 20-35 | 494 |
| 36-55 | 251 |
| 56+ | 86 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 47.8% |
| Learning & Culture | 36.3% |
| Military | 21.4% |
| Religion | 13.2% |
| Business | 13.0% |
| Nobility & Kinship | 11.2% |
| Administration & Law | 9.1% |

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
