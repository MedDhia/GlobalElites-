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

---

# The network-structure layer

`scripts/09_network_structure.py` runs two analyses that the pairwise tables cannot
carry on their own. Outputs live in `data/processed/network_structure/`.

## Part A: positions and blocks

Two sectors occupy the same position when they combine with the same partners,
whether or not they combine with each other. Distance between two sectors is one
minus the correlation between their rows of the association matrix, with the two
sectors' own cells left out of the comparison; linkage is average.

### `sector_profile_correlations.csv`

One row per unordered node pair per period, for both layers.

| Column | Description |
|---|---|
| `layer` | `sector` (13 nodes) or `domain` (4 nodes) |
| `period` | `all` or one of the six eras |
| `node_a`, `node_b` | The pair |
| `profile_correlation` | Correlation between their association profiles |

### `sector_blocks_by_era.csv`

Block membership of every node in every period. Blocks are refitted inside each
period and matched to the pooled solution by best overlap (Hungarian assignment on
Jaccard), so a block name means the same position throughout. The number of blocks
is fixed at four, which is a choice: the silhouette curve is close to flat across
two to six blocks. The cut can return fewer than four; the 1900-2020 sector cut
returns three.

### `block_count_silhouette.csv` and `block_alternatives_pooled.csv`

The silhouette value for two to six blocks on the pooled matrix, and the membership
of the two- and six-block partitions, so the choice of four stays visible.

### `blockmodel_image_by_era.csv`

Mean association within and between blocks.

| Column | Description |
|---|---|
| `layer`, `period` | Identifiers |
| `block_a`, `block_b` | Row and column block |
| `n_cells` | Pairs contributing to the mean; the diagonal excludes self-pairs |
| `mean_assoc` | Mean `assoc_log2` over those pairs |

### `coreness_by_era.csv`

| Column | Description |
|---|---|
| `layer`, `period`, `node` | Identifiers |
| `coreness` | Leading eigenvector of the positive part of the association matrix, its best rank-one approximation, rescaled so the largest score is one |
| `cp_fit` | Correlation between the positive matrix and the outer product of the coreness vector: how well one core with a periphery around it describes that period at all |

Coreness reads as membership of the tightest positive cluster, not as importance.

### `network_indices_by_era.csv`

One row per layer per period.

| Column | Description |
|---|---|
| `n_nodes`, `n_pairs`, `n_crossings` | Size of the network and of the population behind it |
| `share_associated`, `share_dissociated`, `share_indistinguishable` | Composition of the matrix at BH q < 0.05 |
| `mean_abs_assoc`, `sd_assoc` | Size and spread of the scores |
| `degree_centralization` | Freeman centralization of the significant positive ties |
| `transitivity`, `modularity`, `n_communities` | Greedy modularity partition of the significant positive ties, weighted by the score |
| `core_periphery_fit` | As `cp_fit` above |

The domain layer has four nodes and six cells, so its centralization, transitivity,
modularity and core-periphery fit carry little information. Read `sd_assoc` and the
composition columns there and the rest on the sector layer.

## Part B: one level shift at an unknown date

The trend fits reported elsewhere are linear, and a linear trend cannot see a level
shift. Each pair is fitted with a common slope plus one shift at an unknown date:

```
assoc(t) = level_at_centre
         + slope_per_century * (t - centre) / 100
         + shift * 1{t > break_date}
```

Every admissible date is scanned (two cohorts are held out at each end) and the
largest Wald statistic on `shift` is the test statistic. Its null distribution is
simulated 2,000 times under a no-shift model, drawing each cohort with its own
bootstrap standard error inflated by the overdispersion the no-shift fit leaves
behind, so period-to-period variation beyond sampling error is carried into the
null instead of being assumed away.

### `breakpoints_sector_pairs.csv` and `breakpoints_domain_pairs.csv`

