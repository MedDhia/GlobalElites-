# Sectors of elite power: association and dissociation, 3500 BCE to 2020 CE

Which sources of power do historical elites combine, which do they keep apart,
and how have those pairings shifted over a millennium?

This repository stages the BHHT cross-verified database of notable people, reduces
it to a person-by-sector file, measures the association between every pair of
power sectors within birth cohorts, and produces the figures and derived datasets
that follow from it.

The analysis runs at two levels of aggregation, both from the same person-level
file and the same estimator:

- **13 sectors**, 78 pairs. Fine enough to see the church, the academy, the
  officer corps and the counting house separately. Files and figures with no
  prefix.
- **4 domains of power** (political/regulatory, ideational/academic,
  economic/allocative, security/military), 6 pairs. Files prefixed `domain_`,
  figures prefixed `figD`.

The domain layer rests on a reading of where each sector belongs, so it is rerun
under five such readings in `data/processed/robustness/`, figures prefixed `figR`.

On top of both layers sits a network-structure pass in
`data/processed/network_structure/`, figures prefixed `figS`: positions and blocks,
whole-network indices, and a scan for level shifts that a linear trend cannot see.

Both layers are then refitted inside each country in `data/processed/countries/`,
figures prefixed `figC`. A pass in `data/processed/shocks/`, figures prefixed `figE`, asks whether dated
country-level shocks leave a persistent mark. The answer is that this data cannot
say, and the section below shows why. A last pass in
`data/processed/military_revolution/`, figures prefixed `figM`, tests one named
thesis that does make datable, directional predictions about these sectors.

Read together they answer a question neither answers alone: how much of the
movement in elite career combinations is reorganisation *inside* a domain of
power, and how much is a change in which domains get combined at all.

---

## The data

Laouenan, M., Bhargava, P., Eymeoud, J.-B., Gergaud, O., Plique, G. and Wasmer, E.
(2022), "A cross-verified database of notable people, 3500BC-2018AD",
*Scientific Data* 9, 290. <https://doi.org/10.1038/s41597-022-01369-4>

The authors describe their population as an elite of roughly one in 43,000 human
beings who have ever lived: 2.29 million individuals reconstructed from Wikipedia
editions and Wikidata, deduplicated and cross-verified, with birth and death dates,
gender, geography, visibility measures, and an occupational taxonomy at three
levels of granularity. Distributed through the Sciences Po Dataverse under
`doi:10.21410/7E4/RDAG3O`.

The archive is 250 MB, so it is not versioned here. `scripts/00_download_data.py`
fetches it into `data/raw/`, which is git-ignored. Everything downstream is
committed.

## What counts as a sector

The source codes a *main* and, for many people, a *second* occupational domain.
Read substantively, those two domains are the sectors an individual drew authority,
income or standing from. The 13 substantive level-2 domains are used as the sectors:

> Politics · Administration & Law · Military · Religion · Nobility · Kinship ·
> Big business · Small business · Academia · Exploration & Invention ·
> Culture (core) · Culture (periphery) · Sport & Games

Of the 2,071,452 people retained, 723,260 (34.9%) are coded in two distinct
sectors. Each of them is one edge in a network whose nodes are sectors, and that
network is what the analysis describes.

## How association is measured

The reference model is **quasi-independence** on the symmetric sector-by-sector
table, fitted by iterative proportional fitting so that every sector's total is
reproduced exactly, with the diagonal excluded by design. The headline statistic
per pair and period is

```
assoc = log2( observed / expected )
```

so +1 means a pair is combined twice as often as the marginals imply, and -1 half
as often. Intervals come from a parametric bootstrap over the pair counts with
2,000 draws, refitting the model in each; p-values are Benjamini-Hochberg adjusted
within each period.

The reason for quasi-independence over a plain 2x2 odds ratio: every two-sector
elite occupies exactly two slots, so the sector indicators are negatively dependent
by construction. Plain independence would read that arithmetic as elite behaviour.
The odds ratio is still reported alongside, as `log_or_uncond`, for readers who
want the unconditional quantity.

## The four domains

