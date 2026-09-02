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

---

# The four-domain layer

The 13 sectors are collapsed onto four domains of power. Three sectors are left
unclassified because they name a mode of transmission or a form of celebrity
instead of a domain: Nobility, Kinship and Sport & Games.

| Domain | Label in the files | Sectors |
|---|---|---|
| Political / regulatory | `Political` | Politics, Administration & Law |
| Ideational / academic | `Ideational` | Religion, Academia, Culture (core), Culture (periphery) |
| Economic / allocative | `Economic` | Big business, Small business, Exploration & Invention |
| Security / military | `Security` | Military |

Collapsing changes what diversification means. An elite coded Politics plus
Administration & Law spans two sectors but one domain: consolidation inside the
political domain, not a second source of power. Only an elite whose two sectors
fall in two different domains **crosses** a domain boundary, and the association
model is fitted to those crossings.

Of 2,071,452 people, 1,485,223 (71.7%) hold at least one of the four domains and
280,761 cross two of them.

---

## `elites_domain_person_level.csv.gz`  (2,071,452 rows)

The person-level file with the domain recode attached.

| Column | Description |
|---|---|
| `wikidata_code`, `name`, `birth`, `death`, `gender`, `region`, `subregion` | As in the sector file |
| `sector_main`, `sector_second` | The 13-sector coding this layer is built from |
| `domain_main`, `domain_second` | Domain of each slot; empty when the sector is unclassified |
| `n_domains` | 0, 1 or 2 distinct domains held |
| `crosses_domains` | True when `n_domains` == 2 |
| `portfolio` | "Political only", "Political + Security", ..., or "Unclassified" |
| `sector_span` | How the two coded sectors relate once collapsed: one sector / two sectors, one domain / two sectors, two domains / two sectors, one classified / two sectors, none classified |
| `birth_century`, `birth_halfcentury`, `era` | Cohort identifiers |

Counts of `sector_span` over the whole file:

| Value | n |
|---|---|
| one sector | 1,348,192 |
| two sectors, one domain | 287,986 |
| two sectors, two domains | 280,761 |
| two sectors, one classified | 132,633 |
| two sectors, none classified | 21,880 |

---

## `domain_pair_association_*.csv`

Same columns as the sector files, with `domain_a` and `domain_b` in place of
`sector_a` and `sector_b`, and `n_diversified_period` counting crossings.

| File | Rows | Periods |
|---|---|---|
| `domain_pair_association_overall.csv` | 6 | pooled |
| `domain_pair_association_by_era.csv` | 36 | 6 eras |
| `domain_pair_association_by_century.csv` | 54 | 9 centuries, 1100 to 1900 |
| `domain_pair_association_by_halfcentury.csv` | 66 | 11 half-centuries, 1400 to 1949 |
| `domain_pair_association_by_era_region.csv` | 96 | era x UN region |

A period needs 150 crossings to be estimated, which is why the century series
starts at 1100 and the half-century series at 1400. The half-century grid gives
the modern period the resolution the counts there can support.

Because the model is refitted on four categories, `expected_qi` is not comparable
across the two layers; the association scores are.

## `domain_pair_trends.csv`  (12 rows)

Two rows per pair: one fitted on the century grid, one on the half-century grid.

| Column | Description |
|---|---|
| `grid` | `century` or `halfcentury` |
| `pair`, `domain_a`, `domain_b` | The pair |
| `n_points`, `first_period`, `last_period` | Cohorts contributing to the fit |
| `assoc_first`, `assoc_last`, `assoc_mean` | First, last and weighted mean score |
| `slope_per_century` and companions | Inverse-variance weighted slope, standard error, 95% interval, p, and BH q computed within grid |
| `trend` | converging / diverging / flat |

## `domain_pair_summary.csv`  (6 rows)

Pooled score, per-era scores and counts, and the half-century trend, one wide row
per pair.

## `domain_marginals_by_period.csv`