| Column | Description |
|---|---|
| `layer` | `sector centuries` (800-1900), `sector half-centuries` (1400-1949) or `domain half-centuries` (1400-1949) |
| `pair`, `n_points` | The pair and the cohorts behind the fit |
| `break_date` | Best-fitting date of the shift |
| `shift`, `shift_se`, `shift_ci_low`, `shift_ci_high` | Size of the shift and its Wald interval |
| `centre`, `level_at_centre`, `slope_per_century` | The rest of the shift model, enough to redraw the fitted line |
| `level_no_break`, `slope_no_break_per_century`, `rmse_no_break` | The no-shift model it is compared against |
| `sup_wald`, `p_value`, `q_value`, `has_break` | Test statistic, simulated p, BH-adjusted q within layer, and whether q < 0.05 |
| `overdispersion` | Scale inflation used in the null, never below 1 |

The sector layer is fitted on two grids. The century grid covers the whole record
but leans on pre-1100 cohorts of a few thousand people spread over 78 pairs; the
half-century grid runs over the same 1400 to 1949 window as the domain layer, where
the counts are large. The half-century rows are the comparable ones.

### `breakpoint_common_date.csv`

The pooled scan: at each candidate date, the Wald statistic summed over every pair
of that layer, asking whether one date fits the whole system.

| Column | Description |
|---|---|
| `layer`, `date` | Identifiers |
| `sum_wald` | Summed Wald statistic at that date |
| `is_best` | Whether this is the maximising date |
| `p_value_best` | On the maximising row only: simulated p for the pooled supremum, with every pair drawn under its own no-shift model |

---

# The country layer

`scripts/11_country_comparisons.py` repeats the domain and sector analyses inside
each country. Every score is fitted within the country, so it is net of that
country's own sector sizes and comparable with another country's. Outputs live in
`data/processed/countries/`.

Country comes from `citizenship_1_b` in the source, which maps historical polities
onto modern states. It is preferred over `area1_of_rattachment`, which keeps
separate codes for entities such as "Old (before year 1990 AD) Germany" and would
split a country's elites in two. Two consequences: the label is anachronistic for
anyone born before the state existed, and how many elites a country contributes
reflects which Wikipedia editions write about it as much as anything else.

Two panels are used:

| Panel | Threshold | Countries | Coverage |
|---|---|---|---|
| domain | 1,000 elites crossing two domains | 36 | 90% of all crossings |
| sector | 5,000 elites spanning two sectors | 24 | |

## `country_coverage.csv`  (233 rows)

One row per country, including those below the thresholds.

| Column | Description |
|---|---|
| `country` | Cross-verified citizenship, underscores replaced by spaces |
| `n_elites`, `n_classified` | Elites, and those holding at least one of the four domains |
| `n_crossings`, `n_sector_diversified` | Crossing two domains; spanning two of the 13 sectors |
| `crossing_rate`, `crossing_rate_ci_low/high` | Crossings over classified, with a 95% Wilson interval |
| `median_birth` | Median birth year, a rough guide to how modern a country's record is |
| `share_of_all_elites` | Share of everyone with a country |
| `in_domain_panel`, `in_sector_panel` | Whether the country clears each threshold |

## `country_crossing_by_era.csv`

Crossing rate per country per era, for eras with at least 200 classified elites,
with Wilson intervals.

## `country_domain_composition.csv`

| Column | Description |
|---|---|
| `country`, `domain` | Identifiers |
| `n_holders`, `share_of_classified` | Elites holding the domain in either slot. Shares sum above one because a crosser counts in two domains |
| `cross_domain_rate` | Of that domain's holders, the share also holding another |

## `country_domain_pairs.csv`  (216 rows) and `country_domain_pairs_by_era.csv`

The six crossings, per country and per country and modern era, with the same
columns as the other pair tables (`n_pair`, `expected_qi`, `assoc_log2`, bootstrap
interval, `p_value`, `q_value`, `direction`). The era file needs 400 crossings in
the country and era, and covers 1800-1899 and 1900-2020.

## `country_sector_pairs.csv`  (1,872 rows)

The 78 sector pairs for each of the 24 countries in the sector panel.

## `country_clusters.csv` and `country_cluster_profile.csv`

Countries grouped by Ward clustering on Euclidean distance between their six
crossing scores, into four groups named after their largest member. The profile
file gives each group's mean score on each crossing and its size.