The 13 sectors collapse onto four domains. Three sectors are left unclassified
because they name a mode of transmission or a form of celebrity instead of a
domain of power.

| Domain | Sectors |
|---|---|
| Political / regulatory | Politics, Administration & Law |
| Ideational / academic | Religion, Academia, Culture (core), Culture (periphery) |
| Economic / allocative | Big business, Small business, Exploration & Invention |
| Security / military | Military |
| *unclassified* | *Nobility, Kinship, Sport & Games* |

Collapsing changes what diversification means. An elite coded Politics plus
Administration & Law spans two sectors but one domain: consolidation inside the
political domain, not a second source of power. Only an elite whose two sectors
fall in two different domains **crosses** a boundary, and the model is fitted to
those crossings. Of 2,071,452 people, 1,485,223 (71.7%) hold at least one of the
four domains and 280,761 cross two of them.

## What the figures show

| Figure | Content |
|---|---|
| `fig01_association_matrix_overall` | The 13 x 13 association matrix pooled over the whole record |
| `fig02_association_matrix_by_era` | The same matrix refitted within six birth-cohort eras |
| `fig03_pair_trajectories` | Century-by-century paths of the six pairs that pulled apart most and the six that came together most |
| `fig04_sector_networks_by_era` | Sectors as a network, era by era, with associations as edges |
| `fig05_diversification_rates` | How often elites drew on a second sector at all: overall, by region, by sector |
| `fig06_ranked_pairs` | The 20 tightest and the 20 most avoided combinations, with intervals |
| `fig07_pair_trend_slopes` | All 78 pairs ranked by how their association moved, 800 to 1900 |
| `fig08_sector_composition` | What the recorded elite is made of, century by century |
| `fig09_destination_profiles` | For each sector, where its diversifiers actually went |
| `fig10_regional_variation` | The same pair across continents in the two modern eras |

And for the four domains:

| Figure | Content |
|---|---|
| `figD01_domain_association_overall` | The 4 x 4 matrix and the six crossings ranked, pooled |
| `figD02_crossing_trajectories` | Each crossing across half-century cohorts, 1400 to 1949 |
| `figD03_domain_matrix_by_era` | The 4 x 4 matrix refitted in each of six eras |
| `figD04_domain_networks_by_era` | The four domains as a network, era by era, with scores on the edges |
| `figD05_crossing_rates` | Crossing against within-domain consolidation, by region, and by domain |
| `figD06_domain_reach_by_era` | Of the elites holding one domain, what share also hold each other |
| `figD07_portfolio_composition` | Portfolios of power, century by century |
| `figD08_regional_variation` | The same crossing across continents in the two modern eras |

And for the robustness run:

| Figure | Content |
|---|---|
| `figR01_culture_robustness` | The six crossings under all five readings, with what each reading leaves in |
| `figR02_five_domain_pooled` | The five-domain matrix and its ten crossings, pooled |
| `figR03_five_domain_by_era` | The five-domain matrix refitted in each of six eras |
| `figR04_core_pairs_across_readings` | Each core crossing over time, one line per reading |

And for the network-structure pass:

| Figure | Content |
|---|---|
| `figS01_positions_and_blocks` | Dendrogram of sectors by association profile, and the matrix reordered by block |
| `figS02_blocks_over_time` | Which block each sector sits in era by era, and the blockmodel image |
| `figS03_network_indices` | Composition, spread, centralization, transitivity, modularity, core-periphery fit |
| `figS04_coreness` | Who sits at the centre of the positive ties, era by era |
| `figS05_break_scan` | The pooled scan for a common date, and where each pair puts its own shift |
| `figS06_domain_steps` | The six domain crossings with the fitted step model overlaid |

And for the country comparisons:

| Figure | Content |
|---|---|
| `figC01_country_coverage` | What each country contributes, and how often its elites cross a boundary |
| `figC02_country_composition` | What each country's elite is made of, and how far each domain reaches |
| `figC03_country_crossing_matrix` | The six crossings for all 36 countries, grouped by profile |
| `figC04_country_map` | Countries placed on rule-with-coercion against rule-with-money, and on the two axes where they differ most |
| `figC05_crossings_ranked` | Every crossing, every country, ranked with intervals |
| `figC06_country_sector_pairs` | The sector pairs on which countries differ most |
| `figC07_country_change` | An arrow per country from the nineteenth-century cohort to the twentieth |

