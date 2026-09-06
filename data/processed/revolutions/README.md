# Elites who lived through a major revolution

One folder per revolution, holding the elites who were adults in a country whose political order was at stake while the revolution ran.

## Membership

A person is in a cohort when their coded country is one of the countries where the political order was at stake, they were at least 20 years old at some point inside the window, and they were alive when the window opened. Death is missing for more than half the rows, so a missing death year is imputed as birth plus 80 for the alive test only; `death_imputed` marks every row where that was used. The imputation is generous, so the cohorts are upper bounds.

Countries are scoped to the states whose own order was in question, not every state that took an interest. France is not in the Haitian cohort and the United Kingdom is not in the Irish cohort, though both intervened: including the metropole would swamp the cohort with elites whose regime was never at stake.

Country is coded as present-day citizenship, which is the only country field the database carries. That is anachronistic by construction. Germany stands for the German states, Italy for the Italian ones, and the successor republics stand for the territory of the Russian empire.

## Which revolutions are here

A revolution is kept when its cohort holds at least 500 elites and at least 200 who span two sectors, which is the floor the pair estimator needs. Every revolution considered is listed, kept or not.

| Revolution | Years | Elites | Two sectors | Kept |
|---|---|---:|---:|---|
| German Revolution | 1918-1919 | 54,018 | 22,942 | yes |
| Revolutions of 1848 | 1848-1849 | 36,998 | 17,922 | yes |
| Russian Revolution | 1917-1923 | 13,925 | 6,669 | yes |
| French Revolution | 1789-1799 | 12,685 | 5,715 | yes |
| English Revolution | 1642-1651 | 4,037 | 2,423 | yes |
| Glorious Revolution | 1688-1689 | 3,126 | 1,837 | yes |
| Irish revolution | 1916-1923 | 3,104 | 1,327 | yes |
| Latin American independence | 1810-1825 | 2,976 | 2,108 | yes |
| American Revolution | 1775-1783 | 2,925 | 2,076 | yes |
| Chinese Communist Revolution | 1946-1949 | 2,698 | 1,336 | yes |
| Iranian Revolution | 1978-1979 | 2,432 | 1,235 | yes |
| Mexican Revolution | 1910-1920 | 1,923 | 1,213 | yes |
| Cuban Revolution | 1953-1959 | 1,260 | 490 | yes |
| Xinhai Revolution | 1911-1912 | 831 | 514 | yes |
| Turkish revolution | 1919-1923 | 722 | 449 | yes |
| Meiji Restoration | 1868-1869 | 518 | 344 | yes |
| Haitian Revolution | 1791-1804 | 39 | 35 | no, only 39 elites |

## Top-level files

| File | Contents |
|---|---|
| `revolutions_index.csv` | the table above, with the full country lists |
| `cohort_summary.csv` | one row per kept revolution: counts, coverage, age bands |
| `cohort_composition.csv` | sector and group shares, every cohort stacked |
| `cohort_group_pairs.csv` | the 21 group-pair scores, every cohort stacked |

## Caveats

These are descriptive cohorts. Living through a revolution is not an assignment, the windows are conventional dates, and the birth-cohort series inside each folder is a comparison, not a control. Cohorts also overlap where windows are close in the same countries: the Xinhai and Chinese Communist cohorts share people, as do the Russian and German ones through Poland and Austria. `scripts/14_shock_event_study.py` is where the causal question is put.

Coverage of the database rises steeply with time, so the modern cohorts are larger than the early modern ones by a wide margin and the two are not comparable in size. Association scores are refitted inside each cohort, which makes them comparable in a way the raw counts are not.