| Group | Members |
|---|---|
| US group (12) | US, Italy, Canada, Brazil, Australia, Norway, Ireland, Portugal, Chile, Belgium, New Zealand, Lithuania |
| Germany group (16) | Germany, United Kingdom, France, Spain, India, Russia, Switzerland, Argentina, Mexico, Poland, Netherlands, Japan, Denmark, Israel, Hungary, Peru |
| Sweden group (3) | Sweden, Austria, Finland |
| China group (5) | China, Turkey, Iran, Greece, Romania |

---

# The shock event study

`scripts/13_shock_panel.py` builds a country by birth-cohort panel and codes the
shocks; `scripts/14_shock_event_study.py` runs the event study and its
falsification battery. Outputs live in `data/processed/shocks/`.

## Design

Staggered adoption with heterogeneous timing, so the estimator is a
Callaway-Sant'Anna style group-time average treatment effect. For countries first
exposed at cohort g and event time e, ATT(g, e) compares the change in the outcome
from the last pre-exposure cohort (e = -1) to cohort g + e, between those
countries and countries not yet exposed at that cohort plus those never exposed
inside the window. Within-country differences are weighted by the inverse of their
variance, which is the sum of the two cells' bootstrap variances. ATT(e)
aggregates over groups, weighted by treated cells.

Sixteen countries and four never-exposed ones is far too few clusters for
standard errors clustered on country, so inference is randomization inference: the
multiset of shock years is reassigned at random across the panel countries and the
whole estimator is recomputed 2,000 times. The reported p-value is the share of
draws whose |ATT(e)| reaches the observed one. This tests the sharp null of no
effect for any country.

**Exposure.** The panel is birth cohorts, not calendar years. A cohort born in
[b, b+25) has careers running roughly [b+25, b+90). A shock in year T is taken to
fall on the first cohort with b >= T - 50. The 30-year and 70-year alternatives
are written into `shock_list.csv`.

## `shock_panel_pairs.csv`  (912 rows)

Association scores for the six crossings, refitted inside every country and
25-year birth cohort with at least 120 elites crossing two domains, for the 16
countries with at least 6 such cohorts. Same columns as the other pair tables.

## `shock_panel_placebo.csv`

Per country and cohort: `n_classified`, `log_n_classified`, `crossing_rate`, and
the share of classified elites holding each of the four domains. These are the
placebo outcomes: quantities a change in who gets recorded would move.

## `shock_panel_coverage.csv`

Every country and cohort with `n_classified`, `n_crossings`, whether the cell
clears the 120-crossing floor (`usable`) and whether the country is in the panel.

## `shock_list.csv`  (12 rows)

The coded shocks. A shock enters only if it is dated to a single year, is a
rupture in who holds power and not a change of government inside a settled
order, and sits inside the window. Two types are coded separately because the
theoretical priors differ: *revolutionary rupture* (France 1789, Russia 1917,
Germany 1918, Austria 1918) and *state creation* (US 1776, Argentina 1816, Brazil
1822, Italy 1861, Canada 1867, Australia 1901, Norway 1905, New Zealand 1907).
Never exposed inside the window, and therefore usable as controls: Spain, Sweden,
Switzerland, the United Kingdom.

| Column | Description |
|---|---|
| `country`, `year`, `type`, `event` | The coded shock |
| `in_panel` | Whether the country is in the 16-country panel |
| `first_treated_cohort_main/short/long` | First exposed cohort under a 50, 30 or 70-year lag |
| `first_cohort`, `last_cohort`, `n_cohorts` | The country's usable cohorts |
| `n_pre_main`, `n_post_main` | Cohorts on each side of exposure |

## `event_study_att.csv`  (72 rows)

ATT(e) per shock type and crossing.

| Column | Description |
|---|---|
| `spec`, `shock_type`, `outcome`, `event_time` | Identifiers |
| `att` | The aggregated group-time estimate |
| `n_groups`, `n_treated_cells`, `min_controls` | What the estimate rests on |
| `p_value_ri` | Randomization p-value over 2,000 reassignments |
| `null_sd`, `null_ci_low`, `null_ci_high` | Spread and middle 95% of the null draws |