And for the shock event study:

| Figure | Content |
|---|---|
| `figE01_shock_panel` | What the panel contains, and where each shock falls in it |
| `figE02_event_study` | ATT by event time against the randomization null, for both shock types and all six crossings |
| `figE03_falsification` | Pre-trends, composition placebos, and shocks moved 100 years earlier |
| `figE04_rupture_trajectories` | The four rupture cases against the four never-exposed countries |

And for the military revolution test:

| Figure | Content |
|---|---|
| `figM01_predictions` | All 78 pairs' before-and-after change, with the six predicted ones marked |
| `figM02_predicted_trajectories` | Each predicted pair cohort by cohort, with the exposed cohorts shaded |
| `figM03_timing` | Where each shift dates, and the military sector's position in the network |
| `figM04_placebo_and_intensity` | Placebo windows, and high against low military pressure |

Every figure is written as both PDF and 300-dpi PNG.

## What comes out of it

**Three couplings dominate the whole record.** Nobility with kinship
(log2 = +2.91, n = 12,889), military with nobility (+1.80, n = 7,460), and politics
with administration and law (+1.74, n = 61,160). Two of the three are the classic
description of a hereditary ruling stratum; the third is the administrative state.

**The hereditary coupling tightens instead of fading.** Nobility with kinship runs
at +0.61 for elites born 1000 to 1399, +1.76 for those born 1600 to 1799, and +2.36
for those born after 1900. As titled elites shrink to a smaller share of the
recorded population, the ones who remain are recorded through family position far
more distinctively than before.

**Politics and administrative-legal power converge; politics and culture do not.**
Politics with administration and law gains +0.35 per century, the fourth largest
positive movement of the 78 pairs, and reaches +1.98 in the modern era. Politics
with culture (core) sits at -1.76 pooled and moves nowhere.

**Academia switches partners.** Its oldest tie is to religion (+2.36 for cohorts
born 1000 to 1399, decaying to +1.29 after 1900). Its ties to politics (+0.57 per
century), the military (+0.43) and nobility (+0.34) are three of the four steepest
positive trends in the data: the credentialled expert becomes a partner of the
older powers as the clerical tie loosens.

**The sector map hardens.** Among elites born before 1000, 34 of the 78 pairs are
not distinguishable from the reference model. After 1800, only 2 are. Whatever
combination of behaviour and record-keeping produces it, elite career combinations
become far more patterned over time.

**Economic and religious power stay apart.** Religion with big business is the
third most avoided pair in the record (-2.26, n = 520 across 2.07 million people),
and it does not trend.

Read every number alongside the caveats below.

## What comes out of the four domains

**Rule and coercion are the one durable fusion.** Political + Security is the
only crossing above chance in every era: +0.29 before 1000, +0.66 in 1400-1599,
+0.64 in 1600-1799, +0.67 after 1900, pooled at +0.60 (n = 29,577). Nothing else
in the four-domain matrix is positive throughout.

**Economic power sits apart from both rule and coercion.** Political + Economic
is below chance pooled (-0.17, n = 51,656) and Economic + Security is the most
avoided crossing in the record (-0.50, n = 9,328). The one economic tie above
chance is to the ideational domain (+0.20, n = 77,656), which is the inventor and
the professional, not the financier.

**Politics and the ideational domain are at chance.** Political + Ideational is
the most common crossing in absolute terms (96,140 elites, 34% of all crossings)
and the closest to zero once size is netted out (-0.06). The two largest domains
combine about as often as their sizes imply, no more.

**The domain structure is close to stationary while the sector structure moves.**
Not one of the six crossings carries a trend distinguishable from flat, on either
the century grid (1100 to 1900) or the half-century grid (1400 to 1949), after
adjusting the six tests. In the 13-sector layer 47 of 78 pairs move. The
implication is that most of what looks like historical change in elite career
combinations is reorganisation inside a domain, not a change in which domains get
combined.

