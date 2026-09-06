# English Revolution, 1642-1651

Civil war, regicide and the Commonwealth. The one case in the set where the old order was restored within a generation.

Countries whose political order was at stake: United Kingdom, Ireland.

## The cohort

4,037 elites, of whom 2,423 (60%) span two sectors. Birth years 1555 to 1631; median age when the window opened, 35. Death year is imputed as birth plus 80 for 3% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 342 |
| 20-35 | 1,320 |
| 36-55 | 1,457 |
| 56+ | 918 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 48.1% |
| Learning & Culture | 29.7% |
| Nobility & Kinship | 25.5% |
| Religion | 18.8% |
| Administration & Law | 13.0% |
| Business | 9.6% |
| Military | 9.2% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1520 to 1799, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