| Column | Description |
|---|---|
| `period_type`, `period`, `domain` | Identifiers; period types are `era`, `century` and `all` |
| `n_holders` | Elites holding the domain in either slot |
| `share_of_classified` | n_holders over elites with at least one domain. These sum to more than 1 because crossers are counted in two domains |
| `cross_domain_rate` | Among the domain's holders, the share who also hold another domain |

## `domain_portfolio_by_period.csv`

One row per portfolio per period: `n`, `share_of_classified`, and `kind`
(single domain / cross-domain).

## `domain_reach_by_period.csv`

Directional. One row per ordered domain pair per period.

| Column | Description |
|---|---|
| `from_domain`, `to_domain` | Ordered pair |
| `n_from` | Elites holding `from_domain` |
| `n_both` | Of those, how many also hold `to_domain` |
| `reach` | n_both / n_from |

Reach is unnormalised, so a large domain draws high reach from everywhere. Read
it next to the association matrices, which remove that size effect.

## `crossing_by_period.csv`, `crossing_by_region_period.csv`

Elites with at least one domain, how many of them cross two, and the ratio, by
birth century and by birth century and UN region.

## `consolidation_by_period.csv`

Among two-sector elites whose sectors are both classified: how many stayed inside
one domain (`n_within_domain`) against how many crossed (`n_cross_domain`), with
`share_within_domain`, by birth century.

---

# The culture-placement robustness run

`scripts/07_robustness_culture.py` reruns the whole domain analysis under five
readings of where cultural production belongs, holding the estimator and every
other choice constant. The mappings live in `scripts/domainmap.py`.

| Spec | Ideational domain contains | Domains | Other change |
|---|---|---|---|
| `main` | Religion, Academia, Culture (core), Culture (periphery) | 4 | none |
| `culture_out` | Religion, Academia | 4 | both Culture sectors unclassified |
| `culture_own` | Religion, Academia | 5 | both Culture sectors form a `Cultural` domain |
| `culture_core_only` | Religion, Academia, Culture (core) | 4 | Culture (periphery) unclassified |
| `invention_ideational` | Religion, Academia, both Culture sectors, Exploration & Invention | 4 | Exploration & Invention leaves the economic domain |

Outputs live in `data/processed/robustness/`.

## `<spec>_pair_association_overall.csv`, `_by_era.csv`, `_by_halfcentury.csv`

Identical in structure to the domain files, one set per specification. Under
`culture_own` there are 10 pairs instead of 6, and `Cultural` appears in
`domain_a` and `domain_b`.

## `<spec>_crossing_by_period.csv`

Elites with at least one domain, how many cross two, and the ratio, by birth
century, computed under that specification.

## `<spec>_pair_trends.csv`

Inverse-variance weighted slope of the association score on the half-century
grid, 1400 to 1949, with BH q computed within the specification.

## `robustness_universe.csv`  (5 rows)

How each reading changes what is being measured.

| Column | Description |
|---|---|
| `spec`, `label`, `note` | Identifier and prose description |
| `n_domains_in_spec`, `sectors_classified` | Size of the scheme |
| `n_persons`, `n_classified`, `share_classified` | Universe |
| `n_crossing`, `crossing_share_of_classified` | Elites crossing a domain boundary |
| `n_two_sectors_one_domain` | Elites whose two sectors collapse to one domain |
| `n_pairs` | 6 for a four-domain reading, 10 for the five-domain one |

## `robustness_pair_comparison.csv`  (34 rows)

Every pair under every reading, pooled over the whole record: `spec`,
`spec_short`, `spec_label`, `pair`, `is_core_pair` (whether the pair is one of the
six that exist in all five readings), and the usual association columns.

## `robustness_core_by_era.csv`  (180 rows)

The six core pairs under every reading, by era.

Scores are comparable **within** a reading, not across readings with different
numbers of domains. Under `culture_own` the observed count for
Ideational + Economic is 34,182, exactly as under `culture_out`, yet the score is
-0.41 against +0.28: nothing about those elites changed, only the reference model
they are measured against, which now has ten cells to distribute expectations over
instead of six.
