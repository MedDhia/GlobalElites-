# Codebook

All files live in `data/processed/` and are comma-separated with a header row.
Association scores are base-2 logarithms, so +1 means "combined twice as often as
the reference model implies" and -1 means "half as often".

---

## Sector coding

The source database codes each person's occupational domain at three levels of
granularity. Level 2 is used here, and its 13 substantive categories are read as
sectors from which an individual drew authority, income or standing. The two
residual codes (`Other`, `Missing`) are dropped.

| Source value (level2) | Label used here |
|---|---|
| Politics | Politics |
| Administration/Law | Administration & Law |
| Military | Military |
| Religious | Religion |
| Nobility | Nobility |
| Family | Kinship |
| Corporate/Executive/Business (large) | Big business |
| Worker/Business (small) | Small business |
| Academia | Academia |
| Explorer/Inventor/Developer | Exploration & Invention |
| Culture-core | Culture (core) |
| Culture-periphery | Culture (periphery) |
| Sports/Games | Sport & Games |

`Kinship` covers people recorded chiefly through family position, `Culture (core)`
covers writers, composers, painters and the like, and `Culture (periphery)` covers
performers, journalists, designers and adjacent occupations.

---

## `elites_person_level.csv.gz`  (2,071,452 rows)

One row per person retained from the source database: a usable birth year and a
main sector among the 13 above.

| Column | Type | Description |
|---|---|---|
| `wikidata_code` | string | Wikidata identifier, the join column back to the source |
| `name` | string | Name as given in the source |
| `birth`, `death` | numeric | Year, negative for BCE; `death` may be missing |
| `gender` | string | As coded in the source |
| `region`, `subregion` | string | UN region and subregion of the area of attachment |
| `domain_level1` | string | Coarse domain: Culture, Leadership, Discovery/Science, Sports/Games |
| `sector_main` | string | Main sector, one of the 13 |
| `sector_second` | string | Second sector, or empty when the person is coded in one sector only |
| `occupation_level3` | string | Fine-grained occupation from the source |
| `freq_main_occ`, `freq_second_occ` | numeric | Share of the person's occupational mentions falling on each; the second never exceeds the first |
| `visibility` | numeric | Source composite visibility score (`sum_visib_ln_5criteria`) |
| `birth_century` | integer | Century of birth, floored (1543 becomes 1500) |
| `era` | string | Pre-1000, 1000-1399, 1400-1599, 1600-1799, 1800-1899, 1900-2020 |
| `diversified` | boolean | True when `sector_second` is present and differs from `sector_main` |

A `sector_second` equal to `sector_main` is set to missing: repeating a sector
carries no cross-sector information.

---

## `sector_pair_association_*.csv`

Four files with the same columns, differing only in the period they cut on:

| File | One row per |
|---|---|
| `sector_pair_association_overall.csv` | pair, pooled over the whole record (78 rows) |
| `sector_pair_association_by_era.csv` | pair x era (468 rows) |
| `sector_pair_association_by_century.csv` | pair x birth century, 800 to 1900 (936 rows) |
| `sector_pair_association_by_era_region.csv` | pair x era x UN region (1,248 rows) |

| Column | Description |
|---|---|
| `period_type`, `period` | Which cut the row belongs to and its value |
| `sector_a`, `sector_b`, `pair` | The unordered pair; `sector_a` precedes `sector_b` in the canonical sector order |
| `n_elites_period` | All elites in the period, diversified or not |
| `n_diversified_period` | Elites in the period spanning two sectors, the denominator of the model |
| `n_pair` | Elites combining exactly these two sectors |
| `expected_qi` | Expected count under quasi-independence |
| `assoc_log2` | **Headline statistic.** log2((n_pair + 0.5) / (expected_qi + 0.5)) |
| `assoc_ci_low`, `assoc_ci_high` | 95% percentile bootstrap interval, 2,000 draws |
| `assoc_boot_se` | Bootstrap standard deviation of the score |
| `p_value`, `q_value` | Two-sided bootstrap p-value and its Benjamini-Hochberg adjustment within period |
| `share_of_diversified` | n_pair / n_diversified_period |
| `log_or_uncond` and companions | Secondary statistic: log odds ratio of holding both sectors, computed over every elite of the period with a Haldane correction, Wald standard error, interval, p and q |
| `direction` | associated / dissociated / not distinguishable, at q < 0.05 |
| `era`, `region` | Present in the region file only |

Periods with fewer than 300 two-sector elites are not estimated. In the
region file a region also needs 3,000 elites in the era to appear.

---

## `sector_pair_trends.csv`  (78 rows)

Inverse-variance weighted regression of `assoc_log2` on birth century, over the
centuries 800 to 1900.

| Column | Description |
|---|---|
| `pair`, `sector_a`, `sector_b` | The pair |
| `n_centuries`, `first_century`, `last_century` | Centuries contributing to the fit |
| `assoc_first`, `assoc_last`, `assoc_mean` | Score in the first and last contributing century, and the weighted mean |
| `slope_per_century` | Change in the score per century |
| `slope_se`, `slope_ci_low`, `slope_ci_high` | Standard error and 95% interval |
| `p_value`, `q_value` | Two-sided t test and its Benjamini-Hochberg adjustment across the 78 pairs |
| `trend` | converging (slope > 0, q < 0.05), diverging (slope < 0, q < 0.05), flat otherwise |

---

## `sector_pair_summary.csv`  (78 rows, 32 columns)

Pooled score, per-era scores and counts, and the trend, joined into one wide row
per pair. Convenient starting point; nothing in it is not in the files above.

---

## `sector_marginals_by_period.csv`

One row per sector per period (eras and centuries stacked).

| Column | Description |
|---|---|
| `period_type`, `period`, `sector` | Identifiers |
| `n_main` | Elites whose main sector this is |
| `n_any_slot` | Elites holding the sector in either slot |
| `share_of_elites_main` | n_main over all elites of the period |
| `diversification_rate` | Among elites whose main sector this is, the share also coded in a second sector |

## `diversification_by_period.csv` and `diversification_by_region_period.csv`

Counts of elites and of two-sector elites by birth century, with their ratio,
overall and split by UN region.