**The exception is a level shift around 1800.** Four of the six crossings jump
toward zero between the 1750 and 1800 cohorts: Political + Economic from -0.32 to
-0.04, Ideational + Security from -0.77 to -0.18, Ideational + Economic from
+0.70 to +0.16, Political + Security from +0.53 to +0.31. A linear trend does not
capture it, and it coincides with the point where the recorded population
multiplies, so it should be treated as a candidate for a source effect as much as
a candidate for a real reordering.

**Crossing peaks in the eighteenth century.** The share of classified elites
holding two domains runs at 10% to 13% before 1200, climbs to 25% for the 1700
cohort, then falls back to 17% after 1900. Consolidation is the mirror: in every
century, roughly half of all two-sector elites combine two sectors inside one
domain.

**Economic and security elites reach furthest; ideational elites least.** After
1900, 67% of economic elites and 56% of security elites also hold another domain,
against 39% of political elites and 17% of ideational ones.

## Robustness: where does cultural production belong?

Putting Culture in the ideational domain makes it the largest of the four and
gives it a hand in every score it enters, so the whole domain analysis is rerun
under five readings with the estimator and everything else held constant:

| Reading | Ideational domain is | Classified | Crossings |
|---|---|---|---|
| `main` | religion, academy, culture | 1.49M | 280,761 (19%) |
| `culture_out` | religion and academy only | 0.95M | 188,810 (20%) |
| `culture_own` | religion and academy; culture is a fifth domain | 1.49M | 374,703 (25%) |
| `culture_core_only` | religion, academy, Culture (core) | 1.44M | 249,650 (17%) |
| `invention_ideational` | main, plus Exploration & Invention | 1.49M | 270,160 (18%) |

**Four of the six crossings keep their sign under every reading.** Political with
security stays positive across the full range (+0.33 to +1.07). Political with
ideational stays small and negative (-0.06 to -0.18), ideational with security
negative (-0.23 to -0.96), economic with security negative (-0.12 to -1.01). The
two headline claims about coercion, that rule and coercion fuse and that economic
power keeps its distance from coercion, do not depend on the placement of culture.

**The two that flip do so only under the five-domain reading**, and for a reason
worth stating plainly. Ideational with economic runs +0.20 in the main reading and
+0.28, +0.22, +0.21 in the other three four-domain readings, but -0.41 when culture
becomes a fifth domain. Its observed count under `culture_own` is 34,182, exactly
the same 34,182 as under `culture_out`: nothing about those elites changed. What
changed is the reference model, which now spreads its expectations over ten cells
instead of six. Scores are comparable within a reading, not across readings with
different numbers of domains. Political with economic flips the same way and for
the same reason.

**Culture as a fifth domain is worth looking at on its own terms.** It sits close
to the church and the academy (+0.47, n = 93,942), away from politics (-0.57,
n = 40,288) and furthest of all from the military (-0.89, n = 8,189), while
combining with economic power at almost exactly chance (+0.01, n = 43,474). In
that reading political with security reaches +1.07, the tightest fusion anywhere
in the analysis.

**Stationarity survives all five readings.** Of the 34 pair-by-reading trends
fitted on half-century cohorts from 1400 to 1949, 32 are flat after adjustment.
The two exceptions are political with cultural under `culture_own` (+0.18 per
century, q = 0.031) and one pair under `invention_ideational`. The finding that
the domain structure barely moves while the sector structure does is not an
artefact of where culture was put.

**Least sensitive to the reading:** political with ideational, which varies by
0.12 across all five. **Most sensitive:** economic with security, which varies by
0.89.

## Network structure

Two questions the pairwise tables cannot answer on their own.

### Positions

Two sectors occupy the same position when they combine with the same partners,
whether or not they combine with each other. Correlating the rows of the pooled
association matrix and clustering gives four blocks:

