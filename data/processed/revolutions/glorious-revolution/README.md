# Glorious Revolution, 1688-1689

The deposition of James II and the settlement that followed, which opened the fiscal-military state tested in scripts/18.

Countries whose political order was at stake: United Kingdom, Ireland.

## The cohort

3,126 elites, of whom 1,837 (59%) span two sectors. Birth years 1598 to 1669; median age when the window opened, 42. Death year is imputed as birth plus 80 for 3% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 0 |
| 20-35 | 1,078 |
| 36-55 | 1,126 |
| 56+ | 922 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Politics | 48.4% |
| Learning & Culture | 31.3% |
| Nobility & Kinship | 23.1% |
| Religion | 16.5% |
| Administration & Law | 11.9% |
| Business | 11.1% |
| Military | 9.1% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1560 to 1839, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