## `event_study_group_time.csv`

The underlying ATT(g, e), with the treated countries named, so any aggregate can
be traced to the comparisons behind it.

## `event_study_placebo.csv`, `event_study_placebo_time.csv`, `event_study_loo.csv`

The same estimator on the composition outcomes; on shocks shifted 100 years
earlier; and dropping one country at a time.

---

# The military revolution test

`scripts/16_military_revolution.py` tests the military revolution thesis against
the association between sectors of elite power; `scripts/17_military_revolution_figures.py`
draws it. Outputs live in `data/processed/military_revolution/`.

## Design

A period effect, so there are no untreated units in time. The control group is
internal: the 71 sector pairs the thesis says nothing about. That controls for
anything moving all pairs together, coverage change included, but not for anything
moving military pairs for a non-military reason. This is an interrupted time series
with within-sample controls, not an identified experiment.

**Exposure.** A cohort born in year b has its main career in [b+25, b+65]. Against
Roberts' 1560-1660 dating a cohort is PRE if that career closes before the window
opens (cohorts to 1475), POST if it opens after the window closes (cohorts from
1650), TRANSITION otherwise (1500 to 1625). Transition cohorts are held out of the
contrast, not assigned to a side.

**Predictions** are written into the script before the series was computed, each
with the claim and its source. Six carry a signed direction; Military + Nobility is
recorded as contested and excluded from the sign test, because professionalisation
implies loosening (Roberts) while absorption of the nobility into the officer corps
implies tightening (Downing, Ertman).

## `predictions.csv`  (6 rows)

`pair`, `direction` (+1 or -1), `claim`, `source`.

## `europe_sector_pairs_by_cohort.csv`

The series everything rests on: the 78 sector-pair association scores refitted
inside each 25-year European birth cohort from 1350 to 1825, with the usual
columns plus `phase` (pre / transition / post).

## `prepost_contrast.csv`  (78 rows)

Each pair's PRE to POST change.

| Column | Description |
|---|---|
| `pair`, `change`, `change_se` | The change in log2(observed/expected) and its standard error |
| `change_long_post` | The same with the post window extended to 1825 |
| `n_pre_cohorts`, `n_post_cohorts` | Cohorts behind each side |
| `predicted`, `contested`, `direction`, `claim`, `source` | Whether the thesis speaks to this pair |
| `signed_change`, `rank_of_change`, `z` | Change in the predicted direction, rank among all 78, and change over its standard error |

## `test_summary.csv`  (4 rows)

T1 and T2 for the real window, the long-post sensitivity, and two placebo windows
moved 100 years each way. A wider shift leaves no cohorts on one side.

| Column | Description |
|---|---|
| `window`, `pre_cohorts`, `post_cohorts` | Which contrast |
| `n_predictions`, `n_correct_sign`, `p_sign_test` | T1 |
| `mean_signed_change`, `p_permutation` | T2, against 100,000 random six-pair sets drawn from the 78 changes with random signs |

## `breaks_predicted_pairs.csv`  (7 rows)

T3. One level shift at an unknown cohort, fitted per predicted pair with the
machinery in `scripts/breaks.py`. `in_window` is whether the dated cohort falls
between 1495 and 1635, the cohorts exposed to 1560-1660. The model finds the single
largest step, so a series that rises early and falls later is dated by the fall;
read it as "no predicted pair has its dominant step inside the window", not as
"nothing happened inside the window".

## `military_centrality_by_cohort.csv`

T6. Per cohort: the military sector's mean and maximum association with the other
twelve, its coreness among the positive ties, the number of positive ties in the
network, and the core-periphery fit.

## `composition_placebo.csv` and `europe_composition_by_cohort.csv`

T5. The share of European elites in each sector, the diversification rate and the
log elite count, per cohort and contrasted PRE to POST.

## `bloc_did.csv` and `bloc_sector_pairs_by_cohort.csv`

T7. High military pressure is France, Germany, Spain, Austria and Russia; low is
the United Kingdom, the Netherlands, Switzerland and Sweden, following Downing's
contrast between military-bureaucratic absolutism and constitutional survival. The
contrast is run inside each bloc on 50-year cohorts and differenced. Two blocs is
two clusters, so `p_permutation` comes from reassigning which countries sit in
which bloc, 300 draws.

