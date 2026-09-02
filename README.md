# Sectors of elite power: association and dissociation, 3500 BCE to 2020 CE

Which sources of power do historical elites combine, which do they keep apart,
and how have those pairings shifted over a millennium?

This repository stages the BHHT cross-verified database of notable people, reduces
it to a person-by-sector file, measures the association between every pair of
power sectors within birth cohorts, and produces the figures and derived datasets
that follow from it.

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

## Running it

```bash
pip install -r requirements.txt
python scripts/00_download_data.py      # 250 MB into data/raw/
python scripts/01_build_person_level.py # person-level extract
python scripts/02_sector_associations.py
python scripts/03_figures.py
python scripts/04_summary_table.py
```

Total runtime is about three minutes after the download.

## Layout

```
data/raw/         source archive (git-ignored)
data/processed/   person-level extract and all derived tables
docs/CODEBOOK.md  variable-by-variable description of every output file
figures/          ten figures, PDF and PNG
scripts/          the four-step pipeline
```

`data/processed/elites_person_level.csv.gz` is 59 MB. It is committed so the
analysis can be rerun without touching the source archive.

## Citation

Cite the source database as above. The derived tables and figures in this
repository may be cited as a derivative of it.
