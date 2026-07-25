# Conclusions — Regional Patterns in Canadian Dairy Genetic Evaluations

## What this study asked

Provincial genetic reports are usually read on their own, each describing one region's elite dairy population independently. This analysis combined the top 400 animals from all 10 Canadian provinces into a single dataset to ask a broader question: do regional differences in genetic merit go along with regional differences in the information behind those evaluations?

**"Information integration," used throughout this document, means the combination of pedigree, genomic testing, and official phenotype-based records (production and classification) behind an animal's genetic evaluation.** Genomic testing is one part of that combination — the results below treat it that way, as evidence for the broader integration pattern, not as the subject on its own.

Two more concepts matter throughout: an **Estimated Breeding Value (EBV)** is not a direct measurement — it's a statistical prediction of an animal's genetic merit, built from whatever information is available. **Reliability** reflects how much confidence to place in that prediction: how close it's likely to be to the animal's true genetic merit.

## Information behind genetic evaluations

Not every animal in this dataset carries the same weight of evidence. Crossing `LPI Code` (official phenotype-based evaluation vs. pedigree-only) with `GS` (genomic tested or not) gives four distinct information states, each with its own average reliability:

| Evidence available | `REL_PROT` | `REL_CONF` |
|---|---|---|
| Pedigree only | 37.9% | 35.1% |
| Genomic test, no phenotype-based evaluation yet | 81.0% | 77.6% |
| Phenotype-based evaluation, no genomic test | 56.2% | 48.0% |
| Genomic test + phenotype-based evaluation | 84.1% | 81.3% |

