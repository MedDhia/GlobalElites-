# Meiji Restoration, 1868-1869

The overthrow of the shogunate and the dismantling of the samurai order.

Countries whose political order was at stake: Japan.

## The cohort

518 elites, of whom 344 (66%) span two sectors. Birth years 1781 to 1849; median age when the window opened, 32. Death year is imputed as birth plus 80 for 1% of them, for the alive test only.

| Age at the midpoint | Elites |
|---|---:|
| under 20 | 0 |
| 20-35 | 313 |
| 36-55 | 156 |
| 56+ | 49 |

## What they held

Share of the cohort holding each group of sectors, counting both the primary and the secondary sector.

| Group | Share |
|---|---:|
| Military | 38.2% |
| Learning & Culture | 34.4% |
| Nobility & Kinship | 33.2% |
| Politics | 24.3% |
| Business | 11.4% |
| Administration & Law | 7.9% |
| Religion | 3.1% |

## Files

| File | Contents |
|---|---|
| `elites.csv.gz` | the cohort, person by person, with ages |
| `summary.csv` | the counts above in one row |
| `sector_composition.csv` | shares at both the 13-sector and the 7-group level |
| `group_pairs.csv` | the 21 group-pair association scores inside the cohort |
| `group_pairs_by_age_band.csv` | the same, split by age at the window midpoint, where a band clears the floor |
| `birth_cohort_pairs.csv` | the same countries by 40-year birth cohort, 1800 to 1999, as context either side of the window |

Association is `assoc_log2`, the log2 ratio of the observed count of elites holding both groups to the count expected under quasi-independence fitted inside this cohort. Positive is association, negative is dissociation. `scripts/assoc_core.py` holds the estimator and `docs/CODEBOOK.md` documents every column.

These are descriptive cohorts, not treatment groups. Living through a revolution is not an assignment.
