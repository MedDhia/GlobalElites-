# Irish revolution, 1916-1923

The rising, the war of independence, partition and the civil war.

Countries whose political order was at stake: Ireland.

## The cohort

3,104 elites, of whom 1,327 (43%) span two sectors. Birth years 1826 to 1903; median age when the window opened, 36. Death year is imputed as birth plus 80 for 6% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 181 |
| 20-35 | 1,066 |
| 36-55 | 1,119 |
| 56+ | 738 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 36.0% |
| Learning & Culture | 35.1% |
| Business | 10.8% |
| Religion | 9.0% |
| Military | 8.5% |
| Administration & Law | 7.8% |
| Nobility & Kinship | 6.1% |

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