A genomic test alone is associated with higher reliability than phenotype-based records alone (81.0% vs. 56.2% on protein) — a statement about precision, not about which source matters more biologically. Combining both is associated with the highest reliability of any single source. (`EBV` status reflects production and classification records that may come from the animal itself or its relatives, such as daughters — not necessarily the animal's own performance alone.)

**Genomic testing's specific, best-supported contribution is confidence in the estimate, more than the estimate's magnitude — the single most statistically robust result in this project.** The reliability gap between genomically tested and untested animals is large (Cohen's d = 4.92 for protein reliability, 6.93 for conformation reliability: 82.3% vs. 49.5%, and 79.1% vs. 43.6%). The gap in the predicted values themselves is much smaller (comparing pedigree-only to phenotype-based animals directly, d = 0.17 to 0.52 across traits — statistically detectable but modest). Reliability climbs further when genomic testing is paired with phenotype-based records rather than used alone, consistent with the integration pattern this project is built around.

The highest-information group (genomic test + phenotype-based evaluation) ranges from just 2 animals in Manitoba to 67 in Ontario out of each province's 400 — a real difference in how much can be said with full confidence about each province.

**Method note:** provincial comparisons in this report use the unweighted mean of each province's 400 animals as the primary result. As a secondary check, provincial means were recalculated weighting each animal by reliability; results were consistent for most provinces, with Manitoba and Prince Edward Island showing larger differences between the two approaches and interpreted with extra caution as a result. Full method detail is in the statistical methodology document, Section 1.1.

## Regional patterns

The same integration pattern found at the animal level was tested at the regional level using `GS` (genomic tested or not). **Across all 10 provinces, genomic representation is associated with average LPI: r=0.73 (p=0.016), confirmed with a rank-based check (Spearman ρ=0.81, p=0.005) and by removing Quebec, the most extreme point (r=0.71, p=0.033, n=9).** No province needs to be excluded from this comparison — all 10 show a plausible `LPI Code` split and a `GS` field that looks equally trustworthy across the board.

**Genomic representation is not associated with LPI consistency** (r=0.01, not significant) — provinces with more genomic testing are not more internally consistent, only higher-scoring on average. This dataset cannot determine why provinces differ in genomic representation to begin with — nothing here speaks to producer cost, awareness, or access. Where the pattern does hold, it's consistent with treating pedigree, genomic testing, and phenotype-based records as complementary components of one system rather than separate or competing sources.

**By province** (ranked by average LPI):

- **Ontario** has the highest average LPI (3,884) and shows the strongest lean toward conformation over health/fertility of any province, alongside broadly strong performance on most other traits.
- **Quebec** ranks 2nd in average LPI (3,858) but is the most internally consistent province in the dataset (CV=1.45%, the lowest of any province) — a distinct strength from Ontario's. Quebec sits close to neutral on the conformation/health trade-off, unlike Ontario.
- **Manitoba** ranks 3rd (3,805) and leans most strongly toward health/fertility traits of any province — the opposite direction from most others — but 64% of its top-400 sit below breed average on Dairy Strength. Its most complete information group (genomic + phenotype-based) is only 2 animals, so figures specific to that subgroup are suggestive rather than definitive.
- **British Columbia** ranks 4th (3,771), leaning mildly toward health/fertility.
- **Alberta** ranks 5th (3,717), close to neutral on the conformation/health trade-off, and statistically indistinguishable from Nova Scotia (Tukey HSD, not significant).
- **Nova Scotia** ranks 6th (3,710), leaning toward conformation, statistically indistinguishable from Alberta despite the different trait lean.
- **Prince Edward Island** ranks 7th (3,608), leaning toward health/fertility — second only to Manitoba on that trade-off — and statistically indistinguishable from Saskatchewan.
- **Saskatchewan** ranks 8th (3,606), leaning toward conformation, statistically indistinguishable from PEI.
- **Newfoundland & Labrador** ranks 9th (3,558), essentially tied with New Brunswick (statistically indistinguishable), and by far the widest spread between its strongest and weakest animals of any province (LPI standard deviation, CV=2.76%, nearly double the next-highest province).
- **New Brunswick** ranks 10th (3,557), leaning toward conformation, statistically indistinguishable from Newfoundland & Labrador.

**A note on how close many of these rankings are:** several provinces sit within a few dozen LPI points of each other, and this specific ranking reflects one data snapshot (see Limitations). Three pairs are statistically indistinguishable at the 0.05 level (Alberta-Nova Scotia; Newfoundland & Labrador-New Brunswick; Prince Edward Island-Saskatchewan) despite different raw averages — treat small rank differences between adjacent provinces as noise, not a settled hierarchy.

**Multivariate grouping** (PCA + two independent clustering methods, in agreement): two axes explain ~86% of the cross-province pattern — one reflecting overall strength across most traits at once, the other a trade-off between feed efficiency and conformation. Quebec and Ontario score above the dataset average overall and lean toward conformation; Manitoba, British Columbia, Prince Edward Island, and Alberta form a more mixed group; New Brunswick, Newfoundland & Labrador, Nova Scotia, and Saskatchewan score below the dataset average overall. This groups provinces by similarity of profile shape, not by rank — scoring above average on more traits is a factual difference, but "different profile" isn't the same claim as "better" or "worse."

**Conformation vs. health/fertility priority, all 10 provinces** (composite of standardized conformation traits vs. standardized health/fertility traits, using each province's full 400-animal group):

| Province | Leans toward | Score |
|---|---|---|
| Ontario | Conformation (most) | +1.58 |
| New Brunswick | Conformation | +1.02 |
| Nova Scotia | Conformation | +0.99 |
| Saskatchewan | Conformation (mild) | +0.53 |
| Newfoundland & Labrador | Conformation (mild) | +0.42 |
| Quebec | Conformation (very mild) | +0.18 |
| Alberta | Neutral | -0.03 |
| British Columbia | Health/fertility (mild) | -0.61 |
| Prince Edward Island | Health/fertility | -1.44 |
| Manitoba | Health/fertility (most) | -2.65 |

Read this as which traits accompany a high LPI ranking in each province's elite population — the pattern is visible, but its cause isn't.

## Biological interpretation: production and conformation

Every correlation checked between production/component traits (Milk, Fat, Protein, %F, %P) and conformation traits (Conf, MS, F&L, DS, RP) fell below 0.3 — the strongest was Milk vs. Dairy Strength at only r=0.26, consistent with how these trait groups are deliberately designed to be selectable independently.

What conformation *is* associated with is limited. Conformation traits correlate strongly with `LTI` (r=0.80-0.89), but `LTI` itself barely correlates with production (r=-0.09 to -0.20), suggesting `LTI` may be partly built from conformation in the underlying formula rather than an independent confirmation that conformation drives some other outcome. The intuitive idea that better udder conformation (`MS`) coincides with better udder health was tested directly: `MS` vs. `SCS` (mastitis indicator) is r=0.02, and `MS` vs. `HWI` (health/fertility) is r=-0.02, both stable near zero across repeated resampling — not supported. The one real, standalone pattern is a mild trade-off: `DS` (Dairy Strength) vs. `BMR` (mastitis resistance) is r=-0.59, stable — more body capacity coincides with somewhat lower genetic mastitis resistance.

This dataset doesn't demonstrate that conformation delivers a benefit beyond its built-in weight inside the LPI formula. Confirming an actual downstream benefit would need data this project doesn't have — culling age, calving-ease records, clinical mastitis case counts, or realized lifetime profitability.

Separately: LPI is driven far more by Protein, Mammary System, and Feet & Legs than by raw Milk volume (a standardized regression, R²=0.984, found Milk's contribution near zero — β=0.02 — once other traits were accounted for, while Protein, Mammary System, and Feet & Legs each carried β≈0.40-0.43). A high-Milk animal is not necessarily a high-LPI animal. Fat and Protein are the most "solved" traits in the population (only 0.2% of animals fall below breed average on either, versus 22.6% for Dairy Strength). Average LPI rose across birth cohorts from the ~3,400s (2019-2021) to ~3,800 (2025-2026). Feed efficiency showed no meaningful link to body size or conformation (r≈0.02-0.14).

## Practical implications

The central message here is not that one province breeds better animals than another. It's that these evaluations depend on integrating complementary sources of information — pedigree, genomic testing, and phenotype-based records each contribute different evidence, and where more of them are combined, results tend to be both more reliable and more consistent. This dataset cannot estimate economic return — it contains predicted genetic values, not production, health, or financial records — so no ROI claim is made here.

The regional differences in how information sources are combined may represent an opportunity for province-specific knowledge-transfer or extension strategies emphasizing their complementary value, rather than one national message assuming uniform adoption. Whether those differences trace back to producer preference, historical breeding objectives, economics, or something else isn't something this dataset can settle — only that the pattern exists and lines up with measurable differences in evaluation quality.

**By audience:**
- **Producers:** more reliable evaluations reduce uncertainty when selecting replacements or making culling decisions.
- **Geneticists:** the results highlight the complementary — not redundant — contribution of pedigree, genomic, and phenotypic information.
- **Breed organizations and AI/breeding companies:** regional differences in information integration point to where it may be worth better understanding how information is adopted and combined across breeding programs, and where sire/genetics marketing claims should be checked against the underlying reliability, not just the predicted value.
- **Researchers:** this proposes information integration, rather than provincial ranking, as a lens for interpreting elite genetic populations.

## Open questions and limitations

- **Not a census.** Each province's file is its top 400 animals ranked by LPI. Every "provincial average" describes each province's elite tier, not its general herd.
- **"Dataset average" ≠ an official national average** — every average here is computed from these 4,000 records only.
- **Every animal in this dataset is unique** — checked directly (pairwise ID comparison across all 10 provinces): 0 animals appear in more than one province's file.
- **This is a snapshot in time, not a static dataset.** Lactanet's official evaluations are released periodically, and which animals rank in each province's top 400 shifts as new births, milk recording, classification, and genomic results arrive. The selection criterion is each animal's LPI at the time of this data pull — rankings reported here, especially close ones between adjacent provinces, should be read as a point-in-time picture, not a permanent hierarchy.
- **`LPI Code` now shows a plausible PA/EBV split in all 10 provinces** — no province needs to be excluded from that comparison. Manitoba's genomic-and-phenotype sample is still only 2 animals, so figures specific to that subgroup are suggestive rather than definitive.
- **Genomic testing turnaround isn't captured** — a recently-sampled animal awaiting results (about a month) looks identical to one never tested, mainly affecting the youngest cohorts.
- **Age is approximate** (birth year only).
- **No direct body-size/height measurement exists** — `DS` and `Conf` were used as imperfect proxies.
- **"Consistency" was measured two different ways, with different answers:** between-animal consistency (Quebec highest, Newfoundland & Labrador lowest) is a different question from within-animal trait balance (Saskatchewan and PEI most balanced, Newfoundland & Labrador and Manitoba least) — Quebec is only mid-pack on the second measure despite leading the first.

## Future research

This analysis used predicted genetic values only, drawn from top-ranked subsets rather than complete provincial populations. Useful next steps would include validating these regional patterns against complete national evaluation datasets, and combining these genetic evaluations with herd-level production, health, longevity, and economic records to test whether the patterns found here translate into measurable biological or economic outcomes over time.

---

## How confident should these conclusions be treated?

| Finding | Confidence | Why |
|---|---|---|
| Genomic testing is associated with higher reliability | **Very high** | Huge effect sizes (d>4.9), consistent, statistically robust |
| Genomic representation is associated with higher average LPI, across all 10 provinces | **High** | r=0.73 (p=0.016), confirmed via Spearman (ρ=0.81, p=0.005) and by removing the most extreme province; no longer associated with consistency (r=0.01, not significant) — that claim was dropped |
| Conformation has no demonstrated real-world benefit in this dataset | **High** | Every direct test (vs. SCS, HWI, production) came back null or near-null, stable across resamples — a statement about what this dataset can/can't show, not proof conformation is useless in reality |
| Production and conformation are largely independent | **High** | Consistent near-zero correlations across every pair checked, assumptions verified |
| Province differences in LPI/traits are real | **High** | ANOVA + Tukey HSD + narrow 95% CIs all agree |
| Province clustering (3 groups) | **Moderate** | Two independent methods agree, but based on only 10 data points (provinces) |
| Phenotype-based vs. pedigree-only, modest difference | **Moderate** | Statistically real but small effect sizes; some contributing provinces have small samples |
| Manitoba's health/fertility priority | **Moderate** | Directionally clear, but the relevant sample size is very small (n=2) |
| Feed efficiency unrelated to body size | **Moderate** | No good direct size measurement exists; conclusion depends on imperfect proxies |
| Any conclusion framed as "province X's whole population" | **Low** | These are top-400-by-LPI subsets, not population samples |