---

# The fiscal-military state test

`scripts/18_fiscal_military_state.py` tests Brewer's "Sinews of Power" thesis;
`scripts/19_fiscal_military_figures.py` draws it. Outputs live in
`data/processed/fiscal_military/`.

## Why this thesis is testable where the military revolution was not

Brewer's claim is country-specific, dated, and names its counterfactual, so there
is a treated unit (Britain), a window (1688-1783) and a donor pool. The military
revolution is a Europe-wide period with no untreated units, which is why that test
had to lean on within-sample pair controls alone.

## Design

One treated unit with a long pre-period points at the synthetic control family.
Four donors and five pre-cohorts is too few for a synthetic control to mean
anything, since the pre-period fit would be mechanical, so the estimator is a plain
difference in differences with two placebo distributions:

- **in space**: each donor is treated in turn and Britain is ranked among the five.
  With four donors the smallest p this can return is 0.20, which is a limit of the
  panel and is reported as one.
- **in pairs**: Britain's effect on the six predicted pairs is ranked against its
  effect on the fifteen the thesis says nothing about.

**Coarsening.** Sectors are collapsed to seven groups so a country-cohort cell has
enough cases: Politics; Administration & Law; Military; Business (big and small);
Nobility & Kinship; Religion; Learning & Culture (academia, exploration and
invention, both culture sectors). Sport & Games is dropped as negligible before
1800. The coarsening preserves what is particular to the thesis: politics and
administration stay apart because their fusion is the claim, and business stays
apart because public credit is what separates Brewer from the military revolution.

**Phases.** A cohort born in b works in [b+25, b+65]. PRE is a career closed before
1688 (cohorts to 1600), EXPOSED is a career falling entirely inside 1688-1783
(cohorts 1675 and 1700), POST is a career opening after 1783 (cohorts from 1775).
Everything else is transition and is held out.

**Panel.** Britain plus France, Germany, Spain and Italy, being the units with at
least three PRE cohorts, both EXPOSED cohorts and the POST cohorts above the
120-pair floor.

## `predictions.csv`  (6 rows)

`pair`, `direction`, `claim`, `source`. Politics + Nobility & Kinship is recorded
in the script as contested and excluded, because Brewer has the apparatus growing
underneath an aristocratic political order.

## `country_pairs_by_cohort.csv`

The 21 group-pair association scores refitted inside each country and 25-year
cohort, with the usual columns plus `country`, `cohort` and `phase`.

## `phase_contrasts.csv`

Each unit's PRE to EXPOSED change per pair, and its EXPOSED to POST change.

## `did_results.csv`  (21 rows)

| Column | Description |
|---|---|
| `pair` | The group pair |
| `treated_change`, `donor_mean_change`, `n_donors` | Britain and the donor pool |
| `did`, `signed_did` | Britain minus the pool, and that in the predicted direction |
| `direction`, `claim`, `source`, `is_predicted`, `is_contested` | Whether the thesis speaks to this pair |

## `placebo_in_space.csv`, `placebo_in_pairs.csv`, `placebo_in_time.csv`

Each unit treated in turn with its rank and `p_in_space`; the permutation over
pairs; and the time placebo, which is recorded as **not estimable** with the reason
in a `note` column, since a window 200 years earlier needs British cohorts born
before 1423 and none clears the floor.

## `britain_vs_france.csv` and `persistence.csv`

The head-to-head Brewer actually draws, and the EXPOSED to POST change.

## `composition_placebo.csv`

Each unit's group shares and elite count by phase, so the change in the recorded
population can be read next to the change in the association scores.

---

# The Tilly path test

`scripts/20_tilly_paths.py` tests Tilly's coercion and capital paths;
`scripts/21_tilly_figures.py` draws it. Outputs live in `data/processed/tilly/`.

## Design

Tilly's claim is typological and cross-sectional, so there is no dating problem and
no exposure lag. What it predicts is an ordering of countries, which is what this
repository measures country by country.