| Block | Members |
|---|---|
| Politics | Politics, Administration & Law |
| Military | Military, Religion, Nobility, Kinship |
| Academia | Academia, Culture (core), Culture (periphery) |
| Big business | Big business, Small business, Exploration & Invention, Sport & Games |

**The data recover the domain scheme without being told it.** The four blocks are
close to the four domains imposed earlier, with two differences that are themselves
informative: nobility and kinship attach to the military and not to politics,
and sport attaches to business. Within-block association exceeds between-block
association in every era, by 1.64 pooled and by as little as 0.24 in 1600-1799.

Four blocks is a choice, not a finding: the silhouette curve is close to flat from
two to six blocks (0.29 to 0.34). Six blocks scores highest by a hair and splits the
academy from cultural production, which is the same seam the `culture_own` reading
opened in the robustness run.

**Positions hold at the edges and churn in the middle.** Academia and both culture
sectors never leave their block in any era, and kinship never leaves the military
one. Sport, big business, small business and exploration each move three times or
more. Politics itself sits with the business block in 1900-2020.

**The centre changes hands and never gets tight.** Coreness on the positive ties
belongs to culture and the academy before 1400 and to nobility, kinship and the
military after 1800. But the core-periphery fit runs between 0.39 and 0.65 across
the eras, never high enough to say the positive ties form one core with a periphery
around it. Centralization ends at 0.28 against 0.33 before 1000 and modularity at
0.31 against 0.30: as the record thickens the matrix resolves, with the share of
pairs indistinguishable from the reference model falling from 44% before 1000 to
under 3% after 1800, but it does not concentrate.

### Level shifts

The trend fits reported above are linear, and a linear trend cannot see a step.
Fitting each pair with a common slope plus one level shift at an unknown date, and
simulating the null distribution of the largest Wald statistic 2,000 times, changes
one of the earlier conclusions.

**The domain structure does not drift. It steps.** None of the six crossings carried
a linear trend distinguishable from flat. Five of the six carry a level shift: three
dated at 1750 (ideational with economic, ideational with security, political with
economic), two at 1550 (political with ideational, economic with security). Only
political with security has no detectable shift, which is the crossing that was
already the most stable thing in the analysis. The pooled scan puts one common date
at 1750 (p = 0.001). The two results are not in tension: a structure that holds a
level and then moves to another has no trend to find.

**The sectors move together where no single pair moves alone.** Over the same 1400
to 1949 window, only 2 of 78 sector pairs carry a shift that survives adjustment,
yet the pooled scan finds a system-wide date at 1700 (p = 0.0005), and 57 of the 78
pairs put their own best-fitting date between 1650 and 1750. Many small coordinated
shifts, none large enough to detect on its own.

**The whole-record sector scan should be read with care.** On century cohorts from
800, 15 of 78 pairs carry a shift and the pooled date is 1100 (p = 0.0005), but the
cohorts before 1100 hold a few thousand people spread over 78 pairs and the fitted
shifts there run to five and six log points. That result is about how thin the early
record is at least as much as about the eleventh century.

## Comparing countries

Every score is refitted inside the country, so it is net of that country's own
sector sizes. Thirty-six countries clear 1,000 elites crossing two domains and hold
90% of all crossings; 24 clear 5,000 elites spanning two sectors.

**Rule fuses with coercion nearly everywhere.** Political with security is positive
in 34 of the 36 countries and distinguishable from the reference model in 32. It
runs from +1.17 in Iran, +1.10 in Hungary and +1.08 in Japan down to +0.11 in
Australia. Only Canada (-0.14) and New Zealand (-0.17) are negative.

**Three countries sit in the unusual corner of every panel.** Canada, Australia and
New Zealand are the only countries where rule combines with money more often than
chance, the only three where coercion combines with the ideational domain more
often than chance, and two of them are the only ones where rule does not combine
with coercion. Everywhere else money is the domain that keeps its distance from
both rule and coercion.

**Countries differ most on money and coercion, least on rule and ideas.** Economic
with security spans 1.97 across the 36, from -1.96 in Greece to +0.01 in Chile.
Political with ideational spans 0.19, from -0.19 to 0.00: on the crossing that is
the largest in absolute numbers, every country in the panel looks the same.

