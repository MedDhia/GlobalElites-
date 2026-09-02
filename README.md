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
```

Total runtime is about six minutes after the download. Run the scripts from the
repository root; they import `assoc_core.py` and `plotstyle.py` from `scripts/`.

## Layout

```
data/raw/         source archive (git-ignored)
data/processed/   person-level extract and all derived tables
docs/CODEBOOK.md  variable-by-variable description of every output file
figures/          eighteen figures, PDF and PNG
scripts/          the pipeline, plus assoc_core.py (the estimator, shared by both
                  layers) and plotstyle.py (shared figure styling)
```

`data/processed/elites_person_level.csv.gz` is 59 MB. It is committed so the
analysis can be rerun without touching the source archive.

## Citation

Cite the source database as above. The derived tables and figures in this
repository may be cited as a derivative of it.