Nothing here identifies a causal effect. Countries do not receive their endowment
of cities and capital at random; that endowment is Tilly's explanatory variable and
it is inherited from centuries of geography and trade. What can be tested is
whether the ordering he predicts is the ordering the record shows, against a null
in which the path labels are shuffled across countries.

Sectors use the same seven groups as the fiscal-military test. Association scores
are refitted inside each country and era, with a 150-pair floor. The main era is
1600-1799, where the panel is balanced at five countries per path. Ordering is
tested with a Jonckheere-Terpstra statistic against a permutation null over the
path labels, 100,000 draws, which is the right null at five countries per cell.

## `path_coding.csv`  (17 rows)

Tilly's own examples mapped onto the modern states the source codes, with the
alternative coding alongside. The mapping is lossy and the lossiest case is Italy,
which merges Venice and Genoa with the papal and southern states. The alternative
coding moves the three cases Tilly is least explicit about: Denmark to
capital-intensive, Sweden to capitalized coercion, Germany to coercion-intensive.

## `predictions.csv`  (5 rows)

`quantity`, `predicted_order` running from the path predicted lowest to the path
predicted highest, and `claim`. Four pair predictions plus a composite, the
coercion index, defined as the association of politics with the military minus the
association of politics with business.

## `country_era_pairs.csv`

The 21 group-pair association scores refitted inside each country and era.

## `ordering_tests.csv`  (20 rows)

| Column | Description |
|---|---|
| `coding`, `era`, `quantity`, `predicted_order`, `claim` | Identifiers |
| `jt`, `jt_null_mean` | Jonckheere-Terpstra statistic and its permutation mean |
| `p_permutation` | Share of 100,000 label shuffles reaching the observed statistic |
| `q_within_era`, `q_all_tests` | Benjamini-Hochberg over the five tests in the era, and over all twenty. The pre-specification names 1600-1799 as the main era, so the era family is the intended one |
| `n_countries`, `monotone_as_predicted` | Countries in the test, and whether the three path means run in the predicted order |
| `mean_<path>` | Each path's mean |

## `group_means.csv`, `coercion_index.csv`

Each path's mean per quantity and era; and the composite index country by country.

## `leave_one_out.csv`, `alternative_coding.csv`

The composite test dropping each country in turn; and every test rerun under the
alternative coding.

## `manipulation_check.csv`

Whether the coded paths separate countries on the raw mix of elites, measured as
the military share minus the business share. This is not independent of the
outcome data and is not offered as validation of the thesis; it checks that the
coding is not arbitrary, so that a null on the association scores can be read as a
null about association and not about the coding.

---

# Revolutionary cohorts

`scripts/22_revolution_cohorts.py` builds them. Outputs live in
`data/processed/revolutions/`, one subfolder per revolution.

## Membership

A person is in a revolution's cohort when their coded country is one of the
countries where the political order was at stake, they were at least 20 years old
at some point inside the window, and they were alive when the window opened.
Death is missing for more than half the source rows, so a missing death year is
imputed as birth plus 80 for the alive test only; `death_imputed` marks every row
where that was used. The imputation is generous, so the cohorts are upper bounds
on membership.

Countries are scoped to the states whose own order was in question, not every
state that took an interest: France is not in the Haitian cohort and the United
Kingdom is not in the Irish cohort. Country is coded as present-day citizenship,
the only country field the database carries, so the mapping is anachronistic by
construction. Germany stands for the German states, Italy for the Italian ones,
and the successor republics stand for the territory of the Russian empire.

A revolution is kept when its cohort holds at least 500 elites and at least 200
who span two sectors, the floor the pair estimator needs. Sixteen of the
seventeen considered are kept; the Haitian Revolution is not, at 39 elites.

Sectors use the same seven groups as the fiscal-military and Tilly tests.
Association scores are refitted inside each cohort, which makes cohorts of very
different size comparable in a way the raw counts are not.

These are descriptive cohorts, not treatment groups. Cohorts overlap where
windows are close in the same countries, and coverage of the database rises
steeply with time.

## `revolutions_index.csv`  (17 rows)