**Four groups fall out of the six scores.** Ward clustering gives a *US group* (12
countries) with weak associations across the board, political with security only
+0.23; a *Germany group* (16, including the UK, France, India, Russia and Japan)
with the classic pattern, +0.75 on rule with coercion and -0.66 on ideas with
coercion; a *Sweden group* (3: Sweden, Austria, Finland) that separates money from
coercion hardest of all (-1.16) while leaving ideas and coercion nearly free of
each other (-0.11); and a *China group* (5: China, Turkey, Iran, Greece, Romania)
with the tightest rule-coercion fusion (+0.82), the strongest ideas-money tie
(+0.58) and the most emphatic separation of money from coercion (-1.69).

**Specialisation varies more than three-fold.** Japan's elites cross a domain
boundary least often (10%), against 33% in Lithuania, 31% in Peru and 28% in Chile.
The 19% average hides a divide between the large western European records at
15-19% and the smaller Latin American and eastern European ones above 22%, which is
a candidate for a coverage effect as much as a behavioural one.

**The twentieth century tightened rule and coercion almost everywhere.** Between
the 1800-1899 and 1900-2020 cohorts the political-security score rises in 25 of the
30 countries estimable in both, with a median gain of +0.38. It is the only crossing
that moves one way: money with coercion falls in 20 of the 30 (median -0.34), and
the other four split about evenly.

**At sector level the state is where countries part company.** Politics with
administration and law runs from +3.2 in Japan to +1.2 in Canada and Australia; the
Japanese value is the single largest country-sector score in the panel.

## Shocks: what the data can and cannot say

The question is whether dated shocks leave a persistent mark on the association
between fields of power. The design that fits is a staggered event study, so that
is what was run: a Callaway-Sant'Anna style group-time estimator on a country by
25-year-cohort panel, with not-yet-exposed and never-exposed countries as
controls, and randomization inference over 2,000 reassignments of the shock years,
because sixteen countries and four never-exposed ones cannot support standard errors clustered on country.

**The finding is that no shock can be credited with a persistent effect, and four
things say so.**

1. **The estimates are at chance.** Five of the 72 ATT estimates fall outside the
   randomization null, against 3.6 expected. The smallest p-value is 0.014 and the
   smallest Benjamini-Hochberg q across the 72 is 0.55. Nothing survives
   adjustment. Two of the five are at pre-exposure event times, which is a failure
   and not a finding.

2. **Parallel trends fails.** For eleven of the twelve shock-type by crossing
   combinations the largest pre-exposure estimate is more than a sixth of the
   largest post-exposure one, and for one it is larger.

3. **The composition placebos move more than the outcome.** Running the identical
   estimator on the share of elites in each domain, the crossing rate and the log
   number of recorded elites returns 13 results at p < 0.05 against 5 for the
   association scores, and the strongest of them are *before* exposure: for
   revolutionary rupture, the political share at event time -3 has p = 0.001 and
   at -2 p < 0.001. Whatever separates the exposed countries, they were already
   separating before exposure and it shows up in who gets recorded.

4. **A single country moves most estimates more than their own size.** Dropping
   one country at a time shifts 78% of the estimates by more than the estimate
   itself.

One test the design passes: shocks moved 100 years earlier produce a similar
spread of estimates and nothing significant at all. The estimator is not
manufacturing effects. The problem is the panel, and it is worth naming precisely
because it is not fixable by a better estimator:

- Argentina and Brazil have no cohort before their shock, so they cannot enter.
- Only four countries are never exposed inside the window.
- Three of the four rupture cases are Russia, Germany and Austria in 1918, which
  is one event, not three. The rupture arm has two independent events.
- Australia 1901, Norway 1905 and New Zealand 1907 are similarly near-simultaneous.
- Birth cohorts blur exposure. A shock in year T falls on people born across a
  forty-year span, so the event is smeared over one or two 25-year cohorts before
  the estimator ever sees it.
- Revolutions follow crises in the elite order, so the timing is not exogenous to
  the outcome.

What would be needed to answer the question: a shock with many independent
occurrences, dated finely enough to separate cohorts, hitting countries that were
on a common path beforehand, and an outcome measured on a population whose
recording rule does not itself change at the shock. None of the four holds here.
The panel, the shock coding and the whole estimator are committed so the design
can be reused where they do.

Read `figE01` before `figE02`. The first shows why the second is flat.

## The military revolution

Roberts (1955) and Parker (1988) date a transformation of European warfare to about
1560-1660; Downing (1992), Tilly (1990) and Ertman (1997) carry it into state
formation. Every version of the claim is a claim about which fields of power get
combined in the same career, so the predictions can be written down in advance and
tested. Six were, each with its source, before the series was computed:

| Pair | Predicted | Claim |
|---|---|---|
| Politics + Military | tighten | Standing armies fused to rule |
| Administration & Law + Military | tighten | The fiscal-military state |
| Politics + Administration & Law | tighten | Permanent taxation turns rule into administration |
| Military + Exploration & Invention | tighten | The trace italienne makes the military engineer |
| Military + Big business | tighten | Military entrepreneurs and war finance |
| Military + Religion | loosen | Command secularises as the confessional wars close |

Military + Nobility is recorded as contested and left out of the sign test:
professionalisation implies loosening, absorption of the nobility into the officer
corps implies tightening.

**The directional predictions mostly hold.** Five of the six move as the thesis
says, which a sign test puts at p = 0.11 and a permutation test on the size of the
moves at p = 0.12. Suggestive, not significant. The largest moves are the military
engineer (+0.92) and rule with command (+0.61); the fall in the military-religion
tie is the fifth largest fall of all 78 pairs (-1.06).

**The one that fails is the thesis's central claim.** Administration and law with
the military moves the wrong way (-0.29). The fiscal-military state's core
proposition, that paying for armies built the office-holding bureaucracy, is the
prediction this record does not support.

**The contested pair sides against Roberts.** Military with nobility tightens
(+0.14, z = 2.65). That is the Downing and Ertman reading, the nobility absorbed
into the officer corps, and not the Roberts reading in which the professional
officer displaces the noble warrior.

**The dating does not fit.** No predicted pair has its dominant level shift inside
the exposed cohorts. Two of the six do rise across the window, both about the fusion
of rule with command and with administration. The rest move earlier: the
military-engineer tie is made between the 1425 and 1500 cohorts, before the window
opens, and so is the fall in the military-religion tie. Administration with the
military is flat through the window and then falls after 1700. A placebo window a
century earlier than Roberts' fits better than his own, 6 of 6 correct against 5 of
6, though it rests on only two pre-window cohorts. A window a century later fits
worst. The ordering says the contrast is medieval against early modern and is not
sensitive to where in that span the cut falls.

**There is no gradient by military pressure.** Splitting into high pressure (France,
Germany, Spain, Austria, Russia) and low (the United Kingdom, the Netherlands,
Switzerland, Sweden), following Downing's contrast, the high bloc did not move
further on any of the seven pairs. The two largest gaps run the wrong way, and a
permutation test over which countries sit in which bloc clears 0.28 everywhere. The
comparative mechanism every version of the thesis relies on leaves no trace here.

**One thing fits cleanly.** The military sector moves to the centre of the
network across the exposed cohorts, its coreness among the positive ties rising
from about 0.3 in the fifteenth-century cohorts to 0.9 by 1500 and staying high
for three hundred years. Arms did become a hub of elite careers. The record
dates it before Roberts does.

**Read all of it against the composition change.** Between the two ends of the
contrast the European recorded elite is transformed: nobility falls from 35% of
memberships to 12%, kinship from 19% to 7%, politics rises from 14% to 24%, the
military from 9% to 14%, and the number of recorded elites grows eightfold. The
association scores condition on those sizes within each cohort, which is what the
quasi-independence model is for, but a change of that size means the two ends are
not the same population. Selection into the record is not netted out and cannot be.

## Caveats