| Column | Description |
|---|---|
| `revolution`, `slug` | Name and the folder that holds it |
| `window_start`, `window_end` | The conventional dates used |
| `countries`, `n_countries` | The states whose political order was at stake |
| `n_elites`, `n_two_sector` | Cohort size, and how many span two sectors |
| `kept`, `reason` | Whether the cohort clears the floor, and why not when it does not |

## `cohort_summary.csv`  (16 rows)

One row per kept revolution: the index columns plus `n_two_group`,
`share_two_sector`, `n_death_imputed` and `share_death_imputed`, `birth_min` and
`birth_max`, `median_age_at_start`, `share_women`, `median_visibility`, the four
age-band counts (`n_under_20`, `n_20-35`, `n_36-55`, `n_56plus`) and
`top_countries`.

## `cohort_composition.csv`, `cohort_group_pairs.csv`

Every cohort's `sector_composition.csv` and `group_pairs.csv` stacked, for
cross-revolution comparison.

## `<slug>/elites.csv.gz`

The cohort person by person. The person-level columns documented above, plus:

| Column | Description |
|---|---|
| `death_imputed` | True where the death year was missing and birth plus 80 was used for the alive test |
| `group_main`, `group_second` | The seven-group coarsening of the two sectors |
| `revolution`, `revolution_slug` | Which cohort this row belongs to |
| `window_start`, `window_end` | The revolution's dates |
| `age_at_start`, `age_at_end` | Age when the window opened and closed, negative before birth |
| `age_at_midpoint` | Age at the midpoint of the window, rounded |
| `age_band` | `under 20`, `20-35`, `36-55` or `56+`, banded on `age_at_midpoint`. `under 20` are those who reached adulthood inside the window |

## `<slug>/summary.csv`

The one row for this revolution from `cohort_summary.csv`.

## `<slug>/sector_composition.csv`

| Column | Description |
|---|---|
| `revolution`, `category`, `level` | `level` is `sector` for the 13 sectors and `group` for the 7 groups |
| `n_holding`, `share_holding` | Cohort members holding the category in either slot |
| `n_primary`, `share_primary` | Cohort members whose primary sector it is |

## `<slug>/group_pairs.csv`

The 21 group-pair association scores fitted inside the cohort. Columns are those
of `sector_pair_association_*.csv` documented above, with `cat_a`/`cat_b` renamed
`group_a`/`group_b` and `period` renamed `slug`.

## `<slug>/group_pairs_by_age_band.csv`

The same, refitted inside each age band, where the band clears a 100-pair floor.
`age_band` names the band.

## `<slug>/birth_cohort_pairs.csv`

The same countries by 40-year birth cohort, from 120 years before the window to
120 years after, as context either side. `birth_cohort_start` and
`birth_cohort_end` bound the block and `overlaps_window` marks the blocks that
contribute members to the revolutionary cohort. Blocks below the 100-pair floor
are absent, so the series is not balanced across revolutions.

## Figures

`scripts/23_revolution_figures.py` draws six and
`scripts/24_revolution_field_figures.py` four more, all from the tables above.

| Figure | What it shows |
|---|---|
| `figV01_cohorts` | The sixteen cohorts in time, their size and their age composition |
| `figV02_pair_heatmap` | Every group pair by every cohort, ordered by date and by mean association |
| `figV03_what_repeats` | Each pair's spread across cohorts, with the associated / dissociated / not distinguishable counts |
| `figV04_politics_business` | Politics with business cohort by cohort, and against politics with the military |
| `figV05_age_bands` | The four politics pairs refitted inside each age band |
| `figV06_birth_cohorts` | The four politics pairs by 40-year birth cohort, with the revolutionary window marked |
| `figW01_pooled_field_graph` | The pooled shape as a graph, split into what was held together and what was held apart |
| `figW02_field_graphs_by_revolution` | The same graph inside each cohort, keeping the ties it can separate from chance |
| `figW03_space_of_power` | The seven fields placed by classical scaling of the association matrix, and how far each moves between cohorts |
| `figW04_rank_ribbons` | Each tie's position in the cohort's own ordering, across the sixteen |