The source population is what encyclopaedic sources record, not what existed.
Coverage of the pre-1500 world outside Europe is thin, Wikipedia's editorial
attention is uneven across regions and periods, and the sheer volume of modern
biographies is not proportional to modern power. Sector composition
(`fig08`) makes the point: the surge of Sport & Games after 1800 is a fact about
the record before it is a fact about power. The association scores are computed
net of these marginals within each period, which handles composition but not
selection into the record in the first place.

Diversification is measured through a coded second occupational domain, so it
tracks what a biography says a person was, not what they owned or controlled. The
long fall in the two-sector share (69% for cohorts born in the 800s, 29% after
1900) mixes real occupational specialisation with the shorter, thinner biographies
that dominate the modern file. The level of that series should be read cautiously;
the ordering across sectors and the association scores, which condition on the
period, are on firmer ground.

Country is the cross-verified citizenship of the source, projected onto modern
states. The label is anachronistic for anyone born before the state existed: a
fifteenth-century Florentine is filed under Italy. And how many elites a country
contributes reflects which Wikipedia editions write about it, so the cross-country
differences in how often elites cross a boundary should be read more cautiously
than the association scores, which condition on the country's own composition.

Century cohorts before 1400 rest on a few thousand people spread over 78 pairs.
The bootstrap intervals reflect that, and the pre-1000 panels carry the widest
intervals in every figure.

The four-domain layer inherits all of this and adds one decision of its own. The
assignment of sectors to domains is a reading, not a measurement. Placing
Culture in the ideational domain makes that domain the largest of the four and
shapes every score it appears in; placing Exploration & Invention in the
economic domain instead of the ideational one moves about 20,000 elites.
Nobility and Kinship are excluded, which removes the strongest association in
the sector layer from the domain layer entirely.
`scripts/05_domain_associations.py` holds the mapping in a single dictionary at
the top of the file, so an alternative reading is a three-line change and a
rerun.

## Running it

```bash
pip install -r requirements.txt
python scripts/00_download_data.py      # 250 MB into data/raw/
python scripts/01_build_person_level.py # person-level extract
python scripts/02_sector_associations.py
python scripts/03_figures.py
python scripts/04_summary_table.py
python scripts/05_domain_associations.py   # four-domain layer
python scripts/06_domain_figures.py
python scripts/07_robustness_culture.py    # five readings of the domain mapping
python scripts/08_robustness_figures.py
python scripts/09_network_structure.py     # positions, blocks, level shifts
python scripts/10_network_structure_figures.py
python scripts/11_country_comparisons.py   # the same analyses inside each country
python scripts/12_country_figures.py
python scripts/13_shock_panel.py           # country x cohort panel and shock coding
python scripts/14_shock_event_study.py     # slowest step, about 10 minutes
python scripts/15_shock_figures.py
python scripts/16_military_revolution.py   # slowest step, about 25 minutes
python scripts/17_military_revolution_figures.py
```

Total runtime is about an hour after the download. Run the scripts from the
repository root; they import `assoc_core.py` and `plotstyle.py` from `scripts/`.

## Layout

```
data/raw/         source archive (git-ignored)
data/processed/   person-level extract and all derived tables
docs/CODEBOOK.md  variable-by-variable description of every output file
data/processed/robustness/          the domain analysis under five mappings
data/processed/network_structure/   positions, blocks, indices and level shifts
data/processed/countries/           the same analyses inside each of 36 countries
data/processed/shocks/              the cohort panel, the coded shocks, the event study
data/processed/military_revolution/ the pre-specified test of one named thesis
figures/          forty-three figures, PDF and PNG
scripts/          the pipeline, plus assoc_core.py (the pairwise estimator),
                  netstruct.py (positions, blocks, coreness, network indices),
                  breaks.py (the level-shift scan), domainmap.py (the named
                  sector-to-domain mappings) and plotstyle.py (figure styling)
```

`data/processed/elites_person_level.csv.gz` is 59 MB. It is committed so the
analysis can be rerun without touching the source archive.

## Citation

Cite the source database as above. The derived tables and figures in this
repository may be cited as a derivative of it.
